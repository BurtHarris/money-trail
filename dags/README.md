# Airflow DAGs for FEC Data Pipeline

This directory contains Airflow DAGs for the Money Trail FEC data pipeline.

## DAGs

### `fec_change_detection` (Paused by Default)

**Purpose**: Detect FEC file updates and selectively download changed files.

**Schedule**: Daily at 2 AM UTC (configurable; starts paused)

**Workflow**:
1. **check_all_files**: Perform HTTP HEAD requests to all FEC file URLs
   - File types: indiv, cn, cm, ccl, oth, pas2, oppexp, weball
   - Cycles: 2024, 2022, 2020 (configurable)
   - Records response metadata (ETag, Last-Modified, Content-Length, status)
   
2. **record_observations**: Write Daily Observations to `metadata._fec_daily_observation`
   - One row per file checked
   - Useful for tracking FEC availability, update frequency, downtime
   
3. **determine_files_to_download**: Branch task
   - Compares ETag/Last-Modified against stored state in `metadata._fec_download_state`
   - Checks if local parquet file exists
   - Routes to download or skip based on:
     - File changed on FEC server? → Download
     - File missing locally? → Download
     - File unchanged and local copy exists? → Skip
   
4. **download_changed_files** (conditional):
   - Download ZIP from FEC URL
   - Extract CSV from ZIP
   - Write to `data/duckdb/<file_type>_<cycle>.parquet`
   - Record load metadata in `metadata.load_history`
   
5. **done**: Terminal task

**Design Principles** (Conservative Time Usage):
- **HEAD-only checks**: Avoid downloading large ZIPs just to detect updates
- **ETag/Last-Modified comparison**: Fast, no full-file download
- **Skip if unchanged**: Only download files that actually changed
- **Skip if local exists**: Assuming ZIP already cached locally; only re-download if missing
- **Batch checks**: One DAG run checks all files (not per-file DAGs)

**Enabling the DAG**:
```bash
# In Airflow UI: Admin > DAGs > fec_change_detection > Toggle "Paused"
# Or via CLI:
airflow dags unpause fec_change_detection

# Trigger manually (e.g., for testing):
airflow dags trigger fec_change_detection
```

**Monitoring**:
- **Logs**: Check Airflow UI for task logs (click task > Logs tab)
- **Observations**: Query `metadata._fec_daily_observation` to see check history
- **Downloads**: Query `metadata.load_history` to see what was loaded

## Metadata Tables

All tables live in the `metadata` schema in `data/duckdb/money_trail.duckdb`.

### `metadata._fec_download_state`
Full history of FEC file metadata checks.

| Column | Type | Description |
|--------|------|-------------|
| state_id | BIGINT | Unique identifier |
| file_type | VARCHAR | FEC file type (indiv, cn, etc.) |
| cycle | INTEGER | Election cycle (2024, 2022, etc.) |
| url | VARCHAR | FEC download URL |
| probe_time | TIMESTAMP | When HTTP HEAD request was performed |
| http_status | INTEGER | HTTP response status code |
| etag | VARCHAR | ETag header (change detection) |
| last_modified | VARCHAR | Last-Modified header (change detection) |
| content_length | BIGINT | File size in bytes |
| changed | BOOLEAN | True if changed since last check |
| checked_at | TIMESTAMP | When observation was recorded |

### `metadata._fec_daily_observation`
One row per file checked per day. Used to detect trends, outages, update frequency.

| Column | Type | Description |
|--------|------|-------------|
| observation_id | BIGINT | Unique identifier |
| file_type | VARCHAR | FEC file type |
| cycle | INTEGER | Election cycle |
| observation_date | DATE | Date of observation |
| probe_time | TIMESTAMP | When HTTP HEAD request occurred |
| http_status | INTEGER | HTTP response status |
| etag | VARCHAR | ETag (for change detection) |
| last_modified | VARCHAR | Last-Modified (for change detection) |
| content_length | BIGINT | File size in bytes |
| changed | BOOLEAN | True if changed since last check |
| recorded_at | TIMESTAMP | When row was inserted |

### `metadata.load_history`
One row per successful parquet load.

| Column | Type | Description |
|--------|------|-------------|
| load_id | BIGINT | Unique identifier |
| file_type | VARCHAR | FEC file type |
| cycle | INTEGER | Election cycle |
| source_url | VARCHAR | FEC URL downloaded from |
| source_zip_path | VARCHAR | Local path to ZIP file |
| target_parquet_path | VARCHAR | Path to output parquet file |
| row_count | BIGINT | Number of rows in parquet |
| loaded_at | TIMESTAMP | When parquet was written |
| etag | VARCHAR | ETag of source file |
| last_modified | VARCHAR | Last-Modified of source file |

## Next DAGs (TODO)

- `fec_download_and_load`: Full end-to-end DAG that downloads FEC files and writes parquet
- `fec_dbt_transform`: Trigger dbt to materialize staging and marts views
- `fec_daily_pipeline`: Orchestrate all three DAGs together

## Architecture References

- **ADR 0002**: Download State tracking
- **ADR 0008**: Daily Observation Collector
- **ADR 0009**: Duck Lake (parquet storage + DuckDB queries)
