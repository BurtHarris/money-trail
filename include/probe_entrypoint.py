from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

import requests

from include.db_init import init_duckdb
from include.pipeline_config import PIPELINE_CONFIG, PipelineConfig
from include.probe_ledger import ProbeObservation, probe_plan_units

_DEFAULT_DUCKDB_PATH = Path("/workspaces/money-trail/data/duckdb/money_trail.duckdb")


def run_probe_plan(
    config: PipelineConfig = PIPELINE_CONFIG,
    duckdb_path: str = str(_DEFAULT_DUCKDB_PATH),
    checked_at: datetime | None = None,
    request_head: Callable[..., requests.Response] | None = None,
) -> list[ProbeObservation]:
    """Build plan units from pipeline config and record probe observations."""
    init_duckdb(duckdb_path)
    plan = config.build_plan()
    return probe_plan_units(
        plan_units=plan.units,
        duckdb_path=duckdb_path,
        checked_at=checked_at,
        request_head=request_head,
    )
