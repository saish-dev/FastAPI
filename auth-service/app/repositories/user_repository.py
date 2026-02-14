"""
User repository for data access.
"""

import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import ApiKey, RefreshToken, User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_oauth(self, provider: str, subject: str) -> User | None:
        """Get user by OAuth provider and subject."""
        result = await self.db.execute(
            select(User).where(
                User.oauth_provider == provider,
                User.oauth_subject == subject,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


class ApiKeyRepository:
    """Repository for API key database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def get_by_id(self, key_id: UUID) -> ApiKey | None:
        """Get API key by ID."""
        result = await self.db.execute(
            select(ApiKey).where(ApiKey.id == key_id)
        )
        return result.scalar_one_or_none()

    async def get_by_service(self, service_name: str) -> list[ApiKey]:
        """Get all API keys for a service."""
        result = await self.db.execute(
            select(ApiKey).where(
                ApiKey.service_name == service_name,
                ApiKey.is_active == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        service_name: str,
        hashed_key: str,
        permissions: list[str],
        expires_at: datetime | None,
    ) -> ApiKey:
        """Create a new API key."""
        api_key = ApiKey(
            service_name=service_name,
            hashed_key=hashed_key,
            permissions=json.dumps(permissions),
            expires_at=expires_at,
        )
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def update_last_used(self, key_id: UUID) -> None:
        """Update last used timestamp."""
        api_key = await self.get_by_id(key_id)
        if api_key:
            api_key.last_used_at = datetime.utcnow()
            await self.db.commit()

    async def revoke(self, key_id: UUID) -> None:
        """Revoke an API key."""
        api_key = await self.get_by_id(key_id)
        if api_key:
            api_key.is_active = False
            await self.db.commit()


class RefreshTokenRepository:
    """Repository for refresh token database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(
        self, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        """Create a new refresh token."""
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Get refresh token by hash."""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_hash: str) -> None:
        """Revoke a refresh token."""
        token = await self.get_by_hash(token_hash)
        if token:
            token.is_revoked = True
            await self.db.commit()
