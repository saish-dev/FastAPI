"""
Authentication HTTP routers.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.events.publisher import get_event_publisher
from app.repositories.user_repository import (
    ApiKeyRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.schemas.auth import (
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    ValidateApiKeyRequest,
    ValidateApiKeyResponse,
    ValidateTokenRequest,
    ValidateTokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
    event_publisher=Depends(get_event_publisher),
) -> AuthService:
    """Dependency to get auth service."""
    user_repo = UserRepository(db)
    api_key_repo = ApiKeyRepository(db)
    refresh_token_repo = RefreshTokenRepository(db)
    return AuthService(
        user_repo, api_key_repo, refresh_token_repo, event_publisher
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    """
    return await auth_service.register(user_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Login with email and password.

    Returns JWT access token and refresh token.
    """
    ip_address = request.client.host if request.client else None
    return await auth_service.login(
        login_data.email, login_data.password, ip_address
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Returns new access token and refresh token.
    """
    return await auth_service.refresh_access_token(refresh_data.refresh_token)


@router.post("/validate-token", response_model=ValidateTokenResponse)
async def validate_token(
    request: ValidateTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ValidateTokenResponse:
    """
    Validate JWT access token.

    Returns validation result with user information.
    """
    return await auth_service.validate_token(request.token)


@router.post("/api-keys", response_model=CreateApiKeyResponse, status_code=201)
async def create_api_key(
    request: CreateApiKeyRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> CreateApiKeyResponse:
    """
    Create a new API key for service authentication.

    - **service_name**: Name of the service
    - **permissions**: List of permissions
    - **expires_in_days**: Expiration in days (default 365)

    **Note**: The API key is only shown once. Store it securely.
    """
    return await auth_service.create_api_key(request)


@router.post("/validate-api-key", response_model=ValidateApiKeyResponse)
async def validate_api_key(
    request: ValidateApiKeyRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ValidateApiKeyResponse:
    """
    Validate API key.

    Returns validation result with service information and permissions.
    """
    return await auth_service.validate_api_key(request.api_key)
