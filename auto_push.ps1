# Auto-push script for NotaireAI
# Runs every 30 minutes and pushes changes to GitHub

$projectPath = "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    Set-Location $projectPath

    # Check if there are changes
    $status = git status --porcelain

    if ($status) {
        Write-Host "[$timestamp] Changes detected, pushing to GitHub..."

        # Add all changes
        git add .

        # Commit with timestamp
        git commit -m "auto: Sauvegarde automatique - $timestamp"

        # Push
        git push

        Write-Host "[$timestamp] Push completed!"
    } else {
        Write-Host "[$timestamp] No changes to push."
    }

    # Wait 1 hour (3600 seconds)
    Write-Host "[$timestamp] Next push in 1 hour..."
    Start-Sleep -Seconds 3600
}
