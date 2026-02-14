"""
Auth router - proxy to auth service.
"""

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()


# Simplified schemas for gateway (full schemas in auth-service)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


@router.post("/register")
async def register(request: RegisterRequest) -> dict:
    """
    Register a new user (proxies to auth-service).

    Note: In full implementation, this would call auth-service via HTTP or gRPC.
    """
    return {
        "message": "Registration endpoint - implement gRPC/HTTP proxy to auth-service",
        "data": request.model_dump(),
    }


@router.post("/login")
async def login(request: LoginRequest) -> dict:
    """
    Login (proxies to auth-service).

    Note: In full implementation, this would call auth-service via HTTP or gRPC.
    """
    return {
        "message": "Login endpoint - implement gRPC/HTTP proxy to auth-service",
        "data": request.model_dump(),
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str) -> dict:
    """
    Refresh token (proxies to auth-service).
    """
    return {
        "message": "Refresh endpoint - implement gRPC/HTTP proxy to auth-service"
    }
