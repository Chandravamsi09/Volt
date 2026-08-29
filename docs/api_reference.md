# Volt REST API Reference

Volt exposes an OpenAPI 3.1 compliant REST API for pipeline management, feature retrieval, model lifecycle management, and real-time predictions.

## Base URL
`/api/v1`

---

## Endpoints

### 1. Authentication & Security
- `POST /auth/register` — Register a new platform user.
- `POST /auth/login` — Authenticate and receive JWT access token.
- `POST /auth/keys` — Generate programmatic API keys.

### 2. Lakehouse & Pipelines
- `GET /pipelines/tables` — List all lakehouse tables with partition metadata.
- `POST /pipelines/tables/ingest` — Ingest raw batch records into lakehouse.
- `POST /pipelines/query` — Execute arbitrary DuckDB OLAP SQL query.

### 3. Feature Store
- `POST /features/entities` — Register primary entity.
- `GET /features/entities` — List entities.
- `POST /features/views` — Create feature view.
- `GET /features/views` — List feature views.
- `POST /features/online/get` — Low-latency sub-5ms feature vector retrieval.
- `POST /features/views/{view_name}/materialize` — Trigger offline-to-online sync.

### 4. Model Registry & Serving
- `GET /models/{name}/versions` — List all model versions.
- `POST /models/{name}/{version}/transition` — Promote stage (`STAGING` -> `PRODUCTION`).
- `POST /inference/predict` — Direct real-time model prediction.
- `POST /inference/endpoints/{endpoint_name}/predict` — Routed prediction with Canary/AB weights.

### 5. LLM & Observability
- `POST /llm/documents/ingest` — Ingest & embed knowledge document.
- `POST /llm/rag/query` — Query contextual RAG knowledge base.
- `POST /llm/agent/workflow` — Execute multi-agent collaborative task.
- `POST /drift/evaluate` — Compute PSI and KS-test drift metrics.
