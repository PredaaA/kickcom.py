import logging
from datetime import datetime
from typing import Any, Dict, Union

import aiohttp

from kickpy import __version__, utils
from kickpy.errors import (
    BadRequest,
    Forbidden,
    InternalServerError,
    NotFound,
    Ratelimited,
    Unauthorized,
)
from kickpy.logger import init_logging
from kickpy.models.access_token import AccessToken
from kickpy.models.categories import Category
from kickpy.models.channel import Channel
from kickpy.models.events_subscriptions import EventsSubscription, EventsSubscriptionCreated
from kickpy.models.user import User
from kickpy.webhooks.enums import WebhookEvent

logging_listener = init_logging()
log = logging.getLogger(__name__)

USER_AGENT = f"kickcom.py/{__version__}"


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    if response.headers.get("Content-Type") == "application/json":
        return utils.json_loads(text)

    return text


class KickClient:
    def __init__(
        self, client_id: str, client_secret: str, launch_webhook_server: bool = False
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: AccessToken | None = None

        self.id_session = aiohttp.ClientSession(
            base_url="https://id.kick.com", headers={"User-Agent": USER_AGENT}
        )
        self.api_session = aiohttp.ClientSession(
            base_url="https://api.kick.com/public/v1/", headers={"User-Agent": USER_AGENT}
        )

    async def close(self):
        """Close the client and all tasks."""
        await self.id_session.close()
        await self.api_session.close()
        logging_listener.stop()

    async def _fetch_api(self, method: str, endpoint: str, **kwargs) -> dict:
        token = await self._fetch_access_token()

        async with self.api_session.request(
            method,
            endpoint,
            headers={"Authorization": f"Bearer {token.access_token}"},
            **kwargs,
        ) as resp:
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

        return data

    async def _fetch_access_token(self) -> AccessToken:
        if self._access_token and self._access_token.expires_at > datetime.now():
            return self._access_token

        try:
            with open(".kick.token.json", "r") as f:
                json_data = utils.json_loads(f.read())
                access_token = AccessToken.from_dict(json_data)
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

            data = await resp.json()

        access_token = AccessToken.from_dict(data)
        with open(".kick.token.json", "w+") as f:
            f.write(utils.json_dumps(access_token.to_dict()))

        self._access_token = access_token
        return access_token

    async def fetch_public_key(self) -> bytes:
        """Get the public key of the Kick.com API.

        Returns
        -------
        str
            The public key data.
        """
        data = await self._fetch_api("GET", "public-key")

        public_key: str = data["data"]["public_key"]
        return public_key.encode()

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

    async def fetch_channel(self, user_id: int) -> Channel:
        """Get a channel by the broadcaster user ID.

        Parameters
        ----------
        user_id: int
            The broadcaster user ID.

        Returns
        -------
        Channel
            The channel data.
        """
        data = await self._fetch_api("GET", "channels", params={"broadcaster_user_id": user_id})
        return Channel.from_dict(data["data"][0])

    async def fetch_categories(self, query: str) -> list[Category]:
        """Get categories by a query.

        Parameters
        ----------
        query: str
            The query to search for.

        Returns
        -------
        list[Category]
            A list of categories data.
        """
        data = await self._fetch_api("GET", "categories", params={"query": query})
        return [Category(**category) for category in data["data"]]

    async def fetch_events_subscriptions(self) -> list[EventsSubscription]:
        """Get event subscriptions.

        Returns
        -------
        list[EventsSubscription]
            A list of EventsSubscription data.
        """
        data = await self._fetch_api("GET", "events/subscriptions")
        return [EventsSubscription.from_dict(sub) for sub in data["data"]]

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

        Returns
        -------
        bool
            True if successful, otherwise False.
        """
        await self._fetch_api("DELETE", "events/subscriptions", params={"id": subscription_id})
