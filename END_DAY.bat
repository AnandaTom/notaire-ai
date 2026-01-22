@echo off
REM End of Day - NotaireAI
REM Double-click le soir, cree la PR automatiquement

cd /d "%~dp0"

echo.
echo ========================================
echo   NotaireAI - Fin de Journee
echo ========================================
echo.

REM 1. Dernier commit
echo [1/3] Dernier commit...
git add .
git commit -m "chore: Fin de journee - %date% %time%"

REM 2. Push
echo [2/3] Push sur votre branche...
FOR /F "tokens=*" %%i IN ('git rev-parse --abbrev-ref HEAD') DO SET BRANCH=%%i
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
