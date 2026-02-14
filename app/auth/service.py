"""
Authentication service for JWT token management.
"""

from datetime import timedelta

from jose import JWTError

from app.auth.schemas import Token
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.users.models import User
from app.users.service import UserService


class AuthService:
    """Service layer for authentication logic."""

    def __init__(self, user_service: UserService) -> None:
        """
        Initialize service with user service.

        Args:
            user_service: User service instance
        """
        self.user_service = user_service

    async def login(self, email: str, password: str) -> Token:
        """
        Authenticate user and generate tokens.

        Args:
            email: User email
            password: User password

        Returns:
            Access and refresh tokens

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        user = await self.user_service.authenticate(email, password)

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access and refresh tokens

        Raises:
            UnauthorizedException: If refresh token is invalid
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError as e:
            raise UnauthorizedException("Invalid refresh token") from e

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        # Verify user still exists and is active
        user = await self.user_service.get_user(int(user_id))
        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Generate new tokens
        access_token = create_access_token(subject=str(user.id))
        new_refresh_token = create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token.

        Args:
            token: Access token

        Returns:
            Current user

        Raises:
            UnauthorizedException: If token is invalid
        """
        try:
            payload = decode_token(token)
        except JWTError as e:
            raise UnauthorizedException(
                "Could not validate credentials"
            ) from e

        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        user = await self.user_service.get_user(int(user_id))
        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        return user
