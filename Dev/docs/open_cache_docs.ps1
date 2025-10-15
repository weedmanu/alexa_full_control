# Script PowerShell pour ouvrir la documentation HTML du système de cache
# Usage: .\docs\open_cache_docs.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Documentation du Système de Cache" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$htmlFile = Join-Path $PSScriptRoot "CACHE_SYSTEM.html"

if (-not (Test-Path $htmlFile)) {
    Write-Host "[ERREUR]" -ForegroundColor Red -NoNewline
    Write-Host " Fichier HTML non trouvé: $htmlFile"
    Write-Host ""
    Write-Host "Vérifiez que le fichier existe ou régénérez-le avec:"
    Write-Host "  python scripts\update_cache_html.py" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

Write-Host "[INFO]" -ForegroundColor Green -NoNewline
Write-Host " Ouverture de la documentation..."
Write-Host "       Fichier: " -NoNewline
Write-Host $htmlFile -ForegroundColor Cyan
Write-Host ""

# Ouvrir avec le navigateur par défaut
Start-Process $htmlFile

Write-Host "[OK]" -ForegroundColor Green -NoNewline
Write-Host " Documentation ouverte dans le navigateur par défaut."
Write-Host ""
Write-Host "Navigation:" -ForegroundColor Yellow
Write-Host "  + Vue d'ensemble"
Write-Host "  + Diagrammes interactifs (onglets)"
Write-Host "  + Architecture technique"
Write-Host "  + Performance et statistiques"
Write-Host "  + Configuration"
Write-Host "  + Debogage"
Write-Host ""

Start-Sleep -Seconds 2
