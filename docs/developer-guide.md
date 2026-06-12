# Developer Guide

This guide orients contributors to the repository structure, devcontainer vs runtime, and common developer commands.

## VS Code hotkeys (layout first)

- `Ctrl+K`, then `Z`: toggle Zen Mode (focus on editor)
- `Esc`, `Esc`: exit Zen Mode
- `F11`: toggle full screen
- `Ctrl+B`: toggle Side Bar
- `Ctrl+J`: toggle bottom Panel (Terminal/Problems/Output)
- `Ctrl+\\`: split editor
- `Ctrl+1` / `Ctrl+2` / `Ctrl+3`: focus editor group 1/2/3
- `F5`: run selected profile with debugger (when supported)
- `Ctrl+F5`: run selected profile without debugger

**Quick Links**: See [README.md](../README.md) for project overview. See [CONTEXT.md](../CONTEXT.md) for domain glossary and architecture terminology. See [docs/architecture/repository-restructuring-plan.md](./architecture/repository-restructuring-plan.md) for restructuring target-state contract. See [docs/architecture/dev-vs-runtime-topology.md](./architecture/dev-vs-runtime-topology.md) for environment boundaries. See [docs/architecture/data-tier-path-contract.md](./architecture/data-tier-path-contract.md) for data path ownership rules. See [docs/adr/README.md](./adr/README.md) for all Architecture Decision Records.

For complete domain terminology (FEC cycles, file types, layers, etc.), see [CONTEXT.md](../../CONTEXT.md).

Brief definitions of developer terms:

- **ADR (Architecture Decision Record):** A short document that captures a significant architectural decision, its context, and its consequences. ADRs are stored in `docs/adr/` and are numbered sequentially. See ADR 0001–0009.
- **Devcontainer:** A containerized development environment defined in `.devcontainer/`. Opening this repository in VS Code or GitHub Codespaces automatically builds and starts the devcontainer, giving every contributor an identical editor environment with all tools pre-installed.
- **DATA_DIR:** An environment variable that points to the root of the local data directory (`/workspaces/money-trail/data` in devcontainer, `/app/data` in the runtime compose stack). Scripts and DAGs use this variable instead of hardcoded paths so the same code works in both environments.
- **Duck Lake:** Parquet files in `data/ducklake/` (target state) serving as primary immutable storage for FEC data. During migration, `data/duckdb/` remains a compatibility/query surface. See ADR 0009 and the data-tier path contract.
- **Raw Schema:** DuckDB external tables (prefixed `raw_`) pointing to parquet files. Owned by Airflow. See ADR 0006.
- **Staging Schema:** dbt-managed views (prefixed `stg_`) that clean and alias raw data. See ADR 0004.
- **Marts Schema:** dbt-managed views aggregating or filtering staging data for analytics. See ADR 0006.

Key locations:
- ADRs: docs/adr/
- FEC imports: docs/imports/fec-data/
- Notebooks: notebooks/
- Runbooks: docs/runbooks/
- Compose/runtime: compose/runtime.yml (canonical), docker-compose.yml (compatibility), and .devcontainer/docker-compose.yml

## Dev vs Runtime

- Devcontainer (interactive editor): uses `.devcontainer/devcontainer.json` and `.devcontainer/docker-compose.yml`; environment variables set for development include `DATA_DIR=/workspaces/money-trail/data`.
- Runtime (Airflow compose): canonical entrypoint `compose/runtime.yml`; compatibility entrypoint `docker-compose.yml`. Runtime services mount host `./data` to `/app/data` and use `DATA_DIR=/app/data`.
- Environment boundary contract: see `docs/architecture/dev-vs-runtime-topology.md`.

## Common commands

- Launch local runtime: `bash scripts/runtime.sh up`
- Stop runtime: `bash scripts/runtime.sh down`
- Runtime status: `bash scripts/runtime.sh ps`
- Runtime logs: `bash scripts/runtime.sh logs -f`
- Compose config check: `bash scripts/runtime.sh config`
- Rebuild a service: `docker compose -f compose/runtime.yml build <service>`
- Run dbt models: `cd dbt && dbt run`
- Run dbt tests: `cd dbt && dbt test`

## VS Code run and debug (F5)

Core hotkeys are listed at the top of this document.
- For `Run:*` terminal profiles, `F5` and `Ctrl+F5` run the same command effect (non-debug terminal launch).

Launch profiles are committed in `.vscode/launch.json` and run in the environment that VS Code is attached to (host shell or devcontainer shell).

Best-practice chooser:
- Use `Run: Runtime Up/Logs/Down` for Airflow service lifecycle.
- Use `Run: Tests (auto env)` for quick non-debug test runs.
- Use `Debug:*` profiles for Python code and tests you want to step through.

Execution model by profile:

| Profile | Runs where command starts | Runs where workload actually executes | Best use |
|---|---|---|---|
| `Run: Runtime Up` | Current VS Code shell (devcontainer if attached) | Docker Compose runtime containers from `compose/runtime.yml` | Start Airflow runtime stack |
| `Run: Runtime Logs` | Current VS Code shell | Docker Compose runtime containers | Tail runtime logs |
| `Run: Runtime Down` | Current VS Code shell | Docker Compose runtime containers | Stop runtime stack |
| `Run: Tests (auto env)` | Current VS Code shell | Same shell (devcontainer path inside container, local path on host) | Fast test run without debugger |
| `Debug: Current Python File` | Current VS Code shell | Python process in same shell under `debugpy` | Step-through debugging for one file |
| `Debug: Pytest (workspace)` | Current VS Code shell | Pytest process in same shell under `debugpy` | Debug multiple tests |
| `Debug: Pytest (current file)` | Current VS Code shell | Pytest process in same shell under `debugpy` | Debug one test file |

A folder-open task in `.vscode/tasks.json` prints a warning only when VS Code is not attached to a devcontainer, so non-container sessions (including agent-mode opens) get an explicit prompt to switch.

See docs/runbooks/README.md for more operational notes.

## Architecture contract

This project follows the Duck Lake contract: parquet files in `data/ducklake/` are the target immutable source-of-truth, while `data/duckdb/` remains a compatibility layer during migration. DuckDB is the query engine and dbt owns cleaning and QA via views. Key points:

- Storage: Airflow downloads FEC ZIPs and writes one parquet per cycle and file type to `data/ducklake/<file_type>_<cycle>.parquet` as target behavior; compatibility references under `data/duckdb/` are kept until migration slices complete.
- Registration: DuckDB registers parquet files as external tables in the raw schema (raw_<file_type>_<cycle>), not as primary DuckDB tables.
- Transformation: dbt creates staging (stg_<file_type>) and marts views over the raw external tables and is responsible for type coercion, aliasing, and QA.
- Metadata: Airflow owns metadata tables in the metadata schema (download state, daily observations, load history).
- Ownership: Airflow = downloads, file lifecycle, and metadata. dbt = cleaning, QA, and analytical views.

See ADR 0009 (docs/adr/0009-duck-lake-parquet-storage.md) for the formal decision and ADRs 0001–0008 for historical context.

Notes:
- Keep documentation changes small and focused; avoid changing runtime behavior during a docs PR.
- Link to this developer guide from README.md and CONTEXT.md where appropriate.
