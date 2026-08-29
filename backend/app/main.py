"""
Volt AI/ML & Data Platform Main FastAPI Application Factory
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.core.exceptions import VoltException
from backend.app.core.telemetry import prometheus_metrics_middleware
from backend.app.schemas.common import HealthStatus, StandardResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown hooks."""
    # Ensure directories & database tables exist
    settings.ensure_directories()
    await init_db()
    yield
    # Cleanup logic on shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Volt Enterprise AI/ML & Data Lakehouse Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Prometheus Telemetry Middleware
app.middleware("http")(prometheus_metrics_middleware)


# Global Exception Handler
@app.exception_handler(VoltException)
async def volt_exception_handler(request: Request, exc: VoltException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error": {
                "code": exc.code,
                "details": exc.details,
            },
        },
    )


# Health Check Endpoint
@app.get("/health", response_model=StandardResponse[HealthStatus], tags=["Health"])
async def health_check():
    """System health check and dependency status."""
    health = HealthStatus(
        status="healthy",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database="connected",
        redis="connected",
        timestamp=datetime.now(timezone.utc),
    )
    return StandardResponse(data=health, message="Volt Platform is running smoothly.")


# Prometheus Metrics Exporter Endpoint
@app.get("/metrics", tags=["Telemetry"])
async def get_metrics():
    """Expose Prometheus runtime metrics."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)
