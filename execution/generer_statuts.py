#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_statuts.py
==================

Génère les statuts constitutifs en DOCX avec formatage exact (boîtes bleues).
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import comtypes.client
import pythoncom


def set_cell_border(cell, **kwargs):
    """Définit les bordures d'une cellule de tableau."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = OxmlElement(tag)
            for key, val in edge_data.items():
                element.set(qn('w:{}'.format(key)), str(val))
            tcPr.append(element)


def set_cell_background(cell, color):
    """Définit la couleur de fond d'une cellule."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # Supprimer ancien shd si existe
    for shd in tcPr.findall(qn('w:shd')):
        tcPr.remove(shd)

    # Créer nouveau shd
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


def creer_boite_bleue(doc, texte):
    """Crée une boîte bleue avec texte blanc (comme page 1 et 2)."""
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    table.allow_autofit = False

    cell = table.cell(0, 0)
    cell.width = Mm(160)

    # Fond bleu
    set_cell_background(cell, '001f5f')

    # Texte blanc en gras
    p = cell.paragraphs[0]
    p.text = texte
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)

    run = p.runs[0]
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)  # Blanc

    # Bordures (optionnel, peut être sans bordures)
    set_cell_border(
        cell,
        top={"val": "none"},
        bottom={"val": "none"},
        left={"val": "none"},
        right={"val": "none"}
    )

    return table


def generer_statuts_docx(output_docx):
    """Génère le document DOCX des statuts."""

    doc = Document()

    # Configuration page
    section = doc.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    section.left_margin = Mm(25.4)
    section.right_margin = Mm(25.4)
    section.top_margin = Mm(25.4)
    section.bottom_margin = Mm(25.4)

    # Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    style_normal.paragraph_format.space_after = Pt(0)
    style_normal.paragraph_format.line_spacing = 1.0

    # ============================================================================
    # PAGE 1
    # ============================================================================

    # Header page 1 (aligné à droite)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.space_after = Pt(0)
    run = para.add_run('NOM_SOCIETE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.space_after = Pt(0)
    run = para.add_run('Société civile au capital de 1 000 euros')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.space_after = Pt(0)
    run = para.add_run('Siège social : 00 rue Exemple - 00000 VILLE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    para.paragraph_format.space_after = Pt(12)
    run = para.add_run('En cours d\'immatriculation au RCS de METROPOLE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    # Espacement
    for _ in range(10):
        doc.add_paragraph()

    # Boîte bleue "STATUTS"
    creer_boite_bleue(doc, 'STATUTS')

    # Saut de page
    doc.add_page_break()

    # ============================================================================
    # PAGE 2
    # ============================================================================

    # Boîte bleue "LES SOUSSIGNÉS :"
    creer_boite_bleue(doc, 'LES SOUSSIGNÉS :')

    doc.add_paragraph()

    # Personne 1
    para = doc.add_paragraph()
    run = para.add_run('1. Monsieur Prénom1, Prénom3 NOM_FAMILLE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Né le JJ mois AAAA à METROPOLE (00),')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('De nationalité française,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Demeurant 00 rue Exemple - 00000 VILLE,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Marié à Madame Prénom2, Prénom6, Prénom7 NOM_NAISSANCE sous le régime de la participation aux acquêts, suivant contrat de mariage reçu par Maître Prénom_Ancien NOM_ANCIEN_NOTAIRE, Notaire à Charolles (71), le JJ mois AAAA, préalablement à leur union célébrée à la mairie de VILLE_MARIAGE (00), le JJ mois AAAA,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Déclarant que ledit régime n\'a pas été modifié depuis.')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(12)

    # Personne 2
    para = doc.add_paragraph()
    run = para.add_run('2. Madame Prénom2, Prénom6, Prénom7 NOM_NAISSANCE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Née le JJ mois AAAA à VILLE_NAISSANCE (00),')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('De nationalité française,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Demeurant 00 rue Exemple - 00000 VILLE,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Mariée à Monsieur Prénom1, Prénom3 NOM_FAMILLE sous le régime de la participation aux acquêts, suivant contrat de mariage reçu par Maître Prénom_Ancien NOM_ANCIEN_NOTAIRE, Notaire à Charolles (71), le JJ mois AAAA, préalablement à leur union célébrée à la mairie de VILLE_MARIAGE (00), le JJ mois AAAA,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('Déclarant que ledit régime n\'a pas été modifié depuis.')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(12)

    # Texte suite
    para = doc.add_paragraph('Associés fondateurs,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(12)

    para = doc.add_paragraph('Ont établi ainsi qu\'il suit les statuts d\'une société civile qu\'ils sont convenus de constituer entre eux et avec toute autre personne qui viendrait ultérieurement à acquérir la qualité d\'associé.')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(12)

    # Footer page 2
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()

    table_footer = doc.add_table(rows=1, cols=2)
    table_footer.autofit = False
    table_footer.allow_autofit = False

    # Ligne de séparation
    cell_left = table_footer.cell(0, 0)
    p = cell_left.paragraphs[0]
    run = p.add_run('_' * 80)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)

    # Numéro de page avec fond bleu
    cell_right = table_footer.cell(0, 1)
    cell_right.width = Mm(20)
    set_cell_background(cell_right, '001f5f')
    p = cell_right.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('2')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)

    # Pages suivantes (squelette)
    doc.add_page_break()

    # PAGE 3 - Exemple de contenu
    para = doc.add_paragraph()
    run = para.add_run('FORME - OBJET - DENOMINATION - SIEGE - DUREE')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    run.underline = True
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = Pt(12)

    para = doc.add_paragraph()
    run = para.add_run('ARTICLE 1 - FORME')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    para.paragraph_format.space_after = Pt(6)

    para = doc.add_paragraph('La Société est une société civile régie par les dispositions du Code civil et notamment par les articles 1832 et suivants ainsi que par les présents statuts.')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(12)

    para = doc.add_paragraph()
    run = para.add_run('ARTICLE 2 - OBJET')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.bold = True
    para.paragraph_format.space_after = Pt(6)

    para = doc.add_paragraph('La Société a pour objet :')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(6)

    para = doc.add_paragraph('- L\'acquisition, la gestion, l\'administration et l\'exploitation par bail ou autrement de tous immeubles bâtis ou non bâtis,')
    para.style = style_normal
    para.paragraph_format.space_after = Pt(0)

    para = doc.add_paragraph('- Et généralement, toutes opérations quelconques pouvant se rattacher directement ou indirectement à l\'objet social ci-dessus et ne portant pas atteinte au caractère civil de la Société.')
    para.style = style_normal

    # Sauvegarder
    doc.save(output_docx)
    print(f'✅ DOCX créé: {output_docx}')
    return output_docx


def convertir_docx_vers_pdf(docx_path, pdf_path):
    """Convertit DOCX vers PDF via Microsoft Word COM."""
    try:
        pythoncom.CoInitialize()

        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False

        docx_abs = str(Path(docx_path).resolve())
        pdf_abs = str(Path(pdf_path).resolve())

        doc = word.Documents.Open(docx_abs)
        doc.SaveAs(pdf_abs, FileFormat=17)
        doc.Close()
        word.Quit()

        print(f'✅ PDF créé: {pdf_path}')

    except Exception as e:
        print(f'❌ Erreur conversion PDF: {e}')
        raise
    finally:
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    # Générer DOCX
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)

    docx_path = output_dir / 'test statuts.docx'
    pdf_path = output_dir / 'test statuts.pdf'

    generer_statuts_docx(str(docx_path))
    convertir_docx_vers_pdf(str(docx_path), str(pdf_path))

    print('✅ Génération terminée!')
