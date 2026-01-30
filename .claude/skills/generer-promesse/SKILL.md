---
name: generer-promesse
description: Generate a promise of sale (promesse de vente) with automatic type detection. Use when user says "generer promesse", "promesse de vente", "nouvelle promesse", "promise deed".
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
---

# Generate Promise of Sale - Notomai v1.5.0

Generate a promesse de vente using the 3-category property system.

## Arguments
- `$ARGUMENTS` - Context, e.g., "standard Martin→Dupont 250000" or "avec mobilier" or "depuis titre.pdf"

## Available Property Categories

| Category | Template | Use Case |
|----------|----------|----------|
| copropriete | promesse_vente_lots_copropriete.md | Appartement, lots de copro |
| hors_copropriete | promesse_hors_copropriete.md | Maison, villa, local commercial |
| terrain_a_batir | promesse_terrain_a_batir.md | Terrain, lotissement |

## Workflow

### Step 1: Detect property category
Detection is 2-level:
- **Level 1**: Property category (copropriete, hors_copropriete, terrain_a_batir)
- **Level 2**: Transaction type (standard, premium, avec_mobilier, multi_biens)

If category is specified in `$ARGUMENTS`, use it.
Otherwise, use auto-detection:
```bash
python -c "
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses
import json, sys
gp = GestionnairePromesses()
data = json.load(open(sys.argv[1]))
result = gp.detecter_categorie(data)
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
python notaire.py promesse generer \
    --donnees <data_file.json> \
    --categorie <detected_category> \
    --output outputs/
```

Or use the full pipeline:
```bash
python execution/core/assembler_acte.py \
    --template promesse_<category>.md \
    --donnees <data_file.json> \
    --output .tmp/actes_generes/

python execution/core/exporter_docx.py \
    --input .tmp/actes_generes/<id>/acte.md \
    --output outputs/promesse_<category>_<date>.docx
```

### Step 5: Report
```
## Promesse Generated
- Category: <category> (confidence: XX%)
- Template: promesse_<category>.md
- Validation: PASS
- Output: outputs/promesse_<category>_<date>.docx
- Sections: XX fixed + XX variable
```

## Critical Rules
- Read `directives/creer_promesse_vente.md` before starting
- Read `directives/generation_promesses_avancee.md` for advanced features
- Use `schemas/promesse_catalogue_unifie.json` as reference
- If generating from title, always validate extracted data before proceeding
- Detection is 2-level: Level 1 = property category, Level 2 = transaction type (standard/premium/avec_mobilier/multi_biens)
- Templates follow naming convention: `promesse_<category>.md`
