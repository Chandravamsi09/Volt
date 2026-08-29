"""
Vector Store & Similarity Search Manager (Qdrant & In-Memory Fallback)
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
from backend.app.core.config import settings

logger = logging.getLogger("volt.vector_store")


@dataclass
class SearchResult:
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class VectorStoreManager:
    """Vector database manager supporting Qdrant with in-memory fallback."""

    def __init__(self):
        self._collections: Dict[str, Dict[str, Any]] = {}  # In-memory storage fallback
        self._qdrant_client = None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        self._collections[collection_name] = {
            "vector_size": vector_size,
            "documents": [],  # List of {id, vector, text, metadata}
        }
        return True

    def insert_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],  # [{id, vector, text, metadata}]
    ) -> int:
        if collection_name not in self._collections:
            self.create_collection(collection_name)

        col = self._collections[collection_name]
        for doc in documents:
            col["documents"].append({
                "id": str(doc.get("id")),
                "vector": np.array(doc["vector"], dtype=np.float32),
                "text": str(doc.get("text", "")),
                "metadata": doc.get("metadata", {}),
            })
        return len(documents)

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> List[SearchResult]:
        if collection_name not in self._collections:
            return []

        col = self._collections[collection_name]
        q_vec = np.array(query_vector, dtype=np.float32)

        scored_docs = []
        for doc in col["documents"]:
            score = self._cosine_similarity(q_vec, doc["vector"])
            if score >= score_threshold:
                scored_docs.append(SearchResult(
                    id=doc["id"],
                    score=round(score, 4),
                    text=doc["text"],
                    metadata=doc["metadata"],
                ))

        scored_docs.sort(key=lambda x: x.score, reverse=True)
        return scored_docs[:top_k]


vector_store = VectorStoreManager()
