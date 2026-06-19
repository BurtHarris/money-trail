"""FEC ZIP-to-DuckDB bulk loader.

Opens a local FEC bulk-download ZIP, extracts the pipe-delimited text file
inside, and loads it into DuckDB as ``raw.<fec_table>_<cycle>``.  The target
table is created or replaced on every call (full-replace load semantics).

All columns are loaded as ``VARCHAR``; type coercion is left to dbt staging
models.  Callers supply the ordered list of FEC column names, so this module
has **no** dependency on pyarrow.
"""

from __future__ import annotations

import logging
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import duckdb

logger = logging.getLogger(__name__)

# Default inner filenames for the FEC bulk-download ZIPs.
_DEFAULT_INNER_FILENAMES: dict[str, str] = {
    "cn": "cn.txt",
    "cm": "cm.txt",
    "ccl": "ccl.txt",
    "oth": "itoth.txt",
    "pas2": "itpas2.txt",
    "oppexp": "itdissem.txt",
    "weball": "weball.txt",
    "indiv": "itcont.txt",
    "indexp": "indexp.txt",
}


def default_inner_filename(fec_table: str) -> str:
    """Return the FEC-standard inner filename for *fec_table* within its ZIP.

    Falls back to ``<fec_table>.txt`` for unknown tables.

    Args:
        fec_table: FEC short code, e.g. ``"cn"``, ``"indiv"``.

    Returns:
        Expected filename inside the ZIP, e.g. ``"cn.txt"``.
    """
    return _DEFAULT_INNER_FILENAMES.get(fec_table, f"{fec_table}.txt")


def load_fec_zip_to_duckdb(
    zip_path: Path,
    fec_table: str,
    cycle: int,
    duckdb_path: str,
    column_names: list[str],
    inner_filename: Optional[str] = None,
) -> int:
    """Load a FEC bulk-download ZIP into ``raw.<fec_table>_<cycle>`` in DuckDB.

    The target table is **dropped and recreated** on every call.  Callers are
    responsible for ensuring the ``raw`` schema exists (e.g. by running
    ``init_duckdb`` first).

    The text file inside the ZIP is assumed to be pipe-delimited with **no
    header row**; columns map to *column_names* in order.

    Args:
        zip_path:       Path to the local ZIP file.
        fec_table:      FEC table code, e.g. ``"cn"``.
        cycle:          Election cycle year, e.g. ``2024``.
        duckdb_path:    Path to the DuckDB database file.
        column_names:   Ordered list of FEC column names (raw headers).
        inner_filename: Name of the pipe-delimited file inside the ZIP.
                        Defaults to the FEC-standard name for *fec_table*.

    Returns:
        Number of rows loaded into the table.

    Raises:
        FileNotFoundError: If *zip_path* does not exist.
        KeyError:          If the expected inner file is absent from the ZIP.
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"ZIP not found: {zip_path}")

    if inner_filename is None:
        inner_filename = default_inner_filename(fec_table)

    table_name = f"raw.{fec_table}_{cycle}"

    logger.info(
        "Loading %s → %s  (inner=%s, %d columns)",
        zip_path,
        table_name,
        inner_filename,
        len(column_names),
    )

    with zipfile.ZipFile(zip_path) as zf:
        names_lower = {n.lower(): n for n in zf.namelist()}
        actual_name = names_lower.get(inner_filename.lower())
        if actual_name is None:
            raise KeyError(
                f"Expected '{inner_filename}' inside '{zip_path.name}'; "
                f"found: {zf.namelist()!r}"
            )
        with tempfile.TemporaryDirectory() as tmp_dir:
            extracted = Path(tmp_dir) / inner_filename
            with zf.open(actual_name) as src, extracted.open("wb") as dst:
                dst.write(src.read())

            row_count = _load_text_file_to_duckdb(
                text_path=extracted,
                table_name=table_name,
                column_names=column_names,
                duckdb_path=duckdb_path,
            )

    logger.info("Loaded %d rows into %s", row_count, table_name)
    return row_count


def _load_text_file_to_duckdb(
    text_path: Path,
    table_name: str,
    column_names: list[str],
    duckdb_path: str,
) -> int:
    """Create *table_name* from a pipe-delimited, no-header text file.

    Uses DuckDB's ``read_csv`` with ``all_varchar=True`` so that every column
    is stored as ``VARCHAR``; staging models handle type coercion.

    Args:
        text_path:    Path to the extracted pipe-delimited file.
        table_name:   Fully-qualified DuckDB table name, e.g. ``raw.cn_2024``.
        column_names: Ordered list of column names to assign.
        duckdb_path:  Path to the DuckDB database file.

    Returns:
        Row count after load.
    """
    # Build the names list literal for read_csv (e.g. ['col1', 'col2', ...]).
    col_names_literal = "[" + ", ".join(f"'{c}'" for c in column_names) + "]"
    # Use forward slashes; DuckDB handles both separators on all platforms.
    path_str = text_path.as_posix()

    with duckdb.connect(duckdb_path) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
        con.execute(
            f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv(
                '{path_str}',
                sep='|',
                header=False,
                names={col_names_literal},
                all_varchar=True,
                ignore_errors=True
            )
            """
            # ignore_errors=True: FEC bulk files occasionally contain rows with
            # encoding issues or mismatched column counts (e.g., embedded delimiters
            # in address fields).  Problematic rows are silently skipped by DuckDB.
            # The row count returned by this function reflects only rows that were
            # successfully loaded; callers can compare it against expectations if
            # data-quality alerting is required.
        )
        row_count: int = con.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

    return row_count
