@echo off
REM Ultimate Simple Workflow - NotaireAI - PAYOSS
REM Double-click le matin, oubliez tout le reste

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Demarrage Journee (PAYOSS)
echo ========================================
echo.

REM 1. Merge toutes les PRs automatiquement
echo [1/3] Merge des PRs...
powershell -ExecutionPolicy Bypass -File ".\morning_sync.ps1" -AUTO_APPROVE

REM 2. Lancer auto-sync en arriere-plan
echo [2/3] Lancement auto-sync...
start /min powershell -ExecutionPolicy Bypass -File ".\auto_sync_v2.ps1" -BRANCH "payoss/dev"

echo [3/3] Termine !
echo.
echo ========================================
echo   PRET ! Vous pouvez travailler.
echo ========================================
echo.
echo Auto-sync tourne en arriere-plan.
echo Vos changements sont sauvegardes automatiquement.
echo.
pause
