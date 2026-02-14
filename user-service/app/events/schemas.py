"""
Event schemas for user service.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from uuid_extensions import uuid7


class BaseEvent(BaseModel):
    """Base event schema."""

    event_id: UUID = uuid7()
    event_type: str
    timestamp: datetime = datetime.utcnow()


class UserCreatedEvent(BaseEvent):
    """User created event."""

    event_type: str = "UserCreated"
    user_id: UUID
    email: str


class PasswordChangedEvent(BaseEvent):
    """Password changed event."""

    event_type: str = "PasswordChanged"
    user_id: UUID


class UserUpdatedEvent(BaseEvent):
    """User updated event."""

    event_type: str = "UserUpdated"
    user_id: UUID
    fields_updated: list[str]


class UserDeletedEvent(BaseEvent):
    """User deleted event."""

    event_type: str = "UserDeleted"
    user_id: UUID
