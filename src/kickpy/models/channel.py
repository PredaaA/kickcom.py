from dataclasses import dataclass

from .categories import Category
from .stream import Stream


@dataclass
class Channel:
    """Represents a Kick.com channel."""

    broadcaster_user_id: int
    slug: str
    channel_description: str
    banner_picture: str
    stream: Stream
    stream_title: str
    category: Category

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster_user_id=data["broadcaster_user_id"],
            slug=data["slug"],
            channel_description=data["channel_description"],
            banner_picture=data["banner_picture"],
            stream=Stream(**data["stream"]),
            stream_title=data["stream_title"],
            category=Category(**data["category"]),
        )
