COMPOSE ?= docker compose
PORT ?= 8000
WORKERS ?= 4

.PHONY: help up down restart logs clean install-deps rag-worker build dev infra migrate-sql migrate-nosql lint lint-fix

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
	@echo "  make lint            - Run Ruff linter"
	@echo "  make lint-fix        - Run Ruff and fix safe issues"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) --profile app up -d

docker-up-sql:
	$(COMPOSE) up --build -d postgres ollama mlflow temporal temporal-ui rag-worker postgres_migrator

docker-up-nosql:
	# mlflow
	$(COMPOSE) up --build -d postgres ollama mongodb temporal temporal-ui rag-worker mongo_migrator

preload:
	uv run python src/scripts/preload.py

dev: preload docker-up
	uv run python src/apps/rest_api/main.py

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

logs-api:
	$(COMPOSE) logs -f api

logs-worker:
	$(COMPOSE) logs -f rag-worker

clean:
	$(COMPOSE) down -v
	docker system prune -f

install-deps:
	uv sync

rag-worker:
	python src/core/features/rag/workflows/worker.py

migrate-sql:
	python src/core/database/sql/migrate.py

migrate-nosql:
	python src/core/database/nosql/migrate.py

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

api:
	python -m uvicorn src.apps.rest_api.main:app --host 0.0.0.0 --port $(PORT) --reload

api-prod:
	python -m uvicorn src.apps.rest_api.main:app --host 0.0.0.0 --port $(PORT) --workers $(WORKERS)

temporal-ui:
	open http://localhost:8080

shell-api:
	$(COMPOSE) exec api /bin/bash
