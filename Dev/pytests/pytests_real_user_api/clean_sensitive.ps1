<#
Usage: Run from repository root (PowerShell):
  .\Dev\pytests\pytests_real_user_api\clean_sensitive.ps1

This script moves JSON/TXT cookie/sample files from the real-user
folder into a timestamped archive under %TEMP% to avoid accidental
commit/push of sensitive data.
#>

param()

set -ea

$repoRoot = Split-Path -Path $PSScriptRoot -Parent -Parent -Parent
$dataDir = Join-Path $repoRoot 'Dev\pytests\pytests_real_user_api\data'
if (!(Test-Path $dataDir)) {
    Write-Host "No data directory found at $dataDir"
    exit 0
}

$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$archive = Join-Path $env:TEMP "pytests_real_user_api_backup_$ts"
New-Item -ItemType Directory -Path $archive | Out-Null

Get-ChildItem -Path $dataDir -Include '*.json','*.txt' -File -Recurse | ForEach-Object {
    $dest = Join-Path $archive $_.Name
    Move-Item -Path $_.FullName -Destination $dest
    Write-Host "Moved $_ to $dest"
}

Write-Host "Sensitive files moved to $archive"