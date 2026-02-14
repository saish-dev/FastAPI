"""
API v1 router.
Aggregates all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1 import users

router = APIRouter(prefix="/v1")

# Include feature routers
router.include_router(users.router)
