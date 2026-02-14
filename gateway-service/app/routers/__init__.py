"""
Gateway routers - proxy to backend services.
"""

from fastapi import APIRouter

from app.routers import auth, users

router = APIRouter(prefix="/api")

# Include service routers
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])
