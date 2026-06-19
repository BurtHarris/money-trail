"""Tests for the Universal HEAD Probe seam.

Verifies:
- Deterministic URL construction per FecTable and Cycle
- Successful probe captures HTTP headers as a ProbeResult
- Failed probe (HTTP error or network exception) is captured as a first-class
  observation with probe_success=False
"""

from __future__ import annotations

import unittest
import unittest.mock
from datetime import datetime, timezone

from include.fec_head_probe import (
    ProbeResult,
    build_fec_download_url,
    perform_head_probe,
)


class TestBuildFecDownloadUrl(unittest.TestCase):
    """Deterministic URL construction tests."""

    def test_indiv_2024_url(self) -> None:
        url = build_fec_download_url("indiv", 2024)
        self.assertEqual(
            url,
            "https://www.fec.gov/files/bulk-downloads/2024/indiv24.zip",
        )

    def test_cn_2022_url(self) -> None:
        url = build_fec_download_url("cn", 2022)
        self.assertEqual(
            url,
            "https://www.fec.gov/files/bulk-downloads/2022/cn22.zip",
        )

    def test_weball_2020_url(self) -> None:
        url = build_fec_download_url("weball", 2020)
        self.assertEqual(
            url,
            "https://www.fec.gov/files/bulk-downloads/2020/weball20.zip",
        )

    def test_two_digit_suffix_uses_last_two_digits_of_cycle(self) -> None:
        """Cycle suffix is always the last two digits."""
        url = build_fec_download_url("cm", 2010)
        self.assertIn("/2010/", url)
        self.assertTrue(url.endswith("cm10.zip"))


class TestProbeResultSuccessFlag(unittest.TestCase):
    """probe_success property reflects whether the probe is a clean 200."""

    def test_probe_success_true_when_200_and_no_error(self) -> None:
        probe = ProbeResult(
            fec_table="indiv",
            cycle=2024,
            url="https://example.com/indiv24.zip",
            probe_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            http_status=200,
            etag='"abc"',
            last_modified="Wed, 01 Jan 2026 00:00:00 GMT",
            content_length=1024,
            error=None,
        )
        self.assertTrue(probe.probe_success)

    def test_probe_success_false_when_http_error(self) -> None:
        probe = ProbeResult(
            fec_table="cn",
            cycle=2022,
            url="https://example.com/cn22.zip",
            probe_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            http_status=404,
            etag=None,
            last_modified=None,
            content_length=None,
            error="File not found",
        )
        self.assertFalse(probe.probe_success)

    def test_probe_success_false_when_no_http_status(self) -> None:
        probe = ProbeResult(
            fec_table="cm",
            cycle=2020,
            url="https://example.com/cm20.zip",
            probe_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
            http_status=None,
            etag=None,
            last_modified=None,
            content_length=None,
            error="Connection refused",
        )
        self.assertFalse(probe.probe_success)


class TestPerformHeadProbeSuccess(unittest.TestCase):
    """Successful 200 probe returns ProbeResult with headers."""

    def _mock_200_response(self, etag: str, last_modified: str, content_length: str):
        mock_resp = unittest.mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {
            "ETag": etag,
            "Last-Modified": last_modified,
            "Content-Length": content_length,
        }
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = unittest.mock.MagicMock(return_value=False)
        return mock_resp

    def test_successful_probe_captures_all_headers(self) -> None:
        mock_resp = self._mock_200_response(
            etag='"abc123"',
            last_modified="Wed, 01 Jan 2026 00:00:00 GMT",
            content_length="987654321",
        )
        with unittest.mock.patch(
            "include.fec_head_probe.requests.head", return_value=mock_resp
        ):
            result = perform_head_probe(
                url="https://example.com/indiv24.zip",
                fec_table="indiv",
                cycle=2024,
            )

        self.assertTrue(result.probe_success)
        self.assertEqual(result.fec_table, "indiv")
        self.assertEqual(result.cycle, 2024)
        self.assertEqual(result.http_status, 200)
        self.assertEqual(result.etag, '"abc123"')
        self.assertEqual(result.last_modified, "Wed, 01 Jan 2026 00:00:00 GMT")
        self.assertEqual(result.content_length, 987654321)
        self.assertIsNone(result.error)
        self.assertIsNotNone(result.probe_time)

    def test_successful_probe_url_is_preserved(self) -> None:
        mock_resp = self._mock_200_response('"e"', "Mon, 1 Jan 2024 00:00:00 GMT", "100")
        with unittest.mock.patch(
            "include.fec_head_probe.requests.head", return_value=mock_resp
        ):
            result = perform_head_probe(
                url="https://www.fec.gov/files/bulk-downloads/2024/cn24.zip",
                fec_table="cn",
                cycle=2024,
            )
        self.assertEqual(
            result.url, "https://www.fec.gov/files/bulk-downloads/2024/cn24.zip"
        )


class TestPerformHeadProbeFailure(unittest.TestCase):
    """Failed probes are first-class observations with probe_success=False."""

    def test_404_response_is_captured_as_failed_probe(self) -> None:
        mock_resp = unittest.mock.MagicMock()
        mock_resp.status_code = 404
        mock_resp.headers = {}
        with unittest.mock.patch(
            "include.fec_head_probe.requests.head", return_value=mock_resp
        ):
            result = perform_head_probe(
                url="https://example.com/missing24.zip",
                fec_table="indiv",
                cycle=2024,
            )

        self.assertFalse(result.probe_success)
        self.assertEqual(result.http_status, 404)
        self.assertIsNotNone(result.error)
        self.assertIsNone(result.etag)

    def test_network_exception_is_captured_as_failed_probe(self) -> None:
        import requests as req

        with unittest.mock.patch(
            "include.fec_head_probe.requests.head",
            side_effect=req.ConnectionError("Connection refused"),
        ):
            result = perform_head_probe(
                url="https://example.com/indiv24.zip",
                fec_table="indiv",
                cycle=2024,
            )

        self.assertFalse(result.probe_success)
        self.assertIsNone(result.http_status)
        self.assertIn("Connection refused", result.error)

    def test_timeout_is_captured_as_failed_probe(self) -> None:
        import requests as req

        with unittest.mock.patch(
            "include.fec_head_probe.requests.head",
            side_effect=req.Timeout("timed out"),
        ):
            result = perform_head_probe(
                url="https://example.com/indiv24.zip",
                fec_table="indiv",
                cycle=2024,
            )

        self.assertFalse(result.probe_success)
        self.assertIsNone(result.http_status)
        self.assertIsNotNone(result.error)

    def test_probe_time_is_set_even_on_failure(self) -> None:
        """probe_time must be recorded regardless of success/failure."""
        import requests as req

        with unittest.mock.patch(
            "include.fec_head_probe.requests.head",
            side_effect=req.ConnectionError("down"),
        ):
            result = perform_head_probe(
                url="https://example.com/indiv24.zip",
                fec_table="indiv",
                cycle=2024,
            )
        self.assertIsNotNone(result.probe_time)


if __name__ == "__main__":
    unittest.main()
