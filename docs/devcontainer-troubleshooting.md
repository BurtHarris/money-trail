# Devcontainer Troubleshooting

This guide covers common local container issues for Windows and WSL setups.

## Windows and WSL Wayland mount error

If VS Code fails to open the container with an error similar to:

- docker: Error response from daemon: ... /run/guest-services/distro-services/ubuntu.sock: no such file or directory

Docker Desktop usually cannot reach the WSL distro mount service used for the Wayland socket mount.

Use this recovery sequence from PowerShell:

1. Close VS Code windows attached to this repository.
2. Stop WSL:

```powershell
wsl --shutdown
```

3. Restart Docker Desktop.
4. Verify WSL integration is enabled for Ubuntu in Docker Desktop settings.
5. Start Ubuntu once to rehydrate distro services:

```powershell
wsl -d Ubuntu -e sh -lc "echo wsl-ok"
```

6. Reopen this repository in VS Code and run Dev Containers: Rebuild and Reopen in Container.

If the error persists, temporarily disable Wayland socket mounting in VS Code settings:

- Dev Containers: Mount Wayland Socket -> false

## Port conflict on PostgreSQL 5432

If container startup fails with a message like Bind for 0.0.0.0:5432 failed: port is already allocated, another process or container is already using host port 5432.

This repository currently maps PostgreSQL as host 5432 to container 5432:

- Host access: localhost:5432
- Container network access: postgres:5432

If you need a non-default host port, update [.devcontainer/docker-compose.yml](../.devcontainer/docker-compose.yml) from `5432:5432` to a free port such as `5433:5432`, then rebuild the container.

To clean stale containers that may still hold old ports:

```powershell
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Then remove stale entries as needed:

```powershell
docker rm -f <container-name>
```
