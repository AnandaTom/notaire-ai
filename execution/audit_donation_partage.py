#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_donation_partage.py
=========================

Audit complet du document original Donation partage (2).pdf
pour reproduire EXACTEMENT la mise en page.

Basé sur audit_pdf_complet.py utilisé pour la vente de copropriété.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import PyPDF2
from docx import Document
from docx.shared import Pt, Mm

def audit_pdf():
    """Audit du PDF original"""
    pdf_path = Path('docs_originels/Donation partage (2).pdf')

    print("="*80)
    print("AUDIT DONATION-PARTAGE - PDF ORIGINAL")
    print("="*80)

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)

        print(f"\n📄 STATISTIQUES GLOBALES")
        print(f"   Nombre de pages: {num_pages}")

        # Analyser structure page 1
        print(f"\n📄 PAGE 1 - STRUCTURE HEADER")
        page1 = reader.pages[0]
        text1 = page1.extract_text()
        lines1 = [l.strip() for l in text1.split('\n') if l.strip()]

        print(f"   Nombre de lignes: {len(lines1)}")
        print(f"\n   🔍 Détail (30 premières lignes):")
        for i, line in enumerate(lines1[:30], 1):
            prefix = "   "
            if "DONATION-PARTAGE" in line:
                prefix = ">>> "  # Marquer le titre
            elif "100583001" in line:
                prefix = "REF "
            elif any(word in line for word in ["ELEMENTS", "TERMINOLOGIE", "DECLARATIONS"]):
                prefix = "BOX "
            print(f"{prefix}{i:2d}. {line}")

        # Page 2-3 - Éléments préalables avec encadrés
        print(f"\n📄 PAGE 2-3 - ELEMENTS PREALABLES (encadrés)")
        for page_num in [1, 2]:
            page = reader.pages[page_num]
            text = page.extract_text()
            lines = [l.strip() for l in text.split('\n') if l.strip()]

            print(f"\n   Page {page_num+1}:")
            for i, line in enumerate(lines[:20], 1):
                if any(kw in line for kw in ["ELEMENTS", "TERMINOLOGIE", "DECLARATIONS", "DOCUMENTS"]):
                    print(f"   BOX {i:2d}. {line}")

        # Page 7 - DONATION-PARTAGE encadré
        print(f"\n📄 PAGE 7 - DONATION-PARTAGE (titre encadré)")
        page7 = reader.pages[6]
        text7 = page7.extract_text()
        lines7 = [l.strip() for l in text7.split('\n') if l.strip()]

        for i, line in enumerate(lines7[:15], 1):
            if "DONATION-PARTAGE" in line or "PARTAGE" in line:
                print(f"   BOX {i:2d}. {line}")
            elif i <= 5:
                print(f"       {i:2d}. {line}")

        # Calculer densité moyenne
        total_chars = sum(len(reader.pages[i].extract_text()) for i in range(num_pages))
        avg_chars_per_page = total_chars / num_pages

        print(f"\n📊 STATISTIQUES CONTENU")
        print(f"   Caractères totaux: {total_chars}")
        print(f"   Moyenne par page: {avg_chars_per_page:.0f} caractères")
        print(f"   Estimation mots/page: {avg_chars_per_page / 5:.0f} mots")


def analyser_structure_encadres():
    """Analyser précisément où sont les encadrés"""
    pdf_path = Path('docs_originels/Donation partage (2).pdf')

    print(f"\n{'='*80}")
    print("ANALYSE DES ENCADRÉS")
    print("="*80)

    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)

        # Rechercher tous les titres encadrés
        encadres = []

        for page_num in range(min(10, len(reader.pages))):
            page = reader.pages[page_num]
            text = page.extract_text()
            lines = [l.strip() for l in text.split('\n') if l.strip()]

            for i, line in enumerate(lines):
                # Détecter les titres en majuscules (probablement encadrés)
                if line.isupper() and len(line) > 5:
                    if any(kw in line for kw in [
                        "ELEMENTS", "TERMINOLOGIE", "DECLARATIONS", "DOCUMENTS",
                        "EXPOSE", "DONATION-PARTAGE", "PREMIERE PARTIE",
                        "DEUXIEME PARTIE", "TROISIEME PARTIE", "QUATRIEME PARTIE"
                    ]):
                        encadres.append({
                            'page': page_num + 1,
                            'ligne': i + 1,
                            'texte': line
                        })

        print(f"\n📦 TITRES ENCADRÉS DÉTECTÉS:")
        for enc in encadres:
            print(f"   Page {enc['page']}, ligne {enc['ligne']:2d}: {enc['texte']}")


if __name__ == '__main__':
    audit_pdf()
    analyser_structure_encadres()

    print(f"\n{'='*80}")
    print("RECOMMANDATIONS POUR LE TEMPLATE")
    print("="*80)
    print("""
1. PAGE 1 - Structure:
   Ligne 1: Référence (ex: 100583001)
   Ligne 2: Initiales (ex: CDI/ALG/)
   Ligne 3: Date (ex: Le 23 décembre 2025)
   Ligne 4: **DONATION-PARTAGE** (TITRE EN GRAS)
   Ligne 5-7: Info donateurs + astérisques
   Ligne 8+: L'AN DEUX MILLE...

2. ENCADRÉS (uniquement sur les TITRES):
   - ELEMENTS PREALABLES
   - TERMINOLOGIE
   - DECLARATIONS DES PARTIES
   - DOCUMENTS RELATIFS A LA CAPACITE ET A LA QUALITE DES PARTIES
   - EXPOSE PREALABLE
   - DONATION-PARTAGE (page 7)
   - PREMIERE PARTIE, DEUXIEME PARTIE, etc.

3. FORMATAGE:
   - Encadrés = tableaux Word 1x1 avec bordures
   - Pas de contenu dans les encadrés, juste le titre
   - Espacement: 6pt après titres encadrés

4. PAGINATION:
   - Original: 29 pages (28 + couverture)
   - Objectif: reproduire exactement
""")
    print("="*80)
