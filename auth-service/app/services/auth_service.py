"""
Authentication service with business logic.
"""

import hashlib
import json
from datetime import datetime, timedelta
from uuid import UUID

import structlog

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_api_key,
    get_password_hash,
    hash_api_key,
    verify_api_key,
    verify_password,
)
from app.events.publisher import EventPublisher
from app.events.schemas import AuditLogEvent, AuthEvent
from app.models.user import User
from app.repositories.user_repository import (
    ApiKeyRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.schemas.auth import (
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    LoginResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
    ValidateApiKeyResponse,
    ValidateTokenResponse,
)

logger = structlog.get_logger(__name__)


class AuthService:
    """Service for authentication operations."""

    def __init__(
        self,
        user_repo: UserRepository,
        api_key_repo: ApiKeyRepository,
        refresh_token_repo: RefreshTokenRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize service with repositories."""
        self.user_repo = user_repo
        self.api_key_repo = api_key_repo
        self.refresh_token_repo = refresh_token_repo
        self.event_publisher = event_publisher

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictError(
                f"User with email {user_data.email} already exists"
            )

        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
        )

        created_user = await self.user_repo.create(user)

        # Publish audit event
        await self.event_publisher.publish(
            "auth.audit",
            AuditLogEvent(
                user_id=created_user.id,
                action="user_registered",
                resource="user",
                details={"email": created_user.email},
            ).model_dump(mode="json"),
        )

        return UserResponse.model_validate(created_user)

    async def login(
        self, email: str, password: str, ip_address: str | None = None
    ) -> LoginResponse:
        """Authenticate user and return tokens."""
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        # Check if active
        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=7)
        await self.refresh_token_repo.create(user.id, token_hash, expires_at)

        # Publish auth event
        await self.event_publisher.publish(
            "auth.events",
            AuthEvent(
                user_id=user.id,
                action="login",
                ip_address=ip_address,
            ).model_dump(mode="json"),
        )

        logger.info("User logged in", user_id=str(user.id), email=email)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800,  # 30 minutes
            user_id=user.id,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")

            user_id = UUID(payload.get("sub"))

            # Check if token is revoked
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            stored_token = await self.refresh_token_repo.get_by_hash(
                token_hash
            )

            if not stored_token or stored_token.is_revoked:
                raise AuthenticationError("Token has been revoked")

            # Verify user exists and is active
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("User not found or inactive")

            # Create new tokens
            new_access_token = create_access_token(user.id)
            new_refresh_token = create_refresh_token(user.id)

            # Store new refresh token
            new_token_hash = hashlib.sha256(
                new_refresh_token.encode()
            ).hexdigest()
            expires_at = datetime.utcnow() + timedelta(days=7)
            await self.refresh_token_repo.create(
                user.id, new_token_hash, expires_at
            )

            # Revoke old refresh token
            await self.refresh_token_repo.revoke(token_hash)

            # Publish event
            await self.event_publisher.publish(
                "auth.events",
                AuthEvent(
                    user_id=user.id,
                    action="token_refresh",
                ).model_dump(mode="json"),
            )

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=1800,
            )

        except Exception as e:
            raise AuthenticationError(
                f"Invalid refresh token: {str(e)}"
            ) from e

    async def validate_token(self, token: str) -> ValidateTokenResponse:
        """Validate JWT token."""
        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                return ValidateTokenResponse(valid=False)

            user_id = UUID(payload.get("sub"))
            user = await self.user_repo.get_by_id(user_id)

            if not user or not user.is_active:
                return ValidateTokenResponse(valid=False)

            return ValidateTokenResponse(
                valid=True,
                user_id=user.id,
                email=user.email,
            )

        except Exception:
            return ValidateTokenResponse(valid=False)

    async def create_api_key(
        self, request: CreateApiKeyRequest
    ) -> CreateApiKeyResponse:
        """Create a new API key for service authentication."""
        # Generate API key
        api_key = generate_api_key()
        hashed_key = hash_api_key(api_key)

        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(
            days=request.expires_in_days
        )

        # Store API key
        stored_key = await self.api_key_repo.create(
            service_name=request.service_name,
            hashed_key=hashed_key,
            permissions=request.permissions,
            expires_at=expires_at,
        )

        # Publish audit event
        await self.event_publisher.publish(
            "auth.audit",
            AuditLogEvent(
                action="api_key_created",
                resource="api_key",
                details={
                    "service_name": request.service_name,
                    "key_id": str(stored_key.id),
                },
            ).model_dump(mode="json"),
        )

        logger.info(
            "API key created",
            service_name=request.service_name,
            key_id=str(stored_key.id),
        )

        return CreateApiKeyResponse(
            api_key=api_key,  # Return plain key only once
            key_id=stored_key.id,
            service_name=stored_key.service_name,
            created_at=stored_key.created_at,
            expires_at=stored_key.expires_at,
        )

    async def validate_api_key(self, api_key: str) -> ValidateApiKeyResponse:
        """Validate API key."""
        # Get all active API keys (in production, use caching)
        # For now, we'll iterate through keys for the demo
        # In production, hash the key and look it up directly

        hashed_key = hash_api_key(api_key)

        # This is a simplified version - in production, you'd want to optimize this
        # by storing a hash of the key prefix for quick lookup
        from sqlalchemy import select

        from app.models.user import ApiKey

        result = await self.api_key_repo.db.execute(
            select(ApiKey).where(ApiKey.is_active == True)  # noqa: E712
        )
        api_keys = result.scalars().all()

        for key in api_keys:
            if verify_api_key(api_key, key.hashed_key):
                # Check expiration
                if key.expires_at and key.expires_at < datetime.utcnow():
                    return ValidateApiKeyResponse(valid=False)

                # Update last used
                await self.api_key_repo.update_last_used(key.id)

                # Parse permissions
                permissions = (
                    json.loads(key.permissions) if key.permissions else []
                )

                return ValidateApiKeyResponse(
                    valid=True,
                    service_name=key.service_name,
                    permissions=permissions,
                )

        return ValidateApiKeyResponse(valid=False)

    async def revoke_api_key(self, key_id: UUID) -> None:
        """Revoke an API key."""
        await self.api_key_repo.revoke(key_id)

        # Publish audit event
        await self.event_publisher.publish(
            "auth.audit",
            AuditLogEvent(
                action="api_key_revoked",
                resource="api_key",
                details={"key_id": str(key_id)},
            ).model_dump(mode="json"),
        )

        logger.info("API key revoked", key_id=str(key_id))
