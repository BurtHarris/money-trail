# money-trail

Lightweight devcontainer-first workspace for FEC-oriented ELT development with Apache Airflow, OpenLineage, DuckDB, SQLite, and dbt.

## What is included

- VS Code devcontainer for Python-based data engineering work
- Apache Airflow 2.9 with a local SQLite-backed metadata database
- Example DAG that reads from an HTTP source and writes to DuckDB and SQLite
- dbt starter project targeting DuckDB
- OpenLineage Python and Airflow provider dependencies preinstalled

## Quick start

1. Be sure you have up-to-date copies of docker desktop on your machine.

```powershell
winget update docker.Desktop vscode
```

1. Open the repository in VS Code.
2. Reopen in Container.
3. Wait for the post-create bootstrap to finish.
4. Open Airflow at http://localhost:8080
   - username: `devadmin`
   - password: `devadmin`
5. Trigger the DAG `example_http_to_warehouse`.
6. Run dbt commands from `dbt/`, for example:
   - `dbt debug`
   - `dbt run`

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
   - Create a clear issue with scope, acceptance criteria, and constraints.
2. Triage and prepare the issue.
   - Use the `triage` skill vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) so status is explicit.
3. Break larger work into execution slices.
   - Use `to-issues` to split a broad plan into independently deliverable issues.
4. Implement with a development strategy.
   - Use `tdd` when behavior should be test-first.
   - Use `diagnose` when fixing defects or performance regressions.
5. Capture architecture decisions and domain language.
   - Keep domain and architecture docs aligned so future skill runs use the same terms and constraints.
6. Re-run and validate.
   - Re-check labels, acceptance criteria, and local validation commands before opening or updating a PR.

The files under `docs/agents/` are the source of truth for this repo's skill behavior. Update them if your issue workflow, labels, or domain-doc layout changes.

## Skill quick reference

| Skill | Use it when | Primary inputs | Typical output |
| ----- | ----------- | -------------- | -------------- |
| `triage` | An issue needs classification and next-state routing | Issue number, reporter context, current labels | Updated labels and clear owner/state |
| `to-issues` | A large plan should be broken into executable slices | Plan/proposal text, scope boundaries, constraints | Multiple scoped implementation issues |
| `to-prd` | You need a product-style spec from discussion context | Feature idea, goals, non-goals, success criteria | A structured PRD issue/document |
| `diagnose` | A bug or performance regression must be investigated | Repro steps, logs/errors, expected vs actual behavior | Repro steps, root cause, and fix path |
| `tdd` | You want to implement behavior test-first | Acceptance criteria, edge cases, target module | Tests plus implementation in red-green-refactor flow |
| `improve-codebase-architecture` | You want refactoring opportunities grounded in domain language | Existing architecture, pain points, domain docs | Architectural recommendations and candidate refactors |
| `grill-with-docs` | You want to pressure-test terminology/decisions and update docs | Proposed design/plan, glossary terms, ADR context | Clarified terms plus CONTEXT/ADR updates |
| `write-a-skill` | You need a new reusable repo skill | Skill objective, trigger phrases, examples/resources | New skill scaffold and instructions |

## Notes

- This repo intentionally keeps orchestration lightweight to stabilize the development environment first.
- OpenLineage packages are installed now; the next step can wire in a local backend such as Marquez or another collector.
- The example HTTP source points to a public FEC developer page so the container can be validated without requiring an API key.
- Once the container is stable, FEC ingestion code can be moved from your other repository into `dags/`, `include/`, and `dbt/models/`.

## Dev Container troubleshooting (Windows + WSL)

If VS Code fails to open the container with an error similar to:

- `docker: Error response from daemon: ... /run/guest-services/distro-services/ubuntu.sock: no such file or directory`

it usually means Docker Desktop cannot reach the WSL distro mount service used for the Wayland socket mount.

Use this recovery sequence from PowerShell:

1. Close VS Code windows attached to this repo.
2. Stop WSL:

   ```powershell
   wsl --shutdown
   ```

3. Restart Docker Desktop.
4. In Docker Desktop, verify WSL integration is enabled for your Ubuntu distro:
   - Settings -> Resources -> WSL Integration
5. Start Ubuntu once to rehydrate distro services:

   ```powershell
   wsl -d Ubuntu -e sh -lc "echo wsl-ok"
   ```

6. Reopen this repository in VS Code and run **Dev Containers: Rebuild and Reopen in Container**.

If the error persists, temporarily disable Wayland socket mounting in VS Code settings:

- `Dev Containers: Mount Wayland Socket` -> `false`
