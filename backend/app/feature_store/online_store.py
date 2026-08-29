"""
Sub-5ms Online Feature Store (Redis with High-Speed In-Memory Fallback)
"""

import json
import logging
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings

logger = logging.getLogger("volt.online_store")


class OnlineFeatureStore:
    """High-throughput key-value feature store for real-time inference serving."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client = None
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._use_memory_fallback = False

    async def _get_client(self):
        if self._redis_client is None and not self._use_memory_fallback:
            try:
                import redis.asyncio as aioredis
                client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1.5,
                )
                await client.ping()
                self._redis_client = client
            except Exception as exc:
                logger.warning(
                    f"Redis unavailable ({exc}), activating in-memory store fallback."
                )
                self._use_memory_fallback = True
        return self._redis_client

    def _make_key(self, view_name: str, entity_key: str, entity_id: str) -> str:
        return f"volt:fs:{view_name}:{entity_key}:{entity_id}"

    async def write_online_features(
        self,
        view_name: str,
        entity_key: str,
        features_dict: Dict[str, Dict[str, Any]],  # entity_id -> {feat: val}
        ttl_seconds: Optional[int] = None,
    ) -> int:
        """Write bulk feature values into online store."""
        client = await self._get_client()

        if client and not self._use_memory_fallback:
            pipeline = client.pipeline()
            for entity_id, feats in features_dict.items():
                key = self._make_key(view_name, entity_key, entity_id)
                pipeline.set(key, json.dumps(feats), ex=ttl_seconds)
            await pipeline.execute()
        else:
            # Memory store
            for entity_id, feats in features_dict.items():
                key = self._make_key(view_name, entity_key, entity_id)
                self._memory_cache[key] = feats

        return len(features_dict)

    async def get_online_features(
        self,
        view_name: str,
        entity_key: str,
        entity_ids: List[str],
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Fetch online features for real-time inference (sub-5ms)."""
        client = await self._get_client()
        result: Dict[str, Optional[Dict[str, Any]]] = {}

        if client and not self._use_memory_fallback:
            keys = [self._make_key(view_name, entity_key, eid) for eid in entity_ids]
            values = await client.mget(keys)
            for eid, val in zip(entity_ids, values):
                result[eid] = json.loads(val) if val else None
        else:
            for eid in entity_ids:
                key = self._make_key(view_name, entity_key, eid)
                result[eid] = self._memory_cache.get(key)

        return result
