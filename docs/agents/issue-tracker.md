# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the gh CLI for all operations.

## Conventions

- Create an issue: gh issue create --title "..." --body "...". Use a heredoc for multi-line bodies.
- Read an issue: gh issue view <number> --comments, filtering comments by jq and also fetching labels.
- List issues: gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]' with appropriate --label and --state filters.
- Comment on an issue: gh issue comment <number> --body "..."
- Apply / remove labels: gh issue edit <number> --add-label "..." / --remove-label "..."
- Close: gh issue close <number> --comment "..."

Infer the repo from git remote -v - gh does this automatically when run inside a clone.

## Authentication (secure default for agents)

Use short-lived tokens via environment variables instead of disk-persisted `gh auth login` state.

1. On Windows host PowerShell, run `.\scripts\setup-gh-token.ps1` from the repo root.
2. Reopen the devcontainer so token env vars flow into the container runtime.
3. Verify with `scripts/gh_auth_harden.sh --verify`.

Security notes:

- Avoid storing long-lived `oauth_token` values in `~/.config/gh/hosts.yml`.
- Run `scripts/gh_auth_harden.sh --status` to audit current state.
- If disk token storage exists, run `scripts/gh_auth_harden.sh --logout-disk-token`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run gh issue view <number> --comments.