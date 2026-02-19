@echo off
REM Ultimate Simple Workflow - NotaireAI - PAYOSS v2.0
REM Double-click le matin, oubliez tout le reste
REM Inclut la lecture des commits des autres devs

cd /d "C:\Users\paula\IA\VSCode\notaire-ai"

echo.
echo ========================================
echo   NotaireAI - Demarrage Journee (PAYOSS)
echo ========================================
echo.

REM 1. Merge toutes les PRs automatiquement
echo [1/4] Merge des PRs...
powershell -ExecutionPolicy Bypass -File "morning_sync.ps1" -AUTO_APPROVE

REM 2. Lire les commits des autres devs (anti-doublon)
echo [2/4] Lecture des commits de l'equipe...
python read_team_commits.py --days 2 --output 2>nul
IF EXIST ".tmp\team_commits.md" (
    echo.
    echo --- RESUME EQUIPE ---
    type ".tmp\team_commits.md"
    echo --- FIN RESUME ---
    echo.
) ELSE (
    echo Pas de commits recents des autres devs.
)

REM 3. Lancer auto-sync en arriere-plan
echo [3/4] Lancement auto-sync...
start /min powershell -ExecutionPolicy Bypass -File "auto_sync_v2.ps1" -BRANCH "payoss/dev"

echo [4/4] Termine !
echo.
echo ========================================
echo   PRET ! Vous pouvez travailler.
echo ========================================
echo.
echo Auto-sync tourne en arriere-plan.
echo Vos changements sont sauvegardes automatiquement.
echo Le resume equipe est dans .tmp\team_commits.md
echo.
pause
