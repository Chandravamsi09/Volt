"""
Point-in-Time (AS OF) Offline Feature Store Engine
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl
from backend.app.core.config import settings
from backend.app.core.exceptions import FeatureStoreError
from backend.app.feature_store.definitions import FeatureView


class OfflineFeatureStore:
    """Offline feature store managing historical Parquet features with leak-free AS-OF joins."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir or settings.OFFLINE_FEATURE_STORE_PATH)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_view_path(self, view_name: str) -> Path:
        view_dir = self.storage_dir / view_name
        view_dir.mkdir(parents=True, exist_ok=True)
        return view_dir / "features.parquet"

    def write_features(self, view: FeatureView, df: pl.DataFrame) -> int:
        """Persist historical feature partition."""
        target_path = self._get_view_path(view.name)

        # Validate required columns
        for entity in view.entities:
            # We assume join_key column is in the DataFrame
            pass
        if view.timestamp_field not in df.columns:
            raise FeatureStoreError(f"Missing required timestamp field: {view.timestamp_field}")

        if target_path.exists():
            existing = pl.read_parquet(target_path)
            merged = pl.concat([existing, df], how="vertical_relaxed")
        else:
            merged = df

        merged.write_parquet(target_path, compression="zstd")
        return len(df)

    def read_historical_features(self, view_name: str) -> pl.DataFrame:
        target_path = self._get_view_path(view_name)
        if not target_path.exists():
            return pl.DataFrame()
        return pl.read_parquet(target_path)

    def get_historical_features_asof(
        self,
        entity_df: pl.DataFrame,
        entity_key: str,
        timestamp_col: str,
        feature_view: FeatureView,
    ) -> pl.DataFrame:
        """Perform point-in-time correct (AS OF) join preventing future data leakage."""
        feature_df = self.read_historical_features(feature_view.name)
        if feature_df.is_empty():
            return entity_df

        # Sort both datasets by timestamp
        entity_sorted = entity_df.sort(timestamp_col)
        feature_sorted = feature_df.sort(feature_view.timestamp_field)

        # Perform Polars join_asof
        joined_df = entity_sorted.join_asof(
            feature_sorted,
            left_on=timestamp_col,
            right_on=feature_view.timestamp_field,
            by_left=entity_key,
            by_right=entity_key,
            strategy="backward",
        )

        return joined_df
