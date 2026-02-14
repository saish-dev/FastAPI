"""
Authentication API router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth import schemas
from app.auth.dependencies import get_auth_service, get_current_active_user
from app.auth.service import AuthService
from app.users.models import User
from app.users.schemas import User as UserSchema

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=schemas.Token)
async def login(
    login_data: schemas.LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> schemas.Token:
    """
    Login endpoint to get access and refresh tokens.

    Args:
        login_data: Login credentials
        auth_service: Authentication service

    Returns:
        Access and refresh tokens
    """
    return await auth_service.login(login_data.email, login_data.password)


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_data: schemas.RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> schemas.Token:
    """
    Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token
        auth_service: Authentication service

    Returns:
        New access and refresh tokens
    """
    return await auth_service.refresh_access_token(refresh_data.refresh_token)


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserSchema:
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user details
    """
    return UserSchema.model_validate(current_user)
