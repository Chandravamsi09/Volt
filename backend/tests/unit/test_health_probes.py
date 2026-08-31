"""
Unit tests for Health & Readiness Probes
"""
import pytest
from datetime import datetime, timezone
from backend.app.schemas.common import HealthStatus, ReadinessStatus, StandardResponse

def test_health_status_schema():
    health = HealthStatus(
        status="healthy",
        version="1.0.0",
        environment="production",
        database="connected",
        redis="connected",
        timestamp=datetime.now(timezone.utc),
    )
    assert health.status == "healthy"
    assert health.database == "connected"

def test_readiness_status_schema():
    readiness = ReadinessStatus(
        ready=True,
        database_status="ready",
        redis_status="ready",
        lakehouse_accessible=True,
        active_memory_mb=128.5,
        timestamp=datetime.now(timezone.utc),
    )
    assert readiness.ready is True
    assert readiness.lakehouse_accessible is True
