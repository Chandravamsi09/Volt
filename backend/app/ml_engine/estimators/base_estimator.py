"""
Base Estimator Interface for Standardized Model Architectures
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import polars as pl


class BaseEstimator(ABC):
    """Abstract interface for all supervised and unsupervised models in Volt."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.model = None
        self.feature_names: List[str] = []
        self.target_name: Optional[str] = None
        self._is_trained: bool = False

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "BaseEstimator":
        """Train model on feature array X and target array y."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate point predictions."""
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Generate prediction probabilities for classification tasks."""
        pass

    @abstractmethod
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Compute performance metrics against ground truth."""
        pass

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Save model weights to disk."""
        pass

    @classmethod
    @abstractmethod
    def load(cls, filepath: str) -> "BaseEstimator":
        """Load model weights from disk."""
        pass
