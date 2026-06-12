# ADR 0002: Storage Layout and Windows Host Access

Status: Proposed
Date: 2026-06-11

## Context
The project requires a storage layout that supports:

- Clear separation of raw, staged, and analytic (Duck Lake/DuckDB) artifacts.
- Host (Windows) and devcontainer access with minimal path translation friction.
- Long-lived historical retention of analytic outputs.
- Ease of use for notebook-first workflows and Airflow-native runtime.

## Decision
Adopt the following repository-level storage layout:

- data/raw/      -> immutable ingested source files (zip, csv). Mount read-only into runtime.
- data/stage/    -> normalized, cleaned intermediate artifacts produced by ETL.
- data/ducklake/ -> surfaced Duck Lake / DuckDB parquet and queryable artifacts.
- exports/       -> user-facing exports (parquet/csv/json) produced by workflows.
- logs/          -> runtime logs (Airflow, tasks) mapped to host for inspection.

Mounting strategy:
- In devcontainer: mount repository root into /workspaces/money-trail. Use relative paths in scripts.
- In runtime compose: mount ./data -> /app/data, ./logs -> /app/logs, and explicit mounts for dags, dbt, scripts.
- Avoid absolute Windows paths in code; prefer repository-relative paths and environment variables (DATA_DIR).

Windows-specific guidance:
- Use Git's core.autocrlf and .gitattributes to keep LF in repo; allow CRLF on checkout where necessary.
- Prefer file formats and tooling that work on NTFS (avoid symlinks where possible).
- Document path length and permissions expectations in docs/runbooks/README.md.

## Consequences
Pros:
- Clear separation reduces accidental overwrites and simplifies retention policies.
- Host/devcontainer parity via relative mounts.
- Notebooks can open ducklake artifacts directly from data/ducklake.

Cons/Risks:
- Larger repo working sets because of mounting host data directories.
- Requires discipline to keep raw/immutable data immutable.

## Migration notes
- For existing ZIP-centric workflows, update scripts to output surfaced parquet into data/ducklake and move raw ZIPs to data/raw/ if needed.
- Update scripts, Airflow operators, and notebooks to use DATA_DIR env var and repository-relative paths.

## Implementation checklist
- [ ] Add DATA_DIR environment variable to devcontainer and compose files
- [ ] Update scripts to prefer DATA_DIR/repository-relative paths
- [ ] Add runbook entries for Windows path quirks and Docker volume mounting notes
- [ ] Add demo notebook showing reading data/ducklake/sample.parquet

## References
- ADR 0001: Dev/runtime split, Airflow-native ELT, Duck Lake (docs/adr/0001-dev-runtime-split-duck-lake.md)

/cc @BurtHarris
