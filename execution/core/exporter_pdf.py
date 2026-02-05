#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
exporter_pdf.py
===============

Script d'export d'actes notariaux Markdown vers PDF.

Fonctionnalités:
- Conversion Markdown → PDF
- Mise en page notariale (marges, numérotation)
- En-têtes et pieds de page personnalisés
- Gestion des tableaux et annexes

Usage:
    python exporter_pdf.py --input <acte.md> --output <acte.pdf> [--options]

Exemple:
    python exporter_pdf.py --input ../.tmp/actes_generes/acte_001/acte.md \\
                           --output ../.tmp/actes_generes/acte_001/acte.pdf

Dépendances:
    - markdown: pip install markdown
    - weasyprint: pip install weasyprint (nécessite GTK sur Windows)
    ou
    - pdfkit: pip install pdfkit (nécessite wkhtmltopdf)
"""

import argparse
import os
from pathlib import Path
from typing import Optional
import markdown
from datetime import datetime

from execution.security.secure_delete import secure_delete_file


# CSS pour la mise en page notariale - Basé sur audit_pdf_complet.py
# Original: Times New Roman 11pt, interligne 12.6pt, espacement para 12pt
CSS_NOTARIAL = """
/* ============================================
   PAGE SETUP - Format A4 standard notarial
   ============================================ */
@page {
    size: A4;
}

/* ============================================
   CORPS DU DOCUMENT
   Police: Times New Roman 11pt (rendu ~10.9pt avec wkhtmltopdf)
   Interligne: 1.25 (12.6pt/11pt dans l'original)
   ============================================ */
body {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;  /* Compensé pour wkhtmltopdf */
    line-height: 1.25;
    text-align: justify;
    color: #000;
    orphans: 3;
    widows: 3;
    margin: 0;
    padding: 0;
}

/* ============================================
   HEADER - Références en haut à gauche
   ============================================ */
.header-ref {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    line-height: 1.25;
    text-align: left;
    margin-bottom: 12pt;
}

/* ============================================
   HEADER - Bloc titre avec indentation
   ============================================ */
.header-titre {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    line-height: 1.25;
    text-align: left;
    margin-left: 12mm;
    margin-bottom: 12pt;
}

/* ============================================
   HEADER - Bloc notaire avec indentation
   ============================================ */
.header-notaire {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    line-height: 1.25;
    text-align: justify;
    margin-left: 12mm;
    margin-bottom: 6pt;
}

/* ============================================
   PERSONNE - Bloc description d'une personne
   Espacement réduit entre lignes, espace après le bloc
   ============================================ */
.personne {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    line-height: 1.25;
    text-align: justify;
    margin-bottom: 18pt;
}

/* ============================================
   BALISES DIV - pour contrôle précis
   ============================================ */
div {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    line-height: 1.25;
}

/* ============================================
   PARAGRAPHES - Espacement calibré pour 386 mots/page
   ============================================ */
p {
    margin: 0;
    padding: 0;
    text-indent: 0;
    line-height: 1.25;
    margin-bottom: 35pt;  /* Ajusté pour ~42 pages */
}

/* Réduire l'espacement dans les blocs personne */
.personne p, div.personne p {
    margin-bottom: 6pt;
}

/* ============================================
   TITRES - Base commune
   Empêcher les titres orphelins en fin de page
   ============================================ */
h1, h2, h3, h4, h5, h6 {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    page-break-after: avoid !important;
    page-break-inside: avoid !important;
    break-after: avoid !important;
    line-height: 1.25;
}

/* ============================================
   TITRES H2 - Sections principales (PARTIE NORMALISEE, etc.)
   ============================================ */
h2 {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    text-decoration: underline;
    margin-top: 24pt;
    margin-bottom: 12pt;
    line-height: 1.25;
    page-break-after: avoid !important;
}

/* ============================================
   TITRES H3 - Sous-sections (IDENTIFICATION DES PARTIES, etc.)
   Centré, souligné
   ============================================ */
h3 {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    text-decoration: underline;
    margin-top: 18pt;
    margin-bottom: 12pt;
    line-height: 1.25;
    page-break-after: avoid !important;
}

/* ============================================
   TITRES H4 - Rubriques (VENDEUR, ACQUEREUR, etc.)
   Centré, gras
   ============================================ */
h4 {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    margin-top: 12pt;
    margin-bottom: 12pt;
    line-height: 1.25;
    page-break-after: avoid !important;
}

/* ============================================
   SAUTS DE LIGNE (balise br)
   ============================================ */
br {
    line-height: 1.25;
}

/* Les titres h1-h4 sont déjà définis plus haut */

/* ============================================
   LISTES A PUCES
   Indentation standard, puces rondes
   ============================================ */
ul {
    margin: 6pt 0;
    padding-left: 2em;
    list-style-type: disc;
    list-style-position: outside;
}

ol {
    margin: 6pt 0;
    padding-left: 2em;
    list-style-type: decimal;
    list-style-position: outside;
}

li {
    margin: 3pt 0;
    padding: 0;
    text-align: justify;
    line-height: 1.25;
}

li p {
    margin: 0;
    padding: 0;
    display: inline;
}

/* ============================================
   TABLEAUX
   Bordures fines, alignement gauche
   ============================================ */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 6pt 0;
    font-size: 19pt;
    line-height: 1.25;
}

th, td {
    border: 1px solid #000;
    padding: 3pt 6pt;
    text-align: left;
    vertical-align: top;
    line-height: 1.25;
}

th {
    font-weight: bold;
    background-color: transparent;
}

/* ============================================
   MISE EN FORME DU TEXTE
   IMPORTANT: Les éléments strong/b doivent rester inline
   pour éviter les retours à la ligne (ACQUEREURS, BIENS, etc.)
   ============================================ */
strong, b {
    font-weight: bold;
    display: inline;
    /* white-space: nowrap supprimé car cause des coupures de texte */
}

u {
    text-decoration: underline;
}

em, i {
    font-style: italic;
}

a {
    color: #000;
    text-decoration: none;
}

/* ============================================
   ELEMENTS SPECIAUX
   ============================================ */
hr {
    border: none;
    border-top: 1px solid #000;
    margin: 12pt 0;
}

blockquote {
    margin: 6pt 2em;
    font-style: italic;
}

/* Code/Pre - ne pas afficher différemment */
pre, code {
    font-family: "Times New Roman", Times, serif;
    font-size: 19pt;
    white-space: pre-wrap;
    background: none;
    border: none;
    margin: 0;
    padding: 0;
}

/* ============================================
   WATERMARK BROUILLON
   ============================================ */
.brouillon::before {
    content: "PROJET - NE VAUT PAS MINUTE";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
    font-size: 48pt;
    color: rgba(180, 180, 180, 0.15);
    z-index: -1;
    white-space: nowrap;
    font-family: "Times New Roman", Times, serif;
    font-weight: normal;
}

/* ============================================
   CLASSES UTILITAIRES
   ============================================ */
.text-center {
    text-align: center;
}

.text-left {
    text-align: left;
}

.text-right {
    text-align: right;
}

.no-break {
    page-break-inside: avoid;
}

.page-break {
    page-break-before: always;
}

/* ============================================
   SEPARATEURS - lignes d'astérisques
   ============================================ */
.separateur {
    text-align: center;
    margin: 12pt 0;
}
"""


def convertir_markdown_html(contenu_md: str) -> str:
    """
    Convertit le contenu Markdown en HTML.

    Args:
        contenu_md: Contenu Markdown

    Returns:
        Contenu HTML
    """
    # Extensions Markdown
    extensions = [
        'tables',
        'fenced_code',
        'footnotes',
        'attr_list',
        'def_list',
        'abbr',
        'md_in_html',
        'toc'
    ]

    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(contenu_md)

    return html_content


def generer_html_complet(contenu_html: str, titre: str = "Acte Notarié",
                         brouillon: bool = False) -> str:
    """
    Génère le document HTML complet avec le CSS.

    Args:
        contenu_html: Contenu HTML de l'acte
        titre: Titre du document
        brouillon: Ajouter watermark brouillon

    Returns:
        Document HTML complet
    """
    classe_body = 'brouillon' if brouillon else ''

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titre}</title>
    <style>
{CSS_NOTARIAL}
    </style>
</head>
<body class="{classe_body}">
{contenu_html}
</body>
</html>
"""
    return html


def exporter_avec_weasyprint(html: str, chemin_sortie: Path) -> bool:
    """
    Exporte le HTML en PDF avec WeasyPrint.

    Args:
        html: Contenu HTML
        chemin_sortie: Chemin du fichier PDF de sortie

    Returns:
        True si succès
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        font_config = FontConfiguration()
        html_doc = HTML(string=html)
        html_doc.write_pdf(
            str(chemin_sortie),
            font_config=font_config
        )
        return True
    except ImportError:
        print("[AVERTISSEMENT] WeasyPrint non disponible")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur WeasyPrint: {e}")
        return False


def creer_header_html(chemin_temp: Path) -> Path:
    """
    Crée un fichier HTML de header avec pagination conditionnelle.
    Le header n'affiche rien sur la page 1, et affiche "page / total" ensuite.

    Args:
        chemin_temp: Dossier temporaire pour le fichier

    Returns:
        Chemin du fichier header HTML
    """
    header_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: "Times New Roman", Times, serif;
            font-size: 9pt;
            margin: 0;
            padding: 0;
            height: 10mm;
        }
        .pagination {
            text-align: right;
            padding-right: 0;
            margin-top: 2mm;
        }
    </style>
    <script>
        function subst() {
            var vars = {};
            var query_strings_from_url = document.location.search.substring(1).split('&');
            for (var query_string in query_strings_from_url) {
                if (query_strings_from_url.hasOwnProperty(query_string)) {
                    var temp_var = query_strings_from_url[query_string].split('=', 2);
                    vars[temp_var[0]] = decodeURI(temp_var[1]);
                }
            }
            var page = vars['page'];
            var topage = vars['topage'];
            var elem = document.getElementById('pagination');
            if (page == 1) {
                elem.innerHTML = '';
            } else {
                elem.innerHTML = page + ' / ' + topage;
            }
        }
    </script>
</head>
<body onload="subst()">
    <div class="pagination" id="pagination"></div>
</body>
</html>
"""
    chemin_header = chemin_temp / "header.html"
    chemin_temp.mkdir(parents=True, exist_ok=True)
    with open(chemin_header, 'w', encoding='utf-8') as f:
        f.write(header_html)
    return chemin_header


def exporter_avec_pdfkit(html: str, chemin_sortie: Path) -> bool:
    """
    Exporte le HTML en PDF avec pdfkit (wkhtmltopdf).

    Args:
        html: Contenu HTML
        chemin_sortie: Chemin du fichier PDF de sortie

    Returns:
        True si succès
    """
    try:
        import pdfkit

        # Chemins possibles pour wkhtmltopdf sur Windows
        wkhtmltopdf_paths = [
            r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
            r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
        ]

        config = None
        for path in wkhtmltopdf_paths:
            if os.path.exists(path):
                config = pdfkit.configuration(wkhtmltopdf=path)
                break

        # Créer le header HTML pour pagination conditionnelle
        chemin_temp = chemin_sortie.parent / ".tmp_pdf"
        chemin_header = creer_header_html(chemin_temp)

        # Marges style "Minute" notarial - basées sur audit_pdf_complet.py
        # Marges basées sur analyse RTF original:
        # Intérieur (reliure): 60mm, Extérieur: 15mm, Haut: 25mm, Bas: 25mm
        # Note: wkhtmltopdf ne supporte pas marges miroir, marge droite augmentée
        options = {
            'page-size': 'A4',
            'margin-top': '25mm',       # 25mm comme original RTF
            'margin-right': '22mm',     # Augmenté de 15mm original pour compenser rendu
            'margin-bottom': '25mm',    # 25mm comme original RTF
            'margin-left': '60mm',      # Style Minute (reliure)
            'encoding': 'UTF-8',
            'header-html': str(chemin_header),
            'header-spacing': '0',      # Pagination dans la marge
            'enable-local-file-access': None
        }

        if config:
            pdfkit.from_string(html, str(chemin_sortie), options=options, configuration=config)
        else:
            pdfkit.from_string(html, str(chemin_sortie), options=options)

        # Nettoyer le fichier header temporaire (ecrasement securise)
        secure_delete_file(chemin_header)
        try:
            chemin_temp.rmdir()
        except OSError:
            pass

        return True
    except ImportError:
        print("[AVERTISSEMENT] pdfkit non disponible")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur pdfkit: {e}")
        return False


def exporter_html_simple(html: str, chemin_sortie: Path) -> bool:
    """
    Exporte en HTML (fallback si aucun convertisseur PDF disponible).

    Args:
        html: Contenu HTML
        chemin_sortie: Chemin du fichier de sortie (sera .html)

    Returns:
        True si succès
    """
    chemin_html = chemin_sortie.with_suffix('.html')
    try:
        with open(chemin_html, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[AVERTISSEMENT] Fichier HTML genere (PDF non disponible): {chemin_html}")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur ecriture HTML: {e}")
        return False


def exporter_pdf(chemin_entree: Path, chemin_sortie: Path,
                 brouillon: bool = False, titre: Optional[str] = None) -> bool:
    """
    Exporte un acte Markdown en PDF.

    Args:
        chemin_entree: Chemin du fichier Markdown
        chemin_sortie: Chemin du fichier PDF de sortie
        brouillon: Ajouter watermark brouillon
        titre: Titre personnalisé

    Returns:
        True si succès
    """
    # Lire le fichier Markdown
    with open(chemin_entree, 'r', encoding='utf-8') as f:
        contenu_md = f.read()

    # Convertir en HTML
    contenu_html = convertir_markdown_html(contenu_md)

    # Générer le HTML complet
    titre = titre or "Acte Notarié"
    html_complet = generer_html_complet(contenu_html, titre, brouillon)

    # Créer le dossier de sortie si nécessaire
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    # Essayer les différentes méthodes d'export
    if exporter_avec_weasyprint(html_complet, chemin_sortie):
        return True

    if exporter_avec_pdfkit(html_complet, chemin_sortie):
        return True

    # Fallback: export HTML
    return exporter_html_simple(html_complet, chemin_sortie)


def main():
    parser = argparse.ArgumentParser(
        description="Exporte un acte notarial Markdown en PDF"
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        required=True,
        help="Chemin du fichier Markdown d'entrée"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help="Chemin du fichier PDF de sortie (défaut: même nom que l'entrée)"
    )
    parser.add_argument(
        '--titre', '-t',
        type=str,
        help="Titre du document"
    )
    parser.add_argument(
        '--brouillon',
        action='store_true',
        help="Ajouter un watermark 'PROJET'"
    )
    parser.add_argument(
        '--html-only',
        action='store_true',
        help="Générer uniquement le fichier HTML (pas de PDF)"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"[ERREUR] Fichier non trouve: {args.input}")
        return 1

    # Déterminer le chemin de sortie
    chemin_sortie = args.output or args.input.with_suffix('.pdf')

    if args.html_only:
        # Mode HTML uniquement
        with open(args.input, 'r', encoding='utf-8') as f:
            contenu_md = f.read()

        contenu_html = convertir_markdown_html(contenu_md)
        titre = args.titre or "Acte Notarié"
        html_complet = generer_html_complet(contenu_html, titre, args.brouillon)

        chemin_html = chemin_sortie.with_suffix('.html')
        with open(chemin_html, 'w', encoding='utf-8') as f:
            f.write(html_complet)

        print(f"[OK] Fichier HTML genere: {chemin_html}")
        return 0

    # Export PDF
    succes = exporter_pdf(args.input, chemin_sortie, args.brouillon, args.titre)

    if succes:
        if chemin_sortie.exists():
            taille = chemin_sortie.stat().st_size / 1024
            print(f"[OK] PDF genere: {chemin_sortie} ({taille:.1f} Ko)")
        else:
            # Fallback HTML
            chemin_html = chemin_sortie.with_suffix('.html')
            if chemin_html.exists():
                print(f"[INFO] PDF non disponible, HTML genere: {chemin_html}")
                print("   Pour generer le PDF, installez weasyprint ou pdfkit+wkhtmltopdf")
        return 0
    else:
        print(f"[ERREUR] Echec de l'export")
        return 1


if __name__ == '__main__':
    exit(main())
