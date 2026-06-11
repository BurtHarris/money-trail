Architecture Contract — money-trail

Purpose
- Define clear boundaries, ownership, and expectations between core components (Airflow, Duck Lake/Parquet, DuckDB, dbt, and metadata).

Components & Ownership
- Airflow (dags/): owns download orchestration, writing parquet to data/duckdb/, and metadata tables in metadata schema. Owner: Airflow codebase (dags/ + scripts/).
- Storage (data/duckdb/*.parquet): immutable parquet files, one file per file-type+cycle. Owner: Airflow writes; readers treat as immutable.
- DuckDB query engine: query surface used by dbt via external tables referencing parquet. Owner: dbt for views; Airflow for metadata tables.
- dbt (dbt/): owns staging and marts views, data quality tests, and transformations. dbt models must not modify raw parquet files.
- Metadata (metadata schema in DuckDB): Airflow-owned operational tables (download_state, daily_observations, load_history).

Interfaces / Contracts
- Parquet format: one file per <file_type>_<cycle>.parquet; schema follows include/fec_schemas/* modules (pyarrow types). Consumers may rely on column names/aliases documented in schema modules.
- Raw tables: Airflow exposes raw external tables in `raw` schema named raw.<file_type>_<cycle>. These are read-only for dbt.
- Staging views: dbt creates stg_<file_type> views that union cycles, apply canonical aliases, types, and cleansing rules (zip to 5 digits, trim whitespace, round amounts).
- Change detection: Airflow uses metadata._fec_download_state and HEAD checks to trigger downloads.

Behavioral Expectations
- Ownership: Only Airflow writes parquet and metadata tables. dbt modifies only views in staging/marts.
- Backwards compatibility: Staging/marts views should remain stable; breaking changes require an ADR and coordinated deploy.
- Testing: dbt tests must cover type coercion, null handling, and normalization rules. Airflow unit tests should verify download/load logic and metadata updates.

Developer Guidance
- Adding a new File Type: create schema module in include/fec_schemas/, update DAGs and pipeline config (config/pipeline.yaml), and add dbt staging model + tests.
- Local runs: use scripts/bootstrap.sh and docker compose targets per README.

Enforcement & Review
- Changes affecting contracts (schemas, staging behavior, naming) require documentation in an ADR and a dbt test proving compatibility.

References
- CONTEXT.md, docs/adr/ (ADRs 0001–0009), README.md
