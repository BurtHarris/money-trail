#!/usr/bin/env bash
set -euo pipefail

mkdir -p .airflow
mkdir -p .local
DATA_DIR="${DATA_DIR:-./data}"
mkdir -p "${DATA_DIR}/raw"
mkdir -p "${DATA_DIR}/stage"
mkdir -p "${DATA_DIR}/ducklake"
mkdir -p "${DATA_DIR}/duckdb"
mkdir -p exports
mkdir -p logs

bootstrap_airflow="${BOOTSTRAP_AIRFLOW:-1}"

if [[ ! -d "${HOME}/.cache" ]]; then
  mkdir -p "${HOME}/.cache"
fi
if [[ ! -w "${HOME}/.cache" ]]; then
  if command -v sudo >/dev/null 2>&1; then
    sudo chown -R "$(id -u)":"$(id -g)" "${HOME}/.cache"
  fi
fi
mkdir -p "${HOME}/.cache/uv"
if [[ ! -w "${HOME}/.cache" || ! -w "${HOME}/.cache/uv" ]]; then
  echo "ERROR: ${HOME}/.cache is not writable; cannot initialize uv cache." >&2
  exit 1
fi

if [[ "${bootstrap_airflow,,}" != "0" && "${bootstrap_airflow,,}" != "false" && "${bootstrap_airflow,,}" != "no" ]]; then
  export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
  export AIRFLOW__CORE__DAGS_FOLDER="${AIRFLOW__CORE__DAGS_FOLDER:-/workspaces/money-trail/dags}"
  if [[ -z "${AIRFLOW__CORE__EXECUTOR:-}" || "${AIRFLOW__CORE__EXECUTOR}" == "SequentialExecutor" ]]; then
    export AIRFLOW__CORE__EXECUTOR="LocalExecutor"
  fi
  export AIRFLOW__CORE__AUTH_MANAGER="${AIRFLOW__CORE__AUTH_MANAGER:-airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager}"

  if ! command -v airflow >/dev/null 2>&1; then
    echo "ERROR: airflow CLI not found in PATH. Ensure dependencies are installed and run this inside the devcontainer." >&2
    exit 1
  fi

  if [[ -z "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN:-}" || "${AIRFLOW__DATABASE__SQL_ALCHEMY_CONN}" == sqlite:* ]]; then
    export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
  fi

  airflow db migrate

  if ! airflow users list | grep -q "devadmin"; then
    echo "Creating admin user..."
    airflow users create \
      --username devadmin \
      --firstname Dev \
      --lastname Admin \
      --role Admin \
      --email devadmin@example.com \
      --password devadmin
  fi
else
  echo "Skipping Airflow metadata bootstrap (BOOTSTRAP_AIRFLOW=${bootstrap_airflow})"
fi

if [[ -f dbt/profiles.yml.example ]]; then
  if [[ ! -f dbt/profiles.yml ]]; then
    cp dbt/profiles.yml.example dbt/profiles.yml
    echo "✓ Copied dbt/profiles.yml from example"
  fi
else
  echo "ℹ dbt/profiles.yml.example not found, skipping copy"
fi

echo "✓ Bootstrap complete"
