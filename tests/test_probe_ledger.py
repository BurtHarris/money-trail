from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

from include.db_init import init_duckdb
from include.pipeline_config import PlanUnit
from include.probe_ledger import probe_plan_units


class _FakeResponse:
    def __init__(
        self,
        status_code: int,
        headers: dict[str, str] | None = None,
        url: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url or ""


class TestProbeLedger(unittest.TestCase):
    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def test_probe_success_and_failure_both_append_rows(self) -> None:
        db_path = self._tmp_db()
        init_duckdb(db_path)

        plan_units = [
            PlanUnit(cycle=2024, file_type="indiv", style_name="current", change_detection=True),
            PlanUnit(cycle=2022, file_type="cn", style_name="historical", change_detection=False),
        ]

        def fake_head(url: str, timeout: int, allow_redirects: bool):
            if "indiv" in url:
                return _FakeResponse(
                    status_code=200,
                    headers={"ETag": "etag-1", "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
                    url=url,
                )
            raise requests.Timeout("probe timeout")

        checked_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        observations = probe_plan_units(
            plan_units=plan_units,
            duckdb_path=db_path,
            checked_at=checked_at,
            request_head=fake_head,
        )

        self.assertEqual(len(observations), 2)
        with duckdb.connect(db_path) as con:
            rows = con.execute(
                """
                SELECT cycle, file_type, etag, last_modified, probe_ok, status_code,
                       observed_url, error_message
                FROM metadata._fec_download_state
                ORDER BY cycle DESC, file_type ASC
                """
            ).fetchall()

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], 2024)
        self.assertEqual(rows[0][1], "indiv")
        self.assertEqual(rows[0][2], "etag-1")
        self.assertEqual(rows[0][4], True)
        self.assertEqual(rows[0][5], 200)
        self.assertIsNone(rows[0][7])

        self.assertEqual(rows[1][0], 2022)
        self.assertEqual(rows[1][1], "cn")
        self.assertIsNone(rows[1][2])
        self.assertEqual(rows[1][4], False)
        self.assertIsNone(rows[1][5])
        self.assertIn("probe timeout", rows[1][7])

    def test_probe_runs_for_plan_units_even_when_change_detection_false(self) -> None:
        db_path = self._tmp_db()
        init_duckdb(db_path)

        plan_units = [
            PlanUnit(cycle=2024, file_type="indiv", style_name="current", change_detection=True),
            PlanUnit(cycle=2024, file_type="cn", style_name="historical", change_detection=False),
        ]

        called_urls: list[str] = []

        def fake_head(url: str, timeout: int, allow_redirects: bool):
            called_urls.append(url)
            return _FakeResponse(status_code=200, headers={}, url=url)

        probe_plan_units(
            plan_units=plan_units,
            duckdb_path=db_path,
            request_head=fake_head,
        )

        self.assertEqual(len(called_urls), 2)
        self.assertTrue(any("/2024/indiv.zip" in url for url in called_urls))
        self.assertTrue(any("/2024/cn.zip" in url for url in called_urls))


if __name__ == "__main__":
    unittest.main()
