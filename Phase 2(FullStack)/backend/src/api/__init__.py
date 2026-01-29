"""API routes for the todo application."""

from fastapi import APIRouter
from .auth import router as auth_router
from .tasks import router as tasks_router
from .tags import router as tags_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
router.include_router(tags_router, prefix="/tags", tags=["tags"])
