#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$script_dir/bootstrap.sh"

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-airflow}"
POSTGRES_USER="${POSTGRES_USER:-airflow}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-airflow}"

export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

if ! pgrep -f "airflow scheduler" >/dev/null 2>&1; then
  airflow scheduler > logs/airflow-scheduler.log 2>&1 &
fi

if ! pgrep -f "airflow webserver" >/dev/null 2>&1; then
  rm -f "$AIRFLOW_HOME/airflow-webserver.pid"
  airflow webserver --port 8080 > logs/airflow-webserver.log 2>&1 &
fi
