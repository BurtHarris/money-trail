"""DuckDB schema bootstrap.

Creates the ``raw``, ``staging``, ``marts``, and ``metadata`` schemas, and the
``metadata._fec_download_state`` table.  All statements are idempotent — safe
to run multiple times without error.
"""

from __future__ import annotations

import re

import duckdb

SCHEMAS: list[str] = ["raw", "staging", "marts", "metadata"]

_SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_CREATE_DOWNLOAD_STATE_SQL = """
CREATE TABLE IF NOT EXISTS metadata._fec_download_state (
    checked_at    TIMESTAMP,
    cycle         INTEGER,
    file_type     VARCHAR,
    etag          VARCHAR,
    last_modified VARCHAR,
    changed       BOOLEAN,
    downloaded    BOOLEAN,
    probe_ok      BOOLEAN,
    status_code   INTEGER,
    observed_url  VARCHAR,
    error_message VARCHAR
)
"""

_DOWNLOAD_STATE_EVOLUTION_SQL = [
    "ALTER TABLE metadata._fec_download_state ADD COLUMN IF NOT EXISTS probe_ok BOOLEAN",
    "ALTER TABLE metadata._fec_download_state ADD COLUMN IF NOT EXISTS status_code INTEGER",
    "ALTER TABLE metadata._fec_download_state ADD COLUMN IF NOT EXISTS observed_url VARCHAR",
    "ALTER TABLE metadata._fec_download_state ADD COLUMN IF NOT EXISTS error_message VARCHAR",
]


def init_duckdb(duckdb_path: str) -> None:
    """Create schemas and tables in the DuckDB file at *duckdb_path*.

    Safe to call multiple times; uses ``CREATE … IF NOT EXISTS`` throughout.
    """
    with duckdb.connect(duckdb_path) as con:
        for schema in SCHEMAS:
            if not _SAFE_IDENTIFIER_RE.match(schema):
                raise ValueError(f"Unsafe schema name: {schema!r}")
            con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        con.execute(_CREATE_DOWNLOAD_STATE_SQL)
        for alter_sql in _DOWNLOAD_STATE_EVOLUTION_SQL:
            con.execute(alter_sql)
