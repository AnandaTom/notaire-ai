# Auto-Sync Script for NotaireAI
# Automatically syncs with master and pushes changes
# Combines fetch, merge, and push in one script

param(
    [int]$SYNC_INTERVAL_MINUTES = 60,
    [int]$PUSH_INTERVAL_MINUTES = 30,
    [string]$BRANCH = "tom/dev"
)

$projectPath = "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
$syncSeconds = $SYNC_INTERVAL_MINUTES * 60
$pushSeconds = $PUSH_INTERVAL_MINUTES * 60
$lastSync = Get-Date
$lastPush = Get-Date

Write-Host "🚀 NotaireAI Auto-Sync Started"
Write-Host "Branch: $BRANCH"
Write-Host "Sync with master: every $SYNC_INTERVAL_MINUTES minutes"
Write-Host "Push changes: every $PUSH_INTERVAL_MINUTES minutes"
Write-Host "═══════════════════════════════════════════════════════"

while ($true) {
    $now = Get-Date
    $timestamp = $now.ToString("yyyy-MM-dd HH:mm:ss")

    Set-Location $projectPath

    # Ensure we're on the right branch
    $currentBranch = git rev-parse --abbrev-ref HEAD
    if ($currentBranch -ne $BRANCH) {
        Write-Host "[$timestamp] ⚠️  Not on $BRANCH (currently on $currentBranch), switching..."
        git checkout $BRANCH
    }

    # SYNC WITH MASTER (every SYNC_INTERVAL_MINUTES)
    $timeSinceSync = ($now - $lastSync).TotalSeconds
    if ($timeSinceSync -ge $syncSeconds) {
        Write-Host "[$timestamp] 🔄 Syncing with master..."

        # Fetch latest from master
        git fetch origin master

        # Try to merge
        $mergeOutput = git merge origin/master 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$timestamp] ✅ Successfully synced with master"

            # Push the merge
            git push origin $BRANCH
            Write-Host "[$timestamp] ✅ Pushed sync to $BRANCH"
        } else {
            Write-Host "[$timestamp] ⚠️  Merge conflict detected!"
            Write-Host "[$timestamp] ⚠️  Please resolve conflicts manually and run:"
            Write-Host "           git add . && git commit && git push origin $BRANCH"
            # Abort the merge to keep working
            git merge --abort 2>$null
        }

        $lastSync = $now
    }

    # PUSH CHANGES (every PUSH_INTERVAL_MINUTES)
    $timeSincePush = ($now - $lastPush).TotalSeconds
    if ($timeSincePush -ge $pushSeconds) {
        # Check if there are changes
        $status = git status --porcelain

        if ($status) {
            Write-Host "[$timestamp] 📤 Changes detected, committing and pushing..."

            # Add all changes
            git add .

            # Commit with timestamp
            git commit -m "auto: Sauvegarde automatique sur $BRANCH - $timestamp"

            # Push to the current branch
            git push origin $BRANCH

            Write-Host "[$timestamp] ✅ Push completed to $BRANCH!"
        } else {
            Write-Host "[$timestamp] ⏸️  No changes to push."
        }

        $lastPush = $now
    }

    # Show next actions
    $nextSync = $SYNC_INTERVAL_MINUTES - [math]::Floor($timeSinceSync / 60)
    $nextPush = $PUSH_INTERVAL_MINUTES - [math]::Floor($timeSincePush / 60)

    Write-Host "[$timestamp] ⏳ Next sync in ~$nextSync min | Next push in ~$nextPush min"
    Write-Host "───────────────────────────────────────────────────────"

    # Sleep 5 minutes between checks
    Start-Sleep -Seconds 300
}
