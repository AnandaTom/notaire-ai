# Morning Sync Script - NotaireAI
# Review et merge les PRs, puis sync votre branche

param(
    [switch]$AUTO_APPROVE = $false,
    [switch]$DRY_RUN = $false
)

Write-Host "NotaireAI Morning Sync"
Write-Host "========================================"

# 1. Lister les PRs ouvertes
Write-Host ""
Write-Host "Pull Requests ouvertes:"

try {
    $prsJson = gh pr list --json number,title,author,headRefName 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Aucune Pull Request ouverte pour le moment."
        $prs = @()
    } else {
        $prs = $prsJson | ConvertFrom-Json
    }
} catch {
    Write-Host "Aucune Pull Request ouverte pour le moment."
    $prs = @()
}

if ($prs.Count -eq 0) {
    Write-Host "Master est a jour - rien a merger."
} else {
    Write-Host "Trouve $($prs.Count) PR(s) ouverte(s)"

    foreach ($pr in $prs) {
        $number = $pr.number
        $title = $pr.title
        $author = $pr.author.login
        $branch = $pr.headRefName

        Write-Host ""
        Write-Host "----------------------------------------"
        Write-Host "PR #$number : $title"
        Write-Host "Auteur: $author ($branch)"

        if ($DRY_RUN) {
            Write-Host "[DRY RUN] Simulation du merge..."
            continue
        }

        if ($AUTO_APPROVE) {
            Write-Host "AUTO-APPROVE active"

            # Approve
            gh pr review $number --approve 2>&1 | Out-Null

            # Merge
            $mergeResult = gh pr merge $number --squash --delete-branch=false 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Host "PR #$number mergee automatiquement"
            } else {
                Write-Host "Erreur lors du merge: $mergeResult"
            }
        } else {
            # Mode interactif
            Write-Host ""
            Write-Host "Actions disponibles:"
            Write-Host "  [v] Voir les changements (git diff)"
            Write-Host "  [m] Merger cette PR"
            Write-Host "  [s] Skip (ignorer)"
            Write-Host "  [q] Quit (arreter)"

            $action = Read-Host "Votre choix"

            switch ($action.ToLower()) {
                "v" {
                    gh pr diff $number
                    Write-Host ""
                    Write-Host "Merger maintenant ? (y/n)"
                    $merge = Read-Host

                    if ($merge -eq "y") {
                        gh pr review $number --approve 2>&1 | Out-Null
                        gh pr merge $number --squash --delete-branch=false 2>&1 | Out-Null
                        Write-Host "PR #$number mergee"
                    }
                }
                "m" {
                    gh pr review $number --approve 2>&1 | Out-Null
                    gh pr merge $number --squash --delete-branch=false 2>&1 | Out-Null
                    Write-Host "PR #$number mergee"
                }
                "s" {
                    Write-Host "PR #$number ignoree"
                }
                "q" {
                    Write-Host "Arret du script"
                    break
                }
                default {
                    Write-Host "Action invalide, PR ignoree"
                }
            }
        }
    }
}

# 2. Sync votre branche avec master
Write-Host ""
Write-Host "Synchronisation avec master..."
git fetch origin 2>&1 | Out-Null

$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Branche actuelle: $currentBranch"

$mergeResult = git merge origin/master 2>&1

if ($LASTEXITCODE -eq 0) {
    if ($mergeResult -match "Already up to date") {
        Write-Host "Deja a jour avec master"
    } else {
        Write-Host "Branche synchronisee avec master"

        # Push
        git push origin $currentBranch 2>&1 | Out-Null
        Write-Host "Push sur $currentBranch"
    }
} else {
    Write-Host "Conflit detecte lors du merge avec master"
    Write-Host "Resoudre les conflits manuellement:"
    Write-Host "  1. Ouvrir les fichiers en conflit"
    Write-Host "  2. git add . && git commit"
    Write-Host "  3. git push origin $currentBranch"
}

Write-Host ""
Write-Host "========================================"
Write-Host "Morning Sync termine!"
Write-Host ""
Write-Host "Vous etes pret a travailler!"