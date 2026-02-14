"""
Authentication router - handles HTTP requests for authentication.
"""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_auth_service
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Login endpoint.

    Args:
        request: Login credentials
        auth_service: Authentication service

    Returns:
        Access and refresh tokens
    """
    return await auth_service.login(
        email=request.email, password=request.password
    )


@router.post(
    "/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Refresh token endpoint.

    Args:
        request: Refresh token
        auth_service: Authentication service

    Returns:
        New access and refresh tokens
    """
    return await auth_service.refresh_token(
        refresh_token=request.refresh_token
    )
