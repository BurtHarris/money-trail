Param(
    # Open GitHub token management pages to guide least-privilege token creation.
    [switch]$OpenBrowser = $true,
    # Keep compatibility with tools that expect GITHUB_TOKEN instead of GH_TOKEN.
    [switch]$SetGithubTokenAlias = $true,
    # Persist GH_TOKEN/GITHUB_TOKEN at User scope for future terminals (opt-in).
    [switch]$PersistUserScope = $false,
    # Clear persisted User-scope GH_TOKEN/GITHUB_TOKEN and exit.
    [switch]$ClearUserScope = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Security intent:
# - Run this on the Windows host (outside the devcontainer).
# - Prefer GH_TOKEN/GITHUB_TOKEN env vars over `gh auth login` inside containers.
# - This avoids relying on disk-persisted oauth_token in ~/.config/gh/hosts.yml.
# - This path enables local GitHub CLI-backed agent actions in this workspace.
# - Cloud-hosted agents use GitHub-side auth/permissions and do not read local GH_TOKEN.
# - Collect token with masked console input.
# - Use environment variables for runtime auth (preferred over checked-in files).
# - Persist at User scope only (not Machine scope) to limit blast radius.
Write-Host "GitHub token setup for local agent workflows (Windows PowerShell host)." -ForegroundColor Cyan

if ($ClearUserScope) {
    [Environment]::SetEnvironmentVariable('GH_TOKEN', $null, 'User')
    [Environment]::SetEnvironmentVariable('GITHUB_TOKEN', $null, 'User')
    Write-Host "Cleared persisted User-scope GH_TOKEN and GITHUB_TOKEN." -ForegroundColor Green
    Write-Host "Your personal gh auth login state was not modified." -ForegroundColor Green
    return
}

if ($OpenBrowser) {
    Start-Process "https://github.com/settings/personal-access-tokens/new"
    Start-Process "https://github.com/settings/tokens"
    Write-Host "Opened GitHub token pages in your browser." -ForegroundColor Green
}

Write-Host "Create a fine-grained token with least privilege for this repo." -ForegroundColor Yellow
Write-Host "Recommended minimum: Issues (read/write), Pull requests (read/write), Contents (read)." -ForegroundColor Yellow
Write-Host "Security model: set token on host so container uses env vars; avoid gh auth login in-container." -ForegroundColor Yellow

# Prompt is masked so the token is not displayed while typing/pasting.
$secure = Read-Host "Paste the new token" -AsSecureString
# Convert SecureString to plain text only at the last moment so it can be assigned
# to process/user environment variables. The unmanaged buffer is zeroed in finally.
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
try {
    $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ([string]::IsNullOrWhiteSpace($token)) {
    throw "No token provided."
}

# Light validation to reduce copy/paste mistakes (fine-grained tokens usually start
# with github_pat_). Do not block unknown formats to preserve compatibility.
if ($token -notmatch '^(github_pat_|ghp_)') {
    Write-Host "Warning: token prefix is unusual. Verify you pasted the correct token." -ForegroundColor Yellow
}

# Current PowerShell process (immediate use)
$env:GH_TOKEN = $token
if ($SetGithubTokenAlias) {
    $env:GITHUB_TOKEN = $token
}

# Optional persistence for future terminals at User scope (avoids wider Machine-level exposure)
# Default is session-only to avoid changing long-lived personal gh CLI behavior.
if ($PersistUserScope) {
    [Environment]::SetEnvironmentVariable('GH_TOKEN', $token, 'User')
    if ($SetGithubTokenAlias) {
        [Environment]::SetEnvironmentVariable('GITHUB_TOKEN', $token, 'User')
    }
}

# Best-effort cleanup of local variables after export to env vars.
$token = $null
$secure = $null

if ($PersistUserScope) {
    Write-Host "GH_TOKEN set for current session and persisted at User scope." -ForegroundColor Green
} else {
    Write-Host "GH_TOKEN set for current session only (not persisted)." -ForegroundColor Green
}
if ($SetGithubTokenAlias) {
    Write-Host "GITHUB_TOKEN also set for compatibility." -ForegroundColor Green
}
if (-not $PersistUserScope) {
    Write-Host "Default mode preserves your long-lived personal gh auth style." -ForegroundColor Green
}
Write-Host "This script does not modify gh auth login credentials or account selection." -ForegroundColor Green

Write-Host "Next steps:" -ForegroundColor Cyan
if ($PersistUserScope) {
    Write-Host "1) Close and reopen VS Code / devcontainer so env vars are injected." -ForegroundColor Cyan
    Write-Host "2) In container run: scripts/gh_auth_harden.sh --status" -ForegroundColor Cyan
    Write-Host "3) In container run: scripts/gh_auth_harden.sh --verify" -ForegroundColor Cyan
    Write-Host "4) When done, clear persisted vars: .\\scripts\\setup-gh-token.ps1 -ClearUserScope" -ForegroundColor Cyan
} else {
    Write-Host "1) This token is active only in the current PowerShell session." -ForegroundColor Cyan
    Write-Host "2) For devcontainer-wide injection after restart, rerun with -PersistUserScope." -ForegroundColor Cyan
    Write-Host "3) In active shells, run gh auth status to confirm the expected auth source." -ForegroundColor Cyan
}
Write-Host "Note: cloud agents rely on GitHub-side permissions, not local GH_TOKEN." -ForegroundColor Cyan
