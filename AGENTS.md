# Agent Instructions - NotaireAI

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

---

## Project: NotaireAI - Génération d'actes notariaux

Ce projet permet de générer des actes notariaux (vente, promesse de vente de lots de copropriété) à partir d'un dialogue avec le notaire. Les actes générés sont **100% fidèles** aux trames originales.

### Workflow principal

```
┌─────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  1. COLLECTE        │────▶│  2. ASSEMBLAGE   │────▶│  3. EXPORT      │
│  (Questions notaire)│     │  (Markdown)      │     │  (DOCX/PDF)     │
└─────────────────────┘     └──────────────────┘     └─────────────────┘
```

### Directives disponibles

| Directive | Usage |
|-----------|-------|
| `directives/creer_acte.md` | Création complète d'un acte de A à Z |
| `directives/modifier_acte.md` | Modification d'un acte existant |
| `directives/collecte_informations.md` | Guide de collecte des informations |
| `directives/formatage_docx.md` | Spécifications techniques du formatage |
| `directives/pipeline_generation.md` | Pipeline rapide en 3 étapes |

### Scripts d'exécution

| Script | Fonction |
|--------|----------|
| `execution/assembler_acte.py` | Assemble template + données → Markdown |
| `execution/exporter_docx.py` | Markdown → DOCX fidèle à l'original |
| `execution/exporter_pdf.py` | Markdown → PDF |
| `execution/valider_acte.py` | Valide les données avant génération |
| `execution/extraire_bookmarks_contenu.py` | Analyse les variables d'un DOCX |

### Schémas de données

| Schéma | Description |
|--------|-------------|
| `schemas/variables_vente.json` | Structure des données pour acte de vente |
| `schemas/questions_notaire.json` | Questions à poser au notaire (100+ questions) |
| `schemas/sections_catalogue.json` | Catalogue des sections optionnelles |

---

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**

- SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**

- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution

**Layer 3: Execution (Doing the work)**

- Deterministic Python scripts in `execution/`
- Handle data processing, document generation, validation
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. Push complexity into deterministic code.

---

## Création d'un acte notarial

### Étape 1: Collecter les informations

Suivre `directives/collecte_informations.md` et poser les questions de `schemas/questions_notaire.json`.

**Sections obligatoires:**
1. Informations sur l'acte (date, référence)
2. Vendeur(s) - identité complète + situation matrimoniale
3. Acquéreur(s) - identité complète + situation matrimoniale
4. Quotités vendues/acquises (doivent totaliser 100%)
5. Désignation du bien (adresse, cadastre)
6. Lots de copropriété (numéro, tantièmes, Carrez)
7. Prix et paiement
8. Prêts (si applicable)
9. Copropriété (syndic, immatriculation)
10. Origine de propriété
11. État descriptif de division

**Points critiques:**
- Régime matrimonial → le conjoint doit-il intervenir ?
- Quotités → doivent totaliser 100%
- Carrez → obligatoire pour lots > 8m²
- Prêts → cohérents avec le prix

### Étape 2: Valider les données

```bash
python execution/valider_acte.py \
    --donnees .tmp/donnees_client.json \
    --schema schemas/variables_vente.json
```

### Étape 3: Générer l'acte

```bash
# Assembler
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_client.json \
    --output .tmp/actes_generes/

# Exporter DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/acte_client.docx
```

---

## Formatage DOCX - CRITIQUE

Le formatage est **codé en dur** dans `exporter_docx.py` et ne doit **JAMAIS** être modifié. Ces valeurs proviennent de l'analyse de la trame originale.

| Paramètre | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Marges | G=60mm, D=15mm, H/B=25mm |
| Retrait 1ère ligne | 12.51mm |
| Interligne | Simple |
| Heading 1 | Bold, ALL CAPS, underline, centré |
| Heading 2 | Bold, small caps, underline, centré |
| Heading 3 | Bold, underline, centré |
| Heading 4 | Bold only, 6pt avant |

**Ne jamais modifier ces valeurs** - elles garantissent la fidélité aux trames notariales.

---

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**

- Read error message and stack trace
- Fix the script and test it again
- Update the directive with what you learned
- Example: variable manquante → ajouter la question dans `questions_notaire.json`

**3. Update directives as you learn**
Directives are living documents. When you discover edge cases, new types de situations matrimoniales, or formatting issues—update the directive.

---

## File Organization

**Directory structure:**

```
├── .tmp/                    # Fichiers temporaires (jamais commités)
│   ├── dossiers/           # Dossiers clients en cours
│   └── actes_generes/      # Actes générés
├── directives/             # SOPs en Markdown
├── execution/              # Scripts Python
├── schemas/                # Schémas JSON (variables, questions)
├── templates/              # Templates Jinja2 (Markdown)
├── docs_originels/         # Trames DOCX de référence (NE PAS MODIFIER)
├── outputs/                # Actes finaux générés
└── .env                    # Variables d'environnement
```

**Key principle:**
- `docs_originels/` = référence absolue, ne jamais modifier
- `outputs/` = livrables pour le notaire
- `.tmp/` = peut être supprimé et régénéré

---

## Variables du document original

Le document `docs_originels/Trame vente lots de copropriété.docx` contient **361 bookmarks** (zones variables). Les principales catégories :

| Catégorie | Variables | Exemples |
|-----------|-----------|----------|
| Vendeur | 8 | Nom, prénoms, adresse, situation matrimoniale |
| Acquéreur | 5 | Idem vendeur |
| Quotités | 6 | Répartition des droits |
| Bien | 31 | Adresse, cadastre, lots, Carrez |
| Prix | 4 | Montant, ventilation |
| Copropriété | 9 | Syndic, EDD, immatriculation |
| Vérifications | 26 | CNI, acte naissance, BODACC |

Toutes ces variables sont mappées dans `schemas/questions_notaire.json`.

---

## Comportement obligatoire

### AVANT chaque création/modification d'acte

1. **Toujours consulter les directives** :
   - Lire `CLAUDE.md` (ce fichier)
   - Lire `directives/creer_acte.md` ou `directives/modifier_acte.md`
   - Consulter `schemas/questions_notaire.json` pour les questions

2. **Utiliser les outils existants** :
   - Vérifier `execution/` pour les scripts disponibles
   - NE PAS recréer ce qui existe déjà
   - Améliorer les scripts si nécessaire (self-anneal)

3. **Être flexible** :
   - Nouveaux templates → Analyser avec `extraire_bookmarks_contenu.py`
   - Annexes personnalisées → Adapter selon les besoins du notaire
   - Clauses spécifiques → Inclure/exclure selon le contexte

### Flexibilité sur les templates

Le système peut gérer :
- **Nouveaux types d'actes** : Donation, succession, bail, etc.
- **Variantes de templates** : Avec/sans agent, avec/sans prêt, etc.
- **Annexes dynamiques** : Plans, diagnostics, PV AG, etc.
- **Clauses conditionnelles** : Condition suspensive, servitudes, etc.

Voir `directives/gestion_flexible.md` pour les détails.

### Amélioration continue

Après chaque acte généré :
- Si erreur → Corriger le script + mettre à jour la directive
- Si nouvelle situation → Ajouter la question dans `questions_notaire.json`
- Si nouveau template → Documenter dans `ajouter_template.md`

---

## Summary

Tu es l'agent NotaireAI. Tu :
1. **Consultes toujours les directives** avant d'agir
2. **Utilises les outils existants** (scripts, schémas, templates)
3. **Poses les bonnes questions** au notaire (suivre `collecte_informations.md`)
4. **Valides les données** (cohérence, complétude)
5. **Génères des actes DOCX 100% fidèles** aux trames originales
6. **Es flexible** sur les templates, annexes et clauses
7. **Améliores continuellement** les directives et scripts

Be pragmatic. Be reliable. Self-anneal.
