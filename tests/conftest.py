#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conftest.py
-----------
Configuration et fixtures pytest pour les tests du projet NotaireAI.
"""

import json
import sys
from pathlib import Path

import pytest

# Ajoute le répertoire execution au path
PROJECT_ROOT = Path(__file__).parent.parent
EXECUTION_DIR = PROJECT_ROOT / "execution"
sys.path.insert(0, str(EXECUTION_DIR))

# Répertoires
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
EXEMPLES_DIR = PROJECT_ROOT / "exemples"
FIXTURES_DIR = Path(__file__).parent / "fixtures"
TMP_DIR = PROJECT_ROOT / ".tmp" / "tests"


@pytest.fixture(scope="session")
def project_root():
    """Retourne le chemin racine du projet."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def schemas_dir():
    """Retourne le chemin du répertoire schemas."""
    return SCHEMAS_DIR


@pytest.fixture(scope="session")
def templates_dir():
    """Retourne le chemin du répertoire templates."""
    return TEMPLATES_DIR


@pytest.fixture(scope="session")
def tmp_dir():
    """Retourne le chemin du répertoire temporaire pour les tests."""
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    return TMP_DIR


@pytest.fixture
def donnees_vente_exemple():
    """Charge les données d'exemple pour une vente."""
    fichier = EXEMPLES_DIR / "donnees_vente_exemple.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def donnees_promesse_exemple():
    """Charge les données d'exemple pour une promesse."""
    fichier = EXEMPLES_DIR / "donnees_promesse_exemple.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def donnees_reglement_exemple():
    """Charge les données d'exemple pour un règlement de copropriété."""
    fichier = EXEMPLES_DIR / "donnees_reglement_copropriete_exemple.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def donnees_modificatif_exemple():
    """Charge les données d'exemple pour un modificatif EDD."""
    fichier = EXEMPLES_DIR / "donnees_modificatif_edd_exemple.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def schema_vente():
    """Charge le schéma de validation pour une vente."""
    fichier = SCHEMAS_DIR / "variables_vente.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def schema_reglement():
    """Charge le schéma de validation pour un règlement."""
    fichier = SCHEMAS_DIR / "variables_reglement_copropriete.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def schema_modificatif():
    """Charge le schéma de validation pour un modificatif."""
    fichier = SCHEMAS_DIR / "variables_modificatif_edd.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def clauses_catalogue():
    """Charge le catalogue de clauses."""
    fichier = SCHEMAS_DIR / "clauses_catalogue.json"
    if fichier.exists():
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def donnees_test_minimal():
    """Données minimales pour tests rapides."""
    return {
        "acte": {
            "date": "2024-03-15",
            "reference": "TEST-001",
            "type": "vente",
            "notaire": {
                "nom": "DUPONT",
                "prenom": "Jean",
                "office": "Office Test",
                "adresse": "1 rue du Test, 69000 Lyon"
            }
        },
        "vendeurs": [{
            "type": "personne_physique",
            "personne_physique": {
                "civilite": "Monsieur",
                "nom": "VENDEUR",
                "prenom": "Pierre",
                "adresse": "10 rue des Vendeurs, 69000 Lyon"
            }
        }],
        "acquereurs": [{
            "type": "personne_physique",
            "personne_physique": {
                "civilite": "Madame",
                "nom": "ACQUEREUR",
                "prenom": "Marie",
                "adresse": "20 rue des Acheteurs, 69000 Lyon"
            }
        }],
        "prix": {
            "montant": 250000
        }
    }


@pytest.fixture
def donnees_test_reglement_minimal():
    """Données minimales pour un règlement de copropriété."""
    return {
        "acte": {
            "date": "2024-03-15",
            "reference": "EDD-TEST-001",
            "type": "edd_reglement_initial",
            "notaire": {
                "nom": "MARTIN",
                "prenom": "Sophie",
                "office": "Office Test EDD",
                "adresse": "5 rue du Notariat, 69002 Lyon"
            }
        },
        "requerant": {
            "type": "personne_physique",
            "personne_physique": {
                "civilite": "Monsieur",
                "nom": "PROPRIETAIRE",
                "prenom": "Jean",
                "adresse": "1 rue de l'Immeuble, 69003 Lyon"
            }
        },
        "immeuble": {
            "adresse": {
                "numero": "15",
                "voie": "rue des Tests",
                "code_postal": "69003",
                "commune": "Lyon"
            },
            "cadastre": [{
                "section": "AB",
                "numero": "123",
                "surface": "500 m2"
            }]
        },
        "lots": [
            {"numero": 1, "designation": "Appartement", "tantiemes_generaux": 500},
            {"numero": 2, "designation": "Appartement", "tantiemes_generaux": 500}
        ],
        "parties_communes": {
            "generales": ["Sol", "Toiture", "Escalier"]
        },
        "charges": {
            "total_tantiemes": 1000
        }
    }


# Marqueurs personnalisés
def pytest_configure(config):
    """Configure les marqueurs pytest personnalisés."""
    config.addinivalue_line(
        "markers", "slow: marque un test comme lent"
    )
    config.addinivalue_line(
        "markers", "integration: marque un test d'intégration"
    )
    config.addinivalue_line(
        "markers", "docx: marque un test qui génère des fichiers DOCX"
    )
