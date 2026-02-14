"""
Dependency injection setup.
Provides dependencies for FastAPI routes.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.users.unit_of_work import IUnitOfWork
from app.application.users.use_cases import IPasswordHasher, UserUseCases
from app.infrastructure.auth.password_hasher import BcryptPasswordHasher
from app.infrastructure.db.session import get_db
from app.infrastructure.events.event_bus import IEventBus, InMemoryEventBus
from app.infrastructure.repositories.unit_of_work import UnitOfWork

# Singleton instances
_event_bus = InMemoryEventBus()
_password_hasher = BcryptPasswordHasher()


def get_event_bus() -> IEventBus:
    """Get event bus instance."""
    return _event_bus


def get_password_hasher() -> IPasswordHasher:
    """Get password hasher instance."""
    return _password_hasher


async def get_uow(
    session: AsyncSession = Depends(get_db),
    event_bus: IEventBus = Depends(get_event_bus),
) -> AsyncGenerator[IUnitOfWork, None]:
    """
    Get Unit of Work instance.

    Args:
        session: Database session
        event_bus: Event bus

    Yields:
        Unit of Work instance
    """
    uow = UnitOfWork(session, event_bus)
    try:
        yield uow
    finally:
        pass  # Session cleanup handled by get_db


async def get_user_use_cases(
    uow: IUnitOfWork = Depends(get_uow),
    password_hasher: IPasswordHasher = Depends(get_password_hasher),
) -> UserUseCases:
    """
    Get user use cases instance.

    Args:
        uow: Unit of Work
        password_hasher: Password hasher

    Returns:
        User use cases
    """
    return UserUseCases(uow, password_hasher)


# Override dependency for UserUseCases
UserUseCases = Depends(get_user_use_cases)
