# Volt Production Deployment Guide

## 1. Local Full-Stack Cluster (Docker Compose)

Spin up the entire platform (Postgres, Redis, Qdrant, MinIO, API, Worker, Next.js Frontend) in one command:

```bash
docker-compose -f docker/docker-compose.yml up -d --build
```

- **Frontend Dashboard**: `http://localhost:3000`
- **FastAPI OpenAPI Docs**: `http://localhost:8000/api/v1/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`
- **MinIO Console**: `http://localhost:9001`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

---

## 2. Kubernetes Deployment (Helm)

Deploy to production Kubernetes clusters:

```bash
# Add Helm chart values override
helm upgrade --install volt ./helm/volt \
  --namespace volt-prod \
  --create-namespace \
  --values ./helm/volt/values.yaml
```

---

## 3. Standalone Python Development Setup

```bash
# Clone and install dependencies
git clone https://github.com/Chandravamsi09/Volt.git
cd Volt

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with development & LLM extras
pip install -e .[dev,llm]

# Run tests
pytest backend/tests/ -v --cov=backend/app

# Run CLI
volt health
```
