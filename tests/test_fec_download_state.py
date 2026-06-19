from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb

from include.fec_download_state import DownloadStateManager
from include.fec_head_probe import ProbeResult


class TestFecDownloadState(unittest.TestCase):
    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def test_appends_row_on_every_check_even_when_unchanged(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)
        checked_at = datetime(2026, 1, 1, 0, 0, 0)

        first_changed = manager.detect_change("indiv", 2024, "etag-1", "last-mod-1")
        manager.record_download_state_check(
            file_type="indiv",
            cycle=2024,
            checked_at=checked_at,
            etag="etag-1",
            last_modified="last-mod-1",
            changed=first_changed,
            downloaded=False,
        )

        second_changed = manager.detect_change("indiv", 2024, "etag-1", "last-mod-1")
        manager.record_download_state_check(
            file_type="indiv",
            cycle=2024,
            checked_at=checked_at + timedelta(minutes=1),
            etag="etag-1",
            last_modified="last-mod-1",
            changed=second_changed,
            downloaded=False,
        )

        with duckdb.connect(db_path) as con:
            count = con.execute(
                """
                SELECT COUNT(*)
                FROM metadata._fec_download_state
                WHERE file_type = 'indiv' AND cycle = 2024
                """
            ).fetchone()[0]
            latest = con.execute(
                """
                SELECT changed, downloaded
                FROM metadata._fec_download_state
                WHERE file_type = 'indiv' AND cycle = 2024
                ORDER BY checked_at DESC
                LIMIT 1
                """
            ).fetchone()

        self.assertEqual(count, 2)
        self.assertEqual(first_changed, False)
        self.assertEqual(second_changed, False)
        self.assertEqual(latest, (False, False))

    def test_detects_change_when_etag_or_last_modified_differs(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)

        manager.record_download_state_check(
            file_type="cn",
            cycle=2022,
            checked_at=datetime(2026, 1, 1, 0, 0, 0),
            etag="etag-1",
            last_modified="last-mod-1",
            changed=False,
            downloaded=False,
        )

        changed = manager.detect_change("cn", 2022, "etag-2", "last-mod-1")
        self.assertTrue(changed)

        manager.record_download_state_check(
            file_type="cn",
            cycle=2022,
            checked_at=datetime(2026, 1, 1, 0, 5, 0),
            etag="etag-2",
            last_modified="last-mod-1",
            changed=changed,
            downloaded=False,
        )

        latest = manager.get_latest_state("cn", 2022)
        assert latest is not None
        self.assertEqual(latest["changed"], True)
        self.assertEqual(latest["downloaded"], False)


def _make_probe(
    *,
    fec_table: str = "indiv",
    cycle: int = 2024,
    http_status: int = 200,
    etag: str | None = '"abc"',
    last_modified: str | None = "Wed, 01 Jan 2026 00:00:00 GMT",
    error: str | None = None,
    content_length: int | None = 12345,
) -> ProbeResult:
    return ProbeResult(
        fec_table=fec_table,
        cycle=cycle,
        url=f"https://example.com/{fec_table}{str(cycle)[-2:]}.zip",
        probe_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
        http_status=http_status,
        etag=etag,
        last_modified=last_modified,
        content_length=content_length,
        error=error,
    )


class TestProbeLedger(unittest.TestCase):
    """Full Probe Ledger: append-only probe records in DuckDB."""

    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def test_successful_probe_is_stored_in_ledger(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)
        probe = _make_probe(etag='"abc"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT")

        obs_id = manager.append_probe_to_ledger(probe)

        self.assertIsNotNone(obs_id)
        with duckdb.connect(db_path) as con:
            row = con.execute(
                """
                SELECT file_type, cycle, http_status, etag, last_modified,
                       probe_success, error_message
                FROM metadata._fec_daily_observation
                WHERE observation_id = ?
                """,
                [obs_id],
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "indiv")
        self.assertEqual(row[1], 2024)
        self.assertEqual(row[2], 200)
        self.assertEqual(row[3], '"abc"')
        self.assertEqual(row[4], "Wed, 01 Jan 2026 00:00:00 GMT")
        self.assertTrue(row[5])   # probe_success
        self.assertIsNone(row[6]) # error_message

    def test_failed_probe_is_stored_as_first_class_observation(self) -> None:
        """Failure observations are stored — outages are visible in ledger."""
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)
        probe = _make_probe(
            http_status=None, etag=None, last_modified=None,
            error="Connection refused", content_length=None,
        )

        obs_id = manager.append_probe_to_ledger(probe)

        with duckdb.connect(db_path) as con:
            row = con.execute(
                """
                SELECT probe_success, error_message, http_status
                FROM metadata._fec_daily_observation
                WHERE observation_id = ?
                """,
                [obs_id],
            ).fetchone()
        self.assertFalse(row[0])  # probe_success
        self.assertIn("Connection refused", row[1])  # error_message
        self.assertIsNone(row[2])  # http_status

    def test_ledger_is_append_only(self) -> None:
        """Multiple probes accumulate as distinct rows."""
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)

        id1 = manager.append_probe_to_ledger(_make_probe(etag='"v1"'))
        id2 = manager.append_probe_to_ledger(_make_probe(etag='"v2"'))

        self.assertNotEqual(id1, id2)
        with duckdb.connect(db_path) as con:
            count = con.execute(
                "SELECT COUNT(*) FROM metadata._fec_daily_observation "
                "WHERE file_type = 'indiv' AND cycle = 2024"
            ).fetchone()[0]
        self.assertEqual(count, 2)

    def test_probe_ledger_schema_migration_is_idempotent(self) -> None:
        """Creating DownloadStateManager twice on same DB is safe."""
        db_path = self._tmp_db()
        DownloadStateManager(db_path)
        DownloadStateManager(db_path)  # must not raise
        probe = _make_probe()
        obs_id = DownloadStateManager(db_path).append_probe_to_ledger(probe)
        self.assertIsNotNone(obs_id)


class TestLatestLoadBaseline(unittest.TestCase):
    """Latest-load baseline lookup for Freshness Precedence Rule."""

    def _tmp_db(self) -> str:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        return str(Path(tmp_dir.name) / "test.duckdb")

    def test_returns_none_when_no_loads_recorded(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)
        result = manager.get_latest_load_baseline("indiv", 2024)
        self.assertIsNone(result)

    def test_returns_latest_load_record_etag_and_last_modified(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)

        manager.record_load(
            file_type="indiv",
            cycle=2024,
            source_url="https://example.com/indiv24.zip",
            source_zip_path="/data/raw/indiv_2024.zip",
            target_parquet_path="/data/ducklake/indiv_2024.parquet",
            row_count=1000,
            etag='"etag-v1"',
            last_modified="Mon, 1 Jan 2024 00:00:00 GMT",
        )

        baseline = manager.get_latest_load_baseline("indiv", 2024)

        self.assertIsNotNone(baseline)
        self.assertEqual(baseline["etag"], '"etag-v1"')
        self.assertEqual(baseline["last_modified"], "Mon, 1 Jan 2024 00:00:00 GMT")

    def test_returns_most_recent_when_multiple_loads(self) -> None:
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)

        manager.record_load(
            file_type="cn", cycle=2022,
            source_url="https://example.com/cn22.zip",
            source_zip_path="/data/raw/cn_2022.zip",
            target_parquet_path="/data/ducklake/cn_2022.parquet",
            row_count=500,
            etag='"old-etag"',
            last_modified="Mon, 1 Jan 2024 00:00:00 GMT",
        )
        manager.record_load(
            file_type="cn", cycle=2022,
            source_url="https://example.com/cn22.zip",
            source_zip_path="/data/raw/cn_2022.zip",
            target_parquet_path="/data/ducklake/cn_2022.parquet",
            row_count=600,
            etag='"new-etag"',
            last_modified="Tue, 2 Jan 2024 00:00:00 GMT",
        )

        baseline = manager.get_latest_load_baseline("cn", 2022)

        self.assertIsNotNone(baseline)
        self.assertEqual(baseline["etag"], '"new-etag"')
        self.assertEqual(baseline["last_modified"], "Tue, 2 Jan 2024 00:00:00 GMT")

    def test_baseline_isolated_to_fec_table_and_cycle(self) -> None:
        """Baseline for indiv_2024 is not affected by cn_2022 loads."""
        db_path = self._tmp_db()
        manager = DownloadStateManager(db_path)

        manager.record_load(
            file_type="cn", cycle=2022,
            source_url="https://example.com/cn22.zip",
            source_zip_path="/data/raw/cn_2022.zip",
            target_parquet_path="/data/ducklake/cn_2022.parquet",
            row_count=500, etag='"cn-etag"', last_modified="Mon, 1 Jan 2024 00:00:00 GMT",
        )

        baseline = manager.get_latest_load_baseline("indiv", 2024)
        self.assertIsNone(baseline)


if __name__ == "__main__":
    unittest.main()
