@echo off
setlocal enabledelayedexpansion
REM End of Day v3.1 - NotaireAI
REM Commit message intelligent depuis memory/JOURNAL.md
REM Les autres devs/agents peuvent lire git log pour eviter les doublons

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Fin de Journee v3.1
echo ========================================
echo.

REM 0. Recuperer la branche courante
FOR /F "tokens=*" %%i IN ('git rev-parse --abbrev-ref HEAD') DO SET BRANCH=%%i
echo Branche: %BRANCH%
echo.

REM 1. Verifier s'il y a des changements
echo [1/6] Verification des changements...
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
echo [2/6] Staging des fichiers...

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

REM 3. Verifier le journal de session
echo [3/6] Verification du journal de session...

REM Creer .tmp si necessaire
if not exist .tmp mkdir .tmp

REM Extraire le nom du dev depuis la branche
SET DEV_NAME=
FOR /F "tokens=1 delims=/" %%d IN ("%BRANCH%") DO SET DEV_NAME=%%d

REM Date locale-independante (YYYY-MM-DD)
FOR /F "tokens=*" %%d IN ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') DO SET TODAY=%%d
SET JOURNAL_FOUND=0
IF EXIST "memory\JOURNAL.md" (
    findstr /C:"## %TODAY%" "memory\JOURNAL.md" >nul 2>nul
    IF !ERRORLEVEL! EQU 0 SET JOURNAL_FOUND=1
)

IF !JOURNAL_FOUND! EQU 0 (
    echo.
    echo  *** ATTENTION ***
    echo  Aucune entree dans memory/JOURNAL.md pour aujourd'hui ^(%TODAY%^)
    echo  Le commit sera genere depuis git diff ^(mode auto^).
    echo  Pour un meilleur suivi: demandez a l'agent d'ecrire dans le journal.
    echo.
    echo  Continuer quand meme ? ^(O/N^)
    set /p CONTINUE_CHOICE="> "
    IF /I "!CONTINUE_CHOICE!" NEQ "O" (
        echo Commit annule. Remplissez le journal puis relancez END_DAY.bat
        echo.
        pause
        exit /b 0
    )
)

REM 4. Generer le commit message depuis le journal
echo [4/6] Generation du commit message depuis le journal...

python generate_commit_msg.py --dev "%DEV_NAME%"

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
    echo ATTENTION: Generation du message echouee - commit generique utilise
    git commit -m "[%DEV_NAME%] Travail du %TODAY%"
)

REM Verifier que le commit a reussi
IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERREUR: Commit echoue. Verifier les hooks pre-commit.
    echo.
    pause
    exit /b 1
)

REM 5. Pull puis Push
echo [5/6] Push sur %BRANCH%...
git pull --rebase origin %BRANCH%

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERREUR: Rebase echoue. Resoudre les conflits manuellement.
    echo Apres resolution: git rebase --continue, puis relancez END_DAY.bat
    echo.
    pause
    exit /b 1
)

git push origin %BRANCH%

IF !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERREUR: Push echoue. Verifier la connexion et les droits.
    echo.
    pause
    exit /b 1
)

REM 6. Creer PR seulement s'il n'en existe pas deja une
echo [6/6] Verification Pull Request...

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
del /q "%TEMP%\notomai_status.tmp" 2>nul
del /q "%TEMP%\notomai_pr.tmp" 2>nul
echo.
pause
endlocal
