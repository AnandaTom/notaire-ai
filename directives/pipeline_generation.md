# Directive : Pipeline de Génération Rapide

## Objectif

Générer un acte notarial DOCX/PDF fidèle à la trame originale en **3 étapes simples**.

---

## Pipeline en 3 étapes

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  1. DONNÉES     │───▶│  2. ASSEMBLAGE   │───▶│  3. EXPORT      │
│  (JSON)         │    │  (Markdown)      │    │  (DOCX/PDF)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## Étape 1 : Préparer les données

Créer un fichier JSON avec les informations du client. Voir `schemas/variables_vente.json` pour la structure complète.

**Exemple minimal** (`.tmp/donnees_client.json`):
```json
{
  "acte": {
    "date": {"jour": 15, "mois": 3, "annee": 2025},
    "reference": "2025/001"
  },
  "vendeurs": [...],
  "acquereurs": [...],
  "bien": {...},
  "prix": {"montant": 285000}
}
```

---

## Étape 2 : Assembler l'acte

```bash
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_client.json \
    --output .tmp/actes_generes/
```

**Résultat**: `acte.md` + `donnees.json` + `metadata.json`

---

## Étape 3 : Exporter

### Export DOCX (recommandé)
```bash
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/acte_client.docx
```

### Export PDF
```bash
python execution/exporter_pdf.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/acte_client.pdf
```

---

## Commande tout-en-un (exemple)

```bash
# 1. Assembler
python execution/assembler_acte.py \
    -t vente_lots_copropriete.md \
    -d .tmp/donnees_client_test.json \
    -o .tmp/actes_generes/ \
    --id vente_001

# 2. Exporter DOCX
python execution/exporter_docx.py \
    -i .tmp/actes_generes/vente_001/acte.md \
    -o outputs/acte_vente_client.docx

# 3. (Optionnel) Exporter PDF
python execution/exporter_pdf.py \
    -i .tmp/actes_generes/vente_001/acte.md \
    -o outputs/acte_vente_client.pdf
```

---

## Garanties de qualité

Le pipeline garantit automatiquement:

| Aspect | Détail |
|--------|--------|
| **Police** | Times New Roman 11pt partout |
| **Marges** | G=60mm, D=15mm, H/B=25mm |
| **Retrait** | 12.51mm première ligne |
| **Titres** | Styles H1-H4 conformes |
| **Tableaux** | Détection auto de 20+ types |
| **Montants** | Conversion en lettres auto |
| **Dates** | Conversion en lettres auto |

---

## Dépannage rapide

### Erreur "Template non trouvé"
```bash
# Vérifier le dossier templates
ls templates/
# S'assurer que le nom est exact
python execution/assembler_acte.py -t vente_lots_copropriete.md ...
```

### Erreur "Variable manquante"
```bash
# Valider les données d'abord
python execution/valider_acte.py \
    --donnees .tmp/donnees_client.json \
    --schema schemas/variables_vente.json
```

### Formatage incorrect dans le DOCX
- Vérifier que le Markdown source utilise la bonne syntaxe
- Tableaux: `| Col1 | Col2 |` avec ligne de séparation `|---|---|`
- Soulignement: `__texte__` (pas de balises `<u>`)
- **NE JAMAIS modifier** les valeurs dans `exporter_docx.py`

---

## Performance

| Opération | Temps typique |
|-----------|---------------|
| Assemblage | < 1s |
| Export DOCX | < 2s |
| Export PDF | 2-5s |
| **Total** | **< 8s** |

---

## Mises à jour

| Date | Modification |
|------|--------------|
| 2025-01-19 | Création - Pipeline optimisé pour génération rapide et fiable |

---

## Voir aussi

- [directives/creer_acte.md](creer_acte.md) - Flux complet avec collecte de données
- [directives/formatage_docx.md](formatage_docx.md) - Spécifications techniques détaillées
