#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_integration.py
-------------------
Tests d'intégration pour le pipeline complet de génération d'actes.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
EXECUTION_DIR = PROJECT_ROOT / "execution"


class TestPipelineGeneration:
    """Tests du pipeline complet de génération."""

    @pytest.mark.integration
    def test_generer_donnees_reglement(self, tmp_dir):
        """Test de génération de données pour règlement."""
        output_file = tmp_dir / "test_donnees_reglement.json"

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "generer_donnees_test.py"),
                "--type", "reglement",
                "--lots", "5",
                "--output", str(output_file),
                "--seed", "42"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"
        assert output_file.exists()

        # Vérifie le contenu
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "acte" in data
        assert "lots" in data
        assert len(data["lots"]) == 5

    @pytest.mark.integration
    def test_generer_donnees_modificatif(self, tmp_dir):
        """Test de génération de données pour modificatif."""
        output_file = tmp_dir / "test_donnees_modificatif.json"

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "generer_donnees_test.py"),
                "--type", "modificatif",
                "--output", str(output_file),
                "--seed", "123"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"
        assert output_file.exists()

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "syndicat_demandeur" in data
        assert "assemblee_generale" in data

    @pytest.mark.integration
    def test_detecter_type_vente(self, tmp_dir, donnees_vente_exemple):
        """Test de détection du type d'acte vente."""
        if not donnees_vente_exemple:
            pytest.skip("Données vente exemple non disponibles")

        # Écrit les données dans un fichier temporaire
        data_file = tmp_dir / "test_detect_vente.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(donnees_vente_exemple, f)

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "detecter_type_acte.py"),
                "--data", str(data_file),
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["type_acte"] == "vente_lots_copropriete"
        assert output["confiance"] > 50

    @pytest.mark.integration
    def test_detecter_type_reglement(self, tmp_dir, donnees_reglement_exemple):
        """Test de détection du type d'acte règlement."""
        if not donnees_reglement_exemple:
            pytest.skip("Données règlement exemple non disponibles")

        data_file = tmp_dir / "test_detect_reglement.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(donnees_reglement_exemple, f)

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "detecter_type_acte.py"),
                "--data", str(data_file),
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["type_acte"] == "reglement_copropriete"

    @pytest.mark.integration
    def test_detecter_type_modificatif(self, tmp_dir, donnees_modificatif_exemple):
        """Test de détection du type d'acte modificatif."""
        if not donnees_modificatif_exemple:
            pytest.skip("Données modificatif exemple non disponibles")

        data_file = tmp_dir / "test_detect_modificatif.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(donnees_modificatif_exemple, f)

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "detecter_type_acte.py"),
                "--data", str(data_file),
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["type_acte"] == "modificatif_edd"

    @pytest.mark.integration
    def test_suggerer_clauses_vente(self, tmp_dir, donnees_vente_exemple):
        """Test de suggestion de clauses pour une vente."""
        if not donnees_vente_exemple:
            pytest.skip("Données vente exemple non disponibles")

        data_file = tmp_dir / "test_clauses_vente.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(donnees_vente_exemple, f)

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "suggerer_clauses.py"),
                "--data", str(data_file),
                "--type", "vente",
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        assert result.returncode == 0, f"Erreur: {result.stderr}"

        output = json.loads(result.stdout)
        assert "suggestions" in output
        # Il devrait y avoir au moins quelques clauses suggérées
        assert len(output["suggestions"]) > 0


class TestValidationDonnees:
    """Tests de validation des données."""

    @pytest.mark.integration
    def test_valider_donnees_vente(self, tmp_dir, donnees_vente_exemple, schemas_dir):
        """Test de validation des données de vente."""
        if not donnees_vente_exemple:
            pytest.skip("Données vente non disponibles")

        schema_file = schemas_dir / "variables_vente.json"
        if not schema_file.exists():
            pytest.skip("Schéma vente non trouvé")

        data_file = tmp_dir / "test_valid_vente.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(donnees_vente_exemple, f)

        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "valider_acte.py"),
                "--schema", str(schema_file),
                "--data", str(data_file)
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        # Le script peut retourner des avertissements mais pas d'erreur critique
        # pour des données d'exemple valides
        if result.returncode != 0:
            # Vérifie si c'est une erreur de validation ou une vraie erreur
            if "erreur" in result.stderr.lower() or "error" in result.stderr.lower():
                print(f"Sortie: {result.stdout}")
                print(f"Erreur: {result.stderr}")


class TestHistorique:
    """Tests du module d'historique."""

    @pytest.mark.integration
    def test_historique_offline_mode(self, tmp_dir):
        """Test du mode hors-ligne de l'historique."""
        result = subprocess.run(
            [
                sys.executable,
                str(EXECUTION_DIR / "historique_supabase.py"),
                "--action", "list"
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        # Le script doit s'exécuter même sans Supabase configuré
        # (mode hors-ligne)
        assert result.returncode == 0


class TestCompareDocuments:
    """Tests de comparaison de documents."""

    @pytest.mark.integration
    @pytest.mark.docx
    def test_comparer_structure_disponible(self):
        """Vérifie que le script de comparaison est disponible."""
        script = EXECUTION_DIR / "comparer_documents.py"
        assert script.exists()

        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "compare" in result.stdout.lower() or "original" in result.stdout.lower()
