# money-trail

Lightweight devcontainer-first workspace for FEC-oriented ELT development with Apache Airflow, OpenLineage, DuckDB, SQLite, and dbt.

## What is included

- VS Code devcontainer for Python-based data engineering work
- Apache Airflow 2.9 with a PostgreSQL metadata database (replaces SQLite for concurrent worker support)
- PostgreSQL 16 service running in the devcontainer
- Example DAG that reads from an HTTP source and writes to DuckDB and SQLite
- dbt starter project targeting DuckDB
- OpenLineage Python and Airflow provider dependencies preinstalled

## Quick start

1. Be sure you have up-to-date copies of Docker Desktop and VS Code on your machine.

```powershell
winget update docker.desktop vscode
```

2. Open the repository in VS Code.
3. Reopen in Container.
4. Wait for the post-create bootstrap to finish (this runs airflow db migrate against PostgreSQL).
5. Open Airflow at http://localhost:8080
   - username: devadmin
   - password: devadmin
6. PostgreSQL is exposed on your host at localhost:5433.
   - Inside the devcontainer network, services still use postgres:5432.
7. Trigger the DAG example_http_to_warehouse.
8. Run dbt commands from dbt/, for example:
   - dbt debug
   - dbt run

Optional contributor setup (only if you will use Copilot agent GitHub issue/PR actions):

1. On the Windows host (outside the container), run:

```powershell
.\scripts\setup-gh-token.ps1
```
2. Reopen the container so GH_TOKEN / GITHUB_TOKEN are injected.
3. In the container, run:
```bash
scripts/gh_auth_harden.sh --status
scripts/gh_auth_harden.sh --verify
```
Why this is the safer default:
- Token setup is optional and isolated to contributors who need GitHub issue/PR automation.
- Fine-grained, least-privilege scopes reduce impact if a token is leaked.
- Environment-variable auth avoids committing secrets into repo files.
- gh hardening checks help prevent accidental use of disk-persisted oauth_token.

## Security notes

- GitHub token setup is optional and only needed for contributor GitHub issue/PR automation.
- This host-token flow enables local GitHub CLI-backed agent actions in this workspace.
- Cloud agents use GitHub-side auth/permissions and do not consume your local `GH_TOKEN` directly.
- Local Airflow/dbt pipeline usage does not require a GitHub token.
- Prefer fine-grained, least-privilege tokens scoped to this repository.
- Use `GH_TOKEN`/`GITHUB_TOKEN` via host environment variables and avoid committing secrets to files.
- Run `scripts/gh_auth_harden.sh --status` and `scripts/gh_auth_harden.sh --verify` in the container after setup.
- If `~/.config/gh/hosts.yml` contains `oauth_token`, run `scripts/gh_auth_harden.sh --logout-disk-token`.
- Current setup persists tokens at User scope for convenience; this is weaker than session-only auth. On shared machines, clear User-scope tokens when not needed.
- If a token is exposed, revoke it immediately and create a new one.

## Testing vs auth responsibilities

- Testing does not require `GH_TOKEN` or `GITHUB_TOKEN`.
- Run local manual and automated tests in the devcontainer.
- Use CI for branch and PR validation.
- GitHub token setup is only for local `gh` API operations and GitHub CLI-backed agent workflows (issues, comments, labels, PR actions).
- Cloud-hosted agents use GitHub-side permissions and do not rely on local host token environment variables.

## More docs

- Developer docs index: [docs/developer-guide.md](docs/developer-guide.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Devcontainer troubleshooting: [docs/devcontainer-troubleshooting.md](docs/devcontainer-troubleshooting.md)
- Agent and issue workflow docs: [docs/agents](docs/agents)
- Architecture decisions: [docs/adr](docs/adr)
