# kickcom.py

[![PyPI](https://img.shields.io/pypi/v/kickcom.py)](https://pypi.org/project/kickcom.py)

Async library for Kick.com API and webhooks

> [!NOTE]  
> This is in alpha stage, it currently only supports app access tokens. PRs to improve are very welcome!

Find the kick.com [API documentation here](https://docs.kick.com/)

## Installation

```bash
pip install kickcom.py
```

## Client

All endpoints available for app access tokens are available.

```python
from kickpy.client import Client

kick_client = Client("KICK_CLIENT_ID", "KICK_CLIENT_SECRET")

user = await kick_client.fetch_user(4377088)
# Returns:
# User(user_id=4377088, name='KickBot', email='', profile_picture='https://files.kick.com/images/user/4377088/profile_image/conversion/8dde6c21-7008-43d1-b6ac-7d9c34b7d9cc-fullsize.webp')

channel = await kick_client.fetch_channel(4377088)
# Returns:
# Channel(broadcaster_user_id=4377088, slug='kickbot', channel_description='Official bot of https://kickbot.app, the #1 tool for Kick streamers. | VOD Downloader | !clip command | Custom Commands | Timed Messages | Customizable overlays | Stream Deck Plugin |\n\nContact: contact@kickbot.app', banner_picture='https://files.kick.com/images/channel/4295080/banner_image/b0d66fa3-3a4e-45d5-94ea-84d0590990d7', stream=Stream(url='', key='', is_live=False, is_mature=False, language='', start_time='0001-01-01T00:00:00Z', viewer_count=0), stream_title='', category=Category(id=0, name='', thumbnail=''))
```

## Webhook server

Support for receiving webhooks events from Kick is also available.

```python
from kickpy.client import Client
from kickpy.models.webhooks.chat_message import ChatMessage
from kickpy.webhooks.enums import WebhookEvent
from kickpy.webhooks.server import WebhookServer

def on_chat_message(payload: ChatMessage):
    print(payload)


async def main():
    kick_client = Client("KICK_CLIENT_ID", "KICK_CLIENT_SECRET")
    webhook_server = WebhookServer(kick_client, callback_route="KICK_CALLBACK_ROUTE")
    webhook_server.dispatcher.listen(WebhookEvent.CHAT_MESSAGE_SENT, on_chat_message)

    await webhook_server.listen(host="localhost", port=3000, access_log=None)


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.run_forever()
```
