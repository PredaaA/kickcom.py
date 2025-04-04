from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class ChannelSubRenewal:
    """Represents a channel subscription created renewal from a webhook."""

    broadcaster: User
    subscriber: User
    duration: int
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster=User(**data["broadcaster"]),
            subscriber=User(**data["subscriber"]),
            duration=data["duration"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
