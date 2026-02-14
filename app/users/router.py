"""
User API router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.users import schemas
from app.users.dependencies import get_user_service
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[schemas.User])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)],
    skip: int = 0,
    limit: int = 100,
) -> list[schemas.User]:
    """
    Retrieve users with pagination.

    Args:
        service: User service
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of users
    """
    users = await service.get_users(skip=skip, limit=limit)
    return [schemas.User.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> schemas.User:
    """
    Get user by ID.

    Args:
        user_id: User ID
        service: User service

    Returns:
        User details
    """
    user = await service.get_user(user_id)
    return schemas.User.model_validate(user)


@router.post(
    "/", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_in: schemas.UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> schemas.User:
    """
    Create new user.

    Args:
        user_in: User creation data
        service: User service

    Returns:
        Created user
    """
    user = await service.create_user(user_in)
    return schemas.User.model_validate(user)


@router.patch("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> schemas.User:
    """
    Update user.

    Args:
        user_id: User ID
        user_in: User update data
        service: User service

    Returns:
        Updated user
    """
    user = await service.update_user(user_id, user_in)
    return schemas.User.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """
    Delete user.

    Args:
        user_id: User ID
        service: User service
    """
    await service.delete_user(user_id)
