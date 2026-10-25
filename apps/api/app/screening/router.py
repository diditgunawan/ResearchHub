from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.service import ProjectService
from app.screening.schemas import (
    ProtocolCreate,
    ProtocolResponse,
    ExclusionReasonResponse,
    DecisionCreate,
    DecisionResponse,
    ResolutionCreate,
    KappaResponse,
    PrismaResponse,
)
from app.screening.service import ScreeningService
from app.core.errors import ForbiddenError

router = APIRouter(prefix="/projects/{project_id}", tags=["screening"])


@router.get("/protocols", response_model=Optional[ProtocolResponse])
async def get_protocol(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.get_active_protocol(db, project_id)


@router.post("/protocols", response_model=ProtocolResponse)
async def create_protocol(
    project_id: str,
    payload: ProtocolCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, role = await ProjectService.get_project_with_role(db, project_id, current_user.id)
    if role not in ["owner", "reviewer"]:
        raise ForbiddenError("Only project owners and reviewers can define review protocols", code="INSUFFICIENT_ROLE")

    return await ScreeningService.create_or_update_protocol(
        db,
        project_id,
        payload.question,
        payload.pico,
        payload.inclusion_criteria,
        payload.exclusion_criteria,
    )


@router.get("/exclusion-reasons", response_model=List[ExclusionReasonResponse])
async def list_exclusion_reasons(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.get_exclusion_reasons(db, project_id)


@router.get("/screening/queue")
async def get_queue(
    project_id: str,
    stage: str = Query("title_abstract", pattern="^(title_abstract|full_text)$"),
    limit: int = Query(25, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.get_screening_queue(
        db, project_id, current_user.id, stage=stage, limit=limit
    )


@router.post("/screening/decisions", response_model=DecisionResponse)
async def submit_decision(
    project_id: str,
    payload: DecisionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    decision = await ScreeningService.submit_decision(
        db,
        project_id,
        current_user.id,
        payload.work_id,
        payload.stage,
        payload.verdict,
        payload.reason_code,
        payload.notes,
    )
    return decision


@router.get("/screening/conflicts")
async def get_conflicts(
    project_id: str,
    stage: str = Query("title_abstract", pattern="^(title_abstract|full_text)$"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.get_conflicts(db, project_id, stage=stage)


@router.post("/screening/resolutions")
async def resolve_conflict(
    project_id: str,
    payload: ResolutionCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _, role = await ProjectService.get_project_with_role(db, project_id, current_user.id)
    if role != "owner":
        raise ForbiddenError("Only project owners can execute third-party conflict resolutions", code="OWNER_ROLE_REQUIRED")

    resolution = await ScreeningService.resolve_conflict(
        db,
        project_id,
        current_user.id,
        payload.work_id,
        payload.stage,
        payload.final_verdict,
        payload.reason_code,
        payload.rationale,
    )
    return {
        "id": resolution.id,
        "work_id": resolution.work_id,
        "stage": resolution.stage,
        "final_verdict": resolution.final_verdict,
        "resolved_by": resolution.resolved_by,
        "created_at": resolution.created_at,
    }


@router.get("/screening/agreement", response_model=KappaResponse)
async def get_agreement(
    project_id: str,
    stage: str = Query("title_abstract", pattern="^(title_abstract|full_text)$"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.compute_cohen_kappa(db, project_id, stage=stage)


@router.get("/prisma", response_model=PrismaResponse)
async def get_prisma_flow(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await ScreeningService.compute_prisma_flow(db, project_id)
