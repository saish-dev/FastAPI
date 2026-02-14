"""Users domain package."""

from app.domain.users.entities import User
from app.domain.users.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserEmailChanged,
)
from app.domain.users.exceptions import (
    InactiveUserError,
    InvalidEmailError,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserDomainError,
    UserNotFoundError,
)
from app.domain.users.repository import IUserRepository
from app.domain.users.value_objects import Email

__all__ = [
    "User",
    "Email",
    "IUserRepository",
    "UserDomainError",
    "InvalidEmailError",
    "InvalidPasswordError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "InactiveUserError",
    "UserCreated",
    "UserActivated",
    "UserDeactivated",
    "UserEmailChanged",
]
