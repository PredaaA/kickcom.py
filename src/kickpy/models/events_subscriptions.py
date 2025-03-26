from dataclasses import dataclass
from datetime import datetime


@dataclass
class EventsSubscription:
    """Represents a Kick.com event subscriptions."""

    app_id: str
    broadcaster_user_id: int
    created_at: datetime
    event: str
    id: str
    method: str
    updated_at: datetime
    version: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            app_id=data["app_id"],
            broadcaster_user_id=data["broadcaster_user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            event=data["event"],
            id=data["id"],
            method=data["method"],
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data["version"],
        )


@dataclass
class EventsSubscriptionCreated:
    """Represents a Kick.com event subscriptions created."""

    # error: str
    name: str
    subscription_id: str
    version: int
