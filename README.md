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

- `.devcontainer/` - container build and VS Code setup
- `dags/` - Airflow DAGs
- `dbt/` - dbt project and example model
- `data/` - local DuckDB, SQLite, and raw data artifacts
- `scripts/` - bootstrap and local startup helpers

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
