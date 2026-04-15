# kickcom.py

Async library for the [Kick.com](https://kick.com) API and webhooks.

---

## Features

- Full coverage of the [Kick Public API](https://docs.kick.com/)
- **App Access Tokens** (client credentials) for server-side use
- **User Access Tokens** (OAuth 2.1 + PKCE) with built-in browser flow
- **Webhook server** with signature verification for real-time events
- Auto-generated API reference from docstrings
- Async/await with [aiohttp](https://docs.aiohttp.org/)

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

- [Getting Started](getting-started.md) -- Install and make your first API call
- [Authentication](authentication.md) -- App tokens vs user tokens
- [API Reference](api/client.md) -- All client methods
- [Webhooks](webhooks/setup.md) -- Receive real-time events
