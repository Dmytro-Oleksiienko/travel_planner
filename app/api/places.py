"""API routes for Project Places."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.place import (
    PaginatedPlacesResponse,
    PlaceAddRequest,
    PlaceResponse,
    PlaceUpdate,
)
from app.services.place_service import PlaceService

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/places",
    tags=["Places"],
)


@router.post(
    "",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a place to a project",
    description=(
        "Add an artwork from the Art Institute of Chicago to a project. "
        "The backend validates that the artwork exists in the external API. "
        "A project can have at most 10 places, and duplicate artworks are not allowed."
    ),
)
def add_place(
    project_id: int,
    place_data: PlaceAddRequest,
    db: Session = Depends(get_db),
):
    """Add a place to a project."""
    return PlaceService.add_place(db, project_id, place_data)


@router.get(
    "",
    response_model=PaginatedPlacesResponse,
    summary="List all places for a project",
    description="Retrieve a paginated list of places for a specific project.",
)
def list_places(
    project_id: int,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(
        default=settings.DEFAULT_PER_PAGE,
        ge=1,
        le=settings.MAX_PER_PAGE,
        description="Items per page",
    ),
    visited: bool | None = Query(
        default=None,
        description="Filter by visited status",
    ),
    db: Session = Depends(get_db),
):
    """List all places for a project."""
    return PlaceService.list_places(
        db,
        project_id=project_id,
        page=page,
        per_page=per_page,
        visited=visited,
    )


@router.get(
    "/{place_id}",
    response_model=PlaceResponse,
    summary="Get a single place",
    description="Retrieve details of a specific place within a project.",
)
def get_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
):
    """Get a single place within a project."""
    return PlaceService.get_place(db, project_id, place_id)


@router.patch(
    "/{place_id}",
    response_model=PlaceResponse,
    summary="Update a place in a project",
    description=(
        "Update a place's notes or mark it as visited. "
        "When all places in a project are marked as visited, "
        "the project status is automatically set to 'completed'."
    ),
)
def update_place(
    project_id: int,
    place_id: int,
    place_data: PlaceUpdate,
    db: Session = Depends(get_db),
):
    """Update a place's notes or visited status."""
    return PlaceService.update_place(db, project_id, place_id, place_data)
