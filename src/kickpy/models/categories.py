from dataclasses import dataclass


@dataclass
class Category:
    """Represents a Kick.com category."""

    id: int
    name: str
    thumbnail: str
