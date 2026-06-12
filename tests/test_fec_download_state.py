from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

from include.fec_download_state import DownloadStateManager


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


if __name__ == "__main__":
    unittest.main()
