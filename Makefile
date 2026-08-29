.PHONY: help install dev test lint format run-api run-worker run-frontend docker-up docker-down

help:
	@echo "Volt Platform Development Commands:"
	@echo "  make install        - Install python dependencies and CLI"
	@echo "  make dev            - Start all services locally (Docker + API)"
	@echo "  make test           - Run full test suite with coverage"
	@echo "  make lint           - Run linter and typechecks"
	@echo "  make format         - Auto-format codebase"
	@echo "  make run-api        - Start FastAPI backend server"
	@echo "  make run-worker     - Start Celery asynchronous worker"
	@echo "  make run-frontend   - Start Next.js frontend dev server"
	@echo "  make docker-up      - Spin up docker-compose services"
	@echo "  make docker-down    - Tear down docker-compose services"

install:
	pip install -e .[dev,llm]

test:
	pytest backend/tests --cov=backend/app --cov-report=term-missing

lint:
	ruff check .
	mypy backend/app

format:
	ruff format .

run-api:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-worker:
	celery -A backend.app.workers.celery_app worker --loglevel=info

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down
