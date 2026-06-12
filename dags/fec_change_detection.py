"""
FEC Change Detection DAG

Performs HTTP HEAD requests to detect FEC file updates.
Records Daily Observations (ADR 0008) and marks files for download if changed.

This DAG is paused by default. Enable it to run on a schedule or trigger manually.
Conservative approach: Uses HTTP HEAD to avoid large downloads during checks.
"""

from datetime import datetime, timedelta
from typing import Dict, List
import logging
import os
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.exceptions import AirflowException
import requests

from include.fec_download_state import DownloadStateManager
from include.fec_zip_store import build_raw_zip_path, retain_or_download_zip

logger = logging.getLogger(__name__)

# FEC file types to monitor
FILE_TYPES = ["indiv", "cn", "cm", "ccl", "oth", "pas2", "oppexp", "weball"]

# Cycles to monitor (adjust as needed)
CYCLES = [2024, 2022, 2020]

# FEC bulk download base URL
FEC_BASE_URL = "https://www.fec.gov/files/bulk-downloads"

# Default timeout for HTTP requests
HEAD_REQUEST_TIMEOUT = 10
DUCKDB_PATH = Path(
    os.getenv(
        "DUCKDB_PATH",
        str(Path(os.getenv("DATA_DIR", "./data")) / "duckdb" / "money_trail.duckdb"),
    )
)


def build_fec_url(file_type: str, cycle: int) -> str:
    """Build FEC bulk download URL for a file type and cycle."""
    # Example: https://www.fec.gov/files/bulk-downloads/2024/indiv24.zip
    yy = str(cycle)[-2:]  # Convert 2024 -> "24"
    return f"{FEC_BASE_URL}/{cycle}/{file_type}{yy}.zip"


def check_file_change(file_type: str, cycle: int) -> Dict:
    """
    Perform HTTP HEAD request to check if FEC file has changed.
    
    Returns:
        dict with keys:
            - url: FEC download URL
            - file_type: FEC file type code
            - cycle: Election cycle
            - status_code: HTTP response status
            - etag: ETag header (if present)
            - last_modified: Last-Modified header (if present)
            - content_length: Content-Length header (if present)
            - changed: True if file changed since last check
            - error: Error message (if any)
            - checked_at: Datetime of check (ISO format)
    """
    url = build_fec_url(file_type, cycle)
    result = {
        "url": url,
        "file_type": file_type,
        "cycle": cycle,
        "status_code": None,
        "etag": None,
        "last_modified": None,
        "content_length": None,
        "changed": False,
        "error": None,
        "checked_at": None,
    }
    checked_at = datetime.utcnow()
    result["checked_at"] = checked_at.isoformat()

    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    state_manager = DownloadStateManager(str(DUCKDB_PATH))

    try:
        response = requests.head(url, timeout=HEAD_REQUEST_TIMEOUT, allow_redirects=True)
        result["status_code"] = response.status_code

        if response.status_code == 200:
            result["etag"] = response.headers.get("ETag")
            result["last_modified"] = response.headers.get("Last-Modified")
            result["content_length"] = response.headers.get("Content-Length")
            result["changed"] = state_manager.detect_change(
                file_type=file_type,
                cycle=cycle,
                current_etag=result["etag"],
                current_last_modified=result["last_modified"],
            )

        elif response.status_code == 404:
            result["error"] = "File not found on FEC server (404)"
        else:
            result["error"] = f"HTTP {response.status_code}"

    except requests.Timeout:
        result["error"] = f"HEAD request timeout after {HEAD_REQUEST_TIMEOUT}s"
    except requests.RequestException as e:
        result["error"] = f"Request error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
    finally:
        state_manager.record_download_state_check(
            file_type=file_type,
            cycle=cycle,
            checked_at=checked_at,
            etag=result.get("etag"),
            last_modified=result.get("last_modified"),
            changed=result.get("changed", False),
            downloaded=False,
        )

    return result


def check_all_files(**context) -> List[Dict]:
    """
    Check all configured (file_type, cycle) pairs for updates.
    
    Records Daily Observations in metadata._fec_daily_observation table.
    Returns list of results.
    """
    ti = context["task_instance"]
    results = []

    logger.info(f"Starting change detection for {len(FILE_TYPES)} file types x {len(CYCLES)} cycles")

    for file_type in FILE_TYPES:
        for cycle in CYCLES:
            result = check_file_change(file_type, cycle)
            results.append(result)
            
            status = "OK" if result["status_code"] == 200 else "ERROR"
            logger.info(f"[{status}] {file_type}_{cycle}: {result['error'] or 'No error'}")

    # TODO: Write results to metadata._fec_daily_observation table
    # insert_daily_observations(results)

    # Push results to XCom for downstream tasks
    ti.xcom_push(key="check_results", value=results)

    return results


def determine_files_to_download(**context) -> str:
    """
    Analyze check results and determine which files need download.
    
    Decision logic:
    - If status_code != 200: Skip (file unavailable)
    - If changed or not_yet_downloaded: Mark for download
    - Otherwise: Skip (already have latest version)
    
    Returns branch task ID: "download_changed_files" or "skip_download"
    """
    ti = context["task_instance"]
    results = ti.xcom_pull(task_ids="check_all_files", key="check_results")

    # Annotate each result with whether the local ZIP is absent.
    for r in results:
        if r["status_code"] == 200:
            zip_path = build_raw_zip_path(r["file_type"], r["cycle"])
            r["missing_locally"] = not zip_path.exists()

    files_to_download = [r for r in results if r["status_code"] == 200 and (r["changed"] or r.get("missing_locally"))]

    if files_to_download:
        logger.info(f"Marking {len(files_to_download)} files for download")
        ti.xcom_push(key="files_to_download", value=files_to_download)
        return "download_changed_files"
    else:
        logger.info("No files need updating")
        return "skip_download"


def download_changed_files(**context):
    """
    Download files marked for update, retaining existing ZIPs when unchanged.

    For each file in the download list:
    1. Compute the canonical local path: data/raw/<file_type>_<cycle>.zip
    2. If the ZIP already exists locally and the file has not changed since
       the last check, reuse the retained copy (no network request).
    3. Otherwise download the ZIP from the FEC URL and save it to data/raw/.

    Retained ZIPs allow loads to be re-run without re-fetching from FEC.
    """
    ti = context["task_instance"]
    files_to_download = ti.xcom_pull(task_ids="determine_files_to_download", key="files_to_download")

    logger.info("Processing %d FEC files...", len(files_to_download))

    for file_info in files_to_download:
        file_type = file_info["file_type"]
        cycle = file_info["cycle"]
        url = file_info["url"]
        changed = file_info.get("changed", False)

        zip_path, downloaded = retain_or_download_zip(
            file_type=file_type,
            cycle=cycle,
            url=url,
            changed=changed,
        )

        if downloaded:
            logger.info(f"Downloaded {file_type}_{cycle} -> {zip_path}")
        else:
            logger.info(f"Reused retained ZIP for {file_type}_{cycle}: {zip_path}")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "fec_change_detection",
    default_args=default_args,
    description="FEC change detection and selective download (ADR 0008, ADR 0002)",
    schedule_interval="0 2 * * *",  # Daily at 2 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    is_paused_upon_creation=True,  # Start disabled; enable when ready
    tags=["fec", "change-detection"],
) as dag:

    # Check all FEC files for updates
    check_files = PythonOperator(
        task_id="check_all_files",
        python_callable=check_all_files,
        provide_context=True,
    )

    # Determine which files need download
    branch_download = BranchPythonOperator(
        task_id="determine_files_to_download",
        python_callable=determine_files_to_download,
        provide_context=True,
    )

    # Download updated files
    download_files = PythonOperator(
        task_id="download_changed_files",
        python_callable=download_changed_files,
        provide_context=True,
    )

    # Skip if no updates needed
    skip = EmptyOperator(task_id="skip_download")

    # Final task (for both branches)
    done = EmptyOperator(task_id="done", trigger_rule="none_failed_min_one_success")

    # DAG flow
    check_files >> branch_download >> [download_files, skip] >> done
