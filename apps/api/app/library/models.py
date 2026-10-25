import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class LibraryItem(Base):
    """Project-scoped library item mapping project to a canonical work (LIB-008)."""
    __tablename__ = "library_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    added_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class ImportBatch(Base):
    """Tracks batch bibliographic imports with full audit parse report (LIB-002, LIB-004)."""
    __tablename__ = "import_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # ris | bibtex | csv | openalex
    total_count = Column(Integer, default=0, nullable=False)
    imported_count = Column(Integer, default=0, nullable=False)
    skipped_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    report_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class DedupCandidate(Base):
    """Potential duplicate records awaiting human review (LIB-007)."""
    __tablename__ = "dedup_candidates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_a_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    work_b_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending | merged | dismissed
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
