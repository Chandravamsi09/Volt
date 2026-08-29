"""
Production Data Quality & Schema Contract Validation Engine
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import polars as pl
from backend.app.data_engine.contracts import ColumnRule, DatasetContract, DataType


@dataclass
class ColumnValidationResult:
    column: str
    passed: bool
    null_count: int
    null_percentage: float
    invalid_type_count: int
    out_of_bounds_count: int
    regex_mismatches: int
    disallowed_category_count: int
    unique_violations: int
    details: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    contract_name: str
    contract_version: str
    timestamp: datetime
    total_rows: int
    passed: bool
    quality_score: float  # Scale of 0.0 to 100.0
    column_results: Dict[str, ColumnValidationResult]
    errors: List[str]
    warnings: List[str]
    quarantine_row_indices: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "timestamp": self.timestamp.isoformat(),
            "total_rows": self.total_rows,
            "passed": self.passed,
            "quality_score": round(self.quality_score, 2),
            "errors": self.errors,
            "warnings": self.warnings,
            "quarantined_rows_count": len(self.quarantine_row_indices),
            "column_results": {
                col: {
                    "passed": res.passed,
                    "null_count": res.null_count,
                    "null_percentage": round(res.null_percentage, 2),
                    "out_of_bounds_count": res.out_of_bounds_count,
                    "disallowed_category_count": res.disallowed_category_count,
                    "details": res.details,
                }
                for col, res in self.column_results.items()
            },
        }


class DataQualityValidator:
    """Engine for validating Polars DataFrames against declared DatasetContracts."""

    def __init__(self, contract: DatasetContract):
        self.contract = contract

    def validate(self, df: pl.DataFrame) -> ValidationReport:
        errors: List[str] = []
        warnings: List[str] = []
        column_results: Dict[str, ColumnValidationResult] = {}
        quarantine_indices = set()
        total_rows = len(df)

        if total_rows == 0:
            return ValidationReport(
                contract_name=self.contract.name,
                contract_version=self.contract.version,
                timestamp=datetime.now(timezone.utc),
                total_rows=0,
                passed=False,
                quality_score=0.0,
                column_results={},
                errors=["Dataset is empty (0 rows)."],
                warnings=[],
                quarantine_row_indices=[],
            )

        # 1. Check Missing Columns
        present_cols = set(df.columns)
        required_cols = {col.name for col in self.contract.columns}
        missing_cols = required_cols - present_cols

        if missing_cols:
            errors.append(f"Missing required columns in dataset: {list(missing_cols)}")

        # 2. Check Strict Schema Extra Columns
        if self.contract.strict_schema:
            extra_cols = present_cols - required_cols
            if extra_cols:
                warnings.append(f"Undeclared extra columns found: {list(extra_cols)}")

        total_checks = 0
        passed_checks = 0

        # 3. Column-by-Column Validations
        for rule in self.contract.columns:
            col_name = rule.name
            if col_name not in df.columns:
                continue

            col_series = df[col_name]
            col_details = []
            col_passed = True

            # Null check
            null_count = col_series.null_count()
            null_pct = (null_count / total_rows) * 100.0
            total_checks += 1

            if not rule.nullable and null_count > 0:
                col_passed = False
                col_details.append(f"{null_count} null values found ({null_pct:.1f}%) in non-nullable column")
                # Identify null indices for quarantine
                null_idxs = [i for i, val in enumerate(col_series.to_list()) if val is None]
                quarantine_indices.update(null_idxs)
            else:
                passed_checks += 1

            # Numerical Range Bounds
            out_of_bounds = 0
            if rule.dtype in [DataType.INT64, DataType.FLOAT64]:
                valid_vals = col_series.drop_nulls()
                if len(valid_vals) > 0:
                    total_checks += 1
                    if rule.min_value is not None:
                        violations = (valid_vals < rule.min_value).sum()
                        if violations > 0:
                            out_of_bounds += violations
                            col_passed = False
                            col_details.append(f"{violations} values less than min_value {rule.min_value}")
                    if rule.max_value is not None:
                        violations = (valid_vals > rule.max_value).sum()
                        if violations > 0:
                            out_of_bounds += violations
                            col_passed = False
                            col_details.append(f"{violations} values greater than max_value {rule.max_value}")

                    if out_of_bounds == 0:
                        passed_checks += 1

            # Categorical Allow-List
            disallowed_count = 0
            if rule.allowed_values is not None:
                total_checks += 1
                valid_vals = [v for v in col_series.to_list() if v is not None]
                disallowed = [v for v in valid_vals if v not in rule.allowed_values]
                disallowed_count = len(disallowed)
                if disallowed_count > 0:
                    col_passed = False
                    col_details.append(f"{disallowed_count} values outside allowed category set")
                else:
                    passed_checks += 1

            # Unique Constraint Check
            unique_violations = 0
            if rule.unique:
                total_checks += 1
                unique_violations = total_rows - col_series.n_unique()
                if unique_violations > 0:
                    col_passed = False
                    col_details.append(f"{unique_violations} duplicate values found in unique column")
                else:
                    passed_checks += 1

            column_results[col_name] = ColumnValidationResult(
                column=col_name,
                passed=col_passed,
                null_count=null_count,
                null_percentage=null_pct,
                invalid_type_count=0,
                out_of_bounds_count=out_of_bounds,
                regex_mismatches=0,
                disallowed_category_count=disallowed_count,
                unique_violations=unique_violations,
                details=col_details,
            )

        quality_score = (passed_checks / max(total_checks, 1)) * 100.0
        overall_passed = len(errors) == 0 and all(r.passed for r in column_results.values())

        return ValidationReport(
            contract_name=self.contract.name,
            contract_version=self.contract.version,
            timestamp=datetime.now(timezone.utc),
            total_rows=total_rows,
            passed=overall_passed,
            quality_score=quality_score,
            column_results=column_results,
            errors=errors,
            warnings=warnings,
            quarantine_row_indices=sorted(list(quarantine_indices)),
        )
