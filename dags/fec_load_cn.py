"""Airflow DAG: fec_load_cn — per-file-type ingest for FEC Candidate Master (cn).

For each cycle in ``config/pipeline.yaml`` that includes the ``cn`` FecTable,
this DAG runs the full ingest sequence:

1. ``check_freshness_{cycle}``    — HTTP HEAD probe; row appended to
                                    ``metadata._fec_download_state`` on every run.
2. ``branch_cn_{cycle}``          — Freshness Precedence Rule (ADR 0002):
                                    routes to download_and_load or skip.
3. ``download_and_load_cn_{cycle}`` — Download ZIP → load into ``raw.cn_{cycle}``
                                    → record in ``metadata.load_history``.
   *or* ``skip_cn_{cycle}``       — No-op when file is unchanged or probe failed
                                    but a load baseline exists.
4. ``run_dbt_cn``                 — ``dbt run --select tag:cn`` after all cycles.

``schedule=None`` — manual trigger or triggered by an orchestrator DAG.
"""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

from include.fec_download_state import DownloadStateManager
from include.fec_freshness import BranchOutcome, decide_freshness
from include.fec_head_probe import ProbeResult, build_fec_download_url, perform_head_probe
from include.fec_zip_loader import load_fec_zip_to_duckdb
from include.fec_zip_store import retain_or_download_zip
from include.pipeline_config import PIPELINE_CONFIG, build_scope_worklist

logger = logging.getLogger(__name__)

# ─────────────────────────────── Constants ──────────────────────────────── #

FEC_TABLE = "cn"
CN_INNER_FILENAME = "cn.txt"

# Column names for cn — matches include/fec_schemas/cn.py COLUMNS[*].fec_name.
# Defined inline to avoid a pyarrow import at DAG load time.
CN_COLUMNS: list[str] = [
    "cand_id",
    "cand_name",
    "cand_pty_affiliation",
    "cand_election_yr",
    "cand_office_st",
    "cand_office",
    "cand_office_district",
    "cand_ici",
    "cand_status",
    "cand_pcc",
    "cand_st1",
    "cand_st2",
    "cand_city",
    "cand_st",
    "cand_zip",
]

DUCKDB_PATH = Path(
    os.getenv(
        "DUCKDB_PATH",
        str(Path(os.getenv("DATA_DIR", "./data")) / "duckdb" / "money_trail.duckdb"),
    )
)

DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt"

# ──────────────────────── Cycle list from config ────────────────────────── #

_worklist = build_scope_worklist(PIPELINE_CONFIG)
CN_CYCLES: list[int] = sorted(
    {t.cycle for t in _worklist.targets if t.fec_table == FEC_TABLE}
)

# ────────────────────────────── Task functions ──────────────────────────── #


def _check_freshness(cycle: int, **context) -> None:
    """HTTP HEAD probe for cn_{cycle}; always append a row to _fec_download_state."""
    url = build_fec_download_url(FEC_TABLE, cycle)
    probe = perform_head_probe(url, fec_table=FEC_TABLE, cycle=cycle)

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    state_mgr = DownloadStateManager(str(DUCKDB_PATH))

    # Compute whether the content has changed vs the latest _fec_download_state entry.
    state_changed = state_mgr.detect_change(
        file_type=FEC_TABLE,
        cycle=cycle,
        current_etag=probe.etag,
        current_last_modified=probe.last_modified,
    )

    # Always append — regardless of change detection outcome.
    state_mgr.record_download_state_check(
        file_type=FEC_TABLE,
        cycle=cycle,
        checked_at=probe.probe_time,
        etag=probe.etag,
        last_modified=probe.last_modified,
        changed=state_changed,
        downloaded=False,
    )

    # Push the full probe result and state_changed flag to XCom for downstream tasks.
    context["ti"].xcom_push(
        key=f"probe_{cycle}",
        value={
            "fec_table": probe.fec_table,
            "cycle": probe.cycle,
            "url": probe.url,
            "probe_time": probe.probe_time.isoformat(),
            "http_status": probe.http_status,
            "etag": probe.etag,
            "last_modified": probe.last_modified,
            "content_length": probe.content_length,
            "error": probe.error,
            "state_changed": state_changed,
        },
    )


def _branch_freshness(cycle: int, **context) -> str:
    """Apply Freshness Precedence Rule; return the task_id of the next step."""
    ti = context["ti"]
    probe_data = ti.xcom_pull(
        task_ids=f"check_freshness_{cycle}", key=f"probe_{cycle}"
    )
    if probe_data is None:
        raise AirflowException(
            f"No probe XCom for cn_{cycle}; check_freshness task may have failed."
        )

    probe_time = datetime.fromisoformat(probe_data["probe_time"])
    if probe_time.tzinfo is None:
        probe_time = probe_time.replace(tzinfo=timezone.utc)

    probe = ProbeResult(
        fec_table=probe_data["fec_table"],
        cycle=probe_data["cycle"],
        url=probe_data["url"],
        probe_time=probe_time,
        http_status=probe_data["http_status"],
        etag=probe_data["etag"],
        last_modified=probe_data["last_modified"],
        content_length=probe_data["content_length"],
        error=probe_data["error"],
    )

    state_mgr = DownloadStateManager(str(DUCKDB_PATH))
    latest_load = state_mgr.get_latest_load_baseline(FEC_TABLE, cycle)

    decision = decide_freshness(probe, latest_load)
    logger.info(
        "Freshness decision for cn_%s: %s — %s",
        cycle,
        decision.outcome.value,
        decision.reason,
    )

    if decision.outcome == BranchOutcome.hard_fail:
        raise AirflowException(decision.reason)

    if decision.outcome == BranchOutcome.download_required:
        return f"download_and_load_cn_{cycle}"

    # skip_unchanged or retry_later — do not download this cycle.
    if decision.outcome == BranchOutcome.retry_later:
        logger.warning("Retry later for cn_%s: %s", cycle, decision.reason)

    return f"skip_cn_{cycle}"


def _download_and_load(cycle: int, **context) -> None:
    """Download cn_{cycle} ZIP (if needed) and load into raw.cn_{cycle}."""
    ti = context["ti"]
    probe_data = ti.xcom_pull(
        task_ids=f"check_freshness_{cycle}", key=f"probe_{cycle}"
    )
    url = probe_data["url"]
    etag = probe_data.get("etag")
    last_modified = probe_data.get("last_modified")
    # Use the state-change flag to decide whether to force a re-download.
    # If the probe shows unchanged content vs last check, reuse the cached ZIP.
    state_changed: bool = probe_data.get("state_changed", True)

    zip_path, _downloaded = retain_or_download_zip(
        file_type=FEC_TABLE,
        cycle=cycle,
        url=url,
        changed=state_changed,
    )

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    row_count = load_fec_zip_to_duckdb(
        zip_path=zip_path,
        fec_table=FEC_TABLE,
        cycle=cycle,
        duckdb_path=str(DUCKDB_PATH),
        column_names=CN_COLUMNS,
        inner_filename=CN_INNER_FILENAME,
    )
    logger.info("Loaded %d rows into raw.cn_%s", row_count, cycle)

    state_mgr = DownloadStateManager(str(DUCKDB_PATH))
    state_mgr.record_load(
        file_type=FEC_TABLE,
        cycle=cycle,
        source_url=url,
        source_zip_path=str(zip_path),
        target_parquet_path=f"raw.cn_{cycle}",
        row_count=row_count,
        etag=etag,
        last_modified=last_modified,
    )


def _run_dbt_cn() -> None:
    """Run ``dbt run --select tag:cn`` in the dbt project directory."""
    result = subprocess.run(
        ["dbt", "run", "--select", "tag:cn"],
        cwd=str(DBT_PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error("dbt run --select tag:cn failed:\n%s\n%s", result.stdout, result.stderr)
        raise AirflowException(
            f"dbt run --select tag:cn exited with code {result.returncode}"
        )
    logger.info("dbt run --select tag:cn succeeded:\n%s", result.stdout)


# ─────────────────────────────────── DAG ────────────────────────────────── #

with DAG(
    dag_id="fec_load_cn",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "money-trail"},
    tags=["fec", "cn", "ingest"],
    description=(
        "Per-file-type ingest DAG for FEC Candidate Master (cn): "
        "change detection → conditional download → bulk load → dbt run."
    ),
) as dag:

    per_cycle_terminal_tasks: list = []

    for _cycle in CN_CYCLES:
        check_task = PythonOperator(
            task_id=f"check_freshness_{_cycle}",
            python_callable=_check_freshness,
            op_kwargs={"cycle": _cycle},
        )

        branch_task = BranchPythonOperator(
            task_id=f"branch_cn_{_cycle}",
            python_callable=_branch_freshness,
            op_kwargs={"cycle": _cycle},
        )

        download_load_task = PythonOperator(
            task_id=f"download_and_load_cn_{_cycle}",
            python_callable=_download_and_load,
            op_kwargs={"cycle": _cycle},
        )

        skip_task = EmptyOperator(task_id=f"skip_cn_{_cycle}")

        check_task >> branch_task >> [download_load_task, skip_task]

        per_cycle_terminal_tasks.extend([download_load_task, skip_task])

    run_dbt = PythonOperator(
        task_id="run_dbt_cn",
        python_callable=_run_dbt_cn,
        trigger_rule="none_failed_min_one_success",
    )

    per_cycle_terminal_tasks >> run_dbt
