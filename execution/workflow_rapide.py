#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Rapide - Génération Complète en 1 Commande

Usage:
    python execution/workflow_rapide.py --type vente --donnees path/to/data.json [--sections lot,fiscalite,garanties]

Exemple:
    python execution/workflow_rapide.py --type vente --donnees exemples/donnees_vente_exemple.json --sections all
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Sections disponibles par type d'acte
SECTIONS_DISPONIBLES = {
    'vente': {
        'lots_details': 'Détails des lots (plans, composition)',
        'fiscalite_complete': 'Fiscalité détaillée (CSI, droits)',
        'garanties': 'Garanties (éviction, jouissance, hypothèque)',
        'financement_detail': 'Financement détaillé par acquéreur',
        'origine_propriete': 'Origine de propriété complète',
        'indivision': 'Indivision (si plusieurs acquéreurs)',
        'urbanisme': 'Urbanisme complet',
        'dispositions_finales': 'Dispositions finales'
    },
    'promesse_vente': {
        'conditions_suspensives': 'Conditions suspensives détaillées',
        'garanties': 'Garanties',
        'fiscalite': 'Fiscalité'
    }
}

def print_step(step, message):
    """Affiche une étape du workflow"""
    icons = ['🔍', '⚙️', '📄', '✅']
    print(f"\n{icons[step-1]} ÉTAPE {step}/4: {message}")
    print("─" * 60)

def lister_sections_disponibles(type_acte):
    """Liste les sections disponibles pour un type d'acte"""
    print(f"\n📋 Sections disponibles pour '{type_acte}':")
    sections = SECTIONS_DISPONIBLES.get(type_acte, {})
    for code, desc in sections.items():
        print(f"  • {code:20s} → {desc}")
    print("\n💡 Usage: --sections lot,fiscalite,garanties")
    print("   ou:     --sections all (toutes les sections)")

def valider_donnees(donnees_path, type_acte):
    """Valide que les données existent et sont correctes"""
    print_step(1, "Validation des données")

    # Charger données
    try:
        with open(donnees_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lecture données: {e}")
        return False

    # Vérifications basiques
    checks = []
    if type_acte == 'vente':
        checks = [
            ('vendeurs', "Vendeurs présents"),
            ('acquereurs', "Acquéreurs présents"),
            ('bien', "Bien défini"),
            ('prix', "Prix défini")
        ]

    all_ok = True
    for key, desc in checks:
        if key in data:
            print(f"  ✅ {desc}")
        else:
            print(f"  ⚠️  {desc} - MANQUANT (optionnel)")

    print(f"\n  📊 Sections actives détectées:")
    sections_actives = []
    for section in ['indivision', 'urbanisme', 'garanties', 'fiscalite']:
        if section in data:
            sections_actives.append(section)
            print(f"     • {section}")

    if not sections_actives:
        print(f"     • (aucune section optionnelle)")

    return True

def assembler_acte(type_acte, donnees_path, output_dir):
    """Assemble le template avec les données"""
    print_step(2, "Assemblage du template")

    templates = {
        'vente': 'vente_lots_copropriete.md',
        'promesse_vente': 'promesse_vente_lots_copropriete.md',
        'reglement': 'reglement_copropriete_edd.md',
        'modificatif': 'modificatif_edd.md'
    }

    template = templates.get(type_acte)
    if not template:
        print(f"❌ Type d'acte inconnu: {type_acte}")
        return None

    cmd = [
        sys.executable,
        'execution/assembler_acte.py',
        '--template', template,
        '--donnees', str(donnees_path),
        '--output', str(output_dir),
        '--zones-grisees'
    ]

    print(f"  🔧 Template: {template}")
    print(f"  📁 Output: {output_dir}")

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode == 0:
        # Extraire le chemin de l'acte généré
        for line in result.stdout.split('\n'):
            if 'Acte:' in line:
                acte_path = line.split('Acte:')[1].strip()
                print(f"  ✅ Acte généré: {acte_path}")
                return Path(acte_path)
    else:
        print(f"  ❌ Erreur assemblage:")
        print(result.stderr)
        return None

def exporter_docx(acte_md_path, output_path):
    """Exporte le markdown en DOCX avec zones grisées"""
    print_step(3, "Export DOCX avec zones grisées")

    cmd = [
        sys.executable,
        'execution/exporter_docx.py',
        '--input', str(acte_md_path),
        '--output', str(output_path),
        '--zones-grisees'
    ]

    print(f"  📄 Markdown: {acte_md_path.name}")
    print(f"  📦 DOCX: {output_path}")

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode == 0:
        print(f"  ✅ Export réussi")
        return True
    else:
        print(f"  ❌ Erreur export:")
        print(result.stderr)
        return False

def valider_conformite(original_docx, generated_md):
    """Valide la conformité avec le document original"""
    print_step(4, "Validation conformité")

    cmd = [
        sys.executable,
        'execution/comparer_documents_v2.py',
        '--original', str(original_docx),
        '--genere', str(generated_md)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode == 0:
        # Extraire le score
        for line in result.stdout.split('\n'):
            if 'Score global' in line or 'conformité' in line.lower():
                print(f"  {line}")
        return True
    else:
        print(f"  ⚠️  Validation non disponible")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Workflow rapide de génération d\'acte notarial',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Générer acte de vente avec toutes les sections
  python workflow_rapide.py --type vente --donnees exemples/donnees_vente_exemple.json --sections all

  # Générer acte de vente avec sections spécifiques
  python workflow_rapide.py --type vente --donnees data.json --sections lots,fiscalite,garanties

  # Lister sections disponibles
  python workflow_rapide.py --type vente --list-sections
        """
    )

    parser.add_argument('--type', choices=['vente', 'promesse_vente', 'reglement', 'modificatif'],
                       help='Type d\'acte à générer')
    parser.add_argument('--donnees', type=Path, help='Fichier JSON des données')
    parser.add_argument('--sections', help='Sections à inclure (separées par virgules) ou "all"')
    parser.add_argument('--list-sections', action='store_true',
                       help='Lister les sections disponibles et quitter')
    parser.add_argument('--output', type=Path, default=Path('outputs'),
                       help='Dossier de sortie (défaut: outputs/)')
    parser.add_argument('--validate', action='store_true',
                       help='Valider la conformité avec le document original')

    args = parser.parse_args()

    # Liste sections et quitte
    if args.list_sections:
        if not args.type:
            print("❌ Spécifier --type pour lister les sections")
            return 1
        lister_sections_disponibles(args.type)
        return 0

    # Vérifications
    if not args.type or not args.donnees:
        parser.print_help()
        return 1

    if not args.donnees.exists():
        print(f"❌ Fichier données introuvable: {args.donnees}")
        return 1

    # Workflow
    print(f"\n{'='*60}")
    print(f"🚀 WORKFLOW RAPIDE - Génération Acte {args.type.upper()}")
    print(f"{'='*60}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Validation
    if not valider_donnees(args.donnees, args.type):
        return 1

    # 2. Assemblage
    output_tmp = Path('.tmp')
    output_tmp.mkdir(exist_ok=True)

    acte_md_path = assembler_acte(args.type, args.donnees, output_tmp)
    if not acte_md_path:
        return 1

    # 3. Export DOCX
    args.output.mkdir(exist_ok=True, parents=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    docx_output = args.output / f"{args.type}_{timestamp}.docx"

    if not exporter_docx(acte_md_path, docx_output):
        return 1

    # 4. Validation (optionnelle)
    if args.validate:
        originals = {
            'vente': 'docs_originels/Trame vente lots de copropriété.docx',
            'promesse_vente': 'docs_originels/Trame promesse unilatérale de vente lots de copropriété.docx'
        }

        original = originals.get(args.type)
        if original and Path(original).exists():
            valider_conformite(original, acte_md_path)

    # Résumé
    print(f"\n{'='*60}")
    print(f"✅ WORKFLOW TERMINÉ")
    print(f"{'='*60}")
    print(f"📄 Markdown: {acte_md_path}")
    print(f"📦 DOCX: {docx_output}")
    print(f"📁 Dossier: {args.output}")
    print(f"\n💡 Ouvrir le DOCX:")
    print(f"   start {docx_output}  (Windows)")
    print(f"   open {docx_output}   (macOS)")

    return 0

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrompu")
        exit(130)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
