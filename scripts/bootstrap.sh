#!/usr/bin/env bash
set -euo pipefail

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
  if PGPASSWORD="airflow" psql -h localhost -U airflow -d airflow -c "SELECT 1" >/dev/null 2>&1; then
    echo "PostgreSQL is ready"
    break
  fi
  echo "Attempt $i/30: PostgreSQL not ready yet, waiting..."
  sleep 1
done

mkdir -p .airflow
mkdir -p .local
mkdir -p data/raw
mkdir -p data/duckdb
mkdir -p logs

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://airflow:airflow@localhost:5432/airflow"

echo "Running Airflow database migrations..."
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

if [[ ! -f dbt/profiles.yml ]]; then
  cp dbt/profiles.yml.example dbt/profiles.yml
fi

echo "Bootstrap complete"
