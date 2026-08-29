"""
Volt Python Client SDK
"""

from typing import Any, Dict, List, Optional
import httpx


class VoltClient:
    """Synchronous and asynchronous Python client for Volt AI/ML & Data Platform."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.token = None
        self._headers = {"Content-Type": "application/json"}
        if api_key:
            self._headers["X-API-Key"] = api_key

    def login(self, username_or_email: str, password: str) -> str:
        """Authenticate user and store bearer token."""
        url = f"{self.base_url}/api/v1/auth/login"
        resp = httpx.post(url, json={"username_or_email": username_or_email, "password": password})
        resp.raise_for_status()
        data = resp.json()["data"]
        self.token = data["access_token"]
        self._headers["Authorization"] = f"Bearer {self.token}"
        return self.token

    def health(self) -> Dict[str, Any]:
        """Check server health status."""
        resp = httpx.get(f"{self.base_url}/health", headers=self._headers)
        resp.raise_for_status()
        return resp.json()["data"]

    def list_tables(self) -> List[Dict[str, Any]]:
        """List all lakehouse tables."""
        resp = httpx.get(f"{self.base_url}/api/v1/pipelines/tables", headers=self._headers)
        resp.raise_for_status()
        return resp.json()["data"]

    def query_sql(self, sql: str) -> Dict[str, Any]:
        """Execute OLAP SQL query."""
        resp = httpx.post(f"{self.base_url}/api/v1/pipelines/query", json={"sql": sql}, headers=self._headers)
        resp.raise_for_status()
        return resp.json()["data"]

    def get_online_features(self, view_name: str, entity_key: str, entity_ids: List[str]) -> Dict[str, Any]:
        """Fetch online features."""
        url = f"{self.base_url}/api/v1/features/online/get"
        resp = httpx.post(
            url,
            json={"view_name": view_name, "entity_key": entity_key, "entity_ids": entity_ids},
            headers=self._headers,
        )
        resp.raise_for_status()
        return resp.json()["data"]

    def predict(self, model_name: str, version: str, features: List[List[float]]) -> Dict[str, Any]:
        """Execute real-time model prediction."""
        url = f"{self.base_url}/api/v1/inference/predict"
        resp = httpx.post(
            url,
            json={"model_name": model_name, "version": version, "features": features},
            headers=self._headers,
        )
        resp.raise_for_status()
        return resp.json()["data"]

    def query_rag(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Query RAG knowledge base."""
        url = f"{self.base_url}/api/v1/llm/rag/query"
        resp = httpx.post(url, json={"query": query, "top_k": top_k}, headers=self._headers)
        resp.raise_for_status()
        return resp.json()["data"]
