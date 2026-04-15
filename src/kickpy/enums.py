from enum import Enum


class Scope(Enum):
    """Represents the available OAuth scopes."""

    USER_READ = "user:read"
    CHANNEL_READ = "channel:read"
    CHANNEL_WRITE = "channel:write"
    CHANNEL_REWARDS_READ = "channel:rewards:read"
    CHANNEL_REWARDS_WRITE = "channel:rewards:write"
    CHAT_WRITE = "chat:write"
    STREAMKEY_READ = "streamkey:read"
    EVENTS_SUBSCRIBE = "events:subscribe"
    MODERATION_BAN = "moderation:ban"
    MODERATION_CHAT_MESSAGE_MANAGE = "moderation:chat_message:manage"
    KICKS_READ = "kicks:read"
