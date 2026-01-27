from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Stream:
    """Represents a Kick.com stream."""

    url: str
    key: str
    is_live: bool
    is_mature: bool
    language: str
    start_time: datetime
    thumbnail: str
    viewer_count: int
    custom_tags: list[str] | None = None

    def __post_init__(self) -> None:
        self.start_time = datetime.fromisoformat(self.start_time)
        self.custom_tags = list(self.custom_tags) if self.custom_tags is not None else []
