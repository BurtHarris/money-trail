# Developer Guide

This guide orients contributors to the repository structure, devcontainer vs runtime, and common developer commands.

Key locations:
- ADRs: docs/adr/ (see ADR 0001, ADR 0002)
- Restructuring plan: docs/architecture/repository-restructuring-plan.md
- FEC imports: docs/imports/fec-data/
- Notebooks: notebooks/
- Compose/runtime: docker-compose.yml and .devcontainer/docker-compose.yml

Dev vs Runtime
- Devcontainer (interactive editor): uses .devcontainer/devcontainer.json; environment variables set for development include DATA_DIR (set to /workspaces/money-trail/data).
- Runtime (Airflow compose): uses docker-compose.yml; services mount ./data to /app/data and have DATA_DIR=/app/data.

Common commands
- Launch local runtime: docker compose -f docker-compose.yml up --detach --build
- Stop runtime: docker compose -f docker-compose.yml down
- Rebuild a service: docker compose -f docker-compose.yml build <service>

See docs/runbooks/README.md for more operational notes.
