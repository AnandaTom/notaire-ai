@echo off
REM End of Day - NotaireAI
REM Double-click le soir, cree la PR automatiquement

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Fin de Journee
echo ========================================
echo.

REM 1. Verification securite avant commit
echo [1/3] Dernier commit...
git add --update
git add templates/ schemas/ directives/ execution/ docs/ api/ modal/ clauses/ actes_finaux/ web/ dashboard/ frontend/ supabase/ tests/
git add *.py *.md *.json *.ps1 *.bat *.html *.css *.js
REM Ne jamais commiter les secrets
git reset -- .env .env.* .mcp.json .claude/settings.local.json 2>nul
git commit -m "chore: Fin de journee - %date% %time%"

REM 2. Pull puis Push
echo [2/3] Push sur votre branche...
FOR /F "tokens=*" %%i IN ('git rev-parse --abbrev-ref HEAD') DO SET BRANCH=%%i
REM Pull d'abord pour eviter le rejet non-fast-forward
git pull --rebase origin %BRANCH% 2>nul
git push origin %BRANCH%

REM 3. Creer PR si pas deja faite
echo [3/3] Creation Pull Request...
gh pr create --title "Travail du %date%" --body "Auto-PR - Travail de la journee" 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   PR creee ! Bonne soiree !
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   PR deja existante ou pas de nouveau code
    echo   Bonne soiree !
    echo ========================================
)

echo.
pause
