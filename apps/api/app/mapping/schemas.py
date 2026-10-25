from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MapRunCreate(BaseModel):
    kind: str = Field(default="lineage", description="'topic_map' or 'lineage'")
    scope_type: str = Field(default="library_all", description="'library_all' or 'library_subset'")
    work_ids: Optional[List[str]] = Field(default=None, description="Optional subset of work IDs")
    seed: int = Field(default=42, description="Random seed for deterministic clustering")


class ClusterMemberInfo(BaseModel):
    work_id: str
    title: str
    year: Optional[int] = None
    membership_score: float = 1.0


class MapClusterResponse(BaseModel):
    id: str
    label: str
    label_source: str
    keywords: List[str]
    size: int
    is_other: bool
    members: List[ClusterMemberInfo] = []


class LineageNodeResponse(BaseModel):
    work_id: str
    title: str
    year: Optional[int] = None
    doi: Optional[str] = None
    family_id: Optional[str] = None
    family_label: Optional[str] = None
    role: str  # 'root', 'placed', 'needs_review', 'unplaced'
    parent_work_id: Optional[str] = None
    parent_title: Optional[str] = None
    confidence: Optional[float] = None
    confidence_band: Optional[str] = None  # 'high', 'medium', 'low'
    evidence: Dict[str, Any] = {}
    missing_flags: List[str] = []
    user_override: Optional[Dict[str, Any]] = None


class LineageEdgeResponse(BaseModel):
    parent_work_id: str
    child_work_id: str
    score: float
    evidence: Dict[str, Any]


class LineageGraphResponse(BaseModel):
    run_id: str
    project_id: str
    record_count: int
    families: List[MapClusterResponse]
    nodes: List[LineageNodeResponse]
    edges: List[LineageEdgeResponse]
    roots: List[str]
    status: str
    created_at: datetime


class AuditTableResponse(BaseModel):
    run_id: str
    total_records: int
    rows: List[LineageNodeResponse]
    summary: Dict[str, int]  # counts of high, medium, low, roots, needs_review


class UserOverrideRequest(BaseModel):
    work_id: str
    parent_work_id: Optional[str] = None
    family_id: Optional[str] = None
    reason: Optional[str] = "Manual expert correction"


class ManuscriptPositioningRequest(BaseModel):
    lineage_run_id: str
    title: str = Field(..., max_length=1000)
    abstract: str = Field(..., max_length=10000)
    references: Optional[List[str]] = Field(default=None, description="Optional cited DOIs or titles")
    retain_text: bool = Field(default=False, description="Whether to store raw manuscript text")


class TopParentCandidate(BaseModel):
    work_id: str
    title: str
    year: Optional[int]
    doi: Optional[str]
    family_id: Optional[str]
    family_label: Optional[str]
    score: float
    component_scores: Dict[str, float]  # cit, sem, kw, chr
    shared_concepts: List[str]


class ManuscriptPositioningResponse(BaseModel):
    id: str
    lineage_run_id: str
    closest_family_id: Optional[str]
    closest_family_label: Optional[str]
    runner_up_family_id: Optional[str]
    runner_up_family_label: Optional[str]
    top_parents: List[TopParentCandidate]
    shared_concepts: List[str]
    distinctive_concepts: List[str]
    fit_label: str  # 'Strong', 'Moderate', 'Weak'
    disclaimer: str = "Closest in the analyzed set — this does not claim global novelty or absence of prior art."


class GapSignalResponse(BaseModel):
    id: str
    kind: str  # 'unresolved_condition', 'future_work', 'lineage_gap', 'data_quality'
    work_id: Optional[str]
    work_title: Optional[str]
    excerpt: Optional[str]
    frequency: int
    confidence: Optional[float]
    disclaimer: str = "Gaps identified are internal to the analyzed set and do not constitute global novelty."
