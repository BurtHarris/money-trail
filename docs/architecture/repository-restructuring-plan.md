# Repository Restructuring and Migration Plan

This document captures the accepted plan for restructuring the `money-trail` repository according to recent architectural decisions (ADR 0001, ADR 0002). The goal is to align the project’s structure, storage, and operational conventions with the new focus on:

- separated devcontainer and Airflow runtime environments
- surfaced Duck Lake/DuckDB analytical results (not raw ZIPs)
- Airflow-native orchestration of ELT
- notebook-first analyst workflow
- platform/data layout for host (Windows) accessibility and long-lived historical retention

## Tasks & Milestones (Checklist)

### 1. Documentation First
- [ ] Complete and publish ADR 0002 (storage layout, Windows access strategy)
- [ ] Add this plan as `docs/architecture/repository-restructuring-plan.md`
- [ ] Add initial `README.md` files to the following:
  - `docs/architecture/`
  - `docs/imports/fec-data/`
  - `docs/runbooks/`
  - `notebooks/`
  - `compose/`
- [ ] Update `docs/developer-guide.md` to index new architecture docs

### 2. Directory and Repo Scaffolding
- [ ] Create (if not present): `docs/architecture/`, `docs/imports/fec-data/`, `docs/runbooks/`, `notebooks/`, `compose/`
- [ ] Establish `data/raw/`, `data/stage/`, `data/ducklake/`, `exports/` as per ADR 0002
- [ ] Publish and link the restructuring plan

### 3. Migration & Cleanup
- [ ] Inventory and stage selected durable docs from `fec-data` into `docs/imports/fec-data/`
- [ ] Identify and migrate only conceptual, architectural, or durable project memory docs
- [ ] Skip or adapt docs/directories centered on PowerShell script orchestration or ZIPs as surfaced product

### 4. Align Code & Runtime
- [ ] Move Airflow runtime definitions to `compose/`
- [ ] Document devcontainer (editor/interactive dev) boundaries
- [ ] Confirm all paths in code/scripts/configs reference new storage tiers

### 5. Notebook and Access
- [ ] Confirm notebooks can reach surfaced Duck Lake/DuckDB analytics file from host and devcontainer
- [ ] Add at least 1 demo/QA notebook to new `notebooks/`

### 6. Documentation Promotion
- [ ] Review/curate imported fec-data docs, promote into main docs/ADRs as fits

## Out of Scope for this Issue
- Large-scale refactor of legacy ETL scripts (will be a follow-up)
- Historical backfill, final notebook and export conventions (future ADRs)

## Reference
- ADR 0001: Dev/runtime split, Airflow-native ELT, Duck Lake (see docs/adr/0001-dev-runtime-split-duck-lake.md)
- ADR 0002: (pending) Storage layout, host access

Curated FEC docs:
- docs/imports/fec-data/context-fec.md — curated FEC context and glossary
- docs/imports/fec-data/fec-adr-0001-summary.md — ADR 0001 one-line summary
- docs/imports/fec-data/fec-adr-0002-summary.md — ADR 0002 one-line summary
- docs/imports/fec-data/fec-adr-0003-summary.md — ADR 0003 one-line summary
- docs/imports/fec-data/fec-adr-0004-summary.md — ADR 0004 one-line summary
- docs/imports/fec-data/fec-adr-0005-summary.md — ADR 0005 one-line summary
- docs/imports/fec-data/fec-adr-0006-summary.md — ADR 0006 one-line summary
- docs/imports/fec-data/fec-adr-0008-summary.md — ADR 0008 one-line summary

/cc @BurtHarris
