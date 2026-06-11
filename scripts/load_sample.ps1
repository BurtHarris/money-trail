# load_sample.ps1
# Load sample FEC data and verify dbt can recognize it via DuckDB
#
# Usage:
#   .\scripts\load_sample.ps1
#
# This script:
# 1. Generates a sample individual contributions parquet file (sample_indiv_2024.parquet)
# 2. Places it in data/duckdb/ for DuckDB external table queries
# 3. Runs dbt debug to verify DuckDB connection and recognizes the data

param(
    [switch]$SkipGenerate = $false,
    [switch]$SkipDebug = $false
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$DataDir = Join-Path $RootDir 'data' 'duckdb'
$SampleFile = Join-Path $DataDir 'sample_indiv_2024.parquet'

Write-Host "=" * 70
Write-Host "Money Trail Sample Data Loader"
Write-Host "=" * 70
Write-Host ""

# Step 1: Generate sample data if needed
if (-not $SkipGenerate) {
    Write-Host "[1/3] Generating sample data..." -ForegroundColor Cyan
    
    # Ensure data directory exists
    if (-not (Test-Path $DataDir)) {
        New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
        Write-Host "  ✓ Created data directory: $DataDir"
    }
    
    # Run SQL script via DuckDB to generate sample data
    $SqlScript = Join-Path $ScriptDir 'generate_sample_data.sql'
    if (Test-Path $SqlScript) {
        Push-Location $DataDir
        try {
            Get-Content $SqlScript | duckdb 2>&1 | Out-Null
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  ✗ Error generating sample data" -ForegroundColor Red
                exit 1
            }
            
            Write-Host "  ✓ Sample data generated via DuckDB"
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "  ⚠ generate_sample_data.sql not found at $SqlScript" -ForegroundColor Yellow
        Write-Host "  Skipping generation; using existing file if present"
    }
    
    Write-Host ""
}

# Step 2: Verify sample file exists
Write-Host "[2/3] Verifying sample file..." -ForegroundColor Cyan
if (Test-Path $SampleFile) {
    $FileSize = (Get-Item $SampleFile).Length / 1024
    Write-Host "  ✓ Sample file verified: $SampleFile"
    Write-Host "    Size: $([Math]::Round($FileSize, 1)) KB"
} else {
    Write-Host "  ✗ Sample file not found: $SampleFile" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Run dbt debug to verify DuckDB recognizes the data
if (-not $SkipDebug) {
    Write-Host "[3/3] Running dbt debug to verify DuckDB connection..." -ForegroundColor Cyan
    
    Push-Location $RootDir
    try {
        # Change to dbt directory for dbt commands
        $DbtDir = Join-Path $RootDir 'dbt'
        if (Test-Path $DbtDir) {
            Push-Location $DbtDir
            dbt debug
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "  ⚠ dbt debug reported issues (see above)" -ForegroundColor Yellow
            } else {
                Write-Host "  ✓ dbt debug succeeded - DuckDB connection verified"
            }
            
            Pop-Location
        } else {
            Write-Host "  ✗ dbt directory not found at $DbtDir" -ForegroundColor Red
            exit 1
        }
    } finally {
        Pop-Location
    }
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Sample Data Load Complete" -ForegroundColor Green
Write-Host "=" * 70
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Create external table in DuckDB: CREATE EXTERNAL TABLE raw.indiv_2024 AS SELECT * FROM '$SampleFile';"
Write-Host "  2. Run dbt models: dbt run"
Write-Host "  3. View sample data: SELECT * FROM staging.stg_indiv LIMIT 5;"
Write-Host ""
