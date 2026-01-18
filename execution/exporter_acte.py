#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exporter_acte.py
================

Script unifié pour exporter un acte notarial vers DOCX et/ou PDF.

Workflow: Markdown/HTML → DOCX → PDF (via Microsoft Word)

Usage:
    python exporter_acte.py --input <acte.md> --output <acte.pdf>
    python exporter_acte.py --input <acte.md> --output <acte.docx>
    python exporter_acte.py --input <acte.md> --docx <acte.docx> --pdf <acte.pdf>

Le format de sortie est déterminé automatiquement par l'extension.
Pour avoir les deux formats, utilisez --docx et --pdf ensemble.
"""

import argparse
import sys
from pathlib import Path

# Importer les modules locaux
sys.path.insert(0, str(Path(__file__).parent))
from exporter_docx import exporter_docx
from docx_to_pdf import convert_docx_to_pdf


def exporter_acte(chemin_entree: Path, chemin_docx: Path = None, chemin_pdf: Path = None) -> dict:
    """
    Exporte un acte depuis Markdown/HTML vers DOCX et/ou PDF.

    Args:
        chemin_entree: Fichier source (Markdown/HTML)
        chemin_docx: Fichier DOCX de sortie (optionnel)
        chemin_pdf: Fichier PDF de sortie (optionnel)

    Returns:
        dict avec 'docx' et 'pdf' indiquant les chemins générés ou None
    """
    result = {'docx': None, 'pdf': None}

    if not chemin_entree.exists():
        print(f"[ERREUR] Fichier non trouvé: {chemin_entree}")
        return result

    # Si seulement PDF demandé, créer un DOCX temporaire
    temp_docx = None
    if chemin_pdf and not chemin_docx:
        temp_docx = chemin_pdf.with_suffix('.docx')
        chemin_docx = temp_docx

    # Étape 1: Générer le DOCX
    if chemin_docx:
        print(f"[INFO] Génération du DOCX...")
        try:
            if exporter_docx(chemin_entree, chemin_docx):
                taille = chemin_docx.stat().st_size / 1024
                print(f"[OK] DOCX généré: {chemin_docx} ({taille:.1f} Ko)")
                result['docx'] = chemin_docx
            else:
                print(f"[ERREUR] Échec de la génération DOCX")
                return result
        except Exception as e:
            print(f"[ERREUR] {e}")
            import traceback
            traceback.print_exc()
            return result

    # Étape 2: Convertir en PDF si demandé
    if chemin_pdf and result['docx']:
        print(f"[INFO] Conversion en PDF via Microsoft Word...")
        try:
            if convert_docx_to_pdf(chemin_docx, chemin_pdf):
                taille = chemin_pdf.stat().st_size / 1024
                print(f"[OK] PDF généré: {chemin_pdf} ({taille:.1f} Ko)")
                result['pdf'] = chemin_pdf
            else:
                print(f"[ERREUR] Échec de la conversion PDF")
        except Exception as e:
            print(f"[ERREUR] Conversion PDF: {e}")
            import traceback
            traceback.print_exc()

    # Supprimer le DOCX temporaire si seulement PDF demandé
    if temp_docx and temp_docx.exists() and result['pdf']:
        # Garder le DOCX temporaire pour debug, ou décommenter pour supprimer:
        # temp_docx.unlink()
        pass

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Exporter un acte notarial vers DOCX et/ou PDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
    python exporter_acte.py -i acte.md -o acte.pdf    # Génère PDF
    python exporter_acte.py -i acte.md -o acte.docx   # Génère DOCX
    python exporter_acte.py -i acte.md --docx acte.docx --pdf acte.pdf  # Les deux
        """
    )
    parser.add_argument('--input', '-i', type=Path, required=True,
                        help='Fichier source (Markdown/HTML)')
    parser.add_argument('--output', '-o', type=Path, default=None,
                        help='Fichier de sortie (.docx ou .pdf, déterminé par extension)')
    parser.add_argument('--docx', type=Path, default=None,
                        help='Fichier DOCX de sortie')
    parser.add_argument('--pdf', type=Path, default=None,
                        help='Fichier PDF de sortie')

    args = parser.parse_args()

    # Déterminer les sorties
    chemin_docx = args.docx
    chemin_pdf = args.pdf

    if args.output:
        ext = args.output.suffix.lower()
        if ext == '.docx':
            chemin_docx = args.output
        elif ext == '.pdf':
            chemin_pdf = args.output
        else:
            print(f"[ERREUR] Extension non supportée: {ext}. Utilisez .docx ou .pdf")
            return 1

    if not chemin_docx and not chemin_pdf:
        print("[ERREUR] Spécifiez au moins une sortie avec --output, --docx ou --pdf")
        return 1

    # Exporter
    result = exporter_acte(args.input, chemin_docx, chemin_pdf)

    if result['pdf'] or result['docx']:
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
