#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Créer le système de clauses modulaires depuis le catalogue JSON
Génère des fichiers Markdown individuels avec zones grisées
"""
import sys
import json
import os
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def normaliser_nom_fichier(texte):
    """Normalise un texte pour créer un nom de fichier valide"""
    # Remplacer caractères spéciaux
    remplacements = {
        'à': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        ' ': '_',
        '-': '_',
        '/': '_',
        "'": '',
        '"': '',
    }

    result = texte.lower()
    for old, new in remplacements.items():
        result = result.replace(old, new)

    # Garder seulement alphanumériques et underscore
    result = ''.join(c for c in result if c.isalnum() or c == '_')

    return result

def ajouter_zones_grisees(texte, variables_requises):
    """
    Ajoute les marqueurs de zones grisées aux variables Jinja2
    Transforme {{ var }} en <<<VAR_START>>>{{ var }}<<<VAR_END>>>
    """
    import re

    # Pattern pour détecter les variables Jinja2
    pattern = r'\{\{([^}]+)\}\}'

    def replacer(match):
        var_complete = match.group(0)  # {{ ... }}
        var_nom = match.group(1).strip()  # contenu sans {{ }}

        # Vérifier si déjà encadré
        if '<<<VAR_START>>>' in texte[max(0, match.start()-20):match.start()]:
            return var_complete

        return f'<<<VAR_START>>>{var_complete}<<<VAR_END>>>'

    return re.sub(pattern, replacer, texte)

def creer_fichier_clause(clause, categorie_nom, output_dir):
    """Crée un fichier Markdown pour une clause"""

    # Nom de fichier
    nom_fichier = normaliser_nom_fichier(clause['id']) + '.md'
    categorie_dir = output_dir / normaliser_nom_fichier(categorie_nom)
    categorie_dir.mkdir(parents=True, exist_ok=True)

    fichier_path = categorie_dir / nom_fichier

    # Contenu avec métadonnées
    contenu = f"""{{# ============================================================================
   CLAUSE: {clause['nom']}
   ID: {clause['id']}
   Catégorie: {categorie_nom}
   Type d'acte: {', '.join(clause['type_acte'])}
   Obligatoire: {'Oui' if clause.get('obligatoire', False) else 'Non'}
   Variables requises: {', '.join(clause.get('variables_requises', []))}
   Source: {clause.get('source', 'N/A')}
   Date ajout: {clause.get('date_ajout', 'N/A')}
   ============================================================================ #}}

"""

    # Condition d'application si existe
    if clause.get('condition_application'):
        contenu += f"{{%- if {clause['condition_application']} -%}}\n\n"

    # Texte de la clause avec zones grisées
    texte_clause = clause['texte']
    texte_avec_zones = ajouter_zones_grisees(texte_clause, clause.get('variables_requises', []))
    contenu += texte_avec_zones

    # Fermer condition
    if clause.get('condition_application'):
        contenu += "\n\n{%- endif -%}"

    # Écrire fichier
    with open(fichier_path, 'w', encoding='utf-8') as f:
        f.writelines(contenu)

    return fichier_path

def creer_index_categorie(categorie_nom, clauses, output_dir):
    """Crée un fichier index pour une catégorie"""

    categorie_dir = output_dir / normaliser_nom_fichier(categorie_nom)
    index_path = categorie_dir / '_INDEX.md'

    contenu = f"""# Clauses - {categorie_nom}

Total: {len(clauses)} clauses

## Liste des clauses

"""

    for clause in clauses:
        obligatoire = '🔴 OBLIGATOIRE' if clause.get('obligatoire') else '🟢 Optionnelle'
        types = ', '.join(clause['type_acte'])
        contenu += f"### {clause['nom']}\n\n"
        contenu += f"- **ID**: `{clause['id']}`\n"
        contenu += f"- **Statut**: {obligatoire}\n"
        contenu += f"- **Type d'acte**: {types}\n"
        contenu += f"- **Fichier**: `{normaliser_nom_fichier(clause['id'])}.md`\n"

        if clause.get('variables_requises'):
            contenu += f"- **Variables**: {', '.join(clause['variables_requises'])}\n"

        contenu += "\n"

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(contenu)

    return index_path

def creer_index_global(categories, output_dir):
    """Crée l'index global de toutes les clauses"""

    index_path = output_dir / 'README.md'

    total_clauses = sum(len(cat['clauses']) for cat in categories.values())

    contenu = f"""# Catalogue de Clauses Modulaires - NotaireAI

**Total**: {total_clauses} clauses réparties en {len(categories)} catégories

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

"""

    for cat_nom, cat_data in sorted(categories.items()):
        nb_clauses = len(cat_data['clauses'])
        obligatoires = sum(1 for c in cat_data['clauses'] if c.get('obligatoire'))

        contenu += f"### {cat_nom} ({nb_clauses} clauses)\n\n"
        contenu += f"- **Description**: {cat_data['description']}\n"
        contenu += f"- **Clauses obligatoires**: {obligatoires}/{nb_clauses}\n"
        contenu += f"- **Répertoire**: [`{normaliser_nom_fichier(cat_nom)}/`](./{normaliser_nom_fichier(cat_nom)}/_INDEX.md)\n\n"

    contenu += f"""
## 🔧 Insérer une Clause

### Méthode 1: Include Jinja2

```jinja2
{{%- include 'clauses/conditions_suspensives/cs_pret_standard.md' -%}}
```

### Méthode 2: Script Python

```python
from pathlib import Path

def inserer_clause(template_path, clause_id, position='avant', marqueur=None):
    # Charge la clause
    clause_path = Path(f'clauses/{{cat}}/{{clause_id}}.md')

    # Insère dans le template
    # ...
```

## 📝 Ajouter une Nouvelle Clause

1. Ajouter dans `schemas/clauses_catalogue.json`
2. Exécuter `python execution/creer_clauses_modulaires.py`
3. Les fichiers sont automatiquement générés

---

**Généré automatiquement** par `execution/creer_clauses_modulaires.py`
"""

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(contenu)

    return index_path

if __name__ == "__main__":
    # Charger catalogue
    catalogue_path = Path('schemas/clauses_catalogue.json')
    output_dir = Path('clauses')

    print("Chargement du catalogue...")
    with open(catalogue_path, 'r', encoding='utf-8') as f:
        catalogue = json.load(f)

    categories = catalogue['categories']
    print(f"  → {len(categories)} catégories trouvées")
    print(f"  → {sum(len(cat['clauses']) for cat in categories.values())} clauses au total")

    # Créer structure
    output_dir.mkdir(exist_ok=True)
    print(f"\nCréation des fichiers dans {output_dir}/...")

    total_fichiers = 0
    for cat_nom, cat_data in categories.items():
        print(f"\n📁 {cat_nom} ({len(cat_data['clauses'])} clauses)")

        # Créer fichiers clauses
        for clause in cat_data['clauses']:
            fichier = creer_fichier_clause(clause, cat_nom, output_dir)
            print(f"  ✓ {fichier.name}")
            total_fichiers += 1

        # Créer index catégorie
        index = creer_index_categorie(cat_nom, cat_data['clauses'], output_dir)
        print(f"  📄 {index.name}")

    # Créer index global
    print(f"\nCréation de l'index global...")
    index_global = creer_index_global(categories, output_dir)
    print(f"  ✓ {index_global.name}")

    print(f"\n[OK] {total_fichiers} fichiers de clauses créés")
    print(f"  Répertoire: {output_dir.absolute()}")
    print(f"  Index: {index_global.absolute()}")
