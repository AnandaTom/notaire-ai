#!/bin/bash
# Script de validation rapide - Vérif avant commit
# Usage: ./execution/valider_rapide.sh [vente|promesse]

set -e

TYPE=${1:-vente}
VERBOSE=${2:-}

echo "🔍 Validation Rapide - Template $TYPE"
echo "========================================"

# 1. Test assemblage (données minimales)
echo ""
echo "1️⃣  Test assemblage données minimales..."
python execution/assembler_acte.py \
  --template ${TYPE}_lots_copropriete.md \
  --donnees exemples/donnees_${TYPE}_exemple.json \
  --output .tmp/valid_test_min/ \
  --zones-grisees > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "   ✅ Assemblage données minimales OK"
else
  echo "   ❌ ERREUR assemblage données minimales"
  exit 1
fi

# 2. Test assemblage (données maximales)
echo ""
echo "2️⃣  Test assemblage données enrichies..."
if [ -f ".tmp/donnees_test_vague5_enrichi.json" ]; then
  python execution/assembler_acte.py \
    --template ${TYPE}_lots_copropriete.md \
    --donnees .tmp/donnees_test_vague5_enrichi.json \
    --output .tmp/valid_test_max/ \
    --zones-grisees > /dev/null 2>&1

  if [ $? -eq 0 ]; then
    echo "   ✅ Assemblage données enrichies OK"
  else
    echo "   ❌ ERREUR assemblage données enrichies"
    exit 1
  fi
else
  echo "   ⏭️  Données enrichies non disponibles (skip)"
fi

# 3. Vérifier zones grisées
echo ""
echo "3️⃣  Vérification zones grisées..."
ACTE_PATH=$(find .tmp/valid_test_min -name "acte.md" | head -1)
if [ -f "$ACTE_PATH" ]; then
  COUNT=$(grep -c "<<<VAR_START>>>" "$ACTE_PATH" || echo "0")
  if [ "$COUNT" -gt 0 ]; then
    echo "   ✅ Zones grisées présentes ($COUNT marqueurs)"
  else
    echo "   ⚠️  Aucune zone grisée détectée"
  fi
fi

# 4. Test export DOCX
echo ""
echo "4️⃣  Test export DOCX..."
python execution/exporter_docx.py \
  --input "$ACTE_PATH" \
  --output .tmp/valid_test.docx \
  --zones-grisees > /dev/null 2>&1

if [ $? -eq 0 ]; then
  echo "   ✅ Export DOCX OK"
else
  echo "   ❌ ERREUR export DOCX"
  exit 1
fi

echo ""
echo "========================================"
echo "✅ VALIDATION COMPLÈTE - Template $TYPE prêt"
echo ""
echo "💡 Pour tester conformité:"
echo "   python execution/comparer_documents_v2.py \\"
echo "     --original \"docs_original/Trame ${TYPE} lots de copropriété.docx\" \\"
echo "     --genere .tmp/valid_test.docx"
