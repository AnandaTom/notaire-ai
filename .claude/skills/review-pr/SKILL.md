---
name: review-pr
description: Review a pull request with Notomai-specific conventions. Use when user says "review PR", "review pull request", "code review", "revue de code", "check PR".
disable-model-invocation: false
allowed-tools: Bash, Read, Grep, Glob
---

# Code Review - Notomai

Review a pull request against Notomai project conventions and architecture.

## Arguments
- `$ARGUMENTS` - PR number (e.g., "42") or branch name

## Workflow

### Step 1: Get PR details
```bash
# If PR number provided
gh pr view $0 --json title,body,files,additions,deletions,baseRefName

# If branch name, compare against master
git diff master...$0 --stat
```

### Step 2: Review changed files
For each changed file, check against Notomai conventions:

**Architecture (3-Layer)**
- [ ] Directives (`directives/`) contain only Markdown SOPs
- [ ] Execution scripts (`execution/`) contain only deterministic Python
- [ ] No business logic in templates (templates should use Jinja2 only)

**Templates (`templates/`)**
- [ ] All variables wrapped in `{% if var %}` guards
- [ ] No hardcoded values (must use `{{ variable }}`)
- [ ] New sections added at END of `partie_developpee.md`, not inline
- [ ] Uses patterns from `directives/bonnes_pratiques_templates.md`

**Schemas (`schemas/`)**
- [ ] New variables have corresponding questions in `questions_*.json`
- [ ] JSON is valid and follows existing structure
- [ ] Catalogs (clauses, annexes) include required fields: id, nom, type_acte, texte

**Execution scripts (`execution/`)**
- [ ] UTF-8 encoding handled (Windows compatibility)
- [ ] Deep copy used for nested data mutations
- [ ] No modifications to `exporter_docx.py` formatting constants
- [ ] Error messages are clear and actionable

**Security**
- [ ] No secrets, tokens, or credentials in code
- [ ] PII handling follows RGPD (uses encryption_service.py)
- [ ] No `.env` files committed
- [ ] Supabase RLS policies respected

**Tests**
- [ ] New functionality has corresponding tests in `tests/`
- [ ] Tests use fixtures from `tests/conftest.py`
- [ ] No test data contains real client information

### Step 3: Check for regressions
```bash
# Quick test run on affected modules
python -m pytest tests/ -x -q 2>&1
```

### Step 4: Report
```
## PR Review: <title>

### Summary
<1-2 sentence description of what this PR does>

### Checklist
- [x] Architecture compliance
- [x] Template conventions
- [ ] Missing test coverage (details below)
- [x] Security check

### Issues
1. **[BLOCKING]** <description> - `file:line`
2. **[WARNING]** <description> - `file:line`
3. **[SUGGESTION]** <description> - `file:line`

### Verdict: APPROVE / REQUEST CHANGES / NEEDS DISCUSSION
<reasoning>
```

## Notomai-Specific Rules
- `docs_original/` MUST NEVER be modified
- `exporter_docx.py` formatting values are sacred (Times New Roman 11pt, margins G=60mm D=15mm)
- Template conformity must stay >= current levels (80-91%)
- Every new variable needs a question in `questions_*.json`
- Reference `directives/lecons_apprises.md` for known pitfalls
