"""
Outbox pattern implementation for reliable event publishing.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class OutboxEventModel(Base):
    """
    Outbox table for storing events before publishing.
    Ensures events are not lost even if publishing fails.
    """

    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    aggregate_id: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    event_data: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON serialized
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<OutboxEvent(id={self.id}, type={self.event_type})>"
