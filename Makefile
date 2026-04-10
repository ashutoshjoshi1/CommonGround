.PHONY: help setup dev lint format test seed infra-up docker-up docker-down

help:
	@echo "CommonGround commands"
	@echo "  make setup      Install JS and Python dependencies"
	@echo "  make dev        Run web, api, worker"
	@echo "  make lint       Run linters"
	@echo "  make format     Run formatters"
	@echo "  make test       Run unit tests"
	@echo "  make seed       Seed local database"
	@echo "  make infra-up   Start only infra dependencies (Postgres, Redis, MinIO)"
	@echo "  make docker-up  Start full stack with docker compose"
	@echo "  make docker-down Stop docker compose stack"

setup:
	npm install
	cd apps/api && python -m pip install -r requirements-dev.txt

dev:
	npm run dev

lint:
	npm run lint

format:
	npm run format

test:
	npm run test

seed:
	npm run seed

infra-up:
	docker compose -f infra/docker-compose.yml up -d postgres redis minio

docker-up:
	docker compose -f infra/docker-compose.yml up -d --build

docker-down:
	docker compose -f infra/docker-compose.yml down -v
