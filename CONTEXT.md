# Money Trail

FEC campaign finance data pipeline: bulk download extraction, DuckDB loading, and dbt-based cleaning and QA, orchestrated by Apache Airflow.

## Language

**Cycle**:
A two-year FEC election cycle identified by the ending even year (e.g., `2024` covers 2023–2024). All file downloads and raw tables are partitioned by cycle.
_Avoid_: election year, period, filing year

**Cycle Range**:
A string of the form `"YYYY-YYYY"` (e.g., `"2010-2022"`) in the pipeline configuration representing a contiguous span of Cycles stepping by 2. Both endpoints are inclusive.
_Avoid_: cycle list, year range

**File Type**:
One of the FEC bulk download categories: `indiv` (individual contributions), `cn` (candidate master), `cm` (committee master), `oth` (committee-to-committee transfers), `oppexp` (operating expenditures), `ccl` (candidate-committee linkage), `weball` (all-candidates financial summary), `pas2` (contributions to candidates), or `indexp` (independent expenditures).
_Avoid_: table, dataset, category

**weball**:
A File Type representing the FEC's "All Candidates" summary file. Contains one record per candidate with aggregate financial statistics (total receipts, disbursements, cash-on-hand, loans, etc.) for the cycle, regardless of when the candidate is up for election. Updated more frequently than the post-cycle candidate summary file but less precise. Named `weball<YY>.zip` on FEC bulk downloads.
_Avoid_: full archive, combined download, all candidates archive

**Raw Layer**:
DuckDB tables that hold FEC bulk data exactly as downloaded — no cleaning, no transformation. One table per file type per cycle. Owned by Airflow; read by dbt.
_Avoid_: staging (reserved for dbt), landing zone

**Download State**:
A DuckDB table (`metadata._fec_download_state`) that records the full history of HEAD check results per file type and cycle — including timestamp, ETag, Last-Modified, and whether a change was detected. Used both for change detection (compare latest row against current HEAD) and for analyzing FEC update frequency per file type. Owned exclusively by Airflow.
_Avoid_: change log, sync state

**Daily Observation**:
One recorded result of a scheduled HTTP HEAD check for a single File Type and Cycle on a given day, regardless of success or failure. Includes probe time and response metadata (when available) so stability and outage gaps are both measurable over time.
_Avoid_: daily delta, daily change row

**Observation Backfill**:
The process of creating missed Daily Observations after downtime (for example, a sleeping laptop) by running pending probes on the next available run. Backfilled rows are still first-class observations and remain distinguishable by their probe time.
_Avoid_: replay, synthetic fill

**Change Detection**:
An HTTP HEAD request to the FEC download URL compared against the stored Download State. Triggers a download and load only when the remote file has changed.
_Avoid_: delta detection, incremental check

**Style**:
A named, reusable download profile defined in the pipeline configuration. Specifies the file types to fetch (e.g., `[indiv, cn, cm, weball]`) and whether change detection is active. Cycles reference a Style by name rather than repeating these settings.
_Avoid_: mode, profile, template

**Parallelism**:
A pipeline configuration setting controlling whether the orchestrator DAG processes cycles sequentially or in parallel, and whether file types within a cycle run in parallel. Declared in `config/pipeline.yaml`.
_Avoid_: concurrency, threading

**Raw Table**:
A DuckDB table in the `raw` schema holding FEC bulk data exactly as downloaded for one File Type and one Cycle. Named `raw.<file_type>_<cycle>` (e.g., `raw.indiv_2024`). FEC column names used as-is; no cleaning or transformation applied. Owned by Airflow.
_Avoid_: staging table, landing table

**Cross-Cycle View**:
A dbt-managed DuckDB view in the `marts` schema named `<file_type>_all` (e.g., `marts.indiv_all`) that unions all loaded Raw Tables for a given File Type across cycles, adding a `cycle` column. Rebuilt by dbt after each load.
_Avoid_: combined view, union table

**Direct ZIP Load**:
DuckDB's ability to read pipe-delimited files directly from a ZIP archive without extracting to disk, using `read_csv('file.zip!inner.txt', ...)`. Used for all File Types. Requires explicit inner-path targeting for `indiv` because its ZIP contains both a full-cycle root file and date-range partial files in a subdirectory.
_Avoid_: extract then load, unzip

**Schema File**:
A Python module under `include/fec_schemas/` (e.g., `indiv.py`) that defines an ordered list of `FECColumn` entries, each carrying the FEC-assigned raw column name, a readable alias, and a `pyarrow` type. The Raw Table uses FEC names; dbt staging models apply the readable aliases. Single source of truth for both.
_Avoid_: data dictionary, column map, schema YAML
