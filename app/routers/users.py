"""
Users router - handles HTTP requests for user operations.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Create a new user.

    Args:
        user_data: User creation data
        user_service: User service

    Returns:
        Created user
    """
    return await user_service.create_user(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user.

    Args:
        current_user: Current user from token

    Returns:
        Current user data
    """
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user),  # Require authentication
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID
        user_service: User service

    Returns:
        User data
    """
    return await user_service.get_user(user_id)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user),  # Require authentication
) -> list[UserResponse]:
    """
    Get all users with pagination.

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        user_service: User service

    Returns:
        List of users
    """
    return await user_service.get_users(skip=skip, limit=limit)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user),  # Require authentication
) -> UserResponse:
    """
    Update user.

    Args:
        user_id: User ID
        user_data: User update data
        user_service: User service

    Returns:
        Updated user
    """
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    _: User = Depends(get_current_user),  # Require authentication
) -> None:
    """
    Delete user.

    Args:
        user_id: User ID
        user_service: User service
    """
    await user_service.delete_user(user_id)
