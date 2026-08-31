"""
Model Registry, Artifact Vault & Lifecycle API Endpoints
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.ml_engine.registry.model_vault import ModelMetadata, ModelVault
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/models", tags=["Model Registry & MLOps"])


class StageTransitionRequest(BaseModel):
    new_stage: str  # STAGING, PRODUCTION, ARCHIVED


@router.get("/{name}/versions", response_model=StandardResponse[List[Dict[str, Any]]])
async def list_model_versions(name: str):
    """List all registered versions and metadata for a given model."""
    vault = ModelVault()
    versions = vault.list_versions(name)
    return StandardResponse(data=[v.__dict__ for v in versions])


@router.get("/{name}/{version}", response_model=StandardResponse[Dict[str, Any]])
async def get_model_version(name: str, version: str):
    """Retrieve metadata and metrics for a specific model version."""
    vault = ModelVault()
    meta = vault.get_model(name, version)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Model '{name}:{version}' not found.")
    return StandardResponse(data=meta.__dict__)


@router.post("/{name}/{version}/transition", response_model=StandardResponse[Dict[str, Any]])
async def transition_model_stage(name: str, version: str, payload: StageTransitionRequest):
    """Promote or demote model lifecycle stage (e.g. promote to PRODUCTION)."""
    vault = ModelVault()
    updated = vault.transition_stage(name, version, payload.new_stage)
    return StandardResponse(
        data=updated.__dict__,
        message=f"Model '{name}:{version}' transitioned to stage '{payload.new_stage.upper()}'",
    )

@router.get("/{name}/{version}/lineage", response_model=StandardResponse[Dict[str, Any]])
async def get_model_lineage(name: str, version: str):
    """Export cryptographic lineage, dataset provenance, and parameter audit graph."""
    vault = ModelVault()
    lineage = vault.get_model_lineage(name, version)
    return StandardResponse(data=lineage, message=f"Model lineage graph for {name}:{version} generated.")
