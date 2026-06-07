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

1. Follow the Windows + devcontainer auth guide:
   - [docs/windows-devcontainer-github-auth.md](docs/windows-devcontainer-github-auth.md)
2. From the repo root on the Windows host, run:

```powershell
.\scripts\setup-gh-token.ps1
```
   - Default is session-only and does not persist token env vars.
3. If you need token injection after VS Code/devcontainer restart, run:

```powershell
.\scripts\setup-gh-token.ps1 -PersistUserScope
```

4. Reopen the container so GH_TOKEN / GITHUB_TOKEN are injected.
5. In the container, run:
```bash
scripts/gh_auth_harden.sh --status
scripts/gh_auth_harden.sh --verify
```
6. When done with agent workflows, clear persisted vars:

```powershell
.\scripts\setup-gh-token.ps1 -ClearUserScope
```

Developer security/auth details (Windows + devcontainer):
- [docs/windows-devcontainer-github-auth.md](docs/windows-devcontainer-github-auth.md)

## More docs

- Developer docs index: [docs/developer-guide.md](docs/developer-guide.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Devcontainer troubleshooting: [docs/devcontainer-troubleshooting.md](docs/devcontainer-troubleshooting.md)
- Agent and issue workflow docs: [docs/agents](docs/agents)
- Architecture decisions: [docs/adr](docs/adr)
