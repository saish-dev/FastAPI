"""gRPC clients package."""

from app.grpc.auth_client import AuthServiceClient, auth_client
from app.grpc.user_client import UserServiceClient, user_client

__all__ = [
    "AuthServiceClient",
    "auth_client",
    "UserServiceClient",
    "user_client",
]
