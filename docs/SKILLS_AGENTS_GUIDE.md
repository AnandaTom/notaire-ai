# Skills & Agents - Guide Claude Code pour Notomai

> Guide complet des skills (commandes `/slash`) et agents (sous-agents) disponibles pour l'equipe.
> **Version**: 1.0.0 | **Date**: 2026-01-29

---

## Vue d'ensemble

```
.claude/
  skills/               8 commandes /slash invocables
  agents/               3 sous-agents specialises
  commands/             1 commande legacy
  settings.json         Hooks partages (protection docs_original/)
```

### Comment ca marche

| Type | Invocation | Contexte | Quand |
|------|-----------|----------|-------|
| **Skill** (`/nom`) | Manuelle ou auto | Inline (conversation) | Workflows repetables |
| **Agent** | Automatique (Claude decide) | Isole (session separee) | Taches complexes d'audit |
| **Hook** | Automatique (evenement) | Systeme | Protection, validation |

---

## Skills - Commandes /slash

### Workflows de generation (invocation manuelle uniquement)

Ces skills ont des **effets de bord** (creation de fichiers) et ne s'activent qu'a votre demande.

#### `/generer-acte`
**Usage**: `/generer-acte <type> [description]`

Genere un acte notarial complet via le pipeline: validation -> assemblage Jinja2 -> export DOCX.

```
/generer-acte vente
/generer-acte promesse avec mobilier pour Martin→Dupont 350000
/generer-acte reglement_copropriete
/generer-acte modificatif_edd
```

**Etapes executees**:
1. Detection du type d'acte
2. Chargement des donnees (exemple ou fournies)
3. Validation avec `valider_acte.py`
4. Assemblage Jinja2 avec `assembler_acte.py`
5. Export DOCX avec `exporter_docx.py`
6. Verification conformite

---

#### `/generer-promesse`
**Usage**: `/generer-promesse <type> [options]`

Workflow specialise pour les promesses de vente avec detection automatique du sous-type.

```
/generer-promesse standard
/generer-promesse avec_mobilier
/generer-promesse depuis-titre titre.pdf beneficiaires.json 350000
```

**Types supportes**: standard, premium, avec_mobilier, multi_biens

---

#### `/deploy-modal`
**Usage**: `/deploy-modal <env>`

Deploie sur Modal (serverless) apres validation.

```
/deploy-modal prod    # Tests -> Deploy production
/deploy-modal test    # Tests -> Deploy staging
```

---

#### `/test-pipeline`
**Usage**: `/test-pipeline [scope]`

Execute la suite de tests complete.

```
/test-pipeline              # Tous les tests
/test-pipeline security     # Tests securite uniquement
/test-pipeline templates    # Conformite templates
/test-pipeline quick        # pytest uniquement, rapide
```

---

### Workflows d'analyse (auto-invocation possible)

Ces skills sont **lecture seule** et Claude peut les utiliser automatiquement quand le contexte est pertinent.

#### `/valider-template`
**Usage**: `/valider-template [template|all]`

Audit de conformite des templates Jinja2 vs trames originales.

```
/valider-template all                          # Tous les templates
/valider-template vente                        # Template vente
/valider-template promesse/promesse_standard   # Template specifique
```

**Auto-declenchement**: Claude l'utilise quand vous mentionnez "conformite", "audit template", "verifier template".

---

#### `/review-pr`
**Usage**: `/review-pr <numero>`

Revue de code avec les conventions Notomai (securite RGPD, templates, patterns Jinja2).

```
/review-pr 42
/review-pr 17
```

**Auto-declenchement**: Claude l'utilise quand vous mentionnez "review PR", "revue de code".

---

#### `/status`
**Usage**: `/status`

Dashboard complet: templates, tests, API, deploy, database.

**Auto-declenchement**: Claude l'utilise quand vous demandez "ou en est-on?", "status", "etat du projet".

---

#### `/sprint-plan`
**Usage**: `/sprint-plan [focus]`

Planning sprint avec repartition 3 devs (Tom, Augustin, Paul).

```
/sprint-plan              # Analyse complete
/sprint-plan frontend     # Focus frontend
/sprint-plan tests        # Focus tests
/sprint-plan security     # Focus securite
```

**Auto-declenchement**: Claude l'utilise quand vous demandez "planning", "prochaines taches", "qu'est-ce qu'on fait?".

---

## Agents - Sous-agents specialises

Les agents sont **delegates automatiquement** par Claude quand il detecte une tache correspondante. Ils travaillent dans un **contexte isole**.

### template-auditor

**Declencheur**: Modification de templates Jinja2, demande d'audit de conformite.

**Specialite**: Compare les templates dans `templates/` avec les trames de reference dans `docs_original/`. Verifie les bookmarks, blocs conditionnels, couverture des variables.

**Outils**: Read, Grep, Glob, Bash

**Sortie**: Rapport de conformite avec pourcentage, sections manquantes, variables non mappees.

---

### schema-validator

**Declencheur**: Modification de schemas JSON, questions, catalogues.

**Specialite**: Valide la coherence entre `schemas/variables_*.json`, `schemas/questions_*.json` et `schemas/*_catalogue.json`. Verifie les references croisees, les variables sans questions, les questions sans variables.

**Outils**: Read, Grep, Glob, Bash

**Sortie**: Rapport de validation avec erreurs, warnings, suggestions d'enrichissement.

---

### security-reviewer

**Declencheur**: Modification de code dans `execution/security/`, manipulation de PII, endpoints API.

**Specialite**: Revue RGPD, detection de credentials en dur, validation des RLS Supabase, protection PII dans les logs.

**Outils**: Read, Grep, Glob, Bash

**Sortie**: Rapport securite (CRITICAL/HIGH/MEDIUM/LOW) avec remediations.

---

## Hooks - Automatisations

### Protection docs_original/ (PreToolUse)
**Declencheur**: Toute tentative d'Edit ou Write sur un fichier dans `docs_original/`.
**Action**: Bloque l'operation (exit code 2). Les trames originales ne doivent JAMAIS etre modifiees.

### Log des ecritures (PostToolUse)
**Declencheur**: Apres chaque Write de fichier code (.py, .md, .json, .ts, .tsx).
**Action**: Affiche le nom du fichier ecrit pour suivi.

---

## Commandes legacy

### `/ultra-think`
**Usage**: `/ultra-think <probleme>`

Mode d'analyse approfondie multi-dimensionnelle. Utile pour les problemes architecturaux complexes.

---

## Guide rapide par role

### Tom (Backend & Infrastructure)
```
/test-pipeline          # Apres chaque modification
/deploy-modal prod      # Deploiement production
/status                 # Point d'equipe
/sprint-plan            # Planning sprint
```

### Augustin (Frontend & Formulaires)
```
/generer-acte vente     # Tester la generation
/review-pr 42           # Review de code
/status                 # Verifier l'etat API
```

### Paul (Workflows & Diagnostics)
```
/test-pipeline          # Apres chaque modification
/valider-template all   # Audit templates
/generer-promesse standard  # Tester le workflow promesse
```

---

## Configuration technique

### Fichiers partages (commites dans git)
```
.claude/settings.json          # Hooks
.claude/skills/*/SKILL.md      # Skills
.claude/agents/*.md            # Agents
.mcp.json                      # MCP servers
```

### Fichiers personnels (dans .gitignore)
```
.claude/settings.local.json    # Permissions individuelles
```

### Ajouter un nouveau skill
```bash
mkdir .claude/skills/mon-skill
# Creer .claude/skills/mon-skill/SKILL.md avec le format YAML frontmatter
```

### Ajouter un nouvel agent
```bash
# Creer .claude/agents/mon-agent.md avec le format YAML frontmatter
```
