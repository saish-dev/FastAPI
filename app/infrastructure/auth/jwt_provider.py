"""
JWT provider for token generation and validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings


class JWTProvider:
    """JWT token provider."""

    def create_access_token(self, subject: str) -> str:
        """
        Create JWT access token.

        Args:
            subject: Token subject (usually user ID)

        Returns:
            Encoded JWT token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        to_encode: dict[str, Any] = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
        }

        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

    def create_refresh_token(self, subject: str) -> str:
        """
        Create JWT refresh token.

        Args:
            subject: Token subject (usually user ID)

        Returns:
            Encoded JWT refresh token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        to_encode: dict[str, Any] = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
        }

        return jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decode and verify JWT token.

        Args:
            token: JWT token

        Returns:
            Decoded payload

        Raises:
            JWTError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise JWTError(f"Could not validate credentials: {str(e)}") from e
