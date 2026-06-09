# AGENTS.md

Instructions for AI coding agents working in this repository.

## Scope

- Keep changes minimal and focused.
- Prefer fixing root causes over adding retries or broad fallbacks.
- For project context and expected behavior, start with [README.md](README.md).

## First Commands To Run

From the workspace root:

```bash
pwd
ls -la .devcontainer scripts
cat .devcontainer/devcontainer.json
cat .devcontainer/Dockerfile
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

If Python package or CLI availability is in question:

```bash
python --version
uv --version
airflow version
dbt --version
```

## Devcontainer Failure Triage (Priority)

When the devcontainer setup is failing, check in this order:

1. Build-time failures:
   - Inspect [.devcontainer/Dockerfile](.devcontainer/Dockerfile) and dependency install steps.
   - Confirm `requirements.txt` installs cleanly with `uv pip install --system -r /tmp/requirements.txt`.

2. Feature/runtime failures:
   - Inspect [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) for feature and lifecycle commands.
   - `docker-outside-of-docker` can fail on restricted Docker hosts; treat it as a likely culprit if build logs fail during feature install.

3. Post-create/post-start failures:
   - This repo uses `|| true` for both lifecycle commands in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json), so failures can be silent.
   - Re-run manually in container shell to surface real errors:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

4. Airflow startup issues:
   - Check [scripts/bootstrap.sh](scripts/bootstrap.sh) and [scripts/start_airflow.sh](scripts/start_airflow.sh).
   - Verify writable paths: `.airflow/`, `logs/`, `data/raw/`, `data/duckdb/`.
   - Check generated logs in [logs/](logs/).

## Repository Conventions

- Orchestration code lives in [dags/](dags/).
- dbt project lives in [dbt/](dbt/) and uses local profile files.
- Local artifacts are expected in [data/](data/), [logs/](logs/), and [.airflow/](.airflow/).
- Avoid moving these directories unless you also update scripts and environment variables.

## Safe Change Pattern For Devcontainer Fixes

- Prefer small edits in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json), [.devcontainer/Dockerfile](.devcontainer/Dockerfile), and [scripts/](scripts/).
- If changing lifecycle commands, keep them idempotent.
- If removing `|| true`, ensure scripts provide clear errors and do not break on harmless repeats.
- Update [README.md](README.md) when behavior or setup steps change.

## Validation Before Finishing

Run:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

Then verify:

- Airflow webserver process is running.
- No fatal tracebacks in `logs/airflow-webserver.log` or `logs/airflow-scheduler.log`.
- `dbt/profiles.yml` exists (copied from `dbt/profiles.yml.example` if needed).

## Agent skills

### Issue tracker

Issues are tracked in this repository's GitHub Issues (uses the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the label vocabulary: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one CONTEXT.md and docs/adr/ at the repo root. See `docs/agents/domain.md`.
