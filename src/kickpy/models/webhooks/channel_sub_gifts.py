from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class ChannelSubGifts:
    """Represents a channel subscription gift event from a webhook."""

    broadcaster: User
    gifter: User | None
    giftees: list[User]
    created_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.gifter = User(**self.gifter) if self.gifter else None
        self.giftees = [User(**giftee) for giftee in self.giftees]
        self.created_at = datetime.fromisoformat(self.created_at)
        self.expires_at = datetime.fromisoformat(self.expires_at)
