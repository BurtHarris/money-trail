# Compose

Runtime compose definitions and migration target for service topology.

## Current state

- Canonical runtime topology: `compose/runtime.yml`
- Compatibility entrypoint (legacy path): `docker-compose.yml`
- Devcontainer editor environment: `.devcontainer/docker-compose.yml`

## Target state

- Keep `.devcontainer/` focused on editor/dev ergonomics only.
- Keep runtime service topology in `compose/` files.
- Keep `docker-compose.yml` as compatibility shim until migration complete.

## Runtime service contract

Runtime topology covers:

- Airflow webserver
- Airflow scheduler
- Airflow init/bootstrap
- Metadata database and related service dependencies

For architecture intent and ownership boundaries, see:

- `docs/architecture/repository-restructuring-plan.md`
- `docs/architecture/dev-vs-runtime-topology.md`

## Commands

- Start runtime: `bash scripts/runtime.sh up`
- Stop runtime: `bash scripts/runtime.sh down`
- Runtime status: `bash scripts/runtime.sh ps`
- View logs: `bash scripts/runtime.sh logs -f`
- Compose config: `bash scripts/runtime.sh config`
