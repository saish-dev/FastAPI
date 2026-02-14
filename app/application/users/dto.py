"""
Data Transfer Objects (DTOs) for application layer.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserDTO:
    """User data transfer object."""

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool


@dataclass(frozen=True)
class CreateUserDTO:
    """DTO for creating a user."""

    email: str
    password: str
    full_name: str | None = None
    is_superuser: bool = False


@dataclass(frozen=True)
class UpdateUserDTO:
    """DTO for updating a user."""

    email: str | None = None
    password: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
