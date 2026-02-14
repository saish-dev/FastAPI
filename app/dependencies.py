"""
Dependency injection for FastAPI.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(user_repository)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Get user service instance."""
    return UserService(user_repository)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        authorization: Authorization header
        user_repository: User repository

    Returns:
        Current user

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    if not authorization:
        raise AuthenticationError("Missing authorization header")

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")

    token = parts[1]

    try:
        # Decode token
        payload = decode_token(token)

        # Verify token type
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")

        user_id = UUID(payload.get("sub"))

        # Get user from database
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        return user

    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}") from e
    except (ValueError, TypeError) as e:
        raise AuthenticationError(f"Invalid token payload: {str(e)}") from e
