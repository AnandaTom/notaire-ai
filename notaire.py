#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NotaireAI CLI - Point d'entrée simplifié

Usage:
    python notaire.py <commande> [options]

Commandes:
    extraire       Extraire un titre de propriété (PDF/DOCX)
    promesse       Générer une promesse de vente
    vente          Générer un acte de vente
    dashboard      Afficher le tableau de bord
    status         Vérifier le statut du système

Exemples:
    python notaire.py extraire titre.pdf
    python notaire.py promesse --titre titre.pdf --beneficiaires acquereurs.json
    python notaire.py vente --donnees donnees_vente.json
    python notaire.py dashboard
"""

import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def afficher_aide():
    """Affiche l'aide principale."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                     🏛️  NotaireAI CLI                            ║
║              Génération d'actes notariaux intelligente           ║
╚══════════════════════════════════════════════════════════════════╝

USAGE:
    python notaire.py <commande> [options]

COMMANDES PRINCIPALES:

  📄 EXTRACTION
    extraire <fichier>              Extraire un titre de propriété
        -o, --output <fichier>      Sauvegarder en JSON

  📝 GÉNÉRATION
    promesse                        Générer une promesse de vente
        --titre <fichier>           Titre source (PDF/DOCX/référence)
        --beneficiaires <json>      Données des bénéficiaires
        --prix <montant>            Prix en euros
        -o, --output <fichier>      Fichier DOCX de sortie

    vente                           Générer un acte de vente
        --promesse <ref>            Promesse source (JSON/référence)
        --donnees <json>            Données complètes
        -o, --output <fichier>      Fichier DOCX de sortie

    generer                         Génération directe
        --type <type>               Type: vente, promesse_vente, etc.
        --donnees <json>            Fichier de données
        -o, --output <fichier>      Fichier DOCX de sortie

  📊 SYSTÈME
    dashboard                       Afficher le tableau de bord
    status                          Vérifier le statut système

OPTIONS GLOBALES:
    -v, --verbose                   Mode verbeux
    -h, --help                      Afficher l'aide

EXEMPLES:

  # Extraire un titre et sauvegarder
  python notaire.py extraire docs_originels/titre.pdf -o titre.json

  # Générer une promesse depuis un titre
  python notaire.py promesse --titre titre.pdf --beneficiaires acq.json --prix 250000

  # Générer un acte de vente complet
  python notaire.py vente --donnees exemples/donnees_vente_exemple.json

  # Voir le dashboard
  python notaire.py dashboard
""")


def main():
    """Point d'entrée principal."""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        afficher_aide()
        return

    commande = sys.argv[1]

    # Importer l'orchestrateur
    from execution.orchestrateur_notaire import OrchestratorNotaire

    # Détecter verbose
    verbose = '-v' in sys.argv or '--verbose' in sys.argv

    orch = OrchestratorNotaire(verbose=verbose)

    # =========================================================================
    # Commande: extraire
    # =========================================================================
    if commande == 'extraire':
        if len(sys.argv) < 3:
            print("❌ Usage: python notaire.py extraire <fichier> [-o sortie.json]")
            return

        fichier = sys.argv[2]
        output = None

        if '-o' in sys.argv:
            idx = sys.argv.index('-o')
            output = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        elif '--output' in sys.argv:
            idx = sys.argv.index('--output')
            output = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None

        print(f"\n🔍 Extraction de: {fichier}")
        result = orch.extraire_titre(fichier, output)

        if result:
            print(f"\n✅ Extraction réussie")
            print(f"   Date acte: {result.get('date_acte', '?')}")
            print(f"   Notaire: {result.get('notaire', {}).get('nom', '?')}")
            print(f"   Confiance: {result.get('metadata', {}).get('confiance', 0):.0%}")
            if output:
                print(f"   Sauvegardé: {output}")

    # =========================================================================
    # Commande: promesse
    # =========================================================================
    elif commande == 'promesse':
        import argparse
        parser = argparse.ArgumentParser(prog='notaire.py promesse')
        parser.add_argument('--titre', required=True, help='Titre source')
        parser.add_argument('--beneficiaires', required=True, help='JSON bénéficiaires')
        parser.add_argument('--prix', type=float, help='Prix en euros')
        parser.add_argument('-o', '--output', required=True, help='DOCX sortie')
        parser.add_argument('-v', '--verbose', action='store_true')

        args = parser.parse_args(sys.argv[2:])

        import json
        from pathlib import Path

        beneficiaires = json.loads(Path(args.beneficiaires).read_text(encoding='utf-8'))
        options = {}
        if args.prix:
            options['prix'] = {'montant': args.prix, 'devise': 'EUR'}

        orch.verbose = args.verbose
        orch.titre_vers_promesse(args.titre, beneficiaires, args.output, options)

    # =========================================================================
    # Commande: vente
    # =========================================================================
    elif commande == 'vente':
        import argparse
        parser = argparse.ArgumentParser(prog='notaire.py vente')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--promesse', help='Promesse source (JSON ou référence)')
        group.add_argument('--donnees', help='Données complètes JSON')
        parser.add_argument('-o', '--output', help='DOCX sortie')
        parser.add_argument('-v', '--verbose', action='store_true')

        args = parser.parse_args(sys.argv[2:])

        import json
        from pathlib import Path

        orch.verbose = args.verbose

        if args.promesse:
            complements = {}
            orch.promesse_vers_vente(args.promesse, complements, args.output)
        else:
            donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
            orch.generer_acte_complet('vente', donnees, args.output)

    # =========================================================================
    # Commande: generer
    # =========================================================================
    elif commande == 'generer':
        import argparse
        parser = argparse.ArgumentParser(prog='notaire.py generer')
        parser.add_argument('--type', '-t', required=True,
                           choices=['vente', 'promesse_vente', 'reglement_copropriete', 'modificatif_edd'])
        parser.add_argument('--donnees', '-d', required=True, help='Fichier JSON')
        parser.add_argument('-o', '--output', help='DOCX sortie')
        parser.add_argument('-v', '--verbose', action='store_true')

        args = parser.parse_args(sys.argv[2:])

        import json
        from pathlib import Path

        donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
        orch.verbose = args.verbose
        orch.generer_acte_complet(args.type, donnees, args.output)

    # =========================================================================
    # Commande: dashboard
    # =========================================================================
    elif commande == 'dashboard':
        orch.afficher_dashboard()

    # =========================================================================
    # Commande: status
    # =========================================================================
    elif commande == 'status':
        orch.afficher_statut()

    # =========================================================================
    # Commande inconnue
    # =========================================================================
    else:
        print(f"❌ Commande inconnue: {commande}")
        print("   Utilisez 'python notaire.py --help' pour l'aide")


if __name__ == '__main__':
    main()
