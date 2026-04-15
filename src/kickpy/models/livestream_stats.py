from dataclasses import dataclass


@dataclass(slots=True)
class LivestreamStats:
    """Represents livestream statistics."""

    total_count: int
