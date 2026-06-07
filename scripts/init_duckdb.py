#!/usr/bin/env python3
"""Standalone DuckDB schema bootstrap script.

Run from the devcontainer workspace root::

    python scripts/init_duckdb.py

Override the default database path with the ``DUCKDB_PATH`` environment
variable if needed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow ``include.*`` imports when run directly from the project root.
sys.path.insert(0, str(Path(__file__).parent.parent))

from include.db_init import init_duckdb  # noqa: E402

_DEFAULT_DUCKDB_PATH = "/workspaces/money-trail/data/duckdb/money_trail.duckdb"
DUCKDB_PATH = Path(os.getenv("DUCKDB_PATH", _DEFAULT_DUCKDB_PATH))


def main() -> None:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_duckdb(str(DUCKDB_PATH))
    print(f"✓ DuckDB schemas initialised at {DUCKDB_PATH}")


if __name__ == "__main__":
    main()
