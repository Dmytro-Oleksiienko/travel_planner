"""API routes package."""

from app.api.places import router as places_router
from app.api.projects import router as projects_router

__all__ = ["places_router", "projects_router"]
