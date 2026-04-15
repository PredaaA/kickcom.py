# kickcom.py

[![PyPI](https://img.shields.io/pypi/v/kickcom.py)](https://pypi.org/project/kickcom.py)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://predaaa.github.io/kickcom.py)

Modern async Python wrapper for the Kick.com API. OAuth 2.1 PKCE, typed models, webhook server with signature verification, and full coverage of chat, channels, livestreams, moderation, and rewards.

## Features

- Full coverage of the [Kick Public API](https://docs.kick.com/) (users, channels, livestreams, categories, chat, moderation, rewards, KICKs, events)
- **OAuth 2.1 + PKCE** authentication with built-in browser flow and automatic token refresh
- **Webhook server** with cryptographic signature verification for real-time events
- Fully typed dataclass models for all API responses and webhook payloads
- Optional speed extras (`orjson`, `aiodns`, `Brotli`) for faster serialization and networking
- Async/await powered by [aiohttp](https://docs.aiohttp.org/)

## Installation

```bash
pip install kickcom.py
```

Optional speed extras:

```bash
pip install kickcom.py[speed]
```

## Quick Start

```python
import asyncio
from kickpy import KickClient

async def main():
    client = KickClient("CLIENT_ID", "CLIENT_SECRET")

    user = await client.fetch_user(4377088)
    print(user.name)

    channel = await client.fetch_channel(slug="kickbot")
    print(channel.stream_title)

    await client.close()

asyncio.run(main())
```

## Documentation

For full guides and API reference, visit the **[documentation](https://predaaa.github.io/kickcom.py)**.

- [Getting Started](https://predaaa.github.io/kickcom.py/getting-started/) - Install and make your first API call
- [Authentication](https://predaaa.github.io/kickcom.py/authentication/) - App tokens, user tokens, and OAuth flow
- [API Reference](https://predaaa.github.io/kickcom.py/api/client/) - All client methods, models, enums, and errors
- [Webhooks](https://predaaa.github.io/kickcom.py/webhooks/setup/) - Set up a webhook server and handle real-time events
