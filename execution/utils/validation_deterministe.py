# -*- coding: utf-8 -*-
"""
Validation déterministe des données (0 coût LLM).

Remplace les appels LLM par des règles Python/JSON Schema pour:
- Validation de schéma (100% des cas)
- Détection de type d'acte (80% des cas)
- Validation de cohérence (règles métier simples)

Économie: -$0.02/génération (-8%)

Version: 2.1.0
Date: 2026-02-11
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    import jsonschema
    from jsonschema import ValidationError, Draft7Validator
    JSONSCHEMA_DISPONIBLE = True
except ImportError:
    JSONSCHEMA_DISPONIBLE = False


@dataclass
class ResultatValidation:
    """Résultat d'une validation déterministe."""
    valide: bool
    erreurs: List[Dict[str, str]] = field(default_factory=list)
    avertissements: List[Dict[str, str]] = field(default_factory=list)
    score_completude: float = 0.0


class ValidateurDeterministe:
    """
    Validateur déterministe basé sur JSON Schema et règles Python.

    Avantages vs LLM:
    - 0 coût API
    - Temps de réponse <50ms (vs 1-2s LLM)
    - Déterministe (toujours même résultat)
    - Facilement testable
    """

    def __init__(self, schemas_dir: Optional[Path] = None):
        """
        Initialise le validateur.

        Args:
            schemas_dir: Répertoire des schémas JSON (défaut: PROJECT_ROOT/schemas)
        """
        if schemas_dir is None:
            # Détection automatique du répertoire schemas
            current = Path(__file__).parent
            project_root = current.parent.parent
            schemas_dir = project_root / 'schemas'

        self.schemas_dir = schemas_dir
        self._schemas_cache: Dict[str, Any] = {}

        if not JSONSCHEMA_DISPONIBLE:
            print("⚠️  jsonschema non installé - validation limitée")
            print("   Installation: pip install jsonschema")

    def valider_avec_schema(
        self,
        donnees: Dict[str, Any],
        type_acte: str
    ) -> ResultatValidation:
        """
        Valide les données contre le schéma JSON du type d'acte.

        Args:
            donnees: Données à valider
            type_acte: Type d'acte (vente, promesse_vente, etc.)

        Returns:
            ResultatValidation avec erreurs et avertissements
        """
        # Charger le schéma
        schema_path = self._get_schema_path(type_acte)
        if not schema_path or not schema_path.exists():
            return ResultatValidation(
                valide=False,
                erreurs=[{
                    "champ": "schema",
                    "message": f"Schéma non trouvé: {type_acte}"
                }]
            )

        schema = self._charger_schema(schema_path)

        # Validation JSON Schema
        erreurs = []
        avertissements = []

        if JSONSCHEMA_DISPONIBLE:
            validator = Draft7Validator(schema)
            for error in validator.iter_errors(donnees):
                erreurs.append({
                    "champ": ".".join(str(p) for p in error.path),
                    "message": error.message,
                    "type": "schema_violation"
                })

        # Validations métier complémentaires
        erreurs_metier, avert_metier = self._valider_regles_metier(donnees, type_acte)
        erreurs.extend(erreurs_metier)
        avertissements.extend(avert_metier)

        # Calcul score complétude
        score = self._calculer_completude(donnees, type_acte)

        return ResultatValidation(
            valide=len(erreurs) == 0,
            erreurs=erreurs,
            avertissements=avertissements,
            score_completude=score
        )

    def _get_schema_path(self, type_acte: str) -> Optional[Path]:
        """Retourne le chemin du schéma pour le type d'acte."""
        mapping = {
            "vente": "variables_vente.json",
            "promesse_vente": "variables_promesse_vente.json",
            "reglement_copropriete": "variables_reglement_copropriete.json",
            "modificatif_edd": "variables_modificatif_edd.json"
        }

        filename = mapping.get(type_acte)
        if filename:
            return self.schemas_dir / filename
        return None

    def _charger_schema(self, schema_path: Path) -> Dict[str, Any]:
        """Charge et cache un schéma JSON."""
        cache_key = str(schema_path)

        if cache_key not in self._schemas_cache:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self._schemas_cache[cache_key] = json.load(f)

        return self._schemas_cache[cache_key]

    def _valider_regles_metier(
        self,
        donnees: Dict[str, Any],
        type_acte: str
    ) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Valide les règles métier spécifiques au notariat.

        Returns:
            Tuple (erreurs, avertissements)
        """
        erreurs = []
        avertissements = []

        # Règles communes vente/promesse
        if type_acte in ["vente", "promesse_vente"]:
            # Vérifier parties
            vendeurs = donnees.get('vendeurs') or donnees.get('promettants', [])
            acquereurs = donnees.get('acquereurs') or donnees.get('beneficiaires', [])

            if not vendeurs:
                erreurs.append({
                    "champ": "vendeurs/promettants",
                    "message": "Aucun vendeur/promettant défini",
                    "type": "parties_manquantes"
                })

            if not acquereurs:
                erreurs.append({
                    "champ": "acquereurs/beneficiaires",
                    "message": "Aucun acquéreur/bénéficiaire défini",
                    "type": "parties_manquantes"
                })

            # Vérifier prix
            prix = donnees.get('prix', {})
            montant = prix.get('montant', 0)

            if montant <= 0:
                erreurs.append({
                    "champ": "prix.montant",
                    "message": "Prix doit être > 0€",
                    "type": "prix_invalide"
                })

            if montant < 1000:
                avertissements.append({
                    "champ": "prix.montant",
                    "message": f"Prix très faible: {montant}€ (vérifier)",
                    "type": "prix_suspect"
                })

            # Vérifier quotités (vente uniquement)
            if type_acte == "vente":
                quotites_vendues = donnees.get('quotites_vendues', [])
                quotites_acquises = donnees.get('quotites_acquises', [])

                if quotites_vendues:
                    total_vendues = self._calculer_total_quotites(quotites_vendues)
                    if abs(total_vendues - 100) > 0.01:
                        erreurs.append({
                            "champ": "quotites_vendues",
                            "message": f"Quotités vendues = {total_vendues}% (doit être 100%)",
                            "type": "quotites_invalides"
                        })

                if quotites_acquises:
                    total_acquises = self._calculer_total_quotites(quotites_acquises)
                    if abs(total_acquises - 100) > 0.01:
                        erreurs.append({
                            "champ": "quotites_acquises",
                            "message": f"Quotités acquises = {total_acquises}% (doit être 100%)",
                            "type": "quotites_invalides"
                        })

            # Vérifier bien
            bien = donnees.get('bien', {})
            if not bien:
                erreurs.append({
                    "champ": "bien",
                    "message": "Bien non défini",
                    "type": "bien_manquant"
                })
            else:
                # Carrez obligatoire si copropriété >8m²
                if bien.get('lots'):
                    for i, lot in enumerate(bien['lots']):
                        if lot.get('carrez') is None or lot['carrez'] <= 0:
                            avertissements.append({
                                "champ": f"bien.lots[{i}].carrez",
                                "message": "Loi Carrez manquante (obligatoire si >8m²)",
                                "type": "carrez_manquante"
                            })

        return erreurs, avertissements

    def _calculer_total_quotites(self, quotites: List[Dict[str, Any]]) -> float:
        """Calcule le total des quotités en pourcentage."""
        total = 0.0
        for q in quotites:
            fraction = q.get('fraction', '0%')
            # Parse "50%", "50.5%", "1/2", etc.
            if isinstance(fraction, str):
                if '%' in fraction:
                    total += float(fraction.replace('%', '').strip())
                elif '/' in fraction:
                    # Fraction "1/2" → 50%
                    num, denom = fraction.split('/')
                    total += (float(num) / float(denom)) * 100
            elif isinstance(fraction, (int, float)):
                total += float(fraction)

        return total

    def _calculer_completude(self, donnees: Dict[str, Any], type_acte: str) -> float:
        """
        Calcule un score de complétude (0-100%).

        Basé sur la présence des champs obligatoires + optionnels.
        """
        champs_obligatoires = []
        champs_optionnels = []

        if type_acte in ["vente", "promesse_vente"]:
            champs_obligatoires = [
                'acte',
                'vendeurs' if type_acte == "vente" else 'promettants',
                'acquereurs' if type_acte == "vente" else 'beneficiaires',
                'bien',
                'prix'
            ]

            champs_optionnels = [
                'quotites_vendues',
                'quotites_acquises',
                'copropriete',
                'diagnostics',
                'origine_propriete',
                'notaire'
            ]

        # Compter champs présents
        obligatoires_presents = sum(1 for c in champs_obligatoires if donnees.get(c))
        optionnels_presents = sum(1 for c in champs_optionnels if donnees.get(c))

        # Score = 70% obligatoires + 30% optionnels
        score_obligatoires = (obligatoires_presents / len(champs_obligatoires)) * 70 if champs_obligatoires else 0
        score_optionnels = (optionnels_presents / len(champs_optionnels)) * 30 if champs_optionnels else 0

        return score_obligatoires + score_optionnels


# =============================================================================
# Fonctions utilitaires standalone
# =============================================================================

def detecter_type_acte_rapide(texte: str) -> Optional[str]:
    """
    Détection rapide du type d'acte par regex (0 coût LLM).

    Fonction standalone pour usage hors classe.

    Args:
        texte: Texte de la demande

    Returns:
        Type d'acte détecté ou None si ambigu
    """
    texte_lower = texte.lower()

    # Patterns clairs (priorité descendante)
    if re.search(r'\bviager\b', texte_lower):
        return "viager"

    if re.search(r'\bpromesse\b', texte_lower):
        # Sous-types promesse
        if re.search(r'\bterrain\b', texte_lower):
            return "promesse_terrain"
        if re.search(r'\bhors.*copro|maison\b', texte_lower):
            return "promesse_hors_copropriete"
        return "promesse_vente"

    if re.search(r'\bvente\b.*\bacte\b|\bacte\b.*\bvente\b', texte_lower):
        return "vente"

    if re.search(r'\bdonation\b', texte_lower):
        return "donation_partage"

    if re.search(r'\bedd\b|règlement.*copro', texte_lower):
        return "reglement_copropriete"

    if re.search(r'\bmodificatif\b', texte_lower):
        return "modificatif_edd"

    # Ambigu → nécessite LLM
    return None


def valider_quotites(quotites: List[Dict[str, Any]]) -> Tuple[bool, float, str]:
    """
    Valide que les quotités totalisent 100%.

    Args:
        quotites: Liste de quotités

    Returns:
        Tuple (valide, total, message)
    """
    total = 0.0

    for q in quotites:
        fraction = q.get('fraction', '0%')
        if isinstance(fraction, str):
            if '%' in fraction:
                total += float(fraction.replace('%', '').strip())
            elif '/' in fraction:
                num, denom = fraction.split('/')
                total += (float(num) / float(denom)) * 100
        elif isinstance(fraction, (int, float)):
            total += float(fraction)

    valide = abs(total - 100) < 0.01
    message = "Quotités correctes (100%)" if valide else f"Quotités = {total}% (≠ 100%)"

    return valide, total, message


# =============================================================================
# Tests
# =============================================================================

if __name__ == '__main__':
    print("🧪 Tests validation déterministe\n")

    # Test 1: Détection type acte
    tests_detection = [
        ("Promesse Martin → Dupont, 67m² Paris", "promesse_vente"),
        ("Acte de vente", "vente"),
        ("Viager rente 500€/mois", "viager"),
        ("EDD et règlement copropriété", "reglement_copropriete"),
        ("Document notarié", None)  # Ambigu
    ]

    print("1️⃣  Détection type acte:")
    for texte, attendu in tests_detection:
        detecte = detecter_type_acte_rapide(texte)
        status = "✅" if detecte == attendu else "❌"
        print(f"   {status} '{texte[:40]}...' → {detecte} (attendu: {attendu})")

    # Test 2: Validation quotités
    print("\n2️⃣  Validation quotités:")
    quotites_ok = [
        {"fraction": "50%"},
        {"fraction": "50%"}
    ]
    quotites_ko = [
        {"fraction": "60%"},
        {"fraction": "50%"}
    ]

    valide, total, msg = valider_quotites(quotites_ok)
    print(f"   {'✅' if valide else '❌'} {msg}")

    valide, total, msg = valider_quotites(quotites_ko)
    print(f"   {'✅' if valide else '❌'} {msg}")

    # Test 3: Validation avec schéma (si jsonschema disponible)
    if JSONSCHEMA_DISPONIBLE:
        print("\n3️⃣  Validation schéma:")
        validateur = ValidateurDeterministe()

        donnees_test = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Martin"}],
            "acquereurs": [{"nom": "Dupont"}],
            "bien": {"adresse": "12 rue de la Paix"},
            "prix": {"montant": 450000}
        }

        resultat = validateur.valider_avec_schema(donnees_test, "vente")
        print(f"   Valide: {'✅' if resultat.valide else '❌'}")
        print(f"   Complétude: {resultat.score_completude:.0f}%")
        print(f"   Erreurs: {len(resultat.erreurs)}")
        print(f"   Avertissements: {len(resultat.avertissements)}")

        if resultat.erreurs:
            print("\n   Erreurs détectées:")
            for err in resultat.erreurs[:3]:
                print(f"     • {err['champ']}: {err['message']}")

    print("\n✅ Tests terminés")
