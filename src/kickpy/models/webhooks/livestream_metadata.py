from dataclasses import dataclass

from kickpy.models.categories import Category
from kickpy.models.webhooks._shared import User


@dataclass(slots=True)
class LivestreamMetadata:
    """Represents a live stream metadata."""

    title: str
    language: str
    has_mature_content: bool
    category: Category

    def __post_init__(self) -> None:
        self.category = Category(**self.category)


@dataclass(slots=True)
class LiveStreamMetadataUpdated:
    """Represents a live stream status from a webhook."""

    broadcaster: User
    metadata: LivestreamMetadata

    def __post_init__(self) -> None:
        self.broadcaster = User(**self.broadcaster)
        self.metadata = LivestreamMetadata(**self.metadata)
