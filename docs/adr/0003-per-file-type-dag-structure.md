# One DAG per File Type, Coordinated by an Orchestrator DAG

Each FEC file type (`indiv`, `cn`, `cm`, `oth`, `oppexp`, `ccl`) has its own Airflow DAG running the full sequence: change detection → conditional download → truncate/load → scoped dbt run. A separate orchestrator DAG triggers all of them on demand. No scheduled execution is implemented at this time — all DAGs use `schedule=None` and are triggered manually or by the orchestrator. A single monolithic DAG was rejected because FEC files update on different schedules and a failure in one file type should not block the others.
