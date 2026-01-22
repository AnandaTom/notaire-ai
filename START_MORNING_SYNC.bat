@echo off
REM Morning Sync - Review PRs et sync avec master
REM Double-click pour lancer le morning sync

cd /d "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"

echo.
echo ===================================================
echo   Morning Sync - NotaireAI
echo ===================================================
echo.
echo Ce script va:
echo  1. Lister les PRs ouvertes
echo  2. Vous permettre de les reviewer et merger
echo  3. Synchroniser votre branche avec master
echo.
echo MODES:
echo  - Mode INTERACTIF (recommande) : Vous choisissez quoi merger
echo  - Mode AUTO (DANGER) : Merge tout automatiquement
echo.

set /p MODE="Lancer en mode AUTO ? (y/N): "

if /i "%MODE%"=="y" (
    echo.
    echo ATTENTION: Mode AUTO active - Toutes les PRs seront mergees sans review !
    set /p CONFIRM="Etes-vous sur ? (yes pour confirmer): "

    if /i "%CONFIRM%"=="yes" (
        powershell -ExecutionPolicy Bypass -File ".\morning_sync.ps1" -AUTO_APPROVE
    ) else (
        echo Annule. Lancement en mode interactif...
        powershell -ExecutionPolicy Bypass -File ".\morning_sync.ps1"
    )
) else (
    powershell -ExecutionPolicy Bypass -File ".\morning_sync.ps1"
)

echo.
pause
