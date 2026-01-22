# Morning Sync Script - NotaireAI
# Review et merge les PRs, puis sync votre branche

param(
    [switch]$AUTO_APPROVE = $false,  # DANGER: Auto-approve sans review
    [switch]$DRY_RUN = $false        # Test sans merger
)

Write-Host "🌅 NotaireAI Morning Sync"
Write-Host "═══════════════════════════════════════"

# 1. Lister les PRs ouvertes
Write-Host "`n📋 Pull Requests ouvertes:"
$prs = gh pr list --json number,title,author --jq '.[]' | ConvertFrom-Json

if ($prs.Count -eq 0) {
    Write-Host "✅ Aucune PR à merger. Master est à jour !"
} else {
    foreach ($pr in $prs) {
        $number = $pr.number
        $title = $pr.title
        $author = $pr.author.login

        Write-Host "`n─────────────────────────────────────"
        Write-Host "PR #$number : $title"
        Write-Host "Auteur: $author"

        if ($DRY_RUN) {
            Write-Host "[DRY RUN] Simulation du merge..."
            continue
        }

        if ($AUTO_APPROVE) {
            Write-Host "⚠️  AUTO-APPROVE activé (pas de review)"
            gh pr review $number --approve
            gh pr merge $number --squash --delete-branch=false

            Write-Host "✅ PR #$number mergée"
        } else {
            # Mode interactif
            Write-Host "`nVoir les changements ? (y/n)"
            $view = Read-Host

            if ($view -eq "y") {
                gh pr diff $number
            }

            Write-Host "`nMerger cette PR ? (y/n)"
            $merge = Read-Host

            if ($merge -eq "y") {
                gh pr review $number --approve
                gh pr merge $number --squash --delete-branch=false

                Write-Host "✅ PR #$number mergée"
            } else {
                Write-Host "⏭️  PR #$number ignorée"
            }
        }
    }
}

# 2. Sync votre branche avec master
Write-Host "`n🔄 Sync avec master..."
git fetch origin
$mergeResult = git merge origin/master 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Branche synchronisée avec master"

    # Push
    $currentBranch = git rev-parse --abbrev-ref HEAD
    git push origin $currentBranch

    Write-Host "✅ Push sur $currentBranch"
} else {
    Write-Host "⚠️  Conflit détecté. Résoudre manuellement."
}

Write-Host "`n═══════════════════════════════════════"
Write-Host "🎉 Morning Sync terminé !"
Write-Host "`nVous êtes prêt à travailler avec la dernière version ! 🚀"
