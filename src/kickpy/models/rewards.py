from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ChannelReward:
    """Represents a channel points reward."""

    id: str
    title: str
    cost: int
    description: str
    background_color: str
    is_enabled: bool
    is_paused: bool
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool


@dataclass(slots=True)
class RedemptionUser:
    """Represents a user who redeemed a reward."""

    user_id: int


@dataclass(slots=True)
class MinimalChannelReward:
    """Represents a minimal channel reward in redemption responses."""

    id: str
    title: str
    cost: int | None = None
    description: str | None = None
    can_manage: bool | None = None
    is_deleted: bool | None = None


@dataclass(slots=True)
class ChannelRewardRedemption:
    """Represents a channel reward redemption."""

    id: str
    redeemed_at: datetime
    redeemer: RedemptionUser
    status: str
    user_input: str

    def __post_init__(self) -> None:
        if isinstance(self.redeemed_at, str):
            self.redeemed_at = datetime.fromisoformat(self.redeemed_at.replace("Z", "+00:00"))
        if isinstance(self.redeemer, dict):
            self.redeemer = RedemptionUser(**self.redeemer)


@dataclass(slots=True)
class RedemptionsByReward:
    """Represents redemptions grouped by reward."""

    reward: MinimalChannelReward
    redemptions: list[ChannelRewardRedemption] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.reward, dict):
            self.reward = MinimalChannelReward(**self.reward)
        self.redemptions = [
            ChannelRewardRedemption(**r) if isinstance(r, dict) else r for r in self.redemptions
        ]


@dataclass(slots=True)
class FailedRedemption:
    """Represents a failed redemption in accept/reject responses."""

    id: str
    reason: str
