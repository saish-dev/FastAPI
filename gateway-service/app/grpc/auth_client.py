"""
gRPC client for auth service.
"""

import grpc
import structlog

from app.core.config import settings

# Import generated proto files (will be available after running generate_grpc.sh)
try:
    from app.grpc.generated import auth_pb2, auth_pb2_grpc
except ImportError:
    auth_pb2 = None
    auth_pb2_grpc = None

logger = structlog.get_logger(__name__)


class AuthServiceClient:
    """gRPC client for auth service."""

    def __init__(self):
        """Initialize client."""
        self.channel = None
        self.stub = None

    async def connect(self) -> None:
        """Connect to auth service."""
        if not auth_pb2_grpc:
            logger.warning("gRPC proto files not generated")
            return

        self.channel = grpc.aio.insecure_channel(
            settings.AUTH_SERVICE_GRPC_URL
        )
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)
        logger.info(
            "Connected to auth service", url=settings.AUTH_SERVICE_GRPC_URL
        )

    async def close(self) -> None:
        """Close connection."""
        if self.channel:
            await self.channel.close()

    async def validate_token(self, token: str) -> dict:
        """Validate JWT token."""
        if not self.stub or not auth_pb2:
            return {"valid": False}

        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = await self.stub.ValidateToken(request)

            return {
                "valid": response.valid,
                "user_id": response.user_id.value if response.valid else None,
                "email": response.email if response.valid else None,
            }
        except Exception as e:
            logger.error("ValidateToken error", error=str(e))
            return {"valid": False}

    async def validate_api_key(self, api_key: str) -> dict:
        """Validate API key."""
        if not self.stub or not auth_pb2:
            return {"valid": False}

        try:
            request = auth_pb2.ValidateApiKeyRequest(api_key=api_key)
            response = await self.stub.ValidateApiKey(request)

            return {
                "valid": response.valid,
                "service_name": (
                    response.service_name if response.valid else None
                ),
                "permissions": (
                    list(response.permissions) if response.valid else []
                ),
            }
        except Exception as e:
            logger.error("ValidateApiKey error", error=str(e))
            return {"valid": False}


# Global client instance
auth_client = AuthServiceClient()
