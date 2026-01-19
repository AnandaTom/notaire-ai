#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detecter_type_acte.py
---------------------
Détecte automatiquement le type d'acte notarié en fonction
des données fournies.

Analyse les clés et structures présentes pour déterminer
s'il s'agit d'une vente, promesse, règlement de copropriété
ou modificatif EDD.

Usage:
    python detecter_type_acte.py --data donnees.json
    python detecter_type_acte.py --data donnees.json --verbose
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    # Fallback si rich n'est pas disponible
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    console = Console()

console = Console()

# Configuration des signatures de types d'actes
SIGNATURES_ACTES = {
    "vente_lots_copropriete": {
        "cles_obligatoires": ["vendeurs", "acquereurs", "prix"],
        "cles_caracteristiques": ["bien", "financement", "conditions_suspensives"],
        "cles_absentes": ["syndicat_demandeur", "assemblee_generale", "requerant"],
        "poids": 1.0
    },
    "promesse_vente": {
        "cles_obligatoires": ["vendeurs", "acquereurs"],
        "cles_caracteristiques": ["conditions_suspensives", "delai_realisation", "indemnite_immobilisation"],
        "cles_absentes": ["syndicat_demandeur", "requerant"],
        "poids": 1.0
    },
    "reglement_copropriete": {
        "cles_obligatoires": ["requerant", "lots", "parties_communes"],
        "cles_caracteristiques": ["parties_privatives", "syndic", "conseil_syndical", "charges"],
        "cles_absentes": ["vendeurs", "acquereurs", "syndicat_demandeur", "assemblee_generale"],
        "poids": 1.0
    },
    "modificatif_edd": {
        "cles_obligatoires": ["syndicat_demandeur", "assemblee_generale"],
        "cles_caracteristiques": ["modifications", "edd_origine", "historique_modificatifs", "syndic"],
        "cles_absentes": ["vendeurs", "acquereurs", "requerant"],
        "poids": 1.0
    }
}

# Mappage vers les templates
TEMPLATES = {
    "vente_lots_copropriete": "vente_lots_copropriete.md",
    "promesse_vente": "promesse_vente_lots_copropriete.md",
    "reglement_copropriete": "reglement_copropriete_edd.md",
    "modificatif_edd": "modificatif_edd.md"
}

# Mappage vers les schémas de validation
SCHEMAS = {
    "vente_lots_copropriete": "variables_vente.json",
    "promesse_vente": "variables_promesse.json",
    "reglement_copropriete": "variables_reglement_copropriete.json",
    "modificatif_edd": "variables_modificatif_edd.json"
}


def extraire_cles_recursif(data: Dict, prefix: str = "") -> List[str]:
    """
    Extrait récursivement toutes les clés d'un dictionnaire.
    Retourne les clés au format "parent.enfant.sous_enfant".
    """
    cles = []

    if not isinstance(data, dict):
        return cles

    for key, value in data.items():
        cle_complete = f"{prefix}.{key}" if prefix else key
        cles.append(cle_complete)

        if isinstance(value, dict):
            cles.extend(extraire_cles_recursif(value, cle_complete))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            cles.extend(extraire_cles_recursif(value[0], f"{cle_complete}[]"))

    return cles


def calculer_score_type(data: Dict, type_acte: str, signature: Dict, verbose: bool = False) -> Tuple[float, Dict]:
    """
    Calcule un score de correspondance entre les données et un type d'acte.
    Retourne le score et les détails du calcul.
    """
    score = 0.0
    details = {
        "cles_obligatoires_presentes": [],
        "cles_obligatoires_manquantes": [],
        "cles_caracteristiques_presentes": [],
        "cles_absentes_presentes": []
    }

    cles_data = set(data.keys())

    # Vérification des clés obligatoires (poids élevé)
    for cle in signature["cles_obligatoires"]:
        if cle in cles_data:
            score += 30  # 30 points par clé obligatoire
            details["cles_obligatoires_presentes"].append(cle)
        else:
            details["cles_obligatoires_manquantes"].append(cle)

    # Vérification des clés caractéristiques (poids moyen)
    for cle in signature["cles_caracteristiques"]:
        if cle in cles_data:
            score += 10  # 10 points par clé caractéristique
            details["cles_caracteristiques_presentes"].append(cle)

    # Vérification des clés qui devraient être absentes (pénalité)
    for cle in signature["cles_absentes"]:
        if cle in cles_data:
            score -= 20  # -20 points si une clé "interdite" est présente
            details["cles_absentes_presentes"].append(cle)

    # Bonus si toutes les clés obligatoires sont présentes
    if not details["cles_obligatoires_manquantes"]:
        score += 20

    # Applique le poids du type
    score *= signature["poids"]

    return score, details


def detecter_type_acte(data: Dict, verbose: bool = False) -> Tuple[str, float, Dict]:
    """
    Détecte le type d'acte en fonction des données fournies.

    Retourne:
        - Le type d'acte détecté
        - Le score de confiance (0-100)
        - Les détails de l'analyse
    """
    scores = {}
    details_complets = {}

    for type_acte, signature in SIGNATURES_ACTES.items():
        score, details = calculer_score_type(data, type_acte, signature, verbose)
        scores[type_acte] = score
        details_complets[type_acte] = details

    # Trouve le meilleur score
    meilleur_type = max(scores, key=scores.get)
    meilleur_score = scores[meilleur_type]

    # Normalise le score en pourcentage (basé sur un score max théorique)
    score_max_theorique = 30 * 3 + 10 * 4 + 20  # 3 obligatoires + 4 caractéristiques + bonus
    confiance = min(100, max(0, (meilleur_score / score_max_theorique) * 100))

    # Vérifie si la détection est fiable
    second_meilleur = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
    if meilleur_score - second_meilleur < 20:
        confiance *= 0.8  # Réduit la confiance si les scores sont proches

    return meilleur_type, confiance, {
        "scores": scores,
        "details": details_complets,
        "template": TEMPLATES.get(meilleur_type),
        "schema": SCHEMAS.get(meilleur_type)
    }


def detecter_sous_type(data: Dict, type_principal: str) -> str:
    """
    Détecte un sous-type plus précis si applicable.
    """
    if type_principal == "reglement_copropriete":
        acte_type = data.get("acte", {}).get("type", "")
        if acte_type == "edd_seul":
            return "edd_seul"
        elif acte_type == "reglement_seul":
            return "reglement_seul"
        return "edd_reglement_initial"

    elif type_principal == "modificatif_edd":
        modifications = data.get("modifications", [])
        types_modif = [m.get("type") for m in modifications if isinstance(m, dict)]

        if "creation_pcs" in types_modif:
            return "creation_parties_communes_speciales"
        elif "reunion_lots" in types_modif:
            return "reunion_lots"
        elif "suppression_lot" in types_modif and "creation_lot" in types_modif:
            return "division_lot"
        return "modification_generale"

    elif type_principal == "vente_lots_copropriete":
        lots = data.get("bien", {}).get("lots", data.get("lots", []))
        if len(lots) > 1:
            return "vente_plusieurs_lots"
        return "vente_lot_unique"

    return type_principal


def afficher_resultat(type_acte: str, confiance: float, analyse: Dict, verbose: bool = False) -> None:
    """Affiche le résultat de la détection de manière formatée."""

    couleur = "green" if confiance >= 80 else "yellow" if confiance >= 60 else "red"

    console.print()
    console.print(Panel(
        f"[bold {couleur}]Type détecté: {type_acte.replace('_', ' ').title()}[/bold {couleur}]\n\n"
        f"Confiance: {confiance:.1f}%\n"
        f"Template: {analyse.get('template', 'Non défini')}\n"
        f"Schéma: {analyse.get('schema', 'Non défini')}",
        title="DÉTECTION AUTOMATIQUE",
        border_style=couleur
    ))

    if verbose:
        # Affiche les scores de tous les types
        console.print()
        table = Table(title="Scores par type d'acte")
        table.add_column("Type", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Clés obligatoires", justify="center")
        table.add_column("Clés caractéristiques", justify="center")

        for t, score in sorted(analyse["scores"].items(), key=lambda x: x[1], reverse=True):
            details = analyse["details"][t]
            nb_oblig = len(details["cles_obligatoires_presentes"])
            total_oblig = nb_oblig + len(details["cles_obligatoires_manquantes"])
            nb_carac = len(details["cles_caracteristiques_presentes"])

            table.add_row(
                t.replace("_", " "),
                f"{score:.0f}",
                f"{nb_oblig}/{total_oblig}",
                str(nb_carac)
            )

        console.print(table)

        # Détails du type détecté
        details_type = analyse["details"][type_acte]

        if details_type["cles_obligatoires_manquantes"]:
            console.print()
            console.print("[yellow]Clés obligatoires manquantes:[/yellow]")
            for cle in details_type["cles_obligatoires_manquantes"]:
                console.print(f"  [red]✗[/red] {cle}")

        if details_type["cles_absentes_presentes"]:
            console.print()
            console.print("[yellow]Clés inattendues présentes:[/yellow]")
            for cle in details_type["cles_absentes_presentes"]:
                console.print(f"  [yellow]?[/yellow] {cle}")


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Détecte automatiquement le type d'acte notarié",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python detecter_type_acte.py --data donnees.json
  python detecter_type_acte.py --data donnees.json --verbose
  python detecter_type_acte.py --data donnees.json --json
        """
    )

    parser.add_argument(
        "--data", "-d",
        required=True,
        type=str,
        help="Fichier JSON contenant les données de l'acte"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Affiche les détails de l'analyse"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie en format JSON"
    )

    args = parser.parse_args()

    # Charge les données
    data_path = Path(args.data)
    if not data_path.exists():
        console.print(f"[red]Fichier non trouvé: {data_path}[/red]")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Détection
    type_acte, confiance, analyse = detecter_type_acte(data, args.verbose)

    # Détection du sous-type
    sous_type = detecter_sous_type(data, type_acte)

    # Sortie
    if args.json:
        resultat = {
            "type_acte": type_acte,
            "sous_type": sous_type,
            "confiance": round(confiance, 1),
            "template": analyse.get("template"),
            "schema": analyse.get("schema"),
            "scores": {k: round(v, 1) for k, v in analyse["scores"].items()}
        }
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
    else:
        afficher_resultat(type_acte, confiance, analyse, args.verbose)
        if sous_type != type_acte:
            console.print(f"\n[dim]Sous-type: {sous_type.replace('_', ' ')}[/dim]")

    # Code de retour
    if confiance < 50:
        sys.exit(1)  # Détection peu fiable

    sys.exit(0)


if __name__ == "__main__":
    main()
