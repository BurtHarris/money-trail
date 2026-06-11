# Runbooks

Operational runbooks for common tasks and troubleshooting.

Docker & Data tiers
- DATA_DIR is set for devcontainer (/workspaces/money-trail/data) and compose (/app/data).
- Host mounts: Compose mounts ./data into /app/data; place durable analytic outputs in data/ducklake and raw ingests in data/raw.
- Starting runtime: docker compose -f docker-compose.yml up --detach --build

Windows notes
- Avoid absolute Windows paths in code; prefer DATA_DIR and repository-relative paths.
- If encountering path length or permission issues on Windows, consult docs/adr/0002-storage-layout.md.