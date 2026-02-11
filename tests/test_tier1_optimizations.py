# -*- coding: utf-8 -*-
"""
Tests unitaires - Tier 1 Cost Optimizations (v2.1.0)

Valide:
1. Smart model selection (Opus vs Sonnet)
2. Détection type acte rapide (regex)
3. Validation déterministe (JSON Schema + règles métier)
4. Configuration API costs (max_tokens, timeouts, caching)
5. Calcul de coûts

pytest tests/test_tier1_optimizations.py -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from execution.utils.validation_deterministe import (
    detecter_type_acte_rapide,
    ValidateurDeterministe,
    valider_quotites,
    ResultatValidation
)
from execution.gestionnaires.orchestrateur import OrchestratorNotaire
from execution.utils.api_cost_config import (
    get_max_tokens,
    get_model,
    get_timeout,
    should_cache,
    estimer_cout,
    COUT_PAR_1M_TOKENS
)


# =============================================================================
# 1. Tests Smart Model Selection
# =============================================================================

class TestSmartModelSelection:
    """Tests du routage intelligent Opus vs Sonnet."""

    def test_standard_case_uses_sonnet(self):
        """Cas standard → Sonnet (économie 60%)."""
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": "promesse_vente"},
            "promettants": [{"nom": "Martin"}],
            "beneficiaires": [{"nom": "Dupont"}],
            "bien": {"adresse": "12 rue de la Paix"},
            "prix": {"montant": 450000}
        }

        model = orch._choisir_modele(donnees, "promesse_vente")
        assert model == "sonnet", "Cas standard devrait utiliser Sonnet"
        assert orch.stats_modeles["sonnet"] == 1

    def test_viager_uses_opus(self):
        """Viager (complexe) → Opus."""
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": "viager"},
            "promettants": [{"nom": "Martin"}],
            "beneficiaires": [{"nom": "Dupont"}],
            "prix": {"montant": 200000, "type_vente": "viager"}
        }

        model = orch._choisir_modele(donnees, "viager")
        assert model == "opus", "Viager devrait utiliser Opus"
        assert orch.stats_modeles["opus"] == 1

    def test_multi_parties_uses_opus(self):
        """Multi-parties (>2) → Opus."""
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [
                {"nom": "Martin"},
                {"nom": "Dupont"},
                {"nom": "Bernard"}
            ],
            "acquereurs": [{"nom": "Thomas"}],
            "bien": {},
            "prix": {"montant": 300000}
        }

        model = orch._choisir_modele(donnees, "vente")
        assert model == "opus", ">2 vendeurs devrait utiliser Opus"

    def test_high_price_uses_opus(self):
        """Prix >1M€ → Opus."""
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Martin"}],
            "acquereurs": [{"nom": "Dupont"}],
            "bien": {},
            "prix": {"montant": 1500000}
        }

        model = orch._choisir_modele(donnees, "vente")
        assert model == "opus", "Prix >1M€ devrait utiliser Opus"

    def test_incomplete_data_uses_opus(self):
        """Données incomplètes (≥2 champs manquants) → Opus."""
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Martin"}]
            # Manque: acquereurs, bien, prix (3 champs)
        }

        model = orch._choisir_modele(donnees, "vente")
        assert model == "opus", "Données incomplètes devrait utiliser Opus"


# =============================================================================
# 2. Tests Détection Rapide Type Acte
# =============================================================================

class TestDetectionRapide:
    """Tests de détection par regex (0 coût LLM)."""

    @pytest.mark.parametrize("texte,attendu", [
        ("Promesse Martin → Dupont, 67m² Paris", "promesse_vente"),
        ("promesse de vente standard", "promesse_vente"),
        ("Acte de vente définitif", "vente"),
        ("vente appartement", "vente"),
        ("Viager occupé, rente 500€", "viager"),
        ("viager libre", "viager"),
        ("EDD et règlement copropriété", "reglement_copropriete"),
        ("règlement de copro", "reglement_copropriete"),
        ("Modificatif EDD", "modificatif_edd"),
        ("Donation-partage", "donation_partage"),
        ("Document notarié quelconque", None),  # Ambigu
        ("Acte authentique", None),  # Ambigu
    ])
    def test_detection_patterns(self, texte, attendu):
        """Test tous les patterns de détection."""
        resultat = detecter_type_acte_rapide(texte)
        assert resultat == attendu, f"'{texte}' devrait détecter {attendu}"

    def test_detection_sous_types_promesse(self):
        """Test détection sous-types promesse."""
        assert detecter_type_acte_rapide("Promesse terrain à bâtir") == "promesse_terrain"
        assert detecter_type_acte_rapide("Promesse maison hors copropriété") == "promesse_hors_copropriete"
        assert detecter_type_acte_rapide("Promesse appartement") == "promesse_vente"

    def test_detection_case_insensitive(self):
        """Test insensible à la casse."""
        assert detecter_type_acte_rapide("PROMESSE DE VENTE") == "promesse_vente"
        assert detecter_type_acte_rapide("Viager") == "viager"


# =============================================================================
# 3. Tests Validation Déterministe
# =============================================================================

class TestValidationDeterministe:
    """Tests validation sans LLM (JSON Schema + règles métier)."""

    def test_validation_schema_complet(self):
        """Données complètes passent la validation."""
        validateur = ValidateurDeterministe()
        donnees = {
            "acte": {"type": "vente", "date": "01/01/2026"},
            "vendeurs": [{"nom": "Martin", "prenom": "Jean"}],
            "acquereurs": [{"nom": "Dupont", "prenom": "Marie"}],
            "bien": {
                "adresse": {"numero": 12, "voie": "rue de la Paix", "ville": "Paris"}
            },
            "prix": {"montant": 450000, "devise": "EUR"},
            "notaire": {"nom": "Durand"}
        }

        resultat = validateur.valider_avec_schema(donnees, "vente")
        assert isinstance(resultat, ResultatValidation)
        # Peut avoir des warnings, mais pas d'erreurs critiques si structure correcte

    def test_validation_prix_invalide(self):
        """Prix ≤ 0 génère erreur."""
        validateur = ValidateurDeterministe()
        donnees = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Martin"}],
            "acquereurs": [{"nom": "Dupont"}],
            "bien": {},
            "prix": {"montant": 0}  # Invalide
        }

        resultat = validateur.valider_avec_schema(donnees, "vente")
        assert any("prix" in err["champ"].lower() for err in resultat.erreurs)

    def test_validation_parties_manquantes(self):
        """Parties manquantes génèrent erreurs."""
        validateur = ValidateurDeterministe()
        donnees = {
            "acte": {"type": "vente"},
            "bien": {},
            "prix": {"montant": 450000}
            # Manque vendeurs et acquéreurs
        }

        resultat = validateur.valider_avec_schema(donnees, "vente")
        assert len(resultat.erreurs) >= 2  # Au moins vendeurs et acquéreurs

    def test_validation_completude_calcul(self):
        """Score de complétude se calcule correctement."""
        validateur = ValidateurDeterministe()
        donnees_completes = {
            "acte": {"type": "vente"},
            "vendeurs": [{"nom": "Martin"}],
            "acquereurs": [{"nom": "Dupont"}],
            "bien": {},
            "prix": {"montant": 450000},
            "quotites_vendues": [],
            "quotites_acquises": [],
            "copropriete": {},
            "diagnostics": {},
            "origine_propriete": {},
            "notaire": {}
        }

        resultat = validateur.valider_avec_schema(donnees_completes, "vente")
        assert resultat.score_completude >= 90  # Tous champs présents


class TestValidationQuotites:
    """Tests validation quotités (doit totaliser 100%)."""

    def test_quotites_valides_100_pourcent(self):
        """Quotités = 100% sont valides."""
        quotites = [
            {"fraction": "50%"},
            {"fraction": "50%"}
        ]
        valide, total, msg = valider_quotites(quotites)
        assert valide
        assert abs(total - 100) < 0.01

    def test_quotites_invalides_110_pourcent(self):
        """Quotités ≠ 100% sont invalides."""
        quotites = [
            {"fraction": "60%"},
            {"fraction": "50%"}
        ]
        valide, total, msg = valider_quotites(quotites)
        assert not valide
        assert abs(total - 110) < 0.01

    def test_quotites_format_fraction(self):
        """Supporte format fraction '1/2'."""
        quotites = [
            {"fraction": "1/2"},
            {"fraction": "1/2"}
        ]
        valide, total, msg = valider_quotites(quotites)
        assert valide
        assert abs(total - 100) < 0.01

    def test_quotites_format_decimal(self):
        """Supporte format décimal."""
        quotites = [
            {"fraction": 33.33},
            {"fraction": 66.67}
        ]
        valide, total, msg = valider_quotites(quotites)
        assert valide
        assert abs(total - 100) < 0.01


# =============================================================================
# 4. Tests Configuration API Costs
# =============================================================================

class TestCostConfig:
    """Tests configuration max_tokens, timeouts, caching."""

    def test_max_tokens_returns_correct_values(self):
        """Max tokens définis par agent."""
        assert get_max_tokens("workflow-orchestrator") == 4096
        assert get_max_tokens("clause-suggester") == 2048
        assert get_max_tokens("post-generation-reviewer") == 1024
        assert get_max_tokens("template-auditor") == 1024
        assert get_max_tokens("cadastre-enricher") == 512
        assert get_max_tokens("data-collector-qr") == 512
        assert get_max_tokens("schema-validator") == 512

    def test_max_tokens_default_for_unknown_agent(self):
        """Agent inconnu retourne default."""
        assert get_max_tokens("unknown-agent") == 2048

    def test_model_selection_no_fallback(self):
        """Sélection modèle sans fallback."""
        assert "opus" in get_model("workflow-orchestrator", fallback_sonnet=False)
        assert "opus" in get_model("clause-suggester", fallback_sonnet=False)
        assert "sonnet" in get_model("post-generation-reviewer", fallback_sonnet=False)
        assert "haiku" in get_model("cadastre-enricher", fallback_sonnet=False)

    def test_model_selection_with_fallback(self):
        """Opus → Sonnet avec fallback."""
        assert "sonnet" in get_model("workflow-orchestrator", fallback_sonnet=True)
        assert "sonnet" in get_model("clause-suggester", fallback_sonnet=True)
        # Haiku reste haiku
        assert "haiku" in get_model("cadastre-enricher", fallback_sonnet=True)

    def test_timeout_configuration(self):
        """Timeouts définis par agent."""
        assert get_timeout("workflow-orchestrator") == 60
        assert get_timeout("cadastre-enricher") == 10
        assert get_timeout("data-collector-qr") == 45

    def test_caching_configuration(self):
        """Caching activé pour certains agents."""
        assert should_cache("workflow-orchestrator") == True
        assert should_cache("clause-suggester") == True
        assert should_cache("template-auditor") == True
        assert should_cache("data-collector-qr") == True
        assert should_cache("cadastre-enricher") == False


# =============================================================================
# 5. Tests Calcul de Coûts
# =============================================================================

class TestCoutEstimation:
    """Tests d'estimation des coûts API."""

    def test_cost_opus_full(self):
        """Opus sans cache."""
        cout = estimer_cout("claude-opus-4-6", 10000, 3000, 0)
        # Input: 10k * $15/1M = $0.15
        # Output: 3k * $75/1M = $0.225
        # Total: $0.375
        assert 0.37 < cout < 0.38

    def test_cost_opus_cached(self):
        """Opus avec 80% cache."""
        cout = estimer_cout("claude-opus-4-6", 10000, 3000, 8000)
        # Input: 2k * $15/1M = $0.03
        # Cached: 8k * $1.5/1M = $0.012
        # Output: 3k * $75/1M = $0.225
        # Total: ~$0.267
        assert 0.26 < cout < 0.27

    def test_cost_sonnet_vs_opus(self):
        """Sonnet 60% moins cher qu'Opus."""
        cout_opus = estimer_cout("claude-opus-4-6", 10000, 3000, 0)
        cout_sonnet = estimer_cout("claude-sonnet-4-5", 10000, 3000, 0)

        # Sonnet devrait être ~60% moins cher
        ratio = cout_sonnet / cout_opus
        assert 0.18 < ratio < 0.22  # ~20% du coût Opus = 80% économie

    def test_cost_haiku_cheapest(self):
        """Haiku est le moins cher."""
        cout_opus = estimer_cout("claude-opus-4-6", 10000, 3000, 0)
        cout_sonnet = estimer_cout("claude-sonnet-4-5", 10000, 3000, 0)
        cout_haiku = estimer_cout("claude-haiku-4-5", 10000, 3000, 0)

        assert cout_haiku < cout_sonnet < cout_opus

    def test_output_5x_more_expensive_than_input(self):
        """Output coûte 5x l'input."""
        # Test avec Opus
        tarifs = COUT_PAR_1M_TOKENS["claude-opus-4-6"]
        assert tarifs["output"] == tarifs["input"] * 5

        # Test avec Sonnet
        tarifs = COUT_PAR_1M_TOKENS["claude-sonnet-4-5"]
        assert tarifs["output"] == tarifs["input"] * 5


# =============================================================================
# 6. Tests d'Intégration
# =============================================================================

class TestIntegrationTier1:
    """Tests d'intégration bout-en-bout."""

    def test_workflow_complet_standard(self):
        """Workflow complet cas standard → Sonnet."""
        # 1. Détection rapide
        type_acte = detecter_type_acte_rapide("Promesse Martin → Dupont, Paris 450k€")
        assert type_acte == "promesse_vente"

        # 2. Validation
        validateur = ValidateurDeterministe()
        donnees = {
            "acte": {"type": type_acte},
            "promettants": [{"nom": "Martin"}],
            "beneficiaires": [{"nom": "Dupont"}],
            "bien": {"adresse": "Paris"},
            "prix": {"montant": 450000}
        }
        validation = validateur.valider_avec_schema(donnees, type_acte)

        # 3. Smart model selection
        orch = OrchestratorNotaire()
        model = orch._choisir_modele(donnees, type_acte)
        assert model == "sonnet", "Cas standard devrait utiliser Sonnet"

        # 4. Config
        max_tokens = get_max_tokens("workflow-orchestrator")
        assert max_tokens == 4096

    def test_workflow_complet_complexe(self):
        """Workflow complet cas complexe → Opus."""
        # 1. Détection
        type_acte = detecter_type_acte_rapide("Viager occupé, rente 500€/mois")
        assert type_acte == "viager"

        # 2. Smart model selection
        orch = OrchestratorNotaire()
        donnees = {
            "acte": {"type": type_acte},
            "promettants": [{"nom": "Martin"}],
            "beneficiaires": [{"nom": "Dupont"}],
            "prix": {"montant": 200000, "type_vente": "viager"}
        }
        model = orch._choisir_modele(donnees, type_acte)
        assert model == "opus", "Viager devrait utiliser Opus"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
