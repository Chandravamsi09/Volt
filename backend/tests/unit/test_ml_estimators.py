"""
Unit Tests for Machine Learning Estimators & Model Vault
"""

import os
from pathlib import Path
import numpy as np
import pytest
from backend.app.ml_engine.estimators.tabular import TabularClassifier
from backend.app.ml_engine.registry.model_vault import ModelVault


def test_tabular_classifier_training_and_eval():
    np.random.seed(42)
    X = np.random.randn(100, 5)
    y = np.random.choice([0, 1], size=100)

    clf = TabularClassifier(algorithm="gradient_boosting", n_estimators=20, max_depth=3)
    clf.fit(X, y)

    preds = clf.predict(X)
    assert len(preds) == 100

    proba = clf.predict_proba(X)
    assert proba.shape == (100, 2)

    metrics = clf.evaluate(X, y)
    assert "accuracy" in metrics
    assert "f1" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0


def test_model_vault_registration_and_stage_transition(test_temp_dir):
    vault = ModelVault(base_path=test_temp_dir)

    # Create dummy artifact file
    dummy_file = Path(test_temp_dir) / "dummy_model.joblib"
    dummy_file.write_text("model_bytes_data")

    meta = vault.register_model(
        name="credit_risk",
        version="v1.0.0",
        artifact_source_path=str(dummy_file),
        framework="scikit-learn",
        metrics={"f1": 0.92},
        stage="STAGING",
    )

    assert meta.name == "credit_risk"
    assert meta.stage == "STAGING"
    assert len(meta.checksum) == 64

    # Stage Promotion
    promoted = vault.transition_stage("credit_risk", "v1.0.0", "PRODUCTION")
    assert promoted.stage == "PRODUCTION"

    fetched = vault.get_model("credit_risk", "v1.0.0")
    assert fetched is not None
    assert fetched.stage == "PRODUCTION"
