#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-compose/runtime.yml}"
AIRFLOW_UI_URL="${AIRFLOW_UI_URL:-http://localhost:8080}"

is_runtime_healthy() {
  local status
  status=$(docker inspect --format '{{.State.Health.Status}}' money-trail-airflow 2>/dev/null || true)
  [[ "${status}" == "healthy" ]]
}

open_ui_integrated_or_external() {
  local ui_url="$1"

  # In remote/devcontainer sessions, VS Code's browser helper opens external URLs.
  # Use that path first because it is the most reliable from a terminal launch config.
  if [[ -n "${BROWSER:-}" ]] && "${BROWSER}" "${ui_url}" >/dev/null 2>&1; then
    echo "Requested Airflow UI open in browser: ${ui_url}"
    return 0
  fi

  # Secondary attempt: ask local VS Code to open Simple Browser via command URI.
  local encoded_url
  encoded_url="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "${ui_url}")"
  local vscode_uri="vscode://vscode.simple-browser/show?${encoded_url}"
  if [[ -n "${BROWSER:-}" ]] && "${BROWSER}" "${vscode_uri}" >/dev/null 2>&1; then
    echo "Requested Airflow UI open in VS Code Simple Browser: ${ui_url}"
    return 0
  fi

  echo "INFO: Browser launch request failed. Open manually: ${ui_url}"
  return 0
}

already_healthy=0
if is_runtime_healthy; then
  already_healthy=1
fi

bash scripts/runtime.sh up

if [[ "${already_healthy}" -eq 1 ]]; then
  echo "Runtime already healthy; reopening UI."
fi

open_ui_integrated_or_external "${AIRFLOW_UI_URL}"
