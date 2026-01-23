# -*- coding: utf-8 -*-
"""
Patterns regex avancés pour l'extraction des titres de propriété.

Ce module contient des patterns regex améliorés pour extraire avec précision
les données des actes notariaux français.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class TypePersonne(Enum):
    """Types de personnes dans un acte."""
    PHYSIQUE = "physique"
    MORALE = "morale"


class RegimeMatrimonial(Enum):
    """Régimes matrimoniaux français."""
    COMMUNAUTE_LEGALE = "communauté légale"
    COMMUNAUTE_UNIVERSELLE = "communauté universelle"
    SEPARATION_BIENS = "séparation de biens"
    PARTICIPATION_ACQUETS = "participation aux acquêts"
    COMMUNAUTE_MEUBLES_ACQUETS = "communauté de meubles et acquêts"


@dataclass
class PatternResult:
    """Résultat d'un pattern avec confiance."""
    valeur: Any
    confiance: float
    source: str  # Texte source qui a matché
    pattern_id: str


class PatternsAvances:
    """Classe contenant tous les patterns regex avancés."""

    # ========== DATES ==========

    MOIS_FR = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }

    PATTERNS_DATE = [
        # "19 mars 1987", "1er janvier 2020"
        (r'(\d{1,2}(?:er)?)\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})', 'date_lettres', 0.95),
        # "19/03/1987", "01-01-2020"
        (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', 'date_numerique', 0.90),
        # "le dix-neuf mars mil neuf cent quatre-vingt-sept"
        (r'le\s+([a-zéèêë\-]+)\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(mil[a-zéèêë\s\-]+)', 'date_toutes_lettres', 0.85),
    ]

    # ========== NOTAIRES ==========

    PATTERNS_NOTAIRE = [
        # "Maître Pierre COHENDET, notaire à CHAROLLES"
        (r'Ma[îi]tre\s+([A-ZÉÈÊËa-zéèêë\-]+)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+),?\s*(?:,\s*)?notaire\s+(?:associé\s+)?(?:à|au|en)\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-]+(?:\s+[A-ZÉÈÊËa-zéèêë\-]+)?)', 'notaire_simple', 0.95),
        # "Me DUPONT et Me MARTIN, notaires associés"
        (r'M(?:e|aître)s?\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)\s+et\s+M(?:e|aître)s?\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+),?\s*notaires?\s+associés?', 'notaires_associes', 0.90),
        # "Office notarial de CHAROLLES"
        (r'[Oo]ffice\s+[Nn]otarial\s+(?:de|d\'|du)\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+)', 'office_notarial', 0.85),
        # "SCP DUPONT MARTIN, notaires"
        (r'(?:SCP|SELARL|SAS)\s+([A-ZÉÈÊË][A-ZÉÈÊË\s\-&]+),?\s*notaires?', 'societe_notaires', 0.90),
        # "CRPCEN n° 1234"
        (r'CRPCEN\s*(?:n°|:)?\s*(\d+)', 'crpcen', 0.95),
    ]

    # ========== PUBLICATION ==========

    PATTERNS_PUBLICATION = [
        # "publié au SPF de LYON 1er bureau le 15/04/1987 volume 1234 numéro 56"
        (r'publi[ée]\s+(?:au\s+)?(?:SPF|[Ss]ervice\s+de\s+[Pp]ublicité\s+[Ff]oncière)\s+(?:de\s+)?([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+?)(?:\s+\d+(?:er|e|ème)?\s+bureau)?\s+le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})\s+volume\s+(\d+[A-Z]?)\s+n(?:uméro|°)\s+(\d+)', 'publication_spf_complete', 0.95),
        # "Volume 2024P n° 1234"
        (r'[Vv]olume\s+(\d+[A-Z]?)\s+n(?:uméro|°)\s+(\d+)', 'volume_numero', 0.85),
        # "Référence cadastrale: 2024P01234"
        (r'[Rr]éf(?:érence)?\s+(?:de\s+)?publication\s*:?\s*(\d{4}[A-Z]\d+)', 'reference_publication', 0.90),
        # "SPF de LYON 1"
        (r'SPF\s+(?:de\s+)?([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+?)(?:\s+(\d+)(?:er|e|ème)?\s*(?:bureau)?)?', 'spf_simple', 0.80),
    ]

    # ========== PERSONNES PHYSIQUES ==========

    CIVILITES = r'(?:Monsieur|Madame|Mademoiselle|M\.|Mme|Mlle|Mr)'

    PATTERNS_PERSONNE_PHYSIQUE = [
        # "Monsieur Jean-Pierre DUPONT, né le 15 mars 1960 à LYON"
        (rf'({CIVILITES})\s+([A-ZÉÈÊËa-zéèêë\-]+(?:\s+[A-ZÉÈÊËa-zéèêë\-]+)*)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+),?\s*n[ée]\s+le\s+(\d{{1,2}}(?:er)?)\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{{4}})\s+[àa]\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s\(\)]+)', 'personne_complete', 0.95),
        # Version plus simple
        (rf'({CIVILITES})\s+([A-ZÉÈÊËa-zéèêë\-]+(?:\s+[A-ZÉÈÊËa-zéèêë\-]+)*)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)', 'personne_simple', 0.80),
    ]

    PATTERNS_PROFESSION = [
        # "de profession conseiller bancaire"
        (r'de\s+profession\s+([a-zéèêëàâîïôûùç\s\-]+?)(?:,|\.|demeurant)', 'profession_de', 0.90),
        # "exerçant la profession de..."
        (r'exer[çc]ant\s+(?:la\s+)?profession\s+(?:de\s+)?([a-zéèêëàâîïôûùç\s\-]+?)(?:,|\.)', 'profession_exercant', 0.85),
        # "retraité" / "sans profession"
        (r'(retrait[ée]|sans\s+profession|sans\s+activité)', 'profession_statut', 0.95),
    ]

    PATTERNS_ADRESSE = [
        # "demeurant à LYON (69003), 15 rue de la République"
        (r'demeurant\s+[àa]\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+)\s*\((\d{5})\)\s*,?\s*(\d+(?:bis|ter)?)\s+([a-zéèêëàâîïôûùç\s\-]+)', 'adresse_complete', 0.95),
        # "domicilié 15 rue de la République 69003 LYON"
        (r'domicili[ée]\s+(\d+(?:bis|ter)?)\s+([a-zéèêëàâîïôûùç\s\-]+)\s+(\d{5})\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+)', 'adresse_domicilie', 0.90),
    ]

    # ========== REGIMES MATRIMONIAUX ==========

    PATTERNS_REGIME_MATRIMONIAL = [
        # "marié sous le régime de la communauté légale"
        (r'mari[ée]s?\s+sous\s+le\s+r[ée]gime\s+(?:de\s+)?(?:la\s+)?(communaut[ée]\s+l[ée]gale|communaut[ée]\s+universelle|s[ée]paration\s+de\s+biens|participation\s+aux\s+acqu[êe]ts)', 'regime_sous', 0.95),
        # "époux communs en biens"
        (r'[ée]poux\s+communs?\s+en\s+biens', 'regime_communs_biens', 0.90),
        # "non changé depuis" (pour le régime légal)
        (r'r[ée]gime\s+(?:matrimonial\s+)?non\s+chang[ée]', 'regime_non_change', 0.85),
        # Célibataire
        (r'(c[ée]libataire|non\s+mari[ée])', 'celibataire', 0.95),
        # Divorcé
        (r'(divorc[ée]|s[ée]par[ée]\s+de\s+corps)', 'divorce', 0.95),
        # Veuf
        (r'(veuf|veuve)', 'veuf', 0.95),
        # PACS
        (r'(pacs[ée]|li[ée]\s+par\s+un\s+pacte\s+civil\s+de\s+solidarit[ée])', 'pacs', 0.95),
    ]

    PATTERNS_CONTRAT_MARIAGE = [
        # "suivant contrat reçu par Me DUPONT le 15/03/1985"
        (r'suivant\s+contrat\s+(?:de\s+mariage\s+)?re[çc]u\s+par\s+M(?:e|a[îi]tre)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)\s+(?:,\s*)?(?:notaire\s+)?(?:[àa]\s+[A-ZÉÈÊËa-zéèêë\-\s]+\s+)?le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4})', 'contrat_mariage', 0.95),
    ]

    # ========== QUOTITES ==========

    PATTERNS_QUOTITE = [
        # "pour moitié en pleine propriété"
        (r'pour\s+(moiti[ée]|tiers|quart|totalit[ée]|un\s+quart|trois\s+quarts|deux\s+tiers)\s+en\s+(pleine\s+propri[ée]t[ée]|nue[s\-]?propri[ée]t[ée]|usufruit)', 'quotite_lettres', 0.95),
        # "pour 1/2 en pleine propriété"
        (r'pour\s+(\d+)/(\d+)\s+(?:(?:[èe]me|ème)s?\s+)?(?:indivis\s+)?en\s+(pleine\s+propri[ée]t[ée]|nue[s\-]?propri[ée]t[ée]|usufruit)', 'quotite_fraction', 0.95),
        # "à concurrence de 50%"
        (r'[àa]\s+concurrence\s+de\s+(\d+(?:[,\.]\d+)?)\s*%', 'quotite_pourcentage', 0.90),
        # "pour le tout"
        (r'pour\s+le\s+tout(?:\s+en\s+(pleine\s+propri[ée]t[ée]|nue[s\-]?propri[ée]t[ée]|usufruit))?', 'quotite_tout', 0.95),
    ]

    # ========== BIENS IMMOBILIERS ==========

    PATTERNS_ADRESSE_BIEN = [
        # "Un appartement sis à LYON (69003), 15 rue de la République"
        (r'(?:Un|Une|Le|La|L\')\s+(?:appartement|maison|immeuble|local|terrain|lot)\s+sis(?:e)?\s+[àa]\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+)\s*\((\d{5})\)\s*,?\s*(\d+(?:bis|ter)?)\s+([a-zéèêëàâîïôûùç\s\-]+)', 'adresse_bien_complete', 0.95),
        # "situé 15 rue de la République à LYON"
        (r'situ[ée](?:e)?\s+(\d+(?:bis|ter)?)\s+([a-zéèêëàâîïôûùç\s\-]+)\s+[àa]\s+([A-ZÉÈÊË][A-ZÉÈÊËa-zéèêë\-\s]+)\s*\((\d{5})\)', 'adresse_bien_situee', 0.90),
    ]

    PATTERNS_CADASTRE = [
        # "Section AB numéro 123, lieudit Les Vignes, pour 5a 32ca"
        (r'[Ss]ection\s+([A-Z]{1,2})\s+n(?:uméro|°)\s*(\d+),?\s*(?:lieudit\s+([A-Za-zéèêëàâîïôûùç\s\-\']+))?,?\s*pour\s+(\d+)\s*(?:ha)?\s*(\d+)\s*a\s*(\d+)\s*ca', 'cadastre_complet', 0.95),
        # "cadastré section AB n° 123"
        (r'cadastr[ée]\s+section\s+([A-Z]{1,2})\s+n(?:uméro|°)?\s*(\d+)', 'cadastre_simple', 0.85),
        # "figurant au cadastre pour X m²"
        (r'figurant\s+au\s+cadastre\s+pour\s+(\d+(?:\s*\d+)?)\s*m[²2]', 'superficie_cadastre', 0.90),
    ]

    PATTERNS_LOT = [
        # "Lot numéro 25 : un appartement... et les 125/10000èmes"
        (r'[Ll]ot\s+n(?:uméro|°)?\s*(\d+)\s*:?\s*([^,]+?)(?:,|\.)?\s*(?:et\s+)?(?:les\s+)?(\d+)/(\d+)(?:[èe]me|ème)?s?\s+(?:des\s+)?(?:parties\s+communes|tantièmes)', 'lot_complet', 0.95),
        # "Lot n° 25"
        (r'[Ll]ot\s+n(?:uméro|°)?\s*(\d+)', 'lot_simple', 0.80),
        # "125/10000èmes des parties communes"
        (r'(\d+)/(\d+)(?:[èe]me|ème)?s?\s+(?:des\s+)?(?:parties\s+communes|tantièmes)', 'tantiemes', 0.90),
    ]

    PATTERNS_CARREZ = [
        # "d'une superficie de 45,50 m² (loi Carrez)"
        (r'(?:superficie|surface)\s+(?:de\s+)?(\d+(?:[,\.]\d+)?)\s*m[²2]\s*(?:\((?:loi\s+)?[Cc]arrez\))?', 'carrez', 0.95),
        # "mesurage Carrez: 45,50 m²"
        (r'(?:mesurage|superficie)\s+[Cc]arrez\s*:?\s*(\d+(?:[,\.]\d+)?)\s*m[²2]', 'carrez_explicite', 0.95),
    ]

    # ========== PRIX ==========

    PATTERNS_PRIX = [
        # "moyennant le prix de 150 000 € (cent cinquante mille euros)"
        (r'(?:moyennant|pour)\s+(?:le\s+)?prix\s+(?:principal\s+)?(?:de\s+)?(\d[\d\s]*(?:[,\.]\d+)?)\s*(?:€|EUR|euros?)\s*\(([a-zéèêëàâîïôûùç\s\-]+)\)', 'prix_complet', 0.95),
        # "au prix de 150 000 euros"
        (r'(?:au\s+)?prix\s+(?:de\s+)?(\d[\d\s]*(?:[,\.]\d+)?)\s*(?:€|EUR|euros?)', 'prix_simple', 0.90),
        # En francs (anciens actes): "1 500 000 F"
        (r'(\d[\d\s]*(?:[,\.]\d+)?)\s*(?:F|francs?)', 'prix_francs', 0.85),
    ]

    PATTERNS_PRIX_VENTILATION = [
        # "dont 140 000 € pour le terrain et 10 000 € pour les constructions"
        (r'dont\s+(\d[\d\s]*(?:[,\.]\d+)?)\s*(?:€|EUR|euros?)\s+pour\s+(?:le\s+)?(terrain|constructions?|b[âa]timent)', 'ventilation', 0.90),
        # "frais de notaire estimés à 12 000 €"
        (r'frais\s+(?:de\s+)?(?:notaire|acte)\s+(?:estim[ée]s?\s+)?[àa]\s+(\d[\d\s]*(?:[,\.]\d+)?)\s*(?:€|EUR|euros?)', 'frais_notaire', 0.85),
    ]

    # ========== ORIGINE DE PROPRIETE ==========

    PATTERNS_ORIGINE = [
        # "aux termes d'un acte reçu par Me DUPONT le 15/03/2010, publié..."
        (r'aux\s+termes\s+d\'un\s+acte\s+(?:de\s+)?([a-zéèêëàâîïôûùç\s]+)\s+re[çc]u\s+par\s+M(?:e|a[îi]tre)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)(?:,?\s*notaire\s+[àa]\s+([A-ZÉÈÊËa-zéèêë\-\s]+))?\s+le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4})', 'origine_acte', 0.95),
        # "par succession de M. DUPONT décédé le..."
        (r'par\s+(?:voie\s+de\s+)?succession\s+(?:de\s+)?(?:M\.|Mme|M(?:onsieur|adame))\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)\s+d[ée]c[ée]d[ée]\s+le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4})', 'origine_succession', 0.90),
        # "par donation reçue par Me..."
        (r'par\s+(?:voie\s+de\s+)?donation\s+re[çc]ue\s+par\s+M(?:e|a[îi]tre)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)\s+le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4})', 'origine_donation', 0.90),
    ]

    # ========== COPROPRIETE ==========

    PATTERNS_COPROPRIETE = [
        # "règlement de copropriété établi par Me DUPONT le 15/03/1970"
        (r'r[èe]glement\s+de\s+copropri[ée]t[ée]\s+[ée]tabli\s+(?:aux\s+termes\s+d\'un\s+acte\s+re[çc]u\s+)?par\s+M(?:e|a[îi]tre)\s+([A-ZÉÈÊË][A-ZÉÈÊË\-]+)(?:,?\s*notaire\s+[àa]\s+([A-ZÉÈÊËa-zéèêë\-\s]+))?\s+le\s+(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4})', 'reglement_copro', 0.95),
        # "syndic: Cabinet FONCIA"
        (r'[Ss]yndic\s*(?:de\s+copropri[ée]t[ée])?\s*:\s*([A-ZÉÈÊËa-zéèêë\s\-&]+?)(?:,|\.|\s+(?:sis|ayant))', 'syndic', 0.90),
        # "immatriculé sous le numéro 12345"
        (r'immatricul[ée]\s+(?:au\s+registre\s+national\s+des\s+copropri[ée]t[ée]s\s+)?sous\s+le\s+n(?:uméro|°)\s*(\d+)', 'immatriculation_copro', 0.95),
    ]

    @classmethod
    def extraire_date(cls, texte: str) -> List[PatternResult]:
        """Extrait toutes les dates du texte."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_DATE:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                resultats.append(PatternResult(
                    valeur=match.group(0),
                    confiance=confiance,
                    source=match.group(0),
                    pattern_id=pattern_id
                ))
        return resultats

    @classmethod
    def extraire_notaire(cls, texte: str) -> List[PatternResult]:
        """Extrait les informations du notaire."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_NOTAIRE:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                if pattern_id == 'notaire_simple':
                    resultats.append(PatternResult(
                        valeur={
                            'prenom': match.group(1),
                            'nom': match.group(2),
                            'ville': match.group(3).strip()
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                elif pattern_id == 'crpcen':
                    resultats.append(PatternResult(
                        valeur={'crpcen': match.group(1)},
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                else:
                    resultats.append(PatternResult(
                        valeur=match.group(0),
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
        return resultats

    @classmethod
    def extraire_publication(cls, texte: str) -> List[PatternResult]:
        """Extrait les références de publication."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_PUBLICATION:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                if pattern_id == 'publication_spf_complete':
                    resultats.append(PatternResult(
                        valeur={
                            'spf': match.group(1).strip(),
                            'date': match.group(2),
                            'volume': match.group(3),
                            'numero': match.group(4)
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                else:
                    resultats.append(PatternResult(
                        valeur=match.group(0),
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
        return resultats

    @classmethod
    def extraire_personnes(cls, texte: str) -> List[PatternResult]:
        """Extrait les personnes physiques."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_PERSONNE_PHYSIQUE:
            for match in re.finditer(pattern, texte):
                if pattern_id == 'personne_complete':
                    resultats.append(PatternResult(
                        valeur={
                            'civilite': match.group(1),
                            'prenoms': match.group(2),
                            'nom': match.group(3),
                            'date_naissance': f"{match.group(4)} {match.group(5)} {match.group(6)}",
                            'lieu_naissance': match.group(7).strip()
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                else:
                    resultats.append(PatternResult(
                        valeur={
                            'civilite': match.group(1),
                            'prenoms': match.group(2),
                            'nom': match.group(3)
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
        return resultats

    @classmethod
    def extraire_lots(cls, texte: str) -> List[PatternResult]:
        """Extrait les lots de copropriété."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_LOT:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                if pattern_id == 'lot_complet':
                    resultats.append(PatternResult(
                        valeur={
                            'numero': int(match.group(1)),
                            'description': match.group(2).strip(),
                            'tantiemes': {
                                'valeur': int(match.group(3)),
                                'base': int(match.group(4))
                            }
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                elif pattern_id == 'lot_simple':
                    resultats.append(PatternResult(
                        valeur={'numero': int(match.group(1))},
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                elif pattern_id == 'tantiemes':
                    resultats.append(PatternResult(
                        valeur={
                            'valeur': int(match.group(1)),
                            'base': int(match.group(2))
                        },
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
        return resultats

    @classmethod
    def extraire_prix(cls, texte: str) -> List[PatternResult]:
        """Extrait les informations de prix."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_PRIX:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                montant_str = match.group(1).replace(' ', '').replace(',', '.')
                try:
                    montant = float(montant_str)
                    result = {'montant': montant}
                    if pattern_id == 'prix_complet':
                        result['en_lettres'] = match.group(2)
                    if pattern_id == 'prix_francs':
                        result['devise'] = 'FRF'
                    else:
                        result['devise'] = 'EUR'
                    resultats.append(PatternResult(
                        valeur=result,
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                except ValueError:
                    pass
        return resultats

    @classmethod
    def extraire_regime_matrimonial(cls, texte: str) -> List[PatternResult]:
        """Extrait le régime matrimonial."""
        resultats = []
        for pattern, pattern_id, confiance in cls.PATTERNS_REGIME_MATRIMONIAL:
            for match in re.finditer(pattern, texte, re.IGNORECASE):
                if pattern_id == 'regime_sous':
                    regime = match.group(1).lower()
                    resultats.append(PatternResult(
                        valeur={'statut': 'marie', 'regime': regime},
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                elif pattern_id in ['celibataire', 'divorce', 'veuf', 'pacs']:
                    resultats.append(PatternResult(
                        valeur={'statut': pattern_id},
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
                else:
                    resultats.append(PatternResult(
                        valeur=match.group(0),
                        confiance=confiance,
                        source=match.group(0),
                        pattern_id=pattern_id
                    ))
        return resultats

    @classmethod
    def extraire_tout(cls, texte: str) -> Dict[str, List[PatternResult]]:
        """Extrait toutes les informations du texte."""
        return {
            'dates': cls.extraire_date(texte),
            'notaires': cls.extraire_notaire(texte),
            'publications': cls.extraire_publication(texte),
            'personnes': cls.extraire_personnes(texte),
            'lots': cls.extraire_lots(texte),
            'prix': cls.extraire_prix(texte),
            'regimes_matrimoniaux': cls.extraire_regime_matrimonial(texte)
        }


# Export pour utilisation directe
extraire_date = PatternsAvances.extraire_date
extraire_notaire = PatternsAvances.extraire_notaire
extraire_publication = PatternsAvances.extraire_publication
extraire_personnes = PatternsAvances.extraire_personnes
extraire_lots = PatternsAvances.extraire_lots
extraire_prix = PatternsAvances.extraire_prix
extraire_regime_matrimonial = PatternsAvances.extraire_regime_matrimonial
extraire_tout = PatternsAvances.extraire_tout
