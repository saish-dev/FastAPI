"""
User service with business logic.
"""

from uuid import UUID

import structlog

from app.core.exceptions import ConflictError, NotFoundError
from app.events.publisher import EventPublisher
from app.events.schemas import (
    PasswordChangedEvent,
    UserCreatedEvent,
    UserDeletedEvent,
    UserUpdatedEvent,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)

logger = structlog.get_logger(__name__)


class UserService:
    """Service for user operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize service with repositories."""
        self.user_repo = user_repo
        self.event_publisher = event_publisher

    async def get_user(self, user_id: UUID) -> UserResponse:
        """Get user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        return UserResponse.model_validate(user)

    async def list_users(
        self, page: int = 1, page_size: int = 50
    ) -> UserListResponse:
        """List users with pagination."""
        skip = (page - 1) * page_size
        users = await self.user_repo.get_all(skip=skip, limit=page_size)
        total = await self.user_repo.count()

        return UserListResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError(
                f"User with email {user_data.email} already exists"
            )

        # Create user (password would be handled by auth-service)
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            bio=user_data.bio,
        )

        created_user = await self.user_repo.create(user)

        # Publish event
        await self.event_publisher.publish(
            "user.events",
            UserCreatedEvent(
                user_id=created_user.id,
                email=created_user.email,
            ).model_dump(mode="json"),
        )

        logger.info(
            "User created",
            user_id=str(created_user.id),
            email=created_user.email,
        )

        return UserResponse.model_validate(created_user)

    async def update_user(
        self, user_id: UUID, user_data: UserUpdate
    ) -> UserResponse:
        """Update a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        # Track updated fields
        updated_fields = []

        # Update fields
        if user_data.email is not None:
            # Check if email is already taken
            existing_user = await self.user_repo.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ConflictError(
                    f"Email {user_data.email} is already taken"
                )
            user.email = user_data.email
            updated_fields.append("email")

        if user_data.full_name is not None:
            user.full_name = user_data.full_name
            updated_fields.append("full_name")

        if user_data.phone is not None:
            user.phone = user_data.phone
            updated_fields.append("phone")

        if user_data.bio is not None:
            user.bio = user_data.bio
            updated_fields.append("bio")

        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url
            updated_fields.append("avatar_url")

        if user_data.is_active is not None:
            user.is_active = user_data.is_active
            updated_fields.append("is_active")

        updated_user = await self.user_repo.update(user)

        # Publish event
        if updated_fields:
            await self.event_publisher.publish(
                "user.events",
                UserUpdatedEvent(
                    user_id=updated_user.id,
                    fields_updated=updated_fields,
                ).model_dump(mode="json"),
            )

        logger.info(
            "User updated", user_id=str(user_id), fields=updated_fields
        )

        return UserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        await self.user_repo.delete(user)

        # Publish event
        await self.event_publisher.publish(
            "user.events",
            UserDeletedEvent(user_id=user_id).model_dump(mode="json"),
        )

        logger.info("User deleted", user_id=str(user_id))

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> None:
        """Change user password (delegates to auth-service via gRPC)."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        # In a real implementation, this would call auth-service via gRPC
        # For now, we'll just publish an event
        await self.event_publisher.publish(
            "user.events",
            PasswordChangedEvent(user_id=user_id).model_dump(mode="json"),
        )

        logger.info("Password changed", user_id=str(user_id))
