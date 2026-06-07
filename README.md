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
3. Optional (contributors using Copilot agents with GitHub issue/PR actions): run this on the Windows host before opening the container:

```powershell
.\scripts\setup-gh-token.ps1
```
4. Reopen in Container.
5. Wait for the post-create bootstrap to finish (this runs airflow db migrate against PostgreSQL).
6. Open Airflow at http://localhost:8080
   - username: devadmin
   - password: devadmin
7. PostgreSQL is exposed on your host at localhost:5433.
   - Inside the devcontainer network, services still use postgres:5432.
8. Trigger the DAG example_http_to_warehouse.
9. Run dbt commands from dbt/, for example:
   - dbt debug
   - dbt run

## Security notes

- GitHub token setup is a contributor step for agent-driven GitHub operations only (issue creation, labeling, comments, PR actions).
- GitHub token setup is not required to run the local Airflow/dbt pipeline.
- Use `GH_TOKEN`/`GITHUB_TOKEN` via host environment variables and avoid long-lived disk-persisted tokens in `~/.config/gh/hosts.yml`.

## More docs

- Developer docs index: [docs/developer-guide.md](docs/developer-guide.md)
- Contributor workflow: [docs/contributor-workflow.md](docs/contributor-workflow.md)
- Devcontainer troubleshooting: [docs/devcontainer-troubleshooting.md](docs/devcontainer-troubleshooting.md)
- Agent and issue workflow docs: [docs/agents](docs/agents)
- Architecture decisions: [docs/adr](docs/adr)
