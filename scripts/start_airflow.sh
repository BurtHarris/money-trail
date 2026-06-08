#!/usr/bin/env bash
set -euo pipefail

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW__CORE__DAGS_FOLDER:-/workspaces/money-trail/dags}"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-sqlite:////workspaces/money-trail/.airflow/airflow.db}"

if pgrep -f "airflow webserver" >/dev/null 2>&1; then
  exit 0
fi

airflow scheduler > logs/airflow-scheduler.log 2>&1 &
airflow webserver --port 8080 > logs/airflow-webserver.log 2>&1 &
