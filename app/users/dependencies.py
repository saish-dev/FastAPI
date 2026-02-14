"""
User dependencies for dependency injection.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.users.repository import UserRepository
from app.users.service import UserService


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """
    Get user repository instance.

    Args:
        db: Database session

    Returns:
        UserRepository instance
    """
    return UserRepository(db)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """
    Get user service instance.

    Args:
        repository: User repository

    Returns:
        UserService instance
    """
    return UserService(repository)
