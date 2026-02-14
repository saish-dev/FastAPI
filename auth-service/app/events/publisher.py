"""
NATS event publisher for async communication.
"""

import json
from typing import Any

import structlog
from nats.aio.client import Client as NATS

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EventPublisher:
    """NATS event publisher."""

    def __init__(self) -> None:
        """Initialize event publisher."""
        self.nc: NATS | None = None
        self.connected = False

    async def connect(self) -> None:
        """Connect to NATS server."""
        if not settings.NATS_ENABLED:
            logger.info("NATS is disabled, skipping connection")
            return

        try:
            self.nc = NATS()
            await self.nc.connect(settings.NATS_URL)
            self.connected = True
            logger.info("Connected to NATS", url=settings.NATS_URL)
        except Exception as e:
            logger.error("Failed to connect to NATS", error=str(e))
            self.connected = False

    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        if self.nc and self.connected:
            await self.nc.close()
            self.connected = False
            logger.info("Disconnected from NATS")

    async def publish(self, subject: str, event: dict[str, Any]) -> None:
        """
        Publish an event to NATS.

        Args:
            subject: NATS subject/topic
            event: Event data dictionary
        """
        if not self.connected or not self.nc:
            logger.warning(
                "NATS not connected, event not published", subject=subject
            )
            return

        try:
            message = json.dumps(event).encode()
            await self.nc.publish(subject, message)
            logger.info(
                "Event published",
                subject=subject,
                event_type=event.get("event_type"),
            )
        except Exception as e:
            logger.error(
                "Failed to publish event", subject=subject, error=str(e)
            )


# Global event publisher instance
event_publisher = EventPublisher()


async def get_event_publisher() -> EventPublisher:
    """Get event publisher instance."""
    return event_publisher
