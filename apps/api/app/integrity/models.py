import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class AiUsageLog(Base):
    """Granular audit trail for AI-use disclosure statements (ETH-002, ETH-003)."""
    __tablename__ = "ai_usage_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    feature = Column(String(50), nullable=False)  # "synthesis" | "screening_suggestion" | "extraction"
    stage = Column(String(50), nullable=True)
    model = Column(String(100), nullable=False)
    purpose = Column(String(255), nullable=True)
    tokens_in = Column(Integer, default=0, nullable=False)
    tokens_out = Column(Integer, default=0, nullable=False)
    human_reviewed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class ReferenceCheck(Base):
    """Reference list integrity audit log (retractions, unresolved DOIs, mismatches) (ETH-005, ETH-007)."""
    __tablename__ = "reference_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=True)
    doi = Column(String(255), nullable=True, index=True)
    title = Column(Text, nullable=False)
    status = Column(String(50), default="verified", nullable=False)  # "verified" | "unresolved" | "mismatch" | "retracted"
    details = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
