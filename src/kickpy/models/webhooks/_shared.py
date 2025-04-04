from dataclasses import dataclass


@dataclass(slots=True)
class User:
    """Represents a user from a webhook."""

    is_anonymous: bool
    user_id: int
    username: str
    is_verified: bool
    profile_picture: str
    channel_slug: str
