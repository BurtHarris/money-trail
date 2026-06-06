---
status: proposed
---

# Upgrade Airflow Metadata Database from SQLite to PostgreSQL

The devcontainer currently uses a SQLite-backed Airflow metadata database. SQLite is sufficient for single-process local development but cannot handle concurrent writes from multiple Airflow workers or schedulers. As per-file-type DAGs are introduced with configurable parallelism, parallel task execution will contend on the SQLite file and cause locking errors or data corruption. PostgreSQL is the Airflow-recommended production metadata backend, supports concurrent connections, and is required before parallel DAG execution is enabled in this project.
