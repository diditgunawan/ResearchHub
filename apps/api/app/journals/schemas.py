from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class JournalResponse(BaseModel):
    id: str
    openalex_id: Optional[str]
    issn_l: Optional[str]
    issns: List[str] = []
    title: str
    publisher: Optional[str]
    country: Optional[str]
    scope_text: Optional[str]
    languages: List[str] = []
    is_oa: bool
    in_doaj: bool
    apc_usd: Optional[float]
    apc_note: Optional[str]
    scopus_quartile: Optional[str]
    sinta_rank: Optional[str]
    guidelines_url: Optional[str]
    data_as_of: date
    provenance: Dict[str, Any] = {}
    recent_articles: List[Dict[str, Any]] = []
    keywords: List[str] = []
    is_stale: bool = False  # Calculated: True if older than 12 months


class JournalMatchRequest(BaseModel):
    title: str = Field(..., max_length=1000)
    abstract: str = Field(..., max_length=6000)
    keywords: Optional[List[str]] = Field(default=None)
    quartiles: Optional[List[str]] = Field(default=None, description="Filter by Scopus quartile (e.g. ['Q1', 'Q2'])")
    sinta_ranks: Optional[List[str]] = Field(default=None, description="Filter by SINTA rank (e.g. ['S1', 'S2'])")
    require_oa: Optional[bool] = Field(default=None, description="Only Open Access journals")
    require_doaj: Optional[bool] = Field(default=None, description="Only DOAJ-indexed journals")
    max_apc_usd: Optional[float] = Field(default=None, description="Maximum APC cost in USD (0 for no APC)")
    languages: Optional[List[str]] = Field(default=None)


class MatchScoreBreakdown(BaseModel):
    semantic_score: float = Field(..., description="Weight 0.60: Abstract and scope semantic fit")
    keyword_score: float = Field(..., description="Weight 0.25: Topic and keyword alignment")
    citation_affinity: float = Field(..., description="Weight 0.15: Domain and reference citation affinity")
    composite_score: float


class JournalMatchRecommendation(BaseModel):
    journal: JournalResponse
    match_score: float
    score_breakdown: MatchScoreBreakdown
    similar_recent_articles: List[Dict[str, Any]]
    quality_signals: Dict[str, Any]  # DOAJ, Scopus quartile, SINTA rank, APC verified


class JournalMatchResponse(BaseModel):
    total_candidates_evaluated: int
    matched_count: int
    recommendations: List[JournalMatchRecommendation]
    disclaimer: str = (
        "Recommendations indicate topical fit based on title and abstract alignment with historical scope. "
        "ResearchForge does NOT guarantee acceptance probability, peer-review outcomes, or publication speed."
    )


class ChecklistItem(BaseModel):
    item: str
    requirement: str
    source_url: Optional[str]
    is_verifiable: bool
    status: str  # 'verified', 'verify_manually'


class SubmissionChecklistResponse(BaseModel):
    journal_id: str
    journal_title: str
    guidelines_url: Optional[str]
    items: List[ChecklistItem]
