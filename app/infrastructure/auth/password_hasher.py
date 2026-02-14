"""
Password hasher implementation using bcrypt.
"""

from passlib.context import CryptContext

from app.application.users.use_cases import IPasswordHasher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(IPasswordHasher):
    """Bcrypt implementation of password hasher."""

    def hash(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        return pwd_context.verify(password, hashed)
