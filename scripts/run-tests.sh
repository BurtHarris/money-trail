#!/usr/bin/env bash
set -euo pipefail

# Helper to run tests either inside the devcontainer or locally in a lightweight venv.
# Usage: ./scripts/run-tests.sh [--local]

run_pytest() {
  PYTHONPATH=. pytest -q "$@"
}

if [[ "${1-}" == "--local" ]]; then
  echo "Running tests in local venv (lightweight). This will install pytest only."
  python -m venv .venv-tests
  # shellcheck disable=SC1091
  . .venv-tests/bin/activate
  pip install --upgrade pip
  pip install pytest
  run_pytest
  deactivate || true
  exit 0
fi

# Detect devcontainer by checking for .devcontainer folder in repo root
if [[ -d ".devcontainer" ]]; then
  echo "Detected .devcontainer — running pytest. If dependencies are missing, open the devcontainer in VS Code."
  run_pytest
else
  echo "Devcontainer not detected. To run tests locally without the devcontainer, use:"
  echo "  ./scripts/run-tests.sh --local"
  echo "Or open the repository in the devcontainer and run tests there to use the full test deps (Airflow, dbt, etc)."
  exit 2
fi
