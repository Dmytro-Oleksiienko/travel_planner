"""API routes for Travel Projects."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.project import ProjectStatus
from app.schemas.project import (
    PaginatedProjectsResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new travel project",
    description=(
        "Create a new travel project. Optionally include an array of places "
        "(artworks from the Art Institute of Chicago API) to add in the same request."
    ),
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    """Create a new travel project, optionally with places."""
    project = ProjectService.create_project(db, project_data)
    return project


@router.get(
    "",
    response_model=PaginatedProjectsResponse,
    summary="List all travel projects",
    description="Retrieve a paginated list of travel projects with optional filtering.",
)
def list_projects(
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(
        default=settings.DEFAULT_PER_PAGE,
        ge=1,
        le=settings.MAX_PER_PAGE,
        description="Items per page",
    ),
    status_filter: ProjectStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by project status",
    ),
    search: str | None = Query(
        default=None,
        description="Search projects by name",
    ),
    db: Session = Depends(get_db),
):
    """List all projects with pagination and filtering."""
    return ProjectService.list_projects(
        db,
        page=page,
        per_page=per_page,
        status=status_filter,
        search=search,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a single travel project",
    description="Retrieve a single travel project by its ID, including all its places.",
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get a single project by ID."""
    return ProjectService.get_project(db, project_id)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a travel project",
    description="Update a project's name, description, or start date.",
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update a project's information."""
    return ProjectService.update_project(db, project_id, project_data)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a travel project",
    description=(
        "Delete a travel project. A project cannot be deleted if any of its "
        "places are already marked as visited."
    ),
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project. Cannot delete if any places are visited."""
    ProjectService.delete_project(db, project_id)
