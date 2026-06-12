#!/usr/bin/env bash
set -euo pipefail

# Configure GH_TOKEN/GITHUB_TOKEN for local gh/agent workflows using bash.

PERSIST_USER_SCOPE=false
CLEAR_USER_SCOPE=false

ENV_DIR="${HOME}/.config/money-trail"
ENV_FILE="${ENV_DIR}/gh-token.env"
RC_START="# >>> money-trail gh token >>>"
RC_END="# <<< money-trail gh token <<<"
RC_SNIPPET="${RC_START}
[ -f \"${ENV_FILE}\" ] && . \"${ENV_FILE}\"
${RC_END}"

usage() {
  cat <<'EOF'
Usage: scripts/setup-gh-token.sh [option]

Options:
  --persist-user-scope   Persist GH_TOKEN/GITHUB_TOKEN for future shells
  --clear-user-scope     Remove persisted GH_TOKEN/GITHUB_TOKEN and exit
  --help                 Show this help
EOF
}

remove_rc_block() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  awk -v start="$RC_START" -v end="$RC_END" '
    $0 == start {skip=1; next}
    $0 == end {skip=0; next}
    !skip {print}
  ' "$file" > "${file}.tmp"
  mv "${file}.tmp" "$file"
}

ensure_rc_block() {
  local file="$1"
  touch "$file"
  if ! grep -Fq "$RC_START" "$file"; then
    printf "\n%s\n" "$RC_SNIPPET" >> "$file"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --persist-user-scope)
      PERSIST_USER_SCOPE=true
      ;;
    --clear-user-scope)
      CLEAR_USER_SCOPE=true
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

echo "GitHub token setup for local agent workflows (bash host shell)."

if [[ "$CLEAR_USER_SCOPE" == true ]]; then
  rm -f "$ENV_FILE"
  remove_rc_block "${HOME}/.bashrc"
  remove_rc_block "${HOME}/.profile"
  echo "Cleared persisted GH_TOKEN and GITHUB_TOKEN from user scope."
  echo "Your gh auth login state was not modified."
  exit 0
fi

token=""
token_source="manual"

if command -v gh >/dev/null 2>&1; then
  gh_token="$(gh auth token 2>/dev/null || true)"
  if [[ -n "${gh_token}" ]]; then
    token="${gh_token}"
    token_source="gh-auth"
    echo "Using token from existing gh auth session."
  fi
fi

if [[ -z "$token" ]]; then
  echo "No reusable gh auth token found. Falling back to manual token entry."
  echo "Create a fine-grained token with least privilege for this repo:"
  echo "- New token page: https://github.com/settings/personal-access-tokens/new"
  echo "- Token list: https://github.com/settings/tokens"
  echo "- Minimum permissions: Issues (read/write), Pull requests (read/write), Contents (read)."
  read -r -s -p "Paste the new token: " token
  echo
fi

if [[ -z "$token" ]]; then
  echo "No token provided." >&2
  exit 1
fi

if [[ "$token_source" == "manual" ]] && [[ ! "$token" =~ ^(github_pat_|ghp_) ]]; then
  echo "Warning: token prefix is unusual. Verify you pasted the correct token."
fi

export GH_TOKEN="$token"
export GITHUB_TOKEN="$token"

if [[ "$PERSIST_USER_SCOPE" == true ]]; then
  umask 077
  mkdir -p "$ENV_DIR"
  cat > "$ENV_FILE" <<EOF
export GH_TOKEN='${token}'
export GITHUB_TOKEN='${token}'
EOF
  ensure_rc_block "${HOME}/.bashrc"
  ensure_rc_block "${HOME}/.profile"
  echo "GH_TOKEN set for current shell and persisted at user scope."
  echo "Reopen your shell or run: source \"$ENV_FILE\""
else
  echo "GH_TOKEN set for this script process only."
  echo "To keep in the current shell session, run: source scripts/setup-gh-token.sh"
  echo "For future shells, rerun with --persist-user-scope."
fi

echo "GITHUB_TOKEN also set for compatibility."
echo "This script does not modify gh auth login credentials or account selection."
echo "GitHub does not provide a public CLI/API to auto-create fine-grained PATs."

echo "Next steps:"
echo "1) In container run: scripts/gh_auth_harden.sh --status"
echo "2) In container run: scripts/gh_auth_harden.sh --verify"
if [[ "$PERSIST_USER_SCOPE" == true ]]; then
  echo "3) When done, clear persisted vars: scripts/setup-gh-token.sh --clear-user-scope"
fi
