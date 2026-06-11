# FEC Imports Curation Notes

This file tracks candidate durable documentation and resources relevant to FEC data imports that can be staged under docs/imports/fec-data/ and curated into permanent docs.

Candidate sources (review and migrate selected sections):

- CONTEXT.md — project context describing FEC pipeline and cycles; consider extracting the FEC-specific sections into docs/imports/fec-data/context.md
- docs/adr/0001-bulk-downloads-over-api.md — ADR about FEC bulk downloads; keep in ADRs but reference from imports docs
- docs/adr/0002-duckdb-download-state.md — ADR describing download state; cross-link
- docs/adr/0003-per-file-type-dag-structure.md
- docs/adr/0004-dbt-owns-cleaning-and-qa.md
- docs/adr/0005-indiv-zip-root-file-only.md
- docs/adr/0008-daily-head-observation-collector.md
- include/fec_schemas/ (if present) — Python schema definitions for FEC file types (good to surface as reference)
- dags/ (example DAGs that demonstrate FEC ingestion) — consider copying conceptual docs or examples, not DAG code

Recommendations:
- Migrate only conceptual, durable docs (designs, schemas, runbook fragments). Do not copy production DAG code into docs; link to code instead.
- For each source file, extract a one-page summary and place in docs/imports/fec-data/ with a filename indicating origin (e.g., CONTEXT-fec.md, fec-adr-0001-summary.md).
- Add cross-links from docs/architecture/repository-restructuring-plan.md and docs/developer-guide.md to these curated docs.

Curated docs:
- docs/imports/fec-data/context-fec.md — curated FEC context and glossary
- docs/imports/fec-data/fec-adr-0001-summary.md
- docs/imports/fec-data/fec-adr-0002-summary.md
- docs/imports/fec-data/fec-adr-0003-summary.md
- docs/imports/fec-data/fec-adr-0004-summary.md
- docs/imports/fec-data/fec-adr-0005-summary.md
- docs/imports/fec-data/fec-adr-0006-summary.md
- docs/imports/fec-data/fec-adr-0008-summary.md


Next steps taken:
- No automatic code movement performed. Please review the candidate list and confirm which files/sections to extract and stage. If approved, automated extraction can be performed.
