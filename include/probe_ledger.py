from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

import duckdb
import requests

from include.pipeline_config import PlanUnit

FEC_BULK_DOWNLOAD_ROOT = "https://www.fec.gov/files/bulk-downloads"


@dataclass(frozen=True)
class ProbeObservation:
    checked_at: datetime
    cycle: int
    file_type: str
    etag: str | None
    last_modified: str | None
    changed: bool | None
    downloaded: bool
    probe_ok: bool
    status_code: int | None
    observed_url: str | None
    error_message: str | None


def build_bulk_zip_url(cycle: int, file_type: str) -> str:
    return f"{FEC_BULK_DOWNLOAD_ROOT}/{cycle}/{file_type}.zip"


def probe_url(
    url: str,
    checked_at: datetime | None = None,
    request_head: Callable[..., requests.Response] | None = None,
) -> ProbeObservation:
    observed_at = checked_at or datetime.now(timezone.utc)
    head_request = request_head or requests.head
    try:
        response = head_request(url, timeout=30, allow_redirects=True)
        return ProbeObservation(
            checked_at=observed_at,
            cycle=-1,
            file_type="",
            etag=response.headers.get("ETag"),
            last_modified=response.headers.get("Last-Modified"),
            changed=None,
            downloaded=False,
            probe_ok=True,
            status_code=response.status_code,
            observed_url=getattr(response, "url", url),
            error_message=None,
        )
    except requests.RequestException as exc:
        return ProbeObservation(
            checked_at=observed_at,
            cycle=-1,
            file_type="",
            etag=None,
            last_modified=None,
            changed=None,
            downloaded=False,
            probe_ok=False,
            status_code=None,
            observed_url=url,
            error_message=str(exc),
        )


def append_probe_observation(duckdb_path: str, observation: ProbeObservation) -> None:
    with duckdb.connect(duckdb_path) as con:
        con.execute(
            """
            INSERT INTO metadata._fec_download_state (
                checked_at,
                cycle,
                file_type,
                etag,
                last_modified,
                changed,
                downloaded,
                probe_ok,
                status_code,
                observed_url,
                error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                observation.checked_at,
                observation.cycle,
                observation.file_type,
                observation.etag,
                observation.last_modified,
                observation.changed,
                observation.downloaded,
                observation.probe_ok,
                observation.status_code,
                observation.observed_url,
                observation.error_message,
            ],
        )


def probe_plan_unit(
    plan_unit: PlanUnit,
    duckdb_path: str,
    checked_at: datetime | None = None,
    request_head: Callable[..., requests.Response] | None = None,
) -> ProbeObservation:
    url = build_bulk_zip_url(plan_unit.cycle, plan_unit.file_type)
    raw_observation = probe_url(url, checked_at=checked_at, request_head=request_head)
    observation = ProbeObservation(
        checked_at=raw_observation.checked_at,
        cycle=plan_unit.cycle,
        file_type=plan_unit.file_type,
        etag=raw_observation.etag,
        last_modified=raw_observation.last_modified,
        changed=raw_observation.changed,
        downloaded=False,
        probe_ok=raw_observation.probe_ok,
        status_code=raw_observation.status_code,
        observed_url=raw_observation.observed_url,
        error_message=raw_observation.error_message,
    )
    append_probe_observation(duckdb_path, observation)
    return observation


def probe_plan_units(
    plan_units: list[PlanUnit],
    duckdb_path: str,
    checked_at: datetime | None = None,
    request_head: Callable[..., requests.Response] | None = None,
) -> list[ProbeObservation]:
    observations: list[ProbeObservation] = []
    for unit in plan_units:
        # Universal probing must not be gated by style.change_detection.
        observations.append(
            probe_plan_unit(
                plan_unit=unit,
                duckdb_path=duckdb_path,
                checked_at=checked_at,
                request_head=request_head,
            )
        )
    return observations
