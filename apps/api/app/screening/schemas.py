from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProtocolCreate(BaseModel):
    question: str = Field(..., min_length=5, description="Primary research question")
    pico: Optional[Dict[str, Any]] = None  # {"P": "...", "I": "...", "C": "...", "O": "..."}
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None


class ProtocolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    question: str
    pico_json: Optional[Dict[str, Any]] = None
    inclusion_criteria: Optional[str] = None
    exclusion_criteria: Optional[str] = None
    version: int
    created_at: datetime


class ExclusionReasonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    label: str
    is_default: bool


class DecisionCreate(BaseModel):
    work_id: str
    stage: str = Field("title_abstract", pattern="^(title_abstract|full_text)$")
    verdict: str = Field(..., pattern="^(include|exclude|maybe)$")
    reason_code: Optional[str] = None
    notes: Optional[str] = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    work_id: str
    stage: str
    verdict: str
    reason_code: Optional[str]
    notes: Optional[str]
    protocol_version: int
    created_at: datetime


class ConflictItem(BaseModel):
    work_id: str
    title: str
    stage: str
    decisions: List[Dict[str, Any]]  # [{"user_id": "...", "verdict": "include", "reason": "..."}]


class ResolutionCreate(BaseModel):
    work_id: str
    stage: str = Field(..., pattern="^(title_abstract|full_text)$")
    final_verdict: str = Field(..., pattern="^(include|exclude)$")
    reason_code: Optional[str] = None
    rationale: Optional[str] = None


class KappaResponse(BaseModel):
    stage: str
    total_dual_reviewed: int
    observed_agreement: float
    expected_agreement: float
    cohen_kappa: Optional[float]
    interpretation: str  # "Slight", "Moderate", "Substantial", "Almost Perfect", "Undefined"


class PrismaBoxes(BaseModel):
    identified: int
    duplicates_removed: int
    records_screened: int
    excluded_ta: int
    reports_sought: int
    reports_assessed_ft: int
    excluded_ft: int
    studies_included: int


class PrismaReconciliation(BaseModel):
    ok: bool
    issues: List[str]


class PrismaResponse(BaseModel):
    boxes: PrismaBoxes
    reasons: List[Dict[str, Any]]
    reconciliation: PrismaReconciliation
