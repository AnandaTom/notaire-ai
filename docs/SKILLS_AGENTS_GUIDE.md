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

#### 🆕 `/generer-acte-parallel` (Opus 4.6 Agent Teams)
**Usage**: `/generer-acte-parallel <type> "<demande>"`

**NOUVEAU** - Generation parallele avec coordination multi-agents (Opus 4.6). **3-5x plus rapide** que le mode sequential.

```
/generer-acte-parallel promesse "Martin→Dupont, 67m² Paris 15e, 450k€"
/generer-acte-parallel vente --auto
/generer-acte-parallel promesse --strategy=sequential  # Fallback mode
```

**Workflow interne**:
1. Parse requete → intent
2. Spawn `workflow-orchestrator` (Opus)
3. Orchestrator lance 6 agents:
   - **PARALLEL** (3-5s): cadastre-enricher, data-collector-qr, template-auditor
   - **SEQUENTIAL** (~2s): schema-validator → Assemblage
   - **PARALLEL** (2-3s): clause-suggester + Export DOCX
   - **FINAL** (~1s): post-generation-reviewer
4. Decision: PASS/WARNING/BLOCKED
5. Return DOCX + rapport performance

**Speedup attendu**:
- Promesse: 15-20s → **5-8s** (2.5-3x)
- Vente: 18-25s → **6-10s** (2.5-3x)
- Titre → Promesse: 20-30s → **8-15s** (2-3x)

**Options**:
- `--strategy=sequential` - Force mode sequential (debugging)
- `--no-clauses` - Skip clause-suggester (plus rapide)
- `--verbose` - Logs detailles agents

**Sortie**:
```markdown
## ✅ Acte Genere en Mode Parallele

**Duree**: 7.8s (vs 20.3s sequential)
**Speedup**: 2.6x plus rapide
**QA Score**: 94/100

### Agents Executes
- cadastre-enricher: 487ms ✅
- data-collector-qr: 3.2s ✅
- template-auditor: 1.8s ✅
- schema-validator: 124ms ✅
- clause-suggester: 1.7s ✅
- post-generation-reviewer: 892ms ✅

### Clauses Suggerees (3)
🔴 CRITIQUE: Condition suspensive pret [Score: 95]
🟡 RECOMMANDEE: Garantie bancaire [Score: 65]
...

**Fichier**: outputs/promesse_Martin_Dupont_20260211.docx
```

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
/valider-template promesse_hors_copropriete    # Template specifique
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

### 🆕 Agents Opus 4.6 (Agent Teams) - 11/02/2026

#### workflow-orchestrator (Opus)

**Declencheur**: Generation complexe end-to-end, workflows multi-etapes, mode parallele.

**Specialite**: Cerveau central qui coordonne 5+ agents en parallele. Parse requete → planifie execution optimale → lance agents (parallel/sequential) → aggrege resultats → decision go/no-go → rapport performance.

**Outils**: Task, Bash, Read, Write, Grep, Glob

**Sortie**: Rapport execution avec speedup vs sequential, duree par agent, QA score, fichier genere.

---

#### cadastre-enricher (Haiku)

**Declencheur**: Adresse incomplete, cadastre manquant, nouveau dossier (proactif).

**Specialite**: Enrichit donnees cadastrales via APIs gouvernementales (BAN geocoding + IGN parcelles). Adresse → code_insee + parcelle officielle + surface m². Fallback gracieux si API indisponible.

**Outils**: Bash, Read, Write

**Sortie**: Donnees enrichies avec code_insee, surface_m2, coordinates, source=api_cadastre_gouv.

**Performance**: ~500ms, cache 24h TTL.

---

#### data-collector-qr (Sonnet)

**Declencheur**: Champs manquants, nouveau dossier, mode interactif.

**Specialite**: Collecte interactive schema-driven (97 questions, 21 sections). Prefill 64% depuis titre/beneficiaires/prix. Questions conditionnelles (skip si non applicable). Validation temps reel.

**Outils**: Read, Write, Bash, AskUserQuestion

**Sortie**: Donnees completes JSON, taux_completion 100%, questions_posees ≤40.

**Performance**: 3-180s selon mode (auto vs interactif).

---

#### clause-suggester (Opus)

**Declencheur**: Apres assemblage Markdown, avant export final.

**Specialite**: Analyse contexte (type bien, parties, prix, conditions) et suggere 3-5 clauses pertinentes du catalogue (45+). Scoring contextuel avec justifications legales (art. Code Civil). Priorite: CRITIQUE/RECOMMANDEE/OPTIONNELLE.

**Outils**: Read, Grep, Glob

**Sortie**: Suggestions rankees par score + justifications + variables requises + impact legal.

**Performance**: ~2s, precision 90%+.

---

#### post-generation-reviewer (Sonnet)

**Declencheur**: Apres export DOCX, avant livraison notaire.

**Specialite**: QA final 10 dimensions: bookmarks (298/298), quotites=100%, prix coherent, Carrez obligatoire, diagnostics, formatage (Times 11pt, 60mm marge), sections obligatoires, validation legale, coherence cross-field, metadata. Bloque livraison si erreur critique.

**Outils**: Bash, Read, Grep

**Sortie**: Rapport QA avec score/100, status PASS/WARNING/BLOCKED, liste issues par severite.

**Performance**: ~1s, detection erreurs 95%+.

---

### Agents Existants (v1.0)

#### template-auditor (Sonnet)

**Declencheur**: Modification de templates Jinja2, demande d'audit de conformite.

**Specialite**: Compare les templates dans `templates/` avec les trames de reference dans `docs_original/`. Verifie les bookmarks, blocs conditionnels, couverture des variables.

**Outils**: Read, Grep, Glob, Bash

**Sortie**: Rapport de conformite avec pourcentage, sections manquantes, variables non mappees.

---

#### schema-validator (Haiku)

**Declencheur**: Modification de schemas JSON, questions, catalogues.

**Specialite**: Valide la coherence entre `schemas/variables_*.json`, `schemas/questions_*.json` et `schemas/*_catalogue.json`. Verifie les references croisees, les variables sans questions, les questions sans variables.

**Outils**: Read, Grep, Glob, Bash

**Sortie**: Rapport de validation avec erreurs, warnings, suggestions d'enrichissement.

---

#### security-reviewer

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
