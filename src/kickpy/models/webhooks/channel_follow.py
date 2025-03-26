from dataclasses import dataclass

from kickpy.models.webhooks._shared import User


@dataclass
class ChannelFollow:
    """Represents a channel follow event from a webhook."""

    broadcaster: User
    follower: User

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            broadcaster=User(**data["broadcaster"]),
            follower=User(**data["follower"]),
        )
