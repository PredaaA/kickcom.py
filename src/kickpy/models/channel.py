from dataclasses import dataclass

from .categories import Category
from .stream import Stream


@dataclass(slots=True)
class Channel:
    """Represents a Kick.com channel."""

    broadcaster_user_id: int
    slug: str
    channel_description: str
    banner_picture: str
    stream: Stream
    stream_title: str
    category: Category

    def __post_init__(self) -> None:
        self.stream = Stream(**self.stream)
        self.category = Category(**self.category)
