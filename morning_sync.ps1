# Morning Sync Script - NotaireAI v2.0
# Review et merge les PRs, puis sync votre branche
# Ameliore: verification complete + diagnostic final

param(
    [switch]$AUTO_APPROVE = $false,
    [switch]$DRY_RUN = $false
)

$ErrorActionPreference = "Continue"

# Couleurs pour Windows
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NotaireAI Morning Sync v2.0" -ForegroundColor Cyan
Write-Host "   $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

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
Write-Info "[2/4] Synchronisation avec master..."
git fetch origin 2>&1 | Out-Null

$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Branche actuelle: $currentBranch"

# D'abord pull pour recuperer les derniers changements de votre branche
Write-Host "Pull des derniers changements de $currentBranch..."
git pull origin $currentBranch 2>&1 | Out-Null

$mergeResult = git merge origin/master 2>&1

if ($LASTEXITCODE -eq 0) {
    if ($mergeResult -match "Already up to date") {
        Write-Success "Deja a jour avec master"
    } else {
        Write-Success "Branche synchronisee avec master"

        # Push
        git push origin $currentBranch 2>&1 | Out-Null
        Write-Success "Push sur $currentBranch"
    }
} else {
    Write-Error "Conflit detecte lors du merge avec master"
    Write-Warning "Resoudre les conflits manuellement:"
    Write-Host "  1. Ouvrir les fichiers en conflit"
    Write-Host "  2. git add . && git commit"
    Write-Host "  3. git push origin $currentBranch"
    Write-Host ""
    Write-Host "========================================"
    Write-Error "Morning Sync INTERROMPU - Conflits a resoudre"
    exit 1
}

# 3. Verification finale - Push force pour s'assurer que tout est envoye
Write-Host ""
Write-Info "[3/4] Push final pour garantir la synchronisation..."
git push origin $currentBranch 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Push OK"
} else {
    Write-Warning "Push deja a jour ou erreur mineure"
}

# 4. Diagnostic complet
Write-Host ""
Write-Info "[4/4] Diagnostic de synchronisation..."
Write-Host ""

git fetch origin 2>&1 | Out-Null

$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse origin/$currentBranch 2>$null
$masterCommit = git rev-parse origin/master

$behindMaster = (git rev-list --count HEAD..origin/master 2>$null)
$aheadMaster = (git rev-list --count origin/master..HEAD 2>$null)
$behindRemote = (git rev-list --count HEAD..origin/$currentBranch 2>$null)
$aheadRemote = (git rev-list --count origin/$currentBranch..HEAD 2>$null)

Write-Host "----------------------------------------"
Write-Host "ETAT DE SYNCHRONISATION" -ForegroundColor White
Write-Host "----------------------------------------"
Write-Host "Branche locale:    $currentBranch"
Write-Host "Commit local:      $($localCommit.Substring(0,7))"
Write-Host "Commit remote:     $($remoteCommit.Substring(0,7))"
Write-Host "Commit master:     $($masterCommit.Substring(0,7))"
Write-Host "----------------------------------------"

# Status vs Master
if ($behindMaster -eq 0 -and $aheadMaster -eq 0) {
    Write-Success "vs Master:  IDENTIQUE (parfaitement synchronise)"
} elseif ($behindMaster -gt 0) {
    Write-Error "vs Master:  $behindMaster commits EN RETARD"
} else {
    Write-Warning "vs Master:  $aheadMaster commits en avance (PR a creer?)"
}

# Status vs Remote
if ($behindRemote -eq 0 -and $aheadRemote -eq 0) {
    Write-Success "vs Remote:  SYNCHRONISE"
} elseif ($aheadRemote -gt 0) {
    Write-Warning "vs Remote:  $aheadRemote commits locaux non pushes"
} else {
    Write-Warning "vs Remote:  $behindRemote commits a pull"
}

Write-Host "----------------------------------------"
Write-Host ""

# Resume final
$allGood = ($behindMaster -eq 0) -and ($behindRemote -eq 0) -and ($aheadRemote -eq 0)

Write-Host "========================================"
if ($allGood) {
    Write-Success "   MORNING SYNC REUSSI"
    Write-Success "   Tout est synchronise!"
} else {
    Write-Warning "   MORNING SYNC TERMINE"
    Write-Warning "   Verifiez les warnings ci-dessus"
}
Write-Host "========================================"
Write-Host ""
Write-Host "Vous etes pret a travailler!" -ForegroundColor Green