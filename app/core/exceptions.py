"""
Custom exceptions and centralized exception handlers.
"""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class UnauthorizedException(AppException):
    """Unauthorized access exception."""

    def __init__(
        self,
        message: str = "Unauthorized",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenException(AppException):
    """Forbidden access exception."""

    def __init__(
        self, message: str = "Forbidden", details: dict[str, Any] | None = None
    ):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ConflictException(AppException):
    """Resource conflict exception."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """
    Handle custom application exceptions.

    Args:
        request: The request that caused the exception
        exc: The application exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            }
        },
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.

    Args:
        request: The request that caused the exception
        exc: The HTTP exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "path": request.url.path,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.

    Args:
        request: The request that caused the exception
        exc: The validation error

    Returns:
        JSON response with validation error details
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "details": {"errors": errors},
                "path": request.url.path,
            }
        },
    )


async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: The request that caused the exception
        exc: The exception

    Returns:
        JSON response with error details
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.exception("Unexpected error occurred", exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "path": request.url.path,
            }
        },
    )
