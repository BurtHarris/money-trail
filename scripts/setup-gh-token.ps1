Param(
    [switch]$OpenBrowser = $true,
    [switch]$SetGithubTokenAlias = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "GitHub token setup for local agent workflows (Windows PowerShell host)." -ForegroundColor Cyan

if ($OpenBrowser) {
    Start-Process "https://github.com/settings/personal-access-tokens/new"
    Start-Process "https://github.com/settings/tokens"
    Write-Host "Opened GitHub token pages in your browser." -ForegroundColor Green
}

Write-Host "Create a fine-grained token with least privilege for this repo." -ForegroundColor Yellow
Write-Host "Recommended minimum: Issues (read/write), Pull requests (read/write), Contents (read)." -ForegroundColor Yellow

$secure = Read-Host "Paste the new token" -AsSecureString
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

# Current PowerShell process (immediate use)
$env:GH_TOKEN = $token
if ($SetGithubTokenAlias) {
    $env:GITHUB_TOKEN = $token
}

# Persist for future terminals
[Environment]::SetEnvironmentVariable('GH_TOKEN', $token, 'User')
if ($SetGithubTokenAlias) {
    [Environment]::SetEnvironmentVariable('GITHUB_TOKEN', $token, 'User')
}

Write-Host "GH_TOKEN set for current session and persisted at User scope." -ForegroundColor Green
if ($SetGithubTokenAlias) {
    Write-Host "GITHUB_TOKEN also set for compatibility." -ForegroundColor Green
}

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1) Close and reopen VS Code / devcontainer so env vars are injected." -ForegroundColor Cyan
Write-Host "2) In container run: scripts/gh_auth_harden.sh --status" -ForegroundColor Cyan
Write-Host "3) In container run: scripts/gh_auth_harden.sh --verify" -ForegroundColor Cyan
