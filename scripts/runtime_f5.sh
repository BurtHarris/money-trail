#!/usr/bin/env bash
set -euo pipefail

AIRFLOW_UI_URL="${AIRFLOW_UI_URL:-http://localhost:8080}"
AIRFLOW_HEALTH_URL="${AIRFLOW_HEALTH_URL:-http://127.0.0.1:8080/api/v2/monitor/health}"

is_runtime_healthy() {
  curl -sSf "${AIRFLOW_HEALTH_URL}" >/dev/null 2>&1
}

open_ui_integrated_or_external() {
  local ui_url="$1"

  local encoded_url
  encoded_url="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "${ui_url}")"
  local vscode_uri="vscode://vscode.simple-browser/show?${encoded_url}"

  # Try integrated browser first via VS Code URI scheme.
  if [[ -n "${BROWSER:-}" ]] && "${BROWSER}" "${vscode_uri}" >/dev/null 2>&1; then
    echo "Opened Airflow UI in integrated browser: ${ui_url}"
    return 0
  fi

  # Fallback: open the same URL in the configured host browser.
  if [[ -n "${BROWSER:-}" ]] && "${BROWSER}" "${ui_url}" >/dev/null 2>&1; then
    echo "Opened Airflow UI in external browser: ${ui_url}"
    return 0
  fi

  echo "INFO: Browser launch failed. Open manually: ${ui_url}"
  return 0
}

already_healthy=0
if is_runtime_healthy; then
  already_healthy=1
fi

bash scripts/runtime.sh up

if [[ "${already_healthy}" -eq 1 ]]; then
  echo "Runtime already healthy; skipped reopening UI."
  exit 0
fi

open_ui_integrated_or_external "${AIRFLOW_UI_URL}"
