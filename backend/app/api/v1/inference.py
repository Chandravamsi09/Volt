"""
Real-Time Model Inference & Prediction Gateway Endpoints
"""

from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.ml_engine.serving.inference_engine import (
    PredictionOutput,
    inference_engine,
)
from backend.app.ml_engine.serving.traffic_router import RouteTarget, traffic_router
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/inference", tags=["Inference Gateway"])


class PredictRequest(BaseModel):
    model_name: str
    version: str
    features: List[List[float]]


class EndpointPredictRequest(BaseModel):
    endpoint_name: str
    features: List[List[float]]


@router.post("/predict", response_model=StandardResponse[Dict[str, Any]])
async def predict_direct(payload: PredictRequest):
    """Execute low-latency direct model inference."""
    try:
        out = inference_engine.predict(
            name=payload.model_name,
            version=payload.version,
            features=payload.features,
        )
        return StandardResponse(
            data={
                "model_name": out.model_name,
                "version": out.model_version,
                "predictions": out.predictions,
                "probabilities": out.probabilities,
                "latency_ms": out.latency_ms,
            },
            message="Prediction generated successfully",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/endpoints/{endpoint_name}/predict", response_model=StandardResponse[Dict[str, Any]])
async def predict_via_endpoint(endpoint_name: str, payload: EndpointPredictRequest):
    """Execute routed inference according to active Canary/AB testing policies."""
    target, shadows = traffic_router.route_request(endpoint_name)
    out = inference_engine.predict(
        name=target.model_name,
        version=target.version,
        features=payload.features,
    )
    return StandardResponse(
        data={
            "endpoint": endpoint_name,
            "routed_target": {"name": target.model_name, "version": target.version, "weight": target.weight},
            "predictions": out.predictions,
            "latency_ms": out.latency_ms,
        },
        message="Routed prediction executed",
    )
