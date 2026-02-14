"""
Main FastAPI application for gateway service.
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
from app.grpc.auth_client import auth_client
from app.grpc.user_client import user_client
from app.middleware.auth import AuthenticationMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await auth_client.connect()
    await user_client.connect()

    yield

    # Shutdown
    await auth_client.close()
    await user_client.close()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API Gateway for microservices",
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
# Note: Authentication middleware is commented out for initial testing
# Uncomment after gRPC proto files are generated
# app.add_middleware(AuthenticationMiddleware)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
from app.routers import router as api_router

app.include_router(api_router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Aggregated health check.

    In full implementation, this would check health of all backend services.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "auth": "connected" if auth_client.stub else "not_connected",
            "user": "connected" if user_client.stub else "not_connected",
        },
    }
