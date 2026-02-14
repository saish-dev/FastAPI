"""
Pydantic schemas for user service.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    is_active: bool
    is_superuser: bool
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""

    old_password: str
    new_password: str = Field(..., min_length=8)


class UserListResponse(BaseModel):
    """Schema for list of users."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
