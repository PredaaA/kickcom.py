# Webhook Server Setup

kickcom.py includes a webhook server to receive real-time events from Kick.

## Basic Setup

```python
import asyncio
from kickpy import KickClient, WebhookEvent, WebhookServer
from kickpy.models.webhooks.chat_message import ChatMessage

def on_chat_message(payload: ChatMessage):
    print(f"{payload.sender.username}: {payload.content}")

async def main():
    client = KickClient("CLIENT_ID", "CLIENT_SECRET")
    server = WebhookServer(client, callback_route="/webhooks/kick")

    server.dispatcher.listen(WebhookEvent.CHAT_MESSAGE_SENT, on_chat_message)

    await server.listen(host="0.0.0.0", port=3000, access_log=None)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.run_forever()
```

## How It Works

1. **Create a `WebhookServer`** with a `KickClient` and a callback route path
2. **Register listeners** on the dispatcher for specific event types
3. **Start the server** -- it listens for incoming POST requests from Kick
4. **Signature verification** is automatic -- the server fetches the Kick public key and validates every request using RSA PKCS1v15 + SHA-256

## Subscribing to Events

Before receiving events, you must subscribe to them via the API:

```python
await client.subscribe_to_event(
    WebhookEvent.CHAT_MESSAGE_SENT,
    user_id=4377088,  # broadcaster user ID
)
```

To list or remove subscriptions:

```python
# List all subscriptions
subs = await client.fetch_events_subscriptions()
for sub in subs:
    print(f"{sub.event} -> {sub.id}")

# Unsubscribe
await client.unsubscribe_from_event(sub.id)
```

## Async Listeners

Listeners can be either sync or async:

```python
async def on_follow(payload):
    print(f"New follower: {payload.follower.username}")
    # You can await async operations here

server.dispatcher.listen(WebhookEvent.CHANNEL_FOLLOWED, on_follow)
```

## Multiple Event Types

Register multiple listeners for different events:

```python
from kickpy.models.webhooks import (
    ChatMessage,
    ChannelFollow,
    LiveStreamStatusUpdated,
    ModerationBanned,
)

server.dispatcher.listen(WebhookEvent.CHAT_MESSAGE_SENT, on_chat)
server.dispatcher.listen(WebhookEvent.CHANNEL_FOLLOWED, on_follow)
server.dispatcher.listen(WebhookEvent.LIVESTREAM_STATUS_UPDATED, on_stream_status)
server.dispatcher.listen(WebhookEvent.MODERATION_USER_BANNED, on_ban)
```

## Signature Verification

Kick signs every webhook delivery with an RSA signature. The server verifies this automatically:

1. Fetches the public key from `GET /public/v1/public-key` (cached after first fetch)
2. Constructs the message: `{message_id}.{timestamp}.{body}`
3. Verifies the `Kick-Event-Signature` header using RSA PKCS1v15 + SHA-256

Requests that fail verification are rejected with HTTP 400.

## Webhook Headers

Every delivery includes these headers:

| Header | Description |
|--------|-------------|
| `Kick-Event-Message-Id` | Unique message ID (use for idempotency) |
| `Kick-Event-Subscription-Id` | The subscription that triggered this event |
| `Kick-Event-Signature` | Base64-encoded RSA signature |
| `Kick-Event-Message-Timestamp` | RFC 3339 timestamp |
| `Kick-Event-Type` | Event type string (e.g., `chat.message.sent`) |
| `Kick-Event-Version` | Event version (e.g., `1`) |

!!! warning
    Kick will automatically unsubscribe your app from an event type if webhook delivery fails for more than **1 day**.
