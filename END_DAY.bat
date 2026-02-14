@echo off
REM End of Day v2.0 - NotaireAI
REM Ameliore: check changements, check PR existante, git add cible

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Fin de Journee v2.0
echo ========================================
echo.

REM 0. Recuperer la branche courante
FOR /F "tokens=*" %%i IN ('git rev-parse --abbrev-ref HEAD') DO SET BRANCH=%%i
echo Branche: %BRANCH%
echo.

REM 1. Verifier s'il y a des changements
echo [1/4] Verification des changements...
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

REM 2. Commit cible (pas de git add aggressif)
echo [2/4] Commit des changements...

REM Ajouter les fichiers modifies (tracked)
git add --update

REM Ajouter les nouveaux fichiers par dossier (safe)
git add templates/ schemas/ directives/ execution/ docs/ api/ frontend/ supabase/ tests/ 2>nul
git add modal/ deployment_modal/ 2>nul

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

git commit -m "chore: Travail du %date%"

REM 3. Pull puis Push
echo [3/4] Push sur %BRANCH%...
git pull --rebase origin %BRANCH% 2>nul
git push origin %BRANCH%

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo Erreur de push - tentative avec force-with-lease...
    git push --force-with-lease origin %BRANCH%
)

REM 4. Creer PR seulement s'il n'en existe pas deja une
echo [4/4] Verification Pull Request...

gh pr list --head %BRANCH% --state open --json number > "%TEMP%\notomai_pr.tmp" 2>nul
findstr /C:"number" "%TEMP%\notomai_pr.tmp" >nul 2>nul

IF %ERRORLEVEL% EQU 0 (
    echo PR deja ouverte pour %BRANCH% - pas de doublon.
    echo.
    echo ========================================
    echo   Push OK - PR existante mise a jour
    echo   Bonne soiree !
    echo ========================================
) ELSE (
    echo Creation d'une nouvelle PR...
    gh pr create --title "Travail du %date%" --body "Auto-PR - Travail de la journee sur %BRANCH%" 2>nul

    IF %ERRORLEVEL% EQU 0 (
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
)

echo.
pause
