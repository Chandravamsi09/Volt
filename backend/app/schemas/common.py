"""
Common Pydantic Schemas & Standard Envelopes
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base configuration schema."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class StandardResponse(BaseSchema, Generic[T]):
    """Unified API response wrapper."""
    success: bool = True
    message: str = "Operation completed successfully."
    data: Optional[T] = None
    error: Optional[dict] = None


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard pagination envelope."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthStatus(BaseSchema):
    """Platform health check schema."""
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str
    database: str = "connected"
    redis: str = "connected"
    timestamp: datetime


class ReadinessStatus(BaseSchema):
    """Platform subsystem readiness probe schema."""
    ready: bool = True
    database_status: str = "ready"
    redis_status: str = "ready"
    lakehouse_accessible: bool = True
    active_memory_mb: float = 0.0
    timestamp: datetime
