@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    SAUVEGARDE RAPIDE - NotaireAI
echo ========================================
echo.

cd /d "%~dp0"

:: Ajouter tous les fichiers
git add -A

:: Commit avec message automatique (date/heure)
set MSG=Auto-save %date% %time:~0,5%
git commit -m "%MSG%"

:: Push vers ta branche
git push

echo.
echo ✅ Sauvegarde terminée !
echo.
pause
