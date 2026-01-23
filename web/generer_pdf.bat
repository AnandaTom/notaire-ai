@echo off
echo ========================================
echo NotaireAI - Generation PDF Formulaire
echo ========================================
echo.
echo Choisissez une methode:
echo   1. Generation automatique (Chrome/Edge headless)
echo   2. Impression manuelle (ouvre le navigateur)
echo.
choice /C 12 /N /M "Votre choix (1 ou 2): "

if errorlevel 2 goto manual
if errorlevel 1 goto auto

:auto
echo.
echo Generation automatique du PDF...
powershell -ExecutionPolicy Bypass -File "%~dp0generer_pdf_auto.ps1"
goto end

:manual
echo.
echo Ouverture de la version imprimable...
echo.
echo Instructions:
echo   1. Cliquez sur "Remplir avec exemple" (optionnel)
echo   2. Appuyez sur Ctrl+P pour imprimer
echo   3. Choisissez "Microsoft Print to PDF"
echo   4. Cochez "Graphiques d'arriere-plan"
echo   5. Enregistrez le fichier
echo.
start print_version.html

:end
echo.
echo Appuyez sur une touche pour fermer...
pause >nul
