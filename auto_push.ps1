# Auto-push script for NotaireAI
# Runs every X minutes and pushes changes to GitHub
# Customize INTERVAL_MINUTES below

param(
    [int]$INTERVAL_MINUTES = 30,
    [string]$BRANCH = "tom/dev"
)

$projectPath = "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
$intervalSeconds = $INTERVAL_MINUTES * 60

Write-Host "🚀 NotaireAI Auto-Push Started"
Write-Host "Branch: $BRANCH"
Write-Host "Interval: $INTERVAL_MINUTES minutes"
Write-Host "───────────────────────────────────────"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Set-Location $projectPath

    # Ensure we're on the right branch
    $currentBranch = git rev-parse --abbrev-ref HEAD
    if ($currentBranch -ne $BRANCH) {
        Write-Host "[$timestamp] ⚠️  Not on $BRANCH (currently on $currentBranch), switching..."
        git checkout $BRANCH
    }

    # Check if there are changes
    $status = git status --porcelain

    if ($status) {
        Write-Host "[$timestamp] ✅ Changes detected, committing and pushing..."

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

    Write-Host "[$timestamp] ⏳ Next push in $INTERVAL_MINUTES minutes..."
    Write-Host "───────────────────────────────────────"
    Start-Sleep -Seconds $intervalSeconds
}
