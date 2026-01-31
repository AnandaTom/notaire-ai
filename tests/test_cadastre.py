#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests pour le service cadastre."""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from execution.services.cadastre_service import CadastreService, CacheLocal


# =============================================================================
# TESTS CONVERSION SURFACE
# =============================================================================

class TestConversionSurface:
    """Tests de conversion surface texte ↔ m²."""

    def test_ha_a_ca_standard(self):
        assert CadastreService.surface_texte_vers_m2("00 ha 05 a 30 ca") == 530

    def test_ha_a_ca_grands_nombres(self):
        assert CadastreService.surface_texte_vers_m2("01 ha 28 a 21 ca") == 12821

    def test_ha_a_ca_compact(self):
        assert CadastreService.surface_texte_vers_m2("5a 32ca") == 532

    def test_metres_carres(self):
        assert CadastreService.surface_texte_vers_m2("530 m²") == 530

    def test_hectares_decimal(self):
        assert CadastreService.surface_texte_vers_m2("0,0530 ha") == 530

    def test_vide(self):
        assert CadastreService.surface_texte_vers_m2("") is None

    def test_none(self):
        assert CadastreService.surface_texte_vers_m2(None) is None

    def test_m2_vers_texte(self):
        assert CadastreService.m2_vers_surface_texte(530) == "00 ha 05 a 30 ca"

    def test_m2_vers_texte_grand(self):
        assert CadastreService.m2_vers_surface_texte(12821) == "01 ha 28 a 21 ca"

    def test_roundtrip(self):
        texte = "00 ha 05 a 30 ca"
        m2 = CadastreService.surface_texte_vers_m2(texte)
        retour = CadastreService.m2_vers_surface_texte(m2)
        assert retour == texte


# =============================================================================
# TESTS CACHE LOCAL
# =============================================================================

class TestCacheLocal:
    """Tests du cache fichier."""

    def test_set_et_get(self, tmp_path):
        cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=1)
        cache.set("test_key", {"data": "value"})
        result = cache.get("test_key")
        assert result == {"data": "value"}

    def test_get_inexistant(self, tmp_path):
        cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=1)
        assert cache.get("inexistant") is None

    def test_ttl_expire(self, tmp_path):
        cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=0)
        cache.ttl_secondes = 0  # TTL expiré immédiatement
        cache.set("test_key", {"data": "value"})
        # Le cache devrait être expiré
        import time
        time.sleep(0.1)
        result = cache.get("test_key")
        assert result is None


# =============================================================================
# TESTS GEOCODAGE (avec mock)
# =============================================================================

class TestGeocodage:
    """Tests du geocodage avec mock API."""

    @pytest.fixture
    def service(self, tmp_path):
        svc = CadastreService(cache_ttl_heures=0)
        svc.cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=1)
        return svc

    def test_geocoder_adresse_mock(self, service):
        """Test geocoding avec réponse mockée."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "features": [{
                "properties": {
                    "citycode": "75102",
                    "postcode": "75002",
                    "city": "Paris",
                    "district": "Paris 2e",
                    "label": "12 Rue de la Paix 75002 Paris",
                    "score": 0.96,
                },
                "geometry": {"coordinates": [2.331, 48.869]},
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.session, "get", return_value=mock_response):
            result = service.geocoder_adresse("12 rue de la Paix, Paris")

        assert result is not None
        assert result["code_insee"] == "75102"
        assert result["code_postal"] == "75002"
        assert result["latitude"] == 48.869
        assert result["longitude"] == 2.331

    def test_geocoder_adresse_vide(self, service):
        """Test geocoding avec résultat vide."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"features": []}
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.session, "get", return_value=mock_response):
            result = service.geocoder_adresse("adresse inexistante xyz")

        assert result is None


# =============================================================================
# TESTS PARCELLE (avec mock)
# =============================================================================

class TestParcelle:
    """Tests recherche parcelle avec mock API."""

    @pytest.fixture
    def service(self, tmp_path):
        svc = CadastreService(cache_ttl_heures=0)
        svc.cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=1)
        return svc

    def test_chercher_parcelle_mock(self, service):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "features": [{
                "properties": {
                    "section": "AH",
                    "numero": "0068",
                    "feuille": 1,
                    "code_dep": "69",
                    "code_com": "290",
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": [[[[4.93, 45.71], [4.94, 45.71], [4.94, 45.72], [4.93, 45.72], [4.93, 45.71]]]],
                },
            }]
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.session, "get", return_value=mock_response):
            result = service.chercher_parcelle("69290", "AH", "68")

        assert result is not None
        assert result["section"] == "AH"
        assert result["numero"] == "0068"
        assert result["code_insee"] == "69290"
        assert result["surface_m2"] is not None
        assert result["surface_m2"] > 0

    def test_chercher_parcelle_non_trouvee(self, service):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"features": []}
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.session, "get", return_value=mock_response):
            result = service.chercher_parcelle("99999", "ZZ", "9999")

        assert result is None

    def test_numero_normalise(self, service):
        """Vérifie que le numéro est paddé à 4 chiffres."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"features": []}
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.session, "get", return_value=mock_response) as mock_get:
            service.chercher_parcelle("69290", "AH", "68")

        # Vérifier que le numéro est paddé
        call_args = mock_get.call_args
        assert call_args[1]["params"]["numero"] == "0068"


# =============================================================================
# TESTS ENRICHISSEMENT
# =============================================================================

class TestEnrichissement:
    """Tests enrichissement cadastre automatique."""

    @pytest.fixture
    def service(self, tmp_path):
        svc = CadastreService(cache_ttl_heures=0)
        svc.cache = CacheLocal(cache_dir=tmp_path / "cache", ttl_heures=1)
        return svc

    def test_enrichir_avec_cadastre_existant(self, service):
        """Test enrichissement quand cadastre existe déjà."""
        donnees = {
            "bien": {
                "adresse": {
                    "numero": "170",
                    "voie": "rue Joliot Curie",
                    "code_postal": "69800",
                    "ville": "Saint-Priest",
                },
                "cadastre": [{
                    "section": "AH",
                    "numero": "0068",
                    "lieudit": "RUE JOLIOT CURIE",
                    "surface": "00 ha 22 a 07 ca",
                }],
            }
        }

        # Mock geocodage
        mock_geo = MagicMock()
        mock_geo.status_code = 200
        mock_geo.json.return_value = {
            "features": [{
                "properties": {"citycode": "69290", "postcode": "69800",
                               "city": "Saint-Priest", "label": "test", "score": 0.9},
                "geometry": {"coordinates": [4.93, 45.71]},
            }]
        }
        mock_geo.raise_for_status = MagicMock()

        # Mock parcelle
        mock_parc = MagicMock()
        mock_parc.status_code = 200
        mock_parc.json.return_value = {
            "features": [{
                "properties": {"section": "AH", "numero": "0068", "feuille": 1,
                               "code_dep": "69", "code_com": "290"},
                "geometry": {"type": "Polygon", "coordinates": [
                    [[4.93, 45.71], [4.94, 45.71], [4.94, 45.72], [4.93, 45.72], [4.93, 45.71]]
                ]},
            }]
        }
        mock_parc.raise_for_status = MagicMock()

        def side_effect(url, **kwargs):
            if "api-adresse" in url:
                return mock_geo
            return mock_parc

        with patch.object(service.session, "get", side_effect=side_effect):
            result = service.enrichir_cadastre(donnees)

        rapport = result["rapport"]
        assert rapport["cadastre_enrichi"] is True
        assert rapport["code_insee"] == "69290"
        assert rapport["parcelles_validees"] == 1

        # Vérifier enrichissement des données
        parcelle = result["donnees"]["bien"]["cadastre"][0]
        assert parcelle["verifie"] is True
        assert parcelle["code_insee"] == "69290"
        assert parcelle["source"] == "api_cadastre"

    def test_enrichir_sans_bien(self, service):
        """Test enrichissement sans section bien."""
        result = service.enrichir_cadastre({})
        assert result["rapport"]["erreurs"]

    def test_formater_adresse(self, service):
        adresse = {"numero": "12", "voie": "rue de la Paix", "code_postal": "75002", "ville": "Paris"}
        result = service._formater_adresse(adresse)
        assert result == "12 rue de la Paix 75002 Paris"

    def test_formater_adresse_vide(self, service):
        assert service._formater_adresse({}) is None


# =============================================================================
# TESTS PATTERNS CADASTRE
# =============================================================================

class TestPatternsCadastre:
    """Tests des patterns regex améliorés."""

    def test_patterns_charges(self):
        """Vérifie que les patterns cadastre sont chargés."""
        from execution.extraction.patterns_avances import PatternsAvances
        patterns = PatternsAvances.PATTERNS_CADASTRE
        assert len(patterns) >= 8  # 3 originaux + 5 nouveaux

    def test_pattern_tableau(self):
        """Test pattern tableau cadastral."""
        import re
        pattern = r'\|\s*([A-Z]{1,2})\s*\|\s*(\d{1,5})\s*\|\s*([^|]+?)\s*\|\s*(\d{1,2}\s*ha\s*\d{1,2}\s*a\s*\d{1,2}\s*ca)\s*\|'
        texte = "| AB | 145 | 12 RUE DE LA PAIX | 00 ha 05 a 30 ca |"
        m = re.search(pattern, texte)
        assert m is not None
        assert m.group(1) == "AB"
        assert m.group(2) == "145"
        assert "RUE DE LA PAIX" in m.group(3)

    def test_pattern_titre(self):
        """Test pattern format titre de propriété."""
        import re
        pattern = r'section\s+([A-Z]{1,2})\s+n°?\s*(\d+)\s+pour\s+(\d{1,2}\s*ha\s*\d{1,2}\s*a\s*\d{1,2}\s*ca)'
        texte = "section AH n° 211 pour 00 ha 28 a 21 ca"
        m = re.search(pattern, texte)
        assert m is not None
        assert m.group(1) == "AH"
        assert m.group(2) == "211"
