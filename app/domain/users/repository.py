"""
Abstract repository interface for User aggregate.
This is defined in the domain layer - implementation is in infrastructure.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.users.entities import User
from app.domain.users.value_objects import Email


class IUserRepository(ABC):
    """
    Abstract repository interface for User aggregate.
    Defines the contract that infrastructure must implement.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user (create or update)."""
        pass

    @abstractmethod
    async def delete(self, user: User) -> None:
        """Delete user."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users with pagination."""
        pass
