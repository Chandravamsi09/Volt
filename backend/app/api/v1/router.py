"""
Central API v1 Router Aggregator
"""

from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.drift import router as drift_router
from backend.app.api.v1.features import router as features_router
from backend.app.api.v1.inference import router as inference_router
from backend.app.api.v1.llm import router as llm_router
from backend.app.api.v1.models import router as models_router
from backend.app.api.v1.pipelines import router as pipelines_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(pipelines_router)
api_router.include_router(features_router)
api_router.include_router(models_router)
api_router.include_router(inference_router)
api_router.include_router(llm_router)
api_router.include_router(drift_router)
