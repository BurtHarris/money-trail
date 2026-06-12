#!/usr/bin/env bash
set -euo pipefail

# Helper to run tests either inside the devcontainer or locally in a lightweight venv.
# Usage: ./scripts/run-tests.sh [--local]

run_pytest() {
  PYTHONPATH=. pytest -q "$@"
}

resolve_python_cmd() {
  if command -v python >/dev/null 2>&1; then
    PYTHON_CMD=(python)
  elif command -v py >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
  else
    echo "ERROR: Neither 'python' nor 'py' is available on PATH." >&2
    exit 127
  fi
}

is_devcontainer_shell() {
  [[ -f "/.dockerenv" || -n "${REMOTE_CONTAINERS:-}" || -n "${DEVCONTAINER:-}" ]]
}

if [[ "${1-}" == "--local" ]]; then
  resolve_python_cmd
  echo "Running tests in local venv (lightweight). This will install pytest only."
  "${PYTHON_CMD[@]}" -m venv .venv-tests
  if [[ -f ".venv-tests/bin/activate" ]]; then
    # shellcheck disable=SC1091
    . .venv-tests/bin/activate
  elif [[ -f ".venv-tests/Scripts/activate" ]]; then
    # shellcheck disable=SC1091
    . .venv-tests/Scripts/activate
  else
    echo "ERROR: Could not find virtualenv activation script in .venv-tests." >&2
    exit 1
  fi
  pip install --upgrade pip
  pip install pytest
  run_pytest
  deactivate || true
  exit 0
fi

# Detect active devcontainer shell, not repository layout.
if is_devcontainer_shell; then
  echo "Detected devcontainer shell — running pytest."
  run_pytest
else
  echo "Devcontainer not detected. To run tests locally without the devcontainer, use:"
  echo "  ./scripts/run-tests.sh --local"
  echo "Or open the repository in the devcontainer and run tests there to use the full test deps (Airflow, dbt, etc)."
  exit 2
fi
