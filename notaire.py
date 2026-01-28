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

  🤖 AGENT AUTONOME (NOUVEAU!)
    agent "<demande>"               Exécuter une demande en langage naturel
        Exemples:
          agent "Crée une promesse Martin→Dupont, appart 67m² Paris, 450000€"
          agent "Modifie le prix à 460000€ dans le dossier 2026-001"
          agent "Liste les actes récents"
          agent                     Mode interactif

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

  🧠 SYSTÈME INTELLIGENT (NOUVEAU!)
    clauses lister                  Lister les sections disponibles
        --type <fixes|variables|toutes>
    clauses profils                 Lister les profils pré-configurés
    clauses analyser                Analyser les données et sélectionner les sections
        --donnees <json>            Fichier de données
        --profil <id>               Profil à appliquer
        -o <fichier>                Sauvegarder la config

    feedback soumettre              Soumettre un feedback pour amélioration
        --type <ajouter|modifier|supprimer>
        --cible <section_id>        Section concernée
        --contenu <texte>           Nouveau contenu (si ajouter/modifier)
        --raison <texte>            Raison du changement
        --notaire <nom>             Nom du notaire

    feedback lister                 Lister les feedbacks
        --statut <en_attente|approuve|rejete>

    feedback stats                  Statistiques d'apprentissage

  🆕 PROMESSES AVANCÉES (v1.4.0)
    promesse-avancee generer        Générer une promesse (détection auto du type)
        --donnees <json>            Fichier de données
        --type <type>               Forcer un type (standard|premium|avec_mobilier|multi_biens)
        --profil <profil>           Utiliser un profil prédéfini
        -o, --output <fichier>      DOCX de sortie

    promesse-avancee depuis-titre   Générer depuis un titre de propriété
        --titre <fichier>           Titre source (JSON)
        --beneficiaires <json>      Données des bénéficiaires
        --prix <montant>            Prix en euros
        --financement <json>        Options de financement (optionnel)
        -o, --output <fichier>      DOCX de sortie

    promesse-avancee detecter       Détecter le type de promesse
        --donnees <json>            Fichier de données

    promesse-avancee valider        Valider les données
        --donnees <json>            Fichier de données
        --type <type>               Type de promesse (optionnel)

    promesse-avancee profils        Lister les profils disponibles

    promesse-avancee types          Lister les types de promesse

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
    from execution.gestionnaires.orchestrateur import OrchestratorNotaire

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
    # Commande: agent (NOUVEAU - Mode agent autonome)
    # =========================================================================
    elif commande == 'agent':
        from execution.agent_autonome import AgentNotaire

        agent = AgentNotaire()

        if len(sys.argv) > 2:
            # Mode commande directe
            demande = ' '.join(sys.argv[2:])
            agent.executer(demande)
        else:
            # Mode interactif
            print("\n🤖 Agent NotaireAI - Mode interactif")
            print("   Tapez 'aide' pour voir les commandes, 'q' pour quitter\n")

            while True:
                try:
                    demande = input(">>> ").strip()

                    if demande.lower() in ('q', 'quit', 'exit'):
                        print("Au revoir!")
                        break

                    if not demande:
                        continue

                    agent.executer(demande)

                except KeyboardInterrupt:
                    print("\nAu revoir!")
                    break
                except EOFError:
                    break

    # =========================================================================
    # Commande: clauses (Gestion intelligente des clauses)
    # =========================================================================
    elif commande == 'clauses':
        import argparse
        from execution.gestionnaires.gestionnaire_clauses import GestionnaireClausesIntelligent

        parser = argparse.ArgumentParser(prog='notaire.py clauses')
        subparsers = parser.add_subparsers(dest='action', help='Action sur les clauses')

        # Sous-commande: lister
        sub_lister = subparsers.add_parser('lister', help='Lister les sections')
        sub_lister.add_argument('--type', choices=['fixes', 'variables', 'toutes'], default='toutes')

        # Sous-commande: profils
        sub_profils = subparsers.add_parser('profils', help='Lister les profils')

        # Sous-commande: analyser
        sub_analyser = subparsers.add_parser('analyser', help='Analyser les données')
        sub_analyser.add_argument('--donnees', '-d', required=True, help='Fichier JSON')
        sub_analyser.add_argument('--profil', '-p', help='Profil à appliquer')
        sub_analyser.add_argument('-o', '--output', help='Fichier de sortie')

        args = parser.parse_args(sys.argv[2:])

        gestionnaire = GestionnaireClausesIntelligent()

        if args.action == 'lister':
            sections = gestionnaire.obtenir_sections_disponibles()
            if args.type == 'fixes':
                sections = [s for s in sections if s.get('type') == 'fixe']
            elif args.type == 'variables':
                sections = [s for s in sections if s.get('type') == 'variable']

            print(f"\n{'='*60}")
            print(f"SECTIONS DISPONIBLES ({len(sections)})")
            print(f"{'='*60}\n")

            for s in sections:
                status = "✓" if s.get('active', True) else "✗"
                oblig = "[OBLIGATOIRE]" if s.get('obligatoire') else ""
                print(f"  {status} {s['id']}: {s['titre']} ({s['niveau']}) {oblig}")

        elif args.action == 'profils':
            print(f"\n{'='*60}")
            print(f"PROFILS PRÉ-CONFIGURÉS ({len(gestionnaire.profils)})")
            print(f"{'='*60}\n")

            for p in gestionnaire.profils:
                print(f"  • {p['id']}: {p['nom']}")
                print(f"    {p['description']}")
                print()

        elif args.action == 'analyser':
            import json
            from pathlib import Path

            donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
            sections = gestionnaire.selectionner_sections(donnees, args.profil)
            config = gestionnaire.generer_config_template()

            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"[OK] Configuration générée: {args.output}")
            else:
                print(json.dumps(config, ensure_ascii=False, indent=2))

        else:
            parser.print_help()

    # =========================================================================
    # Commande: feedback (Système d'apprentissage continu)
    # =========================================================================
    elif commande == 'feedback':
        import argparse
        from execution.api.api_feedback import APIFeedbackNotaire

        parser = argparse.ArgumentParser(prog='notaire.py feedback')
        subparsers = parser.add_subparsers(dest='action', help='Action feedback')

        # Sous-commande: soumettre
        sub_soumettre = subparsers.add_parser('soumettre', help='Soumettre un feedback')
        sub_soumettre.add_argument('--type', required=True, choices=['ajouter', 'modifier', 'supprimer'])
        sub_soumettre.add_argument('--cible', required=True, help='ID de la section')
        sub_soumettre.add_argument('--contenu', help='Nouveau contenu')
        sub_soumettre.add_argument('--raison', help='Raison du changement')
        sub_soumettre.add_argument('--notaire', default='CLI', help='Nom du notaire')

        # Sous-commande: lister
        sub_lister = subparsers.add_parser('lister', help='Lister les feedbacks')
        sub_lister.add_argument('--statut', choices=['en_attente', 'approuve', 'rejete'])

        # Sous-commande: stats
        sub_stats = subparsers.add_parser('stats', help='Statistiques')

        args = parser.parse_args(sys.argv[2:])

        api = APIFeedbackNotaire()

        if args.action == 'soumettre':
            result = api.soumettre_feedback({
                'action': args.type,
                'cible': args.cible,
                'contenu': args.contenu,
                'raison': args.raison or '',
                'notaire': args.notaire
            })
            print(f"\n✅ {result['message']}")
            print(f"   ID: {result.get('feedback_id')}")
            print(f"   Impact estimé: {result.get('impact_estime')}")

        elif args.action == 'lister':
            feedbacks = api.lister_feedbacks(args.statut if hasattr(args, 'statut') else None)
            print(f"\n{'='*60}")
            print(f"FEEDBACKS ({len(feedbacks)})")
            print(f"{'='*60}\n")

            for f in feedbacks:
                statut = f.get('statut', '?')
                emoji = {'en_attente': '⏳', 'approuve': '✅', 'rejete': '❌'}.get(statut, '?')
                print(f"  {emoji} [{f.get('id')}] {f.get('action')} sur {f.get('cible')}")
                print(f"     Par: {f.get('source_notaire')} - {f.get('date_creation', '')[:10]}")

        elif args.action == 'stats':
            stats = api.obtenir_statistiques()
            print(f"\n{'='*60}")
            print("STATISTIQUES D'APPRENTISSAGE")
            print(f"{'='*60}\n")
            print(f"Total feedbacks: {stats['total_feedbacks']}")
            print(f"  - En attente: {stats['en_attente']}")
            print(f"  - Approuvés: {stats['approuves']}")
            print(f"  - Rejetés: {stats['rejetes']}")
            print(f"Taux d'approbation: {stats['taux_approbation']:.1f}%")

            if stats.get('top_notaires'):
                print(f"\nTop notaires contributeurs:")
                for notaire, count in stats['top_notaires']:
                    print(f"  - {notaire}: {count} feedbacks")

        else:
            parser.print_help()

    # =========================================================================
    # Commande: promesse-avancee (Nouveau système multi-templates)
    # =========================================================================
    elif commande == 'promesse-avancee':
        import argparse
        import json
        from pathlib import Path
        from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses, TypePromesse

        parser = argparse.ArgumentParser(prog='notaire.py promesse-avancee')
        subparsers = parser.add_subparsers(dest='action', help='Action')

        # Sous-commande: generer
        sub_gen = subparsers.add_parser('generer', help='Générer une promesse')
        sub_gen.add_argument('--donnees', '-d', required=True, help='Fichier JSON')
        sub_gen.add_argument('--type', '-t', choices=['standard', 'premium', 'avec_mobilier', 'multi_biens'])
        sub_gen.add_argument('--profil', '-p', help='Profil prédéfini')
        sub_gen.add_argument('-o', '--output', help='Dossier de sortie')
        sub_gen.add_argument('-v', '--verbose', action='store_true')

        # Sous-commande: depuis-titre
        sub_titre = subparsers.add_parser('depuis-titre', help='Générer depuis un titre')
        sub_titre.add_argument('--titre', required=True, help='Fichier titre JSON')
        sub_titre.add_argument('--beneficiaires', '-b', required=True, help='JSON bénéficiaires')
        sub_titre.add_argument('--prix', type=float, required=True, help='Prix en euros')
        sub_titre.add_argument('--financement', '-f', help='JSON financement')
        sub_titre.add_argument('-o', '--output', help='Dossier de sortie')
        sub_titre.add_argument('-v', '--verbose', action='store_true')

        # Sous-commande: detecter
        sub_det = subparsers.add_parser('detecter', help='Détecter le type')
        sub_det.add_argument('--donnees', '-d', required=True, help='Fichier JSON')

        # Sous-commande: valider
        sub_val = subparsers.add_parser('valider', help='Valider les données')
        sub_val.add_argument('--donnees', '-d', required=True, help='Fichier JSON')
        sub_val.add_argument('--type', '-t', choices=['standard', 'premium', 'avec_mobilier', 'multi_biens'])

        # Sous-commande: profils
        subparsers.add_parser('profils', help='Lister les profils')

        # Sous-commande: types
        subparsers.add_parser('types', help='Lister les types')

        args = parser.parse_args(sys.argv[2:])

        gestionnaire = GestionnairePromesses()

        if args.action == 'generer':
            donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))

            # Appliquer profil si spécifié
            if args.profil:
                donnees = gestionnaire.appliquer_profil(donnees, args.profil)

            # Forcer le type si spécifié
            type_force = TypePromesse(args.type) if args.type else None
            output_dir = Path(args.output) if args.output else None

            resultat = gestionnaire.generer(donnees, type_force, output_dir)

            print(f"\n{'='*60}")
            print("GÉNÉRATION PROMESSE")
            print(f"{'='*60}\n")
            print(f"  Succès: {'✓' if resultat.succes else '✗'}")
            print(f"  Type: {resultat.type_promesse.value}")
            print(f"  Durée: {resultat.duree_generation:.2f}s")
            if resultat.fichier_md:
                print(f"  Markdown: {resultat.fichier_md}")
            if resultat.fichier_docx:
                print(f"  DOCX: {resultat.fichier_docx}")
            if resultat.sections_incluses:
                print(f"  Sections: {len(resultat.sections_incluses)}")
            if resultat.erreurs:
                print(f"\n  Erreurs: {resultat.erreurs}")
            if resultat.warnings:
                print(f"  Warnings: {resultat.warnings}")

        elif args.action == 'depuis-titre':
            titre = json.loads(Path(args.titre).read_text(encoding='utf-8'))
            beneficiaires = json.loads(Path(args.beneficiaires).read_text(encoding='utf-8'))
            prix = {"montant": args.prix}

            financement = None
            if args.financement:
                financement = json.loads(Path(args.financement).read_text(encoding='utf-8'))

            output_dir = Path(args.output) if args.output else None

            donnees, resultat = gestionnaire.generer_depuis_titre(
                titre_data=titre,
                beneficiaires=beneficiaires,
                prix=prix,
                financement=financement,
                options={"output_dir": output_dir} if output_dir else None
            )

            print(f"\n{'='*60}")
            print("GÉNÉRATION DEPUIS TITRE")
            print(f"{'='*60}\n")
            print(f"  Succès: {'✓' if resultat.succes else '✗'}")
            print(f"  Type: {resultat.type_promesse.value}")
            if resultat.fichier_docx:
                print(f"  DOCX: {resultat.fichier_docx}")
            if resultat.erreurs:
                print(f"  Erreurs: {resultat.erreurs}")

        elif args.action == 'detecter':
            donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
            resultat = gestionnaire.detecter_type(donnees)

            print(f"\n{'='*60}")
            print("DÉTECTION TYPE PROMESSE")
            print(f"{'='*60}\n")
            print(f"  Type: {resultat.type_promesse.value}")
            print(f"  Raison: {resultat.raison}")
            print(f"  Confiance: {resultat.confiance:.0%}")
            print(f"  Sections: {len(resultat.sections_recommandees)}")
            if resultat.warnings:
                print(f"  Warnings: {resultat.warnings}")

        elif args.action == 'valider':
            donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
            type_promesse = TypePromesse(args.type) if args.type else None

            resultat = gestionnaire.valider(donnees, type_promesse)

            print(f"\n{'='*60}")
            print("VALIDATION DONNÉES")
            print(f"{'='*60}\n")
            print(f"  Valide: {'✓' if resultat.valide else '✗'}")
            if resultat.erreurs:
                print(f"\n  Erreurs:")
                for e in resultat.erreurs:
                    print(f"    - {e}")
            if resultat.warnings:
                print(f"\n  Warnings:")
                for w in resultat.warnings:
                    print(f"    - {w}")
            if resultat.champs_manquants:
                print(f"\n  Champs manquants:")
                for c in resultat.champs_manquants:
                    print(f"    - {c}")
            if resultat.suggestions:
                print(f"\n  Suggestions:")
                for s in resultat.suggestions:
                    print(f"    - {s}")

        elif args.action == 'profils':
            profils = gestionnaire.get_profils_disponibles()

            print(f"\n{'='*60}")
            print(f"PROFILS DISPONIBLES ({len(profils)})")
            print(f"{'='*60}\n")

            for p in profils:
                print(f"  • {p['id']}")
                print(f"    Type: {p['type_promesse']}")
                print(f"    Description: {p['description']}")
                print(f"    Sections: {p['sections_count']}")
                print()

        elif args.action == 'types':
            types_info = gestionnaire.catalogue.get("types_promesse", {})

            print(f"\n{'='*60}")
            print(f"TYPES DE PROMESSE ({len(types_info)})")
            print(f"{'='*60}\n")

            for tid, tdata in types_info.items():
                print(f"  • {tid}")
                print(f"    Nom: {tdata.get('nom')}")
                print(f"    Description: {tdata.get('description')}")
                print(f"    Bookmarks: {tdata.get('bookmarks')}")
                print(f"    Cas d'usage: {', '.join(tdata.get('cas_usage', []))}")
                print()

        else:
            parser.print_help()

    # =========================================================================
    # Commande inconnue
    # =========================================================================
    else:
        print(f"❌ Commande inconnue: {commande}")
        print("   Utilisez 'python notaire.py --help' pour l'aide")


if __name__ == '__main__':
    main()
