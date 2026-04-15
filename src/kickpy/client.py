import logging
import webbrowser
from datetime import datetime
from typing import Any, Dict, Union
from urllib.parse import urlencode

import aiohttp

from kickpy import __version__, utils
from kickpy.enums import Scope
from kickpy.errors import (
    BadRequest,
    Forbidden,
    InternalServerError,
    MissingArgument,
    NotFound,
    Ratelimited,
    Unauthorized,
)
from kickpy.models.access_token import AccessToken
from kickpy.models.categories import Category
from kickpy.models.channel import Channel
from kickpy.models.chat import ChatResponse
from kickpy.models.events_subscriptions import EventsSubscription, EventsSubscriptionCreated
from kickpy.models.kicks import KicksLeaderboard
from kickpy.models.livestream_stats import LivestreamStats
from kickpy.models.livestreams import LiveStream
from kickpy.models.rewards import (
    ChannelReward,
    FailedRedemption,
    RedemptionsByReward,
)
from kickpy.models.user import User
from kickpy.oauth import OAuthCallbackServer, generate_pkce_pair, generate_state
from kickpy.webhooks.enums import WebhookEvent

log = logging.getLogger(__name__)

USER_AGENT = f"kickcom.py/{__version__}"


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    if response.headers.get("Content-Type") == "application/json":
        return utils.json_loads(text)

    return text


class KickClient:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: AccessToken | None = None
        self._user_token: AccessToken | None = None

        self.id_session = aiohttp.ClientSession(
            base_url="https://id.kick.com", headers={"User-Agent": USER_AGENT}
        )
        self.api_session = aiohttp.ClientSession(
            base_url="https://api.kick.com/public/v1/", headers={"User-Agent": USER_AGENT}
        )
        self.api_v2_session = aiohttp.ClientSession(
            base_url="https://api.kick.com/public/v2/", headers={"User-Agent": USER_AGENT}
        )

    async def close(self):
        """Close the client and all sessions."""
        await self.id_session.close()
        await self.api_session.close()
        await self.api_v2_session.close()

    async def _handle_response(self, resp: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
        if resp.status == 204:
            return {}

        if resp.status == 400:
            raise BadRequest(resp)

        if resp.status == 401:
            raise Unauthorized(resp)

        if resp.status == 403:
            raise Forbidden(resp)

        if resp.status == 404:
            raise NotFound(resp)

        # TODO: Implement proper ratelimit handling
        if resp.status == 429:
            raise Ratelimited(resp)

        if resp.status >= 500:
            raise InternalServerError(resp)

        data = await json_or_text(resp)

        if isinstance(data, dict) and "data" in data and not data["data"]:
            raise NotFound(resp)

        return data

    async def _get_token(self, use_user_token: bool) -> AccessToken:
        if use_user_token:
            if not self._user_token:
                self._load_user_token()
            if not self._user_token:
                raise Unauthorized(
                    None,
                    "No user token available. Call authenticate() or set_user_token() first.",
                )
            if self._user_token.expires_at <= datetime.now():
                await self._refresh_user_token()
            return self._user_token
        return await self._fetch_access_token()

    def _load_user_token(self) -> None:
        try:
            with open(".kick.user_token.json", "r") as f:
                json_data = utils.json_loads(f.read())
                token = AccessToken(**json_data)
                if token.expires_at > datetime.now():
                    self._user_token = token
                else:
                    log.info("User token expired, needs re-authentication or refresh.")
                    if token.refresh_token:
                        self._user_token = token
        except (FileNotFoundError, Exception):
            pass

    async def _fetch_api(
        self, method: str, endpoint: str, *, use_user_token: bool = False, **kwargs
    ) -> dict:
        token = await self._get_token(use_user_token)

        async with self.api_session.request(
            method,
            endpoint,
            headers={"Authorization": f"Bearer {token.access_token}"},
            **kwargs,
        ) as resp:
            return await self._handle_response(resp)

    async def _fetch_api_v2(
        self, method: str, endpoint: str, *, use_user_token: bool = False, **kwargs
    ) -> dict:
        token = await self._get_token(use_user_token)

        async with self.api_v2_session.request(
            method,
            endpoint,
            headers={"Authorization": f"Bearer {token.access_token}"},
            **kwargs,
        ) as resp:
            return await self._handle_response(resp)

    async def _fetch_access_token(self) -> AccessToken:
        if self._access_token and self._access_token.expires_at > datetime.now():
            return self._access_token

        try:
            with open(".kick.token.json", "r") as f:
                json_data = utils.json_loads(f.read())
                access_token = AccessToken(**json_data)
                if access_token.expires_at > datetime.now():
                    self._access_token = access_token
                    return access_token

                log.info("Token expired, fetching a new one...")
        except (FileNotFoundError, Exception):
            pass

        async with self.id_session.post(
            "/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        ) as resp:
            if resp.status != 200:
                raise InternalServerError(resp, "Failed to fetch access token.")

            data: dict = await resp.json()

        data["expires_at"] = datetime.now().timestamp() + data.pop("expires_in", 0)
        access_token = AccessToken(**data)
        with open(".kick.token.json", "w+") as f:
            f.write(utils.json_dumps(access_token.to_dict()))

        self._access_token = access_token
        return access_token

    # ---------- OAuth User Token Flow ----------

    async def authenticate(
        self,
        scopes: list[Scope | str],
        redirect_uri: str | None = None,
        port: int = 3000,
        timeout: float = 300,
    ) -> None:
        """Authenticate with Kick using OAuth 2.1 + PKCE.

        Opens the user's browser to authorize, captures the callback on a local server,
        and exchanges the code for tokens.

        Parameters
        ----------
        scopes: list[Scope | str]
            The scopes to request.
        redirect_uri: str | None
            The redirect URI. Defaults to ``http://127.0.0.1:{port}/callback``.
        port: int
            The local port for the callback server. Defaults to 3000.
        timeout: float
            Maximum seconds to wait for the user to authorize. Defaults to 300 (5 minutes).
        """
        code_verifier, code_challenge = generate_pkce_pair()
        state = generate_state()

        if redirect_uri is None:
            redirect_uri = f"http://localhost:{port}/callback"

        scope_str = " ".join(s.value if isinstance(s, Scope) else s for s in scopes)

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": scope_str,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        authorize_url = f"https://id.kick.com/oauth/authorize?{urlencode(params)}"

        callback_server = OAuthCallbackServer()

        webbrowser.open(authorize_url)
        log.info("Opened browser for authorization. Waiting for callback...")

        try:
            code, returned_state = await callback_server.start(port, timeout=timeout)

            if returned_state != state:
                raise RuntimeError("OAuth state mismatch — possible CSRF attack.")

            await self._exchange_code(code, redirect_uri, code_verifier)
        finally:
            await callback_server.stop()

    async def _exchange_code(self, code: str, redirect_uri: str, code_verifier: str) -> None:
        async with self.id_session.post(
            "/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                log.error("Token exchange failed (HTTP %s): %s", resp.status, body)
                raise InternalServerError(resp, f"Failed to exchange authorization code: {body}")

            data: dict = await resp.json()

        data["expires_at"] = datetime.now().timestamp() + data.pop("expires_in", 0)
        data["token_kind"] = "user"
        self._user_token = AccessToken(**data)
        with open(".kick.user_token.json", "w+") as f:
            f.write(utils.json_dumps(self._user_token.to_dict()))

    async def _refresh_user_token(self) -> None:
        if not self._user_token or not self._user_token.refresh_token:
            raise Unauthorized(None, "No refresh token available.")

        async with self.id_session.post(
            "/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self._user_token.refresh_token,
            },
        ) as resp:
            if resp.status != 200:
                raise InternalServerError(resp, "Failed to refresh user token.")

            data: dict = await resp.json()

        data["expires_at"] = datetime.now().timestamp() + data.pop("expires_in", 0)
        data["token_kind"] = "user"
        self._user_token = AccessToken(**data)
        with open(".kick.user_token.json", "w+") as f:
            f.write(utils.json_dumps(self._user_token.to_dict()))

    def set_user_token(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        scope: str,
    ) -> None:
        """Manually set a user token for users who handle OAuth externally.

        Parameters
        ----------
        access_token: str
            The access token.
        refresh_token: str
            The refresh token.
        expires_in: int
            Seconds until the token expires.
        scope: str
            The scopes granted.
        """
        self._user_token = AccessToken(
            access_token=access_token,
            expires_at=datetime.now().timestamp() + expires_in,
            token_type="Bearer",
            refresh_token=refresh_token,
            scope=scope,
            token_kind="user",
        )

    # ---------- Public Key ----------

    async def fetch_public_key(self) -> bytes:
        """Get the public key of the Kick.com API.

        Returns
        -------
        bytes
            The public key data.
        """
        data = await self._fetch_api("GET", "public-key")

        public_key: str = data["data"]["public_key"]
        return public_key.encode()

    # ---------- Users ----------

    async def fetch_user(self, user_id: int) -> User:
        """Get a user by their ID.

        Parameters
        ----------
        user_id: int
            The ID of the user to get.

        Returns
        -------
        User
            The user data.
        """
        data = await self._fetch_api("GET", "users", params={"id": user_id})
        return User(**data["data"][0])

    # ---------- Channels ----------

    async def fetch_channel(self, user_id: int | None = None, slug: str | None = None) -> Channel:
        """Get a channel by the broadcaster user ID or slug.

        Parameters
        ----------
        user_id: int
            The broadcaster user ID.
        slug: str
            The broadcaster user slug.

        Returns
        -------
        Channel
            The channel data.
        """
        if user_id and slug:
            raise MissingArgument("Either user_id or slug must be provided, not both.")
        if not user_id and not slug:
            raise MissingArgument("Either user_id or slug must be provided.")

        params = {}
        if user_id:
            params["broadcaster_user_id"] = user_id
        if slug:
            params["slug"] = slug
        data = await self._fetch_api("GET", "channels", params=params)
        return Channel(**data["data"][0])

    async def update_channel(
        self,
        *,
        category_id: int | None = None,
        stream_title: str | None = None,
        custom_tags: list[str] | None = None,
    ) -> None:
        """Update channel metadata. Requires ``channel:write`` scope.

        At least one parameter must be provided.

        Parameters
        ----------
        category_id: int | None
            The new category ID.
        stream_title: str | None
            The new stream title.
        custom_tags: list[str] | None
            The new custom tags (max 10).
        """
        body = {}
        if category_id is not None:
            body["category_id"] = category_id
        if stream_title is not None:
            body["stream_title"] = stream_title
        if custom_tags is not None:
            body["custom_tags"] = custom_tags

        if not body:
            raise MissingArgument(
                "At least one of category_id, stream_title, or custom_tags must be provided."
            )

        await self._fetch_api("PATCH", "channels", use_user_token=True, json=body)

    # ---------- Livestreams ----------

    async def fetch_livestream(self, broadcaster_user_id: int) -> LiveStream:
        """Get livestream by the broadcaster user ID.

        Parameters
        ----------
        broadcaster_user_id: int
            The broadcaster user ID to get livestream from.

        Returns
        -------
        LiveStream
            The livestream data.
        """
        data = await self._fetch_api(
            "GET", "livestreams", params={"broadcaster_user_id": broadcaster_user_id}
        )
        return LiveStream(**data["data"][0])

    async def fetch_livestreams(
        self,
        broadcaster_user_id: int | list[int] | None = None,
        category_id: int | None = None,
        language: str | None = None,
        limit: int | None = None,
        sort: str = "viewer_count",
    ) -> list[LiveStream]:
        """Get livestreams.

        Parameters
        ----------
        broadcaster_user_id: int | list[int] | None
            One or more broadcaster user IDs (up to 50).
        category_id: int | None
            The category ID to filter by.
        language: str | None
            The language to filter by.
        limit: int | None
            The maximum number of results (1-100, default 25).
        sort: str
            Sort order. Either ``'viewer_count'`` or ``'started_at'``.

        Returns
        -------
        list[LiveStream]
            A list of livestream data.
        """
        if sort not in {"viewer_count", "started_at"}:
            raise ValueError("Invalid sort order. Must be either 'viewer_count' or 'started_at'.")

        params = {}
        if broadcaster_user_id is not None:
            params["broadcaster_user_id"] = broadcaster_user_id
        if category_id:
            params["category_id"] = category_id
        if language:
            params["language"] = language
        if limit:
            params["limit"] = limit
        params["sort"] = sort

        data = await self._fetch_api("GET", "livestreams", params=params)
        return [LiveStream(**livestream) for livestream in data["data"]]

    async def fetch_livestream_stats(self) -> LivestreamStats:
        """Get global livestream statistics.

        Returns
        -------
        LivestreamStats
            The livestream stats.
        """
        data = await self._fetch_api("GET", "livestreams/stats")
        return LivestreamStats(**data["data"])

    # ---------- Categories (v2) ----------

    async def fetch_categories(
        self,
        query: str | None = None,
        *,
        name: list[str] | None = None,
        tag: list[str] | None = None,
        category_id: list[int] | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[Category]:
        """Get categories using the v2 endpoint.

        Parameters
        ----------
        query: str | None
            Shorthand for searching by name. Equivalent to ``name=[query]``.
        name: list[str] | None
            Category names to search for.
        tag: list[str] | None
            Category tags to filter by.
        category_id: list[int] | None
            Category IDs to filter by.
        cursor: str | None
            Pagination cursor.
        limit: int
            Results limit (1-1000, default 25).

        Returns
        -------
        list[Category]
            A list of categories.
        """
        params: dict[str, Any] = {"limit": limit}
        if query is not None:
            if name is not None:
                raise MissingArgument("Cannot use both 'query' and 'name' at the same time.")
            params["name"] = query
        elif name:
            params["name"] = ",".join(name)
        if tag:
            params["tag"] = ",".join(tag)
        if category_id:
            params["id"] = ",".join(str(i) for i in category_id)
        if cursor:
            params["cursor"] = cursor
        data = await self._fetch_api_v2("GET", "categories", params=params)
        return [Category(**category) for category in data["data"]]

    # ---------- Chat ----------

    async def send_chat_message(
        self,
        content: str,
        message_type: str = "bot",
        broadcaster_user_id: int | None = None,
        reply_to_message_id: str | None = None,
    ) -> ChatResponse:
        """Send a chat message. Requires ``chat:write`` scope.

        Parameters
        ----------
        content: str
            The message text (max 500 characters).
        message_type: str
            The sending mode: ``'user'`` or ``'bot'``.
        broadcaster_user_id: int | None
            Required when message_type is ``'user'``. The channel to send to.
        reply_to_message_id: str | None
            Optional message ID to reply to.

        Returns
        -------
        ChatResponse
            The response containing is_sent and message_id.
        """
        if message_type not in {"user", "bot"}:
            raise ValueError("message_type must be either 'user' or 'bot'.")
        if message_type == "user" and broadcaster_user_id is None:
            raise MissingArgument("broadcaster_user_id is required when message_type is 'user'.")

        body: dict = {"content": content, "type": message_type}
        if broadcaster_user_id is not None:
            body["broadcaster_user_id"] = broadcaster_user_id
        if reply_to_message_id is not None:
            body["reply_to_message_id"] = reply_to_message_id

        data = await self._fetch_api("POST", "chat", use_user_token=True, json=body)
        return ChatResponse(**data["data"])

    async def delete_chat_message(self, message_id: str) -> None:
        """Delete a chat message. Requires ``moderation:chat_message:manage`` scope.

        Parameters
        ----------
        message_id: str
            The ID of the message to delete.
        """
        await self._fetch_api("DELETE", f"chat/{message_id}", use_user_token=True)

    # ---------- Moderation ----------

    async def ban_user(
        self,
        broadcaster_user_id: int,
        user_id: int,
        *,
        duration: int | None = None,
        reason: str | None = None,
    ) -> None:
        """Ban or timeout a user. Requires ``moderation:ban`` scope.

        Parameters
        ----------
        broadcaster_user_id: int
            The channel to ban in.
        user_id: int
            The user to ban.
        duration: int | None
            Timeout duration in minutes (1-10080). Omit for permanent ban.
        reason: str | None
            The ban/timeout reason (max 100 characters).
        """
        body: dict = {
            "broadcaster_user_id": broadcaster_user_id,
            "user_id": user_id,
        }
        if duration is not None:
            body["duration"] = duration
        if reason is not None:
            body["reason"] = reason

        await self._fetch_api("POST", "moderation/bans", use_user_token=True, json=body)

    async def unban_user(self, broadcaster_user_id: int, user_id: int) -> None:
        """Unban a user or remove a timeout. Requires ``moderation:ban`` scope.

        Parameters
        ----------
        broadcaster_user_id: int
            The channel to unban in.
        user_id: int
            The user to unban.
        """
        body = {
            "broadcaster_user_id": broadcaster_user_id,
            "user_id": user_id,
        }
        await self._fetch_api("DELETE", "moderation/bans", use_user_token=True, json=body)

    # ---------- Channel Rewards ----------

    async def fetch_channel_rewards(self) -> list[ChannelReward]:
        """Get channel point rewards. Requires ``channel:rewards:read`` scope.

        Returns
        -------
        list[ChannelReward]
            A list of channel rewards.
        """
        data = await self._fetch_api("GET", "channels/rewards", use_user_token=True)
        return [ChannelReward(**reward) for reward in data["data"]]

    async def create_channel_reward(
        self,
        cost: int,
        title: str,
        *,
        background_color: str | None = None,
        description: str | None = None,
        is_enabled: bool | None = None,
        is_user_input_required: bool | None = None,
        should_redemptions_skip_request_queue: bool | None = None,
    ) -> ChannelReward:
        """Create a channel point reward. Requires ``channel:rewards:write`` scope.

        Parameters
        ----------
        cost: int
            The cost in channel points (min 1).
        title: str
            The reward title (max 50 characters).
        background_color: str | None
            Hex color (default ``#00e701``).
        description: str | None
            The reward description (max 200 characters).
        is_enabled: bool | None
            Whether the reward is enabled (default True).
        is_user_input_required: bool | None
            Whether user input is required (default False).
        should_redemptions_skip_request_queue: bool | None
            Whether redemptions skip the queue (default False).

        Returns
        -------
        ChannelReward
            The created reward.
        """
        body: dict = {"cost": cost, "title": title}
        if background_color is not None:
            body["background_color"] = background_color
        if description is not None:
            body["description"] = description
        if is_enabled is not None:
            body["is_enabled"] = is_enabled
        if is_user_input_required is not None:
            body["is_user_input_required"] = is_user_input_required
        if should_redemptions_skip_request_queue is not None:
            body["should_redemptions_skip_request_queue"] = should_redemptions_skip_request_queue

        data = await self._fetch_api("POST", "channels/rewards", use_user_token=True, json=body)
        return ChannelReward(**data["data"])

    async def update_channel_reward(
        self,
        reward_id: str,
        *,
        background_color: str | None = None,
        cost: int | None = None,
        description: str | None = None,
        is_enabled: bool | None = None,
        is_paused: bool | None = None,
        is_user_input_required: bool | None = None,
        should_redemptions_skip_request_queue: bool | None = None,
        title: str | None = None,
    ) -> ChannelReward:
        """Update a channel point reward. Requires ``channel:rewards:write`` scope.

        Only the app that created the reward can update it.

        Parameters
        ----------
        reward_id: str
            The reward ID (ULID).
        background_color: str | None
            Hex color.
        cost: int | None
            The cost in channel points.
        description: str | None
            The reward description.
        is_enabled: bool | None
            Whether the reward is enabled.
        is_paused: bool | None
            Whether the reward is paused.
        is_user_input_required: bool | None
            Whether user input is required.
        should_redemptions_skip_request_queue: bool | None
            Whether redemptions skip the queue.
        title: str | None
            The reward title.

        Returns
        -------
        ChannelReward
            The updated reward.
        """
        body = {}
        if background_color is not None:
            body["background_color"] = background_color
        if cost is not None:
            body["cost"] = cost
        if description is not None:
            body["description"] = description
        if is_enabled is not None:
            body["is_enabled"] = is_enabled
        if is_paused is not None:
            body["is_paused"] = is_paused
        if is_user_input_required is not None:
            body["is_user_input_required"] = is_user_input_required
        if should_redemptions_skip_request_queue is not None:
            body["should_redemptions_skip_request_queue"] = should_redemptions_skip_request_queue
        if title is not None:
            body["title"] = title

        if not body:
            raise MissingArgument("At least one field must be provided to update.")

        data = await self._fetch_api(
            "PATCH", f"channels/rewards/{reward_id}", use_user_token=True, json=body
        )
        return ChannelReward(**data["data"])

    async def delete_channel_reward(self, reward_id: str) -> None:
        """Delete a channel point reward. Requires ``channel:rewards:write`` scope.

        Only the app that created the reward can delete it.

        Parameters
        ----------
        reward_id: str
            The reward ID (ULID).
        """
        await self._fetch_api("DELETE", f"channels/rewards/{reward_id}", use_user_token=True)

    async def fetch_reward_redemptions(
        self,
        *,
        reward_id: str | None = None,
        status: str | None = None,
        ids: list[str] | None = None,
        cursor: str | None = None,
    ) -> list[RedemptionsByReward]:
        """Get reward redemptions. Requires ``channel:rewards:read`` scope.

        Parameters
        ----------
        reward_id: str | None
            Filter by specific reward ID.
        status: str | None
            Filter by status: ``'pending'``, ``'accepted'``, or ``'rejected'``.
        ids: list[str] | None
            Specific redemption IDs (cannot combine with other filters).
        cursor: str | None
            Pagination cursor.

        Returns
        -------
        list[RedemptionsByReward]
            Redemptions grouped by reward.
        """
        params = {}
        if reward_id is not None:
            params["reward_id"] = reward_id
        if status is not None:
            params["status"] = status
        if ids is not None:
            for rid in ids:
                params.setdefault("id", [])
                params["id"].append(rid)
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._fetch_api(
            "GET", "channels/rewards/redemptions", use_user_token=True, params=params
        )
        return [RedemptionsByReward(**entry) for entry in data["data"]]

    async def accept_reward_redemptions(self, ids: list[str]) -> list[FailedRedemption]:
        """Accept pending reward redemptions. Requires ``channel:rewards:write`` scope.

        Parameters
        ----------
        ids: list[str]
            Redemption IDs to accept (1-25, must be unique).

        Returns
        -------
        list[FailedRedemption]
            A list of failed redemptions (empty if all succeeded).
        """
        data = await self._fetch_api(
            "POST",
            "channels/rewards/redemptions/accept",
            use_user_token=True,
            json={"ids": ids},
        )
        return [FailedRedemption(**r) for r in data.get("data", [])]

    async def reject_reward_redemptions(self, ids: list[str]) -> list[FailedRedemption]:
        """Reject pending reward redemptions. Requires ``channel:rewards:write`` scope.

        Parameters
        ----------
        ids: list[str]
            Redemption IDs to reject (1-25, must be unique).

        Returns
        -------
        list[FailedRedemption]
            A list of failed redemptions (empty if all succeeded).
        """
        data = await self._fetch_api(
            "POST",
            "channels/rewards/redemptions/reject",
            use_user_token=True,
            json={"ids": ids},
        )
        return [FailedRedemption(**r) for r in data.get("data", [])]

    # ---------- KICKs ----------

    async def fetch_kicks_leaderboard(self, top: int = 10) -> KicksLeaderboard:
        """Get the KICKs leaderboard. Requires ``kicks:read`` scope.

        Parameters
        ----------
        top: int
            Number of top entries (1-100, default 10).

        Returns
        -------
        KicksLeaderboard
            The leaderboard with lifetime, month, and week rankings.
        """
        data = await self._fetch_api(
            "GET", "kicks/leaderboard", use_user_token=True, params={"top": top}
        )
        return KicksLeaderboard(**data["data"])

    # ---------- Events / Subscriptions ----------

    async def fetch_events_subscriptions(self) -> list[EventsSubscription]:
        """Get event subscriptions.

        Returns
        -------
        list[EventsSubscription]
            A list of EventsSubscription data.
        """
        data = await self._fetch_api("GET", "events/subscriptions")
        return [EventsSubscription(**sub) for sub in data["data"]]

    async def subscribe_to_event(
        self, event_type: WebhookEvent, user_id: int
    ) -> EventsSubscriptionCreated:
        """Subscribe to an event.

        Parameters
        ----------
        event_type: WebhookEvent
            The event type to subscribe to.
        user_id: int
            The user ID to subscribe to.

        Returns
        -------
        EventsSubscriptionCreated
            The created event subscription if successful, otherwise None.
        """
        request_data = {
            "events": [
                {
                    "name": event_type.value,
                    "version": 1,
                }
            ],
            "broadcaster_user_id": user_id,
            "method": "webhook",
        }
        data = await self._fetch_api("POST", "events/subscriptions", json=request_data)
        return EventsSubscriptionCreated(**data["data"][0])

    async def unsubscribe_from_event(self, subscription_id: str) -> None:
        """Unsubscribe from an event.

        Parameters
        ----------
        subscription_id: str
            The subscription ID to unsubscribe from.
        """
        await self._fetch_api("DELETE", "events/subscriptions", params={"id": subscription_id})
