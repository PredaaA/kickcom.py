from dataclasses import dataclass


@dataclass(slots=True)
class Badge:
    """Represents a badge from a webhook."""

    text: str
    type: str
    count: int | None


@dataclass(slots=True)
class Identity:
    """Represents a user's identity from a webhook."""

    username_color: str
    badges: list[Badge]

    def __post_init__(self) -> None:
        self.badges = [Badge(**badge) for badge in self.badges] if self.badges else []


@dataclass(slots=True)
class User:
    """Represents a user from a webhook.

    Some events (e.g. kicks.gifted, channel.reward.redemption.updated) use a
    compact user object that omits ``is_anonymous`` and ``identity``.
    """

    user_id: int
    username: str
    is_verified: bool
    profile_picture: str
    channel_slug: str
    is_anonymous: bool = False
    identity: Identity | None = None

    def __post_init__(self) -> None:
        self.identity = (
            Identity(**self.identity)
            if self.identity and isinstance(self.identity, dict)
            else self.identity
        )
