# FEC Pipeline Context

This document extracts the FEC-specific context from CONTEXT.md to serve as a focused reference for data imports.

FEC campaign finance data pipeline: bulk download extraction, DuckDB loading, and dbt-based cleaning and QA, orchestrated by Apache Airflow.

Language

- Cycle: A two-year FEC election cycle identified by the ending even year (e.g., `2024` covers 2023–2024). All file downloads and raw tables are partitioned by cycle.

- Cycle Range: A string "YYYY-YYYY" (e.g., "2010-2022") representing a contiguous span of Cycles stepping by 2; both endpoints inclusive.

- File Type: One of the FEC bulk download categories: `indiv`, `cn`, `cm`, `oth`, `oppexp`, `ccl`, `weball`, `pas2`, or `indexp`.

- weball: The FEC "All Candidates" summary file; named `weball<YY>.zip` on bulk downloads.

Layers & Concepts

- Raw Layer: DuckDB tables that hold bulk data exactly as downloaded — one table per file type per cycle. Owned by Airflow; read by dbt.

- Download State: A DuckDB table (`metadata._fec_download_state`) recording history of HEAD checks per file type and cycle (timestamp, ETag, Last-Modified, change detected). Owned by Airflow.

- Daily Observation: A recorded result of a scheduled HTTP HEAD check for a File Type and Cycle on a given day; includes probe time and response metadata.

- Observation Backfill: Creating missed Daily Observations after downtime by running pending probes on the next available run. Backfilled rows remain distinguishable by probe time.

- Change Detection: An HTTP HEAD request to the FEC download URL compared against Download State. Triggers download/load only when remote file changed.

- Style: A named, reusable download profile defined in pipeline config specifying file types to fetch and whether change detection is active.

- Parallelism: Pipeline configuration controlling whether orchestrator DAG processes cycles sequentially or in parallel; declared in config/pipeline.yaml.

- Raw Table: A DuckDB table in the `raw` schema named `raw.<file_type>_<cycle>` (e.g., `raw.indiv_2024`). FEC column names used as-is.

- Cross-Cycle View: A dbt-managed DuckDB view in `marts` schema named `<file_type>_all` that unions Raw Tables across cycles and adds a `cycle` column.

- Direct ZIP Load: DuckDB can read pipe-delimited files directly from ZIP archives (e.g., `read_csv('file.zip!inner.txt', ...)`). For `indiv`, an explicit inner-path is required due to multiple files in the ZIP.

- Schema File: Python modules under `include/fec_schemas/` define ordered `FECColumn` entries (raw name, alias, pyarrow type). Raw Tables use FEC names; dbt staging models apply readable aliases.

References

- See docs/adr/0001-bulk-downloads-over-api.md and other ADRs for decision records.

