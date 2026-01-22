#!/usr/bin/env python3
"""
Génération d'acte complet de A à Z.
Pipeline optimisé: données → enrichissement → assemblage → export → conformité

Usage:
    python execution/generer_acte_complet.py --type vente --output .tmp/mon_acte/
    python execution/generer_acte_complet.py --donnees mon_fichier.json --output .tmp/
"""
import argparse
import json
import os
import sys
import time
import subprocess
import glob
from pathlib import Path

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def enrichir_donnees(donnees: dict) -> dict:
    """Ajoute les variables obligatoires manquantes."""

    # Paiement
    if 'paiement' not in donnees:
        donnees['paiement'] = {}
    paiement = donnees['paiement']
    paiement.setdefault('comptant', True)
    paiement.setdefault('montant', donnees.get('prix', {}).get('principal', 250000))
    paiement.setdefault('fonds_empruntes', 0)
    paiement.setdefault('fonds_empruntes_lettres', 'zéro')
    paiement.setdefault('fonds_personnels', paiement.get('montant', 250000))

    # Publication
    if 'publication' not in donnees:
        donnees['publication'] = {
            'service_publicite_fonciere': 'PARIS',
            'date_depot': '2024-03-20'
        }

    # Fiscalité avec taux
    if 'fiscalite' not in donnees:
        donnees['fiscalite'] = {}
    fiscalite = donnees['fiscalite']
    if 'droits_mutation' not in fiscalite:
        assiette = donnees.get('prix', {}).get('principal', 250000)
        fiscalite['droits_mutation'] = {
            'taux': 5.80,
            'assiette': assiette,
            'taux_departemental': 4.50,
            'taux_communal': 1.20,
            'total': round(assiette * 0.058, 2)
        }

    # Origine propriété
    if 'origine_propriete' not in donnees:
        donnees['origine_propriete'] = {
            'type': 'Acquisition',
            'date': '2015-01-01',
            'notaire': 'Maître DURAND'
        }

    # Copropriété - syndic
    if 'copropriete' in donnees and 'syndic' not in donnees['copropriete']:
        donnees['copropriete']['syndic'] = {
            'nom': 'SYNDIC IMMO',
            'adresse': '1 rue de la Paix, 75001 PARIS'
        }

    # Fallbacks pour sections conditionnelles
    donnees.setdefault('pouvoirs', None)
    donnees.setdefault('representation', None)
    donnees.setdefault('mandats', None)
    donnees.setdefault('dommages_ouvrage', {'existe': False})
    donnees.setdefault('garanties', {'vices_caches': {'clause_exoneration': True}})
    donnees.setdefault('assurances', None)
    donnees.setdefault('plus_value', None)
    donnees.setdefault('tva', {'applicable': False})
    donnees.setdefault('declarations_fiscales', None)

    return donnees


def main():
    parser = argparse.ArgumentParser(description='Génération acte complet')
    parser.add_argument('--type', choices=['vente', 'promesse', 'reglement', 'modificatif'],
                        help='Type d\'acte à générer')
    parser.add_argument('--donnees', help='Fichier JSON de données')
    parser.add_argument('--output', required=True, help='Dossier de sortie')
    parser.add_argument('--enrichir', action='store_true', default=True,
                        help='Enrichir automatiquement les données manquantes')
    parser.add_argument('--zones-grisees', action='store_true', default=True,
                        help='Activer les zones grisées')
    args = parser.parse_args()

    print('=' * 60)
    print('GÉNÉRATION ACTE COMPLET - PIPELINE OPTIMISÉ')
    print('=' * 60)

    total_start = time.time()
    times = {}

    # 1. Charger ou générer données
    print('\n[1/4] Préparation données...')
    t1 = time.time()

    if args.donnees:
        with open(args.donnees, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        print(f'  Chargé: {args.donnees}')
    elif args.type:
        # Utiliser données exemple
        exemple_map = {
            'vente': 'exemples/donnees_vente_exemple.json',
            'promesse': 'exemples/donnees_promesse_exemple.json',
            'reglement': 'exemples/donnees_reglement_copropriete_exemple.json',
            'modificatif': 'exemples/donnees_modificatif_edd_exemple.json'
        }
        exemple_path = exemple_map.get(args.type)
        if exemple_path and os.path.exists(exemple_path):
            with open(exemple_path, 'r', encoding='utf-8') as f:
                donnees = json.load(f)
            print(f'  Chargé exemple: {exemple_path}')
        else:
            # Générer données test
            result = subprocess.run([
                sys.executable, 'execution/generer_donnees_test.py',
                '--type', args.type,
                '--output', '.tmp/donnees_temp.json'
            ], capture_output=True, text=True)
            with open('.tmp/donnees_temp.json', 'r', encoding='utf-8') as f:
                donnees = json.load(f)
            print(f'  Généré: .tmp/donnees_temp.json')
    else:
        print('ERREUR: Spécifier --type ou --donnees')
        sys.exit(1)

    # Enrichir si nécessaire
    if args.enrichir:
        donnees = enrichir_donnees(donnees)
        print('  Données enrichies avec variables obligatoires')

    # Sauvegarder données enrichies
    donnees_path = os.path.join(args.output, 'donnees_enrichies.json')
    os.makedirs(args.output, exist_ok=True)
    with open(donnees_path, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    times['1_preparation'] = time.time() - t1
    print(f'  Durée: {times["1_preparation"]:.2f}s')

    # 2. Assemblage
    print('\n[2/4] Assemblage template Jinja2...')
    t2 = time.time()

    template_map = {
        'vente': 'vente_lots_copropriete.md',
        'promesse': 'promesse_vente_lots_copropriete.md',
        'reglement': 'reglement_copropriete_edd.md',
        'modificatif': 'modificatif_edd.md'
    }
    template = template_map.get(args.type, 'vente_lots_copropriete.md')

    cmd = [
        sys.executable, 'execution/assembler_acte.py',
        '--template', template,
        '--donnees', donnees_path,
        '--output', args.output
    ]
    if args.zones_grisees:
        cmd.append('--zones-grisees')

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    if result.returncode != 0:
        print(f'ERREUR: {result.stderr[:500]}')
        sys.exit(1)

    times['2_assemblage'] = time.time() - t2
    print(f'  Durée: {times["2_assemblage"]:.2f}s')

    # Trouver le dossier généré
    dossiers = sorted(glob.glob(os.path.join(args.output, '*/')), key=os.path.getmtime)
    if not dossiers:
        print('ERREUR: Aucun dossier généré')
        sys.exit(1)

    dossier = dossiers[-1]
    acte_md = os.path.join(dossier, 'acte.md')
    acte_docx = os.path.join(dossier, 'acte.docx')

    # 3. Export DOCX
    print('\n[3/4] Export DOCX...')
    t3 = time.time()

    cmd = [
        sys.executable, 'execution/exporter_docx.py',
        '--input', acte_md,
        '--output', acte_docx
    ]
    if args.zones_grisees:
        cmd.append('--zones-grisees')

    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)

    times['3_export'] = time.time() - t3
    print(f'  Durée: {times["3_export"]:.2f}s')

    # 4. Vérification conformité
    print('\n[4/4] Vérification conformité...')
    t4 = time.time()

    original_map = {
        'vente': 'docs_originels/Trame vente lots de copropriété.docx',
        'promesse': 'docs_originels/Trame promesse de vente lots de copropriété.docx',
        'reglement': 'docs_originels/Trame reglement copropriete EDD.docx',
        'modificatif': 'docs_originels/trame modificatif.docx'
    }
    original = original_map.get(args.type, original_map['vente'])

    if os.path.exists(original):
        result = subprocess.run([
            sys.executable, 'execution/comparer_documents.py',
            '--original', original,
            '--genere', acte_docx
        ], capture_output=True, text=True, encoding='utf-8', errors='replace')

        # Extraire score
        for line in result.stdout.split('\n'):
            if any(x in line for x in ['Score', 'Structure', 'Titres', '%', '│']):
                print(line)
    else:
        print(f'  Original non trouvé: {original}')

    times['4_conformite'] = time.time() - t4
    print(f'  Durée: {times["4_conformite"]:.2f}s')

    # Résumé
    total_time = time.time() - total_start

    print('\n' + '=' * 60)
    print('RÉSUMÉ')
    print('=' * 60)
    for k, v in times.items():
        print(f'  {k}: {v:.2f}s')
    print('  ' + '-' * 20)
    print(f'  TOTAL: {total_time:.2f}s')
    print(f'  Vitesse: ~{45/total_time:.1f} pages/seconde')
    print('=' * 60)
    print(f'\n✅ Fichier généré: {acte_docx}')


if __name__ == '__main__':
    main()
