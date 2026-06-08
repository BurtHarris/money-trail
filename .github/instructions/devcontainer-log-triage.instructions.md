---
applyTo: ".devcontainer/**,scripts/bootstrap.sh,scripts/start_airflow.sh"
description: "Use when troubleshooting devcontainer setup failures, lifecycle command issues, or Airflow startup in the container"
---

# Devcontainer Log Triage

Follow this sequence before proposing fixes.

## 1) Surface hidden failures first

This repository uses `|| true` for lifecycle hooks in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json), so post-create and post-start errors can be hidden.

Always re-run manually in the container shell:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

## 2) Verify build and feature assumptions

- Check [.devcontainer/Dockerfile](.devcontainer/Dockerfile) for package install changes.
- Check [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) for feature and lifecycle config.
- Treat `ghcr.io/devcontainers/features/docker-outside-of-docker:1` as a likely failure point on restricted hosts.

## 3) Collect concrete evidence before editing

Run and report output from:

```bash
python --version
pip --version
airflow version
dbt --version
```

Inspect runtime logs:

- [logs/airflow-webserver.log](logs/airflow-webserver.log)
- [logs/airflow-scheduler.log](logs/airflow-scheduler.log)

## 4) Editing guardrails

- Keep fixes minimal and local to `.devcontainer` and `scripts/` unless evidence proves broader changes are needed.
- Prefer deterministic failures over silent ignores; if changing lifecycle commands, ensure scripts remain idempotent.
- Do not mask errors with extra `|| true`.

## 5) Required validation before completion

Run:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

Confirm:

- Airflow webserver is running.
- No fatal traceback appears in Airflow logs.
- `dbt/profiles.yml` exists (copied from `dbt/profiles.yml.example` when missing).

For broader workflow context, reference [AGENTS.md](AGENTS.md) and [README.md](README.md).
