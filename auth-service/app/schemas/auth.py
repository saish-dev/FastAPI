"""
Pydantic schemas for authentication.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    is_superuser: bool
    oauth_provider: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Auth schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class ValidateTokenRequest(BaseModel):
    """Validate token request schema."""

    token: str


class ValidateTokenResponse(BaseModel):
    """Validate token response schema."""

    valid: bool
    user_id: UUID | None = None
    email: str | None = None


# API Key schemas
class CreateApiKeyRequest(BaseModel):
    """Create API key request schema."""

    service_name: str = Field(..., min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list)
    expires_in_days: int = Field(default=365, gt=0, le=3650)


class CreateApiKeyResponse(BaseModel):
    """Create API key response schema."""

    api_key: str
    key_id: UUID
    service_name: str
    created_at: datetime
    expires_at: datetime | None


class ValidateApiKeyRequest(BaseModel):
    """Validate API key request schema."""

    api_key: str


class ValidateApiKeyResponse(BaseModel):
    """Validate API key response schema."""

    valid: bool
    service_name: str | None = None
    permissions: list[str] = Field(default_factory=list)
