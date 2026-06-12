"""FEC download state management utilities."""

from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DownloadStateManager:
    """Manage FEC download state and change detection."""

    def __init__(self, duckdb_path: str):
        """
        Initialize manager with DuckDB file path.
        
        Args:
            duckdb_path: Path to DuckDB file (e.g., /path/to/money_trail.duckdb)
        """
        self.duckdb_path = duckdb_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure metadata tables exist in DuckDB."""
        import duckdb

        conn = duckdb.connect(self.duckdb_path, read_only=False)

        try:
            conn.execute("CREATE SCHEMA IF NOT EXISTS metadata")

            # Table: Download state history (one row per check, append-only)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata._fec_download_state (
                    checked_at TIMESTAMP,
                    cycle INTEGER,
                    file_type VARCHAR,
                    etag VARCHAR,
                    last_modified VARCHAR,
                    changed BOOLEAN,
                    downloaded BOOLEAN
                )
            """)

            # Table: Daily observations (one row per file per day)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata._fec_daily_observation (
                    observation_id BIGINT PRIMARY KEY,
                    file_type VARCHAR,
                    cycle INTEGER,
                    observation_date DATE,
                    probe_time TIMESTAMP,
                    http_status INTEGER,
                    etag VARCHAR,
                    last_modified VARCHAR,
                    content_length BIGINT,
                    changed BOOLEAN,
                    recorded_at TIMESTAMP
                )
            """)

            # Table: Load history (one row per successful parquet write)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata.load_history (
                    load_id BIGINT PRIMARY KEY,
                    file_type VARCHAR,
                    cycle INTEGER,
                    source_url VARCHAR,
                    source_zip_path VARCHAR,
                    target_parquet_path VARCHAR,
                    row_count BIGINT,
                    loaded_at TIMESTAMP,
                    etag VARCHAR,
                    last_modified VARCHAR
                )
            """)

            logger.info("Metadata schema ensured")
        finally:
            conn.close()

    def record_download_state_check(
        self,
        file_type: str,
        cycle: int,
        checked_at: datetime,
        etag: Optional[str],
        last_modified: Optional[str],
        changed: bool,
        downloaded: bool,
    ) -> None:
        """Append one row to metadata._fec_download_state for each check."""
        import duckdb

        conn = duckdb.connect(self.duckdb_path, read_only=False)
        try:
            conn.execute(
                """
                INSERT INTO metadata._fec_download_state
                    (checked_at, cycle, file_type, etag, last_modified, changed, downloaded)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [checked_at, cycle, file_type, etag, last_modified, changed, downloaded],
            )
        finally:
            conn.close()

    def record_observation(self, check_results: List[Dict]) -> int:
        """
        Record daily observations from change detection checks.
        
        Args:
            check_results: List of check result dicts from check_file_change()
        
        Returns:
            Number of observations recorded
        """
        import duckdb

        conn = duckdb.connect(self.duckdb_path, read_only=False)

        try:
            observation_date = datetime.utcnow().date()
            recorded_at = datetime.utcnow()

            for result in check_results:
                # Get next observation_id
                next_id_result = conn.execute(
                    "SELECT COALESCE(MAX(observation_id), 0) + 1 FROM metadata._fec_daily_observation"
                ).fetchone()
                observation_id = next_id_result[0]

                conn.execute(
                    """
                    INSERT INTO metadata._fec_daily_observation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        observation_id,
                        result["file_type"],
                        result["cycle"],
                        observation_date,
                        result["checked_at"],
                        result["status_code"],
                        result.get("etag"),
                        result.get("last_modified"),
                        result.get("content_length"),
                        result.get("changed", False),
                        recorded_at,
                    ],
                )

            logger.info(f"Recorded {len(check_results)} daily observations")
            return len(check_results)

        finally:
            conn.close()

    def get_latest_state(self, file_type: str, cycle: int) -> Optional[Dict]:
        """
        Get latest download state for a file type and cycle.
        
        Args:
            file_type: FEC file type (e.g., "indiv")
            cycle: Election cycle (e.g., 2024)
        
        Returns:
            Dict with latest state, or None if not found
        """
        import duckdb

        conn = duckdb.connect(self.duckdb_path, read_only=True)

        try:
            result = conn.execute(
                """
                SELECT checked_at, etag, last_modified, changed, downloaded
                FROM metadata._fec_download_state
                WHERE file_type = ? AND cycle = ?
                ORDER BY checked_at DESC
                LIMIT 1
                """,
                [file_type, cycle],
            ).fetchone()

            if result:
                return {
                    "checked_at": result[0],
                    "etag": result[1],
                    "last_modified": result[2],
                    "changed": result[3],
                    "downloaded": result[4],
                }
            return None

        finally:
            conn.close()

    def detect_change(
        self,
        file_type: str,
        cycle: int,
        current_etag: Optional[str],
        current_last_modified: Optional[str],
    ) -> bool:
        """
        Detect if file has changed since last check.
        
        Compares ETag and Last-Modified against stored state.
        Change is detected if either tag changed.
        
        Args:
            file_type: FEC file type
            cycle: Election cycle
            current_etag: Current ETag from HEAD request
            current_last_modified: Current Last-Modified from HEAD request
        
        Returns:
            True if changed, False if unchanged or never checked before
        """
        latest = self.get_latest_state(file_type, cycle)

        if not latest:
            # Never checked before - consider it "not changed yet"
            # (will download if missing locally)
            return False

        # Change detected if either ETag or Last-Modified differ
        changed = (
            latest["etag"] != current_etag or 
            latest["last_modified"] != current_last_modified
        )

        return changed

    def record_load(
        self,
        file_type: str,
        cycle: int,
        source_url: str,
        source_zip_path: str,
        target_parquet_path: str,
        row_count: int,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
    ) -> int:
        """
        Record successful load to parquet.
        
        Args:
            file_type: FEC file type
            cycle: Election cycle
            source_url: FEC URL downloaded from
            source_zip_path: Local path to ZIP file
            target_parquet_path: Path to output parquet file
            row_count: Number of rows in parquet
            etag: ETag of downloaded file
            last_modified: Last-Modified of downloaded file
        
        Returns:
            Load ID
        """
        import duckdb

        conn = duckdb.connect(self.duckdb_path, read_only=False)

        try:
            # Get next load_id
            next_id_result = conn.execute(
                "SELECT COALESCE(MAX(load_id), 0) + 1 FROM metadata.load_history"
            ).fetchone()
            load_id = next_id_result[0]

            conn.execute(
                """
                INSERT INTO metadata.load_history VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    load_id,
                    file_type,
                    cycle,
                    source_url,
                    source_zip_path,
                    target_parquet_path,
                    row_count,
                    datetime.utcnow(),
                    etag,
                    last_modified,
                ],
            )

            logger.info(f"Recorded load {load_id}: {file_type}_{cycle} -> {target_parquet_path}")
            return load_id

        finally:
            conn.close()
