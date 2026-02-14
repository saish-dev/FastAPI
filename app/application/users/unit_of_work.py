"""
Unit of Work pattern interface.
Coordinates work across multiple repositories and ensures consistency.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.users.repository import IUserRepository


class IUnitOfWork(ABC):
    """
    Unit of Work interface.
    Manages transactions and coordinates repository operations.
    """

    users: IUserRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        """Enter async context."""
        pass

    @abstractmethod
    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:
        """Exit async context."""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        pass
