# money-trail

Lightweight devcontainer-first workspace for FEC-oriented ELT development with Apache Airflow, OpenLineage, DuckDB, PostgreSQL metadata, and dbt.

## What is included

- VS Code devcontainer for Python-based data engineering work
- Apache Airflow 2.9 with a local PostgreSQL-backed metadata database
- Example DAG that reads from an HTTP source and writes to DuckDB and SQLite
- dbt starter project targeting DuckDB
- OpenLineage Python and Airflow provider dependencies preinstalled

## Quick start

1. Open the repository in VS Code.
2. Reopen in Container.
3. Wait for the post-create bootstrap to finish.
4. Open Airflow at http://localhost:8080
   - username: `devadmin`
   - password: `devadmin`
5. Trigger the DAG `example_http_to_warehouse`.
6. Run dbt commands from `dbt/`, for example:
   - `dbt debug`
   - `dbt run`

## Project layout

- `.devcontainer/` - container build and VS Code setup
- `dags/` - Airflow DAGs
- `dbt/` - dbt project and example model
- `data/` - local DuckDB, SQLite, and raw data artifacts
- `scripts/` - bootstrap and local startup helpers

## Notes

- This repo intentionally keeps orchestration lightweight to stabilize the development environment first.
- OpenLineage packages are installed now; the next step can wire in a local backend such as Marquez or another collector.
- The example HTTP source points to a public FEC developer page so the container can be validated without requiring an API key.
- Once the container is stable, FEC ingestion code can be moved from your other repository into `dags/`, `include/`, and `dbt/models/`.
