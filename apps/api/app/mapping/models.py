from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from app.core.database import Base


class MapRun(Base):
    __tablename__ = "map_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(32), nullable=False)  # 'topic_map', 'lineage'
    scope = Column(JSON, nullable=False, default=dict)  # {type: 'library_subset' | 'search', ids: [...], query}
    params = Column(JSON, nullable=False, default=dict)  # seed, weights, thresholds
    embedding_model = Column(String(64), nullable=False, default="text-embedding-3-small")
    code_version = Column(String(32), nullable=False, default="v1.0.0")
    status = Column(String(32), nullable=False, default="pending")  # pending, completed, failed, refused
    record_count = Column(Integer, default=0)
    excluded = Column(JSON, default=list)  # [{work_id, reason}]
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime, nullable=True)

    clusters = relationship("MapCluster", back_populates="run", cascade="all, delete-orphan")
    nodes = relationship("LineageNode", back_populates="run", cascade="all, delete-orphan")
    edges = relationship("LineageEdge", back_populates="run", cascade="all, delete-orphan")
    gaps = relationship("GapSignal", back_populates="run", cascade="all, delete-orphan")


class MapCluster(Base):
    __tablename__ = "map_clusters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("map_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    label_source = Column(String(32), nullable=False, default="keywords")  # 'keywords', 'llm_constrained'
    keywords = Column(JSON, nullable=False, default=list)  # list of top terms
    size = Column(Integer, nullable=False, default=0)
    is_other = Column(Boolean, nullable=False, default=False)
    language_mix = Column(JSON, default=dict)

    run = relationship("MapRun", back_populates="clusters")
    members = relationship("MapClusterMember", back_populates="cluster", cascade="all, delete-orphan")


class MapClusterMember(Base):
    __tablename__ = "map_cluster_members"

    cluster_id = Column(String(36), ForeignKey("map_clusters.id", ondelete="CASCADE"), primary_key=True)
    work_id = Column(String(36), ForeignKey("works.id"), primary_key=True)
    membership_score = Column(Float, default=1.0)

    cluster = relationship("MapCluster", back_populates="members")


class LineageNode(Base):
    __tablename__ = "lineage_nodes"

    run_id = Column(String(36), ForeignKey("map_runs.id", ondelete="CASCADE"), primary_key=True)
    work_id = Column(String(36), ForeignKey("works.id"), primary_key=True)
    family_id = Column(String(36), ForeignKey("map_clusters.id"), nullable=True)
    role = Column(String(32), nullable=False, default="placed")  # 'root', 'placed', 'needs_review', 'unplaced'
    parent_work_id = Column(String(36), ForeignKey("works.id"), nullable=True)
    confidence = Column(Float, nullable=True)
    confidence_band = Column(String(16), nullable=True)  # 'high', 'medium', 'low'
    evidence = Column(JSON, nullable=False, default=dict)  # {cit, sem, kw, chr, shared_concepts, reason_codes}
    user_override = Column(JSON, nullable=True)  # {by, at, previous}
    missing_flags = Column(JSON, nullable=False, default=list)  # ['no_abstract', 'no_doi', ...]

    run = relationship("MapRun", back_populates="nodes")


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    run_id = Column(String(36), ForeignKey("map_runs.id", ondelete="CASCADE"), primary_key=True)
    parent_work_id = Column(String(36), ForeignKey("works.id"), primary_key=True)
    child_work_id = Column(String(36), ForeignKey("works.id"), primary_key=True)
    score = Column(Float, nullable=False)
    evidence = Column(JSON, nullable=False, default=dict)

    run = relationship("MapRun", back_populates="edges")


class PositioningRun(Base):
    __tablename__ = "positioning_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    lineage_run_id = Column(String(36), ForeignKey("map_runs.id"), nullable=False)
    manuscript_hash = Column(String(64), nullable=False)
    manuscript_text = Column(Text, nullable=True)
    retain_text = Column(Boolean, nullable=False, default=False)
    closest_family_id = Column(String(36), ForeignKey("map_clusters.id"), nullable=True)
    results = Column(JSON, nullable=False, default=dict)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class GapSignal(Base):
    __tablename__ = "gap_signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), ForeignKey("map_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(32), nullable=False)  # 'unresolved_condition', 'future_work', 'lineage_gap', 'data_quality'
    work_id = Column(String(36), ForeignKey("works.id"), nullable=True)
    chunk_id = Column(String(36), ForeignKey("chunks.id"), nullable=True)
    excerpt = Column(String(300), nullable=True)
    frequency = Column(Integer, default=1, nullable=False)
    extractor_version = Column(String(32), default="v1.0.0", nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    run = relationship("MapRun", back_populates="gaps")
