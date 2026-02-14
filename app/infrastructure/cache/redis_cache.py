"""
Redis cache implementation.
"""

from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings


class RedisCache:
    """Redis cache wrapper."""

    def __init__(self) -> None:
        """Initialize Redis cache."""
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = await aioredis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            return None

        return await self.redis.get(key)

    async def set(
        self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        if not self.redis:
            return

        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        if not self.redis:
            return

        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.redis:
            return False

        return await self.redis.exists(key) > 0


# Global cache instance
cache = RedisCache()
