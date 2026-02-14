"""
Event schemas for publishing.
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


class AuthEvent(BaseEvent):
    """Authentication event."""

    event_type: str = "AuthEvent"
    user_id: UUID
    action: str  # login, logout, token_refresh
    ip_address: str | None = None
    user_agent: str | None = None


class AuditLogEvent(BaseEvent):
    """Audit log event."""

    event_type: str = "AuditLogEvent"
    user_id: UUID | None = None
    action: str
    resource: str
    details: dict | None = None
