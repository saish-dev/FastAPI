"""
User entity - the aggregate root.
Pure domain logic with NO framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.domain.shared.entity import Entity
from app.domain.users.events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserEmailChanged,
)
from app.domain.users.exceptions import InactiveUserError, InvalidPasswordError
from app.domain.users.value_objects import Email


@dataclass
class User(Entity):
    """
    User aggregate root.
    Encapsulates all business rules for user management.
    """

    email: Email
    hashed_password: str
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @staticmethod
    def create(
        email: Email,
        hashed_password: str,
        full_name: str | None = None,
        is_superuser: bool = False,
    ) -> "User":
        """
        Factory method to create a new user.
        Raises domain event.
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
        )

        # Raise domain event
        user.add_domain_event(
            UserCreated(
                user_id=user.id,
                email=str(user.email),
                full_name=user.full_name,
                aggregate_id=str(user.id),
            )
        )

        return user

    def change_email(self, new_email: Email) -> None:
        """Change user email and raise domain event."""
        if not self.is_active:
            raise InactiveUserError("Cannot change email for inactive user")

        old_email = str(self.email)
        self.email = new_email
        self.updated_at = datetime.now(timezone.utc)

        self.add_domain_event(
            UserEmailChanged(
                user_id=self.id,
                old_email=old_email,
                new_email=str(new_email),
                aggregate_id=str(self.id),
            )
        )

    def change_password(self, new_hashed_password: str) -> None:
        """Change user password."""
        if not self.is_active:
            raise InactiveUserError("Cannot change password for inactive user")

        if not new_hashed_password:
            raise InvalidPasswordError("Password hash cannot be empty")

        self.hashed_password = new_hashed_password
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate user account."""
        if self.is_active:
            return  # Already active

        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

        self.add_domain_event(
            UserActivated(
                user_id=self.id,
                aggregate_id=str(self.id),
            )
        )

    def deactivate(self) -> None:
        """Deactivate user account."""
        if not self.is_active:
            return  # Already inactive

        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

        self.add_domain_event(
            UserDeactivated(
                user_id=self.id,
                aggregate_id=str(self.id),
            )
        )

    def update_profile(self, full_name: str | None = None) -> None:
        """Update user profile information."""
        if not self.is_active:
            raise InactiveUserError("Cannot update profile for inactive user")

        if full_name is not None:
            self.full_name = full_name

        self.updated_at = datetime.now(timezone.utc)

    def verify_active(self) -> None:
        """Verify that user is active."""
        if not self.is_active:
            raise InactiveUserError(f"User {self.id} is not active")
