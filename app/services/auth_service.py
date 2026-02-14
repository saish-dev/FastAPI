"""
Authentication service - contains business logic for authentication.
"""

from jose import JWTError

from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_repository: UserRepository):
        """Initialize service with repository."""
        self.user_repository = user_repository

    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate user and return tokens.

        Args:
            email: User email
            password: User password

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Create tokens
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            TokenResponse with new tokens

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = decode_token(refresh_token)

            # Verify token type
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")

            user_id = int(payload.get("sub"))

            # Verify user exists and is active
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundError("User not found")

            if not user.is_active:
                raise AuthenticationError("User account is inactive")

            # Create new tokens
            access_token = create_access_token(subject=user.id)
            new_refresh_token = create_refresh_token(subject=user.id)

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
            )

        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}") from e
