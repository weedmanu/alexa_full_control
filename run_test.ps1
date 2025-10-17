<#
Advanced test runner for Windows PowerShell
Usage:
  .\run_test.ps1 [-InstallDeps] [-FixLint] [-SkipLint] [-OpenReport]

Options:
  -InstallDeps : install dev dependencies from Dev\requirements-dev.txt into the user's environment (uses pip user install by default)
  -FixLint     : run linters in fix/auto-fix mode (isort --profile=black, black, ruff --fix)
  -SkipLint    : skip linters entirely
  -OpenReport  : open the generated HTML coverage report after tests

This script is idempotent and prints concise progress. It assumes PowerShell on Windows and Python in PATH.
#>
param(
    [switch]$InstallDeps = $false,
    [ValidateSet('all','black','isort','ruff','flake8','mypy','pytest')] [string[]]$Tools = @('all'),
    [ValidateSet('check','fix')] [string]$Mode = 'fix',
    [switch]$Strict = $false,
    [switch]$OpenReport = $false
)

$ErrorActionPreference = 'Stop'
Write-Host "Starting run_test.ps1 (InstallDeps=$InstallDeps, FixLint=$FixLint, SkipLint=$SkipLint, OpenReport=$OpenReport)"

# Helper: run a command and echo it
function Run-Command {
    param([string]$Cmd, [switch]$AllowFailure)
    Write-Host "\n>>> $Cmd" -ForegroundColor Cyan
    # Use the call operator so PowerShell returns proper exit code
    try {
        iex $Cmd
        $ec = $LASTEXITCODE
    } catch {
        $ec = 1
    }
    if (-not $AllowFailure -and $ec -ne 0) {
        Write-Host "Command failed with exit code $ec" -ForegroundColor Red
    } else {
        Write-Host "Command exit code: $ec" -ForegroundColor Yellow
    }
    return $ec
}

# 1) Optional: install dev requirements
if ($InstallDeps) {
    if (Test-Path "Dev\requirements-dev.txt") {
        Run-Command "python -m pip install -r Dev\requirements-dev.txt"
    } else {
        Write-Host "Dev\requirements-dev.txt not found, skipping dependency install" -ForegroundColor Yellow
    }
}

# 2) Linters & formatters
## Build the list of tools to run
$toolList = @()
if ($Tools -contains 'all') {
    $toolList = @('isort','black','ruff','flake8','mypy','pytest')
} else {
    $toolList = $Tools
}

Write-Host "Tools to run: $($toolList -join ', ') | Mode: $Mode | Strict: $Strict" -ForegroundColor Green

# Execute each tool with appropriate command
$nonZeroCount = 0
foreach ($t in $toolList) {
    switch ($t) {
        'isort' {
            if ($Mode -eq 'check') { $cmd = 'python -m isort --check-only .' } else { $cmd = 'python -m isort .' }
        }
        'black' {
            if ($Mode -eq 'check') { $cmd = 'python -m black --check .' } else { $cmd = 'python -m black .' }
        }
        'ruff' {
            if ($Mode -eq 'check') { $cmd = 'python -m ruff check .' } else { $cmd = 'python -m ruff check . --fix' }
        }
        'flake8' {
            # flake8 has no auto-fix; always check
            $cmd = 'python -m flake8 .'
        }
        'mypy' {
            # mypy is type-check only
            $cmd = 'python -m mypy .'
        }
        'pytest' {
            $cmd = 'python -m pytest --cov=core --cov=services --cov=utils --cov=cli --cov-report=term-missing --cov-report=html -q'
        }
        default {
            Write-Host "Unknown tool: $t" -ForegroundColor Yellow
            continue
        }
    }

    # For flake8/mypy in 'fix' mode, we still run checks and warn
    $allowFailure = $false
    $ec = Run-Command -Cmd $cmd -AllowFailure:$allowFailure
    if ($ec -ne 0) { $nonZeroCount += 1 }
    if ($Strict -and $ec -ne 0) {
        Write-Host "Strict mode: aborting due to failure in $t" -ForegroundColor Red
        exit 1
    }
}

if ($nonZeroCount -gt 0) {
    Write-Host "One or more tools returned non-zero exit codes: $nonZeroCount" -ForegroundColor Yellow
} else {
    Write-Host "All tools finished with exit code 0" -ForegroundColor Green
}

# 4) Optionally open the HTML report
if ($OpenReport) {
    $index = Join-Path -Path (Get-Location) -ChildPath "htmlcov\index.html"
    if (Test-Path $index) {
        Write-Host "Opening coverage report: $index" -ForegroundColor Green
        Start-Process $index
    } else {
        Write-Host "Coverage HTML report not found: $index" -ForegroundColor Yellow
    }
}

if ($nonZeroCount -gt 0) { exit 1 } else { Write-Host "run_test.ps1 finished" -ForegroundColor Green; exit 0 }
