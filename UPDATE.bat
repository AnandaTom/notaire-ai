@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    MISE A JOUR - NotaireAI
echo ========================================
echo.

cd /d "%~dp0"

:: Récupérer la dernière version de master
git pull origin master

echo.
echo ✅ Projet mis à jour avec la dernière version !
echo.
pause
