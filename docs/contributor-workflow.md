# Contributor Workflow

This guide covers project structure, implementation flow, and skill usage for contributors.

## Project layout

```text
.
├── .agents/
│   └── skills/                        # Repo-local skill definitions used by Copilot agents
│       ├── diagnose/
│       ├── tdd/
│       ├── to-issues/
│       ├── triage/
│       └── ...
├── .devcontainer/                     # Container build and VS Code setup
├── AGENTS.md                          # Entry point that tells skills where to read repo conventions
├── compose/                           # Runtime compose topology (target location)
├── dags/                              # Airflow DAGs
├── data/                              # Local DuckDB, SQLite, and raw data artifacts
├── dbt/                               # dbt project and models
├── docs/
│   └── agents/                        # Skill runtime configuration for this repository
│       ├── issue-tracker.md           # How skills create/read/update issues
│       ├── triage-labels.md           # Mapping for canonical triage states
│       └── domain.md                  # Rules for reading CONTEXT/ADR docs
├── scripts/                           # Bootstrap and local startup helpers
└── skills-lock.json                   # Tracks skill setup metadata for this repo
```

## Typical skill workflow

Use this flow when turning an idea into an implemented and validated change with agent support:

1. Define the work item in GitHub Issues.
2. Triage and prepare the issue.
3. Break larger work into execution slices.
4. Implement with a development strategy.
5. Capture architecture decisions and domain language.
6. Re-run and validate.

Workflow details:
- Define with clear scope, acceptance criteria, and constraints.
- Use the triage labels needs-triage, needs-info, ready-for-agent, ready-for-human, and wontfix to keep state explicit.
- Use to-issues to split broad plans into independently deliverable slices.
- Use tdd for test-first behavior changes.
- Use diagnose for defects or performance regressions.
- Keep domain and architecture docs aligned so future runs use consistent terms.
- Re-check labels, acceptance criteria, and validation commands before opening or updating a PR.

The files under docs/agents are the source of truth for this repo's skill behavior. Update them if issue workflow, labels, or domain-doc layout changes.

## Sprint operating model (weekly)

This repository uses a lightweight sprint-oriented workflow.

- Sprint length: 1 week
- Planning unit: one issue should fit 1-2 days of effort
- Estimation buckets: `S` (up to 0.5 day), `M` (1 day), `L` (2 days)
- Scope control: fixed weekly plan with a reserved ad-hoc buffer
- Capacity model: plan `4+1` days each week (4 committed + 1 ad-hoc)
- WIP limit: maximum 2 issues labeled `in-progress` at any time
- Scope container: weekly GitHub Milestone only (no project board required)

Weekly milestone conventions:

- Add a one-sentence sprint goal in milestone description:
   - `This sprint delivers <user-visible outcome> by completing <2-4 key issues>.`
- Keep committed work in the milestone and mark unplanned items with `ad-hoc`.
- If ad-hoc buffer is unused by Thursday, pull the next smallest ready issue.

Checkpoints each week:

1. Monday planning (15-20 min): commit scope and set milestone.
2. Wednesday check-in (5-10 min): update labels/status and adjust scope.
3. Friday review/retro (15-20 min): close sprint, capture metrics, pick improvements.

Definition of Done (DoD) per issue:

1. Code change merged and linked to the issue.
2. Relevant tests pass (`bash scripts/run-tests.sh` or focused pytest).
3. Docs updated only when behavior or commands change.
4. Issue includes a short result note (what changed, what is next).

Release policy:

- Weekly batch release cadence (not continuous).
- Friday release gate uses two checks:
   1. All sprint issues meet DoD.
   2. Test command passes.

Sprint metrics:

1. Commitment reliability = completed committed issues / committed issues.
2. Flow reliability = number of carryover issues.
3. Cycle time (simple) = issue start (`in-progress`) to issue close, in calendar days.

Weekly milestone template (copy/paste)

Use this in the milestone description each Monday.

Title:
Sprint YYYY-Www

Goal:
This sprint delivers <user-visible outcome> by completing <2-4 key issues>.

Cadence and guardrails:
- Sprint length: 1 week
- Capacity: 4 committed days + 1 ad-hoc day
- WIP limit: max 2 issues with `in-progress`
- Slice size: each issue is S/M/L and should fit 1-2 days

Committed scope:
- #<issue-number> <issue title> (S|M|L)
- #<issue-number> <issue title> (S|M|L)
- #<issue-number> <issue title> (S|M|L)

Ad-hoc buffer policy:
- Up to 1 day of unplanned work this sprint
- Mark unplanned work with `ad-hoc`
- If unused by Thursday, pull the smallest ready issue

Definition of Done reminder:
1. Merged and linked to issue.
2. Relevant tests pass.
3. Docs updated when behavior/commands changed.
4. Short issue result note added.

Friday closeout:
- Release gate
   - DoD complete for sprint issues
   - Test command passes
- Metrics
   - Commitment reliability: <completed>/<committed>
   - Flow reliability: <carryover count>
   - Cycle time trend: <average calendar days>
- Process experiments for next sprint
   - <change 1>
   - <change 2>

## Skill quick reference

| Skill | Use it when | Primary inputs | Typical output |
| ----- | ----------- | -------------- | -------------- |
| triage | An issue needs classification and next-state routing | Issue number, reporter context, current labels | Updated labels and clear owner/state |
| to-issues | A large plan should be broken into executable slices | Plan or proposal text, scope boundaries, constraints | Multiple scoped implementation issues |
| to-prd | You need a product-style spec from discussion context | Feature idea, goals, non-goals, success criteria | A structured PRD issue or document |
| diagnose | A bug or performance regression must be investigated | Repro steps, logs or errors, expected vs actual behavior | Repro steps, root cause, and fix path |
| scrum | You want weekly sprint planning, mid-week checks, closeout, or scope adjustment with recommendations | Current sprint context, issues, milestone state, constraints | Recommended scrum action, confirmations, optional docs/issue updates |
| tdd | You want to implement behavior test-first | Acceptance criteria, edge cases, target module | Tests plus implementation in red-green-refactor flow |
| improve-codebase-architecture | You want refactoring opportunities grounded in domain language | Existing architecture, pain points, domain docs | Architectural recommendations and candidate refactors |
| grill-with-docs | You want to pressure-test terminology and decisions and update docs | Proposed design or plan, glossary terms, ADR context | Clarified terms plus CONTEXT or ADR updates |
| write-a-skill | You need a new reusable repo skill | Skill objective, trigger phrases, examples and resources | New skill scaffold and instructions |

## Notes

- This repo intentionally keeps orchestration lightweight to stabilize the development environment first.
- OpenLineage packages are installed now; the next step can wire in a local backend such as Marquez or another collector.
- The example HTTP source points to a public FEC developer page so the container can be validated without requiring an API key.
- Once the container is stable, FEC ingestion code can be moved from your other repository into dags, include, and dbt/models.

## GitHub auth for agents

Use token environment variables as the default auth path for `gh` in this repo.
This enables local GitHub CLI-backed agent actions in this workspace.
Default helper behavior reuses existing host `gh auth` credentials and is session-only.

Windows host + devcontainer guidance is centralized here:
- [docs/windows-devcontainer-github-auth.md](windows-devcontainer-github-auth.md)

## Avoiding Save Conflicts During Agent Edits

When working with an agent and your editor at the same time, you can hit:
`Failed to save ... The content of the file is newer`.

Root cause:
- The file on disk was updated by one writer (agent/tool/formatter), while your
  editor tab still had an older in-memory buffer.
- This is a file version race, not typically a Pylance rewrite behavior.

Safe workflow:
1. If conflict appears, open compare and prefer the newer on-disk version unless
   you intentionally want your unsaved tab edits.
2. Save once after reconciliation.
3. If diagnostics look stale, run `Developer: Reload Window`.
4. Avoid editing/saving the same file manually while a long agent edit is in
   progress.
