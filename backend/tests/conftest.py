"""
Pytest Test Fixtures & Shared Test Resources
"""

import os
import shutil
import tempfile
from datetime import datetime, timezone
import numpy as np
import polars as pl
import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import settings
from backend.app.data_engine.contracts import ColumnRule, DatasetContract, DataType
from backend.app.feature_store.definitions import Entity, Feature, FeatureDataType, FeatureView
from backend.app.main import app


@pytest.fixture(scope="session")
def test_temp_dir():
    temp_dir = tempfile.mkdtemp(prefix="volt_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def sample_tabular_df():
    np.random.seed(42)
    n_rows = 200
    return pl.DataFrame({
        "user_id": [f"user_{i}" for i in range(n_rows)],
        "age": np.random.randint(18, 70, size=n_rows),
        "income": np.random.uniform(20000, 150000, size=n_rows),
        "credit_score": np.random.uniform(300, 850, size=n_rows),
        "transaction_amount": np.random.exponential(scale=50, size=n_rows),
        "is_fraud": np.random.choice([0, 1], size=n_rows, p=[0.8, 0.2]),
        "event_timestamp": [datetime.now(timezone.utc) for _ in range(n_rows)],
    })


@pytest.fixture
def sample_dataset_contract():
    return DatasetContract(
        name="user_transaction_contract",
        version="1.0.0",
        columns=[
            ColumnRule(name="user_id", dtype=DataType.STRING, nullable=False),
            ColumnRule(name="age", dtype=DataType.INT64, nullable=False, min_value=18, max_value=120),
            ColumnRule(name="income", dtype=DataType.FLOAT64, nullable=False, min_value=0),
            ColumnRule(name="is_fraud", dtype=DataType.INT64, nullable=False, allowed_values=[0, 1]),
        ],
        strict_schema=True,
    )
