from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class SynthesisRequest(BaseModel):
    query: str = Field(..., min_length=5, description="Scholarly research question to synthesize")
    scope: str = Field("library", pattern="^(library|screened_included)$")
    max_works: int = Field(10, ge=1, le=50)


class AtomicClaim(BaseModel):
    claim_index: int
    claim_text: str
    citation_chunk_ids: List[str]
    verdict: str = "supported"  # "supported" | "partially_supported" | "unsupported"
    evidence_excerpt: Optional[str] = None
    work_title: Optional[str] = None
    doi: Optional[str] = None


class SynthesisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    query: str
    status: str  # "completed" | "refused" | "low_confidence"
    claims: List[AtomicClaim]
    refusal_reason: Optional[str] = None
    retrieved_works: List[Dict[str, Any]]
    verified_percentage: float
    model: str
    created_at: datetime


class ExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    work_id: str
    title: str
    population: Optional[str]
    method: Optional[str]
    finding: Optional[str]
    limitations: Optional[str]
    edited_by_user: bool
    created_at: datetime
