@echo off
REM Script pour ouvrir la documentation HTML du système de cache
REM Usage: docs\open_cache_docs.bat

echo.
echo ========================================
echo  Documentation du Systeme de Cache
echo ========================================
echo.

set HTML_FILE=%~dp0CACHE_SYSTEM.html

if not exist "%HTML_FILE%" (
    echo [ERREUR] Fichier HTML non trouve: %HTML_FILE%
    echo.
    echo Verifiez que le fichier existe ou regenerez-le avec:
    echo   python scripts\update_cache_html.py
    echo.
    pause
    exit /b 1
)

echo [INFO] Ouverture de la documentation...
echo        Fichier: %HTML_FILE%
echo.

REM Ouvrir avec le navigateur par défaut
start "" "%HTML_FILE%"

echo [OK] Documentation ouverte dans le navigateur par defaut.
echo.
echo Navigation:
echo   - Vue d'ensemble
echo   - Diagrammes interactifs (onglets)
echo   - Architecture technique
echo   - Performance et statistiques
echo   - Configuration
echo   - Debogage
echo.

timeout /t 3 /nobreak >nul
