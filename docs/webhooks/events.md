# Webhook Events

All available webhook event types and their payload models.

## Chat

### chat.message.sent

Fired when a chat message is sent. Enum: `WebhookEvent.CHAT_MESSAGE_SENT`

::: kickpy.models.webhooks.chat_message.ChatMessage

::: kickpy.models.webhooks.chat_message.Reply

::: kickpy.models.webhooks.chat_message.Emote

::: kickpy.models.webhooks.chat_message.EmotePosition

## Channel

### channel.followed

Fired when a user follows a channel. Enum: `WebhookEvent.CHANNEL_FOLLOWED`

::: kickpy.models.webhooks.channel_follow.ChannelFollow

### channel.subscription.new

Fired when a new subscription is created. Enum: `WebhookEvent.CHANNEL_SUB_NEW`

::: kickpy.models.webhooks.channel_sub_created.ChannelSubCreated

### channel.subscription.gifts

Fired when subscriptions are gifted. Enum: `WebhookEvent.CHANNEL_SUB_GIFTS`

::: kickpy.models.webhooks.channel_sub_gifts.ChannelSubGifts

### channel.subscription.renewal

Fired when a subscription is renewed. Enum: `WebhookEvent.CHANNEL_SUB_RENEWAL`

::: kickpy.models.webhooks.channel_sub_renewal.ChannelSubRenewal

### channel.reward.redemption.updated

Fired when a reward redemption status changes. Enum: `WebhookEvent.CHANNEL_REWARD_REDEMPTION_UPDATED`

::: kickpy.models.webhooks.channel_reward_redemption.ChannelRewardRedemption
    options:
      show_root_heading: true
      heading_level: 4

## Livestream

### livestream.status.updated

Fired when a stream goes live or offline. Enum: `WebhookEvent.LIVESTREAM_STATUS_UPDATED`

::: kickpy.models.webhooks.livestream_status.LiveStreamStatusUpdated

### livestream.metadata.updated

Fired when stream metadata changes (title, category, etc.). Enum: `WebhookEvent.LIVESTREAM_METADATA_UPDATED`

::: kickpy.models.webhooks.livestream_metadata.LiveStreamMetadataUpdated

::: kickpy.models.webhooks.livestream_metadata.LivestreamMetadata

## Moderation

### channel.moderation.user_banned

Fired when a user is banned or timed out. Enum: `WebhookEvent.MODERATION_USER_BANNED`

::: kickpy.models.webhooks.moderation_banned.ModerationBanned

::: kickpy.models.webhooks.moderation_banned.Metadata

## KICKs

### kicks.gifted

Fired when KICKs are gifted. Enum: `WebhookEvent.KICKS_GIFTED`

::: kickpy.models.webhooks.kicks_gifted.KicksGifted

::: kickpy.models.webhooks.kicks_gifted.Gift

## Shared Types

These types are used across multiple webhook payloads.

::: kickpy.models.webhooks._shared.User

::: kickpy.models.webhooks._shared.Identity

::: kickpy.models.webhooks._shared.Badge
