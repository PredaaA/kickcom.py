from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class EmotePosition:
    s: int  # start position
    e: int  # end position


@dataclass(slots=True)
class Emote:
    emote_id: str
    positions: List[EmotePosition]

    def __post_init__(self) -> None:
        self.positions = [EmotePosition(**position) for position in self.positions]


@dataclass(slots=True)
class Reply:
    """The parent message when a chat message is a reply."""

    message_id: str
    content: str
    sender: User

    def __post_init__(self) -> None:
        self.sender = User(**self.sender) if isinstance(self.sender, dict) else self.sender


@dataclass(slots=True)
class ChatMessage:
    message_id: str
    broadcaster: User
    sender: User
    content: str
    emotes: List[Emote]
    replies_to: Reply | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        self.broadcaster = (
            User(**self.broadcaster) if isinstance(self.broadcaster, dict) else self.broadcaster
        )
        self.sender = User(**self.sender) if isinstance(self.sender, dict) else self.sender
        self.emotes = [Emote(**emote) for emote in self.emotes if isinstance(emote, dict)]
        self.replies_to = (
            Reply(**self.replies_to)
            if self.replies_to and isinstance(self.replies_to, dict)
            else self.replies_to
        )
        self.created_at = (
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
            if isinstance(self.created_at, str)
            else self.created_at
        )
