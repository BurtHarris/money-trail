# Data path reference inventory

Current path references mapped for #36 migration sequencing.

## Compatibility path references (`data/duckdb`)

### Runtime/code

- `dags/init_duckdb.py`
- `dags/example_http_to_duckdb.py`
- `dags/fec_change_detection.py` (docstring/comments)
- `scripts/init_duckdb.py`
- `dbt/profiles.yml`
- `dbt/profiles.yml.example`

### Docs and runbooks

- `README.md`
- `CONTEXT.md`
- `docs/developer-guide.md`
- `docs/adr/README.md`
- `docs/adr/0006-duckdb-schema-separation.md`
- `docs/adr/0009-duck-lake-parquet-storage.md`
- `dags/README.md`
- `AGENTS.md`

### Tooling/examples

- `scripts/generate_sample_data.sql`
- `scripts/load_sample.ps1`

## Target-tier references already present

- `docs/architecture/data-tier-path-contract.md` (`raw/stage/ducklake/duckdb/exports`)
- `docs/runbooks/README.md` (`data/raw`, `data/ducklake`)
- `scripts/bootstrap.sh` directory scaffolding (`raw/stage/ducklake/duckdb` + `exports`)
- `notebooks/demo_read_ducklake.ipynb` (`data/ducklake`)

## Migration sequencing

1. Keep `data/duckdb` references running as compatibility layer.
2. Shift writer paths and sample-data flows to `data/ducklake` where contract requires immutable parquet.
3. Update dbt/DAG/runtime docs after code-path migrations land.
4. Remove compatibility references only after end-to-end runtime + dbt checks pass.
