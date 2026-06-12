# Duck Lake: Parquet Files as Primary Storage, DuckDB as Query Engine

**Status**: Accepted

**Date**: 2026-06-11

## Context

The original architecture (ADRs 0004–0006) loaded FEC data directly into DuckDB tables (`raw.*`, `staging.*`, `marts.*`), treating DuckDB as both storage and transformation engine. This approach tightly couples data storage to query execution and makes it harder to maintain immutable archives of downloaded data.

A **Duck Lake** approach separates storage from queries:
- **Storage**: Immutable parquet files (one per cycle per file type), stored in `data/duckdb/` and committed to DuckDB as external tables.
- **Queries**: DuckDB views over parquet files, enabling schema separation (raw, staging, marts) without storing data redundantly.

This aligns with modern data lake practices (Iceberg, Delta Lake, Parquet+DuckDB) where storage is decoupled from the query engine.

## Decision

Replace the direct DuckDB table approach with:

1. **Airflow** downloads FEC ZIPs and writes parquet files to `data/duckdb/<file_type>_<cycle>.parquet`.
2. **DuckDB** registers these files as external tables in the `raw` schema via `CREATE EXTERNAL TABLE` or `read_parquet()`.
3. **dbt** creates views in `staging` and `marts` schemas that read and transform the external tables.
4. Parquet files are immutable; re-downloads overwrite only out-of-date files.
5. DuckDB becomes the query engine only, not the source of truth.

## Consequences

### Positive
- **Data durability**: Parquet files are independent of DuckDB and can be inspected/reused with any Arrow-compatible tool.
- **Versioning**: Each parquet file can be versioned or archived independently.
- **Incremental updates**: Easier to replace individual cycle/file-type parquet files without rebuilding entire DuckDB database.
- **Reproducibility**: SQL queries over parquet are reproducible across environments (local, CI, production).
- **Compliance**: Audit trail of what data was downloaded when (parquet file timestamps).

### Negative
- **Setup complexity**: dbt must materialize views over external parquet tables, not direct tables.
- **File management**: Airflow is now responsible for managing file lifecycle (download, extract, write parquet, clean up source ZIPs).

## Compatibility

This decision **supersedes** ADRs 0004 (dbt ownership of cleaning/QA) and 0006 (DuckDB schema separation).

- **ADR 0004** still holds: dbt owns all cleaning and QA (via views/models over parquet).
- **ADR 0006** is updated: `raw` schema now contains external tables pointing to parquet files, not direct DuckDB tables. Ownership remains the same (Airflow for parquet writes, dbt for staging/marts views).

## References

- [DuckDB External Tables](https://duckdb.org/docs/data/external_table.html)
- [DuckDB Parquet Support](https://duckdb.org/docs/data/parquet.html)
