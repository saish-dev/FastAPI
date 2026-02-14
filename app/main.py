"""
Main FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.db.session import close_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")

    # Initialize Redis
    redis_client = Redis.from_url(
        str(settings.REDIS_URL),
        encoding="utf-8",
        decode_responses=True,
    )
    app.state.redis = redis_client
    logger.info("Redis connection established")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await redis_client.close()
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )

    response = await call_next(request)

    logger.info(
        f"Response: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "path": request.url.path,
        },
    )

    return response


# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "version": settings.APP_VERSION}


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
