"""Pydantic schemas for Travel Projects."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus
from app.schemas.place import PlaceAddRequest, PlaceResponse


class ProjectBase(BaseModel):
    """Base schema for project data."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    start_date: date | None = Field(None, description="Planned start date")


class ProjectCreate(ProjectBase):
    """Schema for creating a project, optionally with places."""

    places: list[PlaceAddRequest] | None = Field(
        None,
        max_length=10,
        description="Optional list of places to add (max 10)",
    )


class ProjectUpdate(BaseModel):
    """Schema for updating a project. All fields are optional."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Project name")
    description: str | None = Field(None, description="Project description")
    start_date: date | None = Field(None, description="Planned start date")


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    places: list[PlaceResponse] = []


class ProjectListResponse(ProjectBase):
    """Schema for project in list response (without places details)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ProjectStatus
    places_count: int = Field(0, description="Number of places in the project")
    visited_count: int = Field(0, description="Number of visited places")
    created_at: datetime
    updated_at: datetime


class PaginatedProjectsResponse(BaseModel):
    """Paginated response for projects listing."""

    items: list[ProjectListResponse]
    total: int
    page: int
    per_page: int
    pages: int
