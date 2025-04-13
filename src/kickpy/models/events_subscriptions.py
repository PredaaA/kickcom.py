from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
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

    def __post_init__(self) -> None:
        self.created_at = datetime.fromisoformat(self.created_at)
        self.updated_at = datetime.fromisoformat(self.updated_at)


@dataclass(slots=True)
class EventsSubscriptionCreated:
    """Represents a Kick.com event subscriptions created."""

    # error: str
    name: str
    subscription_id: str
    version: int
