# Developer Guide

This guide orients contributors to the repository structure, devcontainer vs runtime, and common developer commands.

## Glossary

For complete domain terminology (FEC cycles, file types, layers, etc.), see [CONTEXT.md](../../CONTEXT.md).

Brief definitions of developer terms:

- **ADR (Architecture Decision Record):** A short document that captures a significant architectural decision, its context, and its consequences. ADRs are stored in `docs/adr/` and are numbered sequentially. See ADR 0001–0009.
- **Devcontainer:** A containerized development environment defined in `.devcontainer/`. Opening this repository in VS Code or GitHub Codespaces automatically builds and starts the devcontainer, giving every contributor an identical editor environment with all tools pre-installed.
- **DATA_DIR:** An environment variable that points to the root of the local data directory (`/workspaces/money-trail/data` in devcontainer, `/app/data` in the runtime compose stack). Scripts and DAGs use this variable instead of hardcoded paths so the same code works in both environments.
- **Duck Lake:** Parquet files in `data/duckdb/` that serve as primary immutable storage for FEC data, queryable via DuckDB external tables. See ADR 0009.
- **Raw Schema:** DuckDB external tables (prefixed `raw_`) pointing to parquet files. Owned by Airflow. See ADR 0006.
- **Staging Schema:** dbt-managed views (prefixed `stg_`) that clean and alias raw data. See ADR 0004.
- **Marts Schema:** dbt-managed views aggregating or filtering staging data for analytics. See ADR 0006.

Key locations:
- ADRs: docs/adr/
- FEC imports: docs/imports/fec-data/
- Notebooks: notebooks/
- Runbooks: docs/runbooks/
- Compose/runtime: docker-compose.yml and .devcontainer/docker-compose.yml

## Dev vs Runtime

- Devcontainer (interactive editor): uses .devcontainer/devcontainer.json; environment variables set for development include DATA_DIR (set to /workspaces/money-trail/data).
- Runtime (Airflow compose): uses docker-compose.yml; services mount ./data to /app/data and have DATA_DIR=/app/data.

## Common commands

- Launch local runtime: `docker compose -f docker-compose.yml up --detach --build`
- Stop runtime: `docker compose -f docker-compose.yml down`
- Rebuild a service: `docker compose -f docker-compose.yml build <service>`
- Run dbt models: `cd dbt && dbt run`
- Run dbt tests: `cd dbt && dbt test`

See docs/runbooks/README.md for more operational notes.
