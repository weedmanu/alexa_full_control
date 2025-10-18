# Run unit tests and static type checks from Dev/qualitytests
# Exits non-zero if any step fails

param(
	[string]$PythonExe,
	[switch]$InstallMissing,
	[switch]$AllowMutations,
	[switch]$Real,
	[switch]$Mock,
	[switch]$Fix,
	[switch]$Quick,
	[switch]$Check,
	[switch]$SkipBlack,
	[switch]$SkipIsort,
	[switch]$SkipRuff,
	[switch]$SkipPytest,
	[switch]$SkipMypy,
	[switch]$SkipFlake8,
	[switch]$SkipBandit,
	[switch]$SkipVulture,
	[switch]$SkipPylint,
	[switch]$SkipPydocstyle
)

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))

Write-Output "Repo root: $repoRoot"

# If user passed -Check, treat it as -Quick (check-only mode)
if ($Check) { $Quick = $true }

# Determine Python executable
if ([string]::IsNullOrWhiteSpace($PythonExe)) {
	# Fallback to environment variable if present
	$PythonExe = $env:PYTHON_EXE
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
	$default = Join-Path $repoRoot ".venv\Scripts\python.exe"
	if (Test-Path $default) {
		$PythonExe = $default
	} else {
		Write-Warning "Default venv python not found at $default. Will try 'python' from PATH."
		$PythonExe = "python"
	}
}

Write-Output "Using Python executable: $PythonExe"

# Ensure reports directories exist
$reportsDir = Join-Path $repoRoot 'Dev\qualitytests\reports'
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }
$pytestReportsDir = Join-Path $reportsDir 'pytest'
if (-not (Test-Path $pytestReportsDir)) { New-Item -ItemType Directory -Path $pytestReportsDir | Out-Null }

# Path to real-user tests (used to exclude them from automated runs)
$realUserTests = Join-Path $repoRoot 'Dev\pytests\pytests_real_user_api'
# Path where the cookies/data for real-user tests are expected
$realUserData = Join-Path $realUserTests 'data'

# Helper: return $true if real-user data folder exists and contains at least one non-empty file
function Test-HasRealUserData($path) {
	if (-not (Test-Path $path)) { return $false }
	$files = Get-ChildItem -Path $path -File -Recurse -ErrorAction SilentlyContinue
	foreach ($f in $files) {
		try {
			if ($f.Length -gt 0) { return $true }
		} catch { }
	}
	return $false
}

# Optionally install missing dependencies into the venv
if ($InstallMissing) {
	Write-Output "InstallMissing requested - installing dependencies into environment used by $PythonExe"
	# Prefer Dev/requirements-dev.txt then requirements.txt
	$devReq = Join-Path $repoRoot 'Dev\requirements-dev.txt'
	$req = Join-Path $repoRoot 'requirements.txt'
	$pipArgs = @('-m', 'pip', 'install', '--upgrade', 'pip')
	& $PythonExe @pipArgs
	if (Test-Path $devReq) {
		Write-Output "Installing dev requirements from: $devReq"
		& $PythonExe -m pip install -r $devReq
		if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install Dev requirements"; exit $LASTEXITCODE }
	}
	if (Test-Path $req) {
		Write-Output "Installing requirements from: $req"
		& $PythonExe -m pip install -r $req
		if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install requirements.txt"; exit $LASTEXITCODE }
	}
}

# By default, prevent mutation tests from running during automated quality checks.
if (-not $AllowMutations) {
	if ($env:ALEXA_ALLOW_MUTATION) {
		Write-Warning "Unsetting ALEXA_ALLOW_MUTATION for quality checks to avoid destructive tests. Use -AllowMutations to override."
		Remove-Item Env:\ALEXA_ALLOW_MUTATION -ErrorAction SilentlyContinue
	}
}

# Quality pipeline: quick mode runs fast linters + unit tests; full runs all tools
if ($Quick) {
	Write-Output "Quick mode: running fast linters and unit tests"
	$warnings = @()
	# black (check only unless -Fix)
	if (-not $SkipBlack) {
		if ($Fix) {
			$report = Join-Path $reportsDir 'black.txt'
			& $PythonExe -m black cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { Write-Error "black failed (see $report)"; exit $LASTEXITCODE }
		} else {
			$report = Join-Path $reportsDir 'black_check.txt'
			& $PythonExe -m black --check cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { $warnings += 'black' ; Write-Warning "black reported formatting changes would be needed (run with -Fix to apply) (see $report)" }
		}
	} else { Write-Output "Skipping black (per flag)" }

	# isort
	if (-not $SkipIsort) {
		if ($Fix) {
			$report = Join-Path $reportsDir 'isort.txt'
			& $PythonExe -m isort cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { Write-Error "isort failed (see $report)"; exit $LASTEXITCODE }
		} else {
			$report = Join-Path $reportsDir 'isort_check.txt'
			& $PythonExe -m isort --check-only cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { $warnings += 'isort' ; Write-Warning "isort reported import order issues (run with -Fix to apply) (see $report)" }
		}
	} else { Write-Output "Skipping isort (per flag)" }

	# ruff (fix capable)
	if (-not $SkipRuff) {
		if ($Fix) {
			$report = Join-Path $reportsDir 'ruff_fix.txt'
			& $PythonExe -m ruff check --fix cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { Write-Error "ruff failed (see $report)"; exit $LASTEXITCODE }
		} else {
			$report = Join-Path $reportsDir 'ruff_check.txt'
			& $PythonExe -m ruff check cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
			if ($LASTEXITCODE -ne 0) { $warnings += 'ruff' ; Write-Warning "ruff reported issues (run with -Fix to auto-fix where possible) (see $report)" }
		}
	} else { Write-Output "Skipping ruff (per flag)" }

	# pytest unit tests only (exclude Dev tests) - use discovery and ignore Dev and real-user tests to avoid duplicates
	if (-not $SkipPytest) {
	$pytestArgs = @('-m', 'pytest', '-q', '--ignore=Dev')
	# Handle real vs mock mode. Default: mock (exclude real tests).
	if ($Mock -and -not $Real) {
		if (Test-Path $realUserTests) { $pytestArgs += "--ignore=$realUserTests"; Write-Output "Mock mode: ignoring real-user tests at: $realUserTests" }
	} else {
		# Real mode requested: ensure real-user data exists
		if (Test-HasRealUserData $realUserData) {
			Write-Output "Real mode: real-user cookies found at: $realUserData -> running real-user tests"
		} else {
			Write-Warning "Real mode requested but no cookies found in $realUserData. Real tests may skip."
		}
	}

	# By default, exclude mutation tests from quick runs unless AllowMutations switch or env var is set
	if (-not ($AllowMutations -or $env:ALEXA_ALLOW_MUTATION)) {
		Write-Output "Excluding tests marked 'mutation' from quick run. Pass -AllowMutations or set ALEXA_ALLOW_MUTATION=1 to include them."
		$pytestArgs += '-m' ; $pytestArgs += '"not mutation"'
	} else {
		Write-Output "Including mutation tests in pytest run (AllowMutations present)."
	}
	$junit = Join-Path $pytestReportsDir 'pytest_quick.xml'
	$pyout = Join-Path $pytestReportsDir 'pytest_quick.txt'
	$pytestArgs += "--junitxml=$junit"
	& $PythonExe @pytestArgs 2>&1 | Tee-Object -FilePath $pyout
	} else { Write-Output "Skipping pytest (per flag)" }
	if ($LASTEXITCODE -ne 0) { Write-Error "pytest (quick) failed"; exit $LASTEXITCODE }

	if ($warnings.Count -gt 0) {
		Write-Output "Quick run completed with warnings: $($warnings -join ', ')"
		# Do not fail the Quick run for formatting issues
	}

} else {
	Write-Output "Running full quality pipeline (format, lint, types, security, tests)"
	# black/isort/ruff/flake8
	if ($Fix) { & $PythonExe -m black cli core utils services models alexa } else { & $PythonExe -m black --check cli core utils services models alexa }
	if ($LASTEXITCODE -ne 0) { Write-Error "black failed"; exit $LASTEXITCODE }
	if ($Fix) { & $PythonExe -m isort cli core utils services models alexa } else { & $PythonExe -m isort --check-only cli core utils services models alexa }
	if ($LASTEXITCODE -ne 0) { Write-Error "isort failed"; exit $LASTEXITCODE }
	if ($Fix) { & $PythonExe -m ruff check --fix cli core utils services models alexa } else { & $PythonExe -m ruff check cli core utils services models alexa }
	if ($LASTEXITCODE -ne 0) { Write-Error "ruff failed"; exit $LASTEXITCODE }
	$report = Join-Path $reportsDir 'flake8.txt'
	$flake8Conf = (Join-Path $repoRoot 'Dev\qualitytests\tests_conf\.flake8')
	& $PythonExe -m flake8 --config $flake8Conf cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "flake8 failed (see $report)"; exit $LASTEXITCODE }

	# mypy (already configured above)
	Write-Output "Running mypy..."
	$mypyExclude = '(?:^|[\\/])Dev(?:[\\/]|$)|pytests_real_user_api'
			$report = Join-Path $reportsDir 'mypy_quick.txt'
			& $PythonExe -m mypy --config-file (Join-Path $repoRoot 'mypy.ini') --exclude $mypyExclude $repoRoot 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "mypy failed"; exit $LASTEXITCODE }

	# security and other checks
	$report = Join-Path $reportsDir 'bandit.txt'
	& $PythonExe -m bandit -r cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "bandit failed (see $report)"; exit $LASTEXITCODE }
	$report = Join-Path $reportsDir 'vulture.txt'
	& $PythonExe -m vulture cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "vulture failed (see $report)"; exit $LASTEXITCODE }
	$report = Join-Path $reportsDir 'pylint.txt'
	$pylintRc = (Join-Path $repoRoot 'Dev\qualitytests\tests_conf\.pylintrc')
	& $PythonExe -m pylint --rcfile $pylintRc cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "pylint failed (see $report)"; exit $LASTEXITCODE }
	$report = Join-Path $reportsDir 'pydocstyle.txt'
	$pydocCfg = (Join-Path $repoRoot 'Dev\qualitytests\tests_conf\.pydocstyle')
	& $PythonExe -m pydocstyle --config $pydocCfg cli core utils services models alexa 2>&1 | Out-File -FilePath $report -Encoding utf8
	if ($LASTEXITCODE -ne 0) { Write-Error "pydocstyle failed (see $report)"; exit $LASTEXITCODE }

	# full tests
	$junit = Join-Path $pytestReportsDir 'pytest_full.xml'
	$pyout = Join-Path $pytestReportsDir 'pytest_full.txt'
	& $PythonExe -m pytest Dev/pytests/ -q --tb=line --junitxml $junit 2>&1 | Tee-Object -FilePath $pyout
	if ($LASTEXITCODE -ne 0) { Write-Error "pytest failed (see $pyout and $junit)"; exit $LASTEXITCODE }
}
if (-not $Quick) {
	# If the repository contains the copied 'pytests_real_user_api' folder (used for
	# real-user tests with local cookies), ignore it during the general test run to
	# avoid duplicate-module import conflicts.
	$pytestArgs = @('-m', 'pytest', '-q')
	# Exclude the entire Dev folder from pytest
	$pytestArgs += "--ignore=$(Join-Path $repoRoot 'Dev')"
	if (Test-Path $realUserTests) {
		Write-Output "Ignoring real-user tests at: $realUserTests"
		$pytestArgs += "--ignore=$realUserTests"
	}

	& $PythonExe @pytestArgs
	if ($LASTEXITCODE -ne 0) {
		Write-Error "pytest failed with exit code $LASTEXITCODE"
		exit $LASTEXITCODE
	}
} else {
	Write-Output "Quick/Check mode: skipping global pytest invocation (already run)."
}

Write-Output "Running mypy..."
# Exclude the Dev folder and the real-user tests folder from mypy to avoid duplicate-module errors
## Build a Windows-friendly regex to exclude the Dev folder and the real-user tests
	$mypyExclude = '(?:^|[\\/])Dev(?:[\\/]|$)|pytests_real_user_api'
	if (-not $SkipMypy) {
		if ($Quick) {
			# In Quick/Check mode, report mypy issues but do not fail the run
			$report = Join-Path $reportsDir 'mypy_full.txt'
			& $PythonExe -m mypy --config-file (Join-Path $repoRoot 'mypy.ini') --exclude $mypyExclude $repoRoot 2>&1 | Out-File -FilePath $report -Encoding utf8
			$mypyCode = $LASTEXITCODE
			if ($mypyCode -ne 0) {
				Write-Warning "mypy reported type issues (exit code $mypyCode). Run full pipeline to treat this as failure."
			}
		} else {
			& $PythonExe -m mypy --config-file (Join-Path $repoRoot 'mypy.ini') --exclude $mypyExclude $repoRoot
			if ($LASTEXITCODE -ne 0) {
				Write-Error "mypy failed with exit code $LASTEXITCODE"
				exit $LASTEXITCODE
			}
		}
	} else { Write-Output "Skipping mypy (per flag)" }

Write-Output "Quality checks passed."
exit 0
