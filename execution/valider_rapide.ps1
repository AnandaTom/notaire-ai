# Script de validation rapide - Windows PowerShell
# Usage: .\execution\valider_rapide.ps1 [vente|promesse]

param(
    [string]$Type = "vente"
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validation Rapide - Template $Type" -ForegroundColor Cyan
Write-Host "========================================"

# 1. Test assemblage données minimales
Write-Host ""
Write-Host "1️⃣  Test assemblage données minimales..." -ForegroundColor Yellow
try {
    python execution/assembler_acte.py `
        --template "${Type}_lots_copropriete.md" `
        --donnees "exemples/donnees_${Type}_exemple.json" `
        --output ".tmp/valid_test_min/" `
        --zones-grisees 2>&1 | Out-Null
    Write-Host "   ✅ Assemblage données minimales OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ ERREUR assemblage données minimales" -ForegroundColor Red
    exit 1
}

# 2. Test assemblage données enrichies
Write-Host ""
Write-Host "2️⃣  Test assemblage données enrichies..." -ForegroundColor Yellow
if (Test-Path ".tmp/donnees_test_vague5_enrichi.json") {
    try {
        python execution/assembler_acte.py `
            --template "${Type}_lots_copropriete.md" `
            --donnees ".tmp/donnees_test_vague5_enrichi.json" `
            --output ".tmp/valid_test_max/" `
            --zones-grisees 2>&1 | Out-Null
        Write-Host "   ✅ Assemblage données enrichies OK" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ ERREUR assemblage données enrichies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   ⏭️  Données enrichies non disponibles (skip)" -ForegroundColor Gray
}

# 3. Vérifier zones grisées
Write-Host ""
Write-Host "3️⃣  Vérification zones grisées..." -ForegroundColor Yellow
$ActePath = Get-ChildItem -Path ".tmp/valid_test_min" -Filter "acte.md" -Recurse | Select-Object -First 1
if ($ActePath) {
    $Content = Get-Content $ActePath.FullName -Raw
    $Count = ([regex]::Matches($Content, "<<<VAR_START>>>")).Count
    if ($Count -gt 0) {
        Write-Host "   ✅ Zones grisées présentes ($Count marqueurs)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Aucune zone grisée détectée" -ForegroundColor Yellow
    }
}

# 4. Test export DOCX
Write-Host ""
Write-Host "4️⃣  Test export DOCX..." -ForegroundColor Yellow
try {
    python execution/exporter_docx.py `
        --input $ActePath.FullName `
        --output ".tmp/valid_test.docx" `
        --zones-grisees 2>&1 | Out-Null
    Write-Host "   ✅ Export DOCX OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ ERREUR export DOCX" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "✅ VALIDATION COMPLÈTE - Template $Type prêt" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Pour tester conformité:" -ForegroundColor Cyan
Write-Host "   python execution/comparer_documents_v2.py \"
Write-Host "     --original `"docs_originels/Trame $Type lots de copropriété.docx`" \"
Write-Host "     --genere .tmp/valid_test.docx"
