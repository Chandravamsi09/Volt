# ⚡ Volt — Enterprise AI/ML & Data Lakehouse Platform

<div align="center">

[![CI Pipeline](https://github.com/Chandravamsi09/Volt/actions/workflows/ci.yml/badge.svg)](https://github.com/Chandravamsi09/Volt/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-15_App_Router-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**Production-grade, distributed, cloud-native AI/ML & Data Lakehouse Platform engineered for high-throughput batch/stream ingestion, dual feature store synchronization, automated MLOps model registry & serving, hybrid LLM RAG, and statistical drift observability.**

</div>

---

## 🚀 Key Architectural Capabilities

- **High-Performance Lakehouse**: Polars, PyArrow, and DuckDB analytical query engine operating over partitioned Parquet storage.
- **Dual Feature Store**: Point-in-time (AS-OF) historical feature joins preventing training data leakage, combined with sub-5ms Redis online serving.
- **Production MLOps**: Cryptographically verified model vault (SHA-256 checksums), automated ONNX acceleration, and Canary/AB deployment routing.
- **LLM & Multi-Agent Engine**: Qdrant vector database, hybrid RAG context synthesis, safety guardrails (prompt injection & PII redaction), and multi-agent coordination.
- **Continuous Observability**: Real-time Population Stability Index (PSI) and Kolmogorov-Smirnov (KS-test) drift monitors with automated retraining triggers.
- **Modern Control Plane**: Next.js 15 (React 19) App Router dashboard with visual DAG visualizer, model metrics, and online feature inspector.
- **Developer Experience**: Standalone Python Client SDK (`volt_sdk`) and Typer CLI (`volt`).

---

## 📂 Repository Topology

```
Volt/
├── .github/workflows/          # CI/CD pipelines (Test, Lint, Docker Build, Publish)
├── docker/                     # Dockerfiles (API, Worker, Frontend) & docker-compose.yml
├── helm/                       # Production Kubernetes Helm Chart
├── sdk/python/                 # Python Client SDK (VoltClient)
├── cli/                        # Rich Terminal CLI (volt)
├── backend/
│   ├── app/
│   │   ├── api/v1/             # REST Endpoints (Auth, Pipelines, Features, Models, Serving, RAG, Drift)
│   │   ├── core/               # Async Engine, Security, Settings, Exceptions & Telemetry
│   │   ├── data_engine/        # Connectors, Lakehouse Manager, DuckDB OLAP & Transformers
│   │   ├── feature_store/      # Point-in-Time Offline & Sub-5ms Redis Online Store
│   │   ├── ml_engine/          # Estimators, Distributed Training, Model Vault & ONNX Serving
│   │   ├── llm_engine/         # Vector Store, Embeddings, RAG & Safety Guardrails
│   │   ├── observability/      # Statistical Drift (PSI, KS-Test) & Monitors
│   │   └── workers/            # Celery Background Workers & Schedulers
│   └── tests/                  # Multi-tier Unit, Integration, Data Contract & Drift Suites
├── frontend/                   # Next.js 15, React 19, Tailwind CSS Dashboard
└── docs/                       # Architecture, API Reference & Deployment Specifications
```

---

## ⚡ Quick Start

### 1. Run via Docker Compose (Full Stack)
```bash
docker-compose -f docker/docker-compose.yml up -d
```
- Frontend UI: `http://localhost:3000`
- API Documentation: `http://localhost:8000/api/v1/docs`

### 2. Local Python Development
```bash
pip install -e .[dev,llm]
pytest backend/tests/ -v
volt health
```

---

## 🧪 Comprehensive Test Suite

Volt includes multi-tier test suites verifying:
1. `backend/tests/unit/test_feature_store.py`: Offline AS-OF point-in-time join and sub-5ms Redis caching.
2. `backend/tests/unit/test_ml_estimators.py`: Tabular classifiers and Model Vault stage transitions.
3. `backend/tests/unit/test_drift_detector.py`: Statistical PSI and Kolmogorov-Smirnov shift detectors.
4. `backend/tests/data_validation/test_data_contracts.py`: Great Expectations style contract validator.
5. `backend/tests/integration/test_api_endpoints.py`: End-to-end FastAPI integration testing.

---

## 📄 License
Apache License 2.0. See [LICENSE](LICENSE) for details.
