"""
User use cases (application services).
Orchestrates domain logic and coordinates with repositories.
"""

from uuid import UUID

from app.application.users.commands import (
    ActivateUserCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.application.users.dto import CreateUserDTO, UpdateUserDTO, UserDTO
from app.application.users.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    ListUsersQuery,
)
from app.application.users.unit_of_work import IUnitOfWork
from app.domain.users.entities import User
from app.domain.users.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.users.value_objects import Email


class UserUseCases:
    """
    User use cases.
    Coordinates application logic without containing business rules.
    """

    def __init__(self, uow: IUnitOfWork, password_hasher: "IPasswordHasher"):
        """
        Initialize use cases.

        Args:
            uow: Unit of Work for transaction management
            password_hasher: Password hashing service
        """
        self.uow = uow
        self.password_hasher = password_hasher

    async def create_user(self, command: CreateUserCommand) -> UserDTO:
        """
        Create a new user.

        Args:
            command: Create user command

        Returns:
            Created user DTO

        Raises:
            UserAlreadyExistsError: If user with email already exists
        """
        async with self.uow:
            email = Email(command.email)

            # Check if user already exists
            if await self.uow.users.exists_by_email(email):
                raise UserAlreadyExistsError(
                    f"User with email {command.email} already exists"
                )

            # Hash password
            hashed_password = self.password_hasher.hash(command.password)

            # Create user entity
            user = User.create(
                email=email,
                hashed_password=hashed_password,
                full_name=command.full_name,
                is_superuser=command.is_superuser,
            )

            # Save user
            user = await self.uow.users.save(user)
            await self.uow.commit()

            return self._to_dto(user)

    async def get_user_by_id(self, query: GetUserByIdQuery) -> UserDTO:
        """
        Get user by ID.

        Args:
            query: Get user by ID query

        Returns:
            User DTO

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(query.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {query.user_id} not found"
                )

            return self._to_dto(user)

    async def get_user_by_email(self, query: GetUserByEmailQuery) -> UserDTO:
        """
        Get user by email.

        Args:
            query: Get user by email query

        Returns:
            User DTO

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            email = Email(query.email)
            user = await self.uow.users.get_by_email(email)
            if not user:
                raise UserNotFoundError(
                    f"User with email {query.email} not found"
                )

            return self._to_dto(user)

    async def list_users(self, query: ListUsersQuery) -> list[UserDTO]:
        """
        List users with pagination.

        Args:
            query: List users query

        Returns:
            List of user DTOs
        """
        async with self.uow:
            users = await self.uow.users.list(
                skip=query.skip, limit=query.limit
            )
            return [self._to_dto(user) for user in users]

    async def update_user(self, command: UpdateUserCommand) -> UserDTO:
        """
        Update user.

        Args:
            command: Update user command

        Returns:
            Updated user DTO

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(command.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {command.user_id} not found"
                )

            # Update email if provided
            if command.email:
                new_email = Email(command.email)
                user.change_email(new_email)

            # Update password if provided
            if command.password:
                hashed_password = self.password_hasher.hash(command.password)
                user.change_password(hashed_password)

            # Update profile if provided
            if command.full_name is not None:
                user.update_profile(full_name=command.full_name)

            user = await self.uow.users.save(user)
            await self.uow.commit()

            return self._to_dto(user)

    async def activate_user(self, command: ActivateUserCommand) -> UserDTO:
        """
        Activate user.

        Args:
            command: Activate user command

        Returns:
            Activated user DTO

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(command.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {command.user_id} not found"
                )

            user.activate()
            user = await self.uow.users.save(user)
            await self.uow.commit()

            return self._to_dto(user)

    async def deactivate_user(self, command: DeactivateUserCommand) -> UserDTO:
        """
        Deactivate user.

        Args:
            command: Deactivate user command

        Returns:
            Deactivated user DTO

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(command.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {command.user_id} not found"
                )

            user.deactivate()
            user = await self.uow.users.save(user)
            await self.uow.commit()

            return self._to_dto(user)

    async def delete_user(self, command: DeleteUserCommand) -> None:
        """
        Delete user.

        Args:
            command: Delete user command

        Raises:
            UserNotFoundError: If user not found
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(command.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with ID {command.user_id} not found"
                )

            await self.uow.users.delete(user)
            await self.uow.commit()

    def _to_dto(self, user: User) -> UserDTO:
        """Convert domain entity to DTO."""
        return UserDTO(
            id=user.id,
            email=str(user.email),
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


# Password hasher interface (to be implemented in infrastructure)
class IPasswordHasher:
    """Interface for password hashing."""

    def hash(self, password: str) -> str:
        """Hash a password."""
        raise NotImplementedError

    def verify(self, password: str, hashed: str) -> bool:
        """Verify a password against a hash."""
        raise NotImplementedError
