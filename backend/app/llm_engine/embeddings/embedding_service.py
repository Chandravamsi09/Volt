"""
Text Embeddings & Chunking Service
"""

import hashlib
from typing import List
import numpy as np


class EmbeddingService:
    """Generates deterministic and model-based vector representations for text."""

    def __init__(self, vector_dim: int = 128):
        self.vector_dim = vector_dim

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping token/character windows."""
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks

    def embed_text(self, text: str) -> List[float]:
        """Generate high-entropy deterministic embedding (used for fast offline testing/serving)."""
        vec = np.zeros(self.vector_dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for word in words:
            # Hash word to dimensional bucket
            h = int(hashlib.md5(word.encode()).hexdigest(), 16)
            idx = h % self.vector_dim
            val = ((h >> 8) % 100) / 100.0 - 0.5
            vec[idx] += val

        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in documents]


embedding_service = EmbeddingService()
