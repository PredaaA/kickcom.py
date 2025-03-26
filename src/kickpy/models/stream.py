from dataclasses import dataclass
from datetime import datetime


@dataclass
class Stream:
    """Represents a Kick.com stream."""

    url: str
    key: str
    is_live: bool
    is_mature: bool
    language: str
    start_time: datetime
    viewer_count: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            url=data["url"],
            key=data["key"],
            is_live=data["is_live"],
            is_mature=data["is_mature"],
            language=data["language"],
            start_time=datetime.fromisoformat(data["start_time"]),
            viewer_count=data["viewer_count"],
        )
