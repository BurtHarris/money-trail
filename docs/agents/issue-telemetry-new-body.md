## What to build

Implement a dedicated Airflow telemetry DAG that performs HTTP HEAD checks for every configured Cycle and File Type and writes one Daily Observation row per probe outcome to DuckDB metadata, including failures and retry metadata. This collector is separate from ingest DAGs and is scheduled daily at 12:13 PM America/Los_Angeles, with bootstrap run support and backfill when possible after downtime.

## Acceptance criteria

- [ ] Telemetry DAG exists and is importable by Airflow
- [ ] Reads cycle/file-type targets from pipeline configuration
- [ ] Follows redirects and records final URL metadata
- [ ] Records one observation row for every probe outcome (success and failure)
- [ ] Uses retry policy: 3 attempts with exponential backoff
- [ ] Supports bootstrap run and backfill of missed observation dates when possible
- [ ] Stores timestamps in UTC and captures local date for America/Los_Angeles reporting

## Blocked by

- #10 (config/pipeline.yaml)
- #11 (DuckDB schema bootstrap)
