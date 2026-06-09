from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from include.pipeline_config import load_config
from include.probe_entrypoint import run_probe_plan


class _FakeResponse:
    def __init__(self, status_code: int, headers: dict[str, str], url: str) -> None:
        self.status_code = status_code
        self.headers = headers
        self.url = url


class TestProbeEntrypoint(unittest.TestCase):
    def _write_temp_config(self, yaml_text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "pipeline.yaml"
        config_path.write_text(yaml_text, encoding="utf-8")
        return config_path

    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def test_run_probe_plan_uses_plan_units_from_config(self) -> None:
        config_path = self._write_temp_config(
            """
parallelism:
  cycles: sequential
  file_types: parallel
styles:
  current:
    file_types: [indiv, cn]
    change_detection: true
  historical:
    file_types: [weball]
    change_detection: false
cycles:
  - cycle: 2024
    style: current
  - cycle: 2022
    style: historical
"""
        )
        config = load_config(config_path)
        db_path = self._tmp_db()

        called_urls: list[str] = []

        def fake_head(url: str, timeout: int, allow_redirects: bool):
            called_urls.append(url)
            return _FakeResponse(
                status_code=200,
                headers={"ETag": "abc", "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
                url=url,
            )

        observations = run_probe_plan(
            config=config,
            duckdb_path=db_path,
            checked_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            request_head=fake_head,
        )

        expected_unit_count = len(config.build_plan().units)
        self.assertEqual(len(observations), expected_unit_count)
        self.assertEqual(len(called_urls), expected_unit_count)

        with duckdb.connect(db_path) as con:
            row_count = con.execute(
                "SELECT COUNT(*) FROM metadata._fec_download_state"
            ).fetchone()[0]
        self.assertEqual(row_count, expected_unit_count)


if __name__ == "__main__":
    unittest.main()
