from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AuthorRecord(BaseModel):
    name: str
    orcid: Optional[str] = None
    position: Optional[int] = None


class VenueRecord(BaseModel):
    name: str
    issn_l: Optional[str] = None
    openalex_id: Optional[str] = None


class WorkRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doi: Optional[str] = None
    openalex_id: Optional[str] = None
    pmid: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    work_type: Optional[str] = "article"
    language: Optional[str] = "en"
    authors: List[AuthorRecord] = Field(default_factory=list)
    venue: Optional[VenueRecord] = None
    is_oa: bool = False
    oa_url: Optional[str] = None
    cited_by_count: int = 0
    retracted: bool = False
    provenance: Dict[str, Any] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=500)
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    oa_only: bool = False
    language: Optional[str] = None
    cursor: Optional[str] = None
    page_size: int = Field(25, ge=1, le=100)


class SearchPage(BaseModel):
    items: List[WorkRecord]
    next_cursor: Optional[str] = None
    total_estimate: Optional[int] = None
    source: str
    fetched_at: str = Field(default_factory=now_iso)


class SourceStatus(BaseModel):
    source: str
    status: str  # "ok" | "degraded" | "error" | "timeout"
    latency_ms: int
    items_count: int
    error_message: Optional[str] = None


class FederatedSearchResponse(BaseModel):
    items: List[WorkRecord]
    source_status: List[SourceStatus]
    total_results: int
