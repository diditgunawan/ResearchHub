import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, PrimaryKeyConstraint
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Project(Base):
    """Project tenant boundary matching blueprints/03-data-model.sql."""
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class ProjectMember(Base):
    """Project membership and role permissions (owner, reviewer, viewer)."""
    __tablename__ = "project_members"

    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False, default="reviewer")  # owner | reviewer | viewer
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id"),
    )
