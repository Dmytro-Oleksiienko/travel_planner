"""SQLAlchemy model for Project Places (artworks from Art Institute of Chicago)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectPlace(Base):
    """Project Place model.

    Represents an artwork from the Art Institute of Chicago API
    that has been added to a travel project. Users can attach notes
    and mark the place as visited.
    """

    __tablename__ = "project_places"

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_project_external"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist_display: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    visited: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="places")

    def __repr__(self) -> str:
        return (
            f"<ProjectPlace(id={self.id}, external_id={self.external_id}, "
            f"title='{self.title}', visited={self.visited})>"
        )
