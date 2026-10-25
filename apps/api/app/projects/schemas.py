from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    role: str
    created_at: datetime


class MemberAdd(BaseModel):
    email: EmailStr
    role: str = Field("reviewer", pattern="^(owner|reviewer|viewer)$")


class MemberResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime
