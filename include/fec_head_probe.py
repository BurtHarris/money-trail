"""Universal HEAD Probe for FEC bulk download URLs.

Performs HTTP HEAD requests against FEC bulk-download URLs and returns a
:class:`ProbeResult` capturing the outcome — whether the request succeeded
or failed.  Failed probes are first-class observations; callers must record
*all* results to the probe ledger regardless of outcome.

URL pattern: ``https://www.fec.gov/files/bulk-downloads/<cycle>/<fec_table><yy>.zip``
Example:      ``https://www.fec.gov/files/bulk-downloads/2024/indiv24.zip``
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_FEC_BULK_BASE_URL = "https://www.fec.gov/files/bulk-downloads"
_DEFAULT_TIMEOUT = 10  # seconds


def build_fec_download_url(fec_table: str, cycle: int) -> str:
    """Return the canonical FEC bulk-download ZIP URL for *fec_table* / *cycle*.

    Args:
        fec_table: FEC short code, e.g. ``"indiv"``, ``"cn"``.
        cycle:     Even-year election cycle, e.g. ``2024``.

    Returns:
        Full URL string, e.g.
        ``"https://www.fec.gov/files/bulk-downloads/2024/indiv24.zip"``.
    """
    yy = str(cycle)[-2:]
    return f"{_FEC_BULK_BASE_URL}/{cycle}/{fec_table}{yy}.zip"


@dataclass
class ProbeResult:
    """Outcome of one Universal HEAD Probe attempt.

    A ProbeResult is a first-class observation regardless of success or
    failure.  :attr:`probe_success` is ``True`` only when the server
    returned HTTP 200 with no error.
    """

    fec_table: str
    cycle: int
    url: str
    probe_time: datetime
    http_status: Optional[int]
    etag: Optional[str]
    last_modified: Optional[str]
    content_length: Optional[int]
    error: Optional[str]

    @property
    def probe_success(self) -> bool:
        """``True`` iff the probe returned HTTP 200 with no error."""
        return self.http_status == 200 and self.error is None


def perform_head_probe(
    url: str,
    fec_table: str,
    cycle: int,
    timeout: int = _DEFAULT_TIMEOUT,
) -> ProbeResult:
    """Perform an HTTP HEAD request and return a :class:`ProbeResult`.

    The probe time is recorded before the network call so that even
    network failures have an accurate timestamp.  All outcomes —
    including non-200 responses and exceptions — are returned as
    :class:`ProbeResult` with :attr:`~ProbeResult.probe_success` set
    accordingly.  Callers should never swallow or discard the result.

    Args:
        url:       Full URL to probe.
        fec_table: FEC short code for the target file type.
        cycle:     Election cycle year.
        timeout:   HTTP HEAD timeout in seconds.

    Returns:
        A :class:`ProbeResult` capturing the full probe outcome.
    """
    probe_time = datetime.now(tz=timezone.utc)

    http_status: Optional[int] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    content_length: Optional[int] = None
    error: Optional[str] = None

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        http_status = response.status_code

        if http_status == 200:
            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
            raw_cl = response.headers.get("Content-Length")
            if raw_cl is not None:
                try:
                    content_length = int(raw_cl)
                except (ValueError, TypeError):
                    content_length = None
        else:
            error = f"HTTP {http_status}"

    except requests.Timeout as exc:
        error = f"Timeout: {exc}"
    except requests.RequestException as exc:
        error = f"Request error: {exc}"
    except Exception as exc:  # noqa: BLE001
        error = f"Unexpected error: {exc}"

    result = ProbeResult(
        fec_table=fec_table,
        cycle=cycle,
        url=url,
        probe_time=probe_time,
        http_status=http_status,
        etag=etag,
        last_modified=last_modified,
        content_length=content_length,
        error=error,
    )

    log_level = logging.DEBUG if result.probe_success else logging.WARNING
    logger.log(
        log_level,
        "HEAD probe %s_%s: status=%s success=%s error=%s",
        fec_table,
        cycle,
        http_status,
        result.probe_success,
        error,
    )
    return result
