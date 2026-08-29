"""
Data Contract & Great Expectations-Style Quality Validation Tests
"""

import polars as pl
import pytest
from backend.app.data_engine.contracts import ColumnRule, DatasetContract, DataType
from backend.app.data_engine.validators.data_validator import DataQualityValidator


def test_data_contract_clean_dataframe_passes(sample_tabular_df, sample_dataset_contract):
    validator = DataQualityValidator(sample_dataset_contract)
    report = validator.validate(sample_tabular_df)

    assert report.passed is True
    assert report.quality_score >= 95.0
    assert len(report.errors) == 0


def test_data_contract_quarantines_invalid_and_out_of_bounds_rows(sample_dataset_contract):
    # Construct DataFrame with intentional contract violations
    invalid_df = pl.DataFrame({
        "user_id": ["u1", "u2", "u3", "u4"],
        "age": [25, 12, None, 45],  # 12 is < min_value 18, None in non-nullable col
        "income": [50000.0, -100.0, 80000.0, 60000.0],  # -100 is < min_value 0
        "is_fraud": [0, 1, 99, 0],  # 99 is not in allowed_values [0, 1]
    })

    validator = DataQualityValidator(sample_dataset_contract)
    report = validator.validate(invalid_df)

    assert report.passed is False
    assert len(report.quarantine_row_indices) > 0
    assert report.quality_score < 100.0
    assert report.column_results["age"].passed is False
    assert report.column_results["is_fraud"].disallowed_category_count == 1
