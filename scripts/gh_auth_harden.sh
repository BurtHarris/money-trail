#!/usr/bin/env bash
set -euo pipefail

# Hardens GitHub CLI auth for local agent workflows by preferring GH_TOKEN/GITHUB_TOKEN
# environment variables and optionally removing disk-persisted oauth_token entries.

HOSTS_FILE="${HOME}/.config/gh/hosts.yml"

print_status() {
  echo "== GitHub CLI auth status =="
  if gh auth status >/dev/null 2>&1; then
    gh auth status
  else
    echo "Not authenticated via gh auth login."
  fi

  echo
  echo "== Environment token check =="
  if [[ -n "${GH_TOKEN:-}" ]]; then
    echo "GH_TOKEN is set."
  else
    echo "GH_TOKEN is not set."
  fi
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    echo "GITHUB_TOKEN is set."
  else
    echo "GITHUB_TOKEN is not set."
  fi

  echo
  echo "== Disk token check =="
  if [[ -f "${HOSTS_FILE}" ]] && grep -q "oauth_token:" "${HOSTS_FILE}"; then
    echo "WARNING: oauth_token is present in ${HOSTS_FILE}."
    echo "Use: scripts/gh_auth_harden.sh --logout-disk-token"
  else
    echo "No oauth_token found in ${HOSTS_FILE}."
  fi
}

logout_disk_token() {
  echo "Logging out gh for github.com and removing disk token file if present..."
  gh auth logout --hostname github.com --yes || true
  if [[ -f "${HOSTS_FILE}" ]]; then
    rm -f "${HOSTS_FILE}"
  fi
  echo "Done."
}

verify_api() {
  echo "== Verifying API access with current credentials =="
  gh api user --jq '.login'
}

usage() {
  cat <<'EOF'
Usage: scripts/gh_auth_harden.sh [option]

Options:
  --status             Show gh auth status and token storage checks (default)
  --logout-disk-token  Remove disk-persisted gh oauth token
  --verify             Verify GitHub API access with active credentials
  --help               Show this help
EOF
}

cmd="${1:---status}"
case "$cmd" in
  --status)
    print_status
    ;;
  --logout-disk-token)
    logout_disk_token
    ;;
  --verify)
    verify_api
    ;;
  --help)
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac
