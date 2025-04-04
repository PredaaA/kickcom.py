from dataclasses import dataclass


@dataclass(slots=True)
class User:
    """Represents a Kick.com user."""

    user_id: int
    name: str
    email: str
    profile_picture: str
