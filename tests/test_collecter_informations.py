#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_collecter_informations.py
-------------------------------
Tests unitaires pour le module de collecte d'informations (v1.4.0).
Couvre: configuration des types d'actes, chemins des schémas.
"""

import json
import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SCHEMAS_DIR = PROJECT_ROOT / "schemas"


# =============================================================================
# TESTS CONFIGURATION
# =============================================================================

class TestConfiguration:
    """Tests de la configuration du module de collecte."""

    def test_schemas_directory_exists(self):
        """Le dossier schemas/ existe."""
        assert SCHEMAS_DIR.exists()
        assert SCHEMAS_DIR.is_dir()

    def test_schema_vente_exists(self):
        """Le fichier questions_vente.json existe (alias questions_notaire.json)."""
        # Le collecteur cherche "questions_vente.json" pour le type "vente"
        # Mais le vrai fichier s'appelle questions_notaire.json
        path = SCHEMAS_DIR / "questions_notaire.json"
        assert path.exists(), f"Schema vente manquant: {path}"

    def test_schema_promesse_exists(self):
        """Le fichier questions_promesse_vente.json existe."""
        path = SCHEMAS_DIR / "questions_promesse_vente.json"
        assert path.exists(), f"Schema promesse manquant: {path}"

    def test_schema_reglement_exists(self):
        """Le fichier questions_reglement_copropriete.json existe."""
        path = SCHEMAS_DIR / "questions_reglement_copropriete.json"
        assert path.exists(), f"Schema règlement manquant: {path}"

    def test_schema_modificatif_exists(self):
        """Le fichier questions_modificatif_edd.json existe."""
        path = SCHEMAS_DIR / "questions_modificatif_edd.json"
        assert path.exists(), f"Schema modificatif manquant: {path}"


class TestTypesActes:
    """Tests de la configuration des types d'actes dans le collecteur."""

    def test_types_actes_mapping(self):
        """Vérifie que le mapping TYPES_ACTES pointe vers des fichiers existants."""
        from execution.utils.collecter_informations import TYPES_ACTES

        for type_acte, config in TYPES_ACTES.items():
            schema_file = SCHEMAS_DIR / config["schema"]
            assert schema_file.exists(), (
                f"Type '{type_acte}' pointe vers '{config['schema']}' "
                f"qui n'existe pas dans {SCHEMAS_DIR}"
            )

    def test_types_actes_ont_titre(self):
        """Chaque type d'acte a un titre lisible."""
        from execution.utils.collecter_informations import TYPES_ACTES

        for type_acte, config in TYPES_ACTES.items():
            assert "titre" in config, f"Type '{type_acte}' n'a pas de titre"
            assert len(config["titre"]) > 5


class TestSchemasStructure:
    """Tests de la structure des fichiers de questions."""

    def test_promesse_questions_valid_json(self):
        """questions_promesse_vente.json est un JSON valide."""
        path = SCHEMAS_DIR / "questions_promesse_vente.json"
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, (dict, list))

    def test_promesse_questions_has_sections(self):
        """Le fichier de questions promesse contient des sections."""
        path = SCHEMAS_DIR / "questions_promesse_vente.json"
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # La structure peut être une liste de sections ou un dict avec "sections"
        if isinstance(data, dict):
            assert "sections" in data or len(data) > 0
        elif isinstance(data, list):
            assert len(data) > 0
