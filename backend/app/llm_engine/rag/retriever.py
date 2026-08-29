"""
Retrieval-Augmented Generation (RAG) Context Synthesizer
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from backend.app.llm_engine.embeddings.embedding_service import embedding_service
from backend.app.llm_engine.guardrails.input_guard import guardrail
from backend.app.llm_engine.vector_store.qdrant_manager import vector_store


@dataclass
class RAGResponse:
    query: str
    context_chunks: List[str]
    synthesized_answer: str
    sources: List[Dict[str, Any]]
    passed_guardrails: bool


class RAGPipeline:
    """End-to-End RAG query pipeline with document indexing and context retrieval."""

    def __init__(self, collection_name: str = "kb_documents"):
        self.collection_name = collection_name

    def ingest_document(self, doc_id: str, title: str, content: str) -> int:
        """Ingest, chunk, embed, and store document in vector database."""
        chunks = embedding_service.chunk_text(content, chunk_size=300, overlap=30)
        docs_to_insert = []

        for i, chunk in enumerate(chunks):
            vec = embedding_service.embed_text(chunk)
            docs_to_insert.append({
                "id": f"{doc_id}_chunk_{i}",
                "vector": vec,
                "text": chunk,
                "metadata": {"doc_id": doc_id, "title": title, "chunk_index": i},
            })

        return vector_store.insert_documents(self.collection_name, docs_to_insert)

    def query(self, user_query: str, top_k: int = 3) -> RAGResponse:
        # Guardrail check
        guard_res = guardrail.sanitize(user_query)
        if not guard_res.passed:
            return RAGResponse(
                query=user_query,
                context_chunks=[],
                synthesized_answer="Query rejected due to safety violations: " + ", ".join(guard_res.violations),
                sources=[],
                passed_guardrails=False,
            )

        query_vec = embedding_service.embed_text(guard_res.sanitized_text)
        search_results = vector_store.search(self.collection_name, query_vec, top_k=top_k)

        context_texts = [res.text for res in search_results]
        sources = [res.metadata for res in search_results]

        # Synthesize answer from retrieved chunks
        if context_texts:
            joined_context = " ".join(context_texts)
            synthesized = f"Based on knowledge sources: {joined_context[:400]}..."
        else:
            synthesized = "No relevant context found in knowledge base."

        return RAGResponse(
            query=user_query,
            context_chunks=context_texts,
            synthesized_answer=synthesized,
            sources=sources,
            passed_guardrails=True,
        )


rag_pipeline = RAGPipeline()
