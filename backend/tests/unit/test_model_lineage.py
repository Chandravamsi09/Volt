"""
Unit tests for Cryptographic Model Lineage Tracking
"""
import pytest
import tempfile
from pathlib import Path
from backend.app.ml_engine.registry.model_vault import ModelVault

def test_model_lineage_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = ModelVault(base_path=tmpdir)
        
        # Create dummy artifact
        dummy_file = Path(tmpdir) / "model.bin"
        dummy_file.write_bytes(b"dummy_weights_volt_1.0")

        meta = vault.register_model(
            name="fraud_detector_v1",
            version="1.0.0",
            artifact_source_path=str(dummy_file),
            framework="xgboost",
            metrics={"auc_roc": 0.962, "f1_score": 0.91},
            parameters={"max_depth": 6, "learning_rate": 0.05},
            input_schema={"amount": "float", "card_age": "int"},
            output_schema={"is_fraud": "bool"},
        )

        lineage = vault.get_model_lineage("fraud_detector_v1", "1.0.0")
        assert lineage["model_name"] == "fraud_detector_v1"
        assert lineage["artifact_checksum"] == meta.checksum
        assert lineage["provenance_verified"] is True
        assert "amount" in lineage["input_features"]
