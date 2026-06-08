#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW__CORE__DAGS_FOLDER:-/workspaces/money-trail/dags}"
if [[ -z "${AIRFLOW__CORE__EXECUTOR:-}" || "${AIRFLOW__CORE__EXECUTOR}" == "SequentialExecutor" ]]; then
  export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
fi

if [[ -z "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-}" || "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN}" == sqlite:* ]]; then
  export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/airflow"
fi

if ! pgrep -f "airflow scheduler" >/dev/null 2>&1; then
  airflow scheduler > logs/airflow-scheduler.log 2>&1 &
fi

# Avoid transient devcontainer port-forward failures by waiting for 8080 to accept connections.
if ! curl -sSf http://127.0.0.1:8080/ >/dev/null 2>&1; then
  if ! pgrep -f "airflow webserver" >/dev/null 2>&1; then
    airflow webserver --port 8080 > logs/airflow-webserver.log 2>&1 &
  fi

  for _ in $(seq 1 60); do
    if curl -sSf http://127.0.0.1:8080/ >/dev/null 2>&1; then
      exit 0
    fi

    # Retry launch if the previous webserver process died during startup.
    if ! pgrep -f "airflow webserver" >/dev/null 2>&1; then
      airflow webserver --port 8080 > logs/airflow-webserver.log 2>&1 &
    fi

    sleep 1
  done
else
  exit 0
fi

echo "ERROR: Airflow webserver did not become ready on http://127.0.0.1:8080 within 60s" >&2
echo "Last 100 lines of logs/airflow-webserver.log:" >&2
tail -n 100 logs/airflow-webserver.log >&2 || true
exit 1
