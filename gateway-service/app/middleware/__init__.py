"""Middleware package."""

from app.middleware.auth import AuthenticationMiddleware

__all__ = ["AuthenticationMiddleware"]
