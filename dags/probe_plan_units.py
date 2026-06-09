from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from include.probe_entrypoint import run_probe_plan


def _run_probe_plan_task() -> dict[str, int]:
    observations = run_probe_plan()
    return {
        "total_observations": len(observations),
        "success_observations": sum(1 for observation in observations if observation.probe_ok),
        "failed_observations": sum(1 for observation in observations if not observation.probe_ok),
    }


with DAG(
    dag_id="probe_plan_units",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "money-trail"},
    tags=["probe", "telemetry", "download-state"],
    description="Run universal HEAD probes for plan units from pipeline config.",
) as dag:
    run_probe = PythonOperator(
        task_id="run_probe_plan_units",
        python_callable=_run_probe_plan_task,
    )
