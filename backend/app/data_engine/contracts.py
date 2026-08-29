"""
Data Schema Contracts & Structural Constraints Specification
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DataType(str, Enum):
    INT64 = "int64"
    FLOAT64 = "float64"
    STRING = "string"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    CATEGORICAL = "categorical"
    JSON = "json"


class ColumnRule(BaseModel):
    name: str
    dtype: DataType
    nullable: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    unique: bool = False
    description: Optional[str] = None


class DatasetContract(BaseModel):
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    columns: List[ColumnRule]
    primary_key: Optional[str] = None
    timestamp_column: Optional[str] = None
    strict_schema: bool = True  # Disallow undeclared columns if True

    def get_column(self, col_name: str) -> Optional[ColumnRule]:
        for col in self.columns:
            if col.name == col_name:
                return col
        return None
