#!/usr/bin/env bash
set -euo pipefail

# Load sample FEC data and verify dbt can recognize it via DuckDB.

SKIP_GENERATE=false
SKIP_DEBUG=false

usage() {
  cat <<'EOF'
Usage: scripts/load_sample.sh [options]

Options:
  --skip-generate   Skip sample parquet generation
  --skip-debug      Skip dbt debug verification
  --help            Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-generate)
      SKIP_GENERATE=true
      ;;
    --skip-debug)
      SKIP_DEBUG=true
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DATA_DIR="${ROOT_DIR}/data/duckdb"
SAMPLE_FILE="${DATA_DIR}/sample_indiv_2024.parquet"
SQL_SCRIPT="${SCRIPT_DIR}/generate_sample_data.sql"

printf '%0.s=' {1..70}
echo
echo "Money Trail Sample Data Loader"
printf '%0.s=' {1..70}
echo

if [[ "$SKIP_GENERATE" == false ]]; then
  echo "[1/3] Generating sample data..."
  mkdir -p "$DATA_DIR"

  if [[ -f "$SQL_SCRIPT" ]]; then
    if ! (cd "$DATA_DIR" && duckdb < "$SQL_SCRIPT" >/dev/null); then
      echo "Error generating sample data" >&2
      exit 1
    fi
    echo "Sample data generated via DuckDB"
  else
    echo "generate_sample_data.sql not found at $SQL_SCRIPT"
    echo "Skipping generation; using existing file if present"
  fi
  echo
fi

echo "[2/3] Verifying sample file..."
if [[ -f "$SAMPLE_FILE" ]]; then
  file_kb=$(du -k "$SAMPLE_FILE" | awk '{print $1}')
  echo "Sample file verified: $SAMPLE_FILE"
  echo "Size: ${file_kb} KB"
else
  echo "Sample file not found: $SAMPLE_FILE" >&2
  exit 1
fi
echo

if [[ "$SKIP_DEBUG" == false ]]; then
  echo "[3/3] Running dbt debug to verify DuckDB connection..."
  DBT_DIR="${ROOT_DIR}/dbt"
  if [[ ! -d "$DBT_DIR" ]]; then
    echo "dbt directory not found at $DBT_DIR" >&2
    exit 1
  fi

  if (cd "$DBT_DIR" && dbt debug); then
    echo "dbt debug succeeded - DuckDB connection verified"
  else
    echo "dbt debug reported issues (see output above)"
  fi
fi

echo
printf '%0.s=' {1..70}
echo
echo "Sample Data Load Complete"
printf '%0.s=' {1..70}
echo
echo "Next steps:"
echo "  1. Create external table in DuckDB: CREATE EXTERNAL TABLE raw.indiv_2024 AS SELECT * FROM '$SAMPLE_FILE';"
echo "  2. Run dbt models: dbt run"
echo "  3. View sample data: SELECT * FROM staging.stg_indiv LIMIT 5;"
