from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class Gift:
    """Represents a gift from a kicks gifted webhook."""

    amount: int
    name: str
    type: str
    tier: str
    message: str


@dataclass(slots=True)
class KicksGifted:
    """Represents a kicks gifted event from a webhook."""

    broadcaster: User
    sender: User
    gift: Gift
    created_at: datetime

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.sender = User(**self.sender)
        self.gift = Gift(**self.gift)
        self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
