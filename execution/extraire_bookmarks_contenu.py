#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraire_bookmarks_contenu.py
=============================

Extrait les bookmarks d'un document DOCX avec leur contenu textuel associé.
Cela permet d'identifier quelles variables correspondent à quelles données.

Usage:
    python extraire_bookmarks_contenu.py --input <document.docx>
"""

import argparse
import json
import zipfile
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from collections import defaultdict

NSMAP = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}


def extraire_bookmarks_avec_contenu(docx_path: Path) -> list:
    """
    Extrait tous les bookmarks avec leur contenu textuel.
    """
    # Lire le document.xml
    with zipfile.ZipFile(docx_path, 'r') as z:
        xml_content = z.read('word/document.xml').decode('utf-8')

    root = ET.fromstring(xml_content)

    # Collecter tous les bookmarkStart et bookmarkEnd avec leurs IDs
    bookmark_starts = {}  # id -> (nom, element)
    bookmark_ends = {}    # id -> element

    for elem in root.iter():
        if elem.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkStart':
            bm_id = elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
            bm_name = elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name')
            if bm_id and bm_name and not bm_name.startswith('_'):
                bookmark_starts[bm_id] = (bm_name, elem)

        elif elem.tag == '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkEnd':
            bm_id = elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
            if bm_id:
                bookmark_ends[bm_id] = elem

    # Pour chaque bookmark, extraire le contenu entre start et end
    bookmarks = []

    for bm_id, (bm_name, start_elem) in bookmark_starts.items():
        # Trouver le parent paragraphe
        parent_para = None
        for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            if start_elem in list(para.iter()):
                parent_para = para
                break

        # Extraire tout le texte du paragraphe contenant le bookmark
        para_text = ''
        if parent_para is not None:
            for t in parent_para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    para_text += t.text

        bookmarks.append({
            'id': bm_id,
            'nom': bm_name,
            'contexte_paragraphe': para_text[:300] if para_text else ''
        })

    return bookmarks


def decoder_nom_bookmark(nom: str) -> dict:
    """
    Décode le nom du bookmark pour comprendre sa signification.
    Basé sur l'analyse des patterns du logiciel notarial.
    """
    info = {
        'nom_original': nom,
        'categorie': 'inconnu',
        'sous_categorie': '',
        'description': '',
        'repetition': None
    }

    # Extraire le numéro de répétition (r1, r2, etc.)
    rep_match = re.search(r'_r(\d+)_', nom)
    if rep_match:
        info['repetition'] = int(rep_match.group(1))

    # Dictionnaire de décodage des préfixes
    prefixes = {
        # Identification de l'acte
        'PYANNEE': ('acte', 'annee', 'Année de l\'acte'),
        'PYARECC': ('acte', 'reference', 'Référence répertoire'),
        'PTIEY': ('acte', 'type', 'Type d\'acte'),

        # Vendeurs
        'PYVENDE': ('vendeur', 'bloc', 'Bloc vendeur complet'),
        'CompPPFSCENCO': ('vendeur', 'personne_femme_celibataire', 'Femme célibataire'),
        'CompPPHSCENCO': ('vendeur', 'personne_homme_celibataire', 'Homme célibataire'),
        'CompPPFMSCOMM': ('vendeur', 'personne_femme_mariee_commun', 'Femme mariée communauté'),
        'CompPPHMSCOMM': ('vendeur', 'personne_homme_marie_commun', 'Homme marié communauté'),
        'CompPPFMSSEPA': ('vendeur', 'personne_femme_mariee_separation', 'Femme mariée séparation'),
        'CompPPHMSSEPA': ('vendeur', 'personne_homme_marie_separation', 'Homme marié séparation'),

        # Acquéreurs
        'PYACQUE': ('acquereur', 'bloc', 'Bloc acquéreur complet'),
        'CompPPHEPAFCO': ('acquereur', 'personne_couple_pacs', 'Couple pacsé'),

        # Quotités
        'QTVENDU': ('quotite', 'vendue', 'Quotité vendue'),
        'QTVEND4': ('quotite', 'vendue_detail', 'Détail quotité vendue'),
        'PXQUOTT': ('quotite', 'acquise', 'Quotité acquise'),
        'PWQUOTI': ('quotite', 'detail', 'Détail quotité'),

        # Représentation
        'PYREPR': ('representation', 'bloc', 'Représentation'),
        'CompPPFSCENPR': ('representation', 'femme_presente', 'Femme présente'),
        'CompPPHSCENPR': ('representation', 'homme_present', 'Homme présent'),
        'CompPPHEPAFPR': ('representation', 'couple_present', 'Couple présent'),

        # Déclarations et vérifications
        'PYDEPAR': ('declaration', 'parties', 'Déclarations des parties'),
        'PCAPAJUS': ('verification', 'capacite', 'Capacité juridique'),
        'CAPACOV': ('verification', 'covid', 'Vérification COVID'),
        'CAPACAA': ('verification', 'capacite_acquereur', 'Capacité acquéreur'),
        'PACTENAI': ('verification', 'acte_naissance', 'Acte de naissance'),
        'PCARTEID': ('verification', 'carte_identite', 'Carte d\'identité'),
        'PIBODACC': ('verification', 'ibod', 'Vérification IBOD'),
        'CONGEL': ('verification', 'gel_avoirs', 'Gel des avoirs'),
        'DOWJONES': ('verification', 'sanctions', 'Liste Dow Jones sanctions'),
        'PJUSTIFI': ('verification', 'justificatifs', 'Justificatifs d\'identité'),

        # Bien immobilier - Adresse
        'PYADRPE': ('bien', 'adresse', 'Adresse du bien'),
        'PSADRPE': ('bien', 'situation', 'Situation du bien'),
        'PSADRPE_AC': ('bien', 'situation_actuelle', 'Situation actuelle'),

        # Bien immobilier - Cadastre
        'PKNCADSIND02': ('bien', 'cadastre', 'Références cadastrales'),
        'GEOPORT': ('bien', 'geoportail', 'Géoportail'),

        # Bien immobilier - Désignation
        'PYDESY3': ('bien', 'designation', 'Désignation du bien'),
        'PXLOTC10': ('bien', 'lot', 'Lot de copropriété'),
        'PXLOTC14': ('bien', 'lot_tantiemes', 'Tantièmes du lot'),
        'PNEWTELQ': ('bien', 'tel_quel', 'Vente en l\'état'),
        'PPLANLOT': ('bien', 'plan_lots', 'Plan des lots'),
        'PYPPLAN': ('bien', 'plan', 'Plan'),

        # Bien - Surface Carrez
        'CARPN7': ('bien', 'carrez_surface', 'Surface Carrez'),
        'CARPN9': ('bien', 'carrez_mesurage', 'Mesurage Carrez'),
        'CARPN10': ('bien', 'carrez_validite', 'Validité Carrez'),
        'CARPN11': ('bien', 'carrez_attestation', 'Attestation Carrez'),

        # État descriptif de division
        'PAEDD22': ('copropriete', 'edd', 'État descriptif de division'),
        'PYEDD11': ('copropriete', 'edd_origine', 'Origine EDD'),
        'PYEDD14': ('copropriete', 'edd_modificatif', 'EDD modificatif'),
        'PYMODR1': ('copropriete', 'modificatif', 'Règlement modificatif'),

        # Mobilier
        'MOBILIV': ('mobilier', 'inclus', 'Mobilier inclus'),
        'EQUIP1': ('mobilier', 'equipements', 'Équipements'),

        # Usage
        'PUSAGE00': ('bien', 'usage_actuel', 'Usage actuel'),
        'PUSAGE01': ('bien', 'usage_futur', 'Usage futur'),
        'PUSAGE10': ('bien', 'usage_destination', 'Destination'),

        # Origine de propriété
        'PYORRM_': ('origine', 'resume', 'Résumé origine'),
        'PYORIV1': ('origine', 'immediate', 'Origine immédiate'),
        'PYORANTV': ('origine', 'anterieure', 'Origine antérieure'),

        # Urbanisme
        'PURBAN1': ('urbanisme', 'certificat', 'Certificat urbanisme'),
        'PURBAN3': ('urbanisme', 'plu', 'PLU'),
        'PURBAN9': ('urbanisme', 'zone', 'Zone urbanisme'),

        # Prix et paiement
        'PRIX': ('prix', 'total', 'Prix total'),
        'PRIXTTC': ('prix', 'ttc', 'Prix TTC'),
        'PXVTT01': ('prix', 'ventilation', 'Ventilation prix'),
        'PXPART': ('prix', 'part', 'Part du prix'),
        'PMODE': ('paiement', 'mode', 'Mode de paiement'),
        'PFINPDC': ('paiement', 'financement', 'Financement'),
        'PCPTANT': ('paiement', 'comptant', 'Comptant'),
        'PVIRE': ('paiement', 'virement', 'Virement'),

        # Prêts
        'PPRETB': ('pret', 'banque', 'Prêt bancaire'),
        'PPRETM': ('pret', 'montant', 'Montant prêt'),
        'PPRETT': ('pret', 'taux', 'Taux prêt'),
        'PPRETD': ('pret', 'duree', 'Durée prêt'),

        # Copropriété
        'PSYNDIC': ('copropriete', 'syndic', 'Syndic'),
        'PSYNADR': ('copropriete', 'syndic_adresse', 'Adresse syndic'),
        'PIMMATR': ('copropriete', 'immatriculation', 'Immatriculation'),
        'PFONDTR': ('copropriete', 'fonds_travaux', 'Fonds de travaux'),
        'PEMPRCO': ('copropriete', 'emprunt_collectif', 'Emprunt collectif'),

        # Diagnostics
        'PDIAGNO': ('diagnostic', 'bloc', 'Diagnostics'),
        'PDPE': ('diagnostic', 'dpe', 'DPE'),
        'PAMIANTE': ('diagnostic', 'amiante', 'Amiante'),
        'PPLOMB': ('diagnostic', 'plomb', 'Plomb'),
        'PELEC': ('diagnostic', 'electricite', 'Électricité'),
        'PGAZ': ('diagnostic', 'gaz', 'Gaz'),
        'PTERMITE': ('diagnostic', 'termites', 'Termites'),
        'PERNMT': ('diagnostic', 'ernmt', 'ERNMT/ERP'),
        'PASSAIN': ('diagnostic', 'assainissement', 'Assainissement'),

        # Annexes
        'WdAnnexe': ('annexe', 'document', 'Document annexe'),

        # Parties diverses
        'PYPART': ('partie', 'developpee', 'Partie développée'),
        'EXPOCLO': ('clause', 'expose', 'Exposé/Cloture'),
        'NATUQPP': ('clause', 'nature_quotite', 'Nature et quotité'),
        'PNEWBIE': ('clause', 'nouveau', 'Nouvelle clause'),
        'TERMVE': ('clause', 'terminologie', 'Terminologie'),

        # Conditions
        'PCDEUXP': ('condition', 'clause_deux_p', 'Clause'),
        'PEDEUXP': ('condition', 'engagement', 'Engagement'),

        # Divers
        'DOC_CONTENT': ('document', 'contenu', 'Contenu document'),
        'ListeDéroulante': ('formulaire', 'liste', 'Liste déroulante'),
        'Texte': ('formulaire', 'champ_texte', 'Champ texte'),
    }

    # Trouver la correspondance
    for prefix, (cat, sous_cat, desc) in prefixes.items():
        if nom.startswith(prefix) or prefix in nom:
            info['categorie'] = cat
            info['sous_categorie'] = sous_cat
            info['description'] = desc
            break

    return info


def generer_schema_variables(bookmarks: list) -> dict:
    """
    Génère un schéma structuré des variables à partir des bookmarks.
    """
    schema = defaultdict(lambda: defaultdict(list))

    for bm in bookmarks:
        decoded = decoder_nom_bookmark(bm['nom'])
        cat = decoded['categorie']
        sous_cat = decoded['sous_categorie']

        variable = {
            'nom_bookmark': bm['nom'],
            'description': decoded['description'],
            'repetition': decoded['repetition'],
            'exemple_contenu': bm['contexte_paragraphe'][:100] if bm['contexte_paragraphe'] else ''
        }

        schema[cat][sous_cat].append(variable)

    # Convertir en dict normal
    return {k: dict(v) for k, v in schema.items()}


def main():
    import sys
    import io
    # Forcer UTF-8 pour la sortie console
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="Extrait les bookmarks avec leur contenu d'un DOCX"
    )
    parser.add_argument('--input', '-i', type=Path, required=True)
    parser.add_argument('--output', '-o', type=Path)

    args = parser.parse_args()

    if not args.input.exists():
        print(f"[ERREUR] Fichier non trouve: {args.input}")
        return 1

    print(f"Extraction des bookmarks de: {args.input}")

    bookmarks = extraire_bookmarks_avec_contenu(args.input)
    print(f"Bookmarks extraits: {len(bookmarks)}")

    # Decoder et structurer
    schema = generer_schema_variables(bookmarks)

    # Sauvegarder d'abord (avant affichage)
    if args.output:
        rapport = {
            'fichier': str(args.input),
            'total_bookmarks': len(bookmarks),
            'bookmarks': bookmarks,
            'schema_variables': schema
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(rapport, f, ensure_ascii=False, indent=2)
        print(f"Rapport sauvegarde: {args.output}")

    # Afficher le resume
    print("\n" + "="*70)
    print("SCHEMA DES VARIABLES IDENTIFIEES")
    print("="*70)

    for categorie, sous_cats in sorted(schema.items()):
        total_vars = sum(len(v) for v in sous_cats.values())
        print(f"\n> {categorie.upper()} ({total_vars} variables)")
        for sous_cat, variables in sorted(sous_cats.items()):
            print(f"  - {sous_cat}: {len(variables)}")

    return 0


if __name__ == '__main__':
    exit(main())
