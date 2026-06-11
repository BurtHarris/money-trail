# Data tier path contract

This contract defines where artifacts live so ingestion, transformation, and analyst workflows stay predictable during restructuring.

## Path tiers

| Tier | Path | Owner | Purpose |
| --- | --- | --- | --- |
| Raw source artifacts | `data/raw/` | Airflow ingest | Downloaded ZIP/CSV source files and fetch outputs |
| Rebuildable intermediate artifacts | `data/stage/` | Pipeline runtime | Temporary or rebuildable processing outputs |
| Duck Lake analytical artifacts | `data/ducklake/` | Airflow ingest + dbt consumers | Primary immutable analytical parquet surfaces |
| DuckDB compatibility/query surfaces | `data/duckdb/` | Runtime compatibility layer | Existing DuckDB files and parquet/query paths kept during migration |
| Host-facing exports | `exports/` | Analysts and downstream consumers | Stable CSV/reports/snapshots intended for host access |

## Rules

1. Keep source-of-truth analytical parquet outputs in `data/ducklake/` as target state.
2. Keep `data/duckdb/` available while migration is active; do not break existing DAG/dbt paths without coordinated updates.
3. Keep raw ingests in `data/raw/`; cleaning and QA logic remain in dbt models.
4. Keep durable handoff artifacts in `exports/` for host and Windows workflows.
5. Use `DATA_DIR` in code and scripts; avoid absolute host paths.

## Migration notes

1. Current runtime still references `data/duckdb/` in multiple places.
2. Path migration should happen in vertical slices with explicit acceptance criteria.
3. Remove `data/duckdb/` compatibility assumptions only after DAG/dbt/docs alignment.

See also:

- `docs/architecture/repository-restructuring-plan.md`
- `docs/architecture/dev-vs-runtime-topology.md`
- `docs/adr/0002-storage-layout.md`
- `docs/adr/0009-duck-lake-parquet-storage.md`
