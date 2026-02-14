"""
Main FastAPI application for user-service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
)
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.db.session import close_db
from app.events.publisher import event_publisher


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await event_publisher.connect()

    yield

    # Shutdown
    await event_publisher.disconnect()
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="User profile management microservice",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
from app.routers import users_router

app.include_router(users_router, prefix="/users", tags=["Users"])


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Metrics endpoint (placeholder)
@app.get("/metrics", tags=["metrics"])
async def metrics() -> dict:
    """Prometheus metrics endpoint."""
    return {"message": "Metrics endpoint - integrate Prometheus client"}
