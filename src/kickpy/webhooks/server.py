from __future__ import annotations

import asyncio
import base64
import logging
import os
import socket
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, Type, Union

import yarl
from aiohttp import web
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

try:
    from ssl import SSLContext
except ImportError:
    SSLContext = Any

from kickpy.models.webhooks import (
    ALL_PAYLOADS,
    ChannelFollow,
    ChannelSubCreated,
    ChannelSubGifts,
    ChannelSubRenewal,
    ChatMessage,
    LiveStreamStatusUpdated,
)
from kickpy.utils import json_loads
from kickpy.webhooks.enums import WebhookEvent

if TYPE_CHECKING:
    from kickpy.client import KickClient

log = logging.getLogger(__name__)

_ENUM_TO_MODEL: dict[WebhookEvent, ALL_PAYLOADS] = {
    WebhookEvent.CHANNEL_FOLLOWED: ChannelFollow,
    WebhookEvent.CHANNEL_SUB_NEW: ChannelSubCreated,
    WebhookEvent.CHANNEL_SUB_GIFTS: ChannelSubGifts,
    WebhookEvent.CHANNEL_SUB_RENEWAL: ChannelSubRenewal,
    WebhookEvent.CHAT_MESSAGE_SENT: ChatMessage,
    WebhookEvent.LIVESTREAM_STATUS_UPDATED: LiveStreamStatusUpdated,
}


class Dispatcher:
    """A simple event dispatcher for webhook events."""

    def __init__(self) -> None:
        self._listeners: dict[WebhookEvent, list[Callable]] = {}

    def listen(self, event: WebhookEvent, callback: Callable) -> None:
        """Add a listener for an event."""
        if event not in WebhookEvent:
            raise ValueError("Invalid event type")

        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(callback)

    def dispatch(self, event: WebhookEvent, payload: ALL_PAYLOADS) -> None:
        """Dispatch an event to all listeners."""
        if event not in WebhookEvent:
            raise ValueError("Invalid event type")

        if event in self._listeners:
            for callback in self._listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    asyncio.create_task(callback(payload))
                else:
                    callback(payload)


# Took more than inspiration from https://github.com/PythonistaGuild/TwitchIO/blob/v2.10.0/twitchio/ext/eventsub/server.py
# Mostly about the aiohttp server runner
class WebhookServer(web.Application):
    def __init__(self, client: KickClient, callback_route: str, *args, **kwargs):
        self.client: KickClient = client
        self._public_key = None
        self.dispatcher = Dispatcher()

        super().__init__(*args, **kwargs)
        self.router.add_post(yarl.URL(callback_route).path, self.handle_webhook)
        self._closing = asyncio.Event()

    async def listen(self, **kwargs):
        self._closing.clear()
        asyncio.create_task(self._run_app(**kwargs))

    def stop(self):
        self._closing.set()
        self.dispatcher._listeners.clear()

    async def _verify_signature(self, message: bytes, signature_b64: bytes) -> bool:
        if not self._public_key:
            self._public_key = await self.client.fetch_public_key()

        try:
            public_key = serialization.load_pem_public_key(self._public_key)
            decoded_signature = base64.b64decode(signature_b64)
        except Exception:
            return False

        try:
            public_key.verify(decoded_signature, message, padding.PKCS1v15(), hashes.SHA256())
        except Exception:
            return False

        return True

    async def handle_webhook(self, request: web.Request):
        webhook_event = request.headers.get("Kick-Event-Type")
        if webhook_event is None:
            return web.Response(status=400)

        if webhook_event not in WebhookEvent:
            return web.Response(status=400)

        message_id = request.headers.get("Kick-Event-Message-Id")
        subscription_id = request.headers.get("Kick-Event-Subscription-Id")
        event_signature = request.headers.get("Kick-Event-Signature")
        event_timestamp = request.headers.get("Kick-Event-Message-Timestamp")
        event_version = request.headers.get("Kick-Event-Version")

        if None in (message_id, subscription_id, event_signature, event_timestamp, event_version):
            return web.Response(status=400)

        request_body = await request.text()
        signature_valid = await self._verify_signature(
            f"{message_id}.{event_timestamp}.{request_body}".encode(),
            event_signature.encode(),
        )
        if not signature_valid:
            return web.Response(status=400)

        data: dict = await request.json(loads=json_loads)
        payload = _ENUM_TO_MODEL[WebhookEvent(webhook_event)](**data)
        self.dispatcher.dispatch(WebhookEvent(webhook_event), payload)

        return web.Response(status=200)

    async def _run_app(  # noqa: C901
        self,
        *,
        host: Optional[Union[str, web.HostSequence]] = None,
        port: Optional[int] = None,
        path: Optional[str] = None,
        sock: Optional[socket.socket] = None,
        shutdown_timeout: float = 60.0,
        keepalive_timeout: float = 75.0,
        ssl_context: Optional[SSLContext] = None,
        backlog: int = 128,
        access_log_class: Type[web.AbstractAccessLogger] = web.AccessLogger,
        access_log_format: str = web.AccessLogger.LOG_FORMAT,
        access_log: Optional[logging.Logger] = web.access_logger,
        handle_signals: bool = True,
        reuse_address: Optional[bool] = None,
        reuse_port: Optional[bool] = None,
        handler_cancellation: bool = False,
    ) -> None:
        app = self

        runner = web.AppRunner(
            app,
            handle_signals=handle_signals,
            access_log_class=access_log_class,
            access_log_format=access_log_format,
            access_log=access_log,
            keepalive_timeout=keepalive_timeout,
            shutdown_timeout=shutdown_timeout,
            handler_cancellation=handler_cancellation,
        )

        await runner.setup()

        sites = []

        try:
            if host is not None:
                if isinstance(host, (str, bytes, bytearray, memoryview)):
                    sites.append(
                        web.TCPSite(
                            runner,
                            host,
                            port,
                            ssl_context=ssl_context,
                            backlog=backlog,
                            reuse_address=reuse_address,
                            reuse_port=reuse_port,
                        )
                    )
                else:
                    for h in host:
                        sites.append(
                            web.TCPSite(
                                runner,
                                h,
                                port,
                                ssl_context=ssl_context,
                                backlog=backlog,
                                reuse_address=reuse_address,
                                reuse_port=reuse_port,
                            )
                        )
            elif path is None and sock is None or port is not None:
                sites.append(
                    web.TCPSite(
                        runner,
                        port=port,
                        ssl_context=ssl_context,
                        backlog=backlog,
                        reuse_address=reuse_address,
                        reuse_port=reuse_port,
                    )
                )

            if path is not None:
                if isinstance(path, (str, os.PathLike)):
                    sites.append(
                        web.UnixSite(
                            runner,
                            path,
                            ssl_context=ssl_context,
                            backlog=backlog,
                        )
                    )
                else:
                    for p in path:
                        sites.append(
                            web.UnixSite(
                                runner,
                                p,
                                ssl_context=ssl_context,
                                backlog=backlog,
                            )
                        )

            if sock is not None:
                if not isinstance(sock, Iterable):
                    sites.append(
                        web.SockSite(
                            runner,
                            sock,
                            ssl_context=ssl_context,
                            backlog=backlog,
                        )
                    )
                else:
                    for s in sock:
                        sites.append(
                            web.SockSite(
                                runner,
                                s,
                                ssl_context=ssl_context,
                                backlog=backlog,
                            )
                        )
            for site in sites:
                await site.start()

            names = sorted(str(s.name) for s in runner.sites)
            log.debug("Running Webhook server on %s", ", ".join(names))

            await self._closing.wait()
        finally:
            await runner.cleanup()
