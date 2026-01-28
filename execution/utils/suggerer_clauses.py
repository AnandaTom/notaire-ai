#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
suggerer_clauses.py
-------------------
Analyse les données d'un acte notarié et suggère les clauses
pertinentes en fonction du contexte.

Utilise le catalogue de clauses et des règles métier pour
recommander les clauses obligatoires et optionnelles.

Usage:
    python suggerer_clauses.py --data donnees.json --type promesse_vente
    python suggerer_clauses.py --data donnees.json --type vente --verbose
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    console = Console()

console = Console()

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
CATALOGUE_PATH = SCHEMAS_DIR / "clauses_catalogue.json"


@dataclass
class SuggestionClause:
    """Représente une suggestion de clause."""
    clause_id: str
    nom: str
    categorie: str
    priorite: str  # "obligatoire", "recommandee", "optionnelle"
    raison: str
    texte: str
    variables_manquantes: List[str] = field(default_factory=list)


def charger_catalogue() -> Dict:
    """Charge le catalogue de clauses."""
    if not CATALOGUE_PATH.exists():
        console.print(f"[red]Catalogue non trouvé: {CATALOGUE_PATH}[/red]")
        sys.exit(1)

    with open(CATALOGUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def obtenir_valeur_profonde(data: Dict, chemin: str, default: Any = None) -> Any:
    """
    Obtient une valeur profonde dans un dictionnaire.
    Supporte la notation pointée: "objet.sous_objet.valeur"
    """
    parties = chemin.split(".")
    current = data

    for partie in parties:
        if isinstance(current, dict) and partie in current:
            current = current[partie]
        elif isinstance(current, list):
            # Gère les tableaux (retourne le premier élément si existe)
            if current and isinstance(current[0], dict) and partie in current[0]:
                current = current[0][partie]
            else:
                return default
        else:
            return default

    return current


def evaluer_condition(condition: str, data: Dict) -> bool:
    """
    Évalue une condition d'application de clause.
    Supporte les formats:
    - "variable == 'valeur'"
    - "variable == true/false"
    - "variable in ['a', 'b']"
    - "variable | length > 1"
    """
    if not condition:
        return True

    try:
        # Condition simple d'égalité
        match_eq = re.match(r"([\w.]+)\s*==\s*['\"]?(\w+)['\"]?", condition)
        if match_eq:
            variable, valeur = match_eq.groups()
            valeur_actuelle = obtenir_valeur_profonde(data, variable)

            if valeur.lower() == "true":
                return valeur_actuelle is True
            elif valeur.lower() == "false":
                return valeur_actuelle is False
            else:
                return str(valeur_actuelle).lower() == valeur.lower()

        # Condition "in" pour liste
        match_in = re.match(r"([\w.]+)\s+in\s+\[([^\]]+)\]", condition)
        if match_in:
            variable, valeurs = match_in.groups()
            valeur_actuelle = obtenir_valeur_profonde(data, variable)
            liste_valeurs = [v.strip().strip("'\"") for v in valeurs.split(",")]
            return str(valeur_actuelle) in liste_valeurs

        # Condition de longueur
        match_len = re.match(r"([\w.]+)\s*\|\s*length\s*([><=]+)\s*(\d+)", condition)
        if match_len:
            variable, operateur, seuil = match_len.groups()
            valeur_actuelle = obtenir_valeur_profonde(data, variable, [])
            longueur = len(valeur_actuelle) if isinstance(valeur_actuelle, (list, dict, str)) else 0

            if operateur == ">":
                return longueur > int(seuil)
            elif operateur == ">=":
                return longueur >= int(seuil)
            elif operateur == "<":
                return longueur < int(seuil)
            elif operateur == "<=":
                return longueur <= int(seuil)
            elif operateur == "==":
                return longueur == int(seuil)

    except Exception as e:
        console.print(f"[dim]Erreur évaluation condition '{condition}': {e}[/dim]")

    return False


def extraire_variables_clause(texte: str) -> List[str]:
    """Extrait les variables Jinja2 d'un texte de clause."""
    # Pattern pour {{ variable }} et {{ variable | filtre }}
    pattern = r'\{\{\s*([\w.]+)'
    return list(set(re.findall(pattern, texte)))


def verifier_variables_disponibles(variables: List[str], data: Dict) -> Tuple[List[str], List[str]]:
    """
    Vérifie quelles variables sont disponibles dans les données.
    Retourne (présentes, manquantes).
    """
    presentes = []
    manquantes = []

    for var in variables:
        valeur = obtenir_valeur_profonde(data, var)
        if valeur is not None:
            presentes.append(var)
        else:
            manquantes.append(var)

    return presentes, manquantes


def analyser_contexte(data: Dict) -> Dict[str, Any]:
    """
    Analyse les données pour extraire le contexte de l'acte.
    Retourne un dictionnaire de caractéristiques détectées.
    """
    contexte = {
        "type_acte": data.get("acte", {}).get("type", ""),
        "caracteristiques": []
    }

    # Détection bien loué
    occupation = obtenir_valeur_profonde(data, "bien.occupation_actuelle.statut")
    if occupation in ["loue_nu", "loue_meuble"]:
        contexte["caracteristiques"].append("bien_loue")
        contexte["bien_loue"] = True

    # Détection prêt
    if obtenir_valeur_profonde(data, "financement.type") == "pret":
        contexte["caracteristiques"].append("financement_pret")
        contexte["financement_pret"] = True

    # Détection PTZ
    if obtenir_valeur_profonde(data, "financement.ptz"):
        contexte["caracteristiques"].append("financement_ptz")

    # Détection zone DPU
    if obtenir_valeur_profonde(data, "urbanisme.droit_preemption.applicable") is True:
        contexte["caracteristiques"].append("zone_dpu")
        contexte["zone_dpu"] = True

    # Détection DPE passoire
    classe_dpe = obtenir_valeur_profonde(data, "diagnostics.dpe.classe_energie")
    if classe_dpe in ["F", "G"]:
        contexte["caracteristiques"].append("dpe_passoire")
        contexte["dpe_passoire"] = True

    # Détection amiante
    if obtenir_valeur_profonde(data, "diagnostics.amiante.presence") is True:
        contexte["caracteristiques"].append("presence_amiante")

    # Détection emprunt collectif copropriété
    if obtenir_valeur_profonde(data, "copropriete.emprunt_collectif.existe") is True:
        contexte["caracteristiques"].append("emprunt_collectif")
        contexte["emprunt_collectif"] = True

    # Détection plusieurs acquéreurs
    acquereurs = obtenir_valeur_profonde(data, "acquereurs", [])
    if isinstance(acquereurs, list) and len(acquereurs) > 1:
        contexte["caracteristiques"].append("plusieurs_acquereurs")
        contexte["plusieurs_acquereurs"] = True

    # Détection vendeur non professionnel
    vendeurs = obtenir_valeur_profonde(data, "vendeurs", [])
    if vendeurs:
        vendeur = vendeurs[0] if isinstance(vendeurs, list) else vendeurs
        if vendeur.get("type") == "personne_physique":
            contexte["caracteristiques"].append("vendeur_particulier")
            contexte["vendeur_non_professionnel"] = True

    # Détection régime fiscal Pinel
    if obtenir_valeur_profonde(data, "fiscalite.regime_fiscal") == "pinel":
        contexte["caracteristiques"].append("regime_pinel")

    # Détection résidence principale
    if obtenir_valeur_profonde(data, "fiscalite.plus_value.motif_exoneration") == "residence_principale":
        contexte["caracteristiques"].append("residence_principale")

    # Détection hypothèques existantes
    hypotheques = obtenir_valeur_profonde(data, "bien.hypotheques", [])
    if hypotheques:
        contexte["caracteristiques"].append("hypotheques_existantes")

    # Situation matrimoniale
    for partie in ["vendeurs", "acquereurs"]:
        personnes = obtenir_valeur_profonde(data, partie, [])
        if isinstance(personnes, list):
            for p in personnes:
                if p.get("type") == "personne_physique":
                    situation = obtenir_valeur_profonde(p, "personne_physique.situation_matrimoniale.statut")
                    if situation == "marie":
                        regime = obtenir_valeur_profonde(p, "personne_physique.situation_matrimoniale.regime_matrimonial")
                        if regime and "communauté" in regime.lower():
                            contexte["caracteristiques"].append(f"{partie[:-1]}_communaute")

    return contexte


def suggerer_clauses(data: Dict, type_acte: str, verbose: bool = False) -> List[SuggestionClause]:
    """
    Analyse les données et suggère les clauses pertinentes.
    """
    catalogue = charger_catalogue()
    contexte = analyser_contexte(data)
    suggestions = []

    if verbose:
        console.print(f"[dim]Contexte détecté: {contexte['caracteristiques']}[/dim]")

    # Parcours du catalogue
    for categorie_id, categorie in catalogue.get("categories", {}).items():
        clauses = categorie.get("clauses", [])

        for clause in clauses:
            clause_id = clause.get("id", "")
            types_actes = clause.get("type_acte", [])

            # Vérifie si la clause s'applique au type d'acte
            if type_acte not in types_actes and types_actes:
                continue

            # Vérifie la condition d'application
            condition = clause.get("condition_application", "")
            condition_remplie = evaluer_condition(condition, data) if condition else True

            # Détermine la priorité
            est_obligatoire = clause.get("obligatoire", False)

            if est_obligatoire and condition_remplie:
                priorite = "obligatoire"
                raison = "Clause obligatoire pour ce type d'acte"
            elif condition_remplie and condition:
                priorite = "recommandee"
                raison = f"Condition remplie: {condition}"
            elif est_obligatoire and not condition_remplie:
                continue  # Pas applicable
            else:
                # Vérifie si le contexte suggère cette clause
                suggestion_contexte = _clause_pertinente_pour_contexte(clause_id, contexte)
                if suggestion_contexte:
                    priorite = "recommandee"
                    raison = suggestion_contexte
                else:
                    priorite = "optionnelle"
                    raison = "Clause disponible pour ce type d'acte"

            # Vérifie les variables disponibles
            texte = clause.get("texte", "")
            variables_requises = clause.get("variables_requises", [])
            _, manquantes = verifier_variables_disponibles(variables_requises, data)

            # Crée la suggestion
            suggestion = SuggestionClause(
                clause_id=clause_id,
                nom=clause.get("nom", ""),
                categorie=categorie_id,
                priorite=priorite,
                raison=raison,
                texte=texte[:200] + "..." if len(texte) > 200 else texte,
                variables_manquantes=manquantes
            )

            # N'ajoute que si obligatoire/recommandée ou si demandé
            if priorite in ["obligatoire", "recommandee"]:
                suggestions.append(suggestion)

    # Tri par priorité
    ordre_priorite = {"obligatoire": 0, "recommandee": 1, "optionnelle": 2}
    suggestions.sort(key=lambda s: ordre_priorite.get(s.priorite, 3))

    return suggestions


def _clause_pertinente_pour_contexte(clause_id: str, contexte: Dict) -> Optional[str]:
    """
    Vérifie si une clause est pertinente pour le contexte détecté.
    Retourne la raison si oui, None sinon.
    """
    mapping = {
        "cs_pret_standard": ("financement_pret", "Financement par prêt détecté"),
        "cs_pret_ptz": ("financement_ptz", "PTZ détecté"),
        "cs_preemption_urbain": ("zone_dpu", "Bien en zone DPU"),
        "cs_preemption_locataire": ("bien_loue", "Bien actuellement loué"),
        "dpe_passoire": ("dpe_passoire", "DPE classe F ou G"),
        "emprunt_collectif": ("emprunt_collectif", "Emprunt collectif copropriété"),
        "solidarite": ("plusieurs_acquereurs", "Plusieurs acquéreurs"),
        "garantie_vices_caches_exclusion": ("vendeur_non_professionnel", "Vendeur particulier"),
        "regime_fiscal_pinel": ("regime_pinel", "Bien sous régime Pinel"),
        "plus_value_exoneration_rp": ("residence_principale", "Résidence principale du vendeur"),
    }

    for caracteristique in contexte.get("caracteristiques", []):
        if clause_id in mapping and mapping[clause_id][0] == caracteristique:
            return mapping[clause_id][1]

    return None


def generer_alertes(data: Dict, contexte: Dict) -> List[str]:
    """
    Génère des alertes basées sur l'analyse du dossier.
    """
    alertes = []

    # Alerte DPE passoire
    if "dpe_passoire" in contexte.get("caracteristiques", []):
        classe = obtenir_valeur_profonde(data, "diagnostics.dpe.classe_energie")
        alertes.append(f"⚠️ PASSOIRE ÉNERGÉTIQUE: Le bien est classé {classe}. "
                      "Informer l'acquéreur des restrictions de location à venir.")

    # Alerte emprunt collectif
    if "emprunt_collectif" in contexte.get("caracteristiques", []):
        alertes.append("⚠️ EMPRUNT COLLECTIF: Le syndicat a souscrit un emprunt. "
                      "L'acquéreur reprendra les annuités restantes.")

    # Alerte régime Pinel
    if "regime_pinel" in contexte.get("caracteristiques", []):
        alertes.append("⚠️ RÉGIME PINEL: Vérifier que l'engagement de location est terminé "
                      "pour éviter la reprise de l'avantage fiscal.")

    # Alerte amiante
    if "presence_amiante" in contexte.get("caracteristiques", []):
        alertes.append("⚠️ AMIANTE DÉTECTÉ: Vérifier si des travaux sont recommandés "
                      "et informer l'acquéreur de ses obligations.")

    # Alerte vendeur marié sans intervention conjoint
    vendeurs = obtenir_valeur_profonde(data, "vendeurs", [])
    if isinstance(vendeurs, list):
        for vendeur in vendeurs:
            if vendeur.get("type") == "personne_physique":
                situation = obtenir_valeur_profonde(vendeur, "personne_physique.situation_matrimoniale")
                if situation and situation.get("statut") == "marie":
                    regime = situation.get("regime_matrimonial", "")
                    if "communauté" in regime.lower():
                        conjoint = situation.get("conjoint")
                        if not conjoint:
                            alertes.append("⚠️ RÉGIME COMMUNAUTAIRE: Le vendeur est marié sous "
                                         "un régime de communauté. L'intervention du conjoint est nécessaire.")

    return alertes


def afficher_suggestions(suggestions: List[SuggestionClause], alertes: List[str], verbose: bool = False) -> None:
    """Affiche les suggestions de manière formatée."""

    # Alertes
    if alertes:
        console.print()
        console.print(Panel(
            "\n".join(alertes),
            title="[bold red]ALERTES[/bold red]",
            border_style="red"
        ))

    # Clauses obligatoires
    obligatoires = [s for s in suggestions if s.priorite == "obligatoire"]
    if obligatoires:
        console.print()
        console.print("[bold green]CLAUSES OBLIGATOIRES[/bold green]")

        table = Table(show_header=True)
        table.add_column("Clause", style="green")
        table.add_column("Catégorie", style="cyan")
        table.add_column("Variables manquantes", style="yellow")

        for s in obligatoires:
            manquantes = ", ".join(s.variables_manquantes) if s.variables_manquantes else "-"
            table.add_row(s.nom, s.categorie, manquantes)

        console.print(table)

    # Clauses recommandées
    recommandees = [s for s in suggestions if s.priorite == "recommandee"]
    if recommandees:
        console.print()
        console.print("[bold yellow]CLAUSES RECOMMANDÉES[/bold yellow]")

        table = Table(show_header=True)
        table.add_column("Clause", style="yellow")
        table.add_column("Raison")
        table.add_column("Variables manquantes", style="dim")

        for s in recommandees:
            manquantes = ", ".join(s.variables_manquantes) if s.variables_manquantes else "-"
            table.add_row(s.nom, s.raison, manquantes)

        console.print(table)

    if not suggestions:
        console.print("[dim]Aucune clause suggérée pour ce dossier.[/dim]")

    # Résumé
    console.print()
    console.print(Panel(
        f"[bold]Résumé:[/bold]\n"
        f"• Clauses obligatoires: {len(obligatoires)}\n"
        f"• Clauses recommandées: {len(recommandees)}\n"
        f"• Alertes: {len(alertes)}",
        border_style="blue"
    ))


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Suggère les clauses pertinentes pour un acte notarié",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python suggerer_clauses.py --data donnees.json --type promesse_vente
  python suggerer_clauses.py --data donnees.json --type vente --verbose
  python suggerer_clauses.py --data donnees.json --type vente --json
        """
    )

    parser.add_argument(
        "--data", "-d",
        required=True,
        type=str,
        help="Fichier JSON contenant les données de l'acte"
    )

    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["vente", "promesse_vente", "compromis", "reglement", "modificatif"],
        help="Type d'acte"
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

    # Analyse
    contexte = analyser_contexte(data)
    suggestions = suggerer_clauses(data, args.type, args.verbose)
    alertes = generer_alertes(data, contexte)

    # Sortie
    if args.json:
        resultat = {
            "type_acte": args.type,
            "contexte": contexte,
            "alertes": alertes,
            "suggestions": [
                {
                    "id": s.clause_id,
                    "nom": s.nom,
                    "categorie": s.categorie,
                    "priorite": s.priorite,
                    "raison": s.raison,
                    "variables_manquantes": s.variables_manquantes
                }
                for s in suggestions
            ]
        }
        import sys
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
    else:
        console.print()
        console.print(Panel(
            f"[bold white]ANALYSE DES CLAUSES[/bold white]\n\n"
            f"Type d'acte: [cyan]{args.type}[/cyan]\n"
            f"Fichier: [dim]{data_path.name}[/dim]",
            border_style="blue"
        ))

        afficher_suggestions(suggestions, alertes, args.verbose)


if __name__ == "__main__":
    main()
