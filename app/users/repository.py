"""
User repository for database operations.
Implements the Repository pattern for data access.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


class UserRepository:
    """Repository for User database operations."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Get multiple users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, user_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_in: User creation schema

        Returns:
            Created user
        """
        db_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user: User, user_in: UserUpdate) -> User:
        """
        Update a user.

        Args:
            user: Existing user
            user_in: User update schema

        Returns:
            Updated user
        """
        update_data = user_in.model_dump(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """
        Delete a user.

        Args:
            user: User to delete
        """
        await self.db.delete(user)
        await self.db.commit()

    async def is_active(self, user: User) -> bool:
        """
        Check if user is active.

        Args:
            user: User to check

        Returns:
            True if user is active
        """
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """
        Check if user is superuser.

        Args:
            user: User to check

        Returns:
            True if user is superuser
        """
        return user.is_superuser
