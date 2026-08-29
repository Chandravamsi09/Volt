"""
Integration Tests for FastAPI Endpoints (Health, Auth, Pipelines, Serving & RAG)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.ml_engine.estimators.tabular import TabularClassifier
from backend.app.ml_engine.serving.inference_engine import inference_engine


def test_health_check_endpoint(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_lakehouse_ingest_and_sql_query(test_client: TestClient):
    # 1. Ingest records
    records = [
        {"user_id": "u1", "amount": 100.5, "status": "approved"},
        {"user_id": "u2", "amount": 250.0, "status": "declined"},
    ]
    ingest_resp = test_client.post(
        "/api/v1/pipelines/tables/ingest",
        json={"table_name": "test_orders", "data": records, "mode": "append"},
    )
    assert ingest_resp.status_code == 200

    # 2. Query via DuckDB
    query_resp = test_client.post(
        "/api/v1/pipelines/query",
        json={"sql": "SELECT 1 as num, 'volt' as platform"},
    )
    assert query_resp.status_code == 200
    q_data = query_resp.json()["data"]
    assert q_data["row_count"] == 1
    assert q_data["records"][0]["platform"] == "volt"


def test_feature_store_entity_and_view_registration(test_client: TestClient):
    # Register Entity
    entity_resp = test_client.post(
        "/api/v1/features/entities",
        json={"name": "account", "join_key": "account_id", "description": "Banking account"},
    )
    assert entity_resp.status_code == 200

    # Register Feature View
    view_resp = test_client.post(
        "/api/v1/features/views",
        json={
            "name": "account_risk_v1",
            "entities": ["account"],
            "features": [{"name": "risk_score", "dtype": "float64"}],
            "source_table": "raw_account_events",
            "timestamp_field": "event_timestamp",
        },
    )
    assert view_resp.status_code == 200


def test_realtime_inference_serving(test_client: TestClient, test_temp_dir):
    # Train and load a model directly into inference engine
    import numpy as np
    X = np.random.randn(50, 4)
    y = np.random.choice([0, 1], size=50)

    clf = TabularClassifier(n_estimators=10)
    clf.fit(X, y)

    model_path = f"{test_temp_dir}/serving_model.joblib"
    clf.save(model_path)

    inference_engine.load_model(
        name="test_clf",
        version="v1",
        artifact_path=model_path,
        framework="scikit-learn",
    )

    # Invoke prediction endpoint
    predict_resp = test_client.post(
        "/api/v1/inference/predict",
        json={
            "model_name": "test_clf",
            "version": "v1",
            "features": [[0.5, -1.2, 0.3, 0.9], [1.1, 0.4, -0.2, 0.1]],
        },
    )
    assert predict_resp.status_code == 200
    pred_data = predict_resp.json()["data"]
    assert len(pred_data["predictions"]) == 2
    assert "latency_ms" in pred_data


def test_rag_and_guardrail_endpoint(test_client: TestClient):
    # Ingest doc
    ingest_resp = test_client.post(
        "/api/v1/llm/documents/ingest",
        json={
            "doc_id": "guide_01",
            "title": "Volt Architecture Guide",
            "content": "Volt provides high-throughput lakehouse pipelines and sub-5ms feature store serving.",
        },
    )
    assert ingest_resp.status_code == 200

    # Query RAG
    rag_resp = test_client.post(
        "/api/v1/llm/rag/query",
        json={"query": "What does Volt provide?", "top_k": 2},
    )
    assert rag_resp.status_code == 200
    assert rag_resp.json()["data"]["passed_guardrails"] is True
