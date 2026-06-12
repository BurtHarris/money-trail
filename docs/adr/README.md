# Architecture Decision Records (ADRs)

This directory contains all Architecture Decision Records for the Money Trail project. Each ADR documents a significant architectural decision, its context, consequences, and status. ADRs provide historical context and rationale for the current system design.

**See also**: [README.md](../../README.md) for project overview, [CONTEXT.md](../../CONTEXT.md) for domain glossary, and [docs/developer-guide.md](../developer-guide.md) for developer onboarding.

## Index

### Core Architecture (Duck Lake)

- **[ADR 0009: Duck Lake – Parquet Files as Primary Storage, DuckDB as Query Engine](0009-duck-lake-parquet-storage.md)** (Accepted)
  - Establishes parquet files in `data/duckdb/` as immutable primary storage. DuckDB serves as query engine via external tables. dbt owns transformation and QA. Supersedes aspects of ADRs 0004–0006.

### Schema and Ownership

- **[ADR 0006: DuckDB Schemas Separate Airflow and dbt Ownership](0006-duckdb-schema-separation.md)**
  - Defines four schemas (`raw`, `staging`, `marts`, `metadata`) to clearly delineate Airflow (downloads, metadata) vs dbt (cleaning, QA, analytics) responsibilities. Informs ADR 0009.

- **[ADR 0004: dbt Owns All Cleaning and QA; Airflow Does Not Transform Data](0004-dbt-owns-cleaning-and-qa.md)**
  - Establishes that Airflow performs only download and storage; dbt handles all data cleaning, type coercion, aliasing, and QA. Informs ADR 0009.

### Data Pipeline

- **[ADR 0003: One DAG per File Type, Coordinated by an Orchestrator DAG](0003-per-file-type-dag-structure.md)**
  - Specifies per-file-type DAG structure (e.g., `dag_indiv`, `dag_cm`) to isolate failure domains and enable configurable parallelism. Orchestrator DAG (`dag_fec`) coordinates them.

- **[ADR 0005: indiv ZIP Loads Root File Only; Date-Range Partials Excluded](0005-indiv-zip-root-file-only.md)**
  - Limits the `indiv` (Individual Contributions) file type to load only the full-cycle root file from each ZIP, excluding the date-range partial files in subdirectories.

- **[ADR 0008: Daily HEAD Observation Collector for FEC Bulk URLs](0008-daily-head-observation-collector.md)**
  - Documents a scheduled HTTP HEAD check collector task that records update frequency and stability of FEC bulk download URLs. Feeds change detection logic (ADR 0002).

### State and Metadata

- **[ADR 0002: Download State Stored in DuckDB, Not Airflow Variables](0002-duckdb-download-state.md)**
  - Stores full HTTP HEAD check history (ETag, Last-Modified, timestamp) in DuckDB table `metadata._fec_download_state` instead of Airflow variables. Enables change detection and frequency analysis.

### Infrastructure

- **[ADR 0007: Upgrade Airflow Metadata Database from SQLite to PostgreSQL](0007-airflow-postgres-metadata-db.md)** (Proposed)
  - Upgrade to PostgreSQL for concurrent worker support and DAG parallelism. SQLite insufficient for multi-process execution.

- **[ADR 0002: Storage Layout and Windows Host Access](0002-storage-layout.md)**
  - Defines storage directory layout and Windows host file mounting strategy for devcontainer. Ensures `DATA_DIR` environment variable works consistently across dev and runtime.

### Developer Experience

- **[ADR 0010: Airflow Hosts the Project Docs Browser](0010-airflow-docs-browser.md)**
  - Exposes the curated markdown docs inside the Airflow UI through a plugin-backed external view so docs stay in the same authenticated browser session and can be printed cleanly.

### Foundational

- **[ADR 0001: Separate Development and Runtime Environments; Adopt Duck Lake](0001-dev-runtime-split-duck-lake.md)** (Foundational)
  - Establishes the dual-environment model (VS Code devcontainer for interactive work, Docker Compose runtime for Airflow services). Introduces Duck Lake as the core architectural pattern.

- **[ADR 0001: FEC Bulk Downloads Over the REST API](0001-bulk-downloads-over-api.md)**
  - Specifies use of FEC REST API bulk download endpoint rather than individual file fetches. Documents file type categorization and download strategy.

## How to Read ADRs

1. Start with [ADR 0009](0009-duck-lake-parquet-storage.md) for the current architecture overview.
2. Refer to [ADR 0006](0006-duckdb-schema-separation.md) and [ADR 0004](0004-dbt-owns-cleaning-and-qa.md) for ownership and responsibility boundaries.
3. See [ADR 0003](0003-per-file-type-dag-structure.md) and [ADR 0008](0008-daily-head-observation-collector.md) for pipeline orchestration and monitoring.
4. Check [ADR 0002](0002-duckdb-download-state.md) for state management and change detection.

## Cross-References from Domain Docs

- **CONTEXT.md** references ADRs for specific domain terms (e.g., "Duck Lake" → ADR 0009, "Raw Schema" → ADR 0006).
- **Developer Guide** (docs/developer-guide.md) references ADRs for architecture contract and common patterns.
- **README.md** directs to ADRs for architecture decisions.

---

*For questions about a specific decision, consult the corresponding ADR. For domain terminology and glossary, see [CONTEXT.md](../../CONTEXT.md).*
