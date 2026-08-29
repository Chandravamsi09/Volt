"""
Continuous Model & Data Drift Monitoring Engine
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np
import polars as pl
from backend.app.core.config import settings
from backend.app.observability.drift.statistical_detector import (
    ColumnDriftResult,
    StatisticalDriftDetector,
)


@dataclass
class DriftReport:
    model_name: str
    model_version: str
    timestamp: str
    dataset_drift_detected: bool
    drifted_columns_count: int
    total_columns_count: int
    share_of_drifted_columns: float
    column_results: Dict[str, ColumnDriftResult]
    summary_message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "timestamp": self.timestamp,
            "dataset_drift_detected": self.dataset_drift_detected,
            "drifted_columns_count": self.drifted_columns_count,
            "total_columns_count": self.total_columns_count,
            "share_of_drifted_columns": round(self.share_of_drifted_columns, 3),
            "summary_message": self.summary_message,
            "column_results": {
                col: {
                    "column_name": res.column_name,
                    "drift_detected": res.drift_detected,
                    "metric_name": res.metric_name,
                    "metric_value": round(res.metric_value, 4),
                    "threshold": res.threshold,
                    "p_value": round(res.p_value, 4) if res.p_value is not None else None,
                }
                for col, res in self.column_results.items()
            },
        }


class DriftMonitor:
    """Evaluates live production inferences against training baseline distributions."""

    def __init__(
        self,
        psi_threshold: float = 0.25,
        ks_pvalue_threshold: float = 0.05,
        dataset_drift_threshold: float = 0.33,
    ):
        self.psi_threshold = psi_threshold
        self.ks_pvalue_threshold = ks_pvalue_threshold
        self.dataset_drift_threshold = dataset_drift_threshold
        self.detector = StatisticalDriftDetector()

    def profile_and_compare(
        self,
        model_name: str,
        model_version: str,
        baseline_df: pl.DataFrame,
        current_df: pl.DataFrame,
        feature_columns: Optional[List[str]] = None,
    ) -> DriftReport:
        """Run drift detection suite over numerical and categorical feature sets."""
        cols = feature_columns or [c for c in baseline_df.columns if c in current_df.columns]
        column_results: Dict[str, ColumnDriftResult] = {}
        drifted_count = 0

        for col in cols:
            b_series = baseline_df[col].drop_nulls()
            c_series = current_df[col].drop_nulls()

            if len(b_series) == 0 or len(c_series) == 0:
                continue

            b_arr = b_series.to_numpy()
            c_arr = c_series.to_numpy()

            # Check if numerical
            if np.issubdtype(b_arr.dtype, np.number):
                ks_stat, p_val = self.detector.calculate_ks_test(b_arr, c_arr)
                psi_val = self.detector.calculate_psi(b_arr, c_arr)

                # Drift condition: KS p-value < threshold OR PSI >= threshold
                drift_detected = (p_val < self.ks_pvalue_threshold) or (psi_val >= self.psi_threshold)
                if drift_detected:
                    drifted_count += 1

                column_results[col] = ColumnDriftResult(
                    column_name=col,
                    drift_detected=drift_detected,
                    metric_name="PSI / KS-Test",
                    metric_value=psi_val,
                    threshold=self.psi_threshold,
                    p_value=p_val,
                )

        total_cols = max(len(column_results), 1)
        drift_share = drifted_count / total_cols
        dataset_drift_detected = drift_share >= self.dataset_drift_threshold

        msg = (
            f"Dataset drift detected! {drifted_count}/{total_cols} columns drifted ({drift_share:.1%})"
            if dataset_drift_detected
            else f"No significant dataset drift ({drifted_count}/{total_cols} columns drifted)"
        )

        return DriftReport(
            model_name=model_name,
            model_version=model_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            dataset_drift_detected=dataset_drift_detected,
            drifted_columns_count=drifted_count,
            total_columns_count=total_cols,
            share_of_drifted_columns=drift_share,
            column_results=column_results,
            summary_message=msg,
        )


drift_monitor = DriftMonitor()
