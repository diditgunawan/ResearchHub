from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.journals.schemas import (
    JournalResponse, JournalMatchRequest, JournalMatchResponse, SubmissionChecklistResponse
)
from app.journals.service import JournalService

router = APIRouter(prefix="/journals", tags=["Journal Fit Matching"])


@router.get("", response_model=List[JournalResponse])
async def list_and_filter_journals(
    category: Optional[str] = Query(None, description="Disciplinary domain"),
    quartiles: Optional[List[str]] = Query(None, description="Scopus quartiles (Q1, Q2, Q3, Q4)"),
    sinta_ranks: Optional[List[str]] = Query(None, description="SINTA ranks (S1, S2, S3, S4, S5, S6)"),
    require_oa: Optional[bool] = Query(None, description="Filter for Open Access"),
    require_doaj: Optional[bool] = Query(None, description="Filter for DOAJ indexing"),
    max_apc_usd: Optional[float] = Query(None, description="Max APC limit in USD"),
    language: Optional[str] = Query(None, description="Language code (en, id)"),
    country: Optional[str] = Query(None, description="Country"),
    publisher: Optional[str] = Query(None, description="Publisher name"),
    query: Optional[str] = Query(None, description="Free text search"),
    db: AsyncSession = Depends(get_db),
):
    """JRN-001..JRN-004, JRN-011: Multi-parameter journal search with hard filters and provenance."""
    results = await JournalService.search_journals(
        db=db,
        category=category,
        quartiles=quartiles,
        sinta_ranks=sinta_ranks,
        require_oa=require_oa,
        require_doaj=require_doaj,
        max_apc_usd=max_apc_usd,
        language=language,
        country=country,
        publisher=publisher,
        query_text=query,
    )
    return [JournalResponse(**r) for r in results]


@router.post("/match", response_model=JournalMatchResponse)
async def match_manuscript(
    req: JournalMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    JRN-004..JRN-009: Match manuscript title and abstract against journals using 3-component scoring.
    Never guarantees acceptance; displays >= 3 similar recent articles with DOIs.
    """
    res = await JournalService.match_manuscript(
        db=db,
        title=req.title,
        abstract=req.abstract,
        keywords=req.keywords,
        quartiles=req.quartiles,
        sinta_ranks=req.sinta_ranks,
        require_oa=req.require_oa,
        require_doaj=req.require_doaj,
        max_apc_usd=req.max_apc_usd,
        languages=req.languages,
    )
    return JournalMatchResponse(**res)


@router.get("/{journal_id}/checklist", response_model=SubmissionChecklistResponse)
async def get_submission_checklist(
    journal_id: str,
    db: AsyncSession = Depends(get_db),
):
    """JRN-010: Return verified submission checklist citing authoritative author guidelines."""
    res = await JournalService.get_submission_checklist(db=db, journal_id=journal_id)
    return SubmissionChecklistResponse(**res)
