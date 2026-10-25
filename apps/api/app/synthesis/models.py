import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, PrimaryKeyConstraint
from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class Chunk(Base):
    """Text chunks extracted from works (SYN-002)."""
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, default=0, nullable=False)
    section = Column(String(100), default="abstract", nullable=False)  # abstract | methods | results | discussion
    text = Column(Text, nullable=False)
    embedding_model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class Extraction(Base):
    """Per-study structured extraction table (SYN-006, SYN-007)."""
    __tablename__ = "extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    work_id = Column(String(36), ForeignKey("works.id", ondelete="CASCADE"), nullable=False, index=True)
    population = Column(Text, nullable=True)
    method = Column(Text, nullable=True)
    finding = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    supporting_chunk_ids = Column(JSON, nullable=True)  # List of chunk IDs supporting the extraction
    edited_by_user = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)


class SynthesisRun(Base):
    """Grounded RAG synthesis runs with claim-level audit (SYN-008, SYN-017)."""
    __tablename__ = "synthesis_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    status = Column(String(50), default="completed", nullable=False)  # completed | refused | low_confidence
    claims_json = Column(JSON, nullable=True)  # List of atomic claims with citation IDs and verdicts
    refusal_reason = Column(Text, nullable=True)
    model = Column(String(100), default="gemini-1.5-flash", nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)


class SynthesisRunChunk(Base):
    """Mapping of cited chunks to claims with independent verification verdict (SYN-009, SYN-010)."""
    __tablename__ = "synthesis_run_chunks"

    synthesis_run_id = Column(String(36), ForeignKey("synthesis_runs.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(36), ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False)
    claim_index = Column(Integer, default=0, nullable=False)
    verification_verdict = Column(String(50), default="supported", nullable=False)  # supported | partially_supported | unsupported

    __table_args__ = (
        PrimaryKeyConstraint("synthesis_run_id", "chunk_id", "claim_index"),
    )
