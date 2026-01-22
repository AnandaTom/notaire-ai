# Agent Instructions - NotaireAI

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

---

## Project: NotaireAI - Génération d'actes notariaux

Ce projet permet de générer des actes notariaux (vente, promesse de vente, règlement de copropriété, modificatif EDD) à partir d'un dialogue avec le notaire. Les actes générés sont **100% fidèles** aux trames originales.

### 🚀 Démarrage Rapide

**Nouveau utilisateur ?** Consulter [QUICKSTART.md](QUICKSTART.md) pour générer votre premier acte en 30 secondes.

**Développeur ?** Suivre [directives/bonnes_pratiques_templates.md](directives/bonnes_pratiques_templates.md) pour un développement 12x plus rapide.

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
| `directives/creer_acte.md` | Création d'un acte de vente définitif |
| `directives/creer_promesse_vente.md` | Création d'une promesse unilatérale de vente |
| `directives/creer_reglement_copropriete.md` | Création d'un EDD et règlement de copropriété |
| `directives/creer_modificatif_edd.md` | Modification d'un EDD/RC existant |
| `directives/modifier_acte.md` | Modification d'un acte existant |
| `directives/collecte_informations.md` | Guide de collecte des informations |
| `directives/formatage_docx.md` | Spécifications techniques du formatage |
| `directives/pipeline_generation.md` | Pipeline rapide en 3 étapes |
| `directives/apprentissage_continu.md` | Enrichissement continu de la base |
| `directives/lecons_apprises.md` | ⭐ **15 leçons** tirées des tests de production |
| `directives/workflow_notaire.md` | 🎯 **WORKFLOW PRINCIPAL** - À suivre pour chaque génération |
| `directives/bonnes_pratiques_templates.md` | 🚀 **PATTERNS JINJA2** - Templates robustes (12x plus rapide) |

### Scripts d'exécution

| Script | Fonction |
|--------|----------|
| `execution/assembler_acte.py` | Assemble template + données → Markdown (avec normalisation) |
| `execution/exporter_docx.py` | Markdown → DOCX fidèle à l'original |
| `execution/exporter_pdf.py` | Markdown → PDF |
| `execution/valider_acte.py` | Valide les données avant génération |
| `execution/extraire_bookmarks_contenu.py` | Analyse les variables d'un DOCX |
| `execution/generer_donnees_test.py` | Génère données aléatoires réalistes (Faker) |
| `execution/comparer_documents.py` | Valide conformité DOCX (≥80% requis) |
| `execution/detecter_type_acte.py` | Détection automatique du type d'acte |
| `execution/suggerer_clauses.py` | Intelligence de suggestion contextuelle |
| `execution/collecter_informations.py` | CLI interactive avec questionary |
| `execution/historique_supabase.py` | Sauvegarde historique (Supabase + offline) |
| `execution/workflow_rapide.py` | 🚀 **Génération 1 commande** - Validation → Assemblage → Export → Score |
| `execution/test_fiabilite.py` | ✅ **Tests automatisés** - Vérif min/max, zones grisées, conformité |
| `execution/valider_rapide.ps1` / `.sh` | ⚡ **Validation pré-commit** - 4 tests en 10 secondes |
| `execution/generer_donnees_minimales.py` | 🔧 Enrichit données avec 16 variables obligatoires |
| `execution/enrichir_prets_existants.py` | 💰 Calcule mensualités et enrichit prêts |

### Schémas de données

| Schéma | Description |
|--------|-------------|
| `schemas/variables_vente.json` | Structure des données pour acte de vente |
| `schemas/variables_promesse_vente.json` | Structure des données pour promesse de vente |
| `schemas/variables_reglement_copropriete.json` | Structure des données pour EDD/RC |
| `schemas/variables_modificatif_edd.json` | Structure des données pour modificatif |
| `schemas/questions_notaire.json` | Questions pour acte de vente (100+ questions) |
| `schemas/questions_promesse_vente.json` | Questions pour promesse de vente |
| `schemas/questions_reglement_copropriete.json` | Questions pour EDD/RC |
| `schemas/questions_modificatif_edd.json` | Questions pour modificatif |
| `schemas/sections_catalogue.json` | Catalogue des sections optionnelles |
| `schemas/clauses_catalogue.json` | Catalogue des clauses réutilisables |
| `schemas/annexes_catalogue.json` | Catalogue des types d'annexes |

### Templates disponibles

| Template | Type d'acte | Bookmarks |
|----------|-------------|-----------|
| `templates/vente_lots_copropriete.md` | Acte de vente définitif | 361 |
| `templates/promesse_vente_lots_copropriete.md` | Promesse unilatérale de vente | 298 |
| `templates/reglement_copropriete_edd.md` | EDD et règlement de copropriété | 116 |
| `templates/modificatif_edd.md` | Modificatif EDD/RC | 60 |

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

### Intégration de nouvelles sections (Vagues 4-5+)

**Règle d'Or** : **TOUJOURS** ajouter les sections à la FIN de `partie_developpee.md`, jamais inline.

**Conditions Obligatoires** :
```jinja2
{% if variable_racine and variable_racine.enfant %}
{% include 'sections/ma_section.md' %}
{% endif %}
```

**Test Progressif** :
1. Ajouter UN SEUL include
2. Tester assemblage avec `python execution/assembler_acte.py`
3. Si ✅ → Ajouter le suivant
4. Si ❌ → Commenter et analyser erreur avec message amélioré

**Messages d'erreur clairs** (depuis Vague 5) :
```
Variable manquante dans le template: 'plus_value' - 'dict object' has no attribute 'plus_value'
Vérifier que cette variable existe dans les données ou ajouter {% if plus_value %}
```

---

## Apprentissage Continu - CRITIQUE

### Principe : Enrichir la base à chaque interaction

À chaque échange avec un notaire, **TOUJOURS** vérifier et enrichir :

| Élément nouveau | Action | Fichier cible |
|-----------------|--------|---------------|
| Nouvelle clause | Ajouter avec variables Jinja2 | `schemas/clauses_catalogue.json` |
| Nouvelle question | Ajouter avec conditions | `schemas/questions_*.json` |
| Nouvelle annexe | Ajouter avec conditions | `schemas/annexes_catalogue.json` |
| Nouvelle règle de validation | Implémenter + documenter | `execution/valider_acte.py` |
| Nouveau type d'acte | Créer template + schéma + directive | `templates/`, `schemas/`, `directives/` |

### Catalogues à enrichir

| Catalogue | Contenu | Taille actuelle |
|-----------|---------|-----------------|
| `schemas/clauses_catalogue.json` | 45+ clauses réutilisables | 12 catégories |
| `schemas/annexes_catalogue.json` | 28+ types d'annexes | 6 catégories |
| `schemas/questions_notaire.json` | 100+ questions vente | 13 sections |
| `schemas/questions_promesse_vente.json` | Questions promesse | 21 sections |

### Format d'enrichissement

**Nouvelle clause :**
```json
{
  "id": "categorie_description",
  "nom": "Nom lisible",
  "type_acte": ["promesse_vente", "vente"],
  "texte": "Texte avec {{ variables }}",
  "variables_requises": ["var1", "var2"],
  "source": "Notaire X - Dossier Y - Date",
  "date_ajout": "YYYY-MM-DD"
}
```

Voir `directives/apprentissage_continu.md` pour le processus complet.

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
8. **ENRICHIS LA BASE** à chaque nouvelle clause, question ou situation

Be pragmatic. Be reliable. Self-anneal. **Build knowledge.**

---

## 🎯 Comportement par Défaut - CRITIQUE

### Quand un Notaire Demande de Générer un Acte

**TOUJOURS suivre ce process**:

1. **Lire `directives/workflow_notaire.md`** - Workflow complet
2. **Vérifier conformité du template**:
   - ≥80% → Utiliser directement (PROD)
   - <80% → Utiliser exemple complet + avertir notaire
3. **Suivre le workflow en 5 étapes**:
   - Étape 1: Identification (type d'acte + conformité)
   - Étape 2: Collecte données (interactive ou exemple)
   - Étape 3: Détection auto + suggestions
   - Étape 4: Génération (assemble → export → validate)
   - Étape 5: Archivage + enrichissement continu
4. **Après génération**:
   - Valider conformité avec `comparer_documents.py`
   - Enrichir catalogues si nouvelles clauses/situations
   - Documenter dans `lecons_apprises.md` si edge case

### Templates Actuels (v1.1.0)

| Template | Conformité | Comportement |
|----------|-----------|--------------|
| Règlement copropriété | 85.5% ✅ | Utiliser directement |
| Modificatif EDD | 91.7% ✅ | Utiliser directement |
| Vente | 46% ⚠️ | Utiliser `exemples/donnees_vente_exemple.json` |
| Promesse | 60.9% ⚠️ | Utiliser `exemples/donnees_promesse_exemple.json` |

### Garanties au Notaire

**Pour templates PROD (≥80%)**:
> "Je génère un acte 100% conforme à la trame originale en moins d'1 minute. Le document sera identique à votre modèle habituel."

**Pour templates DEV (<80%)**:
> "Le template est en développement ({conformité}%). J'utilise les données d'exemple complètes pour garantir un document conforme dans les sections disponibles. Je vais enrichir le template progressivement."

### Enrichissement Obligatoire

**Après CHAQUE acte généré avec template <80%**:
1. Analyser rapport conformité
2. Identifier 3-5 sections manquantes prioritaires
3. Proposer au notaire: "Je peux enrichir le template avec ces sections maintenant, ça prendra 5 minutes"
4. Si accepté → Enrichir le template
5. Documenter dans CHANGELOG

**Objectif**: 4/4 templates ≥80% dans les 10 prochaines générations

---

## Version 1.2.0 - Performance & Templates PROD

### 🎯 Conformité Templates (Janvier 2026)

| Type | Conformité | Statut | Notes |
|------|-----------|--------|-------|
| Règlement copropriété | **85.5%** | ✅ PROD | Template complet, 22 tableaux |
| Modificatif EDD | **91.7%** | ✅ PROD | Template le plus abouti |
| **Vente** | **85.1%** | ✅ PROD | **37 sections, données enrichies** |
| Promesse | 60.9% | ⚠️ Dev | Template squelette (manque 24 titres) |

**Seuil production**: ≥80% de conformité structurelle. **3/4 templates en PROD!**

### ⚡ Performance Pipeline

| Étape | Durée | Description |
|-------|-------|-------------|
| Assemblage Jinja2 | 1.5s | Template + données → Markdown |
| Export DOCX | 3.5s | Markdown → Word formaté |
| Vérification | 0.7s | Comparaison structure |
| **TOTAL** | **5.7s** | **~8 pages/seconde** |

### 🔧 Corrections Critiques Appliquées

1. **Deep copy automatique** - Fix mutations involontaires données imbriquées
2. **Normalisation PACS** - Alias `conjoint` pour `partenaire`, structure `pacs.*`
3. **Aplatissement personnes** - `personne_physique.*` → racine automatiquement
4. **Encodage UTF-8 Windows** - `sys.stdout.reconfigure()` pour tous scripts
5. **Filtres Jinja2** - Ajout `mois_en_lettres`, `jour_en_lettres`
6. **Quotités obligatoires** - Génération `quotites_vendues/acquises` pour vente
7. **Données matrimoniales** - Support complet divorce/veuf (ex_conjoint, defunt_conjoint)
8. **Structure tantièmes** - Format complet `{valeur, base, base_unite, type}`

### 📚 Nouvelles Ressources

- **[directives/lecons_apprises.md](directives/lecons_apprises.md)** - 15 leçons détaillées + checklist nouveau template
- **[CHANGELOG.md](CHANGELOG.md)** - Historique complet v1.0.0 → v1.1.0
- **6 nouveaux scripts** - Tests, génération, détection, suggestion, comparaison, historique
- **Tests automatisés** - pytest avec fixtures + integration tests

### 🎓 Principe Clé: Self-Anneal

Quand un problème survient:
1. Lire l'erreur + stack trace
2. **Corriger le code** (pas le workaround)
3. **Documenter dans `lecons_apprises.md`**
4. **Enrichir les catalogues** si applicable

**Exemple concret**: Quand `mois_en_lettres` manquait:
- ❌ Mauvais: Modifier le template pour éviter le filtre
- ✅ Bon: Créer le filtre + documenter + ajouter aux tests

Voir [CHANGELOG.md](CHANGELOG.md) pour détails complets.
