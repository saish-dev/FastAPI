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
    assert "environment" in data


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_create_user(client: TestClient) -> None:
    """Test user creation."""
    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert data["is_active"] is True


def test_get_user(client: TestClient) -> None:
    """Test getting user by ID."""
    # Create user first
    user_data = {
        "email": "gettest@example.com",
        "password": "securepassword123",
        "full_name": "Get Test User",
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Get user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_list_users(client: TestClient) -> None:
    """Test listing users."""
    # Create a few users
    for i in range(3):
        user_data = {
            "email": f"user{i}@example.com",
            "password": "securepassword123",
            "full_name": f"User {i}",
        }
        client.post("/api/v1/users/", json=user_data)

    # List users
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3


def test_update_user(client: TestClient) -> None:
    """Test updating user."""
    # Create user
    user_data = {
        "email": "update@example.com",
        "password": "securepassword123",
        "full_name": "Update Test",
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Update user
    update_data = {"full_name": "Updated Name"}
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]


def test_delete_user(client: TestClient) -> None:
    """Test deleting user."""
    # Create user
    user_data = {
        "email": "delete@example.com",
        "password": "securepassword123",
        "full_name": "Delete Test",
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]

    # Delete user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404
