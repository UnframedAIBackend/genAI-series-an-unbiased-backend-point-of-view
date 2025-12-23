PORT ?= 8000
WORKERS ?= 4

.PHONY: help up down restart logs clean install-deps rag-worker build dev infra migrate-sql migrate-nosql

help:
	@echo "Available commands:"
	@echo "  make build           - Build Docker images"
	@echo "  make up              - Start all services (production)"
	@echo "  make infra           - Start only infrastructure services (db, temporal, etc)"
	@echo "  make dev             - Start all services (development with hot-reload)"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo "  make logs            - View logs from all services"
	@echo "  make logs-api        - View API logs"
	@echo "  make logs-worker     - View worker logs"
	@echo "  make clean           - Remove all containers and volumes"
	@echo "  make install-deps    - Install Python dependencies locally"
	@echo "  make rag-worker      - Run Temporal worker locally"
	@echo "  make api             - Run API server locally"
	@echo "  make temporal-ui     - Open Temporal UI in browser"
	@echo "  make shell-api       - Shell into API container"
	@echo "  make shell-worker    - Shell into worker container"
	@echo "  make migrate-sql     - Migrate SQL database"
	@echo "  make migrate-nosql   - Migrate NoSQL database"

build:
	docker compose build

up:
	docker compose --profile app up -d

docker-up:
	docker compose up --build -d postgres mongodb ollama mlflow temporal temporal-ui rag-worker mongo_migrator postgres_migrator

preload:
	uv run python src/scripts/preload.py

dev: preload docker-up
	uv run python src/apps/rest_api/main.py

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f rag-worker

clean:
	docker compose down -v
	docker system prune -f

install-deps:
	uv sync

rag-worker:
	python src/core/features/rag/workflows/worker.py

migrate-sql:
	python src/core/database/sql/migrate.py

migrate-nosql:
	python src/core/database/nosql/migrate.py

api:
	python -m uvicorn src.apps.rest_api.main:app --host 0.0.0.0 --port $(PORT) --reload

api-prod:
	python -m uvicorn src.apps.rest_api.main:app --host 0.0.0.0 --port $(PORT) --workers $(WORKERS)

temporal-ui:
	open http://localhost:8080

shell-api:
	docker compose exec api /bin/bash
