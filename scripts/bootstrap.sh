#!/usr/bin/env bash
set -euo pipefail

mkdir -p .airflow
mkdir -p .local
mkdir -p data/raw
mkdir -p data/duckdb
mkdir -p logs

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW__CORE__DAGS_FOLDER:-/workspaces/money-trail/dags}"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-sqlite:////workspaces/money-trail/.airflow/airflow.db}"

if [[ ! -f "$AIRFLOW_HOME/airflow.db" ]]; then
  airflow db migrate
fi

if ! airflow users list | grep -q "devadmin"; then
  airflow users create \
    --username devadmin \
    --firstname Dev \
    --lastname Admin \
    --role Admin \
    --email devadmin@example.com \
    --password devadmin
fi

if [[ ! -f dbt/profiles.yml ]]; then
  cp dbt/profiles.yml.example dbt/profiles.yml
fi
