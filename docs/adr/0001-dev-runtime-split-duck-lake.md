# ADR 0001: Separate development and runtime environments; adopt Duck Lake as surfaced analytics store

- **Status:** Proposed
- **Date:** 2026-06-11

## Context

The `money-trail` repository is becoming the primary architecture and implementation home for the project. Earlier work in `fec-data` established useful ETL patterns, documentation, and data model thinking, but the target direction for `money-trail` is different in several important ways.

The project needs to support:

1. A clear separation between the environment used for software development and exploration, and the environment used to run scheduled Airflow work.
2. A host-accessible analytics result that can be consumed from Windows without requiring users to work directly with downloaded bulk ZIP files.
3. Greater reliance on Airflow-native orchestration and Airflow-adjacent ELT patterns rather than script-first workflows.
4. A notebook-style user experience for interactive analysis and validation, while retaining the Airflow web UI for orchestration and operational visibility.
5. A storage approach that can preserve slowly changing historical information while allowing more recent election cycles to be refreshed or rebuilt as ingestion and modeling improve.

The prior `fec-data` approach centered more heavily on local ETL scripts, raw ZIP handling, and a single-user operational setup. That repository remains a source of domain knowledge, but its operational architecture is no longer the target baseline.

## Decision

We will treat `money-trail` as the canonical architecture repository and adopt the following decisions.

### 1. Separate development and runtime container environments

The project will use distinct container environments for different purposes:

- **Development container**
  - Used for coding, testing, dbt development, notebooks, and local exploration.
  - Optimized for developer productivity and interactive workflows.
  - May include Jupyter tooling, DuckDB clients, dbt CLI, and repository authoring tools.

- **Airflow runtime environment**
  - Used for the Airflow webserver, scheduler, triggerer, workers, and supporting services.
  - Optimized for repeatable execution of scheduled and manually triggered data workflows.
  - Kept operationally separate from the interactive development environment, even if both share source mounts or selected data volumes.

This split avoids coupling developer ergonomics to Airflow service lifecycle concerns and makes runtime behavior easier to reason about.

### 2. Surface Duck Lake / DuckDB analytical state, not raw ZIP files, as the primary host-facing artifact

The primary host-accessible output of the system will be a Duck Lake / DuckDB-managed analytical store and selected downstream exports derived from it.

Implications:

- Raw downloaded ZIP files are implementation inputs, not the primary user-facing product.
- Raw artifacts may remain inside container-managed or repo-managed storage for reproducibility, audit, or debugging.
- Windows-accessible paths should prioritize the surfaced analytical store, curated extracts, and notebook/report inputs.
- The project should optimize for stable access to queryable analytical results rather than stable exposure of transient ingestion artifacts.

### 3. Prefer Airflow-native orchestration for ELT

Airflow will be the primary orchestration layer for extract, load, transform, quality, and publication workflows.

This means:

- Scheduled and manually triggered work should be modeled as Airflow DAGs and tasks.
- Retry behavior, backfills, dependency control, scheduling, and run history should be expressed in Airflow rather than in ad hoc shell wrappers where practical.
- Transformation steps should be orchestrated from Airflow using native task patterns and supporting tools such as dbt where appropriate.
- Metadata and workflow state should increasingly live in Airflow-managed execution history and explicit project metadata tables rather than being distributed across loosely connected scripts.

Thin helper scripts may still exist, but they support orchestration; they do not replace it.

### 4. Support notebook-style interaction as a first-class user workflow

The project will support notebook-oriented exploration and validation in the development environment.

This means:

- Notebook tools are part of the development workflow.
- Notebooks may be used for QA, exploratory analysis, profiling, and design iteration against the surfaced analytical store.
- The Airflow web UI remains important for monitoring and operations, but it is not the only interface.
- Documentation and repo structure should make room for both orchestrated pipelines and interactive analytical work.

### 5. Adopt a Duck Lake-style storage strategy for historical retention and selective rebuilds

The project will move toward a Duck Lake approach so that historical information can be retained while recent or actively changing cycles can be rebuilt.

The intended operating model is:

- Older, slower-changing election-cycle data should remain preserved in stable analytical partitions or tables.
- Newer cycles may be refreshed, reloaded, or remodeled as source files change or pipeline logic improves.
- Storage and modeling should distinguish between:
  - immutable or mostly stable historical snapshots,
  - currently active or recently changing cycles,
  - derived analytical layers built from those sources.
- The system should favor append- and version-friendly patterns for historical retention while preserving the ability to reprocess recent data with corrected logic.

Exact physical implementation details may evolve, but the architectural direction is to combine durable historical retention with targeted rebuildability.

## Consequences

### Positive

- Development workflows become cleaner and less entangled with runtime service management.
- Airflow becomes the explicit system of record for orchestration behavior.
- Users can interact primarily with curated analytical outputs instead of raw ingestion artifacts.
- Notebook-driven analysis becomes a supported workflow rather than an afterthought.
- Historical and recent-cycle handling can diverge in a controlled way, which better matches FEC data behavior over time.

### Trade-offs

- The project will need clearer boundaries between dev-only tools and runtime dependencies.
- The repository structure and container configuration will become more explicit and possibly more complex.
- Some existing `fec-data` operational assumptions and docs will need to be adapted rather than copied directly.
- A Duck Lake-style design introduces additional modeling and lifecycle decisions around partitioning, versioning, promotion, and rebuild scope.

### Follow-up decisions likely needed

Future ADRs should clarify:

1. The exact container topology and compose/devcontainer relationship.
2. The physical layout and host-mount strategy for raw, staged, analytical, and published data.
3. The lifecycle policy for historical partitions versus rebuildable active-cycle data.
4. The boundary between Airflow-owned transformations and notebook-only exploratory work.
5. The publication model for Windows-accessible outputs derived from the analytical store.

## Migration notes

Documentation from `fec-data` should be treated as source material for this architecture, not as a drop-in operational template. Reusable conceptual material, glossary content, model diagrams, and durable project memory can be staged into `money-trail`, then rewritten to fit this ADR.
