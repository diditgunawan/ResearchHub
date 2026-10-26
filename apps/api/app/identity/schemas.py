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
    created_at: datetime


class SessionResponse(BaseModel):
    user: UserResponse
    session_token: str
