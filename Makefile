SHELL := /bin/bash
export PATH := $(HOME)/.local/bin:$(PATH)

UV := $(HOME)/.local/bin/uv
PYTEST := $(UV) run pytest
RUFF := $(UV) run ruff
MYPY := $(UV) run mypy
UVICORN := $(UV) run uvicorn
DOCKER_COMPOSE := docker compose -f docker/docker-compose.yml

.PHONY: help install setup dev api frontend db test test-unit test-integration lint format typecheck check clean docker-up docker-down docker-build docker-logs run-all stop-all

# ── Meta ──────────────────────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────
install: ## Install backend dependencies
	$(UV) sync --all-extras

install-frontend: ## Install frontend dependencies
	cd frontend && pnpm install

setup: ## Full first-time setup (backend + frontend + .env)
	@test -f .env || cp .env.example .env && echo "Created .env from .env.example"
	$(UV) sync --all-extras
	cd frontend && pnpm install
	@echo ""
	@echo "--- Setup complete ---"
	@echo "Edit .env to add your API keys, then run: make run-all"

# ── Run ───────────────────────────────────────────────────────────────
db: ## Start database (PostgreSQL + pgvector on port 4343)
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database..."
	@$(DOCKER_COMPOSE) exec db pg_isready -U vectraxis -q && echo "Database ready on port 4343" || echo "Database starting..."

api: ## Start backend API server (port 8000)
	$(UVICORN) vectraxis.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

frontend: ## Start frontend dev server (port 3000)
	cd frontend && pnpm dev

dev: ## Start API with hot reload (requires DB running)
	$(UVICORN) vectraxis.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload

run-all: ## Start everything: database + API + frontend
	@echo "Starting database..."
	$(DOCKER_COMPOSE) up -d db
	@echo "Waiting for database to be healthy..."
	@until $(DOCKER_COMPOSE) exec db pg_isready -U vectraxis -q 2>/dev/null; do sleep 1; done
	@echo "Database ready on port 4343"
	@echo "Starting API server on port 8000..."
	$(UVICORN) vectraxis.api.app:create_app --factory --host 0.0.0.0 --port 8000 --reload &
	@sleep 2
	@echo "Starting frontend on port 3000..."
	cd frontend && pnpm dev &
	@sleep 2
	@echo ""
	@echo "=== Vectraxis is running ==="
	@echo "  API:       http://localhost:8000"
	@echo "  Dashboard: http://localhost:3000"
	@echo "  Swagger:   http://localhost:8000/docs"
	@echo "  Scalar:    http://localhost:8000/scalar"
	@echo "  Database:  localhost:4343"
	@echo ""
	@echo "Run 'make stop-all' to stop everything"

stop-all: ## Stop everything: database + API + frontend
	@echo "Stopping services..."
	-@pkill -f "uvicorn vectraxis" 2>/dev/null || true
	-@pkill -f "vite" 2>/dev/null || true
	$(DOCKER_COMPOSE) down
	@echo "All services stopped"

# ── Docker ────────────────────────────────────────────────────────────
docker-up: ## Start all services via Docker (DB + API)
	$(DOCKER_COMPOSE) up -d --build

docker-down: ## Stop all Docker services
	$(DOCKER_COMPOSE) down

docker-build: ## Rebuild Docker images
	$(DOCKER_COMPOSE) build --no-cache

docker-logs: ## Tail Docker logs
	$(DOCKER_COMPOSE) logs -f

# ── Testing ───────────────────────────────────────────────────────────
test: ## Run all unit tests
	$(PYTEST) tests/unit -v

test-unit: ## Run unit tests (alias)
	$(PYTEST) tests/unit -v

test-integration: ## Run integration tests (requires DB)
	$(PYTEST) tests/integration -v -m integration

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/unit --cov=vectraxis --cov-report=term-missing

# ── Code Quality ──────────────────────────────────────────────────────
lint: ## Run linter
	$(RUFF) check .

format: ## Format code
	$(RUFF) format .

typecheck: ## Run type checker
	$(MYPY) src/

check: ## Run all checks: lint + format check + typecheck + tests
	$(RUFF) check .
	$(RUFF) format --check .
	$(PYTEST) tests/unit -q
	@echo ""
	@echo "All checks passed"

# ── Cleanup ───────────────────────────────────────────────────────────
clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage
	@echo "Cleaned"
