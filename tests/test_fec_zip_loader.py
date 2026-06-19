"""Tests for include/fec_zip_loader.py.

Verifies:
- default_inner_filename returns correct names for known and unknown tables.
- load_fec_zip_to_duckdb creates the correct table with correct column names.
- load_fec_zip_to_duckdb raises FileNotFoundError for a missing ZIP.
- load_fec_zip_to_duckdb raises KeyError when the expected inner file is absent.
- Pipe-delimited data with the correct number of columns is loaded cleanly.
"""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

import duckdb

from include.fec_zip_loader import default_inner_filename, load_fec_zip_to_duckdb

# Minimal cn column list — matches include/fec_schemas/cn.py COLUMNS[*].fec_name
_CN_COLUMNS = [
    "cand_id",
    "cand_name",
    "cand_pty_affiliation",
    "cand_election_yr",
    "cand_office_st",
    "cand_office",
    "cand_office_district",
    "cand_ici",
    "cand_status",
    "cand_pcc",
    "cand_st1",
    "cand_st2",
    "cand_city",
    "cand_st",
    "cand_zip",
]

_CN_SAMPLE_ROWS = [
    "C00000059|HALLMARK CARDS PAC|REP|2024|MO|H|02|I|C|C00000059|2501 McGee|"
    "MD #500|Kansas City|MO|64108",
    "C00000422|AMERICAN MEDICAL ASSOCIATION POLITICAL ACTION COMMITTEE|REP|2024|"
    "IL|H|05|I|C|C00000422|515 N State St||Chicago|IL|60610",
]


def _make_cn_zip(rows: list[str], tmp_dir: Path) -> Path:
    """Write a fake cn ZIP to *tmp_dir* and return the path."""
    zip_path = tmp_dir / "cn_2024.zip"
    content = "\n".join(rows).encode("latin-1")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("cn.txt", content)
    zip_path.write_bytes(buf.getvalue())
    return zip_path


class TestDefaultInnerFilename(unittest.TestCase):
    def test_known_tables(self) -> None:
        expected = {
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
        for table, filename in expected.items():
            with self.subTest(table=table):
                self.assertEqual(default_inner_filename(table), filename)

    def test_unknown_table_fallback(self) -> None:
        """Unknown table should fall back to <table>.txt."""
        self.assertEqual(default_inner_filename("newfile"), "newfile.txt")


class TestLoadFecZipToDuckdb(unittest.TestCase):
    def _tmp_db(self) -> tuple[Path, str]:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        db_path = str(Path(td.name) / "test.duckdb")
        # Pre-create the raw schema so the loader can create tables.
        with duckdb.connect(db_path) as con:
            con.execute("CREATE SCHEMA IF NOT EXISTS raw")
        return Path(td.name), db_path

    # ─────────────────────────── Happy path ──────────────────────────── #

    def test_creates_table_with_correct_columns(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        zip_path = _make_cn_zip(_CN_SAMPLE_ROWS, tmp_dir)

        row_count = load_fec_zip_to_duckdb(
            zip_path=zip_path,
            fec_table="cn",
            cycle=2024,
            duckdb_path=db_path,
            column_names=_CN_COLUMNS,
        )

        self.assertEqual(row_count, 2)

        with duckdb.connect(db_path) as con:
            cols = [
                row[0]
                for row in con.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'raw' AND table_name = 'cn_2024'
                    ORDER BY ordinal_position
                    """
                ).fetchall()
            ]
        self.assertEqual(cols, _CN_COLUMNS)

    def test_returns_correct_row_count(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        zip_path = _make_cn_zip(_CN_SAMPLE_ROWS, tmp_dir)

        count = load_fec_zip_to_duckdb(
            zip_path=zip_path,
            fec_table="cn",
            cycle=2024,
            duckdb_path=db_path,
            column_names=_CN_COLUMNS,
        )

        self.assertEqual(count, 2)

    def test_data_is_loaded_correctly(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        zip_path = _make_cn_zip(_CN_SAMPLE_ROWS, tmp_dir)

        load_fec_zip_to_duckdb(
            zip_path=zip_path,
            fec_table="cn",
            cycle=2024,
            duckdb_path=db_path,
            column_names=_CN_COLUMNS,
        )

        with duckdb.connect(db_path) as con:
            row = con.execute(
                "SELECT cand_id, cand_name FROM raw.cn_2024 ORDER BY cand_id LIMIT 1"
            ).fetchone()

        self.assertEqual(row[0], "C00000059")
        self.assertEqual(row[1], "HALLMARK CARDS PAC")

    def test_replaces_table_on_second_load(self) -> None:
        """A second load should replace the first (full-replace semantics)."""
        tmp_dir, db_path = self._tmp_db()
        zip_path = _make_cn_zip(_CN_SAMPLE_ROWS, tmp_dir)

        load_fec_zip_to_duckdb(
            zip_path=zip_path, fec_table="cn", cycle=2024,
            duckdb_path=db_path, column_names=_CN_COLUMNS,
        )
        # Second load with just one row.
        zip_path2 = tmp_dir / "cn_2024_v2.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("cn.txt", _CN_SAMPLE_ROWS[0])
        zip_path2.write_bytes(buf.getvalue())

        count2 = load_fec_zip_to_duckdb(
            zip_path=zip_path2, fec_table="cn", cycle=2024,
            duckdb_path=db_path, column_names=_CN_COLUMNS,
        )

        self.assertEqual(count2, 1)
        with duckdb.connect(db_path) as con:
            total = con.execute("SELECT COUNT(*) FROM raw.cn_2024").fetchone()[0]
        self.assertEqual(total, 1)

    def test_custom_inner_filename(self) -> None:
        """Caller can override the inner filename."""
        tmp_dir, db_path = self._tmp_db()
        zip_path = tmp_dir / "cn_2022.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("CANDIDATE.TXT", _CN_SAMPLE_ROWS[0])
        zip_path.write_bytes(buf.getvalue())

        count = load_fec_zip_to_duckdb(
            zip_path=zip_path,
            fec_table="cn",
            cycle=2022,
            duckdb_path=db_path,
            column_names=_CN_COLUMNS,
            inner_filename="CANDIDATE.TXT",
        )

        self.assertEqual(count, 1)

    # ─────────────────────────── Error cases ─────────────────────────── #

    def test_raises_file_not_found_for_missing_zip(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        missing = tmp_dir / "missing.zip"

        with self.assertRaises(FileNotFoundError):
            load_fec_zip_to_duckdb(
                zip_path=missing, fec_table="cn", cycle=2024,
                duckdb_path=db_path, column_names=_CN_COLUMNS,
            )

    def test_raises_key_error_when_inner_file_absent(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        zip_path = tmp_dir / "bad.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("wrong_name.txt", "data")
        zip_path.write_bytes(buf.getvalue())

        with self.assertRaises(KeyError):
            load_fec_zip_to_duckdb(
                zip_path=zip_path, fec_table="cn", cycle=2024,
                duckdb_path=db_path, column_names=_CN_COLUMNS,
            )

    def test_different_cycles_create_separate_tables(self) -> None:
        tmp_dir, db_path = self._tmp_db()
        zip_2024 = _make_cn_zip([_CN_SAMPLE_ROWS[0]], tmp_dir)
        zip_2022 = tmp_dir / "cn_2022.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("cn.txt", _CN_SAMPLE_ROWS[1])
        zip_2022.write_bytes(buf.getvalue())

        load_fec_zip_to_duckdb(
            zip_path=zip_2024, fec_table="cn", cycle=2024,
            duckdb_path=db_path, column_names=_CN_COLUMNS,
        )
        load_fec_zip_to_duckdb(
            zip_path=zip_2022, fec_table="cn", cycle=2022,
            duckdb_path=db_path, column_names=_CN_COLUMNS,
        )

        with duckdb.connect(db_path) as con:
            cnt_2024 = con.execute("SELECT COUNT(*) FROM raw.cn_2024").fetchone()[0]
            cnt_2022 = con.execute("SELECT COUNT(*) FROM raw.cn_2022").fetchone()[0]

        self.assertEqual(cnt_2024, 1)
        self.assertEqual(cnt_2022, 1)


if __name__ == "__main__":
    unittest.main()
