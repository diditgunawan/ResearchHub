from fastapi import APIRouter, Depends, Header, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_session_token
from app.core.errors import UnauthorizedError
from app.core.config import settings
from app.identity.schemas import MagicLinkRequest, MagicLinkResponse, SessionVerifyRequest, SessionResponse, UserResponse
from app.identity.service import IdentityService

router = APIRouter(prefix="", tags=["identity"])


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session_cookie: Optional[str] = Cookie(None, alias="rf_session"),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Authentication dependency checking Authorization header or secure session cookie."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif session_cookie:
        token = session_cookie

    if not token:
        raise UnauthorizedError("Authentication credentials missing", code="AUTH_REQUIRED")

    user_id = verify_session_token(token)
    if not user_id:
        raise UnauthorizedError("Invalid or expired session token", code="SESSION_EXPIRED")

    user = await IdentityService.get_user_by_id(db, user_id)
    if not user:
        raise UnauthorizedError("User does not exist", code="USER_NOT_FOUND")

    return UserResponse.model_validate(user)


@router.post("/auth/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(
    payload: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    token = await IdentityService.request_magic_link(db, payload.email)
    # In local/test environments we return token directly; in prod it's emailed
    ret_token = token if settings.APP_ENV in ["local", "test"] else None
    return MagicLinkResponse(
        message="Magic login link generated. Please check your inbox.",
        token=ret_token,
    )


@router.post("/auth/session", response_model=SessionResponse)
async def verify_session(
    payload: SessionVerifyRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user, session_token = await IdentityService.verify_magic_link_and_login(db, payload.token)
    
    # Set HttpOnly session cookie per ENG-007
    response.set_cookie(
        key="rf_session",
        value=session_token,
        httponly=True,
        secure=settings.APP_ENV not in ["local", "test"],
        samesite="lax",
        max_age=86400 * 7,
    )

    return SessionResponse(
        user=UserResponse.model_validate(user),
        session_token=session_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
