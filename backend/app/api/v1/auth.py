"""
Authentication, User Management & API Key Endpoints
"""

from datetime import timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.exceptions import UnauthorizedError
from backend.app.core.security import (
    create_access_token,
    generate_api_key,
    get_password_hash,
    verify_password,
)
from backend.app.models.user import APIKey, User
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.user import (
    APIKeyCreate,
    APIKeyCreatedResponse,
    APIKeyRead,
    LoginRequest,
    Token,
    UserCreate,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=StandardResponse[UserRead])
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new platform user."""
    res = await db.execute(select(User).where(User.email == user_in.email))
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return StandardResponse(data=UserRead.model_validate(user), message="User registered successfully")


@router.post("/login", response_model=StandardResponse[Token])
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and obtain JWT access token."""
    res = await db.execute(
        select(User).where(
            (User.username == login_data.username_or_email)
            | (User.email == login_data.username_or_email)
        )
    )
    user = res.scalars().first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    token_obj = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserRead.model_validate(user),
    )
    return StandardResponse(data=token_obj, message="Authentication successful")


@router.post("/keys", response_model=StandardResponse[APIKeyCreatedResponse])
async def create_new_api_key(
    key_in: APIKeyCreate,
    user_id: str = "default-admin-user",  # Simplified dependency
    db: AsyncSession = Depends(get_db),
):
    """Generate a new secure API Key."""
    raw_key, hashed = generate_api_key(prefix="volt_")
    prefix = raw_key[:12]

    api_key_record = APIKey(
        name=key_in.name,
        key_prefix=prefix,
        hashed_key=hashed,
        user_id=user_id,
        description=key_in.description,
        is_active=True,
    )
    db.add(api_key_record)
    await db.commit()
    await db.refresh(api_key_record)

    created_dto = APIKeyCreatedResponse(
        id=api_key_record.id,
        name=api_key_record.name,
        key_prefix=api_key_record.key_prefix,
        is_active=api_key_record.is_active,
        created_at=api_key_record.created_at,
        description=api_key_record.description,
        raw_api_key=raw_key,
    )
    return StandardResponse(data=created_dto, message="API Key created. Store raw key securely.")
