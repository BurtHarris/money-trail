#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/runtime.yml}"
AIRFLOW_HEALTH_URL="${AIRFLOW_HEALTH_URL:-http://127.0.0.1:8080/api/v2/monitor/health}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-90}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found in PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: docker daemon unavailable or permission denied for current user." >&2
  echo "Fix: start Docker Desktop/daemon, then verify socket/group access for this user." >&2
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "ERROR: compose file not found: ${COMPOSE_FILE}" >&2
  exit 1
fi

wait_for_airflow_health() {
  local attempts=0
  while (( attempts < HEALTH_TIMEOUT_SECONDS )); do
    if curl -sSf "${AIRFLOW_HEALTH_URL}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  echo "ERROR: Airflow health endpoint not ready: ${AIRFLOW_HEALTH_URL}" >&2
  docker compose -f "${COMPOSE_FILE}" ps >&2
  exit 1
}

cmd="${1:-up}"
shift || true

case "${cmd}" in
  up)
    docker compose -f "${COMPOSE_FILE}" up -d --build "$@"
    wait_for_airflow_health
    echo "✓ Runtime up and healthy (${AIRFLOW_HEALTH_URL})"
    ;;
  down)
    docker compose -f "${COMPOSE_FILE}" down "$@"
    ;;
  ps)
    docker compose -f "${COMPOSE_FILE}" ps "$@"
    ;;
  logs)
    docker compose -f "${COMPOSE_FILE}" logs "$@"
    ;;
  config)
    docker compose -f "${COMPOSE_FILE}" config "$@"
    ;;
  *)
    echo "Usage: scripts/runtime.sh [up|down|ps|logs|config] [args...]" >&2
    exit 2
    ;;
esac
