"""
Domain events base classes.
Pure domain layer - no framework dependencies.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    aggregate_id: str | None = None
    event_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.__class__.__name__,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": self.aggregate_id,
            "event_version": self.event_version,
            "payload": self._get_payload(),
        }

    def _get_payload(self) -> dict[str, Any]:
        """Get event-specific payload. Override in subclasses."""
        return {}
