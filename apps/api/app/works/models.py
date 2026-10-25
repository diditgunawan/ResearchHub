import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, PrimaryKeyConstraint
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Work(Base):
    """Canonical public scholarly works table matching blueprints/03-data-model.sql."""
    __tablename__ = "works"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    doi = Column(String(255), unique=True, nullable=True, index=True)
    openalex_id = Column(String(255), unique=True, nullable=True, index=True)
    pmid = Column(String(50), unique=True, nullable=True, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    year = Column(Integer, nullable=True, index=True)
    venue = Column(String(500), nullable=True)
    work_type = Column(String(100), default="article", nullable=True)
    is_oa = Column(Boolean, default=False, nullable=False)
    oa_url = Column(String(1000), nullable=True)
    cited_by_count = Column(Integer, default=0, nullable=False)
    retracted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class Author(Base):
    """Normalized author records."""
    __tablename__ = "authors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    orcid = Column(String(50), nullable=True, unique=True)


class WorkAuthor(Base):
    """Many-to-many relationship preserving authorship position."""
    __tablename__ = "work_authors"

    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(String(36), ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, default=1, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("work_id", "author_id"),
    )


class WorkCitation(Base):
    """Citation graph directed edges (citing -> cited)."""
    __tablename__ = "work_citations"

    citing_work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    cited_work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("citing_work_id", "cited_work_id"),
    )
