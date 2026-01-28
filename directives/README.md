# Index des Directives - NotaireAI

## Vue d'ensemble

Ce dossier contient les SOPs (Standard Operating Procedures) pour la génération et la modification d'actes notariaux. Chaque directive est autonome et documentée.

---

## Directives principales

### Création d'actes

| Directive | Description | Quand l'utiliser |
|-----------|-------------|------------------|
| [creer_acte.md](creer_acte.md) | Création d'un acte de vente définitif | Vente finale lots copropriété |
| [creer_promesse_vente.md](creer_promesse_vente.md) | Création d'une promesse unilatérale de vente | Avant-contrat avec option |
| [creer_reglement_copropriete.md](creer_reglement_copropriete.md) | Création d'un EDD et règlement de copropriété | Mise en copropriété d'un immeuble |
| [creer_modificatif_edd.md](creer_modificatif_edd.md) | Modification d'un EDD/RC existant | Division/réunion lots, création PCS |
| [collecte_informations.md](collecte_informations.md) | Guide de collecte des informations | Dialogue avec le notaire |
| [modifier_acte.md](modifier_acte.md) | Modification d'un acte existant | Corrections, ajouts, modifications |

### Aspects techniques

| Directive | Description | Quand l'utiliser |
|-----------|-------------|------------------|
| [formatage_docx.md](formatage_docx.md) | Spécifications de formatage DOCX | Référence technique, debug formatage |
| [pipeline_generation.md](pipeline_generation.md) | Pipeline rapide en 3 étapes | Génération rapide sans questions |
| [validation_donnees.md](validation_donnees.md) | Règles de validation | Comprendre les erreurs de validation |

### Extension du système

| Directive | Description | Quand l'utiliser |
|-----------|-------------|------------------|
| [ajouter_template.md](ajouter_template.md) | Ajouter un nouveau type d'acte | Donation, succession, bail, etc. |
| [apprentissage_continu.md](apprentissage_continu.md) | Enrichissement continu de la base | Nouvelles clauses, questions, templates |

---

## Workflow typique

```
┌─────────────────────────────────────────────────────────────────┐
│                    CRÉATION D'UN ACTE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Lire creer_acte.md                                         │
│     └─► Vue d'ensemble du processus                            │
│                                                                 │
│  2. Suivre collecte_informations.md                            │
│     └─► Poser les questions au notaire                         │
│     └─► Utiliser schemas/questions_notaire.json                │
│                                                                 │
│  3. Consulter validation_donnees.md si erreurs                 │
│     └─► Comprendre et corriger les problèmes                   │
│                                                                 │
│  4. Utiliser pipeline_generation.md                            │
│     └─► Commandes pour générer l'acte                          │
│                                                                 │
│  5. Référencer formatage_docx.md si besoin                     │
│     └─► Vérifier la fidélité du formatage                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────┐
│                  MODIFICATION D'UN ACTE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Lire modifier_acte.md                                      │
│     └─► Identifier le type de modification                     │
│                                                                 │
│  2. Appliquer les modifications selon le type                  │
│     └─► Correction simple                                      │
│     └─► Ajout/retrait de section                               │
│     └─► Modification structurelle                              │
│                                                                 │
│  3. Revalider avec validation_donnees.md                       │
│                                                                 │
│  4. Régénérer avec pipeline_generation.md                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Schémas associés

| Schéma | Directive liée | Description |
|--------|----------------|-------------|
| `schemas/variables_vente.json` | creer_acte.md | Structure des données pour vente |
| `schemas/variables_promesse_vente.json` | creer_promesse_vente.md | Structure des données pour promesse |
| `schemas/variables_reglement_copropriete.json` | creer_reglement_copropriete.md | Structure des données pour EDD/RC |
| `schemas/variables_modificatif_edd.json` | creer_modificatif_edd.md | Structure des données pour modificatif |
| `schemas/questions_notaire.json` | collecte_informations.md | 100+ questions pour vente |
| `schemas/questions_promesse_vente.json` | creer_promesse_vente.md | Questions pour promesse |
| `schemas/questions_reglement_copropriete.json` | creer_reglement_copropriete.md | Questions pour EDD/RC |
| `schemas/questions_modificatif_edd.json` | creer_modificatif_edd.md | Questions pour modificatif |
| `schemas/sections_catalogue.json` | creer_acte.md | Sections optionnelles |
| `schemas/clauses_catalogue.json` | apprentissage_continu.md | 45+ clauses réutilisables |
| `schemas/annexes_catalogue.json` | apprentissage_continu.md | 28+ types d'annexes |

---

## Scripts d'exécution

| Script | Directives liées | Fonction |
|--------|------------------|----------|
| `assembler_acte.py` | pipeline_generation.md | Template + données → Markdown |
| `exporter_docx.py` | formatage_docx.md | Markdown → DOCX fidèle |
| `exporter_pdf.py` | pipeline_generation.md | Markdown → PDF |
| `valider_acte.py` | validation_donnees.md | Validation des données |
| `extraire_bookmarks_contenu.py` | ajouter_template.md | Analyse des variables DOCX |

---

## Points critiques à retenir

### Formatage DOCX (NE JAMAIS MODIFIER)

| Paramètre | Valeur |
|-----------|--------|
| Police | Times New Roman 11pt |
| Marges | G=60mm, D=15mm, H/B=25mm |
| Retrait 1ère ligne | 12.51mm |

### Règles métier essentielles

1. **Quotités** : doivent toujours totaliser 100%
2. **Carrez** : obligatoire pour lots > 8m²
3. **Régime matrimonial** : vérifier si conjoint doit intervenir
4. **Prêts** : cohérents avec le prix

### Documents de référence

| Document | Bookmarks | Type d'acte |
|----------|-----------|-------------|
| `docs_original/Trame vente lots de copropriété.docx` | 361 | Vente |
| `docs_original/Trame promesse unilatérale de vente lots de copropriété.docx` | 298 | Promesse |
| `docs_original/Trame reglement copropriete EDD.docx` | 116 | EDD/RC |
| `docs_original/trame modificatif.docx` | 60 | Modificatif |

**NE JAMAIS MODIFIER ces trames originales.**

---

## Historique des directives

| Date | Action | Directive |
|------|--------|-----------|
| 2025-01-17 | Création | creer_acte.md, modifier_acte.md |
| 2025-01-19 | Création | formatage_docx.md, pipeline_generation.md, collecte_informations.md |
| 2025-01-19 | Création | ajouter_template.md, validation_donnees.md, README.md |
| 2025-01-19 | Mise à jour | creer_acte.md, modifier_acte.md |
| 2025-01-19 | Création | creer_promesse_vente.md, apprentissage_continu.md |
| 2025-01-19 | Création | creer_reglement_copropriete.md, creer_modificatif_edd.md |

---

## Pour aller plus loin

- [CLAUDE.md](../CLAUDE.md) - Instructions globales de l'agent
- [README.md](../README.md) - Documentation générale du projet
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Instructions de déploiement
