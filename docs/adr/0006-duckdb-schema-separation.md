# DuckDB Schemas Separate Airflow and dbt Ownership

The single DuckDB file (`data/duckdb/money_trail.duckdb`) uses four schemas: `raw` (Airflow-owned load target), `staging` (dbt cleaned/aliased models), `marts` (dbt aggregated models including Cross-Cycle Views), and `metadata` (Airflow-owned download state and observation history). Keeping Airflow writes in `raw.*` and `metadata.*` and dbt writes in `staging.*` and `marts.*` makes ownership explicit, prevents naming collisions between Raw Tables and dbt models, and keeps operational state queryable without mixing it into analytics models.
