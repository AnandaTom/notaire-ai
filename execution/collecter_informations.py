#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collecter_informations.py
-------------------------
Interface CLI interactive pour la collecte guidée des informations
nécessaires à la génération d'actes notariés.

Utilise questionary et rich pour une interface utilisateur agréable.
Charge les questions depuis les fichiers schemas/questions_*.json
et génère un fichier JSON compatible avec assembler_acte.py.

Usage:
    python collecter_informations.py --type vente --output .tmp/collecte.json
    python collecter_informations.py --type reglement --resume .tmp/collecte_partielle.json
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import questionary
    from questionary import Style
except ImportError:
    print("Erreur: questionary n'est pas installé. Exécutez: pip install questionary")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
except ImportError:
    print("Erreur: rich n'est pas installé. Exécutez: pip install rich")
    sys.exit(1)

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
TMP_DIR = PROJECT_ROOT / ".tmp"

# Types d'actes supportés
TYPES_ACTES = {
    "vente": {
        "schema": "questions_vente.json",
        "titre": "Acte de Vente de Lots de Copropriété"
    },
    "promesse": {
        "schema": "questions_promesse.json",
        "titre": "Promesse de Vente"
    },
    "reglement": {
        "schema": "questions_reglement_copropriete.json",
        "titre": "État Descriptif de Division et Règlement de Copropriété"
    },
    "modificatif": {
        "schema": "questions_modificatif_edd.json",
        "titre": "Modificatif de l'État Descriptif de Division"
    }
}

# Style personnalisé pour questionary
STYLE = Style([
    ('question', 'bold'),
    ('answer', 'fg:green bold'),
    ('pointer', 'fg:yellow bold'),
    ('highlighted', 'fg:yellow bold'),
    ('selected', 'fg:green'),
    ('separator', 'fg:gray'),
    ('instruction', 'fg:gray italic'),
])

console = Console()


def charger_schema_questions(type_acte: str) -> Dict:
    """Charge le fichier JSON des questions pour un type d'acte donné."""
    if type_acte not in TYPES_ACTES:
        console.print(f"[red]Type d'acte inconnu: {type_acte}[/red]")
        console.print(f"Types disponibles: {', '.join(TYPES_ACTES.keys())}")
        sys.exit(1)

    schema_file = SCHEMAS_DIR / TYPES_ACTES[type_acte]["schema"]

    if not schema_file.exists():
        console.print(f"[red]Fichier schema non trouvé: {schema_file}[/red]")
        sys.exit(1)

    with open(schema_file, "r", encoding="utf-8") as f:
        return json.load(f)


def extraire_chemin_variable(variable: str) -> List[str]:
    """
    Extrait le chemin d'une variable en liste de clés.
    Ex: "requerant.personne_physique.nom" -> ["requerant", "personne_physique", "nom"]
    Ex: "lots[].numero" -> ["lots", "[]", "numero"]
    """
    # Remplace les crochets par un marqueur spécial
    variable = re.sub(r'\[\]', '.[]', variable)
    return [p for p in variable.split('.') if p]


def definir_valeur_profonde(data: Dict, chemin: List[str], valeur: Any, index: int = None) -> None:
    """
    Définit une valeur profonde dans un dictionnaire.
    Crée les clés intermédiaires si nécessaire.
    """
    current = data

    for i, key in enumerate(chemin[:-1]):
        if key == "[]":
            # On traite les tableaux
            parent_key = chemin[i-1] if i > 0 else None
            if parent_key and parent_key in current:
                if not isinstance(current[parent_key], list):
                    current[parent_key] = []
                # On ajoute un élément si nécessaire
                if index is not None:
                    while len(current[parent_key]) <= index:
                        current[parent_key].append({})
                    current = current[parent_key][index]
            continue

        if key not in current:
            # Détermine si la prochaine clé est un tableau
            next_is_array = i + 1 < len(chemin) - 1 and chemin[i + 1] == "[]"
            current[key] = [] if next_is_array else {}

        current = current[key]

    # Définit la valeur finale
    final_key = chemin[-1]
    if final_key != "[]":
        current[final_key] = valeur


def obtenir_valeur_profonde(data: Dict, chemin: List[str], default: Any = None) -> Any:
    """Obtient une valeur profonde dans un dictionnaire."""
    current = data

    for key in chemin:
        if key == "[]":
            continue
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def evaluer_condition(condition: str, data: Dict) -> bool:
    """
    Évalue une condition d'affichage.
    Ex: "requerant.type == 'personne_physique'"
    """
    if not condition:
        return True

    try:
        # Parse la condition
        match = re.match(r"([\w.]+)\s*(==|!=)\s*['\"]?(\w+)['\"]?", condition)
        if not match:
            return True

        variable, operateur, valeur_attendue = match.groups()
        chemin = extraire_chemin_variable(variable)
        valeur_actuelle = obtenir_valeur_profonde(data, chemin)

        if valeur_actuelle is None:
            return False

        # Normalise les valeurs pour comparaison
        valeur_actuelle_str = str(valeur_actuelle).lower()
        valeur_attendue_str = valeur_attendue.lower()

        if operateur == "==":
            return valeur_actuelle_str == valeur_attendue_str
        elif operateur == "!=":
            return valeur_actuelle_str != valeur_attendue_str

    except Exception:
        pass

    return True


def poser_question(question: Dict, data: Dict, index: int = None) -> Any:
    """
    Pose une question à l'utilisateur et retourne la réponse.
    Gère les différents types de questions.
    """
    q_type = question.get("type", "texte")
    q_text = question.get("question", "Question?")
    q_obligatoire = question.get("obligatoire", False)
    q_note = question.get("note", "")

    # Ajoute la note si présente
    if q_note:
        q_text = f"{q_text}\n[dim italic]{q_note}[/dim italic]"

    # Ajoute indicateur obligatoire
    if q_obligatoire:
        q_text = f"{q_text} [red]*[/red]"

    console.print()

    if q_type == "texte":
        reponse = questionary.text(
            q_text,
            style=STYLE,
            validate=lambda x: True if not q_obligatoire else len(x.strip()) > 0
        ).ask()
        return reponse.strip() if reponse else None

    elif q_type == "texte_long":
        console.print(f"[bold]{q_text}[/bold]")
        console.print("[dim](Entrez votre texte, terminez par une ligne vide)[/dim]")
        lignes = []
        while True:
            ligne = input()
            if ligne == "":
                break
            lignes.append(ligne)
        return "\n".join(lignes) if lignes else None

    elif q_type == "nombre":
        reponse = questionary.text(
            q_text,
            style=STYLE,
            validate=lambda x: x.isdigit() or (not q_obligatoire and x == "")
        ).ask()
        return int(reponse) if reponse and reponse.isdigit() else None

    elif q_type == "nombre_decimal":
        reponse = questionary.text(
            q_text,
            style=STYLE,
            validate=lambda x: _is_decimal(x) or (not q_obligatoire and x == "")
        ).ask()
        return float(reponse.replace(",", ".")) if reponse and _is_decimal(reponse) else None

    elif q_type == "date":
        reponse = questionary.text(
            f"{q_text} (format: JJ/MM/AAAA)",
            style=STYLE,
            validate=lambda x: _is_valid_date(x) or (not q_obligatoire and x == "")
        ).ask()
        if reponse and _is_valid_date(reponse):
            # Convertit en format ISO
            jour, mois, annee = reponse.split("/")
            return f"{annee}-{mois.zfill(2)}-{jour.zfill(2)}"
        return None

    elif q_type == "booleen":
        reponse = questionary.confirm(
            q_text,
            style=STYLE,
            default=False
        ).ask()
        return reponse

    elif q_type == "choix_unique":
        options = question.get("options", [])
        if not options:
            return None
        reponse = questionary.select(
            q_text,
            choices=options,
            style=STYLE
        ).ask()
        return reponse

    elif q_type == "choix_multiple":
        options = question.get("options", [])
        if not options:
            return None
        reponses = questionary.checkbox(
            q_text,
            choices=options,
            style=STYLE
        ).ask()
        return reponses if reponses else []

    elif q_type == "tableau":
        colonnes = question.get("colonnes", [])
        return poser_question_tableau(q_text, colonnes)

    elif q_type == "groupe":
        sous_questions = question.get("sous_questions", [])
        return poser_questions_groupe(q_text, sous_questions, data)

    elif q_type == "repetition":
        sous_questions = question.get("sous_questions", [])
        return poser_questions_repetition(q_text, sous_questions, data)

    return None


def _is_decimal(value: str) -> bool:
    """Vérifie si une valeur est un nombre décimal valide."""
    try:
        float(value.replace(",", "."))
        return True
    except ValueError:
        return False


def _is_valid_date(value: str) -> bool:
    """Vérifie si une date est au format JJ/MM/AAAA."""
    try:
        datetime.strptime(value, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def poser_question_tableau(titre: str, colonnes: List[str]) -> List[Dict]:
    """Pose une question de type tableau (plusieurs lignes avec colonnes)."""
    console.print(f"[bold]{titre}[/bold]")
    console.print(f"[dim]Colonnes: {', '.join(colonnes)}[/dim]")
    console.print("[dim](Entrez 'fin' pour terminer)[/dim]")

    lignes = []
    num_ligne = 1

    while True:
        console.print(f"\n[yellow]Ligne {num_ligne}:[/yellow]")

        # Vérifie si on continue
        continuer = questionary.confirm(
            "Ajouter une ligne?",
            default=num_ligne == 1,
            style=STYLE
        ).ask()

        if not continuer:
            break

        ligne = {}
        for col in colonnes:
            valeur = questionary.text(f"  {col}:", style=STYLE).ask()
            ligne[col.lower().replace(" ", "_")] = valeur

        lignes.append(ligne)
        num_ligne += 1

    return lignes


def poser_questions_groupe(titre: str, sous_questions: List[Dict], data: Dict) -> Dict:
    """Pose un groupe de sous-questions."""
    console.print(f"\n[bold cyan]{titre}[/bold cyan]")

    resultats = {}

    for sq in sous_questions:
        variable = sq.get("variable", "")
        chemin = extraire_chemin_variable(variable)

        # Vérifie condition d'affichage
        condition = sq.get("condition_affichage", "")
        if not evaluer_condition(condition, data):
            continue

        reponse = poser_question(sq, data)

        if reponse is not None:
            # Utilise la dernière partie du chemin comme clé
            cle = chemin[-1] if chemin else sq.get("id", "valeur")
            resultats[cle] = reponse

    return resultats


def poser_questions_repetition(titre: str, sous_questions: List[Dict], data: Dict) -> List[Dict]:
    """Pose une série de questions répétables (pour créer plusieurs éléments)."""
    console.print(f"\n[bold cyan]{titre}[/bold cyan]")

    elements = []
    num_element = 1

    while True:
        console.print(f"\n[yellow]═══ Élément {num_element} ═══[/yellow]")

        if num_element > 1:
            continuer = questionary.confirm(
                "Ajouter un autre élément?",
                default=False,
                style=STYLE
            ).ask()

            if not continuer:
                break

        element = {}

        for sq in sous_questions:
            variable = sq.get("variable", "")
            # Extrait la clé (après [])
            chemin = extraire_chemin_variable(variable)
            cle = chemin[-1] if chemin else sq.get("id", "valeur")

            reponse = poser_question(sq, data)

            if reponse is not None:
                element[cle] = reponse

        elements.append(element)
        num_element += 1

        # Si c'est le premier élément, demande si on veut en ajouter d'autres
        if num_element == 2:
            continuer = questionary.confirm(
                "Ajouter un autre élément?",
                default=False,
                style=STYLE
            ).ask()
            if not continuer:
                break

    return elements


def collecter_section(section: Dict, data: Dict) -> Dict:
    """Collecte les réponses pour une section entière."""
    section_id = section.get("id", "section")
    titre = section.get("titre", "Section")
    questions = section.get("questions", [])

    # Affiche le titre de la section
    console.print()
    console.print(Panel(
        f"[bold white]{titre}[/bold white]",
        border_style="blue",
        expand=False
    ))

    resultats = {}

    for question in questions:
        q_id = question.get("id", "")
        variable = question.get("variable", "")

        # Vérifie condition d'affichage
        condition = question.get("condition_affichage", "")
        if not evaluer_condition(condition, data):
            continue

        # Pose la question
        reponse = poser_question(question, data)

        if reponse is not None:
            # Stocke la réponse
            chemin = extraire_chemin_variable(variable) if variable else [q_id]
            definir_valeur_profonde(resultats, chemin, reponse)

            # Met à jour data pour les conditions des questions suivantes
            definir_valeur_profonde(data, chemin, reponse)

        # Gère les sous-questions conditionnelles
        sous_questions = question.get("sous_questions", {})
        if isinstance(sous_questions, dict):
            # Format "si_oui" / "si_marie" etc.
            for condition_key, sq_list in sous_questions.items():
                if _evaluer_sous_condition(condition_key, reponse):
                    for sq in sq_list:
                        sq_variable = sq.get("variable", "")
                        sq_reponse = poser_question(sq, data)
                        if sq_reponse is not None:
                            sq_chemin = extraire_chemin_variable(sq_variable) if sq_variable else [sq.get("id", "val")]
                            definir_valeur_profonde(resultats, sq_chemin, sq_reponse)
                            definir_valeur_profonde(data, sq_chemin, sq_reponse)

    return resultats


def _evaluer_sous_condition(condition_key: str, valeur_parent: Any) -> bool:
    """Évalue si une sous-condition est remplie."""
    condition_key = condition_key.lower()

    if condition_key == "si_oui" and valeur_parent is True:
        return True
    if condition_key == "si_non" and valeur_parent is False:
        return True
    if condition_key == "si_marie" and valeur_parent and "marié" in str(valeur_parent).lower():
        return True
    if condition_key == "si_pacse" and valeur_parent and "pacsé" in str(valeur_parent).lower():
        return True

    return False


def fusionner_resultats(data: Dict, nouveaux: Dict) -> Dict:
    """Fusionne récursivement deux dictionnaires."""
    for key, value in nouveaux.items():
        if key in data and isinstance(data[key], dict) and isinstance(value, dict):
            fusionner_resultats(data[key], value)
        else:
            data[key] = value
    return data


def sauvegarder_progression(data: Dict, output_path: Path) -> None:
    """Sauvegarde la progression actuelle."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    console.print(f"[green]✓ Progression sauvegardée: {output_path}[/green]")


def afficher_resume(data: Dict) -> None:
    """Affiche un résumé des données collectées."""
    console.print()
    console.print(Panel(
        "[bold white]RÉSUMÉ DES INFORMATIONS COLLECTÉES[/bold white]",
        border_style="green"
    ))

    def _afficher_dict(d: Dict, indent: int = 0) -> None:
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                console.print(f"{prefix}[cyan]{key}:[/cyan]")
                _afficher_dict(value, indent + 1)
            elif isinstance(value, list):
                console.print(f"{prefix}[cyan]{key}:[/cyan] [{len(value)} éléments]")
            else:
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                console.print(f"{prefix}[cyan]{key}:[/cyan] {value_str}")

    _afficher_dict(data)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Collecte interactive des informations pour actes notariés",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python collecter_informations.py --type vente --output .tmp/donnees_vente.json
  python collecter_informations.py --type reglement --output .tmp/donnees_edd.json
  python collecter_informations.py --type modificatif --resume .tmp/collecte_partielle.json
        """
    )

    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=list(TYPES_ACTES.keys()),
        help="Type d'acte à générer"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier de sortie JSON (défaut: .tmp/donnees_{type}.json)"
    )

    parser.add_argument(
        "--resume", "-r",
        type=str,
        help="Fichier JSON à reprendre (pour continuer une collecte interrompue)"
    )

    parser.add_argument(
        "--schema",
        type=str,
        help="Chemin vers un fichier schema personnalisé (remplace le schema par défaut)"
    )

    args = parser.parse_args()

    # Détermine le fichier de sortie
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = TMP_DIR / f"donnees_{args.type}.json"

    # Charge le schema des questions
    if args.schema:
        schema_path = Path(args.schema)
        if not schema_path.exists():
            console.print(f"[red]Fichier schema non trouvé: {schema_path}[/red]")
            sys.exit(1)
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
    else:
        schema = charger_schema_questions(args.type)

    # Charge les données existantes si reprise
    data = {}
    if args.resume:
        resume_path = Path(args.resume)
        if resume_path.exists():
            with open(resume_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            console.print(f"[yellow]Reprise de la collecte depuis: {resume_path}[/yellow]")

    # Affiche l'en-tête
    titre_acte = TYPES_ACTES[args.type]["titre"]
    console.print()
    console.print(Panel(
        f"[bold white]COLLECTE D'INFORMATIONS[/bold white]\n\n"
        f"[cyan]{titre_acte}[/cyan]\n\n"
        f"[dim]Répondez aux questions pour générer votre acte.\n"
        f"Appuyez sur Ctrl+C à tout moment pour sauvegarder et quitter.[/dim]",
        border_style="blue",
        expand=False
    ))

    # Parcours des sections
    sections = schema.get("sections", [])
    total_sections = len(sections)

    try:
        for i, section in enumerate(sections, 1):
            console.print(f"\n[dim]Section {i}/{total_sections}[/dim]")

            resultats_section = collecter_section(section, data)
            data = fusionner_resultats(data, resultats_section)

            # Sauvegarde après chaque section
            sauvegarder_progression(data, output_path)

        # Affiche le résumé final
        afficher_resume(data)

        console.print()
        console.print(Panel(
            f"[bold green]✓ Collecte terminée![/bold green]\n\n"
            f"Fichier généré: [cyan]{output_path}[/cyan]\n\n"
            f"[dim]Vous pouvez maintenant utiliser ce fichier avec assembler_acte.py[/dim]",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Collecte interrompue par l'utilisateur.[/yellow]")
        sauvegarder_progression(data, output_path)
        console.print(f"[dim]Reprenez avec: python collecter_informations.py --type {args.type} --resume {output_path}[/dim]")
        sys.exit(0)

    except Exception as e:
        console.print(f"\n[red]Erreur: {e}[/red]")
        sauvegarder_progression(data, output_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
