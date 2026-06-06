# DuckDB Schemas Separate Airflow and dbt Ownership

The single DuckDB file (`data/duckdb/money_trail.duckdb`) uses three schemas: `raw` (Airflow-owned load target), `staging` (dbt cleaned/aliased models), and `marts` (dbt aggregated models including Cross-Cycle Views). Keeping Airflow writes in `raw.*` and dbt writes in `staging.*` and `marts.*` makes ownership explicit, prevents naming collisions between Raw Tables and dbt models, and lets the dbt profile target specific schemas without touching Airflow-managed tables.
