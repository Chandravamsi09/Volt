"""
Feature Store Metadata Definitions: Entities, Features, and Feature Views
"""

from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FeatureDataType(str, Enum):
    INT64 = "int64"
    FLOAT64 = "float64"
    STRING = "string"
    BOOLEAN = "boolean"
    BYTES = "bytes"
    DATETIME = "datetime"


class Entity(BaseModel):
    name: str
    join_key: str
    description: Optional[str] = None
    value_type: FeatureDataType = FeatureDataType.STRING


class Feature(BaseModel):
    name: str
    dtype: FeatureDataType
    description: Optional[str] = None
    default_value: Optional[Any] = None


class FeatureView(BaseModel):
    name: str
    version: str = "1.0.0"
    entities: List[str]  # List of Entity names
    features: List[Feature]
    source_table: str
    timestamp_field: str = "event_timestamp"
    ttl_seconds: int = 86400 * 30  # Default 30 days
    online_enabled: bool = True
    description: Optional[str] = None

    def get_feature_names(self) -> List[str]:
        return [f.name for f in self.features]
