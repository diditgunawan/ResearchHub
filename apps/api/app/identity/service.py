import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Tuple
from app.identity.models import User, AuthMagicLink
from app.core.security import create_session_token
from app.core.errors import UnauthorizedError, BadRequestError


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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
        """Create or locate user, then issue a 15-minute single-use magic link token."""
        clean_email = email.strip().lower()
        user = await IdentityService.get_user_by_email(db, clean_email)
        if not user:
            user = User(email=clean_email)
            db.add(user)
            await db.flush()

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        magic_link = AuthMagicLink(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires,
        )
        db.add(magic_link)
        await db.flush()
        return raw_token

    @staticmethod
    async def verify_magic_link_and_login(db: AsyncSession, token: str) -> Tuple[User, str]:
        """Verify token, enforce single-use, and issue session token."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        stmt = select(AuthMagicLink).where(AuthMagicLink.token_hash == token_hash)
        result = await db.execute(stmt)
        magic_link = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if not magic_link:
            raise UnauthorizedError("Invalid or expired magic link token", code="INVALID_MAGIC_LINK")
        if magic_link.used_at is not None:
            raise UnauthorizedError("Magic link token has already been used", code="TOKEN_ALREADY_USED")
        if _to_utc(magic_link.expires_at) < now:
            raise UnauthorizedError("Magic link token has expired", code="TOKEN_EXPIRED")

        magic_link.used_at = now
        await db.flush()

        user = await IdentityService.get_user_by_id(db, magic_link.user_id)
        if not user:
            raise UnauthorizedError("User record not found", code="USER_NOT_FOUND")

        session_token = create_session_token(user.id)
        return user, session_token
