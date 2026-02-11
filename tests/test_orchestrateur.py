# -*- coding: utf-8 -*-
"""
Tests pour l'orchestrateur NotaireAI - Focus Smart Routing Modèles (v2.1.0)

Tests du Sprint Plan JOUR 1 MATIN:
- Validation → Haiku (déterministe)
- Détection haute confiance → Sonnet (rapide)
- Suggestion clauses → Opus (créativité)
- Génération complexe → Opus
- Génération standard → Sonnet
"""

import pytest
from execution.gestionnaires.orchestrateur import OrchestratorNotaire


class TestSmartRoutingModeles:
    """Tests du smart routing de modèles selon le Sprint Plan."""

    @pytest.fixture
    def orchestrateur(self):
        """Fixture: orchestrateur sans verbose."""
        return OrchestratorNotaire(verbose=False)

    def test_validation_utilise_haiku(self, orchestrateur):
        """
        RÈGLE 1: Validation → Haiku (déterministe, 80% économie).
        """
        modele = orchestrateur._choisir_modele(type_operation="validation")

        assert modele == "claude-haiku-4-5-20251001"
        assert orchestrateur.stats_modeles["haiku"] == 1
        assert orchestrateur.stats_modeles["sonnet"] == 0
        assert orchestrateur.stats_modeles["opus"] == 0

    def test_detection_haute_confiance_utilise_sonnet(self, orchestrateur):
        """
        RÈGLE 2: Détection + confiance >80% → Sonnet (60% économie).
        """
        modele = orchestrateur._choisir_modele(
            type_operation="detection",
            confiance=0.85
        )

        assert modele == "claude-sonnet-4-5-20250929"
        assert orchestrateur.stats_modeles["sonnet"] == 1

    def test_detection_faible_confiance_utilise_opus(self, orchestrateur):
        """
        RÈGLE 2 (inverse): Détection + confiance ≤80% → Opus (qualité).
        """
        modele = orchestrateur._choisir_modele(
            type_operation="detection",
            confiance=0.65
        )

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_suggestion_clauses_utilise_opus(self, orchestrateur):
        """
        RÈGLE 3: Suggestion clauses → Opus (créativité).
        """
        modele = orchestrateur._choisir_modele(type_operation="suggestion_clauses")

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_generation_cas_standard_utilise_sonnet(self, orchestrateur):
        """
        RÈGLE 4a: Génération cas standard → Sonnet (60% économie).

        Cas standard:
        - Type acte fréquent (vente, promesse)
        - 1-2 parties de chaque côté
        - Données complètes
        - Prix < 1M€
        """
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Dupont"}],
            "acquereurs": [{"nom": "Martin"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 350000}
        }

        modele = orchestrateur._choisir_modele(
            type_operation="generation",
            donnees=donnees
        )

        assert modele == "claude-sonnet-4-5-20250929"
        assert orchestrateur.stats_modeles["sonnet"] == 1

    def test_generation_type_complexe_utilise_opus(self, orchestrateur):
        """
        RÈGLE 4b: Génération type complexe (viager, donation) → Opus.
        """
        donnees = {
            "acte": {"type": "viager"},
            "promettants": [{"nom": "Dupont"}],
            "beneficiaires": [{"nom": "Martin"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 250000}
        }

        modele = orchestrateur._choisir_modele(
            type_operation="generation",
            donnees=donnees
        )

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_generation_multi_parties_utilise_opus(self, orchestrateur):
        """
        RÈGLE 4c: Génération multi-parties (>2 vendeurs OU >2 acquéreurs) → Opus.
        """
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [
                {"nom": "Dupont"},
                {"nom": "Martin"},
                {"nom": "Bernard"}  # >2 vendeurs
            ],
            "acquereurs": [{"nom": "Thomas"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 300000}
        }

        modele = orchestrateur._choisir_modele(
            type_operation="generation",
            donnees=donnees
        )

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_generation_prix_eleve_utilise_opus(self, orchestrateur):
        """
        RÈGLE 4d: Génération prix >1M€ → Opus (enjeux importants).
        """
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Dupont"}],
            "acquereurs": [{"nom": "Martin"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 1_500_000}
        }

        modele = orchestrateur._choisir_modele(
            type_operation="generation",
            donnees=donnees
        )

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_generation_donnees_incompletes_utilise_opus(self, orchestrateur):
        """
        RÈGLE 4e: Génération données incomplètes (≥2 champs critiques manquants) → Opus.
        """
        donnees = {
            "acte": {"type": "vente"},
            # Manquants: vendeurs, acquereurs, bien, prix → 4 champs
        }

        modele = orchestrateur._choisir_modele(
            type_operation="generation",
            donnees=donnees
        )

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_fallback_opus_pour_operation_inconnue(self, orchestrateur):
        """
        FALLBACK: Opération non catégorisée → Opus (sécurité).
        """
        modele = orchestrateur._choisir_modele(type_operation="operation_inconnue")

        assert modele == "claude-opus-4-6"
        assert orchestrateur.stats_modeles["opus"] == 1

    def test_stats_modeles_cumul(self, orchestrateur):
        """
        Vérifie que les stats sont bien cumulées sur plusieurs appels.
        """
        orchestrateur._choisir_modele(type_operation="validation")  # Haiku
        orchestrateur._choisir_modele(type_operation="detection", confiance=0.9)  # Sonnet
        orchestrateur._choisir_modele(type_operation="suggestion_clauses")  # Opus

        assert orchestrateur.stats_modeles["haiku"] == 1
        assert orchestrateur.stats_modeles["sonnet"] == 1
        assert orchestrateur.stats_modeles["opus"] == 1


class TestSmartRoutingEconomie:
    """Tests d'estimation d'économie des coûts API."""

    @pytest.fixture
    def orchestrateur(self):
        """Fixture: orchestrateur sans verbose."""
        return OrchestratorNotaire(verbose=False)

    def test_scenario_100_generations_mixtes(self, orchestrateur):
        """
        Scénario: 100 générations mixtes (60% standard, 35% détection, 5% complexe).

        Attendu Sprint Plan:
        - Validation (100%) → Haiku (80% économie)
        - Détection (35%) → Sonnet (60% économie)
        - Génération standard (60%) → Sonnet (60% économie)
        - Génération complexe (5%) → Opus (0% économie)

        Économie totale attendue: ~60% sur l'ensemble.
        """
        # Simuler 100 validations
        for _ in range(100):
            orchestrateur._choisir_modele(type_operation="validation")

        # Simuler 35 détections haute confiance
        for _ in range(35):
            orchestrateur._choisir_modele(type_operation="detection", confiance=0.85)

        # Simuler 60 générations standard
        donnees_std = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Dupont"}],
            "acquereurs": [{"nom": "Martin"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 350000}
        }
        for _ in range(60):
            orchestrateur._choisir_modele(type_operation="generation", donnees=donnees_std)

        # Simuler 5 générations complexes (viager)
        donnees_viager = {
            "acte": {"type": "viager"},
            "promettants": [{"nom": "Dupont"}],
            "beneficiaires": [{"nom": "Martin"}],
            "bien": {"adresse": "12 rue Test"},
            "prix": {"montant": 250000}
        }
        for _ in range(5):
            orchestrateur._choisir_modele(type_operation="generation", donnees=donnees_viager)

        # Vérifier la distribution
        assert orchestrateur.stats_modeles["haiku"] == 100  # Toutes les validations
        assert orchestrateur.stats_modeles["sonnet"] == 95  # 35 détections + 60 générations std
        assert orchestrateur.stats_modeles["opus"] == 5     # 5 générations complexes

        total = sum(orchestrateur.stats_modeles.values())
        assert total == 200  # 100 validations + 35 détections + 60 std + 5 complexes

        # Économie attendue (valeurs indicatives):
        # - Haiku: 100 appels à ~$0.001 au lieu de $0.005 (Opus) → économie $0.40
        # - Sonnet: 95 appels à ~$0.002 au lieu de $0.005 (Opus) → économie $0.285
        # - Opus: 5 appels à $0.005 → coût $0.025
        # Total économisé: ~60% vs 200 appels Opus
        ratio_haiku = orchestrateur.stats_modeles["haiku"] / total
        ratio_sonnet = orchestrateur.stats_modeles["sonnet"] / total
        ratio_opus = orchestrateur.stats_modeles["opus"] / total

        assert ratio_haiku == 0.50  # 50% Haiku
        assert ratio_sonnet == 0.475  # 47.5% Sonnet
        assert ratio_opus == 0.025  # 2.5% Opus


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
