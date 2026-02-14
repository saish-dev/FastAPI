"""
Domain exceptions for users.
"""


class UserDomainError(Exception):
    """Base exception for user domain errors."""

    pass


class InvalidEmailError(UserDomainError):
    """Raised when email is invalid."""

    pass


class InvalidPasswordError(UserDomainError):
    """Raised when password doesn't meet requirements."""

    pass


class UserAlreadyExistsError(UserDomainError):
    """Raised when trying to create a user that already exists."""

    pass


class UserNotFoundError(UserDomainError):
    """Raised when user is not found."""

    pass


class InactiveUserError(UserDomainError):
    """Raised when trying to use an inactive user."""

    pass
