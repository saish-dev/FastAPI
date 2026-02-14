"""
Commands for user use cases.
Commands represent write operations (CQS pattern).
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserCommand:
    """Command to create a new user."""

    email: str
    password: str
    full_name: str | None = None
    is_superuser: bool = False


@dataclass(frozen=True)
class UpdateUserCommand:
    """Command to update a user."""

    user_id: UUID
    email: str | None = None
    password: str | None = None
    full_name: str | None = None


@dataclass(frozen=True)
class ActivateUserCommand:
    """Command to activate a user."""

    user_id: UUID


@dataclass(frozen=True)
class DeactivateUserCommand:
    """Command to deactivate a user."""

    user_id: UUID


@dataclass(frozen=True)
class DeleteUserCommand:
    """Command to delete a user."""

    user_id: UUID
