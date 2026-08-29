"""
User, Authentication & API Key Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from backend.app.schemas.common import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: str = Field(default="ml_engineer", pattern="^(admin|ml_engineer|data_analyst|viewer)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class TokenPayload(BaseSchema):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseSchema):
    username_or_email: str
    password: str


class APIKeyCreate(BaseSchema):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class APIKeyRead(BaseSchema):
    id: str
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    description: Optional[str] = None


class APIKeyCreatedResponse(APIKeyRead):
    raw_api_key: str
