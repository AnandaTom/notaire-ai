#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: Titre de Propriété → Promesse de Vente (DOCX)

Ce script démontre le workflow complet:
1. Chargement d'un titre de propriété (JSON ou extraction PDF)
2. Mapping automatique titre → données promesse
3. Collecte Q&R interactive pour les champs manquants
4. Validation des données
5. Assemblage Jinja2
6. Export DOCX

Usage:
    # Mode auto (pas de questions, utilise les défauts)
    python execution/demo_titre_promesse.py --auto

    # Mode interactif (pose les questions manquantes)
    python execution/demo_titre_promesse.py

    # Depuis un fichier titre spécifique
    python execution/demo_titre_promesse.py --titre mon_titre.json --prix 500000

    # Avec bénéficiaires
    python execution/demo_titre_promesse.py --titre mon_titre.json --beneficiaires benef.json
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Chemins
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR / 'core'))


def charger_titre(titre_path: str = None) -> dict:
    """
    Charge les données d'un titre de propriété.

    Si aucun fichier n'est fourni, utilise les données démo.
    Supporte JSON (données structurées) ou PDF (via extraction OCR).
    """
    if titre_path:
        path = Path(titre_path)
        if not path.exists():
            print(f"  ERREUR: Fichier titre introuvable: {path}")
            sys.exit(1)

        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  Titre charge: {path.name} ({len(data)} sections)")
            return data

        elif path.suffix.lower() == '.pdf':
            # Extraction PDF via le module d'extraction
            try:
                from execution.utils.extraire_titre import extraire_titre_propriete
                data = extraire_titre_propriete(str(path))
                print(f"  Titre extrait (PDF): {path.name}")
                return data
            except ImportError:
                print("  Module extraire_titre non disponible")
                print("  Utilisez un fichier JSON ou installez pytesseract")
                sys.exit(1)
        else:
            print(f"  Format non supporte: {path.suffix}")
            sys.exit(1)

    # Données démo par défaut
    demo_path = PROJECT_ROOT / 'exemples' / 'donnees_demo_complete.json'
    if demo_path.exists():
        with open(demo_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  Donnees demo chargees (scenario DUPONT → MARTIN)")
        return data

    print("  ERREUR: Aucune donnee disponible")
    sys.exit(1)


def charger_beneficiaires(benef_path: str = None) -> list:
    """Charge les données des bénéficiaires."""
    if not benef_path:
        return None

    path = Path(benef_path)
    if not path.exists():
        print(f"  Fichier beneficiaires introuvable: {path}")
        return None

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'beneficiaires' in data:
        return data['beneficiaires']
    elif isinstance(data, dict):
        return [data]

    return None


def run_demo(
    titre_path: str = None,
    beneficiaires_path: str = None,
    prix: int = None,
    mode: str = 'cli',
    output: str = None
):
    """
    Execute le workflow complet: titre → Q&R → promesse → DOCX.
    """
    debut = time.time()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    print()
    print("=" * 60)
    print("  DEMO NOTOMAI - Titre de Propriete -> Promesse de Vente")
    print("=" * 60)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Mode: {'automatique' if mode == 'prefill_only' else 'interactif'}")
    print()

    # ─── Etape 1: Charger le titre ───
    print("  [1/5] CHARGEMENT DU TITRE")
    print("  " + "-" * 40)
    titre_data = charger_titre(titre_path)

    beneficiaires = charger_beneficiaires(beneficiaires_path)
    if beneficiaires:
        print(f"  Beneficiaires charges: {len(beneficiaires)}")

    # ─── Etape 2: Agent Q&R (mapping + collecte) ───
    print()
    print("  [2/5] COLLECTE Q&R (titre -> promesse)")
    print("  " + "-" * 40)

    from execution.agent_autonome import AgentNotaire
    agent = AgentNotaire()

    resultat = agent.executer_depuis_titre(
        titre_data=titre_data,
        beneficiaires=beneficiaires,
        prix=prix,
        mode=mode
    )

    if not resultat.succes:
        print(f"\n  ERREUR: {resultat.message}")
        # Sauvegarder les données collectées pour debug
        if resultat.donnees:
            debug_path = PROJECT_ROOT / '.tmp' / f'demo_debug_{timestamp}.json'
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            debug_path.write_text(
                json.dumps(resultat.donnees, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            print(f"  Donnees sauvegardees pour debug: {debug_path}")

    # ─── Etape 3: Assemblage direct (fallback si orchestrateur echoue) ───
    donnees = resultat.donnees
    fichier_existe = (
        resultat.fichier_genere
        and Path(resultat.fichier_genere).exists()
    )
    if donnees and not fichier_existe:
        print()
        print("  [3/5] ASSEMBLAGE TEMPLATE")
        print("  " + "-" * 40)

        try:
            from execution.core.assembler_acte import AssembleurActe
            assembleur = AssembleurActe(PROJECT_ROOT / 'templates')
            acte_md = assembleur.assembler(
                'promesse_vente_lots_copropriete.md', donnees
            )
            print(f"  Assemblage OK: {len(acte_md)} caracteres")

            # Sauvegarder le markdown
            md_path = PROJECT_ROOT / '.tmp' / f'demo_promesse_{timestamp}.md'
            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(acte_md, encoding='utf-8')

        except Exception as e:
            print(f"  Erreur assemblage: {e}")
            acte_md = None
            md_path = None

    elif fichier_existe:
        # L'orchestrateur a deja genere le fichier
        md_path = Path(resultat.fichier_genere)
        if md_path.suffix == '.md':
            acte_md = md_path.read_text(encoding='utf-8')
        else:
            acte_md = None
    else:
        acte_md = None
        md_path = None

    # ─── Etape 4: Export DOCX ───
    docx_path = None
    if acte_md and md_path:
        print()
        print("  [4/5] EXPORT DOCX")
        print("  " + "-" * 40)

        try:
            from execution.core.exporter_docx import ExporterDocx
            output_name = output or f'demo_promesse_{timestamp}.docx'
            docx_path = PROJECT_ROOT / 'outputs' / output_name

            exporteur = ExporterDocx()
            exporteur.exporter(str(md_path), str(docx_path))
            taille = docx_path.stat().st_size / 1024
            print(f"  DOCX genere: {docx_path.name} ({taille:.1f} Ko)")

        except Exception as e:
            print(f"  Erreur export DOCX: {e}")
    elif fichier_existe and Path(resultat.fichier_genere).suffix == '.docx':
        docx_path = Path(resultat.fichier_genere)

    # ─── Etape 5: Rapport final ───
    duree = time.time() - debut
    print()
    print("  [5/5] RAPPORT FINAL")
    print("  " + "-" * 40)

    # Sauvegarder les données collectées
    if donnees:
        donnees_path = PROJECT_ROOT / '.tmp' / f'demo_donnees_{timestamp}.json'
        donnees_path.parent.mkdir(parents=True, exist_ok=True)
        donnees_path.write_text(
            json.dumps(donnees, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    print()
    print("=" * 60)
    print("  RESULTATS")
    print("=" * 60)
    print(f"  Statut       : {'OK' if (docx_path and docx_path.exists()) else ('Donnees OK' if donnees else 'ECHEC')}")
    if docx_path and docx_path.exists():
        print(f"  Fichier DOCX : {docx_path}")
    if donnees:
        print(f"  Donnees JSON : {donnees_path}")
    if md_path and md_path.exists():
        print(f"  Markdown     : {md_path}")
    print(f"  Duree totale : {duree:.1f}s")
    print(f"  Etapes       : {len(resultat.etapes)}")
    print("=" * 60)
    print()

    return 0 if (donnees) else 1


def main():
    parser = argparse.ArgumentParser(
        description='Demo Notomai: Titre de Propriete -> Promesse de Vente',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Mode automatique (sans interaction)
  python execution/demo_titre_promesse.py --auto

  # Mode interactif (pose les questions manquantes)
  python execution/demo_titre_promesse.py

  # Depuis un titre specifique
  python execution/demo_titre_promesse.py --titre mon_titre.json --prix 500000

  # Avec beneficiaires
  python execution/demo_titre_promesse.py --titre titre.json --beneficiaires benef.json
        """
    )

    parser.add_argument('--titre', type=str, default=None,
                        help='Fichier titre de propriete (JSON ou PDF)')
    parser.add_argument('--beneficiaires', type=str, default=None,
                        help='Fichier JSON des beneficiaires')
    parser.add_argument('--prix', type=int, default=None,
                        help='Prix de vente en euros')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Nom du fichier DOCX de sortie')
    parser.add_argument('--auto', action='store_true',
                        help='Mode automatique (pas de questions, prefill + defauts)')

    args = parser.parse_args()

    mode = 'prefill_only' if args.auto else 'cli'

    return run_demo(
        titre_path=args.titre,
        beneficiaires_path=args.beneficiaires,
        prix=args.prix,
        mode=mode,
        output=args.output
    )


if __name__ == '__main__':
    sys.exit(main() or 0)
