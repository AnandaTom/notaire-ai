---
name: sprint-plan
description: Plan a development sprint by analyzing open issues, PRs, and current state. Use when user says "sprint plan", "planning", "what should we work on", "prochaines taches", "next sprint".
disable-model-invocation: false
allowed-tools: Bash, Read, Grep, Glob
---

# Sprint Planning - Notomai

Analyze the current project state and propose a prioritized sprint plan for the 3-dev team.

## Arguments
- `$ARGUMENTS` - Optional focus area: "templates", "api", "tests", "frontend", "security", or empty for full analysis

## Workflow

### Step 1: Current state assessment
```bash
# Open issues and PRs
gh issue list --limit 20 2>&1
gh pr list --limit 10 2>&1

# Recent activity
git log --oneline --all --since="2 weeks ago" --format="%h %s (%an)" 2>&1
```

### Step 2: Identify gaps
Analyze based on focus area or full project:

**Templates**: Check conformity gaps, missing sections
```bash
grep -r "TODO\|FIXME\|HACK\|XXX" templates/ 2>&1 | head -20
```

**Tests**: Check coverage gaps
```bash
python -m pytest tests/ --co -q 2>&1
# Compare test files vs source files
ls execution/core/*.py | wc -l
ls tests/test_*.py | wc -l
```

**API**: Check endpoint coverage
```bash
grep -n "@app\.\(get\|post\|put\|delete\)" api/main.py 2>&1 | head -20
```

**Frontend**: Check component status
```bash
ls frontend/components/*.tsx frontend/app/**/*.tsx 2>&1 | head -20
```

**Security**: Check advisories
```bash
grep -r "TODO.*secur\|FIXME.*secur\|password\|secret" execution/ --include="*.py" -l 2>&1
```

### Step 3: Read roadmap and docs
```
Read these files for context:
- ROADMAP_AGENT_V1.md (if exists)
- docs/RECOMMANDATIONS_STRATEGIQUES.md (if exists)
- directives/etat_des_lieux.md (if exists)
```

### Step 4: Propose sprint plan
```
## Sprint Plan - <date>

### Team Allocation (3 devs)

**Dev 1 (Tom):** <focus area>
- [ ] Task 1 - <description> [Priority: HIGH]
- [ ] Task 2 - <description> [Priority: MEDIUM]

**Dev 2 (Augustin):** <focus area>
- [ ] Task 1 - <description> [Priority: HIGH]
- [ ] Task 2 - <description> [Priority: MEDIUM]

**Dev 3 (Paul):** <focus area>
- [ ] Task 1 - <description> [Priority: HIGH]
- [ ] Task 2 - <description> [Priority: MEDIUM]

### Sprint Goals
1. <measurable goal>
2. <measurable goal>

### Risks & Dependencies
- <risk or blocker>

### Definition of Done
- All tests pass
- Template conformity >= current levels
- No security warnings
- PR reviewed by at least 1 other dev
```

## Context
The 3 developers are:
- Tom (tom/dev branch) - likely lead/architect
- Augustin - frontend/formulaires/dashboard (from commit history)
- Paul - workflows/diagnostics (from commit history)

Use recent git activity to infer current focus areas and avoid conflicts.
