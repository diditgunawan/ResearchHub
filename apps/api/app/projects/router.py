from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.identity.router import get_current_user
from app.identity.schemas import UserResponse
from app.projects.schemas import ProjectCreate, ProjectResponse, MemberAdd, MemberResponse
from app.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
async def create_project(
    payload: ProjectCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await ProjectService.create_project(
        db, current_user.id, payload.name, payload.description
    )
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        role="owner",
        created_at=project.created_at,
    )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await ProjectService.get_user_projects(db, current_user.id)
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            owner_id=p.owner_id,
            role=role,
            created_at=p.created_at,
        )
        for p, role in rows
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project, role = await ProjectService.get_project_with_role(db, project_id, current_user.id)
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        role=role,
        created_at=project.created_at,
    )


@router.post("/{project_id}/members", response_model=MemberResponse)
async def add_member(
    project_id: str,
    payload: MemberAdd,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await ProjectService.add_member(
        db, project_id, current_user.id, payload.email, payload.role
    )
    members = await ProjectService.get_members(db, project_id, current_user.id)
    target = next(m for m in members if m["user_id"] == member.user_id)
    return MemberResponse(**target)


@router.get("/{project_id}/members", response_model=List[MemberResponse])
async def list_members(
    project_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    members = await ProjectService.get_members(db, project_id, current_user.id)
    return [MemberResponse(**m) for m in members]
