"""
User HTTP routers.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.events.publisher import get_event_publisher
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    ChangePasswordRequest,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()


async def get_user_service(
    db: AsyncSession = Depends(get_db),
    event_publisher=Depends(get_event_publisher),
) -> UserService:
    """Dependency to get user service."""
    user_repo = UserRepository(db)
    return UserService(user_repo, event_publisher)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """
    List all users with pagination.

    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 50, max 100)
    """
    return await user_service.list_users(page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get user by ID."""
    return await user_service.get_user(user_id)


@router.post(
    "", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user.

    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    - **phone**: Optional phone number
    - **bio**: Optional biography
    """
    return await user_service.create_user(user_data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update a user.

    All fields are optional. Only provided fields will be updated.
    """
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> None:
    """Delete a user."""
    await user_service.delete_user(user_id)


@router.put("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: UUID,
    password_data: ChangePasswordRequest,
    user_service: UserService = Depends(get_user_service),
) -> None:
    """
    Change user password.

    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    await user_service.change_password(
        user_id,
        password_data.old_password,
        password_data.new_password,
    )
