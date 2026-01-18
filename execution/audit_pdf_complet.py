#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_pdf_complet.py
====================

Outil d'audit complet pour analyser un PDF et extraire toutes les métriques
de formatage nécessaires pour reproduire exactement le style.

Usage:
    python audit_pdf_complet.py --input <fichier.pdf> [--output <rapport.json>]

Métriques analysées:
- Polices: types, tailles, variations (gras, italique)
- Espacements: interligne, espacement paragraphes, marges
- Structure: position des éléments, alignement
- Densité: mots/page, caractères/ligne
"""

import argparse
import json
import statistics
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import fitz  # PyMuPDF


def analyser_polices(doc: fitz.Document) -> Dict[str, Any]:
    """Analyse les polices utilisées dans tout le document."""
    polices = Counter()
    tailles = []
    tailles_par_page = []
    styles = Counter()  # bold, italic, etc.

    for page_num, page in enumerate(doc):
        page_tailles = []
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    font = span.get("font", "Unknown")
                    size = span.get("size", 0)
                    flags = span.get("flags", 0)

                    polices[font] += 1
                    tailles.append(size)
                    page_tailles.append(size)

                    # Analyser les flags (bit 0=superscript, 1=italic, 2=serifed, 4=bold)
                    if flags & 4:
                        styles["bold"] += 1
                    if flags & 2:
                        styles["italic"] += 1
                    if flags & 1:
                        styles["superscript"] += 1

        if page_tailles:
            tailles_par_page.append({
                "page": page_num + 1,
                "moyenne": statistics.mean(page_tailles),
                "min": min(page_tailles),
                "max": max(page_tailles)
            })

    # Calculer la taille dominante (mode)
    tailles_arrondies = [round(t, 1) for t in tailles]
    taille_dominante = Counter(tailles_arrondies).most_common(1)[0] if tailles_arrondies else (0, 0)

    return {
        "polices_utilisees": dict(polices.most_common(10)),
        "taille_dominante_pt": taille_dominante[0],
        "taille_dominante_occurrences": taille_dominante[1],
        "taille_moyenne_pt": round(statistics.mean(tailles), 2) if tailles else 0,
        "taille_min_pt": round(min(tailles), 2) if tailles else 0,
        "taille_max_pt": round(max(tailles), 2) if tailles else 0,
        "styles": dict(styles),
        "distribution_tailles": dict(Counter(tailles_arrondies).most_common(10)),
        "tailles_par_page": tailles_par_page[:5]  # Échantillon
    }


def analyser_espacements(doc: fitz.Document) -> Dict[str, Any]:
    """Analyse les espacements entre lignes et paragraphes."""
    interlignes = []
    espacements_paragraphes = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]

        positions_y = []

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                y = line["bbox"][1]  # Position Y du haut de la ligne
                positions_y.append(y)

        # Trier par position Y
        positions_y.sort()

        # Calculer les espacements entre lignes consécutives
        for i in range(len(positions_y) - 1):
            espacement = positions_y[i + 1] - positions_y[i]
            if 5 < espacement < 50:  # Filtrer les valeurs aberrantes
                if espacement < 25:  # Interligne normal
                    interlignes.append(espacement)
                else:  # Espacement paragraphe
                    espacements_paragraphes.append(espacement)

    return {
        "interligne_moyen_pt": round(statistics.mean(interlignes), 2) if interlignes else 0,
        "interligne_median_pt": round(statistics.median(interlignes), 2) if interlignes else 0,
        "interligne_min_pt": round(min(interlignes), 2) if interlignes else 0,
        "interligne_max_pt": round(max(interlignes), 2) if interlignes else 0,
        "interligne_ecart_type": round(statistics.stdev(interlignes), 2) if len(interlignes) > 1 else 0,
        "espacement_paragraphe_moyen_pt": round(statistics.mean(espacements_paragraphes), 2) if espacements_paragraphes else 0,
        "espacement_paragraphe_median_pt": round(statistics.median(espacements_paragraphes), 2) if espacements_paragraphes else 0,
        "nb_interlignes_analyses": len(interlignes),
        "nb_espacements_paragraphes": len(espacements_paragraphes)
    }


def analyser_marges(doc: fitz.Document) -> Dict[str, Any]:
    """Analyse les marges de chaque page."""
    marges_gauche = []
    marges_droite = []
    marges_haut = []
    marges_bas = []

    page_width = 595.3  # A4 en points
    page_height = 841.9

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]

        x_min = page_width
        x_max = 0
        y_min = page_height
        y_max = 0

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                bbox = line["bbox"]
                x_min = min(x_min, bbox[0])
                x_max = max(x_max, bbox[2])
                y_min = min(y_min, bbox[1])
                y_max = max(y_max, bbox[3])

        if x_min < page_width:  # Page avec contenu
            marges_gauche.append(x_min)
            marges_droite.append(page_width - x_max)
            marges_haut.append(y_min)
            marges_bas.append(page_height - y_max)

    def stats_marge(valeurs):
        if not valeurs:
            return {"pt": 0, "mm": 0}
        moy = statistics.mean(valeurs)
        return {
            "pt": round(moy, 1),
            "mm": round(moy / 2.83, 1)
        }

    return {
        "marge_gauche": stats_marge(marges_gauche),
        "marge_droite": stats_marge(marges_droite),
        "marge_haut": stats_marge(marges_haut),
        "marge_bas": stats_marge(marges_bas),
        "largeur_contenu_pt": round(page_width - statistics.mean(marges_gauche) - statistics.mean(marges_droite), 1) if marges_gauche else 0,
        "hauteur_contenu_pt": round(page_height - statistics.mean(marges_haut) - statistics.mean(marges_bas), 1) if marges_haut else 0
    }


def analyser_densite(doc: fitz.Document) -> Dict[str, Any]:
    """Analyse la densité de texte (mots/page, caractères/ligne)."""
    mots_par_page = []
    chars_par_ligne = []
    lignes_par_page = []

    for page_num, page in enumerate(doc):
        texte = page.get_text()
        mots = len(texte.split())
        mots_par_page.append(mots)

        blocks = page.get_text("dict")["blocks"]
        nb_lignes = 0

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                nb_lignes += 1
                # Compter les caractères dans cette ligne
                ligne_texte = ""
                for span in line["spans"]:
                    ligne_texte += span.get("text", "")
                if len(ligne_texte) > 10:  # Ignorer lignes très courtes
                    chars_par_ligne.append(len(ligne_texte))

        lignes_par_page.append(nb_lignes)

    return {
        "total_pages": len(doc),
        "total_mots": sum(mots_par_page),
        "mots_par_page_moyen": round(statistics.mean(mots_par_page), 0) if mots_par_page else 0,
        "mots_par_page_min": min(mots_par_page) if mots_par_page else 0,
        "mots_par_page_max": max(mots_par_page) if mots_par_page else 0,
        "chars_par_ligne_moyen": round(statistics.mean(chars_par_ligne), 0) if chars_par_ligne else 0,
        "chars_par_ligne_median": round(statistics.median(chars_par_ligne), 0) if chars_par_ligne else 0,
        "lignes_par_page_moyen": round(statistics.mean(lignes_par_page), 0) if lignes_par_page else 0,
        "mots_par_page_distribution": mots_par_page
    }


def analyser_structure(doc: fitz.Document) -> Dict[str, Any]:
    """Analyse la structure du document (titres, sections, mise en forme)."""
    elements_gras = []
    elements_centres = []
    positions_x_uniques = set()

    page_width = 595.3

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                x_start = line["bbox"][0]
                x_end = line["bbox"][2]
                largeur = x_end - x_start

                # Détecter centrage (tolérance de 20pt)
                centre_ligne = (x_start + x_end) / 2
                centre_page = page_width / 2
                if abs(centre_ligne - centre_page) < 20 and largeur < 400:
                    texte = "".join(span.get("text", "") for span in line["spans"])
                    if len(texte.strip()) > 0:
                        elements_centres.append({
                            "page": page_num + 1,
                            "texte": texte[:50],
                            "x": round(x_start, 1)
                        })

                positions_x_uniques.add(round(x_start, 0))

                for span in line["spans"]:
                    flags = span.get("flags", 0)
                    if flags & 4:  # Bold
                        texte = span.get("text", "").strip()
                        if len(texte) > 2:
                            elements_gras.append({
                                "page": page_num + 1,
                                "texte": texte[:50],
                                "taille": round(span.get("size", 0), 1)
                            })

    return {
        "nb_elements_gras": len(elements_gras),
        "nb_elements_centres": len(elements_centres),
        "positions_x_distinctes": sorted(list(positions_x_uniques))[:10],
        "echantillon_elements_gras": elements_gras[:10],
        "echantillon_elements_centres": elements_centres[:10]
    }


def analyser_page_specifique(doc: fitz.Document, page_num: int) -> Dict[str, Any]:
    """Analyse détaillée d'une page spécifique."""
    if page_num < 0 or page_num >= len(doc):
        return {"erreur": f"Page {page_num + 1} inexistante"}

    page = doc[page_num]
    blocks = page.get_text("dict")["blocks"]

    lignes_details = []
    positions_y = []

    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            y = line["bbox"][1]
            positions_y.append(y)

            texte = "".join(span.get("text", "") for span in line["spans"])
            taille = line["spans"][0].get("size", 0) if line["spans"] else 0
            flags = line["spans"][0].get("flags", 0) if line["spans"] else 0

            lignes_details.append({
                "y_pt": round(y, 1),
                "x_pt": round(line["bbox"][0], 1),
                "taille_pt": round(taille, 1),
                "gras": bool(flags & 4),
                "texte": texte[:60]
            })

    # Calculer espacements
    positions_y.sort()
    espacements = []
    for i in range(len(positions_y) - 1):
        esp = positions_y[i + 1] - positions_y[i]
        if esp > 0:
            espacements.append(round(esp, 1))

    return {
        "page": page_num + 1,
        "nb_lignes": len(lignes_details),
        "lignes": lignes_details[:20],  # Premières 20 lignes
        "espacements_consecutifs": espacements[:20],
        "y_premiere_ligne": round(min(positions_y), 1) if positions_y else 0,
        "y_derniere_ligne": round(max(positions_y), 1) if positions_y else 0
    }


def generer_rapport_complet(chemin_pdf: Path) -> Dict[str, Any]:
    """Génère un rapport d'audit complet du PDF."""
    doc = fitz.open(str(chemin_pdf))

    rapport = {
        "fichier": str(chemin_pdf.name),
        "nb_pages": len(doc),
        "polices": analyser_polices(doc),
        "espacements": analyser_espacements(doc),
        "marges": analyser_marges(doc),
        "densite": analyser_densite(doc),
        "structure": analyser_structure(doc),
        "pages_echantillon": {
            "page_1": analyser_page_specifique(doc, 0),
            "page_10": analyser_page_specifique(doc, 9),
            "page_20": analyser_page_specifique(doc, 19),
            "page_derniere": analyser_page_specifique(doc, len(doc) - 1)
        }
    }

    doc.close()
    return rapport


def afficher_rapport_console(rapport: Dict[str, Any]):
    """Affiche un résumé du rapport en console."""
    print("=" * 70)
    print(f"AUDIT PDF COMPLET: {rapport['fichier']}")
    print("=" * 70)

    print(f"\n{'='*30} RESUME {'='*30}")
    print(f"Pages: {rapport['nb_pages']}")
    print(f"Mots total: {rapport['densite']['total_mots']}")
    print(f"Mots/page: {rapport['densite']['mots_par_page_moyen']}")

    print(f"\n{'='*30} POLICES {'='*30}")
    p = rapport['polices']
    print(f"Taille dominante: {p['taille_dominante_pt']}pt ({p['taille_dominante_occurrences']} occurrences)")
    print(f"Taille moyenne: {p['taille_moyenne_pt']}pt")
    print(f"Plage: {p['taille_min_pt']}pt - {p['taille_max_pt']}pt")
    print(f"Polices utilisées: {list(p['polices_utilisees'].keys())[:3]}")

    print(f"\n{'='*30} ESPACEMENTS {'='*30}")
    e = rapport['espacements']
    print(f"Interligne moyen: {e['interligne_moyen_pt']}pt (médian: {e['interligne_median_pt']}pt)")
    print(f"Interligne min-max: {e['interligne_min_pt']}pt - {e['interligne_max_pt']}pt")
    print(f"Espacement paragraphe: {e['espacement_paragraphe_moyen_pt']}pt")

    print(f"\n{'='*30} MARGES {'='*30}")
    m = rapport['marges']
    print(f"Gauche: {m['marge_gauche']['mm']}mm ({m['marge_gauche']['pt']}pt)")
    print(f"Droite: {m['marge_droite']['mm']}mm ({m['marge_droite']['pt']}pt)")
    print(f"Haut: {m['marge_haut']['mm']}mm ({m['marge_haut']['pt']}pt)")
    print(f"Bas: {m['marge_bas']['mm']}mm ({m['marge_bas']['pt']}pt)")
    print(f"Zone de contenu: {m['largeur_contenu_pt']}pt x {m['hauteur_contenu_pt']}pt")

    print(f"\n{'='*30} DENSITE {'='*30}")
    d = rapport['densite']
    print(f"Caractères/ligne: {d['chars_par_ligne_moyen']} (médian: {d['chars_par_ligne_median']})")
    print(f"Lignes/page: {d['lignes_par_page_moyen']}")

    print(f"\n{'='*30} STRUCTURE {'='*30}")
    s = rapport['structure']
    print(f"Éléments en gras: {s['nb_elements_gras']}")
    print(f"Éléments centrés: {s['nb_elements_centres']}")
    print(f"Positions X distinctes: {s['positions_x_distinctes'][:5]}...")

    # Calcul du ratio line-height
    if p['taille_dominante_pt'] > 0 and e['interligne_moyen_pt'] > 0:
        ratio = e['interligne_moyen_pt'] / p['taille_dominante_pt']
        print(f"\n{'='*30} RATIOS CALCULES {'='*30}")
        print(f"Line-height ratio: {ratio:.2f} (interligne/taille police)")


def main():
    parser = argparse.ArgumentParser(description="Audit complet d'un PDF")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Fichier PDF à analyser")
    parser.add_argument("--output", "-o", type=Path, help="Fichier JSON pour le rapport")
    parser.add_argument("--page", "-p", type=int, help="Analyser une page spécifique (1-indexé)")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"[ERREUR] Fichier non trouvé: {args.input}")
        return 1

    if args.page:
        # Analyse d'une page spécifique
        doc = fitz.open(str(args.input))
        resultat = analyser_page_specifique(doc, args.page - 1)
        doc.close()
        print(json.dumps(resultat, indent=2, ensure_ascii=False))
    else:
        # Rapport complet
        rapport = generer_rapport_complet(args.input)
        afficher_rapport_console(rapport)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(rapport, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Rapport JSON sauvegardé: {args.output}")

    return 0


if __name__ == "__main__":
    exit(main())
