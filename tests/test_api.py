"""
Test authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient) -> None:
    """Test health check endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient) -> None:
    """Test root endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_user(client: TestClient) -> None:
    """Test user creation."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data


def test_login(client: TestClient) -> None:
    """Test user login."""
    # Create user first
    user_data = {
        "email": "login@example.com",
        "password": "loginpassword123",
        "full_name": "Login User",
    }
    client.post("/api/v1/users/", json=user_data)

    # Login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"],
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client: TestClient) -> None:
    """Test getting current user info."""
    # Create user
    user_data = {
        "email": "current@example.com",
        "password": "currentpassword123",
        "full_name": "Current User",
    }
    client.post("/api/v1/users/", json=user_data)

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]


def test_invalid_login(client: TestClient) -> None:
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    }

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_duplicate_user(client: TestClient) -> None:
    """Test creating duplicate user."""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "Duplicate User",
    }

    # Create first user
    response1 = client.post("/api/v1/users/", json=user_data)
    assert response1.status_code == 201

    # Try to create duplicate
    response2 = client.post("/api/v1/users/", json=user_data)
    assert response2.status_code == 409
