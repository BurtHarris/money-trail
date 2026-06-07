"""Airflow DAG: bootstrap DuckDB schemas and the Download State table.

This DAG must run (or have run at least once) before any per-file-type DAG
can execute.  It is idempotent and safe to trigger repeatedly.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

from include.db_init import init_duckdb

DUCKDB_PATH = Path("/workspaces/money-trail/data/duckdb/money_trail.duckdb")


def _bootstrap_duckdb(**context) -> None:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_duckdb(str(DUCKDB_PATH))


with DAG(
    dag_id="init_duckdb",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "money-trail"},
    tags=["init", "duckdb", "schema"],
    description=(
        "Bootstrap DuckDB schemas (raw, staging, marts, metadata) and the "
        "metadata._fec_download_state table."
    ),
) as dag:
    bootstrap = PythonOperator(
        task_id="bootstrap_duckdb_schemas",
        python_callable=_bootstrap_duckdb,
    )
