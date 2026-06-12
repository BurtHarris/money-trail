#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/runtime.yml}"
AIRFLOW_HEALTH_URL="${AIRFLOW_HEALTH_URL:-http://127.0.0.1:8080/api/v2/monitor/health}"
HEALTH_TIMEOUT_SECONDS="${HEALTH_TIMEOUT_SECONDS:-90}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker CLI not found in PATH." >&2
  exit 1
fi

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "ERROR: compose file not found: ${COMPOSE_FILE}" >&2
  exit 1
fi

require_docker_access() {
  if ! docker info >/dev/null 2>&1; then
    echo "ERROR: docker daemon unavailable or permission denied for current user." >&2
    echo "Fix: start Docker Desktop/daemon, then verify socket/group access for this user." >&2
    exit 1
  fi
}

wait_for_airflow_health() {
  local attempts=0
  while (( attempts < HEALTH_TIMEOUT_SECONDS )); do
    # Poll Docker's own healthcheck result to avoid devcontainer network isolation.
    local status
    status=$(docker inspect --format '{{.State.Health.Status}}' money-trail-airflow 2>/dev/null || true)
    if [[ "${status}" == "healthy" ]]; then
      return 0
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  echo "ERROR: Airflow health endpoint not ready after ${HEALTH_TIMEOUT_SECONDS}s" >&2
  docker compose -f "${COMPOSE_FILE}" ps >&2
  exit 1
}

build_progress_mode() {
  if [[ -t 1 ]]; then
    echo "tty"
  else
    echo "plain"
  fi
}

needs_rebuild() {
  local service
  local image_id

  for service in $(docker compose -f "${COMPOSE_FILE}" config --services); do
    image_id="$(docker compose -f "${COMPOSE_FILE}" images -q "${service}" | head -n 1)"
    if [[ -z "${image_id}" ]]; then
      return 0
    fi
  done

  return 1
}

should_wait_for_airflow_health() {
  if [[ "$#" -eq 0 ]]; then
    return 0
  fi

  local arg
  for arg in "$@"; do
    if [[ "${arg}" == "airflow" ]]; then
      return 0
    fi
  done

  return 1
}

cmd="${1:-up}"
shift || true

case "${cmd}" in
  up)
    require_docker_access

    build_requested=0
    up_args=()
    for arg in "$@"; do
      if [[ "${arg}" == "--build" ]]; then
        build_requested=1
      else
        up_args+=("${arg}")
      fi
    done

    if [[ "${build_requested}" -eq 1 ]] || needs_rebuild; then
      progress_mode="$(build_progress_mode)"
      echo "Building runtime images (progress: ${progress_mode})..."
      docker compose --progress "${progress_mode}" -f "${COMPOSE_FILE}" build
    fi

    docker compose -f "${COMPOSE_FILE}" up -d "${up_args[@]}"
    wait_for_airflow_health
    echo "✓ Runtime up and healthy (${AIRFLOW_HEALTH_URL})"
    ;;
  down)
    require_docker_access
    docker compose -f "${COMPOSE_FILE}" down "$@"
    ;;
  start)
    require_docker_access
    docker compose -f "${COMPOSE_FILE}" start "$@"
    if should_wait_for_airflow_health "$@"; then
      wait_for_airflow_health
      echo "✓ Runtime started and healthy (${AIRFLOW_HEALTH_URL})"
    fi
    ;;
  stop)
    require_docker_access
    docker compose -f "${COMPOSE_FILE}" stop "$@"
    ;;
  restart)
    require_docker_access
    docker compose -f "${COMPOSE_FILE}" restart "$@"
    if should_wait_for_airflow_health "$@"; then
      wait_for_airflow_health
      echo "✓ Runtime restarted and healthy (${AIRFLOW_HEALTH_URL})"
    fi
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
    echo "Usage: scripts/runtime.sh [up|down|start|stop|restart|ps|logs|config] [args...]" >&2
    echo "  up supports optional --build to force a rebuild with progress output." >&2
    exit 2
    ;;
esac
