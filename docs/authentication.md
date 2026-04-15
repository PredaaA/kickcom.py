# Authentication

kickcom.py supports two types of access tokens, matching the Kick API's OAuth 2.1 model.

## App Access Token (Default)

Used automatically when you create a `KickClient`. This is a server-to-server token using the **client credentials** grant type. It gives read-only access to public endpoints.

```python
from kickpy import KickClient

client = KickClient("CLIENT_ID", "CLIENT_SECRET")

# These work with app tokens:
user = await client.fetch_user(123)
channel = await client.fetch_channel(slug="xqc")
streams = await client.fetch_livestreams(limit=10)
categories = await client.fetch_categories(query="Gaming")
```

The app token is automatically fetched on the first API call and cached to `.kick.token.json`. It auto-refreshes when expired.

## User Access Token (OAuth 2.1 + PKCE)

Required for endpoints that act on behalf of a user (chat, moderation, rewards, etc.). The library implements the full OAuth 2.1 Authorization Code flow with PKCE.

### Browser Flow (Built-in)

The simplest approach, the library opens the user's browser and captures the callback:

```python
from kickpy import KickClient, Scope

client = KickClient("CLIENT_ID", "CLIENT_SECRET")

await client.authenticate(
    scopes=[Scope.CHAT_WRITE, Scope.MODERATION_BAN],
    port=3000,
)

# User token endpoints are now available
await client.send_chat_message("Hello!", broadcaster_user_id=123)
```

**What happens:**

1. A local HTTP server starts on `http://127.0.0.1:3000`
2. Your browser opens the Kick authorization page
3. The user approves the requested scopes
4. Kick redirects to `http://127.0.0.1:3000/callback` with the authorization code
5. The library exchanges the code for tokens and stores them in `.kick.user_token.json`
6. The local server shuts down

!!! warning
    Your Kick app's **Redirect URL** must match exactly: `http://127.0.0.1:3000/callback` (or whatever port you choose).

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `scopes` | required | List of `Scope` enum values or scope strings |
| `port` | `3000` | Local port for the callback server |
| `redirect_uri` | auto | Override the redirect URI (default: `http://127.0.0.1:{port}/callback`) |
| `timeout` | `300` | Seconds to wait for the user to authorize (default: 5 minutes) |

### Manual Token Injection

If you handle OAuth externally (e.g., your own web app), inject tokens directly:

```python
client.set_user_token(
    access_token="eyJ...",
    refresh_token="dGhp...",
    expires_in=3600,
    scope="chat:write moderation:ban",
)
```

### Token Caching

- **App tokens** are cached to `.kick.token.json`
- **User tokens** are cached to `.kick.user_token.json`
- On startup, cached tokens are loaded automatically if still valid
- If a user token expires and has a refresh token, it auto-refreshes

## Scopes

| Scope | Enum | Endpoints |
|-------|------|-----------|
| `user:read` | `Scope.USER_READ` | `fetch_user` |
| `channel:read` | `Scope.CHANNEL_READ` | `fetch_channel` |
| `channel:write` | `Scope.CHANNEL_WRITE` | `update_channel` |
| `channel:rewards:read` | `Scope.CHANNEL_REWARDS_READ` | `fetch_channel_rewards`, `fetch_reward_redemptions` |
| `channel:rewards:write` | `Scope.CHANNEL_REWARDS_WRITE` | `create_channel_reward`, `update_channel_reward`, `delete_channel_reward`, `accept_reward_redemptions`, `reject_reward_redemptions` |
| `chat:write` | `Scope.CHAT_WRITE` | `send_chat_message` |
| `streamkey:read` | `Scope.STREAMKEY_READ` | Stream key access |
| `events:subscribe` | `Scope.EVENTS_SUBSCRIBE` | `subscribe_to_event` |
| `moderation:ban` | `Scope.MODERATION_BAN` | `ban_user`, `unban_user` |
| `moderation:chat_message:manage` | `Scope.MODERATION_CHAT_MESSAGE_MANAGE` | `delete_chat_message` |
| `kicks:read` | `Scope.KICKS_READ` | `fetch_kicks_leaderboard` |
