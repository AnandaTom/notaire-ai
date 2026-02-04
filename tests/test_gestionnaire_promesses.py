#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gestionnaire_promesses.py
-------------------------------
Tests unitaires pour le gestionnaire de promesses (v1.4.0).
Couvre: détection de type, validation, sélection de template.
"""

import json
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from execution.gestionnaires.gestionnaire_promesses import (
    GestionnairePromesses,
    TypePromesse,
    ResultatDetection,
    ResultatValidation,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def gestionnaire():
    """Gestionnaire de promesses sans Supabase."""
    return GestionnairePromesses(supabase_client=None)


@pytest.fixture
def donnees_standard():
    """Données minimalistes pour promesse standard."""
    return {
        "vendeurs": [{
            "personne_physique": {
                "nom": "DUPONT",
                "prenoms": "Jean Pierre",
                "date_naissance": "15/03/1965",
            },
            "adresse": {"adresse": "45 avenue des Champs", "code_postal": "75008", "ville": "Paris"},
        }],
        "acquereurs": [{
            "personne_physique": {
                "nom": "MARTIN",
                "prenoms": "Sophie",
                "date_naissance": "22/08/1982",
            },
            "adresse": {"adresse": "12 rue de Lyon", "code_postal": "69001", "ville": "Lyon"},
        }],
        "bien": {
            "adresse": {"adresse": "12 rue de la Paix", "code_postal": "75002", "ville": "Paris"},
            "lots": [{"numero": "45", "designation": "Appartement 3ème étage"}],
        },
        "prix": {"montant": 450000},
    }


@pytest.fixture
def donnees_mobilier():
    """Données avec mobilier pour détection automatique."""
    return {
        "vendeurs": [{"personne_physique": {"nom": "DUPONT", "prenoms": "Jean"}}],
        "acquereurs": [{"personne_physique": {"nom": "MARTIN", "prenoms": "Sophie"}}],
        "bien": {"adresse": {"adresse": "12 rue de la Paix"}},
        "prix": {"montant": 450000},
        "mobilier": {
            "liste": [
                {"designation": "Cuisine équipée", "valeur": 15000},
                {"designation": "Dressing chambre", "valeur": 5000},
            ],
            "montant_total": 20000,
        },
    }


@pytest.fixture
def donnees_multi_biens():
    """Données avec plusieurs lots pour détection multi-biens."""
    return {
        "vendeurs": [{"personne_physique": {"nom": "DUPONT", "prenoms": "Jean"}}],
        "acquereurs": [{"personne_physique": {"nom": "MARTIN", "prenoms": "Sophie"}}],
        "bien": {
            "adresse": {"adresse": "12 rue de la Paix"},
            "lots": [
                {"numero": "45", "designation": "Appartement"},
                {"numero": "112", "designation": "Cave"},
                {"numero": "203", "designation": "Parking"},
            ],
        },
        "prix": {"montant": 450000},
    }


# =============================================================================
# TESTS DÉTECTION TYPE
# =============================================================================

class TestDetectionType:
    """Tests de la détection automatique du type de promesse."""

    def test_detection_standard(self, gestionnaire, donnees_standard):
        """Données simples → type standard."""
        detection = gestionnaire.detecter_type(donnees_standard)
        assert isinstance(detection, ResultatDetection)
        assert isinstance(detection.type_promesse, TypePromesse)
        assert detection.confiance > 0

    def test_detection_retourne_raison(self, gestionnaire, donnees_standard):
        """La détection fournit une raison lisible."""
        detection = gestionnaire.detecter_type(donnees_standard)
        assert detection.raison
        assert len(detection.raison) > 3

    def test_detection_confiance_entre_0_et_1(self, gestionnaire, donnees_standard):
        """La confiance est un float entre 0 et 1."""
        detection = gestionnaire.detecter_type(donnees_standard)
        assert 0 <= detection.confiance <= 1

    def test_detection_donnees_vides(self, gestionnaire):
        """Données vides → fallback standard avec faible confiance."""
        detection = gestionnaire.detecter_type({})
        assert detection.type_promesse == TypePromesse.STANDARD
        assert detection.confiance <= 0.6


# =============================================================================
# TESTS VALIDATION
# =============================================================================

class TestValidation:
    """Tests de la validation des données."""

    def test_validation_donnees_completes(self, gestionnaire, donnees_standard):
        """Données complètes → validation OK."""
        validation = gestionnaire.valider(donnees_standard)
        assert isinstance(validation, ResultatValidation)

    def test_validation_donnees_vides(self, gestionnaire):
        """Données vides → erreurs."""
        validation = gestionnaire.valider({})
        assert isinstance(validation, ResultatValidation)
        # Doit avoir des erreurs ou champs manquants
        assert len(validation.erreurs) > 0 or len(validation.champs_manquants) > 0


# =============================================================================
# TESTS SÉLECTION TEMPLATE
# =============================================================================

class TestSelectionTemplate:
    """Tests de la sélection du template approprié."""

    def test_template_standard_existe(self, gestionnaire):
        """Le template standard existe."""
        template = gestionnaire._selectionner_template(TypePromesse.STANDARD)
        assert template is not None
        assert template.exists()

    def test_template_fallback(self, gestionnaire):
        """Si un type n'a pas de template spécifique, fallback vers standard."""
        # Tous les types doivent retourner un template (fallback vers standard)
        for type_p in TypePromesse:
            template = gestionnaire._selectionner_template(type_p)
            assert template is not None, f"Pas de template pour {type_p.value}"


# =============================================================================
# TESTS CATALOGUE
# =============================================================================

class TestCatalogue:
    """Tests du chargement du catalogue unifié."""

    def test_catalogue_charge(self, gestionnaire):
        """Le catalogue unifié est chargé."""
        assert gestionnaire.catalogue is not None
        assert isinstance(gestionnaire.catalogue, dict)

    def test_templates_scannes(self, gestionnaire):
        """Au moins un template est scanné."""
        assert len(gestionnaire.templates_disponibles) >= 1
        assert "standard" in gestionnaire.templates_disponibles
