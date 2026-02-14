"""
Authentication middleware for gateway.
"""

from typing import Callable

import structlog
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.grpc.auth_client import auth_client

logger = structlog.get_logger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens and API keys."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with authentication."""
        # Skip auth for health and docs endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            result = await auth_client.validate_token(token)

            if result["valid"]:
                # Add user info to request state
                request.state.user_id = result["user_id"]
                request.state.email = result["email"]
                request.state.auth_type = "jwt"
                return await call_next(request)

        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            result = await auth_client.validate_api_key(api_key)

            if result["valid"]:
                # Add service info to request state
                request.state.service_name = result["service_name"]
                request.state.permissions = result["permissions"]
                request.state.auth_type = "api_key"
                return await call_next(request)

        # No valid authentication
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication required"},
        )
