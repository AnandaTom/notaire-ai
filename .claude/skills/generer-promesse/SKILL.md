---
name: generer-promesse
description: Generate a promise of sale (promesse de vente) with automatic type detection. Use when user says "generer promesse", "promesse de vente", "nouvelle promesse", "promise deed".
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Generate Promise of Sale - Notomai v1.4.0

Generate a promesse de vente using the advanced multi-template system.

## Arguments
- `$ARGUMENTS` - Context, e.g., "standard Martin→Dupont 250000" or "avec mobilier" or "depuis titre.pdf"

## Available Promise Types

| Type | Template | Use Case |
|------|----------|----------|
| standard | promesse_standard.md | 1 bien simple, pas de mobilier |
| premium | promesse_premium.md | Diagnostics exhaustifs, agences |
| avec_mobilier | promesse_avec_mobilier.md | Vente meublee |
| multi_biens | promesse_multi_biens.md | Lot + parking + cave |

## Workflow

### Step 1: Detect promise type
If type is specified in `$ARGUMENTS`, use it.
Otherwise, use auto-detection:
```bash
python -c "
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses
import json, sys
gp = GestionnairePromesses()
data = json.load(open(sys.argv[1]))
result = gp.detecter_type(data)
print(json.dumps(result, indent=2, ensure_ascii=False))
" <data_file.json>
```

### Step 2: From title (if --titre provided)
If generating from a property title:
```bash
python notaire.py extraire <titre.pdf> -o .tmp/titre_extrait.json
```
Then convert title data to promise data using the gestionnaire.

### Step 3: Validate
```bash
python execution/core/valider_acte.py \
    --donnees <data_file.json> \
    --schema schemas/variables_promesse_vente.json
```

### Step 4: Generate
```bash
python notaire.py promesse-avancee generer \
    --donnees <data_file.json> \
    --type <detected_type> \
    --output outputs/
```

Or use the full pipeline:
```bash
python execution/core/assembler_acte.py \
    --template promesse/<type_template>.md \
    --donnees <data_file.json> \
    --output .tmp/actes_generes/

python execution/core/exporter_docx.py \
    --input .tmp/actes_generes/<id>/acte.md \
    --output outputs/promesse_<type>_<date>.docx
```

### Step 5: Report
```
## Promesse Generated
- Type: <type> (confidence: XX%)
- Template: promesse/<template>.md
- Validation: PASS
- Output: outputs/promesse_<type>_<date>.docx
- Sections: XX fixed + XX variable
```

## Critical Rules
- Read `directives/creer_promesse_vente.md` before starting
- Read `directives/generation_promesses_avancee.md` for advanced features
- Use `schemas/promesse_catalogue_unifie.json` as reference
- If generating from title, always validate extracted data before proceeding
