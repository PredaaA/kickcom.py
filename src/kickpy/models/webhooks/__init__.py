from typing import Union

from kickpy.models.webhooks.channel_follow import ChannelFollow as ChannelFollow
from kickpy.models.webhooks.channel_sub_created import ChannelSubCreated as ChannelSubCreated
from kickpy.models.webhooks.channel_sub_gifts import ChannelSubGifts as ChannelSubGifts
from kickpy.models.webhooks.channel_sub_renewal import ChannelSubRenewal as ChannelSubRenewal
from kickpy.models.webhooks.chat_message import ChatMessage as ChatMessage
from kickpy.models.webhooks.livestream_status import (
    LiveStreamStatusUpdated as LiveStreamStatusUpdated,
)

ALL_PAYLOADS = Union[
    ChannelFollow,
    ChannelSubCreated,
    ChannelSubGifts,
    ChannelSubRenewal,
    ChatMessage,
    LiveStreamStatusUpdated,
]
