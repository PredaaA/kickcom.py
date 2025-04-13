from dataclasses import dataclass
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
class ChatMessage:
    message_id: str
    broadcaster: User
    sender: User
    content: str
    emotes: List[Emote]

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.sender = User(**self.sender)
        self.emotes = [Emote(**emote) for emote in self.emotes]
