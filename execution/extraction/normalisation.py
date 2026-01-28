# -*- coding: utf-8 -*-
"""
normalisation.py
================

Module de normalisation des données extraites des actes notariaux.

Fonctionnalités:
- Normalisation des régimes matrimoniaux
- Normalisation des situations familiales
- Normalisation des types de droits
- Normalisation des adresses
"""

import re
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class RegimeMatrimonial(Enum):
    """Régimes matrimoniaux français normalisés."""
    COMMUNAUTE_LEGALE = "communaute_legale"
    COMMUNAUTE_UNIVERSELLE = "communaute_universelle"
    SEPARATION_BIENS = "separation_biens"
    PARTICIPATION_ACQUETS = "participation_acquets"
    COMMUNAUTE_MEUBLES_ACQUETS = "communaute_meubles_acquets"
    INCONNU = "inconnu"


class StatutMatrimonial(Enum):
    """Statuts matrimoniaux normalisés."""
    CELIBATAIRE = "celibataire"
    MARIE = "marie"
    PACSE = "pacse"
    DIVORCE = "divorce"
    VEUF = "veuf"
    SEPARE = "separe"


class TypeDroit(Enum):
    """Types de droits de propriété."""
    PLEINE_PROPRIETE = "pleine_propriete"
    NUE_PROPRIETE = "nue_propriete"
    USUFRUIT = "usufruit"
    USUFRUIT_VIAGER = "usufruit_viager"
    INDIVISION = "indivision"


# ============================================================================
# REGIMES MATRIMONIAUX - Mapping des alias
# ============================================================================

REGIMES_MATRIMONIAUX_ALIAS: Dict[str, RegimeMatrimonial] = {
    # Communauté légale (défaut depuis 1966)
    "communauté légale": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communaute legale": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communauté réduite aux acquêts": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communaute reduite aux acquets": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "régime légal": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "regime legal": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communauté d'acquêts": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communs en biens": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "époux communs en biens": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "regime_legal": RegimeMatrimonial.COMMUNAUTE_LEGALE,
    "communaute_legale": RegimeMatrimonial.COMMUNAUTE_LEGALE,

    # Communauté universelle
    "communauté universelle": RegimeMatrimonial.COMMUNAUTE_UNIVERSELLE,
    "communaute universelle": RegimeMatrimonial.COMMUNAUTE_UNIVERSELLE,
    "communaute_universelle": RegimeMatrimonial.COMMUNAUTE_UNIVERSELLE,

    # Séparation de biens
    "séparation de biens": RegimeMatrimonial.SEPARATION_BIENS,
    "separation de biens": RegimeMatrimonial.SEPARATION_BIENS,
    "séparatiste": RegimeMatrimonial.SEPARATION_BIENS,
    "separatiste": RegimeMatrimonial.SEPARATION_BIENS,
    "séparation": RegimeMatrimonial.SEPARATION_BIENS,
    "separation_biens": RegimeMatrimonial.SEPARATION_BIENS,

    # Participation aux acquêts
    "participation aux acquêts": RegimeMatrimonial.PARTICIPATION_ACQUETS,
    "participation aux acquets": RegimeMatrimonial.PARTICIPATION_ACQUETS,
    "participation_acquets": RegimeMatrimonial.PARTICIPATION_ACQUETS,

    # Communauté de meubles et acquêts (ancien régime légal avant 1966)
    "communauté de meubles et acquêts": RegimeMatrimonial.COMMUNAUTE_MEUBLES_ACQUETS,
    "communaute de meubles et acquets": RegimeMatrimonial.COMMUNAUTE_MEUBLES_ACQUETS,
    "communaute_meubles_acquets": RegimeMatrimonial.COMMUNAUTE_MEUBLES_ACQUETS,
}

# ============================================================================
# STATUTS MATRIMONIAUX - Mapping des alias
# ============================================================================

STATUTS_MATRIMONIAUX_ALIAS: Dict[str, StatutMatrimonial] = {
    # Célibataire
    "célibataire": StatutMatrimonial.CELIBATAIRE,
    "celibataire": StatutMatrimonial.CELIBATAIRE,
    "non marié": StatutMatrimonial.CELIBATAIRE,
    "non marie": StatutMatrimonial.CELIBATAIRE,
    "non mariée": StatutMatrimonial.CELIBATAIRE,
    "non mariee": StatutMatrimonial.CELIBATAIRE,

    # Marié
    "marié": StatutMatrimonial.MARIE,
    "marie": StatutMatrimonial.MARIE,
    "mariée": StatutMatrimonial.MARIE,
    "mariee": StatutMatrimonial.MARIE,
    "époux": StatutMatrimonial.MARIE,
    "epoux": StatutMatrimonial.MARIE,
    "épouse": StatutMatrimonial.MARIE,
    "epouse": StatutMatrimonial.MARIE,

    # Pacsé
    "pacsé": StatutMatrimonial.PACSE,
    "pacse": StatutMatrimonial.PACSE,
    "pacsée": StatutMatrimonial.PACSE,
    "pacsee": StatutMatrimonial.PACSE,
    "lié par un pacs": StatutMatrimonial.PACSE,
    "lie par un pacs": StatutMatrimonial.PACSE,
    "partenaire pacs": StatutMatrimonial.PACSE,

    # Divorcé
    "divorcé": StatutMatrimonial.DIVORCE,
    "divorce": StatutMatrimonial.DIVORCE,
    "divorcée": StatutMatrimonial.DIVORCE,
    "divorcee": StatutMatrimonial.DIVORCE,

    # Veuf
    "veuf": StatutMatrimonial.VEUF,
    "veuve": StatutMatrimonial.VEUF,

    # Séparé
    "séparé": StatutMatrimonial.SEPARE,
    "separe": StatutMatrimonial.SEPARE,
    "séparée": StatutMatrimonial.SEPARE,
    "separee": StatutMatrimonial.SEPARE,
    "séparé de corps": StatutMatrimonial.SEPARE,
    "separe de corps": StatutMatrimonial.SEPARE,
}

# ============================================================================
# TYPES DE DROITS - Mapping des alias
# ============================================================================

TYPES_DROITS_ALIAS: Dict[str, TypeDroit] = {
    # Pleine propriété
    "pleine propriété": TypeDroit.PLEINE_PROPRIETE,
    "pleine propriete": TypeDroit.PLEINE_PROPRIETE,
    "pleine-propriété": TypeDroit.PLEINE_PROPRIETE,
    "pp": TypeDroit.PLEINE_PROPRIETE,
    "pleine_propriete": TypeDroit.PLEINE_PROPRIETE,

    # Nue-propriété
    "nue-propriété": TypeDroit.NUE_PROPRIETE,
    "nue propriété": TypeDroit.NUE_PROPRIETE,
    "nue-propriete": TypeDroit.NUE_PROPRIETE,
    "nue propriete": TypeDroit.NUE_PROPRIETE,
    "np": TypeDroit.NUE_PROPRIETE,
    "nue_propriete": TypeDroit.NUE_PROPRIETE,

    # Usufruit
    "usufruit": TypeDroit.USUFRUIT,
    "usufruit temporaire": TypeDroit.USUFRUIT,
    "us": TypeDroit.USUFRUIT,

    # Usufruit viager
    "usufruit viager": TypeDroit.USUFRUIT_VIAGER,
    "usufruit_viager": TypeDroit.USUFRUIT_VIAGER,

    # Indivision
    "indivision": TypeDroit.INDIVISION,
    "indivis": TypeDroit.INDIVISION,
    "en indivision": TypeDroit.INDIVISION,
}


# ============================================================================
# FONCTIONS DE NORMALISATION
# ============================================================================

def normaliser_regime_matrimonial(regime: str) -> Tuple[RegimeMatrimonial, str]:
    """
    Normalise un régime matrimonial.

    Args:
        regime: Texte brut du régime matrimonial

    Returns:
        Tuple (enum normalisé, libellé humain)

    Examples:
        >>> normaliser_regime_matrimonial("communs en biens")
        (RegimeMatrimonial.COMMUNAUTE_LEGALE, "Communauté légale réduite aux acquêts")
    """
    if not regime:
        return RegimeMatrimonial.INCONNU, "Non précisé"

    regime_lower = regime.lower().strip()

    # Recherche dans le mapping
    for alias, enum_val in REGIMES_MATRIMONIAUX_ALIAS.items():
        if alias in regime_lower or regime_lower in alias:
            return enum_val, _libelle_regime(enum_val)

    return RegimeMatrimonial.INCONNU, regime


def _libelle_regime(regime: RegimeMatrimonial) -> str:
    """Retourne le libellé humain d'un régime matrimonial."""
    libelles = {
        RegimeMatrimonial.COMMUNAUTE_LEGALE: "Communauté légale réduite aux acquêts",
        RegimeMatrimonial.COMMUNAUTE_UNIVERSELLE: "Communauté universelle",
        RegimeMatrimonial.SEPARATION_BIENS: "Séparation de biens",
        RegimeMatrimonial.PARTICIPATION_ACQUETS: "Participation aux acquêts",
        RegimeMatrimonial.COMMUNAUTE_MEUBLES_ACQUETS: "Communauté de meubles et acquêts",
        RegimeMatrimonial.INCONNU: "Non précisé",
    }
    return libelles.get(regime, "Non précisé")


def normaliser_statut_matrimonial(statut: str) -> Tuple[StatutMatrimonial, str]:
    """
    Normalise un statut matrimonial.

    Args:
        statut: Texte brut du statut

    Returns:
        Tuple (enum normalisé, libellé humain)

    Examples:
        >>> normaliser_statut_matrimonial("mariée")
        (StatutMatrimonial.MARIE, "Marié(e)")
    """
    if not statut:
        return StatutMatrimonial.CELIBATAIRE, "Célibataire"

    statut_lower = statut.lower().strip()

    for alias, enum_val in STATUTS_MATRIMONIAUX_ALIAS.items():
        if alias == statut_lower or alias in statut_lower:
            return enum_val, _libelle_statut(enum_val)

    return StatutMatrimonial.CELIBATAIRE, statut


def _libelle_statut(statut: StatutMatrimonial) -> str:
    """Retourne le libellé humain d'un statut matrimonial."""
    libelles = {
        StatutMatrimonial.CELIBATAIRE: "Célibataire",
        StatutMatrimonial.MARIE: "Marié(e)",
        StatutMatrimonial.PACSE: "Pacsé(e)",
        StatutMatrimonial.DIVORCE: "Divorcé(e)",
        StatutMatrimonial.VEUF: "Veuf/Veuve",
        StatutMatrimonial.SEPARE: "Séparé(e)",
    }
    return libelles.get(statut, "Non précisé")


def normaliser_type_droit(type_droit: str) -> Tuple[TypeDroit, str]:
    """
    Normalise un type de droit de propriété.

    Args:
        type_droit: Texte brut du type de droit

    Returns:
        Tuple (enum normalisé, libellé humain)
    """
    if not type_droit:
        return TypeDroit.PLEINE_PROPRIETE, "Pleine propriété"

    type_lower = type_droit.lower().strip()

    for alias, enum_val in TYPES_DROITS_ALIAS.items():
        if alias == type_lower or alias in type_lower:
            return enum_val, _libelle_type_droit(enum_val)

    return TypeDroit.PLEINE_PROPRIETE, type_droit


def _libelle_type_droit(type_droit: TypeDroit) -> str:
    """Retourne le libellé humain d'un type de droit."""
    libelles = {
        TypeDroit.PLEINE_PROPRIETE: "Pleine propriété",
        TypeDroit.NUE_PROPRIETE: "Nue-propriété",
        TypeDroit.USUFRUIT: "Usufruit",
        TypeDroit.USUFRUIT_VIAGER: "Usufruit viager",
        TypeDroit.INDIVISION: "Indivision",
    }
    return libelles.get(type_droit, "Pleine propriété")


def normaliser_nom(nom: str) -> str:
    """
    Normalise un nom de famille (majuscules).

    Args:
        nom: Nom brut

    Returns:
        Nom en majuscules, tirets conservés

    Examples:
        >>> normaliser_nom("dupont-martin")
        "DUPONT-MARTIN"
    """
    if not nom:
        return ""

    # Conserver les tirets, mettre en majuscules
    return nom.upper().strip()


def normaliser_prenom(prenom: str) -> str:
    """
    Normalise un prénom (première lettre majuscule).

    Args:
        prenom: Prénom brut

    Returns:
        Prénom avec majuscule initiale

    Examples:
        >>> normaliser_prenom("jean-pierre")
        "Jean-Pierre"
    """
    if not prenom:
        return ""

    # Gérer les prénoms composés
    parties = prenom.split('-')
    return '-'.join(p.strip().capitalize() for p in parties)


def normaliser_adresse(adresse: Dict) -> Dict:
    """
    Normalise une adresse.

    Args:
        adresse: Dict avec rue, numero, code_postal, commune, etc.

    Returns:
        Dict normalisé
    """
    if not adresse:
        return {}

    result = {}

    # Numéro de rue
    if 'numero' in adresse:
        num = str(adresse['numero']).strip()
        # Nettoyer bis, ter, quater
        num = re.sub(r'\s*(bis|ter|quater)$', r' \1', num, flags=re.IGNORECASE)
        result['numero'] = num

    # Rue
    if 'rue' in adresse:
        rue = adresse['rue'].strip()
        # Capitalisation intelligente
        mots_minuscules = ['de', 'du', 'des', 'la', 'le', 'les', 'l\'', 'd\'', 'en']
        mots = rue.split()
        rue_norm = []
        for i, mot in enumerate(mots):
            if i == 0 or mot.lower() not in mots_minuscules:
                rue_norm.append(mot.capitalize())
            else:
                rue_norm.append(mot.lower())
        result['rue'] = ' '.join(rue_norm)

    # Code postal
    if 'code_postal' in adresse:
        cp = str(adresse['code_postal']).strip()
        # Assurer 5 chiffres
        if len(cp) < 5:
            cp = cp.zfill(5)
        result['code_postal'] = cp

    # Commune
    if 'commune' in adresse:
        result['commune'] = adresse['commune'].upper().strip()

    # Pays (défaut: France)
    result['pays'] = adresse.get('pays', 'France')

    return result


def normaliser_telephone(telephone: str) -> str:
    """
    Normalise un numéro de téléphone français.

    Args:
        telephone: Numéro brut

    Returns:
        Numéro formaté XX XX XX XX XX

    Examples:
        >>> normaliser_telephone("0612345678")
        "06 12 34 56 78"
    """
    if not telephone:
        return ""

    # Supprimer tout sauf les chiffres et le +
    clean = re.sub(r'[^\d+]', '', telephone)

    # Gérer le +33
    if clean.startswith('+33'):
        clean = '0' + clean[3:]
    elif clean.startswith('33'):
        clean = '0' + clean[2:]

    # Formater par groupes de 2
    if len(clean) == 10:
        return ' '.join([clean[i:i+2] for i in range(0, 10, 2)])

    return telephone


def normaliser_situation_matrimoniale(situation: Dict) -> Dict:
    """
    Normalise une situation matrimoniale complète.

    Args:
        situation: Dict avec statut, regime_matrimonial, conjoint, etc.

    Returns:
        Dict normalisé avec enums et libellés
    """
    if not situation:
        return {
            'statut': 'celibataire',
            'statut_libelle': 'Célibataire'
        }

    result = {}

    # Statut
    statut_raw = situation.get('statut', '')
    statut_enum, statut_libelle = normaliser_statut_matrimonial(statut_raw)
    result['statut'] = statut_enum.value
    result['statut_libelle'] = statut_libelle

    # Régime matrimonial (si marié)
    if statut_enum == StatutMatrimonial.MARIE:
        regime_raw = situation.get('regime_matrimonial', situation.get('regime', ''))
        regime_enum, regime_libelle = normaliser_regime_matrimonial(regime_raw)
        result['regime_matrimonial'] = regime_enum.value
        result['regime_libelle'] = regime_libelle

        # Contrat de mariage (si régime autre que légal)
        if regime_enum != RegimeMatrimonial.COMMUNAUTE_LEGALE:
            result['contrat_mariage'] = situation.get('contrat_mariage', {})

    # Conjoint/Partenaire
    if 'conjoint' in situation:
        conjoint = situation['conjoint']
        result['conjoint'] = {
            'nom': normaliser_nom(conjoint.get('nom', '')),
            'prenoms': normaliser_prenom(conjoint.get('prenoms', conjoint.get('prenom', ''))),
            'intervient': conjoint.get('intervient', False)
        }
    elif 'partenaire' in situation:
        partenaire = situation['partenaire']
        result['partenaire'] = {
            'nom': normaliser_nom(partenaire.get('nom', '')),
            'prenoms': normaliser_prenom(partenaire.get('prenoms', partenaire.get('prenom', '')))
        }

    # PACS
    if statut_enum == StatutMatrimonial.PACSE:
        if 'pacs' in situation:
            result['pacs'] = situation['pacs']
        elif 'date_pacs' in situation:
            result['pacs'] = {
                'date': situation['date_pacs'],
                'lieu': situation.get('lieu_pacs', '')
            }

    return result


# ============================================================================
# Tests intégrés
# ============================================================================

if __name__ == "__main__":
    print("=== Tests de normalisation ===\n")

    # Régimes matrimoniaux
    print("Régimes matrimoniaux:")
    tests_regime = ["communs en biens", "séparatiste", "communauté universelle", "régime légal"]
    for t in tests_regime:
        enum_val, libelle = normaliser_regime_matrimonial(t)
        print(f"  '{t}' → {enum_val.value} ({libelle})")

    # Statuts matrimoniaux
    print("\nStatuts matrimoniaux:")
    tests_statut = ["mariée", "divorcé", "pacsé", "veuve"]
    for t in tests_statut:
        enum_val, libelle = normaliser_statut_matrimonial(t)
        print(f"  '{t}' → {enum_val.value} ({libelle})")

    # Types de droits
    print("\nTypes de droits:")
    tests_droit = ["pleine propriété", "nue-propriété", "usufruit viager"]
    for t in tests_droit:
        enum_val, libelle = normaliser_type_droit(t)
        print(f"  '{t}' → {enum_val.value} ({libelle})")

    # Noms et prénoms
    print("\nNoms et prénoms:")
    print(f"  'dupont-martin' → {normaliser_nom('dupont-martin')}")
    print(f"  'jean-pierre' → {normaliser_prenom('jean-pierre')}")

    # Téléphones
    print("\nTéléphones:")
    tests_tel = ["0612345678", "+33612345678", "06 12 34 56 78"]
    for t in tests_tel:
        print(f"  '{t}' → {normaliser_telephone(t)}")

    # Situation matrimoniale complète
    print("\nSituation matrimoniale complète:")
    situation = {
        'statut': 'mariée',
        'regime_matrimonial': 'séparation de biens',
        'conjoint': {
            'nom': 'dupont',
            'prenoms': 'jean-pierre',
            'intervient': True
        },
        'contrat_mariage': {
            'notaire': 'Me MARTIN',
            'date': '15/06/2010'
        }
    }
    result = normaliser_situation_matrimoniale(situation)
    print(f"  Input: {situation}")
    print(f"  Output: {result}")
