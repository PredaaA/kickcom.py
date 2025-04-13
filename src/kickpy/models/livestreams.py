from dataclasses import dataclass
from datetime import datetime

from kickpy.models.categories import Category


@dataclass(slots=True)
class LiveStream:
    """Represents a Kick.com livestream."""

    broadcaster_user_id: int
    category: Category
    channel_id: int
    has_mature_content: bool
    language: str
    slug: str
    started_at: datetime
    stream_title: str
    thumbnail: str
    viewer_count: int

    def __post_init__(self) -> None:
        self.category = Category(**self.category)
        self.started_at = datetime.fromisoformat(self.started_at)
