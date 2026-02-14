"""
User Pydantic schemas for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


# Properties to receive via API on update
class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(None, min_length=8, max_length=100)
    is_active: bool | None = None
    is_superuser: bool | None = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    """Base schema for user in database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Properties to return to client
class User(UserInDBBase):
    """Schema for user response."""

    pass


# Properties stored in DB
class UserInDB(UserInDBBase):
    """Schema for user in database with hashed password."""

    hashed_password: str
