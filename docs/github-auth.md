# Devcontainer GitHub Auth Guide

This guide is for bash-based host + VS Code devcontainer workflows in this repository.

Scope:
- Focuses on GitHub auth for local `gh` operations and local GitHub CLI-backed agent actions.
- Does not change test execution flow (tests still run in devcontainer/CI).

## Choose an auth path

### Path A (default): Adaptive setup script (reuse `gh auth`, fallback to manual)

Use this when you want an automated host-side flow with no browser token-creation step.
Default behavior is session-only so your long-lived personal `gh auth login` style is not changed.

1. Ensure you are already logged into `gh` on the host:

```bash
gh auth status
```

2. From the repo root, run:

```bash
bash scripts/setup-gh-token.sh
```

Behavior:
- Probes existing host `gh auth` and reuses its token if available.
- If no reusable `gh` token is found, prompts for masked token paste.
- On manual fallback, prints fine-grained token links and minimum permissions.

3. If you need token injection after a VS Code/devcontainer restart, opt in to temporary persistence:

```bash
bash scripts/setup-gh-token.sh --persist-user-scope
```

4. Reopen the devcontainer so `GH_TOKEN` / `GITHUB_TOKEN` are injected.
5. In the container, run:

```bash
scripts/gh_auth_harden.sh --status
scripts/gh_auth_harden.sh --verify
```

6. When done with agent workflows, clear persisted vars:

```bash
bash scripts/setup-gh-token.sh --clear-user-scope
```

Why Path A is preferred:
- Consistent auth for local CLI-agent operations in containerized workflows.
- Reuses existing host `gh` authentication with less operator error.
- Default session-only mode helps preserve personal interactive `gh` habits.

### Path B (optional): Manual-only prep before running the script

Use this if you need a tighter repo-scoped token than your current `gh auth` token scopes.

GitHub does not provide a public CLI/API to auto-create fine-grained PATs. Creation is manual in the web UI.

1. Create a GitHub fine-grained personal access token with these settings:
   - Resource owner: your account (or org that owns the repo)
   - Repository access: Only select repositories -> `BurtHarris/money-trail`
   - Repository permissions (minimum):
     - Issues: Read and write
     - Pull requests: Read and write
     - Contents: Read-only
   - Expiration: short-lived (recommended)
2. Run:

```bash
bash scripts/setup-gh-token.sh
```

Important caveats:
- Manual PAT creation requires browser interaction.
- If you use this path, run hardening checks and clean up disk auth if required:

```bash
scripts/gh_auth_harden.sh --status
scripts/gh_auth_harden.sh --logout-disk-token
scripts/gh_auth_harden.sh --verify
```

## Security notes

- GitHub token setup is optional and only needed for contributor GitHub issue/PR automation.
- Local Airflow/dbt pipeline usage does not require GitHub auth.
- Keep secrets out of repo files, `.env`, scripts, and terminal history.
- If a token is exposed, revoke it immediately and create a new one.
- User-scope token persistence is opt-in and is a convenience tradeoff; session-only use is stricter on shared machines.

## Testing vs auth responsibilities

- Testing does not require `GH_TOKEN` / `GITHUB_TOKEN`.
- Run local manual and automated tests in the devcontainer.
- Use CI for branch and PR validation.
- Token/auth setup is only for local `gh` API operations and local GitHub CLI-backed agent workflows.
- Cloud-hosted agents use GitHub-side permissions and do not rely on local host token environment variables.