# Data tier path contract

This contract defines where artifacts live so ingestion, transformation, and analyst workflows stay predictable during restructuring.

## Path tiers

| Tier | Path | Owner | Purpose | Host access guidance |
| --- | --- | --- | --- | --- |
| Raw source artifacts | `data/raw/` | Airflow ingest | Downloaded ZIP/CSV source files and fetch outputs | Host-visible for troubleshooting, but not the primary analyst handoff surface |
| Rebuildable intermediate artifacts | `data/stage/` | Pipeline runtime | Temporary or rebuildable processing outputs | Keep repository-local; treat as rebuildable working state rather than a sharing surface |
| Duck Lake analytical artifacts | `data/ducklake/` | Airflow ingest + dbt consumers | Primary immutable analytical parquet surfaces | Host-visible under the repo `data/` mount for notebooks and analyst inspection |
| DuckDB compatibility/query surfaces | `data/duckdb/` | Runtime compatibility layer | Existing DuckDB files and parquet/query paths kept during migration | Host-visible for compatibility/debugging only; do not treat as the long-term analyst-facing contract |
| Host-facing exports | `exports/` | Analysts and downstream consumers | Stable CSV/reports/snapshots intended for host access | Primary Windows/host handoff location; runtime must preserve it as `/app/exports` |

## Rules

1. Keep source-of-truth analytical parquet outputs in `data/ducklake/` as target state.
2. Keep `data/duckdb/` available while migration is active; do not break existing DAG/dbt paths without coordinated updates.
3. Keep raw ingests in `data/raw/`; cleaning and QA logic remain in dbt models.
4. Keep durable handoff artifacts in `exports/` for host and Windows workflows.
5. Use `DATA_DIR` in code and scripts; avoid absolute host paths.

## Validation

1. Run `bash scripts/bootstrap.sh` and confirm `data/raw/`, `data/stage/`, `data/ducklake/`, `data/duckdb/`, and `exports/` exist in the repository root.
2. Start runtime with `bash scripts/runtime.sh up` and confirm runtime services mount host `./data` to `/app/data` and host `./exports` to `/app/exports`.
3. On Windows/WSL workflows, treat `exports/` as the first place to look for analyst-facing outputs and `data/ducklake/` as the notebook-friendly analytical surface.

## Migration notes

1. Current runtime still references `data/duckdb/` in multiple places.
2. Path migration should happen in vertical slices with explicit acceptance criteria.
3. Remove `data/duckdb/` compatibility assumptions only after DAG/dbt/docs alignment.

See also:

- `docs/architecture/repository-restructuring-plan.md`
- `docs/architecture/dev-vs-runtime-topology.md`
- `docs/adr/0002-storage-layout.md`
- `docs/adr/0009-duck-lake-parquet-storage.md`
