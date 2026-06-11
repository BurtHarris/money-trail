# Repository restructuring plan for ADR 0001 and ADR 0002

- **Date:** 2026-06-11
- **Status:** Draft planning note

## Goals

Align `money-trail` with the current architecture direction:

1. Separate development and Airflow runtime environments.
2. Make Duck Lake / DuckDB analytical state the primary surfaced artifact.
3. Prefer Airflow-native orchestration for ELT.
4. Support notebook-style analysis as a first-class workflow.
5. Clarify storage tiers and Windows host access points.

## Recommended top-level structure

```text
.devcontainer/              # developer-focused container config
compose/                    # docker compose fragments or runtime definitions
config/                     # pipeline and environment configuration

dags/                       # Airflow DAG definitions
include/                    # reusable Python modules imported by DAGs
plugins/                    # Airflow plugins if needed

notebooks/                  # exploratory, QA, and analysis notebooks

data/
  raw/                      # source downloads and fetch artifacts
  stage/                    # rebuildable intermediate artifacts
  ducklake/                 # primary analytical store
  duckdb/                   # transition or compatibility db files if needed
  published/                # optional curated host-facing outputs

exports/                    # stable Windows-friendly derived outputs

docs/
  adr/                      # architecture decision records
  architecture/             # diagrams, topology notes, operating model docs
  imports/
    fec-data/               # staged docs migrated from fec-data for review
  runbooks/                 # operational procedures
  developer-guide.md        # index into contributor/developer docs

scripts/                    # thin helper scripts for local/dev/runtime support
tests/                      # automated tests
```

## Proposed repository responsibilities

### `.devcontainer/`
Keep this focused on developer workflow:
- editor/dev shell setup
- Python tooling
- notebook dependencies
- dbt CLI and DuckDB client tools
- validation helpers

Do not make this the canonical definition of the Airflow runtime topology.

### `compose/`
Introduce runtime-focused definitions here:
- Airflow webserver
- scheduler
- triggerer
- worker(s) if used
- metadata database and supporting services
- optional notebook service only if needed outside devcontainer

This keeps runtime orchestration separate from editor attachment concerns.

### `dags/`, `include/`, `plugins/`
Use these to make Airflow the orchestration center:
- `dags/` should remain relatively thin
- shared ingestion, storage, and modeling code belongs in `include/`
- `plugins/` only if Airflow extension points are actually needed

### `notebooks/`
Create this explicitly rather than scattering notebooks in ad hoc directories.
Suggested subfolders later if needed:
- `notebooks/exploration/`
- `notebooks/qa/`
- `notebooks/prototyping/`

### `data/`
Align this with ADR 0002:
- `data/raw/` for downloads and source artifacts
- `data/stage/` for rebuildable intermediate state
- `data/ducklake/` for surfaced analytical state
- `data/published/` for published-but-repo-local derived outputs

If `data/duckdb/` already exists in tooling assumptions, keep it temporarily and migrate deliberately.

### `exports/`
Use this as the clearest Windows-facing location for handoff artifacts:
- CSV extracts
- notebook-ready sample data
- curated snapshots
- generated reports intended for easy browsing

### `docs/`
Reshape docs around architecture and operation:
- `docs/adr/` for decisions
- `docs/architecture/` for diagrams and topology docs
- `docs/imports/fec-data/` for migrated source material under review
- `docs/runbooks/` for operational instructions

## Suggested implementation phases

### Phase 1: Documentation-first alignment
- Add ADRs for architecture and storage strategy
- Add this restructuring plan
- Create placeholder directories with README notes where useful
- Stage selected `fec-data` documentation into `docs/imports/fec-data/`

### Phase 2: Runtime/development split
- Move runtime-specific compose definitions into `compose/`
- Keep `.devcontainer/` focused on development experience
- Document how the devcontainer connects to runtime services

### Phase 3: Data tier clarification
- Establish `data/raw/`, `data/stage/`, `data/ducklake/`, and `exports/`
- Update scripts/configs/docs to use the new paths
- Decide which existing paths remain as compatibility shims

### Phase 4: Airflow-native ELT refinement
- Move orchestration concerns into Airflow DAGs and reusable modules
- Reduce dependence on script-first control flows
- Clarify which transforms run via Airflow/dbt and which are notebook-only

### Phase 5: Notebook-first analyst workflow
- Add `notebooks/`
- Document notebook conventions and connection patterns to surfaced analytical state
- Add sample QA or exploration notebooks once the surfaced store stabilizes

## Candidate low-risk changes to make early

1. Create:
   - `docs/architecture/`
   - `docs/imports/fec-data/`
   - `docs/runbooks/`
   - `notebooks/`
   - `compose/`

2. Add small README/index files in those directories.

3. Update `docs/developer-guide.md` to reference ADRs, architecture docs, and runbooks.

4. Inventory current scripts and config references to:
   - `data/`
   - `.devcontainer/`
   - docker compose files
   - Airflow startup paths

## Questions to resolve during restructuring

1. Should notebooks run only in the devcontainer, or also as a separate service?
2. Will the surfaced analytical store be one DuckDB file, a Duck Lake catalog plus files, or a transition period with both?
3. Which current paths are already assumed by scripts and DAGs?
4. What should be committed versus ignored for analytical and published outputs?
5. What is the minimum Windows-host path documentation needed for first useful use?

## Recommendation

Start with docs and directory scaffolding before moving code. That will let subsequent code and config changes line up with explicit architecture decisions instead of growing another temporary structure.
