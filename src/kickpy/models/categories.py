from dataclasses import dataclass


@dataclass(slots=True)
class Category:
    """Represents a Kick.com category."""

    id: int
    name: str
    thumbnail: str
