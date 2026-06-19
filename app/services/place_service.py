"""Business logic for Project Places."""

import math

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import BadRequestException, ConflictException, NotFoundException
from app.models.place import ProjectPlace
from app.models.project import Project
from app.schemas.place import PlaceAddRequest, PlaceUpdate
from app.services.artic_api import ArticAPIClient
from app.services.project_service import ProjectService


class PlaceService:
    """Service layer for place operations within projects."""

    @staticmethod
    def add_place(db: Session, project_id: int, place_data: PlaceAddRequest) -> ProjectPlace:
        """Add a place (artwork) to a project.

        Validates:
        - Project exists
        - Artwork exists in Art Institute API
        - Project has fewer than 10 places
        - Artwork is not already in the project

        Args:
            db: Database session.
            project_id: Project ID.
            place_data: Place data with external_id.

        Returns:
            Created ProjectPlace instance.
        """
        # Check project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project", project_id)

        # Check place limit
        current_count = (
            db.query(func.count(ProjectPlace.id))
            .filter(ProjectPlace.project_id == project_id)
            .scalar()
        )
        if current_count >= 10:
            raise BadRequestException(
                "Project already has the maximum number of places (10)"
            )

        # Check for duplicate
        existing = (
            db.query(ProjectPlace)
            .filter(
                ProjectPlace.project_id == project_id,
                ProjectPlace.external_id == place_data.external_id,
            )
            .first()
        )
        if existing:
            raise ConflictException(
                f"Place with external_id {place_data.external_id} "
                f"already exists in this project"
            )

        # Validate artwork exists in Art Institute API
        artwork = ArticAPIClient.validate_artwork_exists(place_data.external_id)

        # Create the place
        place = ProjectPlace(
            project_id=project_id,
            external_id=artwork["id"],
            title=artwork["title"],
            artist_display=artwork.get("artist_display"),
        )
        db.add(place)
        db.commit()
        db.refresh(place)

        return place

    @staticmethod
    def get_place(db: Session, project_id: int, place_id: int) -> ProjectPlace:
        """Get a single place within a project.

        Args:
            db: Database session.
            project_id: Project ID.
            place_id: Place ID.

        Returns:
            ProjectPlace instance.

        Raises:
            NotFoundException: If project or place not found.
        """
        # Check project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project", project_id)

        place = (
            db.query(ProjectPlace)
            .filter(
                ProjectPlace.id == place_id,
                ProjectPlace.project_id == project_id,
            )
            .first()
        )
        if not place:
            raise NotFoundException("Place", place_id)

        return place

    @staticmethod
    def list_places(
        db: Session,
        project_id: int,
        page: int = 1,
        per_page: int = 10,
        visited: bool | None = None,
    ) -> dict:
        """List places for a project with pagination and filtering.

        Args:
            db: Database session.
            project_id: Project ID.
            page: Page number.
            per_page: Items per page.
            visited: Optional filter by visited status.

        Returns:
            Dictionary with items, total, page, per_page, pages.
        """
        # Check project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project", project_id)

        query = db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id)

        # Apply filters
        if visited is not None:
            query = query.filter(ProjectPlace.visited == visited)

        # Count total
        total = query.count()
        pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        places = (
            query.order_by(ProjectPlace.created_at.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return {
            "items": places,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    @staticmethod
    def update_place(
        db: Session, project_id: int, place_id: int, place_data: PlaceUpdate
    ) -> ProjectPlace:
        """Update a place within a project (notes, visited status).

        When a place is marked as visited, checks if all places in the project
        are visited and updates the project status accordingly.

        Args:
            db: Database session.
            project_id: Project ID.
            place_id: Place ID.
            place_data: Fields to update.

        Returns:
            Updated ProjectPlace instance.
        """
        # Check project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project", project_id)

        place = (
            db.query(ProjectPlace)
            .filter(
                ProjectPlace.id == place_id,
                ProjectPlace.project_id == project_id,
            )
            .first()
        )
        if not place:
            raise NotFoundException("Place", place_id)

        update_data = place_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(place, field, value)

        db.commit()
        db.refresh(place)

        # Check and update project status if visited changed
        if "visited" in update_data:
            ProjectService.check_and_update_project_status(db, project_id)

        return place
