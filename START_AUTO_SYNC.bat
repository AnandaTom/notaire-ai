@echo off
REM Auto-Sync launcher for NotaireAI
REM Double-click this file to start auto-sync (sync with master + auto-push)

cd /d "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"

REM Start PowerShell with the auto_sync script
REM Sync with master: every 60 minutes
REM Push changes: every 30 minutes

powershell -ExecutionPolicy Bypass -File ".\auto_sync.ps1" -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "tom/dev"

pause
