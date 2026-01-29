@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    SAUVEGARDE RAPIDE - NotaireAI
echo ========================================
echo.

cd /d "%~dp0"

:: Ajouter les fichiers modifies (pas les nouveaux non tracked)
git add --update
:: Securite: retirer les fichiers sensibles du staging
git reset -- .env .env.* .mcp.json .claude/settings.local.json 2>nul

:: Commit avec message automatique (date/heure)
set MSG=Auto-save %date% %time:~0,5%
git commit -m "%MSG%"

:: Push vers ta branche
git push

echo.
echo ✅ Sauvegarde terminée !
echo.
pause
