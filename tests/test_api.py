"""
API endpoint tests.
"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_create_user(client: TestClient) -> None:
    """Test user creation."""
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }

    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data


def test_login(client: TestClient) -> None:
    """Test login."""
    # Create user first
    user_data = {
        "email": "login@example.com",
        "password": "securepassword123",
        "full_name": "Login Test",
    }
    client.post("/api/users/", json=user_data)

    # Login
    login_data = {
        "email": "login@example.com",
        "password": "securepassword123",
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client: TestClient) -> None:
    """Test getting current user."""
    # Create and login
    user_data = {
        "email": "current@example.com",
        "password": "securepassword123",
        "full_name": "Current User",
    }
    client.post("/api/users/", json=user_data)

    login_response = client.post(
        "/api/auth/login",
        json={"email": "current@example.com", "password": "securepassword123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"


def test_unauthorized_access(client: TestClient) -> None:
    """Test unauthorized access."""
    response = client.get("/api/users/me")
    assert response.status_code == 401
