"""Main API router aggregating all v1 routes."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.expressions import router as expressions_router
from app.api.images import router as images_router
from app.api.memory import router as memory_router
from app.api.users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(expressions_router)
router.include_router(images_router)
router.include_router(memory_router)
