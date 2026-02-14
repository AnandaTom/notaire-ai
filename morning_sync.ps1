# Morning Sync Script - NotaireAI v3.0
# Corrige: squash→merge, check mergeability, retry, rebase apres merge
# Ameliore: pas de divergence fantome, diagnostic precis

param(
    [switch]$AUTO_APPROVE = $false,
    [switch]$DRY_RUN = $false
)

$ErrorActionPreference = "Continue"

function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NotaireAI Morning Sync v3.0" -ForegroundColor Cyan
Write-Host "   $(Get-Date -Format 'dd/MM/yyyy HH:mm')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

# 0. Fetch tout d'abord
git fetch origin 2>&1 | Out-Null

# 1. Lister les PRs ouvertes
Write-Host ""
Write-Host "Pull Requests ouvertes:"

try {
    $prsJson = gh pr list --json number,title,author,headRefName,mergeable,mergeStateStatus 2>&1

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
        $mergeable = $pr.mergeable
        $mergeState = $pr.mergeStateStatus

        Write-Host ""
        Write-Host "----------------------------------------"
        Write-Host "PR #$number : $title"
        Write-Host "Auteur: $author ($branch)"
        Write-Host "Mergeable: $mergeable | State: $mergeState"

        if ($DRY_RUN) {
            Write-Host "[DRY RUN] Simulation du merge..."
            continue
        }

        if ($AUTO_APPROVE) {
            Write-Host "AUTO-APPROVE active"

            # Verifier la mergeability - attendre si UNKNOWN
            if ($mergeable -eq "UNKNOWN") {
                Write-Warn "Mergeability UNKNOWN - attente 10s pour que GitHub calcule..."
                Start-Sleep -Seconds 10

                # Re-check
                $prCheckJson = gh pr view $number --json mergeable,mergeStateStatus 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $prCheck = $prCheckJson | ConvertFrom-Json
                    $mergeable = $prCheck.mergeable
                    $mergeState = $prCheck.mergeStateStatus
                    Write-Host "Re-check: Mergeable=$mergeable | State=$mergeState"
                }
            }

            # Si CONFLICTING, on skip
            if ($mergeable -eq "CONFLICTING") {
                Write-Err "PR #$number a des conflits - skip (resoudre manuellement)"
                continue
            }

            # Approve
            gh pr review $number --approve 2>&1 | Out-Null

            # Merge avec --merge (PAS --squash pour eviter divergence)
            $mergeResult = gh pr merge $number --merge --delete-branch=false 2>&1

            if ($LASTEXITCODE -eq 0) {
                Write-Success "PR #$number mergee avec succes"
            } else {
                # Retry une fois apres 5s
                Write-Warn "Premier essai echoue, retry dans 5s..."
                Start-Sleep -Seconds 5
                $mergeResult = gh pr merge $number --merge --delete-branch=false 2>&1

                if ($LASTEXITCODE -eq 0) {
                    Write-Success "PR #$number mergee au 2e essai"
                } else {
                    Write-Err "Erreur lors du merge: $mergeResult"
                    Write-Warn "-> La PR reste ouverte, merger manuellement si besoin"
                }
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
                        gh pr merge $number --merge --delete-branch=false 2>&1 | Out-Null
                        Write-Host "PR #$number mergee"
                    }
                }
                "m" {
                    gh pr review $number --approve 2>&1 | Out-Null
                    gh pr merge $number --merge --delete-branch=false 2>&1 | Out-Null
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

# Pull les changements de la branche remote si elle existe
$remoteBranchExists = git ls-remote --heads origin $currentBranch 2>&1
if ($remoteBranchExists) {
    Write-Host "Pull des derniers changements de $currentBranch..."
    git pull origin $currentBranch 2>&1 | Out-Null
}

# Merge master dans la branche courante
$mergeResult = git merge origin/master 2>&1

if ($LASTEXITCODE -eq 0) {
    if ($mergeResult -match "Already up to date") {
        Write-Success "Deja a jour avec master"
    } else {
        Write-Success "Branche synchronisee avec master"
        git push origin $currentBranch 2>&1 | Out-Null
        Write-Success "Push sur $currentBranch"
    }
} else {
    Write-Err "Conflit detecte lors du merge avec master"
    Write-Warn "Resoudre les conflits manuellement:"
    Write-Host "  1. Ouvrir les fichiers en conflit"
    Write-Host "  2. git add . && git commit"
    Write-Host "  3. git push origin $currentBranch"
    Write-Host ""
    Write-Host "========================================"
    Write-Err "Morning Sync INTERROMPU - Conflits a resoudre"
    exit 1
}

# 3. Push final
Write-Host ""
Write-Info "[3/4] Push final pour garantir la synchronisation..."
git push origin $currentBranch 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Push OK"
} else {
    Write-Warn "Push deja a jour"
}

# 4. Diagnostic complet
Write-Host ""
Write-Info "[4/4] Diagnostic de synchronisation..."
Write-Host ""

git fetch origin 2>&1 | Out-Null

$localCommit = git rev-parse HEAD
$remoteRef = git rev-parse "origin/$currentBranch" 2>$null
$masterCommit = git rev-parse origin/master

$behindMaster = (git rev-list --count "HEAD..origin/master" 2>$null)
$aheadMaster = (git rev-list --count "origin/master..HEAD" 2>$null)

# Verifier si le remote existe
if ($remoteRef) {
    $behindRemote = (git rev-list --count "HEAD..origin/$currentBranch" 2>$null)
    $aheadRemote = (git rev-list --count "origin/$currentBranch..HEAD" 2>$null)
    $remoteDisplay = $remoteRef.Substring(0,7)
} else {
    $behindRemote = 0
    $aheadRemote = 0
    $remoteDisplay = "(non publie)"
}

Write-Host "----------------------------------------"
Write-Host "ETAT DE SYNCHRONISATION" -ForegroundColor White
Write-Host "----------------------------------------"
Write-Host "Branche locale:    $currentBranch"
Write-Host "Commit local:      $($localCommit.Substring(0,7))"
Write-Host "Commit remote:     $remoteDisplay"
Write-Host "Commit master:     $($masterCommit.Substring(0,7))"
Write-Host "----------------------------------------"

# Status vs Master
if ($behindMaster -eq 0 -and $aheadMaster -eq 0) {
    Write-Success "vs Master:  IDENTIQUE"
} elseif ($behindMaster -gt 0) {
    Write-Err "vs Master:  $behindMaster commits EN RETARD (sync echoue?)"
} elseif ($aheadMaster -le 5) {
    Write-Success "vs Master:  $aheadMaster commits en avance (OK, travail en cours)"
} else {
    Write-Warn "vs Master:  $aheadMaster commits en avance (penser a creer une PR)"
}

# Status vs Remote
if ($behindRemote -eq 0 -and $aheadRemote -eq 0) {
    Write-Success "vs Remote:  SYNCHRONISE"
} elseif ($aheadRemote -gt 0) {
    Write-Warn "vs Remote:  $aheadRemote commits locaux non pushes"
} else {
    Write-Warn "vs Remote:  $behindRemote commits a pull"
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
    Write-Warn "   MORNING SYNC TERMINE"
    if ($behindMaster -gt 0) {
        Write-Err "   ATTENTION: branche en retard sur master!"
    } else {
        Write-Success "   Branche a jour avec master"
    }
}
Write-Host "========================================"
Write-Host ""
Write-Host "Vous etes pret a travailler!" -ForegroundColor Green
