param(
    [switch]$Local
)

$ErrorActionPreference = "Stop"

function Resolve-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @{
            Exe = "python"
            PrefixArgs = @()
        }
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @{
            Exe = "py"
            PrefixArgs = @("-3")
        }
    }
    throw "Neither 'python' nor 'py' is available on PATH."
}

$python = Resolve-Python

function Invoke-Python {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Args
    )
    & $python.Exe @($python.PrefixArgs + $Args)
}

if ($Local) {
    Write-Host "Running tests in local venv (lightweight). This will install pytest only."
    Invoke-Python -m venv .venv-tests
    & .\.venv-tests\Scripts\python -m pip install --quiet --upgrade pip pytest
    & .\.venv-tests\Scripts\python -m pytest -q
    exit $LASTEXITCODE
}

if ($env:REMOTE_CONTAINERS -or $env:DEVCONTAINER -or (Test-Path "/.dockerenv")) {
    Invoke-Python -m pytest -q
    exit $LASTEXITCODE
}

Write-Host "Open this workspace in the Dev Container for full test dependencies, or run with -Local." -ForegroundColor Yellow
exit 2
