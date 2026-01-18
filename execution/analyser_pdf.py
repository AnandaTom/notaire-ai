#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyser_pdf.py
===============

Script d'analyse de PDF pour comparer la mise en forme.

Fonctionnalités:
- Extraction du texte avec positions
- Mesure des marges
- Analyse de la structure
- Comparaison entre deux PDFs

Usage:
    python analyser_pdf.py --input <fichier.pdf> [--compare <reference.pdf>]

Dépendances:
    pip install pymupdf pillow
"""

import argparse
from pathlib import Path
import sys

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def analyser_marges(doc, page_num: int = 0) -> dict:
    """
    Analyse les marges d'une page PDF.

    Args:
        doc: Document PyMuPDF
        page_num: Numéro de page à analyser

    Returns:
        Dict avec les marges mesurées
    """
    page = doc[page_num]
    rect = page.rect  # Dimensions de la page

    # Extraire tous les blocs de texte
    blocks = page.get_text("dict")["blocks"]

    if not blocks:
        return {"erreur": "Aucun contenu trouvé"}

    # Trouver les limites du contenu
    min_x = float('inf')
    max_x = 0
    min_y = float('inf')
    max_y = 0

    for block in blocks:
        if "lines" in block:  # Bloc de texte
            bbox = block["bbox"]
            min_x = min(min_x, bbox[0])
            max_x = max(max_x, bbox[2])
            min_y = min(min_y, bbox[1])
            max_y = max(max_y, bbox[3])

    # Calculer les marges (en points, 1 point = 1/72 inch)
    # Convertir en mm (1 inch = 25.4 mm)
    pt_to_mm = 25.4 / 72

    return {
        "page_largeur_mm": rect.width * pt_to_mm,
        "page_hauteur_mm": rect.height * pt_to_mm,
        "marge_gauche_mm": min_x * pt_to_mm,
        "marge_droite_mm": (rect.width - max_x) * pt_to_mm,
        "marge_haut_mm": min_y * pt_to_mm,
        "marge_bas_mm": (rect.height - max_y) * pt_to_mm,
        "contenu_largeur_mm": (max_x - min_x) * pt_to_mm,
        "contenu_hauteur_mm": (max_y - min_y) * pt_to_mm,
    }


def extraire_structure(doc, page_num: int = 0) -> list:
    """
    Extrait la structure du texte avec positions.

    Args:
        doc: Document PyMuPDF
        page_num: Numéro de page

    Returns:
        Liste des éléments avec leurs positions
    """
    page = doc[page_num]
    blocks = page.get_text("dict")["blocks"]

    elements = []
    pt_to_mm = 25.4 / 72

    for block in blocks:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            texte = ""
            font_info = set()

            for span in line["spans"]:
                texte += span["text"]
                font_info.add(f"{span['font']} {span['size']:.1f}pt")

            if texte.strip():
                bbox = line["bbox"]
                elements.append({
                    "texte": texte.strip()[:60] + ("..." if len(texte.strip()) > 60 else ""),
                    "x_mm": bbox[0] * pt_to_mm,
                    "y_mm": bbox[1] * pt_to_mm,
                    "largeur_mm": (bbox[2] - bbox[0]) * pt_to_mm,
                    "police": ", ".join(font_info),
                    "gras": "Bold" in str(font_info) or "bold" in str(font_info),
                })

    return elements


def convertir_en_image(doc, page_num: int = 0, dpi: int = 150) -> Path:
    """
    Convertit une page PDF en image PNG.

    Args:
        doc: Document PyMuPDF
        page_num: Numéro de page
        dpi: Résolution

    Returns:
        Chemin vers l'image générée
    """
    page = doc[page_num]

    # Matrice de zoom pour la résolution souhaitée
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    # Rendre la page
    pix = page.get_pixmap(matrix=mat)

    # Sauvegarder
    output_path = Path(f".tmp/pdf_page_{page_num + 1}.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(output_path))

    return output_path


def afficher_analyse(chemin_pdf: Path):
    """
    Affiche une analyse complète du PDF.
    """
    print(f"\n{'='*60}")
    print(f"ANALYSE PDF: {chemin_pdf.name}")
    print(f"{'='*60}\n")

    doc = fitz.open(str(chemin_pdf))

    print(f"Nombre de pages: {len(doc)}")
    print()

    # Analyse des marges
    print("MARGES (Page 1):")
    print("-" * 40)
    marges = analyser_marges(doc, 0)
    for cle, valeur in marges.items():
        if isinstance(valeur, float):
            print(f"  {cle}: {valeur:.1f}")
        else:
            print(f"  {cle}: {valeur}")
    print()

    # Structure des 20 premiers éléments
    print("STRUCTURE (20 premiers éléments):")
    print("-" * 40)
    elements = extraire_structure(doc, 0)

    for i, elem in enumerate(elements[:20]):
        gras_marker = "[B]" if elem["gras"] else "   "
        # Nettoyer le texte des caracteres speciaux
        texte_clean = elem['texte'].encode('ascii', 'replace').decode('ascii')
        print(f"  {gras_marker} x={elem['x_mm']:5.1f}mm | {texte_clean}")

    if len(elements) > 20:
        print(f"  ... et {len(elements) - 20} autres éléments")

    print()

    # Générer une image
    print("EXPORT IMAGE:")
    print("-" * 40)
    img_path = convertir_en_image(doc, 0)
    print(f"  Image générée: {img_path}")

    doc.close()

    return marges, elements


def comparer_pdfs(pdf1: Path, pdf2: Path):
    """
    Compare deux PDFs côte à côte.
    """
    print(f"\n{'='*60}")
    print("COMPARAISON DE PDFs")
    print(f"{'='*60}\n")

    doc1 = fitz.open(str(pdf1))
    doc2 = fitz.open(str(pdf2))

    marges1 = analyser_marges(doc1, 0)
    marges2 = analyser_marges(doc2, 0)

    print(f"{'Mesure':<25} | {'PDF 1':>10} | {'PDF 2':>10} | {'Diff':>10}")
    print("-" * 60)

    for cle in marges1:
        if isinstance(marges1[cle], float):
            v1 = marges1[cle]
            v2 = marges2.get(cle, 0)
            diff = v1 - v2
            print(f"{cle:<25} | {v1:>10.1f} | {v2:>10.1f} | {diff:>+10.1f}")

    doc1.close()
    doc2.close()


def main():
    parser = argparse.ArgumentParser(
        description="Analyse la mise en forme d'un PDF"
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help="Chemin du fichier PDF à analyser"
    )
    parser.add_argument(
        '--compare', '-c',
        type=Path,
        help="PDF de référence pour comparaison"
    )
    parser.add_argument(
        '--export-image',
        action='store_true',
        help="Exporter la première page en image"
    )

    args = parser.parse_args()

    if not PYMUPDF_AVAILABLE:
        print("[ERREUR] PyMuPDF non installe. Installez-le avec:")
        print("  pip install pymupdf")
        return 1

    if not args.input.exists():
        print(f"[ERREUR] Fichier non trouve: {args.input}")
        return 1

    if args.compare:
        if not args.compare.exists():
            print(f"[ERREUR] Fichier de comparaison non trouve: {args.compare}")
            return 1
        comparer_pdfs(args.input, args.compare)
    else:
        afficher_analyse(args.input)

    return 0


if __name__ == '__main__':
    sys.exit(main())
