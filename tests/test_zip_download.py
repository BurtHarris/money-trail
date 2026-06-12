"""Tests for FEC ZIP file storage utilities (Slice D).

Verifies:
- Canonical path placement: data/raw/<file_type>_<cycle>.zip
- Retention: existing ZIP is reused when the remote file is unchanged
- Re-download: ZIP is fetched when the remote file has changed
- Re-download: ZIP is fetched when no local copy exists
"""

from __future__ import annotations

import tempfile
import unittest
import unittest.mock
from pathlib import Path

from include.fec_zip_store import (
    RAW_DIR,
    build_raw_zip_path,
    download_zip,
    retain_or_download_zip,
)


class TestBuildRawZipPath(unittest.TestCase):
    """Path placement tests."""

    def test_path_format(self) -> None:
        """Path must be <raw_dir>/<file_type>_<cycle>.zip."""
        raw_dir = Path("/data/raw")
        path = build_raw_zip_path("indiv", 2024, raw_dir=raw_dir)
        self.assertEqual(path, Path("/data/raw/indiv_2024.zip"))

    def test_various_file_types(self) -> None:
        raw_dir = Path("/data/raw")
        for file_type in ["cn", "cm", "ccl", "oth", "pas2", "oppexp", "weball"]:
            with self.subTest(file_type=file_type):
                path = build_raw_zip_path(file_type, 2022, raw_dir=raw_dir)
                self.assertEqual(path.name, f"{file_type}_2022.zip")
                self.assertEqual(path.parent, raw_dir)

    def test_default_raw_dir_under_data_raw(self) -> None:
        """Without an explicit raw_dir, path falls under data/raw/."""
        path = build_raw_zip_path("cn", 2022)
        self.assertTrue(
            str(path).endswith("data/raw/cn_2022.zip"),
            f"Unexpected path: {path}",
        )

    def test_default_raw_dir_is_data_raw(self) -> None:
        """The module-level RAW_DIR constant must end in data/raw."""
        self.assertTrue(
            str(RAW_DIR).endswith("data/raw"),
            f"Unexpected RAW_DIR: {RAW_DIR}",
        )


class TestDownloadZip(unittest.TestCase):
    """Unit tests for the HTTP download helper."""

    def _make_mock_response(self, content: bytes):
        """Return a context-manager mock that streams *content* in one chunk."""
        mock_resp = unittest.mock.MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.iter_content.return_value = [content]
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        return mock_resp

    def test_creates_file_with_correct_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "indiv_2024.zip"
            fake_content = b"PK\x03\x04fake zip"

            mock_resp = self._make_mock_response(fake_content)
            with unittest.mock.patch("include.fec_zip_store.requests.get", return_value=mock_resp):
                download_zip("https://fec.gov/files/bulk-downloads/2024/indiv24.zip", dest)

            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_bytes(), fake_content)

    def test_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "a" / "b" / "cn_2024.zip"
            mock_resp = self._make_mock_response(b"data")
            with unittest.mock.patch("include.fec_zip_store.requests.get", return_value=mock_resp):
                download_zip("https://example.com/cn24.zip", dest)
            self.assertTrue(dest.exists())

    def test_raises_on_http_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "fail.zip"
            mock_resp = unittest.mock.MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("404 Not Found")
            mock_resp.__enter__ = lambda s: mock_resp
            mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
            with unittest.mock.patch("include.fec_zip_store.requests.get", return_value=mock_resp):
                with self.assertRaises(Exception):
                    download_zip("https://example.com/missing.zip", dest)


class TestRetainOrDownloadZip(unittest.TestCase):
    """Retention and conditional download tests."""

    def _mock_download(self, content: bytes = b"zip-bytes"):
        """Patch download_zip to write *content* to dest_path without HTTP."""

        def _fake_download(url, dest_path, **_kwargs):
            Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
            Path(dest_path).write_bytes(content)

        return unittest.mock.patch("include.fec_zip_store.download_zip", side_effect=_fake_download)

    # ------------------------------------------------------------------ #
    # Retention: existing ZIP, unchanged remote                           #
    # ------------------------------------------------------------------ #

    def test_reuses_existing_zip_when_unchanged(self) -> None:
        """When the ZIP exists and changed=False, no download should occur."""
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)
            zip_path = build_raw_zip_path("cn", 2024, raw_dir=raw_dir)
            zip_path.write_bytes(b"original content")

            with unittest.mock.patch("include.fec_zip_store.download_zip") as mock_dl:
                result_path, downloaded = retain_or_download_zip(
                    file_type="cn",
                    cycle=2024,
                    url="https://fec.gov/files/bulk-downloads/2024/cn24.zip",
                    changed=False,
                    raw_dir=raw_dir,
                )

            mock_dl.assert_not_called()
            self.assertFalse(downloaded)
            self.assertEqual(result_path, zip_path)
            # Original content is preserved.
            self.assertEqual(zip_path.read_bytes(), b"original content")

    def test_returned_path_matches_canonical_path(self) -> None:
        """retain_or_download_zip always returns the canonical path."""
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)
            # Pre-create the file so the retention branch is taken.
            zip_path = build_raw_zip_path("indiv", 2024, raw_dir=raw_dir)
            zip_path.write_bytes(b"data")

            with unittest.mock.patch("include.fec_zip_store.download_zip"):
                result_path, _ = retain_or_download_zip(
                    "indiv", 2024, "https://example.com/indiv24.zip",
                    changed=False, raw_dir=raw_dir,
                )
            self.assertEqual(result_path, zip_path)

    # ------------------------------------------------------------------ #
    # Download: ZIP absent                                                #
    # ------------------------------------------------------------------ #

    def test_downloads_when_zip_missing(self) -> None:
        """When no local ZIP exists, the file must be downloaded."""
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)
            zip_path = build_raw_zip_path("cn", 2022, raw_dir=raw_dir)
            self.assertFalse(zip_path.exists())

            with self._mock_download():
                result_path, downloaded = retain_or_download_zip(
                    "cn", 2022,
                    "https://fec.gov/files/bulk-downloads/2022/cn22.zip",
                    changed=False,
                    raw_dir=raw_dir,
                )

            self.assertTrue(downloaded)
            self.assertTrue(result_path.exists())
            self.assertEqual(result_path, zip_path)

    # ------------------------------------------------------------------ #
    # Download: remote changed                                            #
    # ------------------------------------------------------------------ #

    def test_redownloads_when_changed(self) -> None:
        """Even if a local ZIP exists, changed=True must trigger a download."""
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)
            zip_path = build_raw_zip_path("indiv", 2024, raw_dir=raw_dir)
            zip_path.write_bytes(b"stale content")

            with self._mock_download(b"fresh content"):
                result_path, downloaded = retain_or_download_zip(
                    "indiv", 2024,
                    "https://fec.gov/files/bulk-downloads/2024/indiv24.zip",
                    changed=True,
                    raw_dir=raw_dir,
                )

            self.assertTrue(downloaded)
            self.assertEqual(result_path.read_bytes(), b"fresh content")

    def test_stored_at_canonical_path_after_download(self) -> None:
        """ZIP must land at data/raw/<file_type>_<cycle>.zip after download."""
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp)

            with self._mock_download():
                result_path, _ = retain_or_download_zip(
                    "oppexp", 2020,
                    "https://fec.gov/files/bulk-downloads/2020/oppexp20.zip",
                    changed=False,
                    raw_dir=raw_dir,
                )

            expected = raw_dir / "oppexp_2020.zip"
            self.assertEqual(result_path, expected)


if __name__ == "__main__":
    unittest.main()
