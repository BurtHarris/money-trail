.PHONY: help setup dev-up dev-down airflow-up airflow-down airflow-logs airflow-reset \
        dbt-debug dbt-run dbt-test lint format test clean

SHELL := /bin/bash
DATA_DIR ?= ./data

help:
	@echo "money-trail development commands"
	@echo ""
	@echo "Setup & Environment:"
	@echo "  make setup              Initialize local development environment"
	@echo ""
	@echo "Development Container:"
	@echo "  make dev-up             Start devcontainer workspace"
	@echo "  make dev-down           Stop devcontainer workspace"
	@echo ""
	@echo "Airflow Services (inside devcontainer):"
	@echo "  make airflow-up         Start Airflow runtime services (postgres, webserver, scheduler)"
	@echo "  make airflow-down       Stop Airflow services"
	@echo "  make airflow-logs       Tail Airflow webserver logs"
	@echo "  make airflow-reset      Reset Airflow metadata database (destroys data!)"
	@echo ""
	@echo "dbt Commands (inside devcontainer):"
	@echo "  make dbt-debug          Test dbt DuckDB connection"
	@echo "  make dbt-run            Run dbt models (staging and marts)"
	@echo "  make dbt-test           Run dbt data quality tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint               Run ruff linter"
	@echo "  make format             Format code with ruff"
	@echo "  make test               Run pytest tests"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean              Remove local artifacts (.airflow, logs, caches)"

setup:
	@echo "Initializing development environment..."
	mkdir -p .airflow logs $(DATA_DIR)/raw $(DATA_DIR)/duckdb
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env from template"; \
	fi
	@echo "✓ Setup complete. Run 'make dev-up' to start devcontainer"

dev-up:
	@echo "Starting devcontainer workspace..."
	cd .devcontainer && docker-compose up -d workspace
	@echo "✓ Devcontainer is running"

dev-down:
	@echo "Stopping devcontainer workspace..."
	cd .devcontainer && docker-compose down
	@echo "✓ Devcontainer stopped"

airflow-up:
	@echo "Starting Airflow services..."
	docker-compose up -d postgres airflow-init airflow-webserver airflow-scheduler
	@echo "Waiting for Airflow to be healthy..."
	@for i in {1..30}; do \
		if curl -sf http://localhost:8080/api/v2/monitor/health >/dev/null 2>&1; then \
			echo "✓ Airflow ready at http://localhost:8080 (devadmin/devadmin)"; \
			exit 0; \
		fi; \
		sleep 2; \
	done; \
	echo "✗ Airflow failed to start"; \
	exit 1

airflow-down:
	@echo "Stopping Airflow services..."
	docker-compose down
	@echo "✓ Airflow services stopped"

airflow-logs:
	@docker-compose logs -f airflow-webserver

airflow-reset:
	@echo "WARNING: This will destroy all Airflow metadata!"
	@read -p "Continue? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	rm -rf .airflow logs/*
	@echo "✓ Airflow reset complete"

dbt-debug:
	@echo "Testing dbt DuckDB connection..."
	cd dbt && dbt debug

dbt-run:
	@echo "Running dbt models..."
	cd dbt && dbt run

dbt-test:
	@echo "Running dbt tests..."
	cd dbt && dbt test

lint:
	@echo "Running ruff linter..."
	ruff check dags scripts tests

format:
	@echo "Formatting code with ruff..."
	ruff format dags scripts tests
	ruff check --fix dags scripts tests

test:
	@echo "Running pytest..."
	pytest -v tests/

clean:
	@echo "Cleaning up artifacts..."
	rm -rf .airflow logs/* .pytest_cache .ruff_cache __pycache__ dags/__pycache__ scripts/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup complete"

.DEFAULT_GOAL := help
