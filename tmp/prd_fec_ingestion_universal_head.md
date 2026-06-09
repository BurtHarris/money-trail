## Problem Statement

As the maintainer, I need the pipeline to reliably decide when to download and load FEC bulk files by Cycle and File Type, using durable evidence instead of ad hoc behavior. Today the codebase has Scope Config parsing and Download State bootstrap, but the runtime ingestion layer that performs Universal HEAD Probe, applies Freshness Precedence Rule, and executes Load-Verified Freshness decisions is not fully implemented. This creates risk of unnecessary downloads, missed updates, and unclear operational behavior across current and historical Styles.

## Solution

Introduce a production ingestion runtime that turns Style- and Cycle-driven Scope Config into executable plan units, runs Daily Observation probes for each unit, records a complete probe ledger in Download State, and branches into conditional Direct ZIP Load only when freshness rules require it. Keep ownership boundaries explicit: Airflow owns Raw Layer and metadata state; dbt owns cleaning, QA, and Cross-Cycle View rebuilds. Preserve one-DAG-per-File-Type execution and orchestrator coordination while enabling deterministic skip/download behavior for both current and historical ingest policies.

## User Stories

1. As a pipeline maintainer, I want every configured Cycle and File Type to receive a Daily Observation probe, so that I can measure update cadence even when files do not change.
2. As a pipeline maintainer, I want failed probe attempts to be captured as first-class observations, so that outages are visible in Download State history.
3. As a pipeline maintainer, I want Observation Backfill behavior after local downtime, so that telemetry continuity is preserved.
4. As a pipeline maintainer, I want Style-driven scope expansion, so that current and historical ingestion policy is configured once and reused safely.
5. As a pipeline maintainer, I want strict Cycle Range parsing and validation, so that invalid scheduling intent fails fast.
6. As a pipeline maintainer, I want unknown File Type values rejected at config load time, so that runtime failures are prevented.
7. As a pipeline maintainer, I want Exclusive Cycle Selector validation, so that each cycle entry is unambiguous.
8. As a pipeline maintainer, I want Universal HEAD Probe to run regardless of Style change_detection, so that telemetry remains complete across all Styles.
9. As a pipeline maintainer, I want Freshness Precedence Rule decisions based on latest successful baseline, so that transient probe failures do not trigger incorrect loads.
10. As a pipeline maintainer, I want Load-Verified Freshness semantics, so that skip decisions depend on proven load state rather than probe state alone.
11. As a pipeline maintainer, I want a Full Probe Ledger retained in DuckDB metadata, so that I can audit historical behavior.
12. As a pipeline maintainer, I want a Latest-Success View projection for decision speed, so that probe-to-branch logic remains efficient.
13. As a pipeline maintainer, I want Download State persisted in DuckDB instead of Airflow internals, so that operational metadata survives scheduler resets.
14. As a data engineer, I want Raw Layer loads to remain untransformed, so that extraction remains auditable and deterministic.
15. As a data engineer, I want Direct ZIP Load used where possible, so that local disk extraction overhead is minimized.
16. As a data engineer, I want indiv root-file targeting enforced, so that date-range partial files do not create duplicate loads.
17. As a data engineer, I want one DAG per File Type, so that failures in one stream do not block unrelated streams.
18. As a data engineer, I want an orchestrator DAG to trigger file-type DAGs by configured scope, so that operational control remains centralized.
19. As a data engineer, I want cycle-level and file-type-level Parallelism policy to be configurable, so that runtime behavior can be tuned per environment.
20. As a data engineer, I want idempotent schema/bootstrap steps, so that repeated runs are safe.
21. As a data engineer, I want branch outcomes (download_required, skip_unchanged, retry_later, hard_fail) recorded, so that run behavior is explainable.
22. As an analyst, I want Cross-Cycle Views rebuilt only for affected File Types, so that data products are fresh without unnecessary model work.
23. As a quality owner, I want dbt to own cleaning and QA, so that business rules remain testable and versioned outside orchestration code.
24. As a quality owner, I want ingestion failures to fail the right scope without corrupting other scopes, so that recovery is predictable.
25. As an operator, I want concise run summaries with observation counts and branch outcomes, so that health can be checked quickly.
26. As an operator, I want deterministic URL construction per Cycle and File Type, so that probe and download targets are reproducible.
27. As an operator, I want retries to be policy-driven and bounded, so that transient network issues are handled without runaway jobs.
28. As an operator, I want local/manual triggering compatibility retained, so that devcontainer workflows stay practical.
29. As an implementer, I want clear seams at planner, probe, decision, load, and state-write boundaries, so that tests can validate external behavior cleanly.
30. As a future maintainer, I want the implementation language to remain aligned with domain glossary terms, so that design intent is discoverable in code and docs.

## Implementation Decisions

- Introduce an ingestion planner seam that expands Scope Config into normalized plan units of Cycle × File Type × Style policy.
- Introduce a probe seam that performs Universal HEAD Probe and emits Daily Observation records including failure metadata.
- Introduce a freshness decision seam that consumes new observations plus latest successful baseline and emits branch decisions.
- Introduce a load seam for conditional Direct ZIP Load into Raw Table targets with per-File-Type loader strategy.
- Keep indiv ingestion on explicit root-file-only ZIP inner path selection to prevent duplicate partial ingestion.
- Introduce a state-write seam that appends immutable probe/load outcomes to Download State as the source of operational truth.
- Add a derived latest-success projection over Download State for fast Freshness Precedence Rule evaluation.
- Maintain ownership boundaries: orchestration writes Raw Layer and metadata; dbt writes staging and marts.
- Keep one-DAG-per-File-Type structure coordinated by an orchestrator DAG to isolate failures and retain targeted reruns.
- Use existing parallelism policy to control execution shape without changing domain semantics.
- Keep ingest DAGs trigger-driven for loads; schedule telemetry collection independently to support cadence analysis.
- Preserve idempotent bootstrap behavior for schemas and required metadata structures.
- Use stable branch outcome vocabulary in runtime logs and metadata to support post-run analysis.
- Keep source of truth for file-type vocabulary and scope declarations in configuration and domain glossary.

## Testing Decisions

- Good tests assert externally visible behavior at seams, not implementation details.
- Prioritize highest seams first: planner output contracts, probe outcome contracts, decision branch contracts, and state-write side effects.
- Reuse existing configuration validation test style for Scope Config behavior.
- Reuse existing DuckDB bootstrap test style for metadata schema and idempotency guarantees.
- Add decision tests that cover unchanged, changed, failed-probe, and missing-baseline scenarios using deterministic fixtures.
- Add loader tests that verify correct branch gating (load only when required) and indiv root-file targeting behavior.
- Add orchestrator-level behavior tests that verify one-file-type failure isolation and scoped continuation behavior.
- Add metadata behavior tests that verify Full Probe Ledger append-only semantics and latest-success derivation correctness.
- Add integration smoke tests that run one Cycle/File Type tracer path end-to-end and assert raw table + metadata outcomes.

## Out of Scope

- Migrating to FEC REST API as primary ingestion source.
- Replacing Airflow with another orchestrator.
- Moving Download State out of DuckDB.
- Redesigning dbt model semantics beyond required trigger integration.
- Full automation/scheduling policy beyond telemetry and orchestrator trigger model.
- Broad UI/reporting layer for operations dashboards.
- Historical backfill reprocessing strategy beyond observation backfill and configured cycle scope.

## Further Notes

- This PRD intentionally aligns with existing architectural decisions: bulk downloads over API, DuckDB-owned download state, per-file-type DAG isolation, dbt-owned cleaning/QA, and telemetry-first observation collection.
- Proposed seams are designed to maximize testability and preserve existing module responsibilities.
- Assumption: ready-for-agent indicates implementation can begin without additional triage.
