Param(
    # Open GitHub token management pages to guide least-privilege token creation.
    [switch]$OpenBrowser = $true,
    # Keep compatibility with tools that expect GITHUB_TOKEN instead of GH_TOKEN.
    [switch]$SetGithubTokenAlias = $true
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

# Persist for future terminals at User scope (avoids wider Machine-level exposure)
# Note: persistence is a convenience tradeoff; session-only usage is stricter on shared machines.
[Environment]::SetEnvironmentVariable('GH_TOKEN', $token, 'User')
if ($SetGithubTokenAlias) {
    [Environment]::SetEnvironmentVariable('GITHUB_TOKEN', $token, 'User')
}

# Best-effort cleanup of local variables after export to env vars.
$token = $null
$secure = $null

Write-Host "GH_TOKEN set for current session and persisted at User scope." -ForegroundColor Green
if ($SetGithubTokenAlias) {
    Write-Host "GITHUB_TOKEN also set for compatibility." -ForegroundColor Green
}

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1) Close and reopen VS Code / devcontainer so env vars are injected." -ForegroundColor Cyan
Write-Host "2) In container run: scripts/gh_auth_harden.sh --status" -ForegroundColor Cyan
Write-Host "3) In container run: scripts/gh_auth_harden.sh --verify" -ForegroundColor Cyan
Write-Host "4) Avoid running gh auth login in-container for this workflow." -ForegroundColor Cyan
Write-Host "5) Note: cloud agents rely on GitHub-side permissions, not local GH_TOKEN." -ForegroundColor Cyan
