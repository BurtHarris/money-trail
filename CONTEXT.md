# Money Trail Context

FEC campaign finance data pipeline: bulk download extraction, DuckDB loading, and dbt-based cleaning and QA, orchestrated by Apache Airflow.

**Quick Links**: See [README.md](README.md) for project overview and setup. See [docs/developer-guide.md](docs/developer-guide.md) for developer onboarding and common commands. See [docs/architecture/repository-restructuring-plan.md](docs/architecture/repository-restructuring-plan.md) for restructuring phases. See [docs/architecture/data-tier-path-contract.md](docs/architecture/data-tier-path-contract.md) for data path ownership. See [docs/adr/README.md](docs/adr/README.md) for all Architecture Decision Records.

See [FEC Campaign Finance Data](#fec-campaign-finance-data) for domain terms. See [Architecture & Ownership](#architecture--ownership) for system and implementation terms. For developer onboarding and the architecture contract, see [docs/developer-guide.md](docs/developer-guide.md).

### FEC Campaign Finance Data

**Cycle**:
A two-year FEC election cycle identified by the ending even year (e.g., `2024` covers 2023–2024). All bulk downloads and Bulk Tables are partitioned by cycle.
_Avoid_: election year, period, filing year

**Cycle Range**:
A string of the form `"YYYY-YYYY"` (e.g., `"2010-2022"`) in the pipeline configuration representing a contiguous span of Cycles stepping by 2. Both endpoints are inclusive.
_Avoid_: cycle list, year range

**FecTable**:
One of the FEC bulk download categories: `indiv` (individual contributions), `cn` (candidate master), `cm` (committee master), `oth` (committee-to-committee transfers), `oppexp` (operating expenditures), `ccl` (candidate-committee linkage), `weball` (all-candidates financial summary), `pas2` (contributions to candidates), or `indexp` (independent expenditures). The short code is the FEC's own identifier; it appears in ZIP file names, DuckDB table names, and dbt model names.
_Avoid_: file type, table type, dataset, category

**weball**:
A FecTable representing the FEC's "All Candidates" summary file. Contains one record per candidate with aggregate financial statistics (total receipts, disbursements, cash-on-hand, loans, etc.) for the cycle, regardless of when the candidate is up for election. Updated more frequently than the post-cycle candidate summary file but less precise. Named `weball<YY>.zip` on FEC bulk downloads.
_Avoid_: full archive, combined download, all candidates archive

**Bulk Layer**:
The set of DuckDB tables that hold FEC bulk data as delivered by the FEC — no additional cleaning or transformation applied by this pipeline. Note: the FEC itself preprocesses its bulk data (applying amendments, folding in corrections) before publishing. One table per FecTable per Cycle. Owned by Airflow; read by dbt.
_Avoid_: raw layer, staging (reserved for dbt), landing zone

**Download State**:
A DuckDB table (`metadata._fec_download_state`) that records the full history of HEAD check results per FecTable and Cycle — including timestamp, ETag, Last-Modified, and whether a change was detected. Used both for change detection (compare latest row against current HEAD) and for analyzing FEC update frequency per FecTable. Owned exclusively by Airflow.
_Avoid_: change log, sync state

**Daily Observation**:
One recorded result of a scheduled HTTP HEAD check for a single FecTable and Cycle on a given day, regardless of success or failure. Includes probe time and response metadata (when available) so stability and outage gaps are both measurable over time.
_Avoid_: daily delta, daily change row

**Observation Backfill**:
The process of creating missed Daily Observations after downtime (for example, a sleeping laptop) by running pending probes on the next available run. Backfilled rows are still first-class observations and remain distinguishable by their probe time.
_Avoid_: replay, synthetic fill

**Change Detection**:
An HTTP HEAD request to the FEC download URL compared against the stored Download State. Triggers a download and load only when the remote file has changed.
_Avoid_: delta detection, incremental check

**DownloadProfile**:
A named, reusable download configuration defined in `config/pipeline.yaml`. Specifies which FecTables to fetch (e.g., `[indiv, cn, cm, weball]`) and whether change detection is active. Cycles reference a DownloadProfile by name rather than repeating these settings.
_Avoid_: style, mode, profile, template

**Parallelism**:
A pipeline configuration setting controlling whether the orchestrator DAG processes Cycles sequentially or in parallel, and whether FecTables within a Cycle run in parallel. Declared in `config/pipeline.yaml` under `parallelism.cycles` and `parallelism.tables`.
_Avoid_: concurrency, threading

**Bulk Table**:
A DuckDB table in the `bulk` schema holding FEC bulk data as delivered for one FecTable and one Cycle. Named `bulk.<fec_table>_<cycle>` (e.g., `bulk.indiv_2024`). FEC column names used as-is; no cleaning or transformation applied. Owned by Airflow.
_Avoid_: raw table, staging table, landing table

**Cross-Cycle View**:
A dbt-managed DuckDB view in the `marts` schema named `<fec_table>_all` (e.g., `marts.indiv_all`) that unions all loaded Bulk Tables for a given FecTable across cycles, adding a `cycle` column. Rebuilt by dbt after each load.
_Avoid_: combined view, union table

**Direct ZIP Load**:
DuckDB's ability to read pipe-delimited files directly from a ZIP archive without extracting to disk, using `read_csv('file.zip!inner.txt', ...)`. Used for all FecTables. Requires explicit inner-path targeting for `indiv` because its ZIP contains both a full-cycle root file and date-range partial files in a subdirectory.
_Avoid_: extract then load, unzip

**FecTableSchema**:
A Python module under `include/fec_schemas/` (e.g., `indiv.py`) that defines an ordered list of `FecColumn` entries, each carrying the FEC-assigned raw column name, a readable alias, and a `pyarrow` type. The Bulk Table uses FEC names; dbt staging models apply the readable aliases. Single source of truth for both.
_Avoid_: schema file, data dictionary, column map, schema YAML

### Architecture & Ownership

**Duck Lake**:
Parquet files in `data/ducklake/` are the target primary immutable storage for FEC data (one file per Cycle per FecTable, named `<fec_table>_<cycle>.parquet`). During migration, `data/duckdb/` remains a compatibility/query surface. DuckDB queries parquet via external tables and views, serving as the query engine rather than source of truth. See ADR 0009 and the data-tier path contract.
_Avoid_: "DuckDB lake," "database tables"

**Bulk Schema**:
DuckDB external tables in the `bulk` schema that reference parquet files. Named `bulk.<fec_table>_<cycle>` (e.g., `bulk.indiv_2024`). Owned by Airflow (parquet files are written and managed by Airflow); queried by dbt. See ADR 0009, ADR 0006.
_Avoid_: raw schema, staging (reserved for dbt), landing zone

**Staging Schema**:
dbt-managed DuckDB views in the `staging` schema that clean, alias, and type-coerce Bulk Schema external tables. Named `stg_<fec_table>` (e.g., `stg_indiv`). Includes date parsing, amount formatting, null handling, ZIP code truncation to 5 digits, whitespace trimming, and FEC column name → readable alias mapping. Views union all cycles. Owned by dbt. See ADR 0004 and ADR 0009.
_Avoid_: bulk staging, intermediate tables

**Marts Schema**:
dbt-managed DuckDB views in the `marts` schema for analytical consumption. Includes Cross-Cycle Views that aggregate or filter staging views. See ADR 0009, ADR 0006.
_Avoid_: final tables, analytics layer

**Metadata Schema**:
DuckDB tables in the `metadata` schema holding Airflow operational state: download state, daily observations, load history. Owned exclusively by Airflow. See ADR 0007, ADR 0008.
_Avoid_: system tables, internal tracking

**Runtime Verb**:
A canonical lifecycle command exposed by `scripts/runtime.sh` and aligned to Docker Compose verbs: `up`, `down`, `start`, `stop`, `restart`, plus operational commands `ps`, `logs`, and `config`. Used to manage Airflow runtime services consistently in local development.
_Avoid_: ad-hoc docker command, manual compose workflow

## References

- **FEC Data Documentation**: https://www.fec.gov/data/browse-data/?tab=bulk-data
- **FEC Technical Specifications**: https://www.fec.gov/campaign-finance-data/technical-specifications/
- **FEC Data Catalog**: https://www.fec.gov/campaign-finance-data/
- **FEC File Format Specifications**:
  - [Individual Contributions (indiv)](https://www.fec.gov/campaign-finance-data/individual-contributions-file-description/)
  - [Candidate Master (cn)](https://www.fec.gov/campaign-finance-data/candidate-master-file-description/)
  - [Committee Master (cm)](https://www.fec.gov/campaign-finance-data/committee-master-file-description/)
  - [Candidate-Committee Linkage (ccl)](https://www.fec.gov/campaign-finance-data/candidate-committee-linkage-file-description/)
  - [Committee-to-Committee Transfers (oth)](https://www.fec.gov/campaign-finance-data/committee-to-committee-transfers-file-description/)
  - [Contributions to Candidates (pas2)](https://www.fec.gov/campaign-finance-data/contributions-candidates-file-description/)
  - [Operating Expenditures (oppexp)](https://www.fec.gov/campaign-finance-data/operating-expenditures-file-description/)
  - [All Candidates Financial Summary (weball)](https://www.fec.gov/campaign-finance-data/all-candidates-file-description/)
- **Architecture Decisions**: See `docs/adr/` (ADR 0001–0010)
  - ADR 0002: Download State tracking
  - ADR 0008: Daily Observation Collector
  - ADR 0009: Duck Lake architecture (supersedes aspects of 0004, 0006)
