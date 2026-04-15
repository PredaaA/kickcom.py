from enum import Enum


class WebhookEvent(Enum):
    """Represents the type of webhook events."""

    CHAT_MESSAGE_SENT = "chat.message.sent"
    CHANNEL_FOLLOWED = "channel.followed"
    CHANNEL_SUB_NEW = "channel.subscription.new"
    CHANNEL_SUB_GIFTS = "channel.subscription.gifts"
    CHANNEL_SUB_RENEWAL = "channel.subscription.renewal"
    LIVESTREAM_STATUS_UPDATED = "livestream.status.updated"
    LIVESTREAM_METADATA_UPDATED = "livestream.metadata.updated"
    MODERATION_USER_BANNED = "channel.moderation.user_banned"
    KICKS_GIFTED = "kicks.gifted"
    CHANNEL_REWARD_REDEMPTION_UPDATED = "channel.reward.redemption.updated"
