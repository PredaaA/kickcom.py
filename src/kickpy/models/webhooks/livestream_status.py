from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass
class LiveStreamStatusUpdated:
    """Represents a live stream status from a webhook."""

    broadcaster: User
    is_live: bool
    title: str
    started_at: datetime
    ended_at: datetime | None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster=User(**data["broadcaster"]),
            is_live=data["is_live"],
            title=data["title"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data["ended_at"] else None,
        )
