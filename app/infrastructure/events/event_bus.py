"""
Event bus implementation.
Handles domain event publishing and subscription.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable

from app.domain.shared.events import DomainEvent


class IEventBus(ABC):
    """Event bus interface."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event."""
        pass

    @abstractmethod
    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable
    ) -> None:
        """Subscribe to an event type."""
        pass


class InMemoryEventBus(IEventBus):
    """
    In-memory event bus implementation.
    For production, use a message broker like RabbitMQ or Kafka.
    """

    def __init__(self) -> None:
        """Initialize event bus."""
        self._handlers: dict[type[DomainEvent], list[Callable]] = defaultdict(
            list
        )

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: Domain event to publish
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            try:
                if hasattr(handler, "__call__"):
                    result = handler(event)
                    # Handle async handlers
                    if hasattr(result, "__await__"):
                        await result
            except Exception as e:
                # Log error but don't stop other handlers
                import logging

                logging.error(
                    f"Error handling event {event_type.__name__}: {e}"
                )

    def subscribe(
        self, event_type: type[DomainEvent], handler: Callable
    ) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Handler function (can be async)
        """
        self._handlers[event_type].append(handler)
