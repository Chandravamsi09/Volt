"""
End-to-End ML Training Pipeline Orchestrator
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import polars as pl
from sklearn.model_selection import train_test_split
from backend.app.ml_engine.estimators.base_estimator import BaseEstimator
from backend.app.ml_engine.estimators.tabular import TabularClassifier
from backend.app.ml_engine.registry.experiment_tracker import ExperimentTracker


class MLTrainingPipeline:
    """Orchestrates feature extraction, train/test splitting, training, and metrics logging."""

    def __init__(self, tracker: Optional[ExperimentTracker] = None):
        self.tracker = tracker or ExperimentTracker()

    def train_classification_pipeline(
        self,
        df: pl.DataFrame,
        feature_columns: List[str],
        target_column: str,
        experiment_name: str = "default_experiment",
        run_name: str = "run_1",
        algorithm: str = "gradient_boosting",
        test_size: float = 0.2,
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[BaseEstimator, Dict[str, float], str]:
        """Execute full training lifecycle and record metrics."""
        # 1. Start Experiment Tracking Run
        run_ctx = self.tracker.start_run(
            experiment_name=experiment_name,
            run_name=run_name,
            tags=["classification", algorithm],
        )

        params = hyperparameters or {
            "algorithm": algorithm,
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
        self.tracker.log_params(run_ctx.run_id, params)

        # 2. Extract arrays
        clean_df = df.select(feature_columns + [target_column]).drop_nulls()
        X = clean_df.select(feature_columns).to_numpy()
        y = clean_df.select(target_column).to_numpy().ravel()

        # 3. Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )

        # 4. Instantiate and Train Estimator
        estimator = TabularClassifier(
            algorithm=params.get("algorithm", "gradient_boosting"),
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 5),
            learning_rate=params.get("learning_rate", 0.1),
        )
        estimator.fit(X_train, y_train, feature_names=feature_columns)
        estimator.target_name = target_column

        # 5. Evaluate Performance
        train_metrics = estimator.evaluate(X_train, y_train)
        test_metrics = estimator.evaluate(X_test, y_test)

        combined_metrics = {
            f"train_{k}": v for k, v in train_metrics.items()
        }
        combined_metrics.update({
            f"test_{k}": v for k, v in test_metrics.items()
        })

        for k, v in combined_metrics.items():
            self.tracker.log_metric(run_ctx.run_id, k, v)

        self.tracker.end_run(run_ctx.run_id, status="COMPLETED")
        return estimator, combined_metrics, run_ctx.run_id
