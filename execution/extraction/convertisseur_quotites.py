# -*- coding: utf-8 -*-
"""
convertisseur_quotites.py
=========================

Module de conversion des quotités entre fractions, pourcentages et texte.

Fonctionnalités:
- Conversion fraction → pourcentage (1/2 → 50%)
- Conversion pourcentage → fraction (50% → 1/2)
- Conversion texte → fraction (moitié → 1/2)
- Normalisation des quotités indivises
"""

import re
from typing import Optional, Tuple, Dict, Union
from fractions import Fraction
from dataclasses import dataclass


@dataclass
class Quotite:
    """Représentation normalisée d'une quotité."""
    numerateur: int
    denominateur: int
    pourcentage: float
    en_lettres: str
    type_droit: str = "pleine propriété"  # ou "nue-propriété", "usufruit"

    def __str__(self) -> str:
        return f"{self.numerateur}/{self.denominateur} ({self.pourcentage:.2f}%) en {self.type_droit}"


# Mapping texte français → fractions
QUOTITES_TEXTE = {
    # Fractions simples
    "totalité": (1, 1),
    "tout": (1, 1),
    "le tout": (1, 1),
    "moitié": (1, 2),
    "la moitié": (1, 2),
    "une moitié": (1, 2),
    "tiers": (1, 3),
    "un tiers": (1, 3),
    "deux tiers": (2, 3),
    "quart": (1, 4),
    "un quart": (1, 4),
    "trois quarts": (3, 4),
    "cinquième": (1, 5),
    "un cinquième": (1, 5),
    "deux cinquièmes": (2, 5),
    "trois cinquièmes": (3, 5),
    "quatre cinquièmes": (4, 5),
    "sixième": (1, 6),
    "un sixième": (1, 6),
    "cinq sixièmes": (5, 6),
    "septième": (1, 7),
    "huitième": (1, 8),
    "neuvième": (1, 9),
    "dixième": (1, 10),
    "un dixième": (1, 10),
    # Tantièmes courants
    "centième": (1, 100),
    "millième": (1, 1000),
    "dix millièmes": (1, 10000),
}

# Mapping inverse pour conversion pourcentage → texte
POURCENTAGES_EXACTS = {
    100.0: "la totalité",
    50.0: "la moitié",
    33.33: "un tiers",
    66.67: "deux tiers",
    25.0: "un quart",
    75.0: "trois quarts",
    20.0: "un cinquième",
    40.0: "deux cinquièmes",
    60.0: "trois cinquièmes",
    80.0: "quatre cinquièmes",
}


def fraction_vers_pourcentage(fraction: str) -> float:
    """
    Convertit une fraction en pourcentage.

    Args:
        fraction: Fraction sous forme "1/2", "moitié", etc.

    Returns:
        Pourcentage (50.0 pour "1/2")

    Examples:
        >>> fraction_vers_pourcentage("1/2")
        50.0
        >>> fraction_vers_pourcentage("moitié")
        50.0
        >>> fraction_vers_pourcentage("125/10000")
        1.25
    """
    if not fraction:
        return 0.0

    fraction = fraction.lower().strip()

    # Cas 1: Texte français
    if fraction in QUOTITES_TEXTE:
        num, den = QUOTITES_TEXTE[fraction]
        return (num / den) * 100

    # Cas 2: Format fraction numérique "1/2"
    match = re.match(r'^(\d+)\s*/\s*(\d+)$', fraction)
    if match:
        num = int(match.group(1))
        den = int(match.group(2))
        if den == 0:
            return 0.0
        return (num / den) * 100

    # Cas 3: Déjà un pourcentage "50%" ou "50.5%"
    match = re.match(r'^(\d+(?:[.,]\d+)?)\s*%?$', fraction)
    if match:
        return float(match.group(1).replace(',', '.'))

    return 0.0


def pourcentage_vers_fraction(pct: float, simplifier: bool = True) -> str:
    """
    Convertit un pourcentage en fraction.

    Args:
        pct: Pourcentage (50.0 pour 50%)
        simplifier: Si True, simplifie la fraction (1/2 au lieu de 50/100)

    Returns:
        Fraction sous forme "1/2"

    Examples:
        >>> pourcentage_vers_fraction(50.0)
        "1/2"
        >>> pourcentage_vers_fraction(33.33)
        "1/3"
        >>> pourcentage_vers_fraction(1.25, simplifier=False)
        "125/10000"
    """
    if pct <= 0 or pct > 100:
        return "0/1"

    if pct == 100:
        return "1/1"

    # Utiliser la bibliothèque fractions pour simplification automatique
    try:
        if simplifier:
            # Limiter la précision pour obtenir des fractions "propres"
            frac = Fraction(pct / 100).limit_denominator(10000)
        else:
            # Garder la précision exacte
            frac = Fraction(pct, 100)

        return f"{frac.numerator}/{frac.denominator}"
    except (ValueError, ZeroDivisionError):
        return "0/1"


def pourcentage_vers_texte(pct: float) -> str:
    """
    Convertit un pourcentage en texte français.

    Args:
        pct: Pourcentage

    Returns:
        Texte français ("la moitié", "un tiers", etc.)

    Examples:
        >>> pourcentage_vers_texte(50.0)
        "la moitié"
        >>> pourcentage_vers_texte(33.33)
        "un tiers"
        >>> pourcentage_vers_texte(47.5)
        "47,50%"
    """
    # Vérifier les pourcentages exacts connus
    for pct_ref, texte in POURCENTAGES_EXACTS.items():
        if abs(pct - pct_ref) < 0.01:
            return texte

    # Sinon retourner le pourcentage formaté
    return f"{pct:.2f}%".replace('.', ',')


def texte_vers_fraction(texte: str) -> Optional[Tuple[int, int]]:
    """
    Convertit un texte français en fraction.

    Args:
        texte: Texte français ("moitié", "un tiers", etc.)

    Returns:
        Tuple (numérateur, dénominateur) ou None si non reconnu

    Examples:
        >>> texte_vers_fraction("moitié")
        (1, 2)
        >>> texte_vers_fraction("trois quarts")
        (3, 4)
    """
    texte = texte.lower().strip()

    # Recherche directe
    if texte in QUOTITES_TEXTE:
        return QUOTITES_TEXTE[texte]

    # Recherche avec "pour" : "pour moitié"
    match = re.match(r'^pour\s+(.+)$', texte)
    if match:
        reste = match.group(1)
        if reste in QUOTITES_TEXTE:
            return QUOTITES_TEXTE[reste]

    return None


def normaliser_quotite(valeur: Union[str, float, Dict]) -> Quotite:
    """
    Normalise une quotité depuis n'importe quel format.

    Args:
        valeur: Peut être:
            - str: "1/2", "moitié", "50%"
            - float: 50.0 (interprété comme pourcentage)
            - dict: {"numerateur": 1, "denominateur": 2} ou {"pourcentage": 50}

    Returns:
        Quotite normalisée

    Examples:
        >>> q = normaliser_quotite("1/2")
        >>> q.pourcentage
        50.0
        >>> q.en_lettres
        "la moitié"
    """
    type_droit = "pleine propriété"

    if isinstance(valeur, dict):
        # Format dictionnaire
        if 'numerateur' in valeur and 'denominateur' in valeur:
            num = valeur['numerateur']
            den = valeur['denominateur']
            pct = (num / den) * 100 if den > 0 else 0
        elif 'pourcentage' in valeur:
            pct = valeur['pourcentage']
            frac = pourcentage_vers_fraction(pct)
            parts = frac.split('/')
            num, den = int(parts[0]), int(parts[1])
        else:
            num, den, pct = 0, 1, 0.0

        type_droit = valeur.get('type_droit', valeur.get('type', 'pleine propriété'))

    elif isinstance(valeur, (int, float)):
        # Interprété comme pourcentage
        pct = float(valeur)
        frac = pourcentage_vers_fraction(pct)
        parts = frac.split('/')
        num, den = int(parts[0]), int(parts[1])

    elif isinstance(valeur, str):
        # Extraire le type de droit si présent
        valeur_lower = valeur.lower()
        if 'nue-propriété' in valeur_lower or 'nue propriété' in valeur_lower:
            type_droit = "nue-propriété"
            valeur = re.sub(r'\s+en\s+nue[- ]propriété', '', valeur, flags=re.IGNORECASE)
        elif 'usufruit' in valeur_lower:
            type_droit = "usufruit"
            valeur = re.sub(r'\s+en\s+usufruit', '', valeur, flags=re.IGNORECASE)
        elif 'pleine propriété' in valeur_lower:
            valeur = re.sub(r'\s+en\s+pleine\s+propriété', '', valeur, flags=re.IGNORECASE)

        valeur = valeur.strip()
        pct = fraction_vers_pourcentage(valeur)
        frac = pourcentage_vers_fraction(pct)
        parts = frac.split('/')
        num, den = int(parts[0]), int(parts[1])
    else:
        num, den, pct = 0, 1, 0.0

    en_lettres = pourcentage_vers_texte(pct)

    return Quotite(
        numerateur=num,
        denominateur=den,
        pourcentage=pct,
        en_lettres=en_lettres,
        type_droit=type_droit
    )


def verifier_total_quotites(quotites: list) -> Tuple[bool, float]:
    """
    Vérifie que les quotités totalisent 100%.

    Args:
        quotites: Liste de quotités (str, float, dict ou Quotite)

    Returns:
        Tuple (valide: bool, total: float)

    Examples:
        >>> verifier_total_quotites(["1/2", "1/2"])
        (True, 100.0)
        >>> verifier_total_quotites(["1/3", "1/3"])
        (False, 66.67)
    """
    total = 0.0
    for q in quotites:
        if isinstance(q, Quotite):
            total += q.pourcentage
        else:
            total += normaliser_quotite(q).pourcentage

    # Tolérance de 0.01% pour les erreurs d'arrondi
    valide = abs(total - 100.0) < 0.01

    return valide, round(total, 2)


def repartir_quotites_egales(nombre_parties: int, type_droit: str = "pleine propriété") -> list:
    """
    Génère des quotités égales pour N parties.

    Args:
        nombre_parties: Nombre de parties
        type_droit: Type de droit

    Returns:
        Liste de Quotite

    Examples:
        >>> repartir_quotites_egales(2)
        [Quotite(1, 2, 50.0, "la moitié", "pleine propriété"), ...]
    """
    if nombre_parties <= 0:
        return []

    pct = 100.0 / nombre_parties
    frac = pourcentage_vers_fraction(pct)
    parts = frac.split('/')
    num, den = int(parts[0]), int(parts[1])
    en_lettres = pourcentage_vers_texte(pct)

    return [
        Quotite(
            numerateur=num,
            denominateur=den,
            pourcentage=pct,
            en_lettres=en_lettres,
            type_droit=type_droit
        )
        for _ in range(nombre_parties)
    ]


# ============================================================================
# Tests intégrés
# ============================================================================

if __name__ == "__main__":
    print("=== Tests du convertisseur de quotités ===\n")

    # Test fraction → pourcentage
    tests_fraction = ["1/2", "moitié", "1/3", "trois quarts", "125/10000"]
    print("Fraction → Pourcentage:")
    for t in tests_fraction:
        print(f"  {t} → {fraction_vers_pourcentage(t):.2f}%")

    print("\nPourcentage → Fraction:")
    tests_pct = [50.0, 33.33, 25.0, 1.25, 100.0]
    for p in tests_pct:
        print(f"  {p}% → {pourcentage_vers_fraction(p)}")

    print("\nPourcentage → Texte:")
    for p in tests_pct:
        print(f"  {p}% → {pourcentage_vers_texte(p)}")

    print("\nNormalisation complète:")
    tests_norm = ["1/2", 50.0, {"numerateur": 1, "denominateur": 4}, "moitié en nue-propriété"]
    for t in tests_norm:
        q = normaliser_quotite(t)
        print(f"  {t} → {q}")

    print("\nVérification totaux:")
    print(f"  ['1/2', '1/2'] → {verifier_total_quotites(['1/2', '1/2'])}")
    print(f"  ['1/3', '1/3'] → {verifier_total_quotites(['1/3', '1/3'])}")
    print(f"  ['1/3', '2/3'] → {verifier_total_quotites(['1/3', '2/3'])}")

    print("\nRépartition égale (3 parties):")
    for q in repartir_quotites_egales(3):
        print(f"  {q}")
