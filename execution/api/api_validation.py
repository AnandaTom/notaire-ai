#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api_validation.py
-----------------
API de validation des données d'actes notariaux en temps réel.

Ce module fournit:
- Validation complète des données avant génération
- Validation partielle pendant la saisie
- Modèles de réponse standardisés
- Intégration FastAPI ready

Usage:
    # Depuis FastAPI endpoint
    from execution.api.api_validation import ValidationAPI

    api = ValidationAPI()
    result = await api.valider_donnees(donnees, type_acte="vente")

    # Validation partielle (temps réel)
    result = await api.valider_champ(donnees, champ="vendeurs.0.nom")
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import du validateur existant
try:
    from execution.core.valider_acte import (
        ValidateurActe,
        NiveauErreur,
        ResultatValidation,
        RapportValidation,
    )
except ImportError:
    from valider_acte import (
        ValidateurActe,
        NiveauErreur,
        ResultatValidation,
        RapportValidation,
    )


# =============================================================================
# MODÈLES DE DONNÉES API
# =============================================================================

class StatutValidation(Enum):
    """Statut global de la validation."""
    VALIDE = "valide"
    INVALIDE = "invalide"
    AVERTISSEMENTS = "avertissements"


class NiveauMessage(Enum):
    """Niveau de gravité des messages."""
    ERREUR = "erreur"
    AVERTISSEMENT = "avertissement"
    INFO = "info"
    SUCCES = "succes"


@dataclass
class MessageValidation:
    """Message de validation formaté pour le frontend."""
    niveau: NiveauMessage
    code: str
    message: str
    chemin: str = ""
    suggestion: Optional[str] = None
    champ_ui: Optional[str] = None  # Nom du champ dans l'UI

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON."""
        return {
            "niveau": self.niveau.value,
            "code": self.code,
            "message": self.message,
            "chemin": self.chemin,
            "suggestion": self.suggestion,
            "champ_ui": self.champ_ui
        }


@dataclass
class ResultatValidationAPI:
    """Résultat complet de validation pour le frontend."""
    statut: StatutValidation
    valide: bool
    messages: List[MessageValidation] = field(default_factory=list)
    erreurs_count: int = 0
    avertissements_count: int = 0
    infos_count: int = 0
    score_completude: float = 0.0
    champs_manquants: List[str] = field(default_factory=list)
    temps_validation_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON."""
        return {
            "statut": self.statut.value,
            "valide": self.valide,
            "messages": [m.to_dict() for m in self.messages],
            "erreurs_count": self.erreurs_count,
            "avertissements_count": self.avertissements_count,
            "infos_count": self.infos_count,
            "score_completude": self.score_completude,
            "champs_manquants": self.champs_manquants,
            "temps_validation_ms": self.temps_validation_ms
        }


# =============================================================================
# MAPPING CHEMINS → CHAMPS UI
# =============================================================================

MAPPING_CHAMPS_UI = {
    "vendeurs.0.nom": "Vendeur 1 - Nom",
    "vendeurs.0.prenoms": "Vendeur 1 - Prénoms",
    "vendeurs.0.date_naissance": "Vendeur 1 - Date de naissance",
    "vendeurs.0.lieu_naissance": "Vendeur 1 - Lieu de naissance",
    "vendeurs.0.adresse": "Vendeur 1 - Adresse",
    "vendeurs.0.situation_matrimoniale": "Vendeur 1 - Situation matrimoniale",
    "acquereurs.0.nom": "Acquéreur 1 - Nom",
    "acquereurs.0.prenoms": "Acquéreur 1 - Prénoms",
    "acquereurs.0.date_naissance": "Acquéreur 1 - Date de naissance",
    "acquereurs.0.lieu_naissance": "Acquéreur 1 - Lieu de naissance",
    "acquereurs.0.adresse": "Acquéreur 1 - Adresse",
    "bien.adresse": "Bien - Adresse",
    "bien.cadastre": "Bien - Références cadastrales",
    "bien.lots": "Bien - Lots de copropriété",
    "prix.montant": "Prix de vente",
    "paiement.prets": "Financement - Prêts",
    "diagnostics.dpe": "Diagnostics - DPE",
    "copropriete.syndic": "Copropriété - Syndic",
    "quotites_vendues": "Quotités vendues",
    "quotites_acquises": "Quotités acquises",
}


def get_champ_ui(chemin: str) -> str:
    """Convertit un chemin technique en nom de champ lisible."""
    # Chercher correspondance exacte
    if chemin in MAPPING_CHAMPS_UI:
        return MAPPING_CHAMPS_UI[chemin]

    # Chercher correspondance partielle (pour indices dynamiques)
    for pattern, label in MAPPING_CHAMPS_UI.items():
        # Remplacer les indices dans le pattern
        base_pattern = pattern.replace(".0.", ".\\d+.")
        import re
        if re.match(base_pattern.replace("\\d+", r"\d+"), chemin):
            # Extraire l'indice
            match = re.search(r'\.(\d+)\.', chemin)
            if match:
                indice = int(match.group(1)) + 1
                return label.replace("1", str(indice))

    # Fallback: formater le chemin technique
    return chemin.replace(".", " > ").replace("_", " ").title()


# =============================================================================
# CLASSE PRINCIPALE API
# =============================================================================

class ValidationAPI:
    """API de validation pour intégration frontend."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialise l'API de validation.

        Args:
            schema_path: Chemin vers le schéma JSON (optionnel)
        """
        self.schema = {}
        if schema_path and schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)

    async def valider_donnees(
        self,
        donnees: Dict[str, Any],
        type_acte: str = "vente",
        mode_strict: bool = False
    ) -> ResultatValidationAPI:
        """
        Valide un ensemble complet de données.

        Args:
            donnees: Données à valider
            type_acte: Type d'acte (vente, promesse, reglement, modificatif)
            mode_strict: Si True, toutes les erreurs sont bloquantes

        Returns:
            ResultatValidationAPI avec statut et messages détaillés
        """
        import time
        start_time = time.time()

        # Créer le validateur
        validateur = ValidateurActe(self.schema)

        # Exécuter la validation complète
        rapport = validateur.valider_complet(donnees, strict=mode_strict)

        # Convertir le rapport en format API
        messages = []

        # Convertir les erreurs
        for erreur in rapport.erreurs:
            messages.append(MessageValidation(
                niveau=NiveauMessage.ERREUR,
                code=erreur.code,
                message=erreur.message,
                chemin=erreur.chemin,
                suggestion=erreur.suggestion,
                champ_ui=get_champ_ui(erreur.chemin)
            ))

        # Convertir les avertissements
        for warn in rapport.avertissements:
            messages.append(MessageValidation(
                niveau=NiveauMessage.AVERTISSEMENT,
                code=warn.code,
                message=warn.message,
                chemin=warn.chemin,
                suggestion=warn.suggestion,
                champ_ui=get_champ_ui(warn.chemin)
            ))

        # Convertir les infos
        for info in rapport.infos:
            messages.append(MessageValidation(
                niveau=NiveauMessage.INFO,
                code=info.code,
                message=info.message,
                chemin=info.chemin,
                suggestion=info.suggestion,
                champ_ui=get_champ_ui(info.chemin)
            ))

        # Calculer le score de complétude
        score = self._calculer_completude(donnees, type_acte)

        # Identifier les champs manquants
        champs_manquants = self._identifier_champs_manquants(donnees, type_acte)

        # Déterminer le statut global
        if len(rapport.erreurs) > 0:
            statut = StatutValidation.INVALIDE
        elif len(rapport.avertissements) > 0:
            statut = StatutValidation.AVERTISSEMENTS
        else:
            statut = StatutValidation.VALIDE

        # Calculer le temps
        temps_ms = int((time.time() - start_time) * 1000)

        return ResultatValidationAPI(
            statut=statut,
            valide=rapport.valide,
            messages=messages,
            erreurs_count=len(rapport.erreurs),
            avertissements_count=len(rapport.avertissements),
            infos_count=len(rapport.infos),
            score_completude=score,
            champs_manquants=champs_manquants,
            temps_validation_ms=temps_ms
        )

    async def valider_champ(
        self,
        donnees: Dict[str, Any],
        chemin: str
    ) -> List[MessageValidation]:
        """
        Valide un champ spécifique (pour validation temps réel).

        Args:
            donnees: Données complètes
            chemin: Chemin du champ à valider (ex: "vendeurs.0.nom")

        Returns:
            Liste des messages de validation pour ce champ
        """
        # Valider tout puis filtrer
        resultat = await self.valider_donnees(donnees)

        # Filtrer les messages pour ce champ
        messages_champ = [
            m for m in resultat.messages
            if m.chemin.startswith(chemin) or chemin.startswith(m.chemin)
        ]

        return messages_champ

    def _calculer_completude(
        self,
        donnees: Dict[str, Any],
        type_acte: str
    ) -> float:
        """Calcule le score de complétude des données (0-100%)."""
        # Champs obligatoires par type d'acte
        champs_requis = {
            "vente": [
                "acte.date", "acte.notaire.nom", "acte.notaire.prenom",
                "vendeurs", "acquereurs", "bien.adresse", "bien.lots",
                "prix.montant"
            ],
            "promesse": [
                "acte.date", "acte.notaire.nom",
                "promettants", "beneficiaires", "bien.adresse",
                "prix.montant", "delai_realisation"
            ],
        }

        champs = champs_requis.get(type_acte, champs_requis["vente"])
        presents = 0

        for champ in champs:
            if self._champ_present(donnees, champ):
                presents += 1

        return round((presents / len(champs)) * 100, 1)

    def _champ_present(self, donnees: Dict, chemin: str) -> bool:
        """Vérifie si un champ est présent et non vide."""
        parties = chemin.split('.')
        valeur = donnees

        for partie in parties:
            if isinstance(valeur, dict) and partie in valeur:
                valeur = valeur[partie]
            elif isinstance(valeur, list) and partie.isdigit():
                idx = int(partie)
                if idx < len(valeur):
                    valeur = valeur[idx]
                else:
                    return False
            else:
                return False

        # Vérifier que la valeur n'est pas vide
        if valeur is None:
            return False
        if isinstance(valeur, str) and not valeur.strip():
            return False
        if isinstance(valeur, list) and len(valeur) == 0:
            return False

        return True

    def _identifier_champs_manquants(
        self,
        donnees: Dict[str, Any],
        type_acte: str
    ) -> List[str]:
        """Identifie les champs obligatoires manquants."""
        champs_requis = {
            "vente": [
                "acte.date", "acte.notaire.nom", "acte.notaire.prenom",
                "acte.notaire.ville", "acte.notaire.adresse",
                "vendeurs", "acquereurs",
                "bien.adresse.numero", "bien.adresse.voie",
                "bien.adresse.code_postal", "bien.adresse.ville",
                "bien.lots", "prix.montant"
            ],
            "promesse": [
                "acte.date", "acte.notaire.nom",
                "promettants", "beneficiaires",
                "bien.adresse", "prix.montant", "delai_realisation"
            ],
        }

        champs = champs_requis.get(type_acte, champs_requis["vente"])
        manquants = []

        for champ in champs:
            if not self._champ_present(donnees, champ):
                manquants.append(get_champ_ui(champ))

        return manquants


# =============================================================================
# FASTAPI ROUTER (si FastAPI disponible)
# =============================================================================

try:
    from fastapi import APIRouter, HTTPException, Body
    from pydantic import BaseModel
    from typing import Optional

    router = APIRouter(prefix="/validation", tags=["Validation"])

    class DonneesValidation(BaseModel):
        """Modèle de requête pour validation."""
        donnees: Dict[str, Any]
        type_acte: str = "vente"
        mode_strict: bool = False

    class ChampValidation(BaseModel):
        """Modèle pour validation d'un champ."""
        donnees: Dict[str, Any]
        chemin: str

    @router.post("/donnees")
    async def valider_donnees_endpoint(request: DonneesValidation):
        """
        Valide un ensemble complet de données d'acte.

        - **donnees**: Les données à valider
        - **type_acte**: Type d'acte (vente, promesse)
        - **mode_strict**: Si True, toutes les erreurs sont bloquantes
        """
        api = ValidationAPI()
        result = await api.valider_donnees(
            request.donnees,
            request.type_acte,
            request.mode_strict
        )
        return result.to_dict()

    @router.post("/champ")
    async def valider_champ_endpoint(request: ChampValidation):
        """
        Valide un champ spécifique (pour validation temps réel).

        - **donnees**: Les données complètes
        - **chemin**: Chemin du champ (ex: "vendeurs.0.nom")
        """
        api = ValidationAPI()
        messages = await api.valider_champ(request.donnees, request.chemin)
        return {"messages": [m.to_dict() for m in messages]}

    @router.get("/schema/{type_acte}")
    async def get_schema(type_acte: str):
        """Récupère le schéma JSON pour un type d'acte."""
        schemas_path = Path(__file__).parent.parent / "schemas"
        schema_files = {
            "vente": "variables_vente.json",
            "promesse": "variables_promesse_vente.json",
            "reglement": "variables_reglement_copropriete.json",
            "modificatif": "variables_modificatif_edd.json"
        }

        if type_acte not in schema_files:
            raise HTTPException(
                status_code=404,
                detail=f"Type d'acte inconnu: {type_acte}"
            )

        schema_file = schemas_path / schema_files[type_acte]
        if not schema_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Schéma non trouvé: {schema_files[type_acte]}"
            )

        with open(schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)

except ImportError:
    # FastAPI non disponible
    router = None


# =============================================================================
# CLI POUR TESTS
# =============================================================================

def main():
    """Point d'entrée CLI pour tester la validation."""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="API de validation NotaireAI")
    parser.add_argument(
        '--donnees', '-d',
        type=Path,
        required=True,
        help="Fichier JSON des données à valider"
    )
    parser.add_argument(
        '--type', '-t',
        default="vente",
        help="Type d'acte (vente, promesse)"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Mode strict"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Sortie JSON"
    )

    args = parser.parse_args()

    if not args.donnees.exists():
        print(f"Erreur: Fichier non trouvé: {args.donnees}")
        return 1

    with open(args.donnees, 'r', encoding='utf-8') as f:
        donnees = json.load(f)

    # Exécuter la validation
    api = ValidationAPI()
    result = asyncio.run(api.valider_donnees(donnees, args.type, args.strict))

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print(f"VALIDATION - {args.type.upper()}")
        print("=" * 60)
        print(f"\nStatut: {result.statut.value.upper()}")
        print(f"Valide: {'OUI' if result.valide else 'NON'}")
        print(f"Complétude: {result.score_completude}%")
        print(f"Temps: {result.temps_validation_ms}ms")

        if result.erreurs_count > 0:
            print(f"\n[ERREURS] ({result.erreurs_count}):")
            for msg in result.messages:
                if msg.niveau == NiveauMessage.ERREUR:
                    print(f"  - {msg.champ_ui}: {msg.message}")
                    if msg.suggestion:
                        print(f"    → {msg.suggestion}")

        if result.avertissements_count > 0:
            print(f"\n[AVERTISSEMENTS] ({result.avertissements_count}):")
            for msg in result.messages:
                if msg.niveau == NiveauMessage.AVERTISSEMENT:
                    print(f"  - {msg.champ_ui}: {msg.message}")

        if result.champs_manquants:
            print(f"\n[CHAMPS MANQUANTS] ({len(result.champs_manquants)}):")
            for champ in result.champs_manquants:
                print(f"  - {champ}")

        print("\n" + "=" * 60)

    return 0 if result.valide else 1


if __name__ == '__main__':
    exit(main())
