from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class ChannelSubCreated:
    """Represents a channel subscription created event from a webhook."""

    broadcaster: User
    subscriber: User
    duration: int
    created_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.subscriber = User(**self.subscriber)
        self.created_at = datetime.fromisoformat(self.created_at)
        self.expires_at = datetime.fromisoformat(self.expires_at)
