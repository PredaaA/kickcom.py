from dataclasses import dataclass

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class ChannelFollow:
    """Represents a channel follow event from a webhook."""

    broadcaster: User
    follower: User

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.follower = User(**self.follower)
