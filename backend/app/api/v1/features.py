"""
Feature Store API Endpoints (Entities, Feature Views & Online Retrieval)
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.feature_store.definitions import (
    Entity,
    Feature,
    FeatureDataType,
    FeatureView,
)
from backend.app.feature_store.materializer import FeatureMaterializer
from backend.app.feature_store.online_store import OnlineFeatureStore
from backend.app.feature_store.registry import feature_registry
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/features", tags=["Feature Store"])



class OnlineBatchWriteRequest(BaseModel):
    view_name: str
    entity_key: str
    features_dict: Dict[str, Dict[str, Any]]
    ttl_seconds: Optional[int] = None


class OnlineDeleteRequest(BaseModel):
    view_name: str
    entity_key: str
    entity_ids: List[str]

class OnlineFetchRequest(BaseModel):
    view_name: str
    entity_key: str
    entity_ids: List[str]


@router.post("/entities", response_model=StandardResponse[Entity])
async def register_entity(entity: Entity):
    """Register a new primary entity."""
    res = feature_registry.register_entity(entity)
    return StandardResponse(data=res, message=f"Entity '{entity.name}' registered")


@router.get("/entities", response_model=StandardResponse[List[Entity]])
async def list_entities():
    """List all registered entities."""
    return StandardResponse(data=feature_registry.list_entities())


@router.post("/views", response_model=StandardResponse[FeatureView])
async def register_feature_view(view: FeatureView):
    """Register a new feature view."""
    res = feature_registry.register_feature_view(view)
    return StandardResponse(data=res, message=f"FeatureView '{view.name}' registered")


@router.get("/views", response_model=StandardResponse[List[FeatureView]])
async def list_feature_views():
    """List all registered feature views."""
    return StandardResponse(data=feature_registry.list_feature_views())


@router.post("/online/get", response_model=StandardResponse[Dict[str, Optional[Dict[str, Any]]]])
async def get_online_features(payload: OnlineFetchRequest):
    """Fetch low-latency features for real-time inference (sub-5ms)."""
    online_store = OnlineFeatureStore()
    features = await online_store.get_online_features(
        view_name=payload.view_name,
        entity_key=payload.entity_key,
        entity_ids=payload.entity_ids,
    )
    return StandardResponse(data=features, message="Online features retrieved")


@router.post("/views/{view_name}/materialize", response_model=StandardResponse[Dict[str, Any]])
async def materialize_feature_view(view_name: str, entity_key: str):
    """Trigger on-demand sync from Parquet Lakehouse to Online Redis Store."""
    view = feature_registry.get_feature_view(view_name)
    materializer = FeatureMaterializer()
    res = await materializer.materialize_view(feature_view=view, entity_key=entity_key)
    return StandardResponse(data=res, message="Materialization executed")

@router.post("/online/batch-write", response_model=StandardResponse[Dict[str, int]])
async def batch_write_online_features(payload: OnlineBatchWriteRequest):
    """Bulk write features into online low-latency Redis feature cache."""
    online_store = OnlineFeatureStore()
    count = await online_store.write_online_features(
        view_name=payload.view_name,
        entity_key=payload.entity_key,
        features_dict=payload.features_dict,
        ttl_seconds=payload.ttl_seconds,
    )
    return StandardResponse(data={"written_records": count}, message=f"Successfully materialized {count} records into online store.")


@router.delete("/online/delete", response_model=StandardResponse[Dict[str, int]])
async def delete_online_features(payload: OnlineDeleteRequest):
    """Evict entities from online feature cache."""
    online_store = OnlineFeatureStore()
    deleted = await online_store.delete_online_features(
        view_name=payload.view_name,
        entity_key=payload.entity_key,
        entity_ids=payload.entity_ids,
    )
    return StandardResponse(data={"deleted_records": deleted}, message=f"Evicted {deleted} entities from online store.")
