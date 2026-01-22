@echo off
REM Auto-push launcher for NotaireAI
REM Double-click this file to start auto-push

cd /d "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"

REM Start PowerShell with the auto_push script
REM Default: 30 minutes, branch: tom/dev
REM To customize: edit auto_push.ps1 or pass parameters

powershell -ExecutionPolicy Bypass -File ".\auto_push.ps1" -INTERVAL_MINUTES 30 -BRANCH "tom/dev"

pause
