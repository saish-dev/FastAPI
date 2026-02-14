"""
User domain events.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.shared.events import DomainEvent


@dataclass
class UserCreated(DomainEvent):
    """Event raised when a user is created."""

    user_id: UUID
    email: str
    full_name: str | None

    def _get_payload(self) -> dict[str, Any]:
        """Get event payload."""
        return {
            "user_id": str(self.user_id),
            "email": self.email,
            "full_name": self.full_name,
        }


@dataclass
class UserActivated(DomainEvent):
    """Event raised when a user is activated."""

    user_id: UUID

    def _get_payload(self) -> dict[str, Any]:
        """Get event payload."""
        return {"user_id": str(self.user_id)}


@dataclass
class UserDeactivated(DomainEvent):
    """Event raised when a user is deactivated."""

    user_id: UUID

    def _get_payload(self) -> dict[str, Any]:
        """Get event payload."""
        return {"user_id": str(self.user_id)}


@dataclass
class UserEmailChanged(DomainEvent):
    """Event raised when user email is changed."""

    user_id: UUID
    old_email: str
    new_email: str

    def _get_payload(self) -> dict[str, Any]:
        """Get event payload."""
        return {
            "user_id": str(self.user_id),
            "old_email": self.old_email,
            "new_email": self.new_email,
        }
