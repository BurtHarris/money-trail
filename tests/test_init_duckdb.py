from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import duckdb

from include.db_init import SCHEMAS, init_duckdb


class TestInitDuckdb(unittest.TestCase):
    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def _schema_names(self, db_path: str) -> set[str]:
        with duckdb.connect(db_path) as con:
            rows = con.execute(
                "SELECT DISTINCT schema_name FROM information_schema.schemata"
            ).fetchall()
        return {r[0] for r in rows}

    def test_schemas_created(self) -> None:
        db_path = self._tmp_db()
        init_duckdb(db_path)
        schema_names = self._schema_names(db_path)
        for schema in SCHEMAS:
            self.assertIn(schema, schema_names)

    def test_download_state_table_columns(self) -> None:
        db_path = self._tmp_db()
        init_duckdb(db_path)
        with duckdb.connect(db_path) as con:
            rows = con.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'metadata'
                  AND table_name   = '_fec_download_state'
                ORDER BY ordinal_position
                """
            ).fetchall()
        self.assertEqual(len(rows), 11)
        col_names = [r[0] for r in rows]
        self.assertEqual(
            col_names,
            [
                "checked_at",
                "cycle",
                "file_type",
                "etag",
                "last_modified",
                "changed",
                "downloaded",
                "probe_ok",
                "status_code",
                "observed_url",
                "error_message",
            ],
        )
        col_types = {r[0]: r[1] for r in rows}
        self.assertEqual(col_types["checked_at"], "TIMESTAMP")
        self.assertEqual(col_types["cycle"], "INTEGER")
        self.assertEqual(col_types["file_type"], "VARCHAR")
        self.assertEqual(col_types["etag"], "VARCHAR")
        self.assertEqual(col_types["last_modified"], "VARCHAR")
        self.assertEqual(col_types["changed"], "BOOLEAN")
        self.assertEqual(col_types["downloaded"], "BOOLEAN")
        self.assertEqual(col_types["probe_ok"], "BOOLEAN")
        self.assertEqual(col_types["status_code"], "INTEGER")
        self.assertEqual(col_types["observed_url"], "VARCHAR")
        self.assertEqual(col_types["error_message"], "VARCHAR")

    def test_idempotent(self) -> None:
        db_path = self._tmp_db()
        init_duckdb(db_path)
        # Must not raise on a second call.
        init_duckdb(db_path)
        # Schemas and table must still be present.
        schema_names = self._schema_names(db_path)
        for schema in SCHEMAS:
            self.assertIn(schema, schema_names)


if __name__ == "__main__":
    unittest.main()
