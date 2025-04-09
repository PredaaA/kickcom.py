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
    badges: list[Badge] | None

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            username_color=data["username_color"],
            badges=[Badge(**badge) for badge in data["badges"]] if data.get("badges") else None,
        )


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

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            is_anonymous=data["is_anonymous"],
            user_id=data["user_id"],
            username=data["username"],
            is_verified=data["is_verified"],
            profile_picture=data["profile_picture"],
            channel_slug=data["channel_slug"],
            identity=Identity.from_dict(**data["identity"]) if data.get("identity") else None,
        )
