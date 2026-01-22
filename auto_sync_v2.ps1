# Auto-Sync Script for NotaireAI - Version 2
# Améliorations:
# - Chemin relatif (fonctionne pour tous)
# - Logs persistants
# - Notification sonore sur conflit
# - Sleep optimisé
# - Meilleure gestion des erreurs

param(
    [int]$SYNC_INTERVAL_MINUTES = 60,
    [int]$PUSH_INTERVAL_MINUTES = 30,
    [string]$BRANCH = "",  # Auto-détecté si vide
    [switch]$VERBOSE = $false
)

# Détection automatique du chemin du projet
$projectPath = $PSScriptRoot
if ([string]::IsNullOrEmpty($projectPath)) {
    $projectPath = Get-Location
}

Set-Location $projectPath

# Auto-détection de la branche si non spécifiée
if ([string]::IsNullOrEmpty($BRANCH)) {
    $BRANCH = git rev-parse --abbrev-ref HEAD
    Write-Host "🔍 Branche auto-détectée: $BRANCH"
}

# Validation de la branche
if ($BRANCH -eq "master" -or $BRANCH -eq "main") {
    Write-Host "❌ ERREUR: Vous ne pouvez pas utiliser auto-sync sur la branche master/main !"
    Write-Host "   Créez d'abord votre branche de développement:"
    Write-Host "   git checkout -b votre-nom/dev"
    exit 1
}

# Création du fichier de log
$logFile = Join-Path $projectPath ".auto_sync.log"

function Write-Log {
    param([string]$message, [string]$level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$level] $message"

    # Console
    Write-Host $logMessage

    # Fichier (garder les 1000 dernières lignes)
    Add-Content -Path $logFile -Value $logMessage

    $lines = Get-Content $logFile
    if ($lines.Count -gt 1000) {
        $lines[-1000..-1] | Set-Content $logFile
    }
}

function Play-Sound {
    param([string]$type = "beep")

    if ($type -eq "error") {
        [Console]::Beep(400, 500)
        [Console]::Beep(300, 500)
    } elseif ($type -eq "success") {
        [Console]::Beep(800, 200)
    } else {
        [Console]::Beep(600, 300)
    }
}

$syncSeconds = $SYNC_INTERVAL_MINUTES * 60
$pushSeconds = $PUSH_INTERVAL_MINUTES * 60
$lastSync = Get-Date
$lastPush = Get-Date
$conflictMode = $false

Write-Log "🚀 NotaireAI Auto-Sync v2 Started" "INFO"
Write-Log "Branch: $BRANCH" "INFO"
Write-Log "Sync with master: every $SYNC_INTERVAL_MINUTES minutes" "INFO"
Write-Log "Push changes: every $PUSH_INTERVAL_MINUTES minutes" "INFO"
Write-Log "Log file: $logFile" "INFO"
Write-Host "═══════════════════════════════════════════════════════"

while ($true) {
    $now = Get-Date

    # Vérifier qu'on est sur la bonne branche
    $currentBranch = git rev-parse --abbrev-ref HEAD
    if ($currentBranch -ne $BRANCH) {
        Write-Log "⚠️  Not on $BRANCH (currently on $currentBranch), switching..." "WARN"
        git checkout $BRANCH
    }

    # MODE CONFLIT: Vérifier si résolu
    if ($conflictMode) {
        $status = git status --porcelain
        $inMerge = Test-Path (Join-Path (git rev-parse --git-dir) "MERGE_HEAD")

        if (-not $inMerge -and -not ($status -match "^UU ")) {
            Write-Log "✅ Conflit résolu ! Retour au mode normal." "INFO"
            Play-Sound "success"
            $conflictMode = $false
            $lastSync = $now
        } else {
            Write-Log "⚠️  En attente de résolution du conflit..." "WARN"
            Start-Sleep -Seconds 60
            continue
        }
    }

    # SYNC WITH MASTER
    $timeSinceSync = ($now - $lastSync).TotalSeconds
    if ($timeSinceSync -ge $syncSeconds) {
        Write-Log "🔄 Syncing with master..." "INFO"

        # Fetch latest from master
        git fetch origin master 2>&1 | Out-Null

        # Try to merge
        $mergeResult = git merge origin/master 2>&1

        if ($LASTEXITCODE -eq 0) {
            if ($mergeResult -match "Already up to date") {
                Write-Log "✅ Already up to date with master" "INFO"
            } else {
                Write-Log "✅ Successfully synced with master" "INFO"

                # Push the merge
                git push origin $BRANCH 2>&1 | Out-Null
                Write-Log "✅ Pushed sync to $BRANCH" "INFO"
                Play-Sound "success"
            }
        } else {
            Write-Log "❌ MERGE CONFLICT DETECTED!" "ERROR"
            Write-Log "❌ Action requise: Résoudre les conflits manuellement" "ERROR"
            Write-Log "   1. Ouvrir les fichiers en conflit" "ERROR"
            Write-Log "   2. Résoudre les conflits (chercher <<<<<<<)" "ERROR"
            Write-Log "   3. git add . && git commit && git push origin $BRANCH" "ERROR"

            Play-Sound "error"

            # Ne pas abort: laisser l'utilisateur résoudre
            $conflictMode = $true
        }

        $lastSync = $now
    }

    # PUSH CHANGES (skip si en mode conflit)
    if (-not $conflictMode) {
        $timeSincePush = ($now - $lastPush).TotalSeconds

        if ($timeSincePush -ge $pushSeconds) {
            # Check if there are changes
            $status = git status --porcelain

            if ($status) {
                Write-Log "📤 Changes detected, committing and pushing..." "INFO"

                # Add all changes
                git add . 2>&1 | Out-Null

                # Commit with timestamp
                $commitMsg = "auto: Sauvegarde automatique sur $BRANCH - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                git commit -m $commitMsg 2>&1 | Out-Null

                # Push to the current branch
                $pushResult = git push origin $BRANCH 2>&1

                if ($LASTEXITCODE -eq 0) {
                    Write-Log "✅ Push completed to $BRANCH!" "INFO"
                } else {
                    Write-Log "❌ Push failed: $pushResult" "ERROR"
                    Play-Sound "error"
                }
            } else {
                if ($VERBOSE) {
                    Write-Log "⏸️  No changes to push." "INFO"
                }
            }

            $lastPush = $now
        }
    }

    # Calculer le prochain événement
    $nextSync = $syncSeconds - $timeSinceSync
    $nextPush = $pushSeconds - $timeSincePush
    $nextEvent = [math]::Min($nextSync, $nextPush)

    # Ne pas dépasser 5 minutes de sleep
    $sleepTime = [math]::Min($nextEvent, 300)

    if (-not $conflictMode) {
        $nextSyncMin = [math]::Ceiling($nextSync / 60)
        $nextPushMin = [math]::Ceiling($nextPush / 60)
        Write-Log "⏳ Next sync in ~$nextSyncMin min | Next push in ~$nextPushMin min" "INFO"
        Write-Host "───────────────────────────────────────────────────────"
    }

    Start-Sleep -Seconds $sleepTime
}
