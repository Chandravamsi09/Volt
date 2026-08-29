"""
Base SQLAlchemy Declarative Model Mixins
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from backend.app.core.database import Base


def utc_now() -> datetime:
    """Current UTC timestamp generator."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Provides created_at and updated_at timestamps."""

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class UUIDPrimaryKeyMixin:
    """Provides a UUID string primary key."""

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
