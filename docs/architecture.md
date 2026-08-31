# Volt System Architecture & Technical Specification

## Overview

Volt is a cloud-native, distributed Enterprise AI/ML & Data Platform designed to bridge high-throughput analytical data lakehouses with real-time, low-latency machine learning inference and LLM orchestration.

---

## High-Level Topology

```
+-----------------------------------------------------------------------------+
|                                Control Plane                                |
|  Next.js 15 (React 19) Dashboard  |  Typer CLI (volt)  |  Python SDK Client |
+---------------------------------------+-------------------------------------+
                                        | HTTP / REST / gRPC
                                        v
+-----------------------------------------------------------------------------+
|                           FastAPI Core Gateway API                          |
|  Auth / RBAC  |  Pipeline API  |  Feature Store API  |  Inference Gateway   |
+-------------------+--------------------+--------------------+---------------+
                    |                    |                    |
                    v                    v                    v
+-----------------------+ +-----------------------+ +-----------------------+
|   Data Lakehouse      | |     Feature Store     | |   ML Engine & Vault   |
| - Polars Ingestion    | | - Offline Parquet     | | - Model Registry      |
| - DuckDB OLAP Engine  | | - Redis Online Store  | | - ONNX Serving Graph  |
| - Parquet Partitions  | | - Sync Materializer   | | - Drift Monitor (PSI) |
+-----------------------+ +-----------------------+ +-----------------------+
                    ^                    ^                    ^
                    |                    |                    |
+-----------------------------------------------------------------------------+
|                     Distributed Asynchronous Workers                        |
|  Celery Workers  |  Redis Streams  |  Periodic Beat Drift Audits            |
+-----------------------------------------------------------------------------+
```

---

## Subsystems

### 1. Data Engine & Lakehouse
- **Polars & PyArrow**: Multi-threaded vector processing for sub-second ingestion and feature transformations.
- **DuckDB**: In-process OLAP engine supporting point-in-time SQL queries over Parquet partitions.
- **Contract Enforcement**: Declarative schema contracts with quarantine partitioning.

### 2. Dual Feature Store
- **Offline Store**: Point-in-time correct (AS-OF) historical feature joins preventing target leakage during training.
- **Online Store**: Sub-5ms Redis key-value store optimized with bulk multi-get (`MGET`).
- **Materialization Engine**: Asynchronous Celery daemon keeping Redis synchronized with the latest lakehouse snapshots.

### 3. Model Vault & Real-Time Serving
- **Cryptographic Verification**: SHA-256 model weight checksums.
- **ONNX Accelerated Inference**: Zero-copy execution runtime.
- **Traffic Router**: Canary rollouts (e.g. 90/10), A/B testing, and shadow traffic replication.

### 4. Vector & LLM Engine
- **Hybrid RAG**: Semantic text search with Qdrant vector index.
- **Guardrails**: Prompt injection defense and automated PII redaction.
- **Multi-Agent Orchestrator**: Planner, Analyst, and ML Architect agents.

### 5. Observability & Drift Monitoring
- **Statistical Detector**: Population Stability Index (PSI) & Kolmogorov-Smirnov (KS) test.
- **Automated Retraining & Webhooks**: Drift triggers activating Celery training workflows and dispatching Slack/PagerDuty incident webhooks.
