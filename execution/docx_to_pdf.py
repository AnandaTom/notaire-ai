#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
docx_to_pdf.py
==============

Convertit un fichier DOCX en PDF en utilisant Microsoft Word ou LibreOffice.

Usage:
    python docx_to_pdf.py --input <acte.docx> --output <acte.pdf>

Méthodes de conversion (par ordre de préférence):
1. Microsoft Word (via docx2pdf) - Meilleure fidélité
2. LibreOffice en mode headless - Alternative gratuite

Installation des dépendances:
    pip install docx2pdf

Pour LibreOffice (optionnel):
    - Télécharger depuis https://www.libreoffice.org/
    - Ajouter au PATH ou spécifier le chemin via --libreoffice-path
"""

import argparse
import subprocess
import sys
from pathlib import Path
import shutil


def convert_with_word(docx_path: Path, pdf_path: Path) -> bool:
    """Convertit avec Microsoft Word via docx2pdf."""
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        return pdf_path.exists()
    except ImportError:
        print("[INFO] docx2pdf non installé. Installer avec: pip install docx2pdf")
        return False
    except Exception as e:
        print(f"[WARN] Erreur Word: {e}")
        return False


def find_libreoffice() -> str:
    """Trouve l'exécutable LibreOffice."""
    # Chemins courants sur Windows
    possible_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"C:\Program Files\LibreOffice\program\soffice.com",
    ]

    # Vérifier d'abord dans le PATH
    soffice = shutil.which("soffice")
    if soffice:
        return soffice

    # Chercher dans les chemins courants
    for path in possible_paths:
        if Path(path).exists():
            return path

    return None


def convert_with_libreoffice(docx_path: Path, pdf_path: Path, libreoffice_path: str = None) -> bool:
    """Convertit avec LibreOffice en mode headless."""
    soffice = libreoffice_path or find_libreoffice()

    if not soffice:
        print("[INFO] LibreOffice non trouvé.")
        return False

    try:
        # LibreOffice génère le PDF dans le répertoire de sortie spécifié
        output_dir = pdf_path.parent

        cmd = [
            soffice,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(docx_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"[WARN] LibreOffice stderr: {result.stderr}")
            return False

        # LibreOffice nomme le fichier avec le même nom que l'entrée
        generated_pdf = output_dir / (docx_path.stem + ".pdf")

        # Renommer si nécessaire
        if generated_pdf != pdf_path:
            if generated_pdf.exists():
                shutil.move(str(generated_pdf), str(pdf_path))

        return pdf_path.exists()

    except subprocess.TimeoutExpired:
        print("[WARN] LibreOffice timeout (120s)")
        return False
    except Exception as e:
        print(f"[WARN] Erreur LibreOffice: {e}")
        return False


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path, libreoffice_path: str = None) -> bool:
    """
    Convertit un DOCX en PDF en essayant plusieurs méthodes.

    Args:
        docx_path: Chemin du fichier DOCX source
        pdf_path: Chemin du fichier PDF de sortie
        libreoffice_path: Chemin optionnel vers LibreOffice

    Returns:
        True si la conversion a réussi, False sinon
    """
    if not docx_path.exists():
        print(f"[ERREUR] Fichier non trouvé: {docx_path}")
        return False

    # Créer le répertoire de sortie si nécessaire
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Méthode 1: Microsoft Word (meilleure qualité)
    print("[INFO] Tentative de conversion avec Microsoft Word...")
    if convert_with_word(docx_path, pdf_path):
        return True

    # Méthode 2: LibreOffice
    print("[INFO] Tentative de conversion avec LibreOffice...")
    if convert_with_libreoffice(docx_path, pdf_path, libreoffice_path):
        return True

    print("[ERREUR] Aucune méthode de conversion disponible.")
    print("Solutions:")
    print("  1. Installer docx2pdf: pip install docx2pdf (nécessite Microsoft Word)")
    print("  2. Installer LibreOffice: https://www.libreoffice.org/")
    return False


def main():
    parser = argparse.ArgumentParser(description='Convertir un DOCX en PDF')
    parser.add_argument('--input', '-i', type=Path, required=True,
                        help='Fichier DOCX source')
    parser.add_argument('--output', '-o', type=Path, required=True,
                        help='Fichier PDF de sortie')
    parser.add_argument('--libreoffice-path', type=str, default=None,
                        help='Chemin vers l\'exécutable LibreOffice (optionnel)')

    args = parser.parse_args()

    if convert_docx_to_pdf(args.input, args.output, args.libreoffice_path):
        taille = args.output.stat().st_size / 1024
        print(f"[OK] PDF généré: {args.output} ({taille:.1f} Ko)")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
