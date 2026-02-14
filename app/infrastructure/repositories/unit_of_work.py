"""
Unit of Work implementation.
Coordinates repositories and manages transactions.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.users.unit_of_work import IUnitOfWork
from app.domain.users.repository import IUserRepository
from app.infrastructure.events.event_bus import IEventBus
from app.infrastructure.repositories.user_repository import UserRepository


class UnitOfWork(IUnitOfWork):
    """
    SQLAlchemy implementation of Unit of Work.
    Manages database transactions and coordinates repositories.
    """

    def __init__(self, session: AsyncSession, event_bus: IEventBus):
        """
        Initialize Unit of Work.

        Args:
            session: SQLAlchemy async session
            event_bus: Event bus for publishing domain events
        """
        self.session = session
        self.event_bus = event_bus
        self.users: IUserRepository = UserRepository(session)
        self._domain_events: list[Any] = []

    async def __aenter__(self) -> "UnitOfWork":
        """Enter async context."""
        return self

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Exit async context."""
        if exc_type is not None:
            await self.rollback()
        else:
            # Collect domain events before commit
            await self._collect_domain_events()

    async def commit(self) -> None:
        """Commit the transaction and publish domain events."""
        await self.session.commit()
        # Publish events after successful commit
        await self._publish_domain_events()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self.session.rollback()
        self._domain_events.clear()

    async def _collect_domain_events(self) -> None:
        """Collect domain events from all aggregates."""
        # In a real implementation, you'd track all aggregates
        # For now, we'll handle this in the repository layer
        pass

    async def _publish_domain_events(self) -> None:
        """Publish collected domain events."""
        for event in self._domain_events:
            await self.event_bus.publish(event)
        self._domain_events.clear()
