# Download State Stored in DuckDB, Not Airflow Variables

The last-seen ETag/Last-Modified per file type and cycle is persisted in a DuckDB metadata table (`_fec_download_state`) rather than Airflow Variables or a separate SQLite file. Airflow Variables are awkward to query in bulk, couple pipeline state to the scheduler, and are lost if the Airflow metadata DB is reset. DuckDB puts the state alongside the data it guards, is queryable with SQL, and survives Airflow re-deploys cleanly.
