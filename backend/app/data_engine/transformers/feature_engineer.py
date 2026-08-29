"""
Polars-Accelerated Feature Engineering Pipeline
"""

from typing import Any, Dict, List, Optional
import polars as pl
from backend.app.core.exceptions import ValidationError
from backend.app.data_engine.transformers.base_transformer import BaseTransformer


class NumericalScaler(BaseTransformer):
    """Zero-mean unit-variance (standard) or min-max normalization."""

    def __init__(self, columns: List[str], method: str = "standard"):
        super().__init__({"columns": columns, "method": method})
        self.columns = columns
        self.method = method
        self.stats: Dict[str, Dict[str, float]] = {}

    def fit(self, df: pl.DataFrame) -> "NumericalScaler":
        self.stats = {}
        for col in self.columns:
            if col not in df.columns:
                continue
            series = df[col].cast(pl.Float64).drop_nulls()
            if self.method == "standard":
                mean_val = series.mean() or 0.0
                std_val = series.std() or 1.0
                if std_val == 0.0:
                    std_val = 1.0
                self.stats[col] = {"mean": float(mean_val), "std": float(std_val)}
            elif self.method == "minmax":
                min_val = series.min() or 0.0
                max_val = series.max() or 1.0
                denom = max_val - min_val
                if denom == 0.0:
                    denom = 1.0
                self.stats[col] = {"min": float(min_val), "max": float(max_val), "denom": float(denom)}
        self._is_fitted = True
        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self._is_fitted:
            raise ValidationError("Transformer must be fitted before transform().")

        expressions = []
        for col, col_stats in self.stats.items():
            if col in df.columns:
                if self.method == "standard":
                    expr = (pl.col(col).cast(pl.Float64) - col_stats["mean"]) / col_stats["std"]
                else:
                    expr = (pl.col(col).cast(pl.Float64) - col_stats["min"]) / col_stats["denom"]
                expressions.append(expr.alias(f"{col}_scaled"))

        return df.with_columns(expressions) if expressions else df

    def to_dict(self) -> Dict[str, Any]:
        return {"columns": self.columns, "method": self.method, "stats": self.stats}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NumericalScaler":
        scaler = cls(columns=data["columns"], method=data["method"])
        scaler.stats = data.get("stats", {})
        scaler._is_fitted = bool(scaler.stats)
        return scaler


class CategoricalEncoder(BaseTransformer):
    """High-performance One-Hot Encoding and Frequency Encoding."""

    def __init__(self, columns: List[str], method: str = "one_hot", max_categories: int = 20):
        super().__init__({"columns": columns, "method": method, "max_categories": max_categories})
        self.columns = columns
        self.method = method
        self.max_categories = max_categories
        self.vocabularies: Dict[str, List[str]] = {}

    def fit(self, df: pl.DataFrame) -> "CategoricalEncoder":
        self.vocabularies = {}
        for col in self.columns:
            if col not in df.columns:
                continue
            value_counts = df[col].cast(pl.Utf8).value_counts().sort("count", descending=True)
            top_vals = [
                str(v)
                for v in value_counts[col].head(self.max_categories).to_list()
                if v is not None
            ]
            self.vocabularies[col] = top_vals
        self._is_fitted = True
        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if not self._is_fitted:
            raise ValidationError("Transformer must be fitted before transform().")

        expressions = []
        for col, cats in self.vocabularies.items():
            if col in df.columns:
                for cat in cats:
                    safe_cat = str(cat).replace(" ", "_").replace("-", "_").lower()
                    expr = (pl.col(col).cast(pl.Utf8) == cat).cast(pl.Int32).alias(f"{col}_{safe_cat}")
                    expressions.append(expr)

        return df.with_columns(expressions) if expressions else df

    def to_dict(self) -> Dict[str, Any]:
        return {
            "columns": self.columns,
            "method": self.method,
            "max_categories": self.max_categories,
            "vocabularies": self.vocabularies,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CategoricalEncoder":
        enc = cls(
            columns=data["columns"],
            method=data["method"],
            max_categories=data.get("max_categories", 20),
        )
        enc.vocabularies = data.get("vocabularies", {})
        enc._is_fitted = bool(enc.vocabularies)
        return enc


class DateTimeFeatureExtractor(BaseTransformer):
    """Extract temporal features: hour, day_of_week, day_of_month, is_weekend, quarter."""

    def __init__(self, timestamp_column: str):
        super().__init__({"timestamp_column": timestamp_column})
        self.timestamp_column = timestamp_column

    def fit(self, df: pl.DataFrame) -> "DateTimeFeatureExtractor":
        self._is_fitted = True
        return self

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:
        if self.timestamp_column not in df.columns:
            return df

        ts = pl.col(self.timestamp_column).cast(pl.Datetime)
        return df.with_columns([
            ts.dt.hour().alias(f"{self.timestamp_column}_hour"),
            ts.dt.weekday().alias(f"{self.timestamp_column}_dayofweek"),
            ts.dt.day().alias(f"{self.timestamp_column}_day"),
            ts.dt.month().alias(f"{self.timestamp_column}_month"),
            (ts.dt.weekday() >= 5).cast(pl.Int32).alias(f"{self.timestamp_column}_is_weekend"),
        ])

    def to_dict(self) -> Dict[str, Any]:
        return {"timestamp_column": self.timestamp_column}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DateTimeFeatureExtractor":
        extractor = cls(timestamp_column=data["timestamp_column"])
        extractor._is_fitted = True
        return extractor
