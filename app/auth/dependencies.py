"""
Authentication dependencies for dependency injection.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.service import AuthService
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.service import UserService

security = HTTPBearer()


def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    """
    Get authentication service instance.

    Args:
        user_service: User service

    Returns:
        AuthService instance
    """
    return AuthService(user_service)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Get current authenticated user from token.

    Args:
        credentials: HTTP bearer credentials
        auth_service: Authentication service

    Returns:
        Current user

    Raises:
        UnauthorizedException: If token is invalid
    """
    return await auth_service.get_current_user(credentials.credentials)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        Current active user

    Raises:
        UnauthorizedException: If user is inactive
    """
    from app.core.exceptions import UnauthorizedException

    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current active user

    Returns:
        Current superuser

    Raises:
        ForbiddenException: If user is not superuser
    """
    from app.core.exceptions import ForbiddenException

    if not current_user.is_superuser:
        raise ForbiddenException("Not enough permissions")
    return current_user
