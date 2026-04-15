# Getting Started

## Installation

```bash
pip install kickcom.py
```

Optional speed extras (orjson, aiodns, Brotli):

```bash
pip install kickcom.py[speed]
```

## Setup

Before using the library, you need a Kick developer application:

1. Create a [Kick](https://kick.com) account and enable 2FA
2. Go to **Account Settings** > **Developer** tab
3. Create an app to get your **Client ID** and **Client Secret**

## First API Call

```python
import asyncio
from kickpy import KickClient

async def main():
    client = KickClient("YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET")

    # Fetch a user by ID
    user = await client.fetch_user(4377088)
    print(f"Name: {user.name}")
    print(f"Profile: {user.profile_picture}")

    # Fetch a channel by slug
    channel = await client.fetch_channel(slug="kickbot")
    print(f"Title: {channel.stream_title}")
    print(f"Live: {channel.stream.is_live}")

    # Search categories
    categories = await client.fetch_categories(query="Gaming")
    for cat in categories:
        print(f"{cat.name} ({cat.id})")

    # Get live streams
    streams = await client.fetch_livestreams(limit=5)
    for stream in streams:
        print(f"{stream.slug}: {stream.viewer_count} viewers")

    await client.close()

asyncio.run(main())
```

!!! note
    `KickClient` uses app access tokens by default (client credentials flow). This gives you read-only access to public data. For write operations (chat, moderation, rewards), you need a [user token](authentication.md).

## Context Manager

You can also use `KickClient` without manually calling `close()`:

```python
async def main():
    client = KickClient("CLIENT_ID", "CLIENT_SECRET")
    try:
        user = await client.fetch_user(4377088)
        print(user.name)
    finally:
        await client.close()
```
