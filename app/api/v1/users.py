"""
User API endpoints.
This is the API layer - handles HTTP translation only.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.application.users.commands import (
    ActivateUserCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    DeleteUserCommand,
    UpdateUserCommand,
)
from app.application.users.dto import UserDTO
from app.application.users.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
    ListUsersQuery,
)
from app.application.users.use_cases import UserUseCases
from app.domain.users.exceptions import UserDomainError

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic schemas for API
class UserResponse(BaseModel):
    """User response schema."""

    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_dto(cls, dto: UserDTO) -> "UserResponse":
        """Create from DTO."""
        return cls(
            id=dto.id,
            email=dto.email,
            full_name=dto.full_name,
            is_active=dto.is_active,
            is_superuser=dto.is_superuser,
        )


class CreateUserRequest(BaseModel):
    """Create user request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    is_superuser: bool = False


class UpdateUserRequest(BaseModel):
    """Update user request schema."""

    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    full_name: str | None = None


@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: CreateUserRequest,
    use_cases: UserUseCases = Depends(),
) -> UserResponse:
    """
    Create a new user.

    Args:
        request: Create user request
        use_cases: User use cases dependency

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    try:
        command = CreateUserCommand(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            is_superuser=request.is_superuser,
        )
        user_dto = await use_cases.create_user(command)
        return UserResponse.from_dto(user_dto)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    use_cases: UserUseCases = Depends(),
) -> UserResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID
        use_cases: User use cases dependency

    Returns:
        User details

    Raises:
        HTTPException: If user not found
    """
    try:
        query = GetUserByIdQuery(user_id=user_id)
        user_dto = await use_cases.get_user_by_id(query)
        return UserResponse.from_dto(user_dto)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    use_cases: UserUseCases = Depends(),
) -> list[UserResponse]:
    """
    List users with pagination.

    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        use_cases: User use cases dependency

    Returns:
        List of users
    """
    query = ListUsersQuery(skip=skip, limit=limit)
    users = await use_cases.list_users(query)
    return [UserResponse.from_dto(user) for user in users]


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    use_cases: UserUseCases = Depends(),
) -> UserResponse:
    """
    Update user.

    Args:
        user_id: User ID
        request: Update user request
        use_cases: User use cases dependency

    Returns:
        Updated user

    Raises:
        HTTPException: If user not found
    """
    try:
        command = UpdateUserCommand(
            user_id=user_id,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )
        user_dto = await use_cases.update_user(command)
        return UserResponse.from_dto(user_dto)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    use_cases: UserUseCases = Depends(),
) -> UserResponse:
    """
    Activate user.

    Args:
        user_id: User ID
        use_cases: User use cases dependency

    Returns:
        Activated user

    Raises:
        HTTPException: If user not found
    """
    try:
        command = ActivateUserCommand(user_id=user_id)
        user_dto = await use_cases.activate_user(command)
        return UserResponse.from_dto(user_dto)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    use_cases: UserUseCases = Depends(),
) -> UserResponse:
    """
    Deactivate user.

    Args:
        user_id: User ID
        use_cases: User use cases dependency

    Returns:
        Deactivated user

    Raises:
        HTTPException: If user not found
    """
    try:
        command = DeactivateUserCommand(user_id=user_id)
        user_dto = await use_cases.deactivate_user(command)
        return UserResponse.from_dto(user_dto)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    use_cases: UserUseCases = Depends(),
) -> None:
    """
    Delete user.

    Args:
        user_id: User ID
        use_cases: User use cases dependency

    Raises:
        HTTPException: If user not found
    """
    try:
        command = DeleteUserCommand(user_id=user_id)
        await use_cases.delete_user(command)
    except UserDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
