from dataclasses import dataclass
from typing import List

from kickpy.models.webhooks._shared import User


@dataclass
class EmotePosition:
    s: int  # start position
    e: int  # end position


@dataclass
class Emote:
    emote_id: str
    positions: List[EmotePosition]


@dataclass
class ChatMessage:
    message_id: str
    broadcaster: User
    sender: User
    content: str
    emotes: List[Emote]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            message_id=data["message_id"],
            broadcaster=User(**data["broadcaster"]),
            sender=User(**data["sender"]),
            content=data["content"],
            emotes=[
                Emote(
                    emote_id=emote["emote_id"],
                    positions=[EmotePosition(**pos) for pos in emote["positions"]],
                )
                for emote in data["emotes"]
            ],
        )
