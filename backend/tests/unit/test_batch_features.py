"""
Unit tests for Batch Online Feature Store Operations
"""
import pytest
from backend.app.feature_store.online_store import OnlineFeatureStore

@pytest.mark.asyncio
async def test_batch_feature_write_and_retrieval():
    store = OnlineFeatureStore()
    test_data = {
        "user_101": {"transaction_count_24h": 15, "risk_score": 0.04},
        "user_102": {"transaction_count_24h": 3, "risk_score": 0.88},
    }
    
    written = await store.write_online_features(
        view_name="user_risk_features",
        entity_key="user_id",
        features_dict=test_data,
    )
    assert written == 2

    retrieved = await store.get_online_features(
        view_name="user_risk_features",
        entity_key="user_id",
        entity_ids=["user_101", "user_102"],
    )
    assert retrieved["user_101"]["transaction_count_24h"] == 15
    assert retrieved["user_102"]["risk_score"] == 0.88

    deleted = await store.delete_online_features(
        view_name="user_risk_features",
        entity_key="user_id",
        entity_ids=["user_101"],
    )
    assert deleted >= 1
