# Devcontainer vs runtime topology

This document makes environment boundaries explicit so repository restructuring can proceed safely.

## Purpose split

- **Devcontainer (`.devcontainer/`)**: editor attachment, local tooling, and reproducible contributor shell.
- **Runtime topology (`compose/runtime.yml`)**: Airflow services and metadata dependencies.

## Current topology

### Devcontainer topology

- File: `.devcontainer/docker-compose.yml`
- Service: `workspace`
- Runtime profile: long-lived editor container (`sleep infinity`)
- Airflow profile in dev shell: no runtime Airflow services; post-create bootstrap runs with `BOOTSTRAP_AIRFLOW=0`

### Runtime topology

- Canonical file: `compose/runtime.yml`
- Compatibility file: `docker-compose.yml`
- Services: `airflow`, `init-airflow`, `scheduler`
- Runtime profile: local Airflow service stack
- Data mounts: `./data`, `./dags`, `./dbt`, `./logs`, `./scripts`

## Boundary rules

1. Devcontainer config must not become canonical runtime service definition.
2. Runtime topology changes must not require editor-container rebuild for normal service updates.
3. `DATA_DIR` behavior stays consistent across dev shell and runtime service containers.
4. Airflow orchestration behavior remains owned by DAG/include modules, not ad hoc local scripts.

## Migration direction

1. Keep runtime behavior unchanged while using `compose/runtime.yml` as canonical runtime file.
2. Update docs and scripts to reference compose location explicitly.
3. Keep compatibility entrypoint (`docker-compose.yml`) until migration complete.
4. Remove compatibility entrypoint only after docs and helper scripts are aligned.
