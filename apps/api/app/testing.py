import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from app.identity.models import User, AuthMagicLink
from app.identity.service import IdentityService
from app.core.security import create_session_token


async def issue_link(db, email: str) -> str:
    """Helper for testing and truth audit probes to obtain a fresh single-use magic link token."""
    token = await IdentityService.request_magic_link(db, email)
    await db.commit()
    return token


async def make_session(db, email: str) -> str:
    """Helper for testing and truth audit probes to obtain a valid session token directly."""
    clean_email = email.strip().lower()
    user = await IdentityService.get_user_by_email(db, clean_email)
    if not user:
        user = User(email=clean_email)
        db.add(user)
    await db.commit()
    return create_session_token(user.id)
