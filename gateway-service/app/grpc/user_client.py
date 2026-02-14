"""
gRPC client for user service.
"""

import grpc
import structlog

from app.core.config import settings

# Import generated proto files
try:
    from app.grpc.generated import common_pb2, user_pb2, user_pb2_grpc
except ImportError:
    user_pb2 = None
    user_pb2_grpc = None
    common_pb2 = None

logger = structlog.get_logger(__name__)


class UserServiceClient:
    """gRPC client for user service."""

    def __init__(self):
        """Initialize client."""
        self.channel = None
        self.stub = None

    async def connect(self) -> None:
        """Connect to user service."""
        if not user_pb2_grpc:
            logger.warning("gRPC proto files not generated")
            return

        self.channel = grpc.aio.insecure_channel(
            settings.USER_SERVICE_GRPC_URL
        )
        self.stub = user_pb2_grpc.UserServiceStub(self.channel)
        logger.info(
            "Connected to user service", url=settings.USER_SERVICE_GRPC_URL
        )

    async def close(self) -> None:
        """Close connection."""
        if self.channel:
            await self.channel.close()


# Global client instance
user_client = UserServiceClient()
