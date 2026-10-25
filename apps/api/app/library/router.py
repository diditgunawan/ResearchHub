from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.service import ProjectService
from app.library.service import LibraryService

router = APIRouter(prefix="/projects/{project_id}", tags=["library"])


class AddToLibraryRequest(BaseModel):
    work_id: str
    user_notes: Optional[str] = None


class ImportRequest(BaseModel):
    format: str = Field(..., pattern="^(ris|bibtex|csv)$")
    content: str = Field(..., min_length=5)


@router.get("/library/items")
async def list_library_items(
    project_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify project membership (Owner/Reviewer/Viewer)
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    items, total = await LibraryService.list_items(db, project_id, limit=limit, offset=offset)
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/library/items")
async def add_item_to_library(
    project_id: str,
    payload: AddToLibraryRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    item = await LibraryService.add_to_library(
        db, project_id, payload.work_id, user_id=current_user.id, notes=payload.user_notes
    )
    return {
        "id": item.id,
        "project_id": item.project_id,
        "work_id": item.work_id,
        "user_notes": item.user_notes,
        "created_at": item.created_at,
    }


@router.post("/imports")
async def import_references(
    project_id: str,
    payload: ImportRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Reviewer or Owner can import
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    batch = await LibraryService.import_text(
        db, project_id, current_user.id, payload.format, payload.content
    )
    return {
        "batch_id": batch.id,
        "source": batch.source,
        "total_count": batch.total_count,
        "imported_count": batch.imported_count,
        "skipped_count": batch.skipped_count,
        "status": batch.status,
        "report": batch.report_json,
    }


@router.get("/exports")
async def export_references(
    project_id: str,
    format: str = Query("bibtex", pattern="^(bibtex|ris|csv)$"),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ProjectService.get_project_with_role(db, project_id, current_user.id)
    text = await LibraryService.export_library(db, project_id, format)
    
    media_types = {
        "bibtex": "application/x-bibtex",
        "ris": "application/x-research-info-systems",
        "csv": "text/csv",
    }
    return Response(
        content=text,
        media_type=media_types.get(format, "text/plain"),
        headers={"Content-Disposition": f'attachment; filename="library_{project_id[:8]}.{format}"'},
    )
