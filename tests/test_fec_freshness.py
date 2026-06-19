"""Tests for the Freshness Precedence Rule and branch outcome decisions.

Verifies:
- No load baseline → download_required (never been loaded)
- Probe matches last load etag/last_modified → skip_unchanged
- Probe differs from last load → download_required
- Failed probe with a load baseline → retry_later
  (transient failure: use prior evidence, do not trigger incorrect load)
- Failed probe with no load baseline → hard_fail
  (no evidence to fall back on)

The ``decide_freshness`` function implements Load-Verified Freshness: skip
decisions are based on what was *actually loaded*, not just what was probed.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from include.fec_freshness import BranchOutcome, FreshnessDecision, decide_freshness
from include.fec_head_probe import ProbeResult


def _make_probe(
    *,
    fec_table: str = "indiv",
    cycle: int = 2024,
    http_status: int = 200,
    etag: str | None = '"abc"',
    last_modified: str | None = "Wed, 01 Jan 2026 00:00:00 GMT",
    error: str | None = None,
) -> ProbeResult:
    return ProbeResult(
        fec_table=fec_table,
        cycle=cycle,
        url=f"https://example.com/{fec_table}{str(cycle)[-2:]}.zip",
        probe_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
        http_status=http_status,
        etag=etag,
        last_modified=last_modified,
        content_length=1024,
        error=error,
    )


def _make_load_baseline(
    *,
    etag: str | None = '"abc"',
    last_modified: str | None = "Wed, 01 Jan 2026 00:00:00 GMT",
) -> dict:
    return {
        "etag": etag,
        "last_modified": last_modified,
        "loaded_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }


class TestDecideFreshnessNoBaseline(unittest.TestCase):
    """When there is no prior load, a successful probe always requires download."""

    def test_successful_probe_no_baseline_is_download_required(self) -> None:
        probe = _make_probe(etag='"abc"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT")
        decision = decide_freshness(probe, latest_load=None)
        self.assertEqual(decision.outcome, BranchOutcome.download_required)

    def test_decision_includes_reason(self) -> None:
        probe = _make_probe()
        decision = decide_freshness(probe, latest_load=None)
        self.assertIsInstance(decision.reason, str)
        self.assertTrue(len(decision.reason) > 0)


class TestDecideFreshnessUnchanged(unittest.TestCase):
    """When probe matches the last load baseline, file is skip_unchanged."""

    def test_matching_etag_and_last_modified_is_skip_unchanged(self) -> None:
        probe = _make_probe(etag='"abc"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT")
        baseline = _make_load_baseline(
            etag='"abc"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT"
        )
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.skip_unchanged)

    def test_matching_etag_only_is_skip_unchanged(self) -> None:
        """ETag match alone is sufficient to skip."""
        probe = _make_probe(etag='"abc"', last_modified=None)
        baseline = _make_load_baseline(etag='"abc"', last_modified=None)
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.skip_unchanged)


class TestDecideFreshnessChanged(unittest.TestCase):
    """When probe differs from last load, a download is required."""

    def test_different_etag_is_download_required(self) -> None:
        probe = _make_probe(etag='"new-etag"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT")
        baseline = _make_load_baseline(
            etag='"old-etag"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT"
        )
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.download_required)

    def test_different_last_modified_is_download_required(self) -> None:
        probe = _make_probe(etag='"abc"', last_modified="Thu, 02 Jan 2026 00:00:00 GMT")
        baseline = _make_load_baseline(
            etag='"abc"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT"
        )
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.download_required)

    def test_both_different_is_download_required(self) -> None:
        probe = _make_probe(etag='"new"', last_modified="Thu, 02 Jan 2026 00:00:00 GMT")
        baseline = _make_load_baseline(etag='"old"', last_modified="Wed, 01 Jan 2026 00:00:00 GMT")
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.download_required)

    def test_no_etag_in_probe_but_last_modified_changed_is_download_required(self) -> None:
        """When etag is absent but last_modified changed, download is required."""
        probe = _make_probe(etag=None, last_modified="Thu, 02 Jan 2026 00:00:00 GMT")
        baseline = _make_load_baseline(etag=None, last_modified="Wed, 01 Jan 2026 00:00:00 GMT")
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.download_required)


class TestDecideFreshnessFailedProbe(unittest.TestCase):
    """Failed probes use latest load baseline to decide safely."""

    def test_failed_probe_with_baseline_is_retry_later(self) -> None:
        """Transient failure: don't trigger incorrect load, retry later."""
        probe = _make_probe(http_status=None, etag=None, last_modified=None, error="Timeout")
        baseline = _make_load_baseline()
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.retry_later)

    def test_failed_probe_no_baseline_is_hard_fail(self) -> None:
        """No evidence to fall back on; cannot safely skip or download."""
        probe = _make_probe(http_status=None, etag=None, last_modified=None, error="Timeout")
        decision = decide_freshness(probe, latest_load=None)
        self.assertEqual(decision.outcome, BranchOutcome.hard_fail)

    def test_404_with_baseline_is_retry_later(self) -> None:
        """Server 404 with a known baseline is treated as transient (retry)."""
        probe = _make_probe(http_status=404, etag=None, last_modified=None, error="HTTP 404")
        baseline = _make_load_baseline()
        decision = decide_freshness(probe, latest_load=baseline)
        self.assertEqual(decision.outcome, BranchOutcome.retry_later)

    def test_404_no_baseline_is_hard_fail(self) -> None:
        probe = _make_probe(http_status=404, etag=None, last_modified=None, error="HTTP 404")
        decision = decide_freshness(probe, latest_load=None)
        self.assertEqual(decision.outcome, BranchOutcome.hard_fail)


class TestFreshnessDecisionContract(unittest.TestCase):
    """FreshnessDecision always carries outcome and a non-empty reason."""

    def _all_scenarios(self):
        probe_ok = _make_probe()
        probe_fail = _make_probe(http_status=None, etag=None, last_modified=None, error="err")
        baseline = _make_load_baseline()
        return [
            (probe_ok, None),
            (probe_ok, baseline),
            (probe_fail, baseline),
            (probe_fail, None),
        ]

    def test_decision_always_has_outcome_and_reason(self) -> None:
        for probe, baseline in self._all_scenarios():
            with self.subTest(probe_success=probe.probe_success, has_baseline=baseline is not None):
                d = decide_freshness(probe, latest_load=baseline)
                self.assertIsInstance(d, FreshnessDecision)
                self.assertIsInstance(d.outcome, BranchOutcome)
                self.assertIsInstance(d.reason, str)
                self.assertGreater(len(d.reason), 0)


if __name__ == "__main__":
    unittest.main()
