from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass
class ChannelSubGifts:
    """Represents a channel subscription gift event from a webhook."""

    broadcaster: User
    gifter: User | None
    giftees: list[User]
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster=User(**data["broadcaster"]),
            gifter=User(**data["gifter"]) if data["gifter"] else None,
            giftees=[User(**giftee) for giftee in data["giftees"]],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
