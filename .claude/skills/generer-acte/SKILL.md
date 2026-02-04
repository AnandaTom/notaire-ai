---
name: generer-acte
description: Generate a notarial deed (vente, promesse, reglement, modificatif, donation). Use when user says "generate deed", "generer acte", "creer acte", "nouvelle vente", "nouveau acte".
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Generate Notarial Deed - Notomai

Generate a complete notarial deed following the 3-layer architecture.

## Arguments
- `$ARGUMENTS` - The type and context, e.g., "vente Martin→Dupont 350000" or "promesse avec mobilier"

## Workflow

### Step 1: Identify deed type
Parse `$ARGUMENTS` to determine:
- **Type**: vente | promesse | reglement | modificatif | donation
- **Template**: Map to the correct template in `templates/`
- **Conformity**: Check current conformity level (must be >=80%)

Available templates and conformity:
| Type | Template | Conformity |
|------|----------|------------|
| vente | vente_lots_copropriete.md | 80.2% |
| promesse | promesse_vente_lots_copropriete.md | 88.9% |
| reglement | reglement_copropriete_edd.md | 85.5% |
| modificatif | modificatif_edd.md | 91.7% |

### Step 2: Check for data file
If the user provides a JSON data file path, use it directly.
Otherwise, ask the user what data source to use:
- Interactive collection (ask questions from `schemas/questions_*.json`)
- Generate minimal test data with `python execution/generation/generer_donnees_minimales.py`
- Use existing dossier from `.tmp/dossiers/`

### Step 3: Validate data
```bash
python execution/core/valider_acte.py \
    --donnees <data_file.json> \
    --schema schemas/variables_<type>.json
```
Report any validation errors. Do NOT proceed if there are ERREUR-level issues.

### Step 4: Assemble
```bash
python execution/core/assembler_acte.py \
    --template <template_name>.md \
    --donnees <data_file.json> \
    --output .tmp/actes_generes/
```

### Step 5: Export DOCX
```bash
python execution/core/exporter_docx.py \
    --input .tmp/actes_generes/<id>/acte.md \
    --output outputs/acte_<type>_<date>.docx
```

### Step 6: Report
```
## Generation Complete
- Type: <type>
- Template: <template> (XX% conformity)
- Validation: PASS (X warnings)
- Output: outputs/<filename>.docx
- Assembly time: Xs
- Export time: Xs
```

## Critical Rules
- ALWAYS read `directives/workflow_notaire.md` before starting
- NEVER modify templates or `exporter_docx.py` formatting
- Use `directives/creer_<type>.md` for type-specific rules
- Log any new clauses/situations for continuous learning
