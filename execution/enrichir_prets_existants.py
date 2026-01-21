#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichir les prêts existants avec champs calculés
Ajoute: mensualite, taux_nominal (depuis taux), etc.
"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def calculer_mensualite(montant, taux_annuel, duree_mois):
    """Calcule la mensualité d'un prêt amortissable"""
    if taux_annuel == 0:
        return montant / duree_mois

    taux_mensuel = taux_annuel / 100 / 12
    mensualite = montant * taux_mensuel / (1 - (1 + taux_mensuel) ** -duree_mois)
    return round(mensualite, 2)

def enrichir_prets(data: dict) -> dict:
    """Enrichit les prêts avec champs manquants"""

    if 'paiement' not in data or 'prets' not in data['paiement']:
        return data

    for pret in data['paiement']['prets']:
        # Taux nominal = taux (alignement noms)
        if 'taux' in pret and 'taux_nominal' not in pret:
            pret['taux_nominal'] = pret['taux']

        # Calculer mensualité si manquante
        if 'mensualite' not in pret:
            if all(k in pret for k in ['montant', 'taux', 'duree_mois']):
                pret['mensualite'] = calculer_mensualite(
                    pret['montant'],
                    pret['taux'],
                    pret['duree_mois']
                )

        # Type de taux par défaut
        if 'type_taux' not in pret:
            pret['type_taux'] = 'fixe'

        # Garantie si type_garantie existe
        if 'type_garantie' in pret and 'garantie' not in pret:
            if pret['type_garantie'] == 'hypotheque_legale_preteur':
                pret['garantie'] = {
                    'type': 'hypotheque',
                    'montant_inscription': round(pret['montant'] * 1.3, 2),
                    'rang': '1er rang'
                }

    return data

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Enrichir prêts existants')
    parser.add_argument('--input', '-i', required=True, help='Fichier données source')
    parser.add_argument('--output', '-o', help='Fichier données enrichies (défaut: écrase input)')

    args = parser.parse_args()

    # Charger
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Enrichir
    data = enrichir_prets(data)

    # Sauvegarder
    output = args.output or args.input
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    nb_prets = len(data.get('paiement', {}).get('prets', []))
    print(f'✅ {nb_prets} prêt(s) enrichi(s): {output}')
    print(f'   Ajouts: mensualite, taux_nominal, type_taux, garantie')

if __name__ == '__main__':
    main()
