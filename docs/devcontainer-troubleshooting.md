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

## Runtime stack port conflicts

The devcontainer now runs only the workspace service. Airflow runtime services are started from [compose/runtime.yml](../compose/runtime.yml) (with [docker-compose.yml](../docker-compose.yml) kept as compatibility entrypoint).

If runtime startup fails with a port-in-use message (for example on 8080), check current container port bindings:

```powershell
bash scripts/runtime.sh ps
```

If needed, adjust host mappings in [compose/runtime.yml](../compose/runtime.yml) and restart the runtime stack.

To clean stale containers that may still hold old ports:

```powershell
docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Then remove stale entries as needed:

```powershell
docker rm -f <container-name>
```
