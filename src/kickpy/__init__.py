"""Async library for Kick.com API and webhooks"""

__version__ = "1.0.1"

from kickpy.client import KickClient
from kickpy.enums import Scope
from kickpy.webhooks.enums import WebhookEvent
from kickpy.webhooks.server import WebhookServer

__all__ = [
    "KickClient",
    "Scope",
    "WebhookEvent",
    "WebhookServer",
]
