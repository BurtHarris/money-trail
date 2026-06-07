#!/usr/bin/env bash
set -euo pipefail

mkdir -p .airflow
mkdir -p .local
mkdir -p data/raw
mkdir -p data/duckdb
mkdir -p logs

export AIRFLOW_HOME="${AIRFLOW_HOME:-/workspaces/money-trail/.airflow}"
POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-airflow}"
POSTGRES_USER="${POSTGRES_USER:-airflow}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-airflow}"

export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

cleanup_stale_airflow_state() {
  local pid_file="$AIRFLOW_HOME/airflow-webserver.pid"

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(tr -d '[:space:]' < "$pid_file")"

    if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
      echo "Removing stale Airflow webserver PID file..."
      rm -f "$pid_file"
    fi
  fi

  if [[ -f "$AIRFLOW_HOME/airflow.db" ]]; then
    echo "Removing stale local SQLite metastore..."
    rm -f "$AIRFLOW_HOME"/airflow.db "$AIRFLOW_HOME"/airflow.db-*
  fi
}

wait_for_postgres() {
  echo "Waiting for PostgreSQL service to be reachable..."

  local db_ready=false
  for i in {1..60}; do
    if POSTGRES_HOST="$POSTGRES_HOST" \
      POSTGRES_PORT="$POSTGRES_PORT" \
      POSTGRES_USER="$POSTGRES_USER" \
      POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
      python3 - <<'PY'
import os
import psycopg2

connection = psycopg2.connect(
    dbname="postgres",
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
connection.close()
PY
    then
      echo "PostgreSQL is ready (attempt $i/60)"
      db_ready=true
      break
    fi

    if [[ $((i % 10)) -eq 0 ]]; then
      echo "Attempt $i/60: PostgreSQL not ready yet..."
    fi

    sleep 1
  done

  if [[ "$db_ready" = false ]]; then
    echo "PostgreSQL failed to become ready after 60 seconds"
    exit 1
  fi
}

ensure_postgres_database() {
  POSTGRES_HOST="$POSTGRES_HOST" \
    POSTGRES_PORT="$POSTGRES_PORT" \
    POSTGRES_DB="$POSTGRES_DB" \
    POSTGRES_USER="$POSTGRES_USER" \
    POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    python3 - <<'PY'
import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

connection = psycopg2.connect(
    dbname="postgres",
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

database_name = os.environ["POSTGRES_DB"]
with connection.cursor() as cursor:
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    exists = cursor.fetchone() is not None
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}") .format(sql.Identifier(database_name)))
        print(f"Created PostgreSQL database '{database_name}' for Airflow metadata.")

connection.close()
PY
}

metadata_schema_exists() {
  POSTGRES_HOST="$POSTGRES_HOST" \
    POSTGRES_PORT="$POSTGRES_PORT" \
    POSTGRES_DB="$POSTGRES_DB" \
    POSTGRES_USER="$POSTGRES_USER" \
    POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    python3 - <<'PY'
import os
import sys

import psycopg2

connection = psycopg2.connect(
    dbname=os.environ["POSTGRES_DB"],
    host=os.environ["POSTGRES_HOST"],
    port=os.environ["POSTGRES_PORT"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
)

with connection.cursor() as cursor:
    cursor.execute(
        """
        SELECT EXISTS (
          SELECT 1
          FROM information_schema.tables
          WHERE table_schema = 'public' AND table_name = 'alembic_version'
        )
        """
    )
    schema_exists = cursor.fetchone()[0]

connection.close()
sys.exit(0 if schema_exists else 1)
PY
}

cleanup_stale_airflow_state
wait_for_postgres
ensure_postgres_database

if metadata_schema_exists; then
  echo "Running Airflow database migrations..."
  airflow db migrate
else
  echo "Rebuilding missing Airflow metadata schema in PostgreSQL..."
  airflow db reset --yes
fi

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
