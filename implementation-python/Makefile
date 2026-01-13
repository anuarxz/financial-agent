.PHONY: help setup install env db run api docker-cli docker-api docker-down clean

# Variables
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)/Scripts/python
	PIP := $(VENV)/Scripts/pip
endif

# Colors
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help: 
	@echo ""
	@echo "Financial Agent - Available Commands"
	@echo "====================================="
	@echo ""
	@echo "$(CYAN)Docker (recommended):$(RESET)"
	@echo "  make docker-cli    Start PostgreSQL + CLI interactivo"
	@echo "  make docker-api    Start PostgreSQL + API REST"
	@echo "  make docker-down   Stop all containers"
	@echo ""
	@echo "$(CYAN)Local development:$(RESET)"
	@echo "  make setup         Full setup (venv + deps + .env)"
	@echo "  make db            Start only PostgreSQL in Docker"
	@echo "  make run           Run CLI (requires: make db)"
	@echo "  make api           Run API (requires: make db)"
	@echo ""
	@echo "$(CYAN)Utilities:$(RESET)"
	@echo "  make install       Install dependencies only"
	@echo "  make clean         Remove venv and cache files"
	@echo ""

# =============================================================================
# Docker 
# =============================================================================

docker-cli: env ## PostgreSQL + CLI 
	@echo "$(GREEN)Starting Financial Agent CLI...$(RESET)"
	docker-compose run --rm cli

docker-api: env ## PostgreSQL + API
	@echo "$(GREEN)Starting Financial Agent API on http://localhost:8000$(RESET)"
	docker-compose up --build

docker-down: 
	docker-compose down

# =============================================================================
# Local 
# =============================================================================

setup: venv install env db-init ## Inicialización en local
	@echo ""
	@echo "$(GREEN)Setup complete!$(RESET)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit .env and add your API key (GEMINI_API_KEY, OPENAI_API_KEY, etc.)"
	@echo "  2. Run: make run   (start CLI)"
	@echo ""

venv: 
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(CYAN)Creating virtual environment...$(RESET)"; \
		python -m venv $(VENV); \
	fi

install: venv 
	@echo "$(CYAN)Installing dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

env: 
	@if [ ! -f ".env" ]; then \
		echo "$(CYAN)Creating .env from .env.example...$(RESET)"; \
		cp .env.example .env; \
		echo "$(YELLOW)Remember to edit .env and add your API key!$(RESET)"; \
	fi

db: ## Contenedor Postgres
	@echo "$(CYAN)Starting PostgreSQL...$(RESET)"
	docker-compose up -d db
	@echo "$(GREEN)PostgreSQL running on localhost:5433$(RESET)"

db-init: db ## Esquema bbdd
	@echo "$(CYAN)Waiting for PostgreSQL to be ready...$(RESET)"
	@sleep 3
	$(PYTHON) scripts/init_db.py

run: ## CLI local
	$(PYTHON) cli.py

api: ## API local
	$(PYTHON) main.py

# =============================================================================
# Clean
# =============================================================================

clean: 
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/**/__pycache__
	rm -rf .pytest_cache
	@echo "$(GREEN)Cleaned!$(RESET)"
