---
name: devcontainer-repair
description: "Repair failing devcontainer setup in this repository. Use for devcontainer build failures, lifecycle command failures, hidden postCreate/postStart errors, and Airflow startup issues in containerized development."
argument-hint: "Describe the failure symptom or paste the key error line"
user-invocable: true
---

# Devcontainer Repair

Use this skill to diagnose and fix devcontainer setup failures with a strict evidence-first workflow.

## When To Use

- Devcontainer fails to build or reopen.
- Container starts but project setup is broken.
- Airflow does not start after container launch.
- Lifecycle commands appear to pass but behavior is still broken.

## Repository-Specific Pitfall

In this repository, lifecycle commands in [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) use `|| true`. This can hide post-create and post-start failures unless you rerun scripts manually.

## Procedure

1. Reproduce without editing files
   - Run [reproduce-devcontainer-failure prompt](../../prompts/reproduce-devcontainer-failure.prompt.md).
   - Confirm whether failure stage is build, feature install, post-create, post-start, or runtime.

2. Gather minimum decisive evidence
   - Read [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json), [.devcontainer/Dockerfile](.devcontainer/Dockerfile), and [requirements.txt](requirements.txt).
   - Run:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
python --version
uv --version
airflow version
dbt --version
```

   - Check logs:
     - [logs/airflow-webserver.log](logs/airflow-webserver.log)
     - [logs/airflow-scheduler.log](logs/airflow-scheduler.log)

3. Apply the smallest fix that matches evidence
   - Prefer changes in `.devcontainer/` and `scripts/` first.
   - Keep lifecycle scripts idempotent.
   - Avoid adding new silent-failure patterns.

4. Validate before finishing
   - Run:

```bash
bash scripts/bootstrap.sh
bash scripts/start_airflow.sh
```

   - Confirm Airflow webserver is running and logs show no fatal traceback.
   - Confirm `dbt/profiles.yml` exists.

5. Report results in a stable structure
   - Reproduction summary
   - Evidence (commands and log excerpts)
   - Root cause
   - Minimal fix
   - Validation results

## Linked Guidance

- [AGENTS.md](../../../AGENTS.md)
- [devcontainer-log-triage instruction](../../instructions/devcontainer-log-triage.instructions.md)
- [reproduce-devcontainer-failure prompt](../../prompts/reproduce-devcontainer-failure.prompt.md)
