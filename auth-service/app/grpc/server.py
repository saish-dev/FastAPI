"""
gRPC server implementation for auth service.
"""

import asyncio
from concurrent import futures
from uuid import UUID

import grpc
import structlog

from app.core.config import settings
from app.db.session import async_session_maker
from app.events.publisher import event_publisher
from app.repositories.user_repository import (
    ApiKeyRepository,
    RefreshTokenRepository,
    UserRepository,
)
from app.services.auth_service import AuthService

# Import generated proto files (will be available after running generate_grpc.sh)
try:
    from app.grpc.generated import auth_pb2, auth_pb2_grpc, common_pb2
except ImportError:
    # Fallback for when proto files haven't been generated yet
    auth_pb2 = None
    auth_pb2_grpc = None
    common_pb2 = None

logger = structlog.get_logger(__name__)


class AuthServicer:
    """gRPC servicer for auth service."""

    async def _get_auth_service(self) -> AuthService:
        """Get auth service instance with repositories."""
        async with async_session_maker() as db:
            user_repo = UserRepository(db)
            api_key_repo = ApiKeyRepository(db)
            refresh_token_repo = RefreshTokenRepository(db)
            return AuthService(
                user_repo, api_key_repo, refresh_token_repo, event_publisher
            )

    async def ValidateToken(self, request, context):
        """Validate JWT token."""
        if not auth_pb2:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("gRPC proto files not generated")
            return auth_pb2.ValidateTokenResponse()

        try:
            auth_service = await self._get_auth_service()
            result = await auth_service.validate_token(request.token)

            response = auth_pb2.ValidateTokenResponse(
                valid=result.valid,
            )

            if result.valid and result.user_id:
                response.user_id.value = str(result.user_id)
                response.email = result.email or ""

            return response

        except Exception as e:
            logger.error("ValidateToken error", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.ValidateTokenResponse(valid=False)

    async def ValidateApiKey(self, request, context):
        """Validate API key."""
        if not auth_pb2:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("gRPC proto files not generated")
            return auth_pb2.ValidateApiKeyResponse()

        try:
            auth_service = await self._get_auth_service()
            result = await auth_service.validate_api_key(request.api_key)

            response = auth_pb2.ValidateApiKeyResponse(
                valid=result.valid,
                service_name=result.service_name or "",
                permissions=result.permissions,
            )

            return response

        except Exception as e:
            logger.error("ValidateApiKey error", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return auth_pb2.ValidateApiKeyResponse(valid=False)

    async def Login(self, request, context):
        """Login with credentials."""
        if not auth_pb2:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("gRPC proto files not generated")
            return auth_pb2.LoginResponse()

        try:
            auth_service = await self._get_auth_service()
            result = await auth_service.login(request.email, request.password)

            response = auth_pb2.LoginResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                expires_in=result.expires_in,
            )
            response.user_id.value = str(result.user_id)

            return response

        except Exception as e:
            logger.error("Login error", error=str(e))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_pb2.LoginResponse()

    async def RefreshToken(self, request, context):
        """Refresh access token."""
        if not auth_pb2:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("gRPC proto files not generated")
            return auth_pb2.RefreshTokenResponse()

        try:
            auth_service = await self._get_auth_service()
            result = await auth_service.refresh_access_token(
                request.refresh_token
            )

            response = auth_pb2.RefreshTokenResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                expires_in=result.expires_in,
            )

            return response

        except Exception as e:
            logger.error("RefreshToken error", error=str(e))
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details(str(e))
            return auth_pb2.RefreshTokenResponse()


async def serve() -> None:
    """Start gRPC server."""
    if not auth_pb2_grpc:
        logger.warning("gRPC proto files not generated, skipping gRPC server")
        return

    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=settings.GRPC_MAX_WORKERS)
    )
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)
    server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")

    logger.info("Starting gRPC server", port=settings.GRPC_PORT)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
