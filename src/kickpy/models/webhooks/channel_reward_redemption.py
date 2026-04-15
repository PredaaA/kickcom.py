from dataclasses import dataclass
from datetime import datetime

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class Reward:
    """Represents a channel reward."""

    id: str
    title: str
    cost: int
    description: str


@dataclass(slots=True)
class ChannelRewardRedemption:
    """Represents a channel reward redemption updated event from a webhook."""

    id: str
    user_input: str
    status: str
    redeemed_at: datetime
    reward: Reward
    redeemer: User
    broadcaster: User

    def __post_init__(self) -> None:
        self.redeemed_at = datetime.fromisoformat(self.redeemed_at.replace("Z", "+00:00"))
        self.reward = Reward(**self.reward)
        self.redeemer = User(**self.redeemer)
        self.broadcaster = User(**self.broadcaster)
