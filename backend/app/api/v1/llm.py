"""
LLM, Vector Search, RAG & Multi-Agent API Endpoints
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.llm_engine.agents.agent_orchestrator import agent_orchestrator
from backend.app.llm_engine.rag.retriever import rag_pipeline
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/llm", tags=["LLM & Vector Engine"])


class DocumentIngestRequest(BaseModel):
    doc_id: str
    title: str
    content: str


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3


class AgentWorkflowRequest(BaseModel):
    task: str
    dataset_summary: Optional[Dict[str, Any]] = None


@router.post("/documents/ingest", response_model=StandardResponse[Dict[str, Any]])
async def ingest_document(payload: DocumentIngestRequest):
    """Ingest, chunk, embed, and store document in vector collection."""
    count = rag_pipeline.ingest_document(
        doc_id=payload.doc_id,
        title=payload.title,
        content=payload.content,
    )
    return StandardResponse(
        data={"doc_id": payload.doc_id, "chunks_indexed": count},
        message="Document indexed in vector store",
    )


@router.post("/rag/query", response_model=StandardResponse[Dict[str, Any]])
async def query_rag(payload: RAGQueryRequest):
    """Execute contextual RAG query with safety guardrails."""
    res = rag_pipeline.query(user_query=payload.query, top_k=payload.top_k)
    return StandardResponse(
        data={
            "query": res.query,
            "answer": res.synthesized_answer,
            "context_chunks": res.context_chunks,
            "sources": res.sources,
            "passed_guardrails": res.passed_guardrails,
        },
        message="RAG query executed",
    )


@router.post("/agent/workflow", response_model=StandardResponse[Dict[str, Any]])
async def trigger_agent_workflow(payload: AgentWorkflowRequest):
    """Run collaborative multi-agent data science orchestration."""
    summary = payload.dataset_summary or {"rows": 10000, "target": "is_fraud"}
    res = agent_orchestrator.run_data_science_workflow(
        task_description=payload.task,
        dataset_summary=summary,
    )
    return StandardResponse(
        data={
            "task": res.task,
            "status": res.status,
            "steps": [s.__dict__ for s in res.steps],
            "final_output": res.final_output,
        },
        message="Agent workflow executed",
    )

class GuardrailValidationRequest(BaseModel):
    prompt: str


@router.post("/guardrails/validate", response_model=StandardResponse[Dict[str, Any]])
async def validate_guardrails(payload: GuardrailValidationRequest):
    """Verify and audit user input against injection attacks and PII disclosure."""
    guard = InputGuardrail()
    report = guard.scan_and_audit(payload.prompt)
    return StandardResponse(data=report, message="Guardrail audit evaluation completed.")
