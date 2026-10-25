from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Tuple
from app.identity.models import User
from app.core.security import create_magic_link_token, verify_magic_link_token, create_session_token
from app.core.errors import UnauthorizedError, BadRequestError


class IdentityService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def request_magic_link(db: AsyncSession, email: str) -> str:
        """Create or locate user, then issue a 15-minute magic link token."""
        clean_email = email.strip().lower()
        user = await IdentityService.get_user_by_email(db, clean_email)
        if not user:
            user = User(email=clean_email)
            db.add(user)
            await db.flush()
        
        token = create_magic_link_token(clean_email)
        return token

    @staticmethod
    async def verify_magic_link_and_login(db: AsyncSession, token: str) -> Tuple[User, str]:
        """Verify token and issue session token."""
        email = verify_magic_link_token(token)
        if not email:
            raise UnauthorizedError("Invalid or expired magic link token", code="INVALID_MAGIC_LINK")

        user = await IdentityService.get_user_by_email(db, email)
        if not user:
            raise UnauthorizedError("User record not found", code="USER_NOT_FOUND")

        session_token = create_session_token(user.id)
        return user, session_token
