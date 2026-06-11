# Developer Guide

This guide orients contributors to the repository structure, devcontainer vs runtime, and common developer commands.

## Glossary

- **ADR (Architecture Decision Record):** A short document that captures a significant architectural decision, its context, and its consequences. ADRs are stored in `docs/adr/` and are numbered sequentially. They are meant to be read in order to understand *why* the project is structured the way it is.
- **Devcontainer:** A containerized development environment defined in `.devcontainer/`. Opening this repository in VS Code or GitHub Codespaces automatically builds and starts the devcontainer, giving every contributor an identical editor environment with all tools pre-installed.
- **DATA_DIR:** An environment variable that points to the root of the local data directory (`/workspaces/money-trail/data` in devcontainer, `/app/data` in the runtime compose stack). Scripts and DAGs use this variable instead of hardcoded paths so the same code works in both environments.
- **Duck Lake:** The project's analytic data tier — a collection of Parquet files queryable via DuckDB, stored under `data/ducklake/`.

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
