"""
User service layer for business logic.
"""

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import verify_password
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    """Service layer for user business logic."""

    def __init__(self, repository: UserRepository) -> None:
        """
        Initialize service with repository.

        Args:
            repository: User repository instance
        """
        self.repository = repository

    async def get_user(self, user_id: int) -> User:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance

        Raises:
            NotFoundException: If user not found
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance

        Raises:
            NotFoundException: If user not found
        """
        user = await self.repository.get_by_email(email)
        if not user:
            raise NotFoundException(f"User with email {email} not found")
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get multiple users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        return await self.repository.get_multi(skip=skip, limit=limit)

    async def create_user(self, user_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_in: User creation schema

        Returns:
            Created user

        Raises:
            ConflictException: If user with email already exists
        """
        existing_user = await self.repository.get_by_email(user_in.email)
        if existing_user:
            raise ConflictException(
                f"User with email {user_in.email} already exists"
            )

        return await self.repository.create(user_in)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """
        Update a user.

        Args:
            user_id: User ID
            user_in: User update schema

        Returns:
            Updated user

        Raises:
            NotFoundException: If user not found
            ConflictException: If email already taken
        """
        user = await self.get_user(user_id)

        # Check if email is being changed and already exists
        if user_in.email and user_in.email != user.email:
            existing_user = await self.repository.get_by_email(user_in.email)
            if existing_user:
                raise ConflictException(
                    f"User with email {user_in.email} already exists"
                )

        return await self.repository.update(user, user_in)

    async def delete_user(self, user_id: int) -> None:
        """
        Delete a user.

        Args:
            user_id: User ID

        Raises:
            NotFoundException: If user not found
        """
        user = await self.get_user(user_id)
        await self.repository.delete(user)

    async def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate a user.

        Args:
            email: User email
            password: User password

        Returns:
            Authenticated user

        Raises:
            UnauthorizedException: If credentials are invalid
        """
        user = await self.repository.get_by_email(email)
        if not user:
            raise UnauthorizedException("Incorrect email or password")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        return user
