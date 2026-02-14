"""
Global application dependencies.
"""

import logging
from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


async def get_redis(request: Request) -> Redis:
    """
    Get Redis client from app state.

    Args:
        request: FastAPI request

    Returns:
        Redis client instance
    """
    return request.app.state.redis


async def check_rate_limit(
    request: Request,
    redis: Annotated[Redis, Depends(get_redis)],
) -> None:
    """
    Check rate limit for the request.

    Args:
        request: FastAPI request
        redis: Redis client

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not settings.RATE_LIMIT_ENABLED:
        return

    from fastapi import HTTPException, status

    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"

    # Get current count
    count = await redis.get(key)

    if count and int(count) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )

    # Increment counter
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)  # 60 seconds TTL
    await pipe.execute()
