"""Business logic for Travel Projects."""

import math

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.exceptions import ConflictException, NotFoundException
from app.models.place import ProjectPlace
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.artic_api import ArticAPIClient


class ProjectService:
    """Service layer for project operations."""

    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate) -> Project:
        """Create a new travel project, optionally with places.

        Args:
            db: Database session.
            project_data: Project creation data.

        Returns:
            Created Project instance.

        Raises:
            BadRequestException: If any place external_id is invalid.
        """
        # Create the project
        project = Project(
            name=project_data.name,
            description=project_data.description,
            start_date=project_data.start_date,
        )
        db.add(project)
        db.flush()  # Get the project ID

        # Add places if provided
        if project_data.places:
            if len(project_data.places) > 10:
                from app.exceptions import BadRequestException
                raise BadRequestException("A project can have at most 10 places")

            # Check for duplicate external_ids in the request
            external_ids = [p.external_id for p in project_data.places]
            if len(external_ids) != len(set(external_ids)):
                from app.exceptions import BadRequestException
                raise BadRequestException("Duplicate external_id values in the request")

            for place_data in project_data.places:
                # Validate artwork exists in Art Institute API
                artwork = ArticAPIClient.validate_artwork_exists(place_data.external_id)

                place = ProjectPlace(
                    project_id=project.id,
                    external_id=artwork["id"],
                    title=artwork["title"],
                    artist_display=artwork.get("artist_display"),
                )
                db.add(place)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project(db: Session, project_id: int) -> Project:
        """Get a single project by ID.

        Args:
            db: Database session.
            project_id: Project ID.

        Returns:
            Project instance with places loaded.

        Raises:
            NotFoundException: If project not found.
        """
        project = (
            db.query(Project)
            .options(joinedload(Project.places))
            .filter(Project.id == project_id)
            .first()
        )
        if not project:
            raise NotFoundException("Project", project_id)
        return project

    @staticmethod
    def list_projects(
        db: Session,
        page: int = 1,
        per_page: int = 10,
        status: ProjectStatus | None = None,
        search: str | None = None,
    ) -> dict:
        """List projects with pagination and filtering.

        Args:
            db: Database session.
            page: Page number (1-indexed).
            per_page: Items per page.
            status: Optional status filter.
            search: Optional search query for project name.

        Returns:
            Dictionary with items, total, page, per_page, pages.
        """
        query = db.query(Project)

        # Apply filters
        if status:
            query = query.filter(Project.status == status)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))

        # Count total
        total = query.count()
        pages = math.ceil(total / per_page) if total > 0 else 1

        # Paginate
        projects = (
            query.order_by(Project.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        # Build response with counts
        items = []
        for project in projects:
            places_count = (
                db.query(func.count(ProjectPlace.id))
                .filter(ProjectPlace.project_id == project.id)
                .scalar()
            )
            visited_count = (
                db.query(func.count(ProjectPlace.id))
                .filter(
                    ProjectPlace.project_id == project.id,
                    ProjectPlace.visited == True,
                )
                .scalar()
            )
            items.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "start_date": project.start_date,
                "status": project.status,
                "places_count": places_count,
                "visited_count": visited_count,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    @staticmethod
    def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Project:
        """Update a project's information.

        Args:
            db: Database session.
            project_id: Project ID.
            project_data: Fields to update.

        Returns:
            Updated Project instance.

        Raises:
            NotFoundException: If project not found.
        """
        project = (
            db.query(Project)
            .options(joinedload(Project.places))
            .filter(Project.id == project_id)
            .first()
        )
        if not project:
            raise NotFoundException("Project", project_id)

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> None:
        """Delete a project.

        A project cannot be deleted if any of its places are marked as visited.

        Args:
            db: Database session.
            project_id: Project ID.

        Raises:
            NotFoundException: If project not found.
            ConflictException: If any places are visited.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException("Project", project_id)

        # Check if any places are visited
        visited_count = (
            db.query(func.count(ProjectPlace.id))
            .filter(
                ProjectPlace.project_id == project_id,
                ProjectPlace.visited == True,
            )
            .scalar()
        )

        if visited_count > 0:
            raise ConflictException(
                "Cannot delete project: it has places that are already marked as visited"
            )

        db.delete(project)
        db.commit()

    @staticmethod
    def check_and_update_project_status(db: Session, project_id: int) -> None:
        """Check if all places in a project are visited and update status.

        Args:
            db: Database session.
            project_id: Project ID.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        total_places = (
            db.query(func.count(ProjectPlace.id))
            .filter(ProjectPlace.project_id == project_id)
            .scalar()
        )

        if total_places == 0:
            # No places — keep as planning
            if project.status != ProjectStatus.PLANNING:
                project.status = ProjectStatus.PLANNING
                db.commit()
            return

        visited_count = (
            db.query(func.count(ProjectPlace.id))
            .filter(
                ProjectPlace.project_id == project_id,
                ProjectPlace.visited == True,
            )
            .scalar()
        )

        if visited_count == total_places:
            project.status = ProjectStatus.COMPLETED
        else:
            project.status = ProjectStatus.PLANNING

        db.commit()
