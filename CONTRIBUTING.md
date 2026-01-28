# Guide de Contribution - Notomai

Ce document définit les conventions et règles pour contribuer au projet Notomai.

## Structure du Projet (v1.5.0)

```
notomai/
├── api/                        # API REST (FastAPI)
├── directives/                 # SOPs et workflows (Markdown)
├── execution/                  # Scripts Python
│   ├── core/                   # Fonctions critiques (NE PAS MODIFIER sans review)
│   ├── gestionnaires/          # Orchestration métier
│   ├── analyse/                # Scripts d'analyse
│   ├── generation/             # Génération de données
│   ├── database/               # Accès BDD (Supabase)
│   ├── extraction/             # Module ML
│   ├── utils/                  # Utilitaires
│   ├── api/                    # Endpoints API internes
│   └── security/               # Sécurité RGPD
├── schemas/                    # Schémas JSON
├── templates/                  # Templates Jinja2
│   ├── vente/                  # Templates vente
│   ├── promesse/               # Templates promesse
│   ├── copropriete/            # Templates copropriété
│   ├── donation/               # Templates donation
│   ├── sections/               # Sections modulaires
│   └── _archive/               # Templates obsolètes
├── docs/                       # Documentation technique
├── docs_original/              # Trames de référence (LECTURE SEULE)
├── frontend/                   # Application Next.js
├── outputs/                    # Actes générés
└── tests/                      # Tests automatisés
```

## Conventions de Nommage

### Fichiers Python
- **Convention** : `snake_case.py`
- **Exemples** : `assembler_acte.py`, `gestionnaire_promesses.py`

### Fichiers Markdown
- **Directives** : `snake_case.md` (ex: `creer_acte.md`)
- **Docs racine** : `UPPERCASE.md` (ex: `README.md`, `CHANGELOG.md`)

### Fichiers JSON
- **Convention** : `type_categorie.json`
- **Exemples** : `variables_vente.json`, `questions_promesse_vente.json`

### Répertoires
- **Convention** : `snake_case` en anglais
- **Exceptions** : `directives/` (domaine métier français)

## Règles Git

### Branches
```
main              → Production (protégée)
develop           → Intégration
feature/*         → Nouvelles fonctionnalités
fix/*             → Corrections de bugs
refactor/*        → Restructurations
docs/*            → Documentation
```

### Messages de Commit
```
feat: Nouvelle fonctionnalité
fix: Correction de bug
docs: Documentation uniquement
refactor: Restructuration sans changement fonctionnel
chore: Maintenance, dépendances
test: Ajout ou modification de tests
perf: Amélioration de performance
```

**Format** :
```
type: description courte (< 70 caractères)

Description détaillée si nécessaire.

Co-Authored-By: [Nom] <email>
```

## Imports Python

Ordre des imports (PEP8 + conventions projet) :

```python
# 1. Standard library
import json
import os
from pathlib import Path

# 2. Third-party
from jinja2 import Environment
from python_docx import Document

# 3. Local - Core (critique)
from execution.core.assembler_acte import assembler_acte
from execution.core.exporter_docx import exporter_docx

# 4. Local - Gestionnaires
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

# 5. Local - Utils et autres
from execution.utils.suggerer_clauses import suggerer
from execution.database.supabase_client import get_client
```

## Fichiers Critiques

Ces fichiers ne doivent **jamais** être modifiés sans validation du Lead :

| Fichier | Raison |
|---------|--------|
| `execution/core/exporter_docx.py` | Formatage DOCX codé en dur |
| `docs_original/*.docx` | Trames de référence |
| `schemas/variables_*.json` | Structures de données validées |
| `.env` | Variables sensibles |

## Workflow de Développement

### 1. Avant de commencer
```bash
git checkout develop
git pull origin develop
git checkout -b feature/ma-fonctionnalite
```

### 2. Pendant le développement
- Suivre les conventions ci-dessus
- Ajouter des tests si applicable
- Documenter les changements

### 3. Avant de pousser
```bash
# Lancer les tests
pytest tests/ -v

# Vérifier le CLI
python notaire.py status

# Valider les templates
python execution/test_fiabilite.py
```

### 4. Pull Request
- Titre clair et concis
- Description des changements
- Référence aux issues si applicable

## Tests

### Structure des tests
```
tests/
├── conftest.py           # Fixtures partagées
├── test_assembler_acte.py
├── test_integration.py
└── fixtures/             # Données de test
```

### Commandes
```bash
pytest tests/ -v              # Tous les tests
pytest tests/ -k "assembler"  # Tests spécifiques
pytest tests/ --cov           # Avec couverture
```

## Documentation

### Mettre à jour la documentation
1. Modifier le fichier concerné dans `directives/` ou `docs/`
2. Si changement majeur, mettre à jour `CHANGELOG.md`
3. Si nouvelle fonctionnalité, documenter dans `CLAUDE.md`

### Synchroniser les fichiers miroirs
Les fichiers suivants doivent rester synchronisés :
- `CLAUDE.md` (maître)
- `AGENTS.md` (miroir)
- `GEMINI.md` (miroir)

## Contact

Pour toute question sur les conventions ou l'architecture, consulter :
- `CLAUDE.md` - Instructions complètes
- `directives/lecons_apprises.md` - Leçons de production
- `directives/workflow_notaire.md` - Workflow principal
