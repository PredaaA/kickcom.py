# kickcom.py

Modern async Python wrapper for the [Kick.com](https://kick.com) API - OAuth 2.1 PKCE, typed models, webhook server with signature verification, and full coverage of chat, channels, livestreams, moderation, and rewards.

---

## Features

- Full coverage of the [Kick Public API](https://docs.kick.com/) (users, channels, livestreams, categories, chat, moderation, rewards, KICKs, events)
- **OAuth 2.1 + PKCE** authentication with built-in browser flow and automatic token refresh
- **Webhook server** with cryptographic signature verification for real-time events
- Fully typed dataclass models for all API responses and webhook payloads
- Optional speed extras (`orjson`, `aiodns`, `Brotli`) for faster serialization and networking
- Async/await powered by [aiohttp](https://docs.aiohttp.org/)

## Quick Example

```python
import asyncio
from kickpy import KickClient

async def main():
    client = KickClient("CLIENT_ID", "CLIENT_SECRET")

    user = await client.fetch_user(4377088)
    print(user.name)

    await client.close()

asyncio.run(main())
```

## Next Steps

- [Getting Started](getting-started.md) - Install and make your first API call
- [Authentication](authentication.md) - App tokens, user tokens, and OAuth flow
- [API Reference](api/client.md) - All client methods, models, enums, and errors
- [Webhooks](webhooks/setup.md) - Set up a webhook server and handle real-time events
