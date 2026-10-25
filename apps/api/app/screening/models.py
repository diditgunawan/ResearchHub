import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class ReviewProtocol(Base):
    """Versioned systematic review protocol (SCR-001, SCR-002)."""
    __tablename__ = "review_protocols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    pico_json = Column(JSON, nullable=True)  # Population, Intervention, Comparison, Outcome
    inclusion_criteria = Column(Text, nullable=True)
    exclusion_criteria = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class ExclusionReason(Base):
    """Controlled vocabulary of exclusion reasons (SCR-005)."""
    __tablename__ = "exclusion_reasons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    code = Column(String(50), nullable=False)
    label = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)


class ScreeningDecision(Base):
    """Append-only audit log of reviewer screening decisions (SCR-004)."""
    __tablename__ = "screening_decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)  # "title_abstract" | "full_text"
    verdict = Column(String(20), nullable=False)  # "include" | "exclude" | "maybe"
    reason_code = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    protocol_version = Column(Integer, default=1, nullable=False)
    supersedes_id = Column(String(36), nullable=True)  # Used when a reviewer changes their decision
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class ScreeningResolution(Base):
    """Third-party conflict resolution decision (SCR-009)."""
    __tablename__ = "screening_resolutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)  # "title_abstract" | "full_text"
    resolved_by = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    final_verdict = Column(String(20), nullable=False)  # "include" | "exclude"
    reason_code = Column(String(50), nullable=True)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class AiSuggestion(Base):
    """Non-authoritative AI screening suggestions (SCR-014, SCR-015)."""
    __tablename__ = "ai_suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(50), nullable=False)
    suggestion = Column(String(20), nullable=False)  # "include" | "exclude" | "maybe"
    rationale = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)
    prompt_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
