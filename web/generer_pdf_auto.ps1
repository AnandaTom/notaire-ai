# Script PowerShell pour générer automatiquement un PDF du formulaire
# Utilise Chrome/Edge en mode headless

param(
    [switch]$Exemple,
    [string]$Output = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NotaireAI - Generation PDF Automatique" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Chemins
$webDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$htmlFile = Join-Path $webDir "print_version.html"
$htmlUri = "file:///$($htmlFile.Replace('\', '/'))"

# Chemin de sortie
if ($Output -eq "") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $suffix = if ($Exemple) { "_exemple" } else { "" }
    $Output = Join-Path (Split-Path -Parent $webDir) "outputs\formulaire_vendeur$suffix`_$timestamp.pdf"
}

# Créer le dossier de sortie
$outputDir = Split-Path -Parent $Output
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Source  : $htmlFile" -ForegroundColor Gray
Write-Host "Sortie  : $Output" -ForegroundColor Gray
Write-Host ""

# Chercher Chrome ou Edge
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe",
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
)

$chromePath = $null
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        $browserName = if ($path -match "Edge") { "Edge" } else { "Chrome" }
        break
    }
}

if ($chromePath -eq $null) {
    Write-Host "Erreur: Chrome ou Edge non trouve" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions alternatives:" -ForegroundColor Yellow
    Write-Host "  1. Installer Chrome: https://www.google.com/chrome/" -ForegroundColor Gray
    Write-Host "  2. Utiliser generer_pdf.bat (impression manuelle)" -ForegroundColor Gray
    Write-Host "  3. Installer Playwright: pip install playwright && playwright install chromium" -ForegroundColor Gray
    exit 1
}

Write-Host "Navigateur: $browserName" -ForegroundColor Green

# Préparer la commande
$chromeArgs = @(
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--print-to-pdf=`"$Output`"",
    "--no-margins",
    "$htmlUri"
)

Write-Host "Generation du PDF..." -ForegroundColor Yellow

# Exécuter Chrome/Edge en mode headless
try {
    $process = Start-Process -FilePath $chromePath -ArgumentList $chromeArgs -Wait -PassThru -NoNewWindow

    if ($process.ExitCode -eq 0 -and (Test-Path $Output)) {
        $fileSize = (Get-Item $Output).Length / 1KB
        Write-Host ""
        Write-Host "PDF genere avec succes!" -ForegroundColor Green
        Write-Host "  Taille: $([math]::Round($fileSize, 1)) Ko" -ForegroundColor Gray
        Write-Host "  Fichier: $Output" -ForegroundColor Cyan
        Write-Host ""

        # Ouvrir le PDF
        $response = Read-Host "Ouvrir le PDF? (O/N)"
        if ($response -eq "O" -or $response -eq "o") {
            Start-Process $Output
        }
    } else {
        Write-Host ""
        Write-Host "Erreur lors de la generation du PDF" -ForegroundColor Red
        Write-Host "Code de sortie: $($process.ExitCode)" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Erreur: $_" -ForegroundColor Red
    exit 1
}
