## Problem Statement

The repository is transitioning from an earlier mixed structure to an architecture aligned with current ADRs, but the operating model is still partially implicit. Contributors need a clear, shared product definition for repository restructuring so implementation work can be parallelized safely without regressing ingestion reliability, schema ownership boundaries, or analyst workflows.

Today, gaps include inconsistent discoverability of runtime-vs-development responsibilities, incomplete codification of storage tier intent, and uneven documentation of how Airflow, Duck Lake storage, DuckDB query surfaces, dbt transformations, and notebook analysis fit together. Without a PRD-level contract, implementation can drift and produce rework.

## Solution

Deliver a repository restructuring and scaffolding initiative that formalizes architecture intent and developer workflow around these outcomes:

- Airflow remains the orchestrator for ingest/load behavior.
- Duck Lake parquet artifacts remain the primary immutable analytical storage.
- DuckDB remains the query engine and schema host for raw/metadata ownership boundaries.
- dbt remains owner of staging and marts transformations/QA.
- The repository layout clearly separates development container concerns from runtime service topology and analyst-facing artifacts.

The solution is complete when repository structure, docs, and operational seams are explicit enough that work can be broken into independent vertical slices with low coupling and clear acceptance criteria.

## User Stories

1. As a pipeline maintainer, I want repository directories to map cleanly to runtime responsibilities, so that I can locate and change orchestration logic without side effects.
2. As a pipeline maintainer, I want Airflow orchestration boundaries documented, so that DAG refactors preserve per-file-type failure isolation.
3. As a dbt developer, I want ownership boundaries between raw/metadata and staging/marts made explicit, so that cleaning logic does not leak into ingest code.
4. As a data analyst, I want notebook workflows to be first-class and discoverable, so that I can validate and explore data without reverse engineering setup.
5. As a Windows-based contributor, I want clear host-facing artifact paths, so that I can reliably access exports and reports outside containers.
6. As a new contributor, I want a canonical architecture narrative linked from onboarding docs, so that I can become productive quickly.
7. As a reviewer, I want restructuring changes split into tractable slices, so that I can review behavior changes independently.
8. As an operator, I want lifecycle scripts to remain idempotent, so that reruns do not produce hidden failures.
9. As a maintainer, I want runtime compose definitions separate from editor attachment concerns, so that runtime changes do not destabilize local development ergonomics.
10. As a maintainer, I want data tier definitions (`raw`, `stage`, `ducklake`, `duckdb`, `exports`) documented and enforced, so that artifact placement is predictable.
11. As a maintainer, I want a clean target-state path contract, so that new implementation can move directly to the intended architecture.
12. As a maintainer, I want ADR alignment called out in one place, so that code changes are evaluated against explicit decisions.
13. As an Airflow engineer, I want metadata and observation state expectations preserved, so that change-detection telemetry remains analyzable.
14. As a quality engineer, I want dbt testing expectations captured as behavior-level requirements, so that data quality guarantees survive restructuring.
15. As a release owner, I want a phased rollout plan, so that risky changes can be sequenced and validated.
16. As a contributor, I want known non-goals stated, so that scope does not expand into unrelated product work.
17. As a maintainer, I want explicit acceptance criteria for each restructuring concern, so that done-ness is objective.
18. As a maintainer, I want clear dependency edges between DAG code, shared include modules, and docs, so that refactors do not introduce hidden coupling.
19. As a maintainer, I want analyst-facing outputs surfaced consistently, so that downstream consumers are not impacted by internal path churn.
20. As a maintainer, I want PRD language to match domain vocabulary, so that issue decomposition and implementation remain semantically precise.

## Implementation Decisions

- Keep bulk-download-first ingestion as the canonical source acquisition strategy, aligned with ADR 0001.
- Keep operational HTTP/download state in DuckDB metadata tables, aligned with ADR 0002.
- Preserve per-file-type DAG decomposition plus orchestration layer to maintain independent failure domains, aligned with ADR 0003.
- Preserve the ownership split where Airflow owns ingest/load and dbt owns cleaning/QA, aligned with ADR 0004.
- Preserve indiv root-file-only loading semantics to avoid duplicate partial-file ingestion, aligned with ADR 0005.
- Preserve schema ownership boundaries: Airflow-owned raw/metadata and dbt-owned staging/marts, aligned with ADR 0006.
- Treat PostgreSQL-backed Airflow metadata runtime as the target operating posture while keeping local developer workflows straightforward, aligned with ADR 0007 direction.
- Preserve daily HEAD observation collection and historical telemetry analysis capability, aligned with ADR 0008.
- Preserve Duck Lake as primary immutable storage and DuckDB as query engine with external table/view surfaces, aligned with ADR 0009.
- Maintain a development/runtime split: devcontainer focuses editor and tooling ergonomics; runtime topology lives in compose/runtime definitions.
- Use documentation-first sequencing for restructuring: codify architecture and directory intent before large behavioral moves.
- Treat restructuring as greenfield for path and layout decisions, prioritizing target-state clarity over backward-compatibility shims.

## Testing Decisions

- Good tests validate external behavior and contracts, not internal implementation details.
- Prefer highest-available seams:
  - Repository seam: docs and directory contract checks that verify required structure and references exist.
  - Runtime seam: bootstrap/start scripts execute successfully and idempotently in supported local workflow.
  - Data contract seam: dbt run/test confirms staging/marts behavior remains valid after path/structure shifts.
  - Pipeline seam: Airflow DAG discovery and critical DAG execution smoke checks succeed.
- Modules/areas to test:
  - Airflow startup/bootstrap path and configuration handoff.
  - DAG import/discovery and orchestration entry points.
  - include modules used by DAGs for storage/path/config behavior.
  - dbt profile/project execution invariants tied to DuckDB/Duck Lake surfaces.
  - Export/report artifact path behavior for host accessibility.
- Prior art:
  - Existing Python tests around initialization and pipeline config.
  - Existing dbt run/test workflow used as quality gate for transformation outputs.

## Out of Scope

- Introducing new source systems beyond FEC bulk downloads.
- Redesigning business logic for FEC transformations unrelated to repository structure.
- Full replatforming away from Airflow, dbt, DuckDB, or Duck Lake.
- Broad UI/product work unrelated to repository architecture and developer/analyst workflow.
- Performance tuning beyond what is necessary to preserve current behavior during restructuring.

## Further Notes

- This PRD is intended to be decomposed into independently grabbable vertical slices immediately after publication.
- Priority should favor low-risk scaffolding and documentation alignment before deeper behavioral migration.
- Each implementation issue derived from this PRD should include explicit ADR references and acceptance criteria tied to observable behavior.
