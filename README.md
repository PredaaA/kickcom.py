# kickcom.py

[![PyPI](https://img.shields.io/pypi/v/kickcom.py)](https://pypi.org/project/kickcom.py)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://predaaa.github.io/kickcom.py)

Async library for Kick.com API and webhooks

[Documentation](https://predaaa.github.io/kickcom.py) | [Kick API Reference](https://docs.kick.com/)

## Installation

```bash
pip install kickcom.py
```

Optional speed extras:

```bash
pip install kickcom.py[speed]
```

## Quick Start

### App Access Token (Bot / Server-side)

```python
import asyncio
from kickpy import KickClient

async def main():
    client = KickClient("KICK_CLIENT_ID", "KICK_CLIENT_SECRET")

    user = await client.fetch_user(4377088)
    print(user.name)

    channel = await client.fetch_channel(slug="kickbot")
    print(channel.stream_title)

    await client.close()

asyncio.run(main())
```

### User Access Token (OAuth 2.1 + PKCE)

Some endpoints require a user token. The library handles the full OAuth flow with a built-in local callback server:

```python
import asyncio
from kickpy import KickClient, Scope

async def main():
    client = KickClient("KICK_CLIENT_ID", "KICK_CLIENT_SECRET")

    # Opens browser, captures callback on localhost, exchanges code for tokens
    await client.authenticate(
        scopes=[Scope.CHAT_WRITE, Scope.MODERATION_BAN],
        port=3000,  # redirect URI must be http://127.0.0.1:3000/callback in your Kick app settings
    )

    # User token endpoints are now available
    await client.send_chat_message("Hello from kickcom.py!", broadcaster_user_id=4377088)

    await client.close()

asyncio.run(main())
```

If you handle OAuth externally, you can inject tokens directly:

```python
client.set_user_token(
    access_token="...",
    refresh_token="...",
    expires_in=3600,
    scope="chat:write moderation:ban",
)
```

## API Reference

### Users

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_user(user_id)` | Get a user by ID | App |

### Channels

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_channel(user_id?, slug?)` | Get a channel by broadcaster ID or slug | App |
| `update_channel(category_id?, stream_title?, custom_tags?)` | Update channel metadata | User (`channel:write`) |

### Livestreams

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_livestream(broadcaster_user_id)` | Get a single livestream | App |
| `fetch_livestreams(broadcaster_user_id?, category_id?, language?, limit?, sort?)` | Get multiple livestreams | App |
| `fetch_livestream_stats()` | Get global livestream stats | App |

### Categories

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_categories(query?, name?, tag?, category_id?, cursor?, limit?)` | Search categories (v2) | App |

### Chat

| Method | Description | Token |
|--------|-------------|-------|
| `send_chat_message(content, message_type?, broadcaster_user_id?, reply_to_message_id?)` | Send a chat message | User (`chat:write`) |
| `delete_chat_message(message_id)` | Delete a chat message | User (`moderation:chat_message:manage`) |

### Moderation

| Method | Description | Token |
|--------|-------------|-------|
| `ban_user(broadcaster_user_id, user_id, duration?, reason?)` | Ban or timeout a user | User (`moderation:ban`) |
| `unban_user(broadcaster_user_id, user_id)` | Unban a user | User (`moderation:ban`) |

### Channel Rewards

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_channel_rewards()` | List channel point rewards | User (`channel:rewards:read`) |
| `create_channel_reward(cost, title, ...)` | Create a reward | User (`channel:rewards:write`) |
| `update_channel_reward(reward_id, ...)` | Update a reward | User (`channel:rewards:write`) |
| `delete_channel_reward(reward_id)` | Delete a reward | User (`channel:rewards:write`) |
| `fetch_reward_redemptions(reward_id?, status?, ids?, cursor?)` | Get redemptions | User (`channel:rewards:read`) |
| `accept_reward_redemptions(ids)` | Accept pending redemptions | User (`channel:rewards:write`) |
| `reject_reward_redemptions(ids)` | Reject pending redemptions | User (`channel:rewards:write`) |

### KICKs

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_kicks_leaderboard(top?)` | Get KICKs leaderboard | User (`kicks:read`) |

### Events / Subscriptions

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_events_subscriptions()` | List event subscriptions | App |
| `subscribe_to_event(event_type, user_id)` | Subscribe to a webhook event | App |
| `unsubscribe_from_event(subscription_id)` | Unsubscribe from an event | App |

### Other

| Method | Description | Token |
|--------|-------------|-------|
| `fetch_public_key()` | Get the Kick public key for webhook verification | App |

## OAuth Scopes

```python
from kickpy import Scope

Scope.USER_READ                       # user:read
Scope.CHANNEL_READ                    # channel:read
Scope.CHANNEL_WRITE                   # channel:write
Scope.CHANNEL_REWARDS_READ            # channel:rewards:read
Scope.CHANNEL_REWARDS_WRITE           # channel:rewards:write
Scope.CHAT_WRITE                      # chat:write
Scope.STREAMKEY_READ                  # streamkey:read
Scope.EVENTS_SUBSCRIBE                # events:subscribe
Scope.MODERATION_BAN                  # moderation:ban
Scope.MODERATION_CHAT_MESSAGE_MANAGE  # moderation:chat_message:manage
Scope.KICKS_READ                      # kicks:read
```

## Webhook Server

Receive and process webhook events from Kick:

```python
import asyncio
from kickpy import KickClient, WebhookEvent, WebhookServer
from kickpy.models.webhooks.chat_message import ChatMessage

def on_chat_message(payload: ChatMessage):
    print(f"{payload.sender.username}: {payload.content}")

async def main():
    client = KickClient("KICK_CLIENT_ID", "KICK_CLIENT_SECRET")
    server = WebhookServer(client, callback_route="/webhooks/kick")
    server.dispatcher.listen(WebhookEvent.CHAT_MESSAGE_SENT, on_chat_message)

    await server.listen(host="localhost", port=3000, access_log=None)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.run_forever()
```

### Webhook Events

| Event | Enum |
|-------|------|
| `chat.message.sent` | `WebhookEvent.CHAT_MESSAGE_SENT` |
| `channel.followed` | `WebhookEvent.CHANNEL_FOLLOWED` |
| `channel.subscription.new` | `WebhookEvent.CHANNEL_SUB_NEW` |
| `channel.subscription.gifts` | `WebhookEvent.CHANNEL_SUB_GIFTS` |
| `channel.subscription.renewal` | `WebhookEvent.CHANNEL_SUB_RENEWAL` |
| `livestream.status.updated` | `WebhookEvent.LIVESTREAM_STATUS_UPDATED` |
| `livestream.metadata.updated` | `WebhookEvent.LIVESTREAM_METADATA_UPDATED` |
| `channel.moderation.user_banned` | `WebhookEvent.MODERATION_USER_BANNED` |
| `kicks.gifted` | `WebhookEvent.KICKS_GIFTED` |
| `channel.reward.redemption.updated` | `WebhookEvent.CHANNEL_REWARD_REDEMPTION_UPDATED` |
