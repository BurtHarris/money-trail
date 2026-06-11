Repository Navigation — money-trail

Purpose
- Quick cheat-sheet mapping concepts to files/paths and common developer workflows.

Where to look
- DAGs and orchestration
  - dags/ — Airflow DAGs (download, load, change-detection)
  - scripts/ — bootstrap, local startup helpers
  - compose/ and docker-compose.yml — local compose orchestration

- Schemas & data formats
  - include/fec_schemas/ — Python schema modules (one per file type)
  - data/duckdb/ — Parquet immutable storage (file_type_cycle.parquet)
  - sql/ — analysis and QA queries

- dbt
  - dbt/ — dbt project with models, tests, and profiles
  - dbt/models/staging/ — staging models (stg_*)
  - dbt/models/marts/ — marts and cross-cycle views

- Metadata & config
  - config/pipeline.yaml — pipeline styles, cycles, and parallelism settings
  - docs/adr/ — architecture decisions (ADRs 0001–0009)
  - CONTEXT.md — glossary and ownership guidance

- Tests & development
  - tests/ — pytest tests for key pipeline components
  - notebooks/ — exploratory notebooks and demos
  - requirements.txt — Python deps; .devcontainer/ for container setup

Common tasks (cheat commands)
- Rebuild devcontainer and bootstrap: open in VS Code + Reopen in Container; or scripts/bootstrap.sh
- Start Airflow locally: docker compose up -d postgres airflow-init airflow-webserver airflow-scheduler
- Run dbt: cd dbt && dbt debug && dbt run && dbt test
- Run tests: pytest -q

Adding work guidance
- To add a new file type: add schema in include/fec_schemas/, update config/pipeline.yaml, add DAG or update existing DAGs as needed, add dbt staging + tests, and add ADR if contract changes.

Quick links
- README.md — quick start
- CONTEXT.md — glossary and ownership
- docs/adr/ — ADRs

Contact
- Use repository issue tracker for questions; reference ADR numbers when proposing contract changes.
