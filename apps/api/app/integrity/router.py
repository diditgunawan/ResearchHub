from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.service import ProjectService
from app.integrity.service import IntegrityService

router = APIRouter(prefix="/projects/{project_id}", tags=["integrity"])


@router.get("/reference-checks")
async def list_reference_checks(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await IntegrityService.get_reference_checks(db, project_id)


@router.post("/reference-checks")
async def run_reference_audit(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await IntegrityService.run_reference_audit(db, project_id)


@router.get("/ai-disclosure")
async def get_ai_disclosure(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return await IntegrityService.generate_disclosure_statement(db, project_id)
