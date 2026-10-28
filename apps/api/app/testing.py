import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from app.identity.models import User, AuthMagicLink
from app.identity.service import IdentityService
from app.core.security import create_session_token


async def issue_link(db, email: str) -> str:
    """Helper for testing and truth audit probes to obtain a fresh single-use magic link token."""
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
    await db.commit()
    return raw_token


async def bootstrap_owner(db, email: str) -> User:
    """Helper for testing to explicitly bootstrap an owner with system_admin rights."""
    clean_email = email.strip().lower()
    user = await IdentityService.get_user_by_email(db, clean_email)
    if not user:
        user = User(email=clean_email, is_system_admin=True)
        db.add(user)
    else:
        user.is_system_admin = True
    await db.commit()
    return user


async def make_session(db, email: str) -> str:
    """Helper for testing and truth audit probes to obtain a valid session token directly."""
    clean_email = email.strip().lower()
    user = await IdentityService.get_user_by_email(db, clean_email)
    if not user:
        user = User(email=clean_email)
        db.add(user)
        await db.flush()
    _, session_token = await IdentityService.create_server_session(db, user.id)
    await db.commit()
    return session_token
