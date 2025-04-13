from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class LiveStreamStatusUpdated:
    """Represents a live stream status from a webhook."""

    broadcaster: User
    is_live: bool
    title: str
    started_at: datetime
    ended_at: datetime | None

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.started_at = datetime.fromisoformat(self.started_at)
        self.ended_at = datetime.fromisoformat(self.ended_at) if self.ended_at else None
