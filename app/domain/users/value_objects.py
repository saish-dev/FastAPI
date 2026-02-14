"""
Email value object with validation.
Pure domain logic - no framework dependencies.
"""

import re
from dataclasses import dataclass

from app.domain.shared.value_object import ValueObject
from app.domain.users.exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email(ValueObject):
    """Email value object with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate email on creation."""
        self._validate()

    def _validate(self) -> None:
        """Validate email format."""
        if not self.value:
            raise InvalidEmailError("Email cannot be empty")

        if len(self.value) > 255:
            raise InvalidEmailError("Email is too long")

        # Basic email regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise InvalidEmailError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        """String representation."""
        return self.value

    @property
    def domain(self) -> str:
        """Get email domain."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Get local part of email."""
        return self.value.split("@")[0]
