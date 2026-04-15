from dataclasses import dataclass


@dataclass(slots=True)
class ChatResponse:
    """Represents the response from sending a chat message."""

    is_sent: bool
    message_id: str
