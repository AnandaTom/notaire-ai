#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse d'un fichier RTF pour extraire les marges et mise en page."""

import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def analyze_rtf(filepath):
    with open(filepath, 'rb') as f:
        content = f.read(15000).decode('latin-1', errors='ignore')

    print('=== ANALYSE DU FICHIER RTF ===')
    print(f'Fichier: {filepath}')
    print()

    # Patterns pour les marges (twips: 1 mm = 56.7 twips)
    margin_patterns = {
        'margl': 'Marge gauche',
        'margr': 'Marge droite',
        'margt': 'Marge haut',
        'margb': 'Marge bas',
        'gutter': 'Gouttiere',
    }

    page_patterns = {
        'paperw': 'Largeur page',
        'paperh': 'Hauteur page',
    }

    print('=== MARGES ===')
    for code, name in margin_patterns.items():
        pattern = '\\\\' + code + r'(\d+)'
        match = re.search(pattern, content)
        if match:
            twips = int(match.group(1))
            mm = twips / 56.7
            print(f'{name}: {twips} twips = {mm:.1f}mm')

    print('\n=== PAGE ===')
    for code, name in page_patterns.items():
        pattern = '\\\\' + code + r'(\d+)'
        match = re.search(pattern, content)
        if match:
            twips = int(match.group(1))
            mm = twips / 56.7
            print(f'{name}: {mm:.0f}mm')

    # Police
    match = re.search(r'\\fs(\d+)', content)
    if match:
        half_pts = int(match.group(1))
        print(f'Taille police par defaut: {half_pts/2}pt')

    # Marges miroir
    print('\n=== OPTIONS ===')
    if 'margmirror' in content:
        print('Marges miroir: OUI')
    else:
        print('Marges miroir: Non')

    if 'facingp' in content:
        print('Pages en vis-a-vis: OUI')

    # Afficher un extrait du RTF
    print('\n=== EXTRAIT RTF (en-tete) ===')
    print(content[:1500])

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'docs_originels/Trame promesse unilatérale de vente lots de copropriété.rtf'
    analyze_rtf(filepath)
