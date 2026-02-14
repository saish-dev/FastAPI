"""
Custom exceptions and exception handlers.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        """Initialize exception."""
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize exception."""
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(AppException):
    """Authorization error."""

    def __init__(self, message: str = "Not authorized"):
        """Initialize exception."""
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class NotFoundError(AppException):
    """Not found error."""

    def __init__(self, message: str = "Resource not found"):
        """Initialize exception."""
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Conflict error."""

    def __init__(self, message: str = "Resource already exists"):
        """Initialize exception."""
        super().__init__(message, status.HTTP_409_CONFLICT)


# Exception handlers


async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    import logging

    logging.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
