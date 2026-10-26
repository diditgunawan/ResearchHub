from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str
    token: Optional[str] = None


class SessionVerifyRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    full_name: Optional[str] = None
    is_system_admin: bool = False
    status: str = "active"
    created_at: datetime


class SessionResponse(BaseModel):
    user: UserResponse
    session_token: str


class PasskeyRegisterChallengeResponse(BaseModel):
    challenge: str
    rp: dict
    user: dict
    pubKeyCredParams: list


class PasskeyRegisterVerifyRequest(BaseModel):
    credential_id: str
    public_key: str
    label: Optional[str] = "Primary Passkey"


class PasskeyLoginChallengeResponse(BaseModel):
    challenge: str
    rp_id: str


class PasskeyLoginVerifyRequest(BaseModel):
    credential_id: str
    signature: Optional[str] = None


class InstanceSettingsResponse(BaseModel):
    access_mode: str
    registration: str
    owner_email: Optional[str] = None


class InstanceSettingsUpdateRequest(BaseModel):
    access_mode: Optional[str] = None
    registration: Optional[str] = None
