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
$prsJson = gh pr list --json number,title,author,headRefName 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la récupération des PRs"
    Write-Host $prsJson
    exit 1
}

$prs = $prsJson | ConvertFrom-Json

if ($prs.Count -eq 0) {
    Write-Host "✅ Aucune PR à merger. Master est à jour !"
} else {
    Write-Host "   Trouvé $($prs.Count) PR(s) ouverte(s)"

    foreach ($pr in $prs) {
        $number = $pr.number
        $title = $pr.title
        $author = $pr.author.login
        $branch = $pr.headRefName

        Write-Host "`n─────────────────────────────────────"
        Write-Host "PR #$number : $title"
        Write-Host "Auteur: $author ($branch)"

        if ($DRY_RUN) {
            Write-Host "[DRY RUN] Simulation du merge..."
            continue
        }

        if ($AUTO_APPROVE) {
            Write-Host "⚠️  AUTO-APPROVE activé (pas de review manuelle)"

            # Approve
            gh pr review $number --approve 2>&1 | Out-Null

            # Merge
            $mergeResult = gh pr merge $number --squash --delete-branch=false 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ PR #$number mergée automatiquement"
            } else {
                Write-Host "❌ Erreur lors du merge: $mergeResult"
            }
        } else {
            # Mode interactif
            Write-Host "`nActions disponibles:"
            Write-Host "  [v] Voir les changements (git diff)"
            Write-Host "  [m] Merger cette PR"
            Write-Host "  [s] Skip (ignorer)"
            Write-Host "  [q] Quit (arrêter)"

            $action = Read-Host "`nVotre choix"

            switch ($action.ToLower()) {
                "v" {
                    gh pr diff $number
                    Write-Host "`nMerger maintenant ? (y/n)"
                    $merge = Read-Host

                    if ($merge -eq "y") {
                        gh pr review $number --approve 2>&1 | Out-Null
                        gh pr merge $number --squash --delete-branch=false 2>&1 | Out-Null
                        Write-Host "✅ PR #$number mergée"
                    }
                }
                "m" {
                    gh pr review $number --approve 2>&1 | Out-Null
                    gh pr merge $number --squash --delete-branch=false 2>&1 | Out-Null
                    Write-Host "✅ PR #$number mergée"
                }
                "s" {
                    Write-Host "⏭️  PR #$number ignorée"
                }
                "q" {
                    Write-Host "👋 Arrêt du script"
                    break
                }
                default {
                    Write-Host "⏭️  Action invalide, PR ignorée"
                }
            }
        }
    }
}

# 2. Sync votre branche avec master
Write-Host "`n🔄 Synchronisation avec master..."
git fetch origin 2>&1 | Out-Null

$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "   Branche actuelle: $currentBranch"

$mergeResult = git merge origin/master 2>&1

if ($LASTEXITCODE -eq 0) {
    if ($mergeResult -match "Already up to date") {
        Write-Host "✅ Déjà à jour avec master"
    } else {
        Write-Host "✅ Branche synchronisée avec master"

        # Push
        git push origin $currentBranch 2>&1 | Out-Null
        Write-Host "✅ Push sur $currentBranch"
    }
} else {
    Write-Host "⚠️  Conflit détecté lors du merge avec master"
    Write-Host "   Résoudre les conflits manuellement:"
    Write-Host "   1. Ouvrir les fichiers en conflit"
    Write-Host "   2. git add . && git commit"
    Write-Host "   3. git push origin $currentBranch"
}

Write-Host "`n═══════════════════════════════════════"
Write-Host "🎉 Morning Sync terminé !"
Write-Host "`nVous êtes prêt à travailler avec la dernière version ! 🚀"
