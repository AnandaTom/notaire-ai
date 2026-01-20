# Catalogue de Clauses Modulaires - NotaireAI

**Total**: 48 clauses réparties en 16 catégories

## 🎯 Utilisation

Chaque clause est un fichier Markdown autonome avec:
- ✅ Zones grisées automatiques (`<<<VAR_START>>>` / `<<<VAR_END>>>`)
- ✅ Conditions d'application Jinja2
- ✅ Variables documentées
- ✅ Métadonnées (source, date, type d'acte)

## 📁 Structure

```
clauses/
├── README.md (ce fichier)
├── conditions_suspensives/
│   ├── _INDEX.md
│   ├── cs_pret_standard.md
│   └── ...
├── garanties/
│   ├── _INDEX.md
│   └── ...
└── ...
```

## 📊 Catégories

### conditions_suspensives (6 clauses)

- **Description**: Conditions dont la réalisation conditionne la vente
- **Clauses obligatoires**: 2/6
- **Répertoire**: [`conditions_suspensives/`](./conditions_suspensives/_INDEX.md)

### copropriete (3 clauses)

- **Description**: Clauses spécifiques à la copropriété
- **Clauses obligatoires**: 3/3
- **Répertoire**: [`copropriete/`](./copropriete/_INDEX.md)

### delais_retractation (1 clauses)

- **Description**: Clauses relatives au délai de rétractation
- **Clauses obligatoires**: 1/1
- **Répertoire**: [`delais_retractation/`](./delais_retractation/_INDEX.md)

### diagnostics (2 clauses)

- **Description**: Clauses relatives aux diagnostics
- **Clauses obligatoires**: 2/2
- **Répertoire**: [`diagnostics/`](./diagnostics/_INDEX.md)

### divers (3 clauses)

- **Description**: Clauses diverses
- **Clauses obligatoires**: 3/3
- **Répertoire**: [`divers/`](./divers/_INDEX.md)

### execution_forcee (1 clauses)

- **Description**: Clauses d'exécution forcée
- **Clauses obligatoires**: 0/1
- **Répertoire**: [`execution_forcee/`](./execution_forcee/_INDEX.md)

### fiscalite (3 clauses)

- **Description**: Clauses fiscales
- **Clauses obligatoires**: 3/3
- **Répertoire**: [`fiscalite/`](./fiscalite/_INDEX.md)

### fiscalite_copropriete (2 clauses)

- **Description**: Clauses fiscales spécifiques à la copropriété
- **Clauses obligatoires**: 0/2
- **Répertoire**: [`fiscalite_copropriete/`](./fiscalite_copropriete/_INDEX.md)

### garanties (4 clauses)

- **Description**: Clauses de garantie du vendeur/promettant
- **Clauses obligatoires**: 3/4
- **Répertoire**: [`garanties/`](./garanties/_INDEX.md)

### indemnite_immobilisation (2 clauses)

- **Description**: Clauses relatives à l'indemnité d'immobilisation (promesse unilatérale)
- **Clauses obligatoires**: 1/2
- **Répertoire**: [`indemnite_immobilisation/`](./indemnite_immobilisation/_INDEX.md)

### modificatif_edd (5 clauses)

- **Description**: Clauses spécifiques aux modificatifs de l'EDD
- **Clauses obligatoires**: 3/5
- **Répertoire**: [`modificatif_edd/`](./modificatif_edd/_INDEX.md)

### reglement_copropriete (9 clauses)

- **Description**: Clauses spécifiques au règlement de copropriété et EDD
- **Clauses obligatoires**: 4/9
- **Répertoire**: [`reglement_copropriete/`](./reglement_copropriete/_INDEX.md)

### servitudes (2 clauses)

- **Description**: Clauses relatives aux servitudes
- **Clauses obligatoires**: 1/2
- **Répertoire**: [`servitudes/`](./servitudes/_INDEX.md)

### servitudes_copropriete (2 clauses)

- **Description**: Servitudes spécifiques en copropriété
- **Clauses obligatoires**: 0/2
- **Répertoire**: [`servitudes_copropriete/`](./servitudes_copropriete/_INDEX.md)

### substitution (2 clauses)

- **Description**: Clauses de substitution
- **Clauses obligatoires**: 0/2
- **Répertoire**: [`substitution/`](./substitution/_INDEX.md)

### urbanisme (1 clauses)

- **Description**: Clauses urbanistiques
- **Clauses obligatoires**: 1/1
- **Répertoire**: [`urbanisme/`](./urbanisme/_INDEX.md)


## 🔧 Insérer une Clause

### Méthode 1: Include Jinja2

```jinja2
{%- include 'clauses/conditions_suspensives/cs_pret_standard.md' -%}
```

### Méthode 2: Script Python

```python
from pathlib import Path

def inserer_clause(template_path, clause_id, position='avant', marqueur=None):
    # Charge la clause
    clause_path = Path(f'clauses/{cat}/{clause_id}.md')

    # Insère dans le template
    # ...
```

## 📝 Ajouter une Nouvelle Clause

1. Ajouter dans `schemas/clauses_catalogue.json`
2. Exécuter `python execution/creer_clauses_modulaires.py`
3. Les fichiers sont automatiquement générés

---

**Généré automatiquement** par `execution/creer_clauses_modulaires.py`
