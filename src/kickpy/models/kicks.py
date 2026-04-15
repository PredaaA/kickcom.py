from dataclasses import dataclass, field


@dataclass(slots=True)
class KicksLeaderboardEntry:
    """Represents a single entry in the KICKs leaderboard."""

    gifted_amount: int
    rank: int
    user_id: int
    username: str


@dataclass(slots=True)
class KicksLeaderboard:
    """Represents the KICKs leaderboard with lifetime, month, and week rankings."""

    lifetime: list[KicksLeaderboardEntry] = field(default_factory=list)
    month: list[KicksLeaderboardEntry] = field(default_factory=list)
    week: list[KicksLeaderboardEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.lifetime = [
            KicksLeaderboardEntry(**e) if isinstance(e, dict) else e for e in self.lifetime
        ]
        self.month = [KicksLeaderboardEntry(**e) if isinstance(e, dict) else e for e in self.month]
        self.week = [KicksLeaderboardEntry(**e) if isinstance(e, dict) else e for e in self.week]
