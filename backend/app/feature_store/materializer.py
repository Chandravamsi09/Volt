"""
Feature Store Offline-to-Online Materialization Pipeline
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import polars as pl
from backend.app.feature_store.definitions import FeatureView
from backend.app.feature_store.offline_store import OfflineFeatureStore
from backend.app.feature_store.online_store import OnlineFeatureStore

logger = logging.getLogger("volt.materializer")


class FeatureMaterializer:
    """Synchronizes latest feature values from Parquet Lakehouse to Redis Online Store."""

    def __init__(
        self,
        offline_store: Optional[OfflineFeatureStore] = None,
        online_store: Optional[OnlineFeatureStore] = None,
    ):
        self.offline_store = offline_store or OfflineFeatureStore()
        self.online_store = online_store or OnlineFeatureStore()

    async def materialize_view(
        self,
        feature_view: FeatureView,
        entity_key: str,
    ) -> Dict[str, Any]:
        """Materialize latest state of each entity into Redis."""
        start_time = datetime.now(timezone.utc)
        historical_df = self.offline_store.read_historical_features(feature_view.name)

        if historical_df.is_empty():
            logger.info(f"No records to materialize for feature view '{feature_view.name}'")
            return {
                "view_name": feature_view.name,
                "materialized_count": 0,
                "duration_seconds": 0.0,
                "timestamp": start_time.isoformat(),
            }

        # Deduplicate to retain latest record per entity
        latest_df = (
            historical_df.sort(feature_view.timestamp_field, descending=True)
            .unique(subset=[entity_key], keep="first")
        )

        feature_cols = feature_view.get_feature_names()
        records = latest_df.to_dicts()

        features_payload: Dict[str, Dict[str, Any]] = {}
        for row in records:
            entity_id = str(row[entity_key])
            feats = {k: row[k] for k in feature_cols if k in row}
            features_payload[entity_id] = feats

        written_count = await self.online_store.write_online_features(
            view_name=feature_view.name,
            entity_key=entity_key,
            features_dict=features_payload,
            ttl_seconds=feature_view.ttl_seconds,
        )

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            f"Successfully materialized {written_count} entities for view '{feature_view.name}' in {duration:.3f}s"
        )

        return {
            "view_name": feature_view.name,
            "materialized_count": written_count,
            "duration_seconds": duration,
            "timestamp": start_time.isoformat(),
        }
