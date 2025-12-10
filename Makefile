.PHONY: dev migrate seed seed-nosql docker-up docker-down help

help:
	@echo "Available commands:"
	@echo "  make dev          - Run the REST API development server (starts Docker)"
	@echo "  make migrate      - Run SQL migrations (starts Docker)"
	@echo "  make seed         - Run SQL seeders (starts Docker)"
	@echo "  make seed-nosql   - Run NoSQL seeders (starts Docker)"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"

dev:
	uv run python src/apps/rest_api/main.py

migrate: docker-up
	uv run python src/core/database/sql/migrate.py

seed: docker-up
	uv run python src/core/database/sql/seeder.py

seed-nosql: docker-up
	uv run python src/core/database/nosql/seeder.py

docker-up:
	docker compose up -d --wait

docker-down:
	docker compose down
