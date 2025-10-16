#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Complete Development Quality Testing Suite for Alexa Full Control

.DESCRIPTION
    Manages virtual environment activation and runs comprehensive quality checks
    including: mypy, ruff, black, isort, flake8, pytest, coverage, bandit, safety, vulture

.PARAMETER All
    Run all quality checks (default)

.PARAMETER Mypy
    Run mypy static type checking

.PARAMETER Ruff
    Run ruff linter

.PARAMETER Black
    Run black code formatter check

.PARAMETER Isort
    Run isort import sorting check

.PARAMETER Flake8
    Run flake8 style guide check

.PARAMETER Pytest
    Run pytest unit tests

.PARAMETER Coverage
    Run pytest with coverage report

.PARAMETER Bandit
    Run bandit security check

.PARAMETER Safety
    Run safety dependency check

.PARAMETER Vulture
    Run vulture dead code detection

.PARAMETER Fix
    Auto-fix issues (for ruff, black, isort)

.PARAMETER Verbose
    Verbose output

.PARAMETER NoVenv
    Don't use virtual environment

.PARAMETER Path
    Specific path to check

.PARAMETER Pattern
    Test pattern to match (pytest -k)

.EXAMPLE
    .\run_tests.ps1 -All
    .\run_tests.ps1 -Mypy -Ruff
    .\run_tests.ps1 -Pytest -Coverage
    .\run_tests.ps1 -All -Fix -Verbose
    .\run_tests.ps1 -NoVenv -Bandit -Safety
#>

param(
	[switch]$All = $false,
	[switch]$Mypy = $false,
	[switch]$Ruff = $false,
	[switch]$Black = $false,
	[switch]$Isort = $false,
	[switch]$Flake8 = $false,
	[switch]$Pytest = $false,
	[switch]$Coverage = $false,
	[switch]$Bandit = $false,
	[switch]$Safety = $false,
	[switch]$Vulture = $false,
	[switch]$Fix = $false,
	[switch]$Verbose = $false,
	[switch]$NoVenv = $false,
	[string]$Path = "",
	[string]$Pattern = ""
)

# Set up error handling
$ErrorActionPreference = "Continue"

# Colors and indicators for output
$Green = @{ForegroundColor = "Green" }
$Red = @{ForegroundColor = "Red" }
$Yellow = @{ForegroundColor = "Yellow" }
$Cyan = @{ForegroundColor = "Cyan" }

$OkMark = "[OK]"
$FailMark = "[FAIL]"
$InfoMark = "[INFO]"
$RunMark = "[RUN]"

# Script variables
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot "venv"
$VenvScriptPath = Join-Path $VenvPath "Scripts"
$PythonExe = if ($NoVenv) { "python" } else { Join-Path $VenvScriptPath "python.exe" }

# Track results
$FailedChecks = @()
$PassedChecks = @()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-Header {
	param([string]$Message)
	Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
	Write-Host $Message -ForegroundColor Cyan
	Write-Host "$('=' * 80)" -ForegroundColor Cyan
}

function Write-Success {
	param([string]$Message)
	Write-Host "$OkMark $Message" @Green
}

function Write-Error {
	param([string]$Message)
	Write-Host "$FailMark $Message" @Red
}

function Write-Info {
	param([string]$Message)
	Write-Host "$InfoMark $Message" -ForegroundColor Yellow
}

function Write-Running {
	param([string]$Message)
	Write-Host "$RunMark Running: $Message" -ForegroundColor Cyan
}

function Initialize-VirtualEnv {
	Write-Info "Virtual Environment Setup"

	if ($NoVenv) {
		Write-Info "Skipping venv (--NoVenv specified)"
		return
	}

	if (-not (Test-Path $VenvPath)) {
		Write-Info "Creating virtual environment at $VenvPath"
		python -m venv $VenvPath
		if ($LASTEXITCODE -ne 0) {
			Write-Error "Failed to create virtual environment"
			exit 1
		}
	}

	Write-Info "Activating virtual environment"
	& "$VenvPath\Scripts\Activate.ps1"

	if ($LASTEXITCODE -ne 0) {
		Write-Error "Failed to activate virtual environment"
		exit 1
	}

	Write-Success "Virtual environment activated"
}

function Run-Check {
	param(
		[string]$CheckName,
		[string]$Command,
		[string]$SuccessMessage = "Check passed"
	)

	Write-Header $CheckName
	Write-Running $Command

	try {
		Invoke-Expression $Command
		if ($LASTEXITCODE -eq 0) {
			Write-Success "$CheckName passed"
			$PassedChecks += $CheckName
			return $true
		}
		else {
			Write-Error "$CheckName failed (exit code: $LASTEXITCODE)"
			$FailedChecks += $CheckName
			return $false
		}
	}
	catch {
		Write-Error "$CheckName error: $_"
		$FailedChecks += $CheckName
		return $false
	}
}

function Get-TargetPath {
	if ($Path) { return $Path }
	return "core"
}

function Get-TestPattern {
	if ($Pattern) { return "-k", $Pattern }
	return @()
}

# ============================================================================
# QUALITY CHECK FUNCTIONS
# ============================================================================

function Invoke-Mypy {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m mypy `"$targetPath`" --strict"
	if ($Verbose) { $cmd += " -v" }
	Run-Check "MYPY - Static Type Checking" $cmd
}

function Invoke-Ruff {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m ruff check `"$targetPath`" --select E,W,F"
	if ($Fix) { $cmd += " --fix" }
	Run-Check "RUFF - Linting $(if ($Fix) {'[AUTO-FIX]'} else {'[CHECK]'})" $cmd
}

function Invoke-Black {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m black `"$targetPath`""
	if (-not $Fix) { $cmd += " --check" }
	if ($Verbose) { $cmd += " -v" }
	Run-Check "BLACK - Code Formatting $(if ($Fix) {'[AUTO-FIX]'} else {'[CHECK]'})" $cmd
}

function Invoke-Isort {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m isort `"$targetPath`""
	if (-not $Fix) { $cmd += " --check-only" }
	if ($Verbose) { $cmd += " -v" }
	Run-Check "ISORT - Import Sorting $(if ($Fix) {'[AUTO-FIX]'} else {'[CHECK]'})" $cmd
}

function Invoke-Flake8 {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m flake8 `"$targetPath`" --max-line-length=120"
	Run-Check "FLAKE8 - Style Guide Enforcement" $cmd
}

function Invoke-Pytest {
	$targetPath = if ($Path) { $Path } else { "Dev/pytests" }
	$cmd = "& `"$PythonExe`" -m pytest `"$targetPath`" --tb=short"

	$pattern = Get-TestPattern
	if ($pattern.Count -gt 0) {
		$cmd += " -k `"$($pattern[1])`""
	}

	if ($Verbose) {
		$cmd += " -v"
	}
	else {
		$cmd += " -q"
	}

	$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
	Run-Check "PYTEST - Unit Tests" $cmd
	Remove-Item env:PYTEST_DISABLE_PLUGIN_AUTOLOAD -ErrorAction SilentlyContinue
}

function Invoke-Coverage {
	$targetPath = if ($Path) { $Path } else { "Dev/pytests" }
	$cmd = "& `"$PythonExe`" -m pytest `"$targetPath`" --cov=core --cov-report=html --cov-report=term-missing --tb=short"

	if ($Verbose) {
		$cmd += " -v"
	}
	else {
		$cmd += " -q"
	}

	$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
	Run-Check "COVERAGE - Code Coverage Report" $cmd
	Remove-Item env:PYTEST_DISABLE_PLUGIN_AUTOLOAD -ErrorAction SilentlyContinue

	Write-Info "Coverage report generated in htmlcov/index.html"
}

function Invoke-Bandit {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m bandit -r `"$targetPath`" -f json"
	Run-Check "BANDIT - Security Check" $cmd
}

function Invoke-Safety {
	$cmd = "& `"$PythonExe`" -m safety check --json"
	Run-Check "SAFETY - Dependency Security Check" $cmd
}

function Invoke-Vulture {
	$targetPath = Get-TargetPath
	$cmd = "& `"$PythonExe`" -m vulture `"$targetPath`" --min-confidence 80"
	Run-Check "VULTURE - Dead Code Detection" $cmd
}

function Invoke-All {
	Invoke-Mypy
	Invoke-Ruff
	Invoke-Black
	Invoke-Isort
	Invoke-Flake8
	Invoke-Coverage
	Invoke-Bandit
	Invoke-Safety
	Invoke-Vulture
}

# ============================================================================
# PRINT SUMMARY
# ============================================================================

function Print-Summary {
	Write-Header "SUMMARY"

	if ($PassedChecks.Count -gt 0) {
		Write-Host "`n$OkMark Passed Checks ($($PassedChecks.Count)):" @Green
		$PassedChecks | ForEach-Object { Write-Host "  - $_" @Green }
	}

	if ($FailedChecks.Count -gt 0) {
		Write-Host "`n$FailMark Failed Checks ($($FailedChecks.Count)):" @Red
		$FailedChecks | ForEach-Object { Write-Host "  - $_" @Red }
	}

	Write-Host "`n$('=' * 80)`n" -ForegroundColor Cyan

	if ($FailedChecks.Count -eq 0) {
		Write-Success "ALL CHECKS PASSED!"
		return 0
	}
	else {
		Write-Error "SOME CHECKS FAILED!"
		return 1
	}
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

try {
	# Initialize virtual environment
	Initialize-VirtualEnv

	# If no specific check is selected, run all
	if (-not ($Mypy -or $Ruff -or $Black -or $Isort -or $Flake8 -or $Pytest -or $Coverage -or $Bandit -or $Safety -or $Vulture)) {
		$All = $true
	}

	# Run selected checks
	if ($All) {
		Invoke-All
	}
	else {
		if ($Mypy) { Invoke-Mypy }
		if ($Ruff) { Invoke-Ruff }
		if ($Black) { Invoke-Black }
		if ($Isort) { Invoke-Isort }
		if ($Flake8) { Invoke-Flake8 }
		if ($Pytest) { Invoke-Pytest }
		if ($Coverage) { Invoke-Coverage }
		if ($Bandit) { Invoke-Bandit }
		if ($Safety) { Invoke-Safety }
		if ($Vulture) { Invoke-Vulture }
	}

	# Print summary
	$exitCode = Print-Summary
	exit $exitCode
}
catch {
	Write-Error "Fatal error: $_"
	exit 1
}
