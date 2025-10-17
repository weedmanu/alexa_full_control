# run_quality_checks.ps1 - Pipeline de tests de qualité complet
# Usage: .\run_quality_checks.ps1 [-AutoFix] [-Verbose]

param(
    [switch]$AutoFix = $false,
    [switch]$Verbose = $false
)

# Couleurs pour l'output
$colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

# Activer venv
Write-Host "`n========== ACTIVATION VENV ==========" -ForegroundColor $colors.Info
.\.venv\Scripts\Activate.ps1

# Vérifier que Python fonctionne
Write-Host "Vérification de l'environnement..." -ForegroundColor $colors.Info
$pythonVersion = python --version
Write-Host "✅ $pythonVersion" -ForegroundColor $colors.Success

Write-Host "`n========== QUALITY CHECKS PIPELINE ==========" -ForegroundColor $colors.Info
$mode = if ($AutoFix) { "AUTO-FIX ENABLED" } else { "CHECK ONLY" }
Write-Host "Mode: $mode" -ForegroundColor $colors.Warning

# Définition des tests
$checks = @(
    @{ 
        name = "1 BLACK (Formatage)"
        test = '.\.venv\Scripts\python.exe -m black --check cli core utils services models alexa'
        fix = '.\.venv\Scripts\python.exe -m black cli core utils services models alexa'
        canAutoFix = $true
    },
    @{
        name = "2 ISORT (Imports)"
        test = '.\.venv\Scripts\python.exe -m isort --check-only cli core utils services models alexa'
        fix = '.\.venv\Scripts\python.exe -m isort cli core utils services models alexa'
        canAutoFix = $true
    },
    @{
        name = "3 RUFF (Linting)"
        test = '.\.venv\Scripts\python.exe -m ruff check cli core utils services models alexa'
        fix = '.\.venv\Scripts\python.exe -m ruff check --fix cli core utils services models alexa'
        canAutoFix = $true
    },
    @{
        name = "4 FLAKE8 (Style)"
        test = '.\.venv\Scripts\python.exe -m flake8 cli core utils services models alexa --max-line-length=120 --ignore=E501,W293,W291'
        fix = ''
        canAutoFix = $false
    },
    @{
        name = "5 MYPY (Types)"
        test = '.\.venv\Scripts\python.exe -m mypy cli core utils services models --ignore-missing-imports'
        fix = ''
        canAutoFix = $false
    },
    @{
        name = "6 PYTEST (Tests)"
        test = '.\.venv\Scripts\python.exe -m pytest Dev/pytests/ -q --tb=line'
        fix = ''
        canAutoFix = $false
    }
)

$passedChecks = @()
$failedChecks = @()
$autoFixedChecks = @()
$startTime = Get-Date

foreach ($check in $checks) {
    Write-Host "`n$($check.name)" -ForegroundColor $colors.Warning
    Write-Host "────────────────────────────────────────────────────────"
    
    # Run test
    if ($Verbose) {
        Write-Host "Exécution: $($check.test)`n" -ForegroundColor $colors.Info
        Invoke-Expression $check.test
    } else {
        $output = Invoke-Expression $check.test 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PASSED" -ForegroundColor $colors.Success
        $passedChecks += $check.name
    } else {
        Write-Host "❌ FAILED" -ForegroundColor $colors.Error
        $failedChecks += $check.name
        
        # Show test output for failed checks
        if (-not $Verbose) {
            Write-Host "`nDétails:" -ForegroundColor $colors.Info
            if ($output) {
                $output | Select-Object -First 20
            }
        }
        
        # Try auto-fix if enabled
        if ($AutoFix -and $check.canAutoFix) {
            Write-Host "`nAttempting auto-fix..." -ForegroundColor $colors.Warning
            Invoke-Expression $check.fix 2>&1 | Out-Null
            
            Write-Host "Re-testing..." -ForegroundColor $colors.Info
            Invoke-Expression $check.test 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ AUTO-FIXED" -ForegroundColor $colors.Success
                $autoFixedChecks += $check.name
                $failedChecks = @($failedChecks | Where-Object { $_ -ne $check.name })
            } else {
                Write-Host "Manual fix required" -ForegroundColor $colors.Warning
            }
        }
    }
}

# Résumé final
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n========== FINAL SUMMARY ==========" -ForegroundColor $colors.Info
Write-Host "Duration: $([Math]::Round($duration.TotalSeconds, 2)) seconds" -ForegroundColor $colors.Info
Write-Host "`nPassed: $($passedChecks.Count)/$($checks.Count)" -ForegroundColor $colors.Success

if ($autoFixedChecks.Count -gt 0) {
    Write-Host "`nAuto-Fixed: $($autoFixedChecks.Count)" -ForegroundColor $colors.Warning
}

if ($failedChecks.Count -gt 0) {
    Write-Host "`nFailed: $($failedChecks.Count)" -ForegroundColor $colors.Error
    foreach ($failed in $failedChecks) {
        Write-Host "  - $failed" -ForegroundColor $colors.Error
    }
    Write-Host "`nSee Dev/docs/reference/QUALITY_EXECUTION.md for fix instructions" -ForegroundColor $colors.Warning
    exit 1
} else {
    Write-Host "`nALL CHECKS PASSED!" -ForegroundColor $colors.Success
    Write-Host "Project is production-ready!" -ForegroundColor $colors.Success
    exit 0
}
