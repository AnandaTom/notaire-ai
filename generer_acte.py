#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_acte.py - CLI Master NotaireAI
======================================

Point d'entrée principal pour la génération d'actes notariaux.
Interface simplifiée pour notaires avec progress bars et feedback visuel.

Usage:
    python generer_acte.py                     # Mode interactif guidé
    python generer_acte.py --type vente        # Type prédéfini
    python generer_acte.py -d donnees.json     # Données depuis fichier
    python generer_acte.py --quick             # Mode rapide (pas d'interactif)

Exemples:
    # Mode guidé complet
    python generer_acte.py

    # Génération rapide avec données existantes
    python generer_acte.py --type vente -d exemples/donnees_vente_exemple.json

    # Avec nom de fichier personnalisé
    python generer_acte.py --type promesse_vente -d donnees.json -o "Promesse_Dupont.docx"
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Chemins
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR

# Importer rich pour l'interface
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    class Console:
        def print(self, *args, **kwargs):
            # Strip rich formatting
            text = args[0] if args else ""
            if isinstance(text, str):
                import re
                text = re.sub(r'\[.*?\]', '', text)
            print(text)

console = Console()

# Types d'actes supportés
TYPES_ACTES = {
    'vente': {
        'nom': 'Acte de vente définitif',
        'template': 'vente_lots_copropriete.md',
        'conformite': 0.85,
        'exemple': 'exemples/donnees_vente_exemple.json',
        'questions': 'schemas/questions_notaire.json'
    },
    'promesse_vente': {
        'nom': 'Promesse unilatérale de vente',
        'template': 'promesse_vente_lots_copropriete.md',
        'conformite': 0.61,
        'exemple': 'exemples/donnees_promesse_exemple.json',
        'questions': 'schemas/questions_promesse_vente.json'
    },
    'reglement_copropriete': {
        'nom': 'Règlement de copropriété / EDD',
        'template': 'reglement_copropriete_edd.md',
        'conformite': 0.855,
        'exemple': None,
        'questions': 'schemas/questions_reglement_copropriete.json'
    },
    'modificatif_edd': {
        'nom': 'Modificatif EDD',
        'template': 'modificatif_edd.md',
        'conformite': 0.917,
        'exemple': None,
        'questions': 'schemas/questions_modificatif_edd.json'
    }
}


def afficher_banniere():
    """Affiche la bannière d'accueil."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗ ██████╗ ████████╗ █████╗ ██╗██████╗ ███████╗   ║
║   ████╗  ██║██╔═══██╗╚══██╔══╝██╔══██╗██║██╔══██╗██╔════╝   ║
║   ██╔██╗ ██║██║   ██║   ██║   ███████║██║██████╔╝█████╗     ║
║   ██║╚██╗██║██║   ██║   ██║   ██╔══██║██║██╔══██╗██╔══╝     ║
║   ██║ ╚████║╚██████╔╝   ██║   ██║  ██║██║██║  ██║███████╗   ║
║   ╚═╝  ╚═══╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝   ║
║                                                              ║
║              Génération d'Actes Notariaux v1.3.0             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(banner, style="bold blue")
    else:
        print(banner)


def afficher_types_actes() -> str:
    """Affiche et sélectionne le type d'acte."""
    if RICH_AVAILABLE:
        table = Table(title="Types d'actes disponibles", show_header=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Type", style="green")
        table.add_column("Conformité", justify="center")
        table.add_column("Statut")

        for i, (key, info) in enumerate(TYPES_ACTES.items(), 1):
            conf = info['conformite']
            barre = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
            statut = "[green]PROD[/green]" if conf >= 0.8 else "[yellow]DEV[/yellow]"
            table.add_row(str(i), info['nom'], f"{barre} {conf:.0%}", statut)

        console.print(table)
        console.print()

        # Sélection
        choix = Prompt.ask(
            "Sélectionnez le type d'acte",
            choices=[str(i) for i in range(1, len(TYPES_ACTES) + 1)],
            default="1"
        )
        return list(TYPES_ACTES.keys())[int(choix) - 1]
    else:
        print("\nTypes d'actes disponibles:")
        for i, (key, info) in enumerate(TYPES_ACTES.items(), 1):
            conf = info['conformite']
            print(f"  {i}. {info['nom']} ({conf:.0%})")
        choix = input("\nSélectionnez (1-4): ").strip() or "1"
        return list(TYPES_ACTES.keys())[int(choix) - 1]


def charger_donnees(chemin: str) -> Dict[str, Any]:
    """Charge les données depuis un fichier JSON."""
    path = Path(chemin)
    if not path.exists():
        # Essayer relativement au projet
        path = PROJECT_ROOT / chemin
    if not path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {chemin}")

    return json.loads(path.read_text(encoding='utf-8'))


def generer_nom_fichier(type_acte: str, donnees: Dict[str, Any]) -> str:
    """Génère un nom de fichier intelligent basé sur les données."""
    # Essayer d'extraire des noms
    noms = []

    # Chercher dans vendeurs/promettants
    for key in ['vendeurs', 'promettants']:
        if key in donnees:
            for p in donnees[key][:2]:  # Max 2 noms
                nom = p.get('nom') or p.get('personne_physique', {}).get('nom', '')
                if nom:
                    noms.append(nom.upper())

    # Chercher dans acquéreurs/bénéficiaires
    for key in ['acquereurs', 'beneficiaires']:
        if key in donnees:
            for p in donnees[key][:1]:  # Max 1 nom
                nom = p.get('nom') or p.get('personne_physique', {}).get('nom', '')
                if nom:
                    noms.append(nom.upper())

    # Construire le nom
    type_court = {
        'vente': 'Vente',
        'promesse_vente': 'Promesse',
        'reglement_copropriete': 'RC',
        'modificatif_edd': 'Modif_EDD'
    }.get(type_acte, type_acte)

    date_str = datetime.now().strftime('%Y%m%d')

    if noms:
        return f"{type_court}_{'-'.join(noms[:2])}_{date_str}.docx"
    else:
        return f"{type_court}_{date_str}.docx"


def executer_workflow(
    type_acte: str,
    donnees: Dict[str, Any],
    output: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """Exécute le workflow complet avec progress bar."""

    # Import de l'orchestrateur
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from execution.orchestrateur_notaire import OrchestratorNotaire, TypeActe
    except ImportError:
        console.print("[red]Erreur: Impossible de charger l'orchestrateur[/red]")
        return {"succes": False, "erreur": "Module orchestrateur non trouvé"}

    if RICH_AVAILABLE:
        console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Génération en cours...", total=100)

            # Étape 1: Initialisation
            progress.update(task, description="[cyan]Initialisation...", advance=10)
            orch = OrchestratorNotaire(verbose=verbose)

            # Étape 2: Enrichissement
            progress.update(task, description="[cyan]Enrichissement des données...", advance=20)

            # Étape 3: Assemblage
            progress.update(task, description="[cyan]Assemblage du template...", advance=20)

            # Étape 4: Export
            progress.update(task, description="[cyan]Export DOCX...", advance=30)

            # Exécuter le workflow réel
            result = orch.generer_acte_complet(type_acte, donnees, output)

            # Étape 5: Finalisation
            progress.update(task, description="[green]Terminé!", advance=20)

        return result

    else:
        # Mode sans rich
        print("\n[*] Génération en cours...")
        orch = OrchestratorNotaire(verbose=verbose)
        result = orch.generer_acte_complet(type_acte, donnees, output)
        return result


def afficher_resultat(result, output: str):
    """Affiche le résultat de la génération."""
    if RICH_AVAILABLE:
        if result.statut == "succes":
            message = (
                f"[bold green]GÉNÉRATION RÉUSSIE[/bold green]\n\n"
                f"[bold]Fichier:[/bold] {output}\n"
                f"[bold]Durée:[/bold] {result.duree_totale_ms / 1000:.1f}s"
            )
            if result.score_conformite:
                message += f"\n[bold]Conformité:[/bold] {result.score_conformite:.0%}"
            panel = Panel(
                message,
                title="Résultat",
                border_style="green"
            )
            console.print(panel)

            if result.alertes:
                console.print("\n[yellow]Alertes:[/yellow]")
                for a in result.alertes:
                    console.print(f"  [yellow]•[/yellow] {a}")

            console.print(f"\n[dim]Ouvrir: {output}[/dim]")

        else:
            panel = Panel(
                f"[bold red]ÉCHEC DE LA GÉNÉRATION[/bold red]\n\n"
                f"[bold]Erreurs:[/bold]\n" +
                "\n".join(f"  • {e}" for e in result.erreurs),
                title="Erreur",
                border_style="red"
            )
            console.print(panel)
    else:
        if result.statut == "succes":
            print(f"\n[OK] Génération réussie!")
            print(f"     Fichier: {output}")
            print(f"     Durée: {result.duree_totale_ms / 1000:.1f}s")
        else:
            print(f"\n[ERREUR] Génération échouée:")
            for e in result.erreurs:
                print(f"  - {e}")


def mode_interactif() -> Dict[str, Any]:
    """Mode interactif guidé pour les notaires."""
    afficher_banniere()

    # 1. Sélection du type d'acte
    console.print("[bold]ÉTAPE 1/4:[/bold] Type d'acte\n")
    type_acte = afficher_types_actes()
    info_acte = TYPES_ACTES[type_acte]

    console.print(f"\n[green]✓[/green] Type sélectionné: {info_acte['nom']}")

    # 2. Source des données
    console.print(f"\n[bold]ÉTAPE 2/4:[/bold] Données\n")

    if RICH_AVAILABLE:
        choix_donnees = Prompt.ask(
            "Source des données",
            choices=["1", "2", "3"],
            default="1"
        )
        console.print("  1. Utiliser les données d'exemple")
        console.print("  2. Charger depuis un fichier JSON")
        console.print("  3. Saisie interactive (non disponible)")
    else:
        print("  1. Utiliser les données d'exemple")
        print("  2. Charger depuis un fichier JSON")
        choix_donnees = input("\nChoix (1-2): ").strip() or "1"

    donnees = None
    if choix_donnees == "1":
        if info_acte['exemple']:
            donnees = charger_donnees(info_acte['exemple'])
            console.print(f"[green]✓[/green] Données d'exemple chargées")
        else:
            console.print("[yellow]Pas d'exemple disponible pour ce type[/yellow]")
            return {"succes": False, "erreur": "Pas d'exemple disponible"}
    elif choix_donnees == "2":
        if RICH_AVAILABLE:
            chemin = Prompt.ask("Chemin du fichier JSON")
        else:
            chemin = input("Chemin du fichier JSON: ")
        try:
            donnees = charger_donnees(chemin)
            console.print(f"[green]✓[/green] Données chargées depuis {chemin}")
        except FileNotFoundError as e:
            console.print(f"[red]Erreur: {e}[/red]")
            return {"succes": False, "erreur": str(e)}

    # 3. Nom du fichier de sortie
    console.print(f"\n[bold]ÉTAPE 3/4:[/bold] Fichier de sortie\n")

    nom_suggere = generer_nom_fichier(type_acte, donnees)
    if RICH_AVAILABLE:
        nom_fichier = Prompt.ask("Nom du fichier", default=nom_suggere)
    else:
        nom_fichier = input(f"Nom du fichier [{nom_suggere}]: ").strip() or nom_suggere

    # S'assurer de l'extension .docx
    if not nom_fichier.endswith('.docx'):
        nom_fichier += '.docx'

    output_path = PROJECT_ROOT / 'outputs' / nom_fichier
    output_path.parent.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]✓[/green] Sortie: {output_path}")

    # 4. Confirmation et génération
    console.print(f"\n[bold]ÉTAPE 4/4:[/bold] Génération\n")

    if RICH_AVAILABLE:
        if not Confirm.ask("Lancer la génération?", default=True):
            console.print("[yellow]Annulé[/yellow]")
            return {"succes": False, "erreur": "Annulé par l'utilisateur"}
    else:
        confirm = input("Lancer la génération? [O/n]: ").strip().lower()
        if confirm == 'n':
            print("Annulé")
            return {"succes": False, "erreur": "Annulé par l'utilisateur"}

    # Exécuter le workflow
    result = executer_workflow(type_acte, donnees, str(output_path))

    # Afficher le résultat
    afficher_resultat(result, str(output_path))

    return result


def mode_rapide(args) -> Dict[str, Any]:
    """Mode rapide sans interaction."""
    console.print(f"\n[bold blue]NotaireAI[/bold blue] - Mode rapide\n")

    # Valider le type d'acte
    if args.type not in TYPES_ACTES:
        console.print(f"[red]Type d'acte invalide: {args.type}[/red]")
        console.print(f"Types valides: {', '.join(TYPES_ACTES.keys())}")
        return {"succes": False, "erreur": "Type invalide"}

    info_acte = TYPES_ACTES[args.type]
    console.print(f"[cyan]Type:[/cyan] {info_acte['nom']}")

    # Charger les données
    if args.donnees:
        try:
            donnees = charger_donnees(args.donnees)
            console.print(f"[cyan]Données:[/cyan] {args.donnees}")
        except FileNotFoundError as e:
            console.print(f"[red]{e}[/red]")
            return {"succes": False, "erreur": str(e)}
    elif info_acte['exemple']:
        donnees = charger_donnees(info_acte['exemple'])
        console.print(f"[cyan]Données:[/cyan] exemple par défaut")
    else:
        console.print("[red]Aucune donnée fournie et pas d'exemple disponible[/red]")
        return {"succes": False, "erreur": "Pas de données"}

    # Définir le fichier de sortie
    if args.output:
        output = args.output
        if not output.endswith('.docx'):
            output += '.docx'
    else:
        output = generer_nom_fichier(args.type, donnees)

    output_path = PROJECT_ROOT / 'outputs' / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    console.print(f"[cyan]Sortie:[/cyan] {output_path}\n")

    # Exécuter le workflow
    result = executer_workflow(args.type, donnees, str(output_path), verbose=args.verbose)

    # Afficher le résultat
    afficher_resultat(result, str(output_path))

    return result


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="NotaireAI - Génération d'actes notariaux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python generer_acte.py                              # Mode interactif
  python generer_acte.py --type vente                 # Génération rapide
  python generer_acte.py -t vente -d donnees.json     # Avec données
  python generer_acte.py -t promesse_vente -o mon_acte.docx
        """
    )

    parser.add_argument(
        '-t', '--type',
        choices=list(TYPES_ACTES.keys()),
        help="Type d'acte à générer"
    )

    parser.add_argument(
        '-d', '--donnees',
        help="Fichier JSON des données"
    )

    parser.add_argument(
        '-o', '--output',
        help="Nom du fichier de sortie"
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Mode verbeux"
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help="Mode rapide (utilise les exemples par défaut)"
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help="Liste les types d'actes disponibles"
    )

    args = parser.parse_args()

    # Liste des types
    if args.list:
        afficher_banniere()
        if RICH_AVAILABLE:
            table = Table(title="Types d'actes disponibles")
            table.add_column("Clé", style="cyan")
            table.add_column("Nom")
            table.add_column("Conformité")
            table.add_column("Exemple")

            for key, info in TYPES_ACTES.items():
                table.add_row(
                    key,
                    info['nom'],
                    f"{info['conformite']:.0%}",
                    "✓" if info['exemple'] else "-"
                )
            console.print(table)
        else:
            for key, info in TYPES_ACTES.items():
                print(f"{key}: {info['nom']} ({info['conformite']:.0%})")
        return

    # Mode rapide ou interactif
    if args.type or args.quick:
        if args.quick and not args.type:
            args.type = 'vente'  # Type par défaut en mode quick
        mode_rapide(args)
    else:
        mode_interactif()


if __name__ == '__main__':
    main()
