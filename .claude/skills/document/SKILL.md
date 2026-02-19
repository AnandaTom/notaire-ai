---
name: document
description: MANDATORY after /review passes clean. Syncs script docstrings, directives, CLAUDE.md, and memory/ files with current code reality. Covers ALL changed files (Python, TypeScript, React, templates). Auto-invoke after any code modification once review is done — do not wait for user to ask.
argument-hint: "[file-path (optional)]"
---

You are being asked to update documentation to match recent code changes.

## Instructions

1. **Identify what changed.** If the user passed `$ARGUMENTS`, document those files. Otherwise, check git for uncommitted changes:
   ```bash
   git diff --name-only
   git diff --cached --name-only
   ```
   Cover ALL file types — not just Python:
   - `.py` in `execution/` → docstrings + directives + CLAUDE.md scripts table
   - `.ts/.tsx` in `frontend/` → component props, store shape, accessibility annotations
   - `templates/*.md` → Jinja2 conditions, sections, variables still accurate?
   - `schemas/*.json` → schema version bumped? CLAUDE.md schemas table updated?
   - `memory/*.md` → always update JOURNAL.md + ISSUES.md (see Step 5)

2. **Read every changed file completely.** Understand what the code does now.

3. **Read the project memory files** to understand team context:
   - `memory/JOURNAL.md` — recent session logs
   - `memory/CODE_MAP.md` — file/endpoint map
   - `memory/ISSUES.md` — open issues tracker

4. **Spawn the documenter subagent** using the Task tool:
   ```
   subagent_type: "general-purpose"
   ```
   Pass it:
   - The full content of ALL changed files (Python AND TypeScript/React)
   - The language/framework context for each file
   - The content of the relevant directive(s) from `directives/`
   - The relevant sections of `CLAUDE.md` (scripts tables, agents tables, skills tables)
   - The current `memory/CODE_MAP.md`, `memory/ISSUES.md`, and `memory/JOURNAL.md`
   - Clear instruction: "Follow the documenter agent prompt at ~/.claude/agents/documenter.md. Perform all passes including the frontend pass. Return what needs updating."

5. **Act on findings:**
   - **Script docstring fixes** → apply them directly (Edit tool)
   - **Directive updates** → apply them directly (Edit tool)
   - **CLAUDE.md updates** → apply them directly (Edit tool)
   - **memory/ updates** → apply them directly (Edit tool)
   - **No changes needed** → report clean

6. **memory/ — TOUJOURS mettre à jour, sans exception :**
   - `memory/JOURNAL.md` → OBLIGATOIRE. Ajouter une entrée pour CHAQUE session avec des modifications de code. Pas de condition "if significant". Tout commit = une entrée journal.
   - `memory/ISSUES.md` → Si une issue a été fixée dans cette session : la fermer avec le commit hash. Si un nouveau problème a été trouvé : l'ajouter.
   - `memory/CODE_MAP.md` → Si des fichiers ont été ajoutés/supprimés ou si les LOC ont changé significativement : mettre à jour.

7. **Report to the user** with a short summary:
   - What was checked
   - What was updated (files + what changed)
   - What was already in sync

## Key Behavior

- Do NOT ask the user what to document — detect changes from git and act
- Do NOT skip the subagent — fresh eyes catch stale docs that the author misses
- Do NOT add documentation that isn't needed — only fix gaps between code and docs
- Do NOT limit scope to Python — frontend changes need documentation too
- ALWAYS run AFTER `/review` — never before, never instead of

## JOURNAL.md — Format obligatoire (anti-conflit multi-devs)

Quand tu ecris dans `memory/JOURNAL.md`, utilise **TOUJOURS** ce format d'entete :

```markdown
## YYYY-MM-DD — Prenom (Pseudo)
```

Exemples :
- `## 2026-02-18 — Tom`
- `## 2026-02-18 (soir) — Paul (Payoss)`
- `## 2026-02-19 — Augustin`

**Regles :**
- Le nom du dev DOIT apparaitre apres le tiret long `—` (pas `-`, pas `–`)
- Detecter le dev depuis la branche git (`tom/dev` → Tom, `payoss/dev` → Paul/Payoss)
- Si plusieurs sessions le meme jour, ajouter `(matin)`, `(soir)`, `(nuit)` entre la date et le tiret
- Ne JAMAIS ecraser l'entree d'un autre dev — toujours AJOUTER en dessous
- Les nouvelles entrees vont AVANT le bloc `## Template entree journal` en fin de fichier
- `generate_commit_msg.py` filtre par dev pour construire le commit message — le format doit etre respecte
