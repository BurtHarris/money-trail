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
   - `bash scripts/runtime.sh up`
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

**Duck Lake**: Parquet files in `data/ducklake/` are the target primary immutable storage (one file per FEC file type per cycle). During migration, compatibility surfaces in `data/duckdb/` remain available. Airflow downloads and writes parquet, DuckDB queries parquet via external tables, and dbt builds cleaning/aggregation views.

### Documentation Roadmap

- **[CONTEXT.md](CONTEXT.md)** — Domain glossary (Cycles, File Types, Raw Layer, Staging Schema, etc.) and system architecture terms. Start here to understand the ubiquitous language used across the project.
- **[docs/developer-guide.md](docs/developer-guide.md)** — Developer onboarding, common commands, devcontainer vs runtime setup, and the architecture contract. Essential for contributors.
- **[docs/architecture/repository-restructuring-plan.md](docs/architecture/repository-restructuring-plan.md)** — Target-state repository contract and phased restructuring plan tied to ADR decisions.
- **[docs/architecture/dev-vs-runtime-topology.md](docs/architecture/dev-vs-runtime-topology.md)** — Explicit boundary between editor devcontainer topology and runtime Airflow service topology.
- **[docs/architecture/data-tier-path-contract.md](docs/architecture/data-tier-path-contract.md)** — Canonical path contract for `data/raw`, `data/stage`, `data/ducklake`, `data/duckdb`, and `exports`.
- **[docs/architecture/README.md](docs/architecture/README.md)** — Index for architecture contracts and restructuring docs.
- **[docs/adr/README.md](docs/adr/README.md)** — Index of all Architecture Decision Records (ADRs 0001–0009). Each ADR documents a significant design choice and its consequences. ADR 0009 formalizes Duck Lake.
- **[docs/runbooks/](docs/runbooks/)** — Operational guides and troubleshooting for common tasks.

## Notes

- **Data pipeline**: Airflow downloads FEC bulk data and writes parquet files to Duck Lake surfaces (`data/ducklake/` target state, `data/duckdb/` compatibility during migration). dbt queries parquet-backed raw tables and creates views for analysis. See ADR 0009 and the data-tier path contract.
- **Runtime control**: Use `scripts/runtime.sh` for canonical runtime lifecycle commands (`up`, `down`, `ps`, `logs`, `config`) against `compose/runtime.yml`.
- **Schema separation**: DuckDB uses four schemas (`raw`, `staging`, `marts`, `metadata`) to keep Airflow and dbt ownership clear. See ADR 0006.
- **Data quality**: All cleaning and QA lives in dbt (staging and marts models). Airflow is kept simple. See ADR 0004.
- **FEC data dictionary**: Each file type has official format documentation at https://www.fec.gov/campaign-finance-data/ (see CONTEXT.md for links to specific formats).
- **Data normalization**: ZIP codes are truncated to 5 digits, amounts rounded to 2 decimals, and whitespace trimmed in staging models.
