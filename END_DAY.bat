@echo off
setlocal enabledelayedexpansion
REM End of Day v3.0 - NotaireAI
REM Commit message intelligent depuis memory/JOURNAL.md
REM Les autres devs/agents peuvent lire git log pour eviter les doublons

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Fin de Journee v3.0
echo ========================================
echo.

REM 0. Recuperer la branche courante
FOR /F "tokens=*" %%i IN ('git rev-parse --abbrev-ref HEAD') DO SET BRANCH=%%i
echo Branche: %BRANCH%
echo.

REM 1. Verifier s'il y a des changements
echo [1/5] Verification des changements...
git status --porcelain > "%TEMP%\notomai_status.tmp"
FOR %%A IN ("%TEMP%\notomai_status.tmp") DO SET STATUS_SIZE=%%~zA

IF %STATUS_SIZE% EQU 0 (
    echo Aucun changement detecte.
    echo.
    echo ========================================
    echo   Rien a commiter - Bonne soiree !
    echo ========================================
    echo.
    pause
    exit /b 0
)

REM 2. Stage les fichiers (comme avant, safe)
echo [2/5] Staging des fichiers...

REM Ajouter les fichiers modifies (tracked)
git add --update

REM Ajouter les nouveaux fichiers par dossier (safe)
git add templates/ schemas/ directives/ execution/ docs/ api/ frontend/ supabase/ tests/ 2>nul
git add modal/ deployment_modal/ memory/ scripts/ 2>nul

REM Ajouter les fichiers a la racine (BAT, PY utils)
git add *.bat *.py *.ps1 2>nul

REM Ne jamais commiter les secrets
git reset -- .env .env.* .mcp.json .claude/settings.local.json 2>nul
git reset -- deploy_log.txt .auto_sync.log 2>nul

REM Verifier qu'il y a bien des fichiers stages
git diff --cached --quiet
IF %ERRORLEVEL% EQU 0 (
    echo Aucun fichier a commiter apres filtrage.
    echo.
    echo ========================================
    echo   Rien a commiter - Bonne soiree !
    echo ========================================
    echo.
    pause
    exit /b 0
)

REM 3. Generer le commit message depuis le journal
echo [3/5] Generation du commit message depuis le journal...

REM Creer .tmp si necessaire
if not exist .tmp mkdir .tmp

REM Extraire le nom du dev depuis la branche
SET DEV_NAME=
FOR /F "tokens=1 delims=/" %%d IN ("%BRANCH%") DO SET DEV_NAME=%%d

python generate_commit_msg.py --dev "%DEV_NAME%" 2>nul

REM Verifier si le fichier a ete genere
IF EXIST ".tmp\commit_msg.txt" (
    echo Message genere depuis memory/JOURNAL.md
    echo ---
    type ".tmp\commit_msg.txt"
    echo ---
    echo.

    REM Commit avec le message genere
    git commit -F ".tmp\commit_msg.txt"
) ELSE (
    echo Pas de journal trouve - commit standard
    git commit -m "[%DEV_NAME%] Travail du %date%"
)

REM 4. Pull puis Push
echo [4/5] Push sur %BRANCH%...
git pull --rebase origin %BRANCH% 2>nul
git push origin %BRANCH%

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo Erreur de push - tentative avec force-with-lease...
    git push --force-with-lease origin %BRANCH%
)

REM 5. Creer PR seulement s'il n'en existe pas deja une
echo [5/5] Verification Pull Request...

gh pr list --head %BRANCH% --state open --json number > "%TEMP%\notomai_pr.tmp" 2>nul
findstr /C:"number" "%TEMP%\notomai_pr.tmp" >nul 2>nul

IF !ERRORLEVEL! EQU 0 (
    echo PR deja ouverte pour %BRANCH% - pas de doublon.
    echo.
    echo ========================================
    echo   Push OK - PR existante mise a jour
    echo   Commit message detaille inclus !
    echo   Bonne soiree !
    echo ========================================
    goto :end
)

echo Creation d'une nouvelle PR...
gh pr create --title "[%DEV_NAME%] Travail du %date%" --body "Auto-PR - Travail de la journee sur %BRANCH%. Voir le commit message pour les details." 2>nul

IF !ERRORLEVEL! EQU 0 (
    echo.
    echo ========================================
    echo   PR creee ! Bonne soiree !
    echo ========================================
) ELSE (
    echo.
    echo ========================================
    echo   Push OK mais PR non creee
    echo   (peut-etre aucune difference avec master)
    echo   Bonne soiree !
    echo ========================================
)

:end
REM Nettoyage
del /q ".tmp\commit_msg.txt" 2>nul
echo.
pause
endlocal
