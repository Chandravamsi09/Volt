"""
Base Transformer Interface for High-Throughput Data Transformations
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import polars as pl


class BaseTransformer(ABC):
    """Abstract interface for all scalable DataFrame transformations in Volt."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._is_fitted: bool = False

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    @abstractmethod
    def fit(self, df: pl.DataFrame) -> "BaseTransformer":
        """Learn parameters (means, standard deviations, vocabularies) from data."""
        pass

    @abstractmethod
    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """Apply the learned transformation to a DataFrame."""
        pass

    def fit_transform(self, df: pl.DataFrame) -> pl.DataFrame:
        """Fit and transform in a single optimized pass."""
        return self.fit(df).transform(df)

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize transformation parameters to dictionary."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseTransformer":
        """Reconstruct transformer from serialized state."""
        pass

    def save(self, file_path: str) -> None:
        """Save transformer metadata to JSON file."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, file_path: str) -> "BaseTransformer":
        """Load transformer from JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
