from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import duckdb
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

DATA_DIR = Path("/workspaces/money-trail/data")
RAW_DIR = DATA_DIR / "raw"
DUCKDB_PATH = DATA_DIR / "duckdb" / "money_trail.duckdb"
SQLITE_PATH = DATA_DIR / "money_trail.sqlite"
SOURCE_URL = os.getenv(
    "FEC_SAMPLE_URL",
    "https://api.open.fec.gov/developers/",
)


def fetch_http_source(**context) -> str:
    response = requests.get(SOURCE_URL, timeout=30)
    response.raise_for_status()
    payload = {
        "fetched_at": datetime.utcnow().isoformat(),
        "url": SOURCE_URL,
        "status_code": response.status_code,
        "content_preview": response.text[:5000],
    }
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DIR / "fec_source.json"
    output_path.write_text(json.dumps(payload, indent=2))
    return str(output_path)


def load_into_duckdb(ti, **context) -> None:
    raw_path = ti.xcom_pull(task_ids="fetch_http_source")
    payload = json.loads(Path(raw_path).read_text())
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DUCKDB_PATH)) as con:
        con.execute(
            """
            create table if not exists raw_http_source (
                fetched_at varchar,
                url varchar,
                status_code integer,
                content_preview varchar
            )
            """
        )
        con.execute(
            "insert into raw_http_source values (?, ?, ?, ?)",
            [
                payload["fetched_at"],
                payload["url"],
                payload["status_code"],
                payload["content_preview"],
            ],
        )


def load_into_sqlite(ti, **context) -> None:
    raw_path = ti.xcom_pull(task_ids="fetch_http_source")
    payload = json.loads(Path(raw_path).read_text())
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(SQLITE_PATH) as con:
        con.execute(
            """
            create table if not exists raw_http_source (
                fetched_at text,
                url text,
                status_code integer,
                content_preview text
            )
            """
        )
        con.execute(
            "insert into raw_http_source values (?, ?, ?, ?)",
            (
                payload["fetched_at"],
                payload["url"],
                payload["status_code"],
                payload["content_preview"],
            ),
        )
        con.commit()


with DAG(
    dag_id="example_http_to_warehouse",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "money-trail"},
    tags=["example", "http", "duckdb", "sqlite", "openlineage"],
) as dag:
    fetch = PythonOperator(
        task_id="fetch_http_source",
        python_callable=fetch_http_source,
    )

    to_duckdb = PythonOperator(
        task_id="load_into_duckdb",
        python_callable=load_into_duckdb,
    )

    to_sqlite = PythonOperator(
        task_id="load_into_sqlite",
        python_callable=load_into_sqlite,
    )

    fetch >> [to_duckdb, to_sqlite]
