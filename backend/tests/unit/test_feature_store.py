"""
Unit Tests for Feature Store (Offline Parquet AS-OF Join & Online Sub-5ms Store)
"""

import asyncio
from datetime import datetime, timezone
import polars as pl
import pytest
from backend.app.feature_store.definitions import (
    Entity,
    Feature,
    FeatureDataType,
    FeatureView,
)
from backend.app.feature_store.offline_store import OfflineFeatureStore
from backend.app.feature_store.online_store import OnlineFeatureStore
from backend.app.feature_store.registry import FeatureRegistry


def test_feature_registry_lifecycle():
    registry = FeatureRegistry()
    entity = Entity(name="user", join_key="user_id", description="Customer entity")
    registry.register_entity(entity)

    assert registry.get_entity("user").join_key == "user_id"
    assert len(registry.list_entities()) == 1

    view = FeatureView(
        name="user_stats_v1",
        entities=["user"],
        features=[
            Feature(name="avg_spend", dtype=FeatureDataType.FLOAT64),
            Feature(name="tx_count", dtype=FeatureDataType.INT64),
        ],
        source_table="user_transactions",
        timestamp_field="event_timestamp",
    )
    registry.register_feature_view(view)
    assert registry.get_feature_view("user_stats_v1").name == "user_stats_v1"


def test_offline_store_asof_join(test_temp_dir):
    store = OfflineFeatureStore(storage_dir=test_temp_dir)
    view = FeatureView(
        name="user_features",
        entities=["user"],
        features=[Feature(name="score", dtype=FeatureDataType.FLOAT64)],
        source_table="raw_features",
        timestamp_field="event_timestamp",
    )

    t0 = datetime(2026, 8, 30, 1, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 8, 30, 2, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 8, 30, 3, 0, 0, tzinfo=timezone.utc)

    feature_df = pl.DataFrame({
        "user_id": ["u1", "u1"],
        "event_timestamp": [t0, t2],
        "score": [10.5, 20.0],
    })
    store.write_features(view, feature_df)

    # Observation entity at t1 (should backward join to t0 value 10.5, not t2 future value)
    entity_df = pl.DataFrame({
        "user_id": ["u1"],
        "obs_timestamp": [t1],
    })

    joined = store.get_historical_features_asof(
        entity_df=entity_df,
        entity_key="user_id",
        timestamp_col="obs_timestamp",
        feature_view=view,
    )

    assert len(joined) == 1
    assert joined["score"][0] == 10.5


@pytest.mark.asyncio
async def test_online_store_write_and_read():
    online_store = OnlineFeatureStore()
    payload = {
        "user_101": {"score": 98.4, "tier": "gold"},
        "user_102": {"score": 45.2, "tier": "silver"},
    }

    written = await online_store.write_online_features(
        view_name="test_view",
        entity_key="user_id",
        features_dict=payload,
    )
    assert written == 2

    fetched = await online_store.get_online_features(
        view_name="test_view",
        entity_key="user_id",
        entity_ids=["user_101", "user_102", "user_999"],
    )

    assert fetched["user_101"]["score"] == 98.4
    assert fetched["user_102"]["tier"] == "silver"
    assert fetched["user_999"] is None
