from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.service import ProjectService
from app.synthesis.models import SynthesisRun, Extraction
from app.works.models import Work
from app.synthesis.schemas import SynthesisRequest, SynthesisResponse, ExtractionResponse, AtomicClaim
from app.synthesis.service import SynthesisService
from app.core.errors import NotFoundError

router = APIRouter(prefix="/projects/{project_id}", tags=["synthesis"])


@router.post("/synthesis", response_model=SynthesisResponse)
async def run_synthesis(
    project_id: str,
    payload: SynthesisRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await SynthesisService.synthesize(
        db,
        project_id,
        payload.query,
        scope=payload.scope,
        max_works=payload.max_works,
    )


@router.get("/synthesis/{run_id}", response_model=SynthesisResponse)
async def get_synthesis_run(
    project_id: str,
    run_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    stmt = select(SynthesisRun).where(
        SynthesisRun.id == run_id,
        SynthesisRun.project_id == project_id,
    )
    run = (await db.execute(stmt)).scalar_one_or_none()
    if not run:
        raise NotFoundError(f"Synthesis run '{run_id}' not found", code="SYNTHESIS_NOT_FOUND")

    claims = [AtomicClaim(**c) for c in (run.claims_json or [])]
    return SynthesisResponse(
        id=run.id,
        query=run.query,
        status=run.status,
        claims=claims,
        refusal_reason=run.refusal_reason,
        retrieved_works=[],
        verified_percentage=100.0 if run.status == "completed" else 0.0,
        model=run.model,
        created_at=run.created_at,
    )


@router.get("/extractions", response_model=List[ExtractionResponse])
async def list_extractions(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    stmt = (
        select(Extraction, Work.title)
        .join(Work, Extraction.work_id == Work.id)
        .where(Extraction.project_id == project_id)
        .order_by(Extraction.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        ExtractionResponse(
            id=ext.id,
            work_id=ext.work_id,
            title=title,
            population=ext.population,
            method=ext.method,
            finding=ext.finding,
            limitations=ext.limitations,
            edited_by_user=ext.edited_by_user,
            created_at=ext.created_at,
        )
        for ext, title in rows
    ]
