#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verifier_export.py
==================

Script de verification de conformite entre un document genere et l'original.

Fonctionnalites:
- Compare le nombre de pages (via PyMuPDF/fitz)
- Verifie les polices utilisees
- Detecte la presence de tableaux
- Verifie l'absence de commentaires HTML
- Analyse le format de pagination

Usage:
    python verifier_export.py --genere fichier.pdf --original docs_originels/...

Dependances:
    pip install pymupdf
"""

import argparse
import json
import re
import statistics
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class NiveauDifference(Enum):
    """Niveau de gravite des differences."""
    CRITIQUE = "CRITIQUE"       # Difference majeure - echec probable
    AVERTISSEMENT = "AVERTISSEMENT"  # Difference notable
    INFO = "INFO"              # Information


@dataclass
class Difference:
    """Represente une difference detectee."""
    niveau: NiveauDifference
    categorie: str
    message: str
    valeur_generee: Any = None
    valeur_originale: Any = None
    impact_score: float = 0.0  # Impact sur le score (0-1)


@dataclass
class RapportVerification:
    """Rapport complet de verification."""
    fichier_genere: str
    fichier_original: str
    score_conformite: float = 100.0
    differences: List[Difference] = field(default_factory=list)
    metriques: Dict[str, Any] = field(default_factory=dict)

    def ajouter_difference(self, diff: Difference):
        """Ajoute une difference et met a jour le score."""
        self.differences.append(diff)
        self.score_conformite -= diff.impact_score
        if self.score_conformite < 0:
            self.score_conformite = 0


class VerificateurExport:
    """
    Verificateur de conformite entre documents PDF.
    """

    def __init__(self, chemin_genere: Path, chemin_original: Path):
        """
        Initialise le verificateur.

        Args:
            chemin_genere: Chemin du fichier PDF genere
            chemin_original: Chemin du fichier PDF original
        """
        self.chemin_genere = chemin_genere
        self.chemin_original = chemin_original
        self.doc_genere: Optional[fitz.Document] = None
        self.doc_original: Optional[fitz.Document] = None
        self.rapport = RapportVerification(
            fichier_genere=str(chemin_genere.name),
            fichier_original=str(chemin_original.name)
        )

    def __enter__(self):
        """Ouvre les documents."""
        self.doc_genere = fitz.open(str(self.chemin_genere))
        self.doc_original = fitz.open(str(self.chemin_original))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme les documents."""
        if self.doc_genere:
            self.doc_genere.close()
        if self.doc_original:
            self.doc_original.close()

    def verifier_tout(self) -> RapportVerification:
        """
        Execute toutes les verifications.

        Returns:
            Rapport de verification complet
        """
        # 1. Nombre de pages
        self._verifier_nombre_pages()

        # 2. Polices utilisees
        self._verifier_polices()

        # 3. Presence de tableaux
        self._verifier_tableaux()

        # 4. Commentaires HTML (dans le texte extrait)
        self._verifier_commentaires_html()

        # 5. Format de pagination
        self._verifier_pagination()

        # 6. Metriques supplementaires
        self._calculer_metriques_supplementaires()

        return self.rapport

    def _verifier_nombre_pages(self):
        """Verifie que le nombre de pages correspond."""
        pages_genere = len(self.doc_genere)
        pages_original = len(self.doc_original)

        self.rapport.metriques['pages'] = {
            'genere': pages_genere,
            'original': pages_original,
            'difference': pages_genere - pages_original
        }

        if pages_genere != pages_original:
            diff_abs = abs(pages_genere - pages_original)
            diff_pct = diff_abs / pages_original * 100 if pages_original > 0 else 100

            # Determiner le niveau de gravite
            if diff_pct > 20:
                niveau = NiveauDifference.CRITIQUE
                impact = 25.0
            elif diff_pct > 10:
                niveau = NiveauDifference.AVERTISSEMENT
                impact = 10.0
            else:
                niveau = NiveauDifference.INFO
                impact = 5.0

            self.rapport.ajouter_difference(Difference(
                niveau=niveau,
                categorie="PAGES",
                message=f"Nombre de pages different: {pages_genere} vs {pages_original} ({diff_pct:.1f}%)",
                valeur_generee=pages_genere,
                valeur_originale=pages_original,
                impact_score=impact
            ))

    def _extraire_polices(self, doc: fitz.Document) -> Dict[str, int]:
        """
        Extrait les polices utilisees dans un document.

        Args:
            doc: Document PyMuPDF

        Returns:
            Dict des polices avec leur nombre d'occurrences
        """
        polices = Counter()

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        font = span.get("font", "Unknown")
                        # Normaliser le nom de la police
                        font_base = self._normaliser_police(font)
                        polices[font_base] += 1

        return dict(polices)

    def _normaliser_police(self, nom_police: str) -> str:
        """
        Normalise le nom d'une police pour comparaison.

        Args:
            nom_police: Nom brut de la police

        Returns:
            Nom normalise
        """
        # Enlever les suffixes de style (Bold, Italic, etc.)
        nom = nom_police.lower()
        suffixes = ['-bold', '-italic', '-regular', '-light', '-medium',
                   'bold', 'italic', 'regular', 'light', 'medium',
                   '-oblique', 'oblique', '-semibold', 'semibold']
        for suffix in suffixes:
            nom = nom.replace(suffix, '')

        # Normaliser les noms communs
        nom = nom.strip('-').strip()
        return nom

    def _verifier_polices(self):
        """Verifie la correspondance des polices utilisees."""
        polices_genere = self._extraire_polices(self.doc_genere)
        polices_original = self._extraire_polices(self.doc_original)

        # Polices dominantes
        police_dom_genere = max(polices_genere.items(), key=lambda x: x[1])[0] if polices_genere else "None"
        police_dom_original = max(polices_original.items(), key=lambda x: x[1])[0] if polices_original else "None"

        self.rapport.metriques['polices'] = {
            'genere': dict(Counter(polices_genere).most_common(5)),
            'original': dict(Counter(polices_original).most_common(5)),
            'police_dominante_genere': police_dom_genere,
            'police_dominante_original': police_dom_original
        }

        # Verifier si la police dominante est la meme
        if police_dom_genere != police_dom_original:
            # Verifier similarite
            if not self._polices_similaires(police_dom_genere, police_dom_original):
                self.rapport.ajouter_difference(Difference(
                    niveau=NiveauDifference.AVERTISSEMENT,
                    categorie="POLICES",
                    message=f"Police dominante differente: '{police_dom_genere}' vs '{police_dom_original}'",
                    valeur_generee=police_dom_genere,
                    valeur_originale=police_dom_original,
                    impact_score=10.0
                ))

        # Verifier les polices manquantes ou supplementaires
        polices_set_gen = set(polices_genere.keys())
        polices_set_orig = set(polices_original.keys())

        polices_manquantes = polices_set_orig - polices_set_gen
        polices_supplementaires = polices_set_gen - polices_set_orig

        if polices_manquantes:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.INFO,
                categorie="POLICES",
                message=f"Polices de l'original non presentes: {', '.join(polices_manquantes)}",
                valeur_generee=list(polices_set_gen),
                valeur_originale=list(polices_manquantes),
                impact_score=2.0
            ))

        if polices_supplementaires:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.INFO,
                categorie="POLICES",
                message=f"Polices supplementaires dans le genere: {', '.join(polices_supplementaires)}",
                valeur_generee=list(polices_supplementaires),
                valeur_originale=list(polices_set_orig),
                impact_score=1.0
            ))

    def _polices_similaires(self, police1: str, police2: str) -> bool:
        """
        Verifie si deux polices sont similaires.

        Args:
            police1: Premiere police
            police2: Deuxieme police

        Returns:
            True si similaires
        """
        # Familles de polices equivalentes
        familles_equivalentes = [
            {'times', 'timesnewroman', 'times-roman', 'timesroman'},
            {'arial', 'helvetica', 'arialmt'},
            {'courier', 'couriernew'},
            {'garamond', 'ebgaramond', 'garamondpremier'},
            {'calibri', 'carlito'},
        ]

        p1 = police1.lower().replace(' ', '').replace('-', '')
        p2 = police2.lower().replace(' ', '').replace('-', '')

        for famille in familles_equivalentes:
            if p1 in famille and p2 in famille:
                return True

        return p1 == p2

    def _detecter_tableaux(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Detecte la presence de tableaux dans un document.

        Args:
            doc: Document PyMuPDF

        Returns:
            Liste des tableaux detectes
        """
        tableaux = []

        for page_num, page in enumerate(doc):
            # Methode 1: Chercher des lignes horizontales et verticales
            drawings = page.get_drawings()
            lignes_h = []
            lignes_v = []

            for drawing in drawings:
                for item in drawing.get("items", []):
                    if item[0] == "l":  # Ligne
                        p1, p2 = item[1], item[2]
                        # Ligne horizontale
                        if abs(p1.y - p2.y) < 2:
                            lignes_h.append((p1.y, min(p1.x, p2.x), max(p1.x, p2.x)))
                        # Ligne verticale
                        elif abs(p1.x - p2.x) < 2:
                            lignes_v.append((p1.x, min(p1.y, p2.y), max(p1.y, p2.y)))

            # Si on a plusieurs lignes horizontales et verticales proches, c'est probablement un tableau
            if len(lignes_h) >= 3 and len(lignes_v) >= 2:
                tableaux.append({
                    'page': page_num + 1,
                    'lignes_h': len(lignes_h),
                    'lignes_v': len(lignes_v),
                    'type': 'graphique'
                })

            # Methode 2: Analyser l'alignement du texte
            blocks = page.get_text("dict")["blocks"]
            positions_x = []

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    x = round(line["bbox"][0], 0)
                    positions_x.append(x)

            # Si plusieurs colonnes alignees, potentiel tableau
            position_counts = Counter(positions_x)
            colonnes_multiples = [x for x, count in position_counts.items() if count >= 3]

            if len(colonnes_multiples) >= 3:
                tableaux.append({
                    'page': page_num + 1,
                    'colonnes': len(colonnes_multiples),
                    'type': 'alignement'
                })

        return tableaux

    def _verifier_tableaux(self):
        """Verifie la presence et correspondance des tableaux."""
        tableaux_genere = self._detecter_tableaux(self.doc_genere)
        tableaux_original = self._detecter_tableaux(self.doc_original)

        nb_tableaux_gen = len(tableaux_genere)
        nb_tableaux_orig = len(tableaux_original)

        self.rapport.metriques['tableaux'] = {
            'genere': nb_tableaux_gen,
            'original': nb_tableaux_orig,
            'details_genere': tableaux_genere[:5],
            'details_original': tableaux_original[:5]
        }

        if nb_tableaux_orig > 0 and nb_tableaux_gen == 0:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.CRITIQUE,
                categorie="TABLEAUX",
                message=f"Tableaux manquants: l'original contient {nb_tableaux_orig} tableau(x), le genere n'en contient aucun",
                valeur_generee=nb_tableaux_gen,
                valeur_originale=nb_tableaux_orig,
                impact_score=15.0
            ))
        elif abs(nb_tableaux_gen - nb_tableaux_orig) > 0:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.AVERTISSEMENT,
                categorie="TABLEAUX",
                message=f"Nombre de tableaux different: {nb_tableaux_gen} vs {nb_tableaux_orig}",
                valeur_generee=nb_tableaux_gen,
                valeur_originale=nb_tableaux_orig,
                impact_score=5.0
            ))

    def _extraire_texte_complet(self, doc: fitz.Document) -> str:
        """
        Extrait tout le texte d'un document.

        Args:
            doc: Document PyMuPDF

        Returns:
            Texte complet
        """
        texte = ""
        for page in doc:
            texte += page.get_text()
        return texte

    def _verifier_commentaires_html(self):
        """Verifie l'absence de commentaires HTML dans le texte."""
        texte_genere = self._extraire_texte_complet(self.doc_genere)

        # Patterns de commentaires HTML
        patterns_html = [
            r'<!--.*?-->',           # Commentaires HTML classiques
            r'<!\[CDATA\[.*?\]\]>',  # Sections CDATA
            r'&lt;!--.*?--&gt;',     # Commentaires echappes
        ]

        commentaires_trouves = []

        for pattern in patterns_html:
            matches = re.findall(pattern, texte_genere, re.DOTALL | re.IGNORECASE)
            commentaires_trouves.extend(matches)

        # Verifier aussi les balises HTML residuelles
        balises_html = re.findall(r'</?[a-z][a-z0-9]*[^>]*>', texte_genere, re.IGNORECASE)

        self.rapport.metriques['commentaires_html'] = {
            'commentaires_trouves': len(commentaires_trouves),
            'balises_html_residuelles': len(balises_html),
            'exemples_commentaires': commentaires_trouves[:3],
            'exemples_balises': balises_html[:5]
        }

        if commentaires_trouves:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.CRITIQUE,
                categorie="HTML",
                message=f"Commentaires HTML detectes dans le document ({len(commentaires_trouves)} occurrence(s))",
                valeur_generee=commentaires_trouves[:3],
                valeur_originale="Aucun attendu",
                impact_score=20.0
            ))

        if balises_html:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.AVERTISSEMENT,
                categorie="HTML",
                message=f"Balises HTML residuelles detectees ({len(balises_html)} occurrence(s))",
                valeur_generee=balises_html[:5],
                valeur_originale="Aucune attendue",
                impact_score=10.0
            ))

    def _detecter_format_pagination(self, doc: fitz.Document) -> Dict[str, Any]:
        """
        Detecte le format de pagination d'un document.

        Args:
            doc: Document PyMuPDF

        Returns:
            Informations sur la pagination
        """
        pagination_info = {
            'detectee': False,
            'format': None,
            'position': None,
            'pages_avec_numero': [],
            'exemples': []
        }

        # Patterns de pagination courants
        patterns_pagination = [
            r'^\s*[-—]\s*(\d+)\s*[-—]\s*$',                    # - 1 -
            r'^\s*Page\s+(\d+)\s*$',                           # Page 1
            r'^\s*(\d+)\s*/\s*(\d+)\s*$',                      # 1/10
            r'^\s*Page\s+(\d+)\s+sur\s+(\d+)\s*$',             # Page 1 sur 10
            r'^\s*(\d+)\s*$',                                   # 1
        ]

        for page_num, page in enumerate(doc):
            # Analyser le bas de la page
            page_height = page.rect.height
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                # Verifier si le bloc est en bas de page (dernier 10%)
                if block["bbox"][1] > page_height * 0.9:
                    for line in block["lines"]:
                        texte_ligne = "".join(span.get("text", "") for span in line["spans"]).strip()

                        for pattern in patterns_pagination:
                            match = re.match(pattern, texte_ligne, re.IGNORECASE)
                            if match:
                                pagination_info['detectee'] = True
                                pagination_info['pages_avec_numero'].append(page_num + 1)
                                pagination_info['exemples'].append({
                                    'page': page_num + 1,
                                    'texte': texte_ligne,
                                    'position_y': round(block["bbox"][1], 1)
                                })

                                # Determiner le format
                                if 'Page' in texte_ligne and 'sur' in texte_ligne:
                                    pagination_info['format'] = 'Page X sur Y'
                                elif 'Page' in texte_ligne:
                                    pagination_info['format'] = 'Page X'
                                elif '/' in texte_ligne:
                                    pagination_info['format'] = 'X/Y'
                                elif '-' in texte_ligne or '—' in texte_ligne:
                                    pagination_info['format'] = '- X -'
                                else:
                                    pagination_info['format'] = 'X'

                                pagination_info['position'] = 'bas'
                                break

        return pagination_info

    def _verifier_pagination(self):
        """Verifie la correspondance du format de pagination."""
        pagination_genere = self._detecter_format_pagination(self.doc_genere)
        pagination_original = self._detecter_format_pagination(self.doc_original)

        self.rapport.metriques['pagination'] = {
            'genere': pagination_genere,
            'original': pagination_original
        }

        # Verifier la coherence
        if pagination_original['detectee'] and not pagination_genere['detectee']:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.AVERTISSEMENT,
                categorie="PAGINATION",
                message="L'original a une pagination, le document genere n'en a pas",
                valeur_generee="Aucune pagination",
                valeur_originale=pagination_original['format'],
                impact_score=5.0
            ))
        elif pagination_genere['detectee'] and not pagination_original['detectee']:
            self.rapport.ajouter_difference(Difference(
                niveau=NiveauDifference.INFO,
                categorie="PAGINATION",
                message="Le document genere a une pagination, l'original n'en a pas",
                valeur_generee=pagination_genere['format'],
                valeur_originale="Aucune pagination",
                impact_score=2.0
            ))
        elif pagination_genere['detectee'] and pagination_original['detectee']:
            if pagination_genere['format'] != pagination_original['format']:
                self.rapport.ajouter_difference(Difference(
                    niveau=NiveauDifference.AVERTISSEMENT,
                    categorie="PAGINATION",
                    message=f"Format de pagination different: '{pagination_genere['format']}' vs '{pagination_original['format']}'",
                    valeur_generee=pagination_genere['format'],
                    valeur_originale=pagination_original['format'],
                    impact_score=3.0
                ))

    def _calculer_metriques_supplementaires(self):
        """Calcule des metriques supplementaires pour le rapport."""
        # Tailles des fichiers
        self.rapport.metriques['taille_fichiers'] = {
            'genere_ko': round(self.chemin_genere.stat().st_size / 1024, 1),
            'original_ko': round(self.chemin_original.stat().st_size / 1024, 1)
        }

        # Densite de texte
        texte_gen = self._extraire_texte_complet(self.doc_genere)
        texte_orig = self._extraire_texte_complet(self.doc_original)

        mots_gen = len(texte_gen.split())
        mots_orig = len(texte_orig.split())

        self.rapport.metriques['densite_texte'] = {
            'mots_genere': mots_gen,
            'mots_original': mots_orig,
            'difference_pct': round((mots_gen - mots_orig) / mots_orig * 100, 1) if mots_orig > 0 else 0
        }


def afficher_rapport(rapport: RapportVerification):
    """Affiche le rapport de verification en console."""
    print("=" * 70)
    print("RAPPORT DE VERIFICATION D'EXPORT")
    print("=" * 70)

    print(f"\nFichier genere:  {rapport.fichier_genere}")
    print(f"Fichier original: {rapport.fichier_original}")

    # Score
    print(f"\n{'='*30} SCORE {'='*31}")
    if rapport.score_conformite >= 90:
        status = "[OK]"
    elif rapport.score_conformite >= 70:
        status = "[ATTENTION]"
    else:
        status = "[ECHEC]"

    print(f"Score de conformite: {rapport.score_conformite:.1f}/100 {status}")

    # Differences par niveau
    critiques = [d for d in rapport.differences if d.niveau == NiveauDifference.CRITIQUE]
    avertissements = [d for d in rapport.differences if d.niveau == NiveauDifference.AVERTISSEMENT]
    infos = [d for d in rapport.differences if d.niveau == NiveauDifference.INFO]

    if critiques:
        print(f"\n{'='*30} CRITIQUES ({len(critiques)}) {'='*24}")
        for diff in critiques:
            print(f"   [{diff.categorie}] {diff.message}")
            if diff.valeur_generee is not None:
                print(f"      Genere: {diff.valeur_generee}")
            if diff.valeur_originale is not None:
                print(f"      Original: {diff.valeur_originale}")

    if avertissements:
        print(f"\n{'='*30} AVERTISSEMENTS ({len(avertissements)}) {'='*17}")
        for diff in avertissements:
            print(f"   [{diff.categorie}] {diff.message}")

    if infos:
        print(f"\n{'='*30} INFORMATIONS ({len(infos)}) {'='*20}")
        for diff in infos:
            print(f"   [{diff.categorie}] {diff.message}")

    # Metriques
    print(f"\n{'='*30} METRIQUES {'='*28}")

    if 'pages' in rapport.metriques:
        p = rapport.metriques['pages']
        print(f"   Pages: {p['genere']} (genere) vs {p['original']} (original)")

    if 'polices' in rapport.metriques:
        pol = rapport.metriques['polices']
        print(f"   Police dominante genere: {pol['police_dominante_genere']}")
        print(f"   Police dominante original: {pol['police_dominante_original']}")

    if 'tableaux' in rapport.metriques:
        t = rapport.metriques['tableaux']
        print(f"   Tableaux: {t['genere']} (genere) vs {t['original']} (original)")

    if 'commentaires_html' in rapport.metriques:
        h = rapport.metriques['commentaires_html']
        print(f"   Commentaires HTML: {h['commentaires_trouves']}")
        print(f"   Balises HTML residuelles: {h['balises_html_residuelles']}")

    if 'pagination' in rapport.metriques:
        pag = rapport.metriques['pagination']
        format_gen = pag['genere'].get('format', 'Non detecte')
        format_orig = pag['original'].get('format', 'Non detecte')
        print(f"   Pagination genere: {format_gen}")
        print(f"   Pagination original: {format_orig}")

    if 'densite_texte' in rapport.metriques:
        d = rapport.metriques['densite_texte']
        print(f"   Mots: {d['mots_genere']} (genere) vs {d['mots_original']} (original) [{d['difference_pct']:+.1f}%]")

    print("\n" + "=" * 70)


def generer_json(rapport: RapportVerification) -> Dict[str, Any]:
    """
    Genere une representation JSON du rapport.

    Args:
        rapport: Rapport de verification

    Returns:
        Dict serialisable en JSON
    """
    return {
        'fichier_genere': rapport.fichier_genere,
        'fichier_original': rapport.fichier_original,
        'score_conformite': rapport.score_conformite,
        'statut': 'OK' if rapport.score_conformite >= 90 else ('ATTENTION' if rapport.score_conformite >= 70 else 'ECHEC'),
        'differences': [
            {
                'niveau': diff.niveau.value,
                'categorie': diff.categorie,
                'message': diff.message,
                'valeur_generee': str(diff.valeur_generee) if diff.valeur_generee is not None else None,
                'valeur_originale': str(diff.valeur_originale) if diff.valeur_originale is not None else None,
                'impact_score': diff.impact_score
            }
            for diff in rapport.differences
        ],
        'metriques': rapport.metriques,
        'resume': {
            'nb_critiques': len([d for d in rapport.differences if d.niveau == NiveauDifference.CRITIQUE]),
            'nb_avertissements': len([d for d in rapport.differences if d.niveau == NiveauDifference.AVERTISSEMENT]),
            'nb_infos': len([d for d in rapport.differences if d.niveau == NiveauDifference.INFO])
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verifie la conformite d'un document genere par rapport a l'original"
    )
    parser.add_argument(
        '--genere', '-g',
        type=Path,
        required=True,
        help="Chemin vers le fichier PDF genere"
    )
    parser.add_argument(
        '--original', '-o',
        type=Path,
        required=True,
        help="Chemin vers le fichier PDF original"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Sortie au format JSON"
    )
    parser.add_argument(
        '--output', '-O',
        type=Path,
        help="Fichier de sortie pour le rapport JSON"
    )
    parser.add_argument(
        '--seuil',
        type=float,
        default=70.0,
        help="Seuil minimum de conformite (defaut: 70)"
    )

    args = parser.parse_args()

    # Verifier PyMuPDF
    if not PYMUPDF_AVAILABLE:
        print("[ERREUR] PyMuPDF non installe. Installez-le avec:")
        print("  pip install pymupdf")
        return 1

    # Verifier les fichiers
    if not args.genere.exists():
        print(f"[ERREUR] Fichier genere non trouve: {args.genere}")
        return 1

    if not args.original.exists():
        print(f"[ERREUR] Fichier original non trouve: {args.original}")
        return 1

    # Verifier les extensions
    if args.genere.suffix.lower() != '.pdf':
        print(f"[ERREUR] Le fichier genere doit etre un PDF: {args.genere}")
        return 1

    if args.original.suffix.lower() != '.pdf':
        print(f"[ERREUR] Le fichier original doit etre un PDF: {args.original}")
        return 1

    # Executer la verification
    try:
        with VerificateurExport(args.genere, args.original) as verificateur:
            rapport = verificateur.verifier_tout()
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la verification: {e}")
        return 1

    # Afficher/sauvegarder le resultat
    if args.json or args.output:
        resultat_json = generer_json(rapport)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(resultat_json, f, indent=2, ensure_ascii=False)
            print(f"[OK] Rapport sauvegarde: {args.output}")

        if args.json:
            print(json.dumps(resultat_json, indent=2, ensure_ascii=False))
    else:
        afficher_rapport(rapport)

    # Code de retour base sur le seuil
    if rapport.score_conformite >= args.seuil:
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
