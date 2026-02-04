---
name: status
description: Show full project status - templates, tests, deployment, database. Use when user says "status", "etat", "dashboard", "project status", "ou en est-on".
disable-model-invocation: false
allowed-tools: Bash, Read, Grep, Glob
---

# Project Status - Notomai

Display a comprehensive status dashboard of the Notomai project.

## Workflow

### Step 1: Git status
```bash
git status --short
git log --oneline -5
git branch --show-current
```

### Step 2: Template conformity
Check each template exists and report conformity from CLAUDE.md:
```bash
# Check templates exist
ls -la templates/vente_lots_copropriete.md templates/promesse_vente_lots_copropriete.md templates/reglement_copropriete_edd.md templates/modificatif_edd.md 2>&1

# Count template sizes
wc -l templates/*.md
```

### Step 3: Test health
```bash
python -m pytest tests/ --co -q 2>&1 | tail -5
```
Report number of collected tests.

### Step 4: Schema stats
```bash
# Count questions per schema
python -c "
import json, glob
for f in sorted(glob.glob('schemas/questions_*.json')):
    data = json.load(open(f, encoding='utf-8'))
    sections = data.get('sections', [])
    total_q = sum(len(s.get('questions', [])) for s in sections)
    print(f'  {f.split(chr(92))[-1].split(\"/\")[-1]}: {len(sections)} sections, {total_q} questions')
"

# Count clauses
python -c "
import json
data = json.load(open('schemas/clauses_catalogue.json', encoding='utf-8'))
cats = data.get('categories', data.get('clauses', []))
print(f'  Clauses: {len(cats)} categories')
"
```

### Step 5: Dependencies check
```bash
python -c "
import jinja2, docx, markdown, supabase, dotenv, rich
print('Core deps: OK')
print(f'  jinja2: {jinja2.__version__}')
print(f'  python-docx: {docx.__version__}')
" 2>&1
```

### Step 6: Report
```
## Notomai Status Dashboard

### Git
- Branch: <current>
- Status: clean/dirty (X files changed)
- Last commit: <hash> <message>

### Templates (v1.4.0)
| Template | Conformity | Status |
|----------|-----------|--------|
| Vente | 80.2% | PROD |
| Promesse | 88.9% | PROD |
| Reglement | 85.5% | PROD |
| Modificatif | 91.7% | PROD |

### Tests
- Collected: XX tests
- Last run: <status if available>

### Schemas
- Questions: XX sections, YY questions
- Clauses: XX categories
- Annexes: XX types

### Dependencies
- Python core: OK/MISSING
- Modal CLI: available/missing

### Team (3 devs)
- Recent activity from git log
```
