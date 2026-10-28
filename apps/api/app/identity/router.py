import os
import secrets
from fastapi import APIRouter, Depends, Header, Response, Cookie, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.errors import UnauthorizedError, ForbiddenError
from app.core.config import settings
from app.identity.schemas import (
    MagicLinkRequest,
    MagicLinkResponse,
    SessionVerifyRequest,
    SessionResponse,
    UserResponse,
    PasskeyRegisterChallengeResponse,
    PasskeyRegisterVerifyRequest,
    PasskeyLoginChallengeResponse,
    PasskeyLoginVerifyRequest,
    InstanceSettingsResponse,
    InstanceSettingsUpdateRequest,
)
from app.identity.service import IdentityService

router = APIRouter(prefix="", tags=["identity"])


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session_cookie: Optional[str] = Cookie(None, alias="rf_session"),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Authentication dependency checking Authorization header or secure session cookie with server session validation."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif session_cookie:
        token = session_cookie

    if not token:
        raise UnauthorizedError("Authentication credentials missing", code="AUTH_REQUIRED")

    user = await IdentityService.verify_server_session(db, token)
    if not user:
        raise UnauthorizedError("Invalid or expired session token", code="SESSION_EXPIRED")

    return UserResponse.model_validate(user)


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Dependency verifying the caller possesses system_admin authority (ADR-009)."""
    if not current_user.is_system_admin:
        raise ForbiddenError("System administrator privileges required", code="ADMIN_REQUIRED")
    return current_user


@router.post("/auth/magic-link", response_model=MagicLinkResponse, response_model_exclude_none=True)
async def request_magic_link(
    payload: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
):
    token = await IdentityService.request_magic_link(db, payload.email)
    # Strictly zero secrets returned over HTTP (P1 & P9 compliance).
    # In local development, print to console loopback for convenience.
    if settings.APP_ENV in ["local", "test"]:
        print(f"[AUTH DEV LOG] Single-use token for {payload.email}: {token}")

    return MagicLinkResponse(
        message="Magic login link generated. Please check your inbox.",
        token=None,
    )


@router.post("/auth/session", response_model=SessionResponse)
async def verify_session(
    payload: SessionVerifyRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    user, session_token = await IdentityService.verify_magic_link_and_login(db, payload.token, ip=ip, user_agent=ua)

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


@router.post("/auth/logout")
async def logout(
    authorization: Optional[str] = Header(None),
    session_cookie: Optional[str] = Cookie(None, alias="rf_session"),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    """Revoke active server-side session."""
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif session_cookie:
        token = session_cookie

    if token:
        await IdentityService.revoke_session(db, token)

    if response:
        response.delete_cookie(key="rf_session")

    return {"message": "Session successfully revoked"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


# ===== WebAuthn / Passkeys Endpoints (ADR-009 / Blueprint 17) =====

@router.post("/auth/passkey/register-challenge", response_model=PasskeyRegisterChallengeResponse)
async def passkey_register_challenge(
    current_user: UserResponse = Depends(get_current_user),
):
    """Generate WebAuthn registration challenge for navigator.credentials.create()."""
    challenge = secrets.token_urlsafe(32)
    return PasskeyRegisterChallengeResponse(
        challenge=challenge,
        rp={"name": settings.WEBAUTHN_RP_NAME, "id": settings.WEBAUTHN_RP_ID},
        user={"id": current_user.id, "name": current_user.email, "displayName": current_user.full_name or current_user.email},
        pubKeyCredParams=[{"alg": -7, "type": "public-key"}, {"alg": -257, "type": "public-key"}],
    )


@router.post("/auth/passkey/register-verify")
async def passkey_register_verify(
    payload: PasskeyRegisterVerifyRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enroll verified Passkey credential for the current user."""
    cred = await IdentityService.register_passkey(
        db,
        user_id=current_user.id,
        credential_id=payload.credential_id,
        public_key=payload.public_key,
        label=payload.label,
    )
    return {"message": "Passkey successfully enrolled", "credential_id": cred.credential_id}


@router.post("/auth/passkey/login-challenge", response_model=PasskeyLoginChallengeResponse)
async def passkey_login_challenge():
    """Generate WebAuthn assertion challenge for navigator.credentials.get()."""
    challenge = secrets.token_urlsafe(32)
    return PasskeyLoginChallengeResponse(
        challenge=challenge,
        rp_id=settings.WEBAUTHN_RP_ID,
    )


@router.post("/auth/passkey/login-verify", response_model=SessionResponse)
async def passkey_login_verify(
    payload: PasskeyLoginVerifyRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate via enrolled Passkey credential."""
    if not payload.signature:
        raise UnauthorizedError("Passkey login requires a verified signature", code="SIGNATURE_REQUIRED")

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    user, session_token = await IdentityService.login_with_passkey(
        db, credential_id=payload.credential_id, signature=payload.signature, ip=ip, user_agent=ua
    )

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


# ===== Admin Console Endpoints (Single-Owner / Multi-User - Blueprint 17) =====

@router.get("/admin/settings", response_model=InstanceSettingsResponse)
async def get_instance_settings(
    admin_user: UserResponse = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    inst = await IdentityService.get_instance_settings(db)
    val = inst.value or {}
    return InstanceSettingsResponse(
        access_mode=val.get("access_mode", settings.ACCESS_MODE),
        registration=val.get("registration", settings.REGISTRATION_POLICY),
        owner_email=admin_user.email,
    )


@router.post("/admin/settings", response_model=InstanceSettingsResponse)
async def update_instance_settings(
    payload: InstanceSettingsUpdateRequest,
    admin_user: UserResponse = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    updates = {}
    if payload.access_mode is not None:
        updates["access_mode"] = payload.access_mode
    if payload.registration is not None:
        updates["registration"] = payload.registration

    inst = await IdentityService.update_instance_settings(db, updates)
    val = inst.value or {}
    return InstanceSettingsResponse(
        access_mode=val.get("access_mode", settings.ACCESS_MODE),
        registration=val.get("registration", settings.REGISTRATION_POLICY),
        owner_email=admin_user.email,
    )
