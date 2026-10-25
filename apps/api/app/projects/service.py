from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Tuple, Optional
from app.projects.models import Project, ProjectMember
from app.identity.models import User
from app.identity.service import IdentityService
from app.core.errors import NotFoundError, ForbiddenError, ConflictError


class ProjectService:
    @staticmethod
    async def create_project(
        db: AsyncSession,
        user_id: str,
        name: str,
        description: Optional[str] = None
    ) -> Project:
        """Create a new project and assign creator as 'owner'."""
        project = Project(name=name, description=description, owner_id=user_id)
        db.add(project)
        await db.flush()

        member = ProjectMember(project_id=project.id, user_id=user_id, role="owner")
        db.add(member)
        await db.flush()

        return project

    @staticmethod
    async def get_user_projects(db: AsyncSession, user_id: str) -> List[Tuple[Project, str]]:
        """List all projects the user is a member of with their active role."""
        stmt = (
            select(Project, ProjectMember.role)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.all()

    @staticmethod
    async def get_project_with_role(
        db: AsyncSession,
        project_id: str,
        user_id: str
    ) -> Tuple[Project, str]:
        """Fetch project and verify user membership, returning (project, role)."""
        stmt = (
            select(Project, ProjectMember.role)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .where(Project.id == project_id, ProjectMember.user_id == user_id)
        )
        result = await db.execute(stmt)
        row = result.first()
        if not row:
            raise NotFoundError(f"Project '{project_id}' not found or access denied", code="PROJECT_NOT_FOUND")
        return row[0], row[1]

    @staticmethod
    async def add_member(
        db: AsyncSession,
        project_id: str,
        inviter_user_id: str,
        invitee_email: str,
        role: str
    ) -> ProjectMember:
        """Add a member to project. Only project 'owner' can add members."""
        _, inviter_role = await ProjectService.get_project_with_role(db, project_id, inviter_user_id)
        if inviter_role != "owner":
            raise ForbiddenError("Only project owners can manage members", code="INSUFFICIENT_PROJECT_ROLE")

        # Resolve or invite user
        clean_email = invitee_email.strip().lower()
        user = await IdentityService.get_user_by_email(db, clean_email)
        if not user:
            user = User(email=clean_email)
            db.add(user)
            await db.flush()

        # Check existing membership
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing:
            raise ConflictError("User is already a project member", code="MEMBER_ALREADY_EXISTS")

        member = ProjectMember(project_id=project_id, user_id=user.id, role=role)
        db.add(member)
        await db.flush()
        return member

    @staticmethod
    async def get_members(db: AsyncSession, project_id: str, user_id: str) -> List[dict]:
        """List all members of a project."""
        await ProjectService.get_project_with_role(db, project_id, user_id)
        stmt = (
            select(User.id, User.email, User.full_name, ProjectMember.role, ProjectMember.created_at)
            .join(ProjectMember, User.id == ProjectMember.user_id)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.created_at.asc())
        )
        result = await db.execute(stmt)
        return [
            {
                "user_id": r[0],
                "email": r[1],
                "full_name": r[2],
                "role": r[3],
                "created_at": r[4],
            }
            for r in result.all()
        ]
