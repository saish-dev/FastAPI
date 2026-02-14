"""
User service - contains business logic for user operations.
"""

from uuid import UUID

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    """Service for user operations."""

    def __init__(self, user_repository: UserRepository):
        """Initialize service with repository."""
        self.user_repository = user_repository

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user

        Raises:
            ConflictError: If user with email already exists
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(
            user_data.email
        )
        if existing_user:
            raise ConflictError(
                f"User with email {user_data.email} already exists"
            )

        # Create user model
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )

        # Save to database
        created_user = await self.user_repository.create(user)

        return UserResponse.model_validate(created_user)

    async def get_user(self, user_id: UUID) -> UserResponse:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User data

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        return UserResponse.model_validate(user)

    async def get_users(
        self, skip: int = 0, limit: int = 100
    ) -> list[UserResponse]:
        """
        Get all users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of users
        """
        users = await self.user_repository.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]

    async def update_user(
        self, user_id: UUID, user_data: UserUpdate
    ) -> UserResponse:
        """
        Update user.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user

        Raises:
            NotFoundError: If user not found
            ConflictError: If email already exists
        """
        # Get existing user
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        # Check email uniqueness if changing email
        if user_data.email and user_data.email != user.email:
            existing_user = await self.user_repository.get_by_email(
                user_data.email
            )
            if existing_user:
                raise ConflictError(
                    f"User with email {user_data.email} already exists"
                )
            user.email = user_data.email

        # Update fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        # Save changes
        updated_user = await self.user_repository.update(user)

        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: UUID) -> None:
        """
        Delete user.

        Args:
            user_id: User ID

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")

        await self.user_repository.delete(user)
