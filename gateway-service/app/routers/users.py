"""
Users router - proxy to user service.
"""

from uuid import UUID

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_users(page: int = 1, page_size: int = 50) -> dict:
    """
    List users (proxies to user-service).

    Note: In full implementation, this would call user-service via gRPC.
    """
    return {
        "message": "List users endpoint - implement gRPC proxy to user-service",
        "params": {"page": page, "page_size": page_size},
    }


@router.get("/{user_id}")
async def get_user(user_id: UUID) -> dict:
    """
    Get user (proxies to user-service).
    """
    return {
        "message": "Get user endpoint - implement gRPC proxy to user-service",
        "user_id": str(user_id),
    }


@router.post("")
async def create_user(user_data: dict) -> dict:
    """
    Create user (proxies to user-service).
    """
    return {
        "message": "Create user endpoint - implement gRPC proxy to user-service",
        "data": user_data,
    }


@router.put("/{user_id}")
async def update_user(user_id: UUID, user_data: dict) -> dict:
    """
    Update user (proxies to user-service).
    """
    return {
        "message": "Update user endpoint - implement gRPC proxy to user-service",
        "user_id": str(user_id),
        "data": user_data,
    }


@router.delete("/{user_id}")
async def delete_user(user_id: UUID) -> dict:
    """
    Delete user (proxies to user-service).
    """
    return {
        "message": "Delete user endpoint - implement gRPC proxy to user-service",
        "user_id": str(user_id),
    }
