"""
Data & Model Drift Telemetry API Endpoints
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
import polars as pl
from pydantic import BaseModel
from backend.app.observability.drift.drift_monitor import drift_monitor
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/drift", tags=["Model Observability & Drift"])


class DriftCheckRequest(BaseModel):
    model_name: str
    model_version: str
    baseline_data: List[Dict[str, Any]]
    current_data: List[Dict[str, Any]]
    feature_columns: Optional[List[str]] = None


@router.post("/evaluate", response_model=StandardResponse[Dict[str, Any]])
async def evaluate_drift(payload: DriftCheckRequest):
    """Calculate PSI, KS-test, and dataset drift between baseline and current data."""
    baseline_df = pl.DataFrame(payload.baseline_data)
    current_df = pl.DataFrame(payload.current_data)

    report = drift_monitor.profile_and_compare(
        model_name=payload.model_name,
        model_version=payload.model_version,
        baseline_df=baseline_df,
        current_df=current_df,
        feature_columns=payload.feature_columns,
    )
    return StandardResponse(data=report.to_dict(), message="Drift evaluation completed")

class DriftAlertRequest(BaseModel):
    model_name: str
    drift_results: Dict[str, Any]
    webhook_url: Optional[str] = None


@router.post("/alerts/webhook", response_model=StandardResponse[Dict[str, Any]])
async def dispatch_drift_alert(payload: DriftAlertRequest):
    """Format and dispatch dataset drift alert notification payload."""
    monitor = DriftMonitor()
    alert_payload = monitor.build_drift_alert_payload(
        model_name=payload.model_name,
        drift_results=payload.drift_results,
        webhook_url=payload.webhook_url,
    )
    return StandardResponse(data=alert_payload, message="Drift alert payload prepared and dispatched.")
