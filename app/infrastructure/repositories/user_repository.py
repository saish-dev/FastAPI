"""
User repository implementation.
Implements the domain repository interface using SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.entities import User
from app.domain.users.repository import IUserRepository
from app.domain.users.value_objects import Email
from app.infrastructure.db.models import UserModel


class UserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == str(email))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == str(email))
        )
        return result.scalar_one_or_none() is not None

    async def save(self, user: User) -> User:
        """Save user (create or update)."""
        # Check if user exists
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        existing_model = result.scalar_one_or_none()

        if existing_model:
            # Update existing
            self._update_model_from_entity(existing_model, user)
        else:
            # Create new
            model = self._to_model(user)
            self.session.add(model)

        await self.session.flush()
        return user

    async def delete(self, user: User) -> None:
        """Delete user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)
            await self.session.flush()

    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List users with pagination."""
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        user = User(
            id=model.id,
            email=Email(model.email),
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        # Clear any events that might have been added during reconstruction
        user.clear_domain_events()
        return user

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _update_model_from_entity(
        self, model: UserModel, entity: User
    ) -> None:
        """Update SQLAlchemy model from domain entity."""
        model.email = str(entity.email)
        model.hashed_password = entity.hashed_password
        model.full_name = entity.full_name
        model.is_active = entity.is_active
        model.is_superuser = entity.is_superuser
        model.updated_at = entity.updated_at
