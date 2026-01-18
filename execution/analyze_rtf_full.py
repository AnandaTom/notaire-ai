#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse complete d'un fichier RTF."""

import re
import sys
from collections import Counter

def analyze_rtf(filepath):
    with open(filepath, 'rb') as f:
        content = f.read().decode('latin-1', errors='ignore')

    print('=== ANALYSE RTF COMPLETE ===')
    print(f'Fichier: {filepath}')
    print(f'Taille: {len(content)} caracteres')
    print()

    # Marges
    print('=== MARGES ===')
    margin_codes = {
        'margl': 'Marge gauche',
        'margr': 'Marge droite',
        'margt': 'Marge haut',
        'margb': 'Marge bas',
        'gutter': 'Gouttiere'
    }

    for code, name in margin_codes.items():
        pattern = r'\\' + code + r'(\d+)'
        match = re.search(pattern, content)
        if match:
            twips = int(match.group(1))
            mm = twips / 56.7
            print(f'{name}: {twips} twips = {mm:.1f}mm')

    # Marges miroir
    if 'margmirror' in content:
        print('Marges miroir: OUI')
    else:
        print('Marges miroir: Non')

    # Page
    print()
    print('=== PAGE ===')
    for code, name in [('paperw', 'Largeur'), ('paperh', 'Hauteur')]:
        pattern = r'\\' + code + r'(\d+)'
        match = re.search(pattern, content)
        if match:
            twips = int(match.group(1))
            mm = twips / 56.7
            print(f'{name}: {mm:.0f}mm')

    # Police
    print()
    print('=== POLICE ===')
    fs_matches = re.findall(r'\\fs(\d+)', content)
    if fs_matches:
        counter = Counter(int(v) for v in fs_matches)
        print('Tailles utilisees (half-points):')
        for half_pt, count in counter.most_common(5):
            print(f'  {half_pt/2}pt: {count} fois')

    # Espacement paragraphe
    print()
    print('=== ESPACEMENT PARAGRAPHE ===')

    # Space after
    sa_matches = re.findall(r'\\sa(\d+)', content)
    if sa_matches:
        counter = Counter(int(v) for v in sa_matches)
        print('Space after:')
        for twips, count in counter.most_common(10):
            pt = twips / 20
            print(f'  {pt:.0f}pt ({twips} twips): {count} fois')
    else:
        print('Aucun space after explicite (utilise defaut)')

    # Space before
    sb_matches = re.findall(r'\\sb(\d+)', content)
    if sb_matches:
        counter = Counter(int(v) for v in sb_matches)
        print('Space before:')
        for twips, count in counter.most_common(5):
            pt = twips / 20
            print(f'  {pt:.0f}pt ({twips} twips): {count} fois')

    # Interligne
    print()
    print('=== INTERLIGNE ===')
    sl_matches = re.findall(r'\\sl(\d+)', content)
    if sl_matches:
        counter = Counter(int(v) for v in sl_matches)
        for twips, count in counter.most_common(5):
            # 240 twips = simple, 360 = 1.5, 480 = double
            ratio = twips / 240
            print(f'  sl{twips} ({ratio:.2f}x): {count} fois')
    else:
        print('Interligne simple par defaut')

    # First line indent
    print()
    print('=== ALINEA (first line indent) ===')
    fi_matches = re.findall(r'\\fi(\d+)', content)
    if fi_matches:
        counter = Counter(int(v) for v in fi_matches)
        for twips, count in counter.most_common(5):
            mm = twips / 56.7
            print(f'  {twips} twips = {mm:.1f}mm: {count} fois')

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'docs_originels/Trame promesse unilatérale de vente lots de copropriété.rtf'
    analyze_rtf(filepath)
