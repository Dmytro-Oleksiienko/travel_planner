"""Pydantic schemas for Project Places."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlaceAddRequest(BaseModel):
    """Schema for adding a place to a project."""

    external_id: int = Field(..., gt=0, description="Artwork ID from Art Institute of Chicago API")


class PlaceUpdate(BaseModel):
    """Schema for updating a place within a project."""

    notes: str | None = Field(None, description="Notes about the place")
    visited: bool | None = Field(None, description="Whether the place has been visited")


class PlaceResponse(BaseModel):
    """Schema for place response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime


class PaginatedPlacesResponse(BaseModel):
    """Paginated response for places listing."""

    items: list[PlaceResponse]
    total: int
    page: int
    per_page: int
    pages: int
