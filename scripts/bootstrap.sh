#!/usr/bin/env bash
set -euo pipefail

# Wait for PostgreSQL to be ready using Docker healthcheck
echo "Waiting for PostgreSQL service to be healthy..."
DB_READY=false
for i in {1..60}; do
  if PGPASSWORD="airflow" psql -h localhost -U airflow -d airflow -c "SELECT 1" >/dev/null 2>&1; then
    echo "✓ PostgreSQL is ready (attempt $i/60)"
    DB_READY=true
    break
  fi
  if [ $((i % 10)) -eq 0 ]; then
    echo "⏳ Attempt $i/60: PostgreSQL not ready yet..."
  fi
  sleep 1
done

if [ "$DB_READY" = false ]; then
  echo "✗ PostgreSQL failed to become ready after 60 seconds"
  exit 1
fi

mkdir -p .airflow
mkdir -p .local
mkdir -p data/raw
mkdir -p data/duckdb
mkdir -p logs

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://airflow:[REDACTED]@localhost:5432/airflow"

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

if [[ -f dbt/profiles.yml.example ]]; then
  if [[ ! -f dbt/profiles.yml ]]; then
    cp dbt/profiles.yml.example dbt/profiles.yml
    echo "✓ Copied dbt/profiles.yml from example"
  fi
else
  echo "ℹ dbt/profiles.yml.example not found, skipping copy"
fi

echo "✓ Bootstrap complete"
