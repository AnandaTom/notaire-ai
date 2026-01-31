---
name: valider-template
description: Audit template conformity against original trames. Use when user says "valider template", "audit template", "check conformity", "verifier conformite", "comparer template".
disable-model-invocation: false
allowed-tools: Bash, Read, Grep, Glob
---

# Validate Template Conformity - Notomai

Audit a Jinja2 template's structural conformity against the original notarial trames.

## Arguments
- `$ARGUMENTS` - Template name or type: "vente", "promesse", "reglement", "modificatif", or a file path

## Template Mapping

| Argument | Template File | Target Conformity |
|----------|--------------|-------------------|
| vente | templates/vente_lots_copropriete.md | >=80% |
| promesse | templates/promesse_vente_lots_copropriete.md | >=88% |
| reglement | templates/reglement_copropriete_edd.md | >=85% |
| modificatif | templates/modificatif_edd.md | >=91% |
| all | All 4 templates | Per-template targets |

## Workflow

### Step 1: Identify template(s)
Parse `$ARGUMENTS` to determine which template(s) to audit.
If "all", audit all 4 main templates.

### Step 2: Structural analysis
For each template, analyze:

1. **Section count**: Count `## ` and `### ` headings
2. **Jinja2 blocks**: Count `{% if %}`, `{% for %}`, `{% include %}`
3. **Variables**: Extract all `{{ variable }}` references
4. **Bookmark coverage**: Compare variables against schema definitions

```bash
# Count sections
grep -c "^##" templates/<template>.md

# Count Jinja2 conditionals
grep -c "{% if" templates/<template>.md

# Extract all variables used
grep -oP '\{\{[^}]+\}\}' templates/<template>.md | sort -u | wc -l

# Compare with schema
python -c "
import json
schema = json.load(open('schemas/variables_<type>.json'))
# Count expected variables
def count_vars(obj, prefix=''):
    count = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, dict):
                count += count_vars(v, f'{prefix}{k}.')
            else:
                count += 1
    return count
print(f'Schema variables: {count_vars(schema)}')
"
```

### Step 3: Compare with original
```bash
python execution/analyse/comparer_documents.py \
    --template templates/<template>.md \
    --original docs_original/<trame>.docx 2>&1
```

### Step 4: Check for common issues
- Missing `{% if %}` guards (causes KeyError in production)
- Variables referenced but not in schema
- Sections without conditional guards
- Nested objects accessed without null checks

Read `directives/lecons_apprises.md` for the 15 known production issues.

### Step 5: Report
```
## Template Audit: <template_name>

### Conformity Score: XX%
- Target: XX% | Status: PASS/FAIL

### Structure
- Sections: XX headings
- Conditionals: XX {% if %} blocks
- Variables: XX unique references
- Schema coverage: XX/YY variables mapped

### Issues Found
1. [CRITICAL] <description> at line XX
2. [WARNING] <description> at line XX
3. [INFO] <description> at line XX

### Recommendations
- <specific action to improve conformity>
```

## Critical Rules
- NEVER modify templates during audit - only report
- Always compare against `docs_original/` as ground truth
- Reference `directives/bonnes_pratiques_templates.md` for Jinja2 patterns
- Report line numbers for every issue found
