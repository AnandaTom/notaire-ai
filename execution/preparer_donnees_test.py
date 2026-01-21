#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prépare les données de test en appliquant tous les enrichissements
Usage: python execution/preparer_donnees_test.py --input data.json [--vague 5]
"""
import subprocess
import sys
import json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def run_script(script, input_file, output_file=None):
    """Exécute un script d'enrichissement"""
    cmd = [sys.executable, script, '--input', input_file]
    if output_file:
        cmd.extend(['--output', output_file])

    result = subprocess.run(cmd, capture_output=True, text=True,
                          encoding='utf-8', errors='replace')
    return result.returncode == 0, result.stdout

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Prépare données de test avec enrichissements')
    parser.add_argument('--input', '-i', required=True, help='Fichier données source')
    parser.add_argument('--output', '-o', help='Fichier données préparées')
    parser.add_argument('--vague', type=int, default=6, choices=[3,4,5,6],
                       help='Niveau enrichissement (3=base, 4=+origine, 5=+sections H2, 6=+servitudes/état/équip)')

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Fichier introuvable: {args.input}")
        return 1

    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + '_prepare')

    print("🔧 PRÉPARATION DONNÉES DE TEST")
    print("="*60)
    print(f"📥 Source: {input_path}")
    print(f"📤 Cible: {output_path}")
    print(f"🎯 Vague: {args.vague}")
    print("")

    # Copier fichier source
    import shutil
    shutil.copy(input_path, output_path)

    # Étape 1: Données minimales (16 variables obligatoires)
    print("1️⃣  Enrichissement minimal (16 variables)...")
    success, stdout = run_script(
        'execution/generer_donnees_minimales.py',
        str(output_path),
        str(output_path)
    )
    if success:
        print("   ✅ Variables minimales ajoutées")
    else:
        print("   ⚠️  Déjà enrichi ou erreur")

    # Étape 2: Enrichir prêts
    print("2️⃣  Calcul mensualités prêts...")
    success, stdout = run_script(
        'execution/enrichir_prets_existants.py',
        str(output_path)
    )
    if success:
        print("   ✅ Prêts enrichis")
    else:
        print("   ⚠️  Aucun prêt ou erreur")

    # Étape 3+: Vagues enrichissement
    if args.vague >= 5:
        print("5️⃣  Enrichissement Vague 5 (Garanties, Fiscalité, Lots)...")

        # Vérifier si script Vague 5 existe et utilise le bon fichier source
        vague5_script = Path('.tmp/enrichir_donnees_vague5.py')
        if vague5_script.exists():
            # Modifier temporairement le script pour utiliser notre fichier
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False,
                                            encoding='utf-8') as tmp:
                tmp_path = tmp.name
                with open(vague5_script, 'r', encoding='utf-8') as f:
                    script_content = f.read()

                # Modifier les chemins
                script_content = script_content.replace(
                    "with open('.tmp/donnees_test_vague3_enrichi.json'",
                    f"with open('{output_path}'"
                )
                script_content = script_content.replace(
                    "with open('.tmp/donnees_test_vague5_enrichi.json'",
                    f"with open('{output_path}'"
                )
                tmp.write(script_content)

            # Exécuter script modifié
            result = subprocess.run([sys.executable, tmp_path],
                                  capture_output=True, text=True,
                                  encoding='utf-8', errors='replace')
            Path(tmp_path).unlink()  # Supprimer fichier temporaire

            if result.returncode == 0:
                print("   ✅ Vague 5 appliquée")
            else:
                print("   ⚠️  Erreur Vague 5")
        else:
            print("   ⏭️  Script Vague 5 non trouvé")

    if args.vague >= 6:
        print("6️⃣  Enrichissement Vague 6 (Servitudes, État bien, Équipements)...")

        vague6_script = Path('.tmp/enrichir_donnees_vague6.py')
        if vague6_script.exists():
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False,
                                            encoding='utf-8') as tmp:
                tmp_path = tmp.name
                with open(vague6_script, 'r', encoding='utf-8') as f:
                    script_content = f.read()

                # Modifier les chemins
                script_content = script_content.replace(
                    "with open('.tmp/donnees_test_vague5_enrichi.json'",
                    f"with open('{output_path}'"
                )
                script_content = script_content.replace(
                    "with open('.tmp/donnees_test_vague6_enrichi.json'",
                    f"with open('{output_path}'"
                )
                tmp.write(script_content)

            # Exécuter script modifié
            result = subprocess.run([sys.executable, tmp_path],
                                  capture_output=True, text=True,
                                  encoding='utf-8', errors='replace')
            Path(tmp_path).unlink()

            if result.returncode == 0:
                print("   ✅ Vague 6 appliquée")
            else:
                print("   ⚠️  Erreur Vague 6")
        else:
            print("   ⏭️  Script Vague 6 non trouvé")

    # Résumé
    print("")
    print("="*60)
    print(f"✅ DONNÉES PRÉPARÉES: {output_path}")

    # Vérifier contenu
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sections = []
    if 'urbanisme' in data: sections.append('urbanisme')
    if 'indivision' in data: sections.append('indivision')
    if 'garanties' in data: sections.append('garanties')
    if 'fiscalite' in data: sections.append('fiscalite')
    if 'servitudes' in data: sections.append('servitudes')
    if 'etat_bien' in data: sections.append('etat_bien')
    if 'equipements' in data: sections.append('equipements')
    if 'paiement' in data and 'prets' in data['paiement']:
        if data['paiement']['prets'] and 'mensualite' in data['paiement']['prets'][0]:
            sections.append('prets_enrichis')

    print(f"📊 Sections présentes: {', '.join(sections)}")
    print("")
    print("💡 Tester l'assemblage:")
    print(f"   python execution/assembler_acte.py \\")
    print(f"     --template vente_lots_copropriete.md \\")
    print(f"     --donnees {output_path} \\")
    print(f"     --output .tmp/test/ --zones-grisees")

    return 0

if __name__ == '__main__':
    exit(main())
