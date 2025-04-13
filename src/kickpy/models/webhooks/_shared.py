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
    """Represents a user from a webhook."""

    is_anonymous: bool
    user_id: int
    username: str
    is_verified: bool
    profile_picture: str
    channel_slug: str
    identity: Identity | None

    def __post_init__(self) -> None:
        self.identity = Identity(**self.identity) if self.identity else None
