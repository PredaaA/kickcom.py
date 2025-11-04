from dataclasses import dataclass

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class Metadata:
    """Represents metadata for a moderation banned webhook."""

    reason: str
    created_at: str
    expires_at: str | None  # null for permanent bans


@dataclass(slots=True)
class ModerationBanned:
    """Represents a moderation banned event from a webhook."""

    broadcaster: User
    moderator: User
    banned_user: User
    metadata: Metadata

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.moderator = User(**self.moderator)
        self.banned_user = User(**self.banned_user)
        self.metadata = Metadata(**self.metadata)
