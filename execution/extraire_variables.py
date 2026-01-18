#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraire_variables.py
=====================

Script d'extraction des variables depuis un template Jinja2 d'acte notarial.

Fonctionnalités:
- Parse un template Markdown/Jinja2
- Identifie toutes les variables {{ variable }}
- Identifie les blocs conditionnels {% if condition %}
- Génère un rapport des variables requises
- Compare avec le schéma JSON pour validation

Usage:
    python extraire_variables.py <chemin_template> [--schema <chemin_schema>] [--output <fichier_sortie>]

Exemple:
    python extraire_variables.py ../templates/vente_lots_copropriete.md --schema ../schemas/variables_vente.json
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict


def extraire_variables_jinja(contenu: str) -> Set[str]:
    """
    Extrait toutes les variables Jinja2 du template.

    Patterns reconnus:
    - {{ variable }}
    - {{ objet.propriete }}
    - {{ objet.sous_objet.propriete }}
    - {{ variable|filtre }}

    Args:
        contenu: Contenu du template

    Returns:
        Set de chemins de variables uniques
    """
    # Pattern pour les variables Jinja2
    pattern_variable = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*(?:\|[^}]*)?\}\}'

    variables = set()
    matches = re.findall(pattern_variable, contenu)

    for match in matches:
        # Nettoyer la variable (enlever les filtres potentiels)
        variable = match.split('|')[0].strip()
        variables.add(variable)

    return variables


def extraire_boucles_for(contenu: str) -> List[Dict[str, Any]]:
    """
    Extrait les boucles for et leurs variables d'itération.

    Pattern: {% for item in collection %}

    Args:
        contenu: Contenu du template

    Returns:
        Liste de dictionnaires avec variable_iteration, collection, ligne
    """
    pattern_for = r'\{%\s*for\s+(\w+)\s+in\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*%\}'

    boucles = []
    for match in re.finditer(pattern_for, contenu):
        ligne = contenu[:match.start()].count('\n') + 1
        boucles.append({
            'variable_iteration': match.group(1),
            'collection': match.group(2),
            'ligne': ligne
        })

    return boucles


def extraire_conditions(contenu: str) -> List[Dict[str, Any]]:
    """
    Extrait les blocs conditionnels if.

    Patterns:
    - {% if condition %}
    - {% elif condition %}

    Args:
        contenu: Contenu du template

    Returns:
        Liste de dictionnaires avec condition, variables_utilisees, ligne
    """
    pattern_if = r'\{%\s*(if|elif)\s+(.+?)\s*%\}'

    conditions = []
    for match in re.finditer(pattern_if, contenu):
        condition = match.group(2)
        ligne = contenu[:match.start()].count('\n') + 1

        # Extraire les variables de la condition
        variables = set()
        # Pattern pour variables dans conditions
        var_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        for var_match in re.finditer(var_pattern, condition):
            var = var_match.group(1)
            # Exclure les mots-clés Python/Jinja
            mots_cles = {'true', 'false', 'True', 'False', 'none', 'None', 'and', 'or', 'not', 'in', 'is', 'if', 'else', 'elif'}
            if var not in mots_cles and not var.isdigit():
                variables.add(var)

        conditions.append({
            'type': match.group(1),
            'condition': condition,
            'variables_utilisees': list(variables),
            'ligne': ligne
        })

    return conditions


def extraire_includes(contenu: str) -> List[Dict[str, str]]:
    """
    Extrait les directives include.

    Pattern: {% include 'chemin/fichier.md' %}

    Args:
        contenu: Contenu du template

    Returns:
        Liste de chemins de fichiers inclus
    """
    pattern_include = r"\{%\s*include\s+['\"](.+?)['\"]\s*%\}"

    includes = []
    for match in re.finditer(pattern_include, contenu):
        ligne = contenu[:match.start()].count('\n') + 1
        includes.append({
            'fichier': match.group(1),
            'ligne': ligne
        })

    return includes


def extraire_sections_optionnelles(contenu: str) -> List[Dict[str, Any]]:
    """
    Extrait les marqueurs de sections optionnelles.

    Pattern: <!-- SECTION: nom_section | OPTIONNEL --> ou <!-- SECTION: nom | CONDITIONNEL: condition -->

    Args:
        contenu: Contenu du template

    Returns:
        Liste de sections avec nom, type, condition
    """
    pattern_section = r'<!--\s*SECTION:\s*(\w+)\s*\|\s*(OPTIONNEL|CONDITIONNEL)(?::\s*(.+?))?\s*-->'

    sections = []
    for match in re.finditer(pattern_section, contenu):
        ligne = contenu[:match.start()].count('\n') + 1
        sections.append({
            'nom': match.group(1),
            'type': match.group(2).lower(),
            'condition': match.group(3) if match.group(3) else None,
            'ligne': ligne
        })

    return sections


def construire_arbre_variables(variables: Set[str]) -> Dict:
    """
    Construit une structure arborescente des variables.

    Exemple:
        {"vendeurs.nom", "vendeurs.prenom", "prix.montant"}
        ->
        {
            "vendeurs": {"nom": {}, "prenom": {}},
            "prix": {"montant": {}}
        }

    Args:
        variables: Set de chemins de variables

    Returns:
        Dictionnaire arborescent
    """
    arbre = {}

    for var in sorted(variables):
        parties = var.split('.')
        noeud = arbre
        for partie in parties:
            if partie not in noeud:
                noeud[partie] = {}
            noeud = noeud[partie]

    return arbre


def comparer_avec_schema(variables: Set[str], chemin_schema: Path) -> Dict[str, List[str]]:
    """
    Compare les variables extraites avec le schéma JSON.

    Args:
        variables: Set de variables extraites
        chemin_schema: Chemin vers le fichier de schéma JSON

    Returns:
        Dictionnaire avec variables_manquantes, variables_non_declarees
    """
    with open(chemin_schema, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    # Extraire toutes les propriétés du schéma
    def extraire_proprietes_schema(obj: Dict, prefixe: str = '') -> Set[str]:
        proprietes = set()

        if 'properties' in obj:
            for nom, prop in obj['properties'].items():
                chemin = f"{prefixe}.{nom}" if prefixe else nom
                proprietes.add(chemin)
                proprietes.update(extraire_proprietes_schema(prop, chemin))

        if 'items' in obj:
            proprietes.update(extraire_proprietes_schema(obj['items'], prefixe))

        if '$ref' in obj:
            ref_path = obj['$ref'].split('/')[-1]
            if '$defs' in schema and ref_path in schema['$defs']:
                proprietes.update(extraire_proprietes_schema(schema['$defs'][ref_path], prefixe))

        return proprietes

    proprietes_schema = extraire_proprietes_schema(schema)

    # Normaliser les variables (enlever les index de boucle)
    variables_normalisees = set()
    for var in variables:
        # Remplacer les accès par index (ex: vendeurs[0]) par le chemin simple
        var_norm = re.sub(r'\[\d+\]', '', var)
        variables_normalisees.add(var_norm)

    # Comparer
    variables_manquantes = []
    variables_non_declarees = []

    # Variables dans le template mais pas dans le schéma
    for var in variables_normalisees:
        # Vérifier si la variable ou un de ses parents est dans le schéma
        parties = var.split('.')
        trouve = False
        for i in range(len(parties)):
            chemin_partiel = '.'.join(parties[:i+1])
            if chemin_partiel in proprietes_schema:
                trouve = True
                break
        if not trouve and not var.startswith('loop.'):  # Ignorer les variables de boucle Jinja
            variables_non_declarees.append(var)

    return {
        'variables_non_declarees': sorted(variables_non_declarees),
        'proprietes_schema': sorted(list(proprietes_schema))
    }


def generer_rapport(chemin_template: Path, chemin_schema: Path = None) -> Dict:
    """
    Génère un rapport complet d'analyse du template.

    Args:
        chemin_template: Chemin vers le fichier template
        chemin_schema: Chemin optionnel vers le schéma JSON

    Returns:
        Dictionnaire contenant l'analyse complète
    """
    with open(chemin_template, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Extraction
    variables = extraire_variables_jinja(contenu)
    boucles = extraire_boucles_for(contenu)
    conditions = extraire_conditions(contenu)
    includes = extraire_includes(contenu)
    sections = extraire_sections_optionnelles(contenu)

    # Construire l'arbre
    arbre = construire_arbre_variables(variables)

    # Rapport
    rapport = {
        'fichier': str(chemin_template),
        'statistiques': {
            'nombre_variables': len(variables),
            'nombre_boucles': len(boucles),
            'nombre_conditions': len(conditions),
            'nombre_includes': len(includes),
            'nombre_sections_optionnelles': len(sections)
        },
        'variables': sorted(list(variables)),
        'arbre_variables': arbre,
        'boucles': boucles,
        'conditions': conditions,
        'includes': includes,
        'sections_optionnelles': sections
    }

    # Comparaison avec schéma si fourni
    if chemin_schema and chemin_schema.exists():
        rapport['comparaison_schema'] = comparer_avec_schema(variables, chemin_schema)

    return rapport


def afficher_rapport(rapport: Dict, verbose: bool = False):
    """
    Affiche le rapport de manière formatée.

    Args:
        rapport: Dictionnaire du rapport
        verbose: Afficher tous les détails
    """
    print("=" * 60)
    print(f"ANALYSE DU TEMPLATE: {rapport['fichier']}")
    print("=" * 60)

    stats = rapport['statistiques']
    print(f"\n📊 STATISTIQUES:")
    print(f"   - Variables: {stats['nombre_variables']}")
    print(f"   - Boucles for: {stats['nombre_boucles']}")
    print(f"   - Conditions if: {stats['nombre_conditions']}")
    print(f"   - Fichiers inclus: {stats['nombre_includes']}")
    print(f"   - Sections optionnelles: {stats['nombre_sections_optionnelles']}")

    print(f"\n📁 STRUCTURE DES VARIABLES:")

    def afficher_arbre(arbre: Dict, niveau: int = 0):
        for cle, sous_arbre in sorted(arbre.items()):
            print("   " * niveau + f"├── {cle}")
            if sous_arbre:
                afficher_arbre(sous_arbre, niveau + 1)

    afficher_arbre(rapport['arbre_variables'])

    if rapport['boucles']:
        print(f"\n🔄 BOUCLES:")
        for boucle in rapport['boucles']:
            print(f"   - for {boucle['variable_iteration']} in {boucle['collection']} (ligne {boucle['ligne']})")

    if rapport['sections_optionnelles']:
        print(f"\n📑 SECTIONS OPTIONNELLES:")
        for section in rapport['sections_optionnelles']:
            condition = f" → {section['condition']}" if section['condition'] else ""
            print(f"   - {section['nom']} ({section['type']}{condition}) (ligne {section['ligne']})")

    if rapport['includes']:
        print(f"\n📎 FICHIERS INCLUS:")
        for inc in rapport['includes']:
            print(f"   - {inc['fichier']} (ligne {inc['ligne']})")

    if 'comparaison_schema' in rapport:
        comp = rapport['comparaison_schema']
        if comp['variables_non_declarees']:
            print(f"\n⚠️ VARIABLES NON DÉCLARÉES DANS LE SCHÉMA:")
            for var in comp['variables_non_declarees']:
                print(f"   - {var}")

    if verbose:
        print(f"\n📋 LISTE COMPLÈTE DES VARIABLES:")
        for var in rapport['variables']:
            print(f"   - {var}")


def main():
    parser = argparse.ArgumentParser(
        description="Extrait les variables d'un template Jinja2 d'acte notarial"
    )
    parser.add_argument(
        'template',
        type=Path,
        help="Chemin vers le fichier template"
    )
    parser.add_argument(
        '--schema',
        type=Path,
        help="Chemin vers le schéma JSON pour validation"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help="Fichier de sortie JSON"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Afficher tous les détails"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Sortie au format JSON uniquement"
    )

    args = parser.parse_args()

    if not args.template.exists():
        print(f"❌ Erreur: Le fichier {args.template} n'existe pas")
        return 1

    rapport = generer_rapport(args.template, args.schema)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, ensure_ascii=False, indent=2)
        print(f"✅ Rapport sauvegardé dans {args.output}")

    if args.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=2))
    else:
        afficher_rapport(rapport, args.verbose)

    return 0


if __name__ == '__main__':
    exit(main())
