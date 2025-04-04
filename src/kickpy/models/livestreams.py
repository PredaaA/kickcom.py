from dataclasses import dataclass
from datetime import datetime

from kickpy.models.categories import Category

# {
#       "broadcaster_user_id": 1,
#       "category": {
#         "id": 1,
#         "name": "text",
#         "thumbnail": "text"
#       },
#       "channel_id": 1,
#       "has_mature_content": true,
#       "language": "text",
#       "slug": "text",
#       "started_at": "text",
#       "stream_title": "text",
#       "thumbnail": "text",
#       "viewer_count": 1
#     }


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster_user_id=data["broadcaster_user_id"],
            category=Category(**data["category"]),
            channel_id=data["channel_id"],
            has_mature_content=data["has_mature_content"],
            language=data["language"],
            slug=data["slug"],
            started_at=datetime.fromisoformat(data["started_at"]),
            stream_title=data["stream_title"],
            thumbnail=data["thumbnail"],
            viewer_count=data["viewer_count"],
        )
