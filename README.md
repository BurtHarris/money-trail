# money-trail

Lightweight devcontainer-first workspace for FEC-oriented ELT development with Apache Airflow, OpenLineage, DuckDB, PostgreSQL metadata, and dbt.

## What is included

- VS Code devcontainer for Python-based data engineering work
- Apache Airflow 3.2 with a local PostgreSQL-backed metadata database
- Dedicated containers for Airflow webserver and scheduler, separate from the VS Code workspace container
- **Duck Lake architecture**: Parquet files as immutable storage, DuckDB as query engine
- FEC campaign finance data pipeline: bulk download extraction, parquet storage, dbt-based cleaning and QA
- dbt starter project targeting DuckDB
- OpenLineage Python and Airflow provider dependencies preinstalled

## Quick start

1. Open the repository in VS Code.
2. Reopen in Container.
3. Wait for the post-create bootstrap to finish.
4. Start Airflow runtime services when needed:
   - `docker compose up -d postgres airflow-init airflow-webserver airflow-scheduler`
5. Open Airflow at http://localhost:8080
   - username: `devadmin`
   - password: `devadmin`
6. Trigger the DAG `fec_download_and_load` to download FEC data and populate parquet files.
7. Run dbt commands from `dbt/`:
   - `dbt debug` - verify DuckDB connection
   - `dbt run` - materialize staging and marts views
   - `dbt test` - run data quality tests

## Project layout

- `.devcontainer/` - container build and VS Code setup
- `dags/` - Airflow DAGs (FEC download, parquet write, dbt trigger)
- `dbt/` - dbt project with staging and marts models
- `data/` - local data artifacts (parquet files, DuckDB, raw ZIPs)
- `scripts/` - bootstrap and local startup helpers
- `docs/` - architecture decisions (ADRs), developer guide, runbooks
- `sql/` - analysis and QA queries

## Architecture Overview

**Duck Lake**: Parquet files in `data/duckdb/` serve as primary immutable storage (one file per FEC file type per cycle). Airflow downloads and writes parquet. DuckDB queries these files via external tables. dbt creates views for cleaning (staging) and aggregation (marts).

See [CONTEXT.md](CONTEXT.md) for domain glossary, [docs/developer-guide.md](docs/developer-guide.md) for developer onboarding and the architecture contract, and [docs/adr/](docs/adr/) for architecture decisions (ADR 0009 documents the Duck Lake approach).

## Notes

- **Data pipeline**: Airflow downloads FEC bulk data and writes parquet files to `data/duckdb/`. dbt queries these files and creates views for analysis. See ADR 0009.
- **Schema separation**: DuckDB uses four schemas (`raw`, `staging`, `marts`, `metadata`) to keep Airflow and dbt ownership clear. See ADR 0006.
- **Data quality**: All cleaning and QA lives in dbt (staging and marts models). Airflow is kept simple. See ADR 0004.
- **FEC data dictionary**: Each file type has official format documentation at https://www.fec.gov/campaign-finance-data/ (see CONTEXT.md for links to specific formats).
- **Data normalization**: ZIP codes are truncated to 5 digits, amounts rounded to 2 decimals, and whitespace trimmed in staging models.
