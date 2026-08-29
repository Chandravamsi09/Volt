"""
Tabular Estimators: Gradient Boosted Trees & Random Forests
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from backend.app.ml_engine.estimators.base_estimator import BaseEstimator


class TabularClassifier(BaseEstimator):
    """Production Tabular Classifier supporting Random Forest & Gradient Boosting."""

    def __init__(
        self,
        algorithm: str = "gradient_boosting",
        n_estimators: int = 100,
        max_depth: int = 5,
        learning_rate: float = 0.1,
        random_state: int = 42,
    ):
        config = {
            "algorithm": algorithm,
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": random_state,
        }
        super().__init__(config)
        self.algorithm = algorithm

        if algorithm == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
            )
        else:
            self.model = GradientBoostingClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                learning_rate=learning_rate,
                random_state=random_state,
            )

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "TabularClassifier":
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        self.model.fit(X, y)
        self._is_trained = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model must be trained before calling predict().")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model must be trained before calling predict_proba().")
        return self.model.predict_proba(X)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        preds = self.predict(X)
        proba = self.predict_proba(X)

        metrics = {
            "accuracy": float(accuracy_score(y, preds)),
            "precision": float(precision_score(y, preds, average="weighted", zero_division=0)),
            "recall": float(recall_score(y, preds, average="weighted", zero_division=0)),
            "f1": float(f1_score(y, preds, average="weighted", zero_division=0)),
        }

        # Calculate ROC-AUC for binary or multi-class if applicable
        try:
            if proba.shape[1] == 2:
                metrics["roc_auc"] = float(roc_auc_score(y, proba[:, 1]))
            else:
                metrics["roc_auc"] = float(roc_auc_score(y, proba, multi_class="ovr"))
        except Exception:
            metrics["roc_auc"] = 0.0

        return metrics

    def save(self, filepath: str) -> None:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "config": self.config,
            "feature_names": self.feature_names,
            "target_name": self.target_name,
            "model": self.model,
            "_is_trained": self._is_trained,
        }
        joblib.dump(payload, filepath)

    @classmethod
    def load(cls, filepath: str) -> "TabularClassifier":
        payload = joblib.load(filepath)
        instance = cls(**payload["config"])
        instance.feature_names = payload.get("feature_names", [])
        instance.target_name = payload.get("target_name")
        instance.model = payload["model"]
        instance._is_trained = payload.get("_is_trained", True)
        return instance
