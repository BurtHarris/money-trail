# Issue Dependency Update Plan: Daily HEAD Telemetry Sub-Product

This document captures the issue tracker updates needed to align open issues with ADR-0008 and related ADR edits.

## New Issue To Add (first)

Title: Daily HEAD observation collector (all cycles/file types, success+failure rows)

Suggested labels:
- enhancement
- ready-for-agent

Suggested body:

## What to build

Implement a dedicated Airflow telemetry DAG that performs HTTP HEAD checks for every configured Cycle and File Type and writes one Daily Observation row per probe outcome to DuckDB metadata, including failures and retry metadata. This collector is separate from ingest DAGs and is scheduled daily at 12:13 PM America/Los_Angeles, with bootstrap run support and backfill when possible after downtime.

## Acceptance criteria

- [ ] Telemetry DAG exists and is importable by Airflow
- [ ] Reads cycle/file-type targets from pipeline configuration
- [ ] Follows redirects and records final URL metadata
- [ ] Records one observation row for every probe outcome (success and failure)
- [ ] Uses retry policy: 3 attempts with exponential backoff
- [ ] Supports bootstrap run and backfill of missed observation dates when possible
- [ ] Stores timestamps in UTC and captures local date for America/Los_Angeles reporting

## Blocked by

- #10 (config/pipeline.yaml)
- #11 (DuckDB schema bootstrap)

## Existing Issues To Update

### #13 Per-file-type DAG: cn tracer bullet

Update Blocked by section to include the new telemetry issue.

Replace Blocked by with:

- #10 (config/pipeline.yaml)
- #11 (DuckDB schema bootstrap)
- #12 (Schema Files)
- <NEW_TELEMETRY_ISSUE_NUMBER> (daily observation collector contract)

Rationale: keeps probe semantics and metadata schema consistent across telemetry and ingest paths.

### #14 Per-file-type DAGs for remaining 8 file types

No dependency change required beyond #13.

Optional clarification to add:

- Reuse shared HEAD probe + metadata persistence utilities from #13 / telemetry collector.

### #17 Orchestrator DAG with configurable parallelism

No dependency change required.

Optional clarification to add:

- Ingest DAGs remain schedule=None; scheduled runs are handled by the dedicated telemetry collector DAG.

### #18 PRD issue

Optional comment to add:

- ADR-0008 defines the telemetry sub-product path and dedicated scheduled collector DAG.

## Suggested Command Sequence (after auth)

1. Create new telemetry issue first.
2. Capture new issue number.
3. Edit #13 Blocked by references to include the new issue.
4. Add optional clarifying comments to #14, #17, #18.

Example commands:

```bash
# 1) Create new issue (replace labels as needed)
gh issue create \
  --title "Daily HEAD observation collector (all cycles/file types, success+failure rows)" \
  --label "enhancement" \
  --label "ready-for-agent" \
  --body-file docs/agents/issue-telemetry-new-body.md

# 2) Edit issue #13 body (manual paste recommended for Blocked by section)
gh issue edit 13 --body-file /tmp/issue13-updated.md

# 3) Optional comments
gh issue comment 14 --body "Telemetry ADR alignment: reuse shared HEAD probe and metadata persistence utilities from tracer bullet + telemetry collector."
gh issue comment 17 --body "ADR alignment: ingest DAGs stay schedule=None; dedicated telemetry collector DAG carries scheduled cadence."
gh issue comment 18 --body "ADR-0008 added: daily HEAD observation collector as telemetry sub-product for cadence evidence gathering."
```
