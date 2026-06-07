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

## Skill quick reference

| Skill | Use it when | Primary inputs | Typical output |
| ----- | ----------- | -------------- | -------------- |
| triage | An issue needs classification and next-state routing | Issue number, reporter context, current labels | Updated labels and clear owner/state |
| to-issues | A large plan should be broken into executable slices | Plan or proposal text, scope boundaries, constraints | Multiple scoped implementation issues |
| to-prd | You need a product-style spec from discussion context | Feature idea, goals, non-goals, success criteria | A structured PRD issue or document |
| diagnose | A bug or performance regression must be investigated | Repro steps, logs or errors, expected vs actual behavior | Repro steps, root cause, and fix path |
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

1. Set `GH_TOKEN` on your Windows host (PowerShell).

	Recommended one-command setup from the repo root on the host:

	```powershell
	.\scripts\setup-gh-token.ps1
	```

	What this does:
	- Opens the GitHub token pages in your browser.
	- Prompts for token paste in PowerShell (masked input).
	- Sets `GH_TOKEN` for the current PowerShell session.
	- Persists `GH_TOKEN` at User scope for future sessions.
	- Sets `GITHUB_TOKEN` too for compatibility.

	Manual browser links (if needed):
	- New fine-grained token: https://github.com/settings/personal-access-tokens/new
	- Token list: https://github.com/settings/tokens

	Recommended minimum repo permissions:
	- Issues: Read and write
	- Pull requests: Read and write
	- Contents: Read

	Quick host-side check:

	```powershell
	if ($env:GH_TOKEN) { 'set' } else { 'missing' }
	```

	Security notes:
	- Never commit tokens to files, `.env`, scripts, or terminal history.
	- If a token is exposed, revoke it immediately and create a new one.
2. Reopen the devcontainer so the token is injected.
3. Run `scripts/gh_auth_harden.sh --status` and `scripts/gh_auth_harden.sh --verify`.

If `~/.config/gh/hosts.yml` contains `oauth_token`, remove disk-persisted auth with:

`scripts/gh_auth_harden.sh --logout-disk-token`
