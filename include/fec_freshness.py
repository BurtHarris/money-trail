"""Freshness Precedence Rule and branch outcome decisions.

Implements Load-Verified Freshness: the decision to skip a download is based
on what was *actually loaded* (the latest load baseline from ``load_history``),
not just what was probed.  This prevents both unnecessary downloads (when the
file hasn't changed since the last load) and incorrect skips (when a transient
probe failure would otherwise suppress a needed download).

Branch outcomes:

``download_required``
    The file is new or the probe shows a different version than last loaded.
    Download and load immediately.

``skip_unchanged``
    The probe matches the last load baseline.  No download needed this run.

``retry_later``
    The probe failed but a load baseline exists.  Cannot determine change
    status; defer to the next scheduled run.

``hard_fail``
    The probe failed and there is no load baseline at all.  No safe decision
    is possible; the operator must intervene.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from include.fec_head_probe import ProbeResult


class BranchOutcome(str, Enum):
    """Stable vocabulary for ingestion branch decisions."""

    download_required = "download_required"
    skip_unchanged = "skip_unchanged"
    retry_later = "retry_later"
    hard_fail = "hard_fail"


@dataclass
class FreshnessDecision:
    """Result of a Freshness Precedence Rule evaluation.

    Attributes:
        outcome: The branch to take.
        reason:  Human-readable explanation for logs and metadata.
    """

    outcome: BranchOutcome
    reason: str


def decide_freshness(
    probe: ProbeResult,
    latest_load: Optional[dict],
) -> FreshnessDecision:
    """Apply the Freshness Precedence Rule and return a branch decision.

    The rule hierarchy is:

    1. If the probe failed (not a clean 200):
       - Has a load baseline → ``retry_later`` (transient; don't guess)
       - No load baseline    → ``hard_fail``   (no evidence at all)

    2. Probe succeeded:
       - No load baseline                → ``download_required`` (never loaded)
       - etag or last_modified differ    → ``download_required`` (file changed)
       - Both etag and last_modified match (or both absent and equal)
         → ``skip_unchanged``

    Args:
        probe:       Result of the current Universal HEAD Probe.
        latest_load: Dict with ``etag`` and ``last_modified`` from the most
                     recent successful load, or ``None`` if the file has
                     never been loaded.

    Returns:
        A :class:`FreshnessDecision` with :attr:`~FreshnessDecision.outcome`
        and a descriptive :attr:`~FreshnessDecision.reason`.
    """
    if not probe.probe_success:
        if latest_load is not None:
            return FreshnessDecision(
                outcome=BranchOutcome.retry_later,
                reason=(
                    f"Probe failed ({probe.error!r}) for {probe.fec_table}_{probe.cycle}; "
                    "deferring to next run — load baseline exists."
                ),
            )
        return FreshnessDecision(
            outcome=BranchOutcome.hard_fail,
            reason=(
                f"Probe failed ({probe.error!r}) for {probe.fec_table}_{probe.cycle} "
                "and no load baseline exists; operator intervention required."
            ),
        )

    # Probe succeeded.
    if latest_load is None:
        return FreshnessDecision(
            outcome=BranchOutcome.download_required,
            reason=(
                f"{probe.fec_table}_{probe.cycle} has never been loaded; "
                "download required."
            ),
        )

    # Compare probe headers against last load.
    etag_matches = probe.etag == latest_load.get("etag")
    lm_matches = probe.last_modified == latest_load.get("last_modified")

    if etag_matches and lm_matches:
        return FreshnessDecision(
            outcome=BranchOutcome.skip_unchanged,
            reason=(
                f"{probe.fec_table}_{probe.cycle} probe matches last load "
                f"(etag={probe.etag!r}, last_modified={probe.last_modified!r}); "
                "skip."
            ),
        )

    changed_fields = []
    if not etag_matches:
        changed_fields.append(
            f"etag {latest_load.get('etag')!r} → {probe.etag!r}"
        )
    if not lm_matches:
        changed_fields.append(
            f"last_modified {latest_load.get('last_modified')!r} → {probe.last_modified!r}"
        )

    return FreshnessDecision(
        outcome=BranchOutcome.download_required,
        reason=(
            f"{probe.fec_table}_{probe.cycle} changed since last load: "
            + ", ".join(changed_fields)
        ),
    )
