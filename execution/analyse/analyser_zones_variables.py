#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyser_zones_variables_v2.py
==============================

Version améliorée: analyse approfondie du XML pour détecter TOUTES les zones
avec mise en forme spéciale (grisé, surligné, couleur de fond, champs, etc.)

Usage:
    python analyser_zones_variables_v2.py --input <document.docx>
"""

import argparse
import json
import re
import zipfile
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET

# Namespace Word
NSMAP = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
}


def extraire_xml_document(docx_path: Path) -> dict:
    """Extrait les fichiers XML du DOCX."""
    xmls = {}
    with zipfile.ZipFile(docx_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.xml'):
                xmls[name] = z.read(name).decode('utf-8')
    return xmls


def analyser_runs_avec_formatage(xml_content: str) -> list:
    """
    Analyse le document.xml pour trouver tous les runs avec formatage spécial.
    """
    root = ET.fromstring(xml_content)

    zones = []

    # Trouver tous les paragraphes
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        para_text_parts = []

        # Extraire le texte et le formatage de chaque run
        for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
            run_text = ''
            formatage = {}

            # Extraire le texte
            for t in run.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    run_text += t.text

            if not run_text.strip():
                continue

            # Analyser les propriétés du run (rPr)
            rPr = run.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
            if rPr is not None:
                # Surlignage (highlight)
                highlight = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}highlight')
                if highlight is not None:
                    val = highlight.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if val and val.lower() not in ['none', 'white']:
                        formatage['highlight'] = val

                # Ombrage (shading)
                shd = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
                if shd is not None:
                    fill = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                    color = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color')
                    if fill and fill.lower() not in ['auto', 'ffffff', '']:
                        formatage['shading_fill'] = fill
                    if color and color.lower() not in ['auto', '000000', '']:
                        formatage['shading_color'] = color

                # Couleur du texte (color)
                color = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color')
                if color is not None:
                    val = color.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')
                    if val and val.lower() not in ['auto', '000000', 'black']:
                        formatage['text_color'] = val

            para_text_parts.append((run_text, formatage))

        # Reconstituer le texte du paragraphe
        para_full_text = ''.join([t for t, _ in para_text_parts])

        # Enregistrer les zones avec formatage
        for run_text, formatage in para_text_parts:
            if formatage:
                zones.append({
                    'texte': run_text.strip(),
                    'formatage': formatage,
                    'contexte_paragraphe': para_full_text[:200]
                })

    return zones


def detecter_champs_formulaire(xml_content: str) -> list:
    """
    Détecte les champs de formulaire (fldSimple, fldChar, etc.)
    """
    root = ET.fromstring(xml_content)
    champs = []

    # Champs simples
    for fld in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldSimple'):
        instr = fld.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr', '')
        texte = ''.join(t.text or '' for t in fld.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        champs.append({
            'type': 'fldSimple',
            'instruction': instr,
            'texte': texte.strip()
        })

    # Champs complexes (bookmarks qui peuvent être des champs de formulaire)
    for bookmark in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkStart'):
        name = bookmark.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name', '')
        if name and not name.startswith('_'):
            champs.append({
                'type': 'bookmark',
                'nom': name
            })

    return champs


def extraire_tout_le_texte(xml_content: str) -> str:
    """Extrait tout le texte du document."""
    root = ET.fromstring(xml_content)
    textes = []

    for t in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
        if t.text:
            textes.append(t.text)

    return ' '.join(textes)


def detecter_patterns_variables_dans_texte(texte: str) -> list:
    """
    Détecte les patterns typiques de variables/placeholders dans le texte:
    - Texte entre crochets [...]
    - Texte entre parenthèses avec points de suspension (...)
    - Points de suspension ....
    - Tirets répétés ----
    - Espaces underscorés ____
    - Formulations type "ci-après dénommé", "représenté par"
    """
    patterns = []

    # Crochets avec contenu
    for m in re.finditer(r'\[([^\]]+)\]', texte):
        patterns.append({'type': 'crochets', 'texte': m.group(1), 'complet': m.group(0)})

    # Points de suspension (3 ou plus)
    for m in re.finditer(r'\.{3,}', texte):
        # Capturer le contexte autour
        start = max(0, m.start() - 50)
        end = min(len(texte), m.end() + 50)
        patterns.append({'type': 'ellipsis', 'contexte': texte[start:end]})

    # Tirets répétés (placeholder)
    for m in re.finditer(r'-{3,}|_{3,}', texte):
        start = max(0, m.start() - 50)
        end = min(len(texte), m.end() + 50)
        patterns.append({'type': 'placeholder_tirets', 'contexte': texte[start:end]})

    # Mots en MAJUSCULES isolés (potentiellement des placeholders)
    for m in re.finditer(r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b', texte):
        mot = m.group(0)
        # Filtrer les mots courants
        mots_courants = ['LE', 'LA', 'LES', 'DE', 'DU', 'DES', 'ET', 'OU', 'UN', 'UNE',
                        'CE', 'SA', 'SON', 'SES', 'AU', 'AUX', 'PAR', 'POUR', 'AVEC',
                        'SUR', 'EN', 'EST', 'SONT', 'QUI', 'QUE', 'EUR', 'EUROS']
        if mot not in mots_courants and len(mot) > 2:
            patterns.append({'type': 'majuscules', 'texte': mot})

    return patterns


def identifier_variables_notariales(texte_complet: str) -> dict:
    """
    Identifie les types de variables spécifiques aux actes notariaux.
    """
    variables = {
        'parties': {
            'vendeurs': [],
            'acquereurs': []
        },
        'bien': {
            'adresse': [],
            'cadastre': [],
            'lots': [],
            'superficie': []
        },
        'financier': {
            'prix': [],
            'prets': [],
            'frais': []
        },
        'dates': [],
        'references': {
            'notaire': [],
            'acte': [],
            'copropriete': []
        }
    }

    # Patterns pour chaque catégorie
    patterns = {
        'vendeur': [
            r'VENDEUR[S]?\s*[:\-]?\s*([^\n]+)',
            r'(?:Monsieur|Madame|M\.|Mme)\s+([A-ZÉÈÊËÀÂÄÙÛÜÎÏÔÖÇ][A-Za-zéèêëàâäùûüîïôöç\-]+(?:\s+[A-ZÉÈÊËÀÂÄÙÛÜÎÏÔÖÇ][A-Za-zéèêëàâäùûüîïôöç\-]+)*)',
        ],
        'acquereur': [
            r'ACQ[UÉ]REUR[S]?\s*[:\-]?\s*([^\n]+)',
        ],
        'adresse': [
            r'(\d+[,\s]+(?:rue|avenue|boulevard|place|allée|impasse|chemin)[^,\n]+)',
            r'(\d{5}\s+[A-ZÉÈÊËÀÂÄÙÛÜÎÏÔÖÇ][A-Za-zéèêëàâäùûüîïôöç\-\s]+)',
        ],
        'cadastre': [
            r'section\s+([A-Z]{1,2})',
            r'n[°o]\s*(\d+)',
            r'lieudit\s+["\']?([^"\']+)["\']?',
        ],
        'prix': [
            r'(\d[\d\s]*(?:,\d{2})?\s*(?:€|euros?))',
            r'prix\s*[:\-]?\s*(\d[\d\s]*)',
        ],
        'dates': [
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})',
        ]
    }

    for cat, pats in patterns.items():
        for pat in pats:
            for m in re.finditer(pat, texte_complet, re.IGNORECASE):
                if cat == 'vendeur':
                    variables['parties']['vendeurs'].append(m.group(0))
                elif cat == 'acquereur':
                    variables['parties']['acquereurs'].append(m.group(0))
                elif cat == 'adresse':
                    variables['bien']['adresse'].append(m.group(0))
                elif cat == 'cadastre':
                    variables['bien']['cadastre'].append(m.group(0))
                elif cat == 'prix':
                    variables['financier']['prix'].append(m.group(0))
                elif cat == 'dates':
                    variables['dates'].append(m.group(0))

    return variables


def analyser_document_complet(docx_path: Path) -> dict:
    """
    Analyse complète du document DOCX.
    """
    print(f"Analyse approfondie de: {docx_path}")

    # Extraire les XMLs
    xmls = extraire_xml_document(docx_path)

    document_xml = xmls.get('word/document.xml', '')
    if not document_xml:
        print("[ERREUR] document.xml non trouvé")
        return {}

    # Analyses
    zones_formatees = analyser_runs_avec_formatage(document_xml)
    champs = detecter_champs_formulaire(document_xml)
    texte_complet = extraire_tout_le_texte(document_xml)
    patterns_texte = detecter_patterns_variables_dans_texte(texte_complet)
    variables_notariales = identifier_variables_notariales(texte_complet)

    # Statistiques
    rapport = {
        'fichier': str(docx_path),
        'statistiques': {
            'zones_formatees': len(zones_formatees),
            'champs_formulaire': len(champs),
            'patterns_texte': len(patterns_texte),
            'longueur_texte': len(texte_complet)
        },
        'zones_avec_formatage_special': zones_formatees,
        'champs_formulaire': champs,
        'patterns_dans_texte': patterns_texte,
        'variables_notariales_detectees': variables_notariales,
        'texte_complet': texte_complet
    }

    return rapport


def afficher_rapport(rapport: dict):
    """Affiche un résumé du rapport."""
    print("\n" + "="*70)
    print("RAPPORT D'ANALYSE DES VARIABLES")
    print("="*70)

    stats = rapport.get('statistiques', {})
    print(f"\nStatistiques:")
    print(f"  - Zones avec formatage spécial: {stats.get('zones_formatees', 0)}")
    print(f"  - Champs de formulaire: {stats.get('champs_formulaire', 0)}")
    print(f"  - Patterns détectés dans le texte: {stats.get('patterns_texte', 0)}")
    print(f"  - Longueur du texte: {stats.get('longueur_texte', 0)} caractères")

    # Zones formatées
    zones = rapport.get('zones_avec_formatage_special', [])
    if zones:
        print(f"\n--- Zones avec formatage spécial ({len(zones)}) ---")
        for i, z in enumerate(zones[:20], 1):  # Limiter à 20
            print(f"  {i}. \"{z['texte'][:50]}...\" | Formatage: {z['formatage']}")

    # Patterns
    patterns = rapport.get('patterns_dans_texte', [])
    if patterns:
        print(f"\n--- Patterns détectés ({len(patterns)}) ---")
        types_count = defaultdict(int)
        for p in patterns:
            types_count[p['type']] += 1
        for t, c in types_count.items():
            print(f"  - {t}: {c} occurrences")

    # Variables notariales
    vars_not = rapport.get('variables_notariales_detectees', {})
    print("\n--- Variables notariales identifiées ---")
    for cat, sous_cats in vars_not.items():
        if isinstance(sous_cats, dict):
            for sous_cat, vals in sous_cats.items():
                if vals:
                    print(f"  {cat}/{sous_cat}: {len(vals)} éléments")
        elif isinstance(sous_cats, list) and sous_cats:
            print(f"  {cat}: {len(sous_cats)} éléments")


def main():
    parser = argparse.ArgumentParser(
        description="Analyse approfondie des zones variables d'un DOCX"
    )
    parser.add_argument('--input', '-i', type=Path, required=True)
    parser.add_argument('--output', '-o', type=Path, help="Fichier JSON de sortie")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"[ERREUR] Fichier non trouvé: {args.input}")
        return 1

    rapport = analyser_document_complet(args.input)
    afficher_rapport(rapport)

    if args.output:
        # Ne pas sauvegarder le texte complet pour éviter fichier trop gros
        rapport_save = {k: v for k, v in rapport.items() if k != 'texte_complet'}
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(rapport_save, f, ensure_ascii=False, indent=2)
        print(f"\nRapport sauvegardé: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
