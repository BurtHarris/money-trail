# Runbooks

A runbook is a step-by-step reference for a specific operational task — starting a service, recovering from a failure, or performing routine maintenance. Unlike architecture docs (which explain *why*), runbooks focus on *what to do right now*. Each entry describes the trigger (when to use it), the steps to execute, and what success looks like.

This directory collects runbooks for the money-trail project: devcontainer setup, runtime compose stack, data ingestion, and Windows-specific quirks.

## Windows Docker / Volume Notes

- Docker Desktop on Windows uses WSL2 backend. Ensure Docker Desktop is running before invoking `docker compose`.
- File sharing: when mounting host paths into containers, ensure the host path is accessible to Docker Desktop (use shared drives or WSL2 mount points).
- Path lengths: avoid very long repository paths on Windows; prefer shorter parent folders (e.g., C:\workspace\money-trail).
- CRLF handling: repository files use LF; Git will convert on checkout if core.autocrlf is enabled. Use `.gitattributes` for binaries and notebooks.
- If Docker cannot access a mounted path, start Docker Desktop GUI and check Settings > Resources > File Sharing or ensure the path is under your user home/WSL mount.

## Common troubleshooting

- If `airflow-webserver` healthcheck fails, inspect logs: `docker compose logs -f airflow-webserver` and check postgres is healthy.
- To rebuild images after dependency changes: `docker compose build --no-cache`.



Docker & Data tiers
- DATA_DIR is set for devcontainer (/workspaces/money-trail/data) and compose (/app/data).
- Host mounts: Compose mounts ./data into /app/data; place durable analytic outputs in data/ducklake and raw ingests in data/raw.
- Starting runtime: `bash scripts/runtime.sh up`  # canonical runtime lifecycle helper
- Stopping runtime: `bash scripts/runtime.sh down`
- Runtime status: `bash scripts/runtime.sh ps`
- If runtime helper reports docker-daemon access error, start Docker daemon/Desktop and confirm current user has docker socket/group access.


Windows notes
- Avoid absolute Windows paths in code; prefer DATA_DIR and repository-relative paths.
- If encountering path length or permission issues on Windows, consult docs/adr/0002-storage-layout.md.