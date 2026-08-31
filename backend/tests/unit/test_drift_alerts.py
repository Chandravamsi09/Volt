"""
Unit tests for Drift Alerting & Webhook Payload Formatting
"""
import pytest
from backend.app.observability.drift.drift_monitor import DriftMonitor

def test_drift_alert_payload_generation():
    monitor = DriftMonitor()
    mock_drift = {
        "drift_detected": True,
        "mean_psi": 0.32,
        "feature_drift": {
            "income": {"drift_detected": True, "psi": 0.35},
            "age": {"drift_detected": False, "psi": 0.05},
        }
    }
    
    alert = monitor.build_drift_alert_payload("credit_risk_v2", mock_drift, webhook_url="https://hooks.slack.com/services/test")
    assert alert["severity"] == "HIGH"
    assert alert["drift_detected"] is True
    assert alert["metrics_summary"]["features_drifted"] == 1
    assert alert["recommended_action"] == "Trigger Automated Retraining Workflow"
