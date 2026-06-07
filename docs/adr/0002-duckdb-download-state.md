# Download State Stored in DuckDB, Not Airflow Variables

FEC HEAD-check state is persisted in DuckDB metadata tables rather than Airflow Variables or a separate SQLite file. DuckDB keeps pipeline state next to the data it protects, is queryable with SQL for update-frequency analysis, and survives Airflow metadata resets cleanly. Airflow Variables are awkward to query in bulk, couple state to scheduler internals, and do not support durable observation history analysis as well.
