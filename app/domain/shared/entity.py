"""
Base entity class for domain entities.
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from app.domain.shared.events import DomainEvent


@dataclass
class Entity(ABC):
    """Base class for all domain entities."""

    id: UUID = field(default_factory=uuid4)
    _domain_events: list[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def __eq__(self, other: Any) -> bool:
        """Entities are equal if they have the same ID."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be dispatched."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()

    def get_domain_events(self) -> list[DomainEvent]:
        """Get all domain events."""
        return self._domain_events.copy()
