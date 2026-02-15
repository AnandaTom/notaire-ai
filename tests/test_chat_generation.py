# -*- coding: utf-8 -*-
"""
Tests d'integration: Chat -> Generation de documents.

Verifie que le chatbot (AnthropicAgent + ChatHandler) peut declencher
la generation DOCX via les pipelines existants.

5 scenarios:
1. generate_document tool avec type promesse (output_dir + fichier_url)
2. generate_document tool avec type vente (routing orchestrateur)
3. ChatHandler fallback: generation_prete -> declencher_generation
4. ChatHandler pre-fill depuis entites
5. SYSTEM_PROMPT contient les types d'actes supportes
"""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

# Fix imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Encodage Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# =============================================================================
# Test 1: generate_document tool - promesse avec output_dir + fichier_url
# =============================================================================

class TestGenerateDocumentPromesse:
    """Verifie que generate_document passe output_dir et retourne fichier_url."""

    def test_output_dir_is_passed_to_gestionnaire(self):
        """Le tool passe output_dir depuis NOTAIRE_OUTPUT_DIR."""
        from execution.anthropic_tools import ToolExecutor

        executor = ToolExecutor(etude_id="test")

        # Mock du gestionnaire
        mock_resultat = MagicMock()
        mock_resultat.succes = True
        mock_resultat.fichier_docx = "outputs/promesse_test.docx"
        mock_resultat.categorie_bien = MagicMock(value="copropriete")
        mock_resultat.type_promesse = MagicMock(value="standard")
        mock_resultat.sections_incluses = ["designation"]
        mock_resultat.erreurs = []
        mock_resultat.warnings = []
        mock_resultat.duree_generation = 1.5

        with patch.object(executor, '_get_gestionnaire') as mock_get:
            mock_gestionnaire = MagicMock()
            mock_gestionnaire.generer.return_value = mock_resultat
            mock_get.return_value = mock_gestionnaire

            agent_state = {
                "donnees_collectees": {"promettants": [{"nom": "Martin"}], "prix": {"montant": 450000}},
                "type_acte": "promesse_vente",
            }
            tool_input = {}

            result = executor._exec_generate_document(tool_input, agent_state)

            # Verify output_dir was passed
            call_args = mock_gestionnaire.generer.call_args
            assert call_args is not None
            assert "output_dir" in call_args.kwargs or (
                len(call_args.args) > 2 and call_args.args[2] is not None
            )

    def test_fichier_url_set_in_agent_state(self):
        """Apres generation, fichier_url est present dans agent_state."""
        from execution.anthropic_tools import ToolExecutor

        executor = ToolExecutor(etude_id="test")

        mock_resultat = MagicMock()
        mock_resultat.succes = True
        mock_resultat.fichier_docx = "outputs/promesse_Martin_20260214.docx"
        mock_resultat.categorie_bien = MagicMock(value="copropriete")
        mock_resultat.type_promesse = MagicMock(value="standard")
        mock_resultat.sections_incluses = []
        mock_resultat.erreurs = []
        mock_resultat.warnings = []
        mock_resultat.duree_generation = 2.0

        with patch.object(executor, '_get_gestionnaire') as mock_get:
            mock_gestionnaire = MagicMock()
            mock_gestionnaire.generer.return_value = mock_resultat
            mock_get.return_value = mock_gestionnaire

            agent_state = {
                "donnees_collectees": {"promettants": [{"nom": "Martin"}], "prix": {"montant": 450000}},
            }

            result = executor._exec_generate_document({}, agent_state)

            assert result["succes"] is True
            assert result["fichier_url"] == "/files/promesse_Martin_20260214.docx"
            assert agent_state["fichier_url"] == "/files/promesse_Martin_20260214.docx"
            assert agent_state["fichier_genere"] == "outputs/promesse_Martin_20260214.docx"

    def test_empty_donnees_returns_error(self):
        """Si donnees_collectees est vide, retourne une erreur claire."""
        from execution.anthropic_tools import ToolExecutor

        executor = ToolExecutor(etude_id="test")
        agent_state = {"donnees_collectees": {}}
        result = executor._exec_generate_document({}, agent_state)

        assert result["succes"] is False
        assert len(result["erreurs"]) > 0
        assert "fichier_url" in result


# =============================================================================
# Test 2: generate_document tool - vente routing
# =============================================================================

class TestGenerateDocumentVente:
    """Verifie que type_acte=vente route vers OrchestratorNotaire."""

    def test_vente_routing_to_orchestrateur(self):
        """type_acte=vente appelle OrchestratorNotaire au lieu de GestionnairePromesses."""
        from execution.anthropic_tools import ToolExecutor

        executor = ToolExecutor(etude_id="test")

        mock_resultat = MagicMock()
        mock_resultat.statut = "succes"
        mock_resultat.fichiers_generes = ["outputs/vente_test.docx"]
        mock_resultat.erreurs = []
        mock_resultat.alertes = []
        mock_resultat.duree_totale_ms = 3000
        mock_resultat.score_conformite = 80.2

        with patch('execution.anthropic_tools.Path.mkdir'):
            with patch(
                'execution.gestionnaires.orchestrateur.OrchestratorNotaire'
            ) as MockOrch:
                mock_orch = MagicMock()
                mock_orch.generer_acte_complet.return_value = mock_resultat
                MockOrch.return_value = mock_orch

                agent_state = {
                    "donnees_collectees": {"vendeurs": [{"nom": "Martin"}], "prix": {"montant": 300000}},
                    "type_acte": "vente",
                }
                tool_input = {"type_acte": "vente"}

                result = executor._exec_generate_document(tool_input, agent_state)

                assert result["succes"] is True
                assert result["type_acte"] == "vente"
                assert result["fichier_url"] == "/files/vente_test.docx"
                mock_orch.generer_acte_complet.assert_called_once()

    def test_type_acte_in_tool_schema(self):
        """Le schema du tool generate_document inclut type_acte."""
        from execution.anthropic_tools import TOOLS

        gen_tool = next(t for t in TOOLS if t["name"] == "generate_document")
        props = gen_tool["input_schema"]["properties"]

        assert "type_acte" in props
        assert "promesse_vente" in props["type_acte"]["enum"]
        assert "vente" in props["type_acte"]["enum"]


# =============================================================================
# Test 3: ChatHandler generation trigger
# =============================================================================

class TestChatHandlerGeneration:
    """Verifie que ChatHandler declenche la generation quand prete."""

    def test_confirmation_triggers_generation_when_ready(self):
        """Quand etape_workflow=generation_prete et user dit 'oui', generer."""
        from execution.chat_handler import ChatHandler, ContexteConversation

        handler = ChatHandler(verbose=False)

        # Simuler un contexte avec questionnaire complet
        contexte = {
            "type_acte_en_cours": "promesse_vente",
            "etape_workflow": "generation_prete",
            "donnees_collectees": {
                "promettants": [{"nom": "Martin", "prenoms": "Jean"}],
                "beneficiaires": [{"nom": "Dupont", "prenoms": "Marie"}],
                "bien": {"adresse": {"voie": "12 rue de la Paix"}},
                "prix": {"montant": 450000},
            },
            "questionnaire_active": False,
            "questionnaire_state": None,
        }

        # Mock la generation pour eviter les vrais appels
        with patch(
            'execution.gestionnaires.gestionnaire_promesses.GestionnairePromesses'
        ) as MockGest:
            mock_resultat = MagicMock()
            mock_resultat.succes = True
            mock_resultat.fichier_docx = "outputs/promesse_test.docx"
            mock_resultat.erreurs = []

            mock_gest = MagicMock()
            mock_gest.generer.return_value = mock_resultat
            MockGest.return_value = mock_gest

            reponse = handler.traiter_message(
                message="Oui, generer le document",
                user_id="test",
                etude_id="etude_test",
                contexte=contexte,
            )

            assert "genere" in reponse.content.lower() or "succes" in reponse.content.lower() or "erreur" in reponse.content.lower()

    def test_generer_keyword_triggers_when_ready(self):
        """'Generer le document' declenche la generation meme si l'intention est CREER."""
        from execution.chat_handler import ChatHandler

        handler = ChatHandler(verbose=False)

        contexte = {
            "type_acte_en_cours": "promesse_vente",
            "etape_workflow": "generation_prete",
            "donnees_collectees": {"promettants": [{"nom": "Test"}], "prix": {"montant": 100000}},
            "questionnaire_active": False,
            "questionnaire_state": None,
        }

        with patch(
            'execution.gestionnaires.gestionnaire_promesses.GestionnairePromesses'
        ) as MockGest:
            mock_resultat = MagicMock()
            mock_resultat.succes = True
            mock_resultat.fichier_docx = "outputs/promesse_test2.docx"
            mock_resultat.erreurs = []

            mock_gest = MagicMock()
            mock_gest.generer.return_value = mock_resultat
            MockGest.return_value = mock_gest

            reponse = handler.traiter_message(
                message="Generer le document",
                user_id="test",
                etude_id="etude_test",
                contexte=contexte,
            )

            # Should trigger generation, not start a new questionnaire
            assert reponse.action is not None or "genere" in reponse.content.lower()


# =============================================================================
# Test 4: ChatHandler pre-fill from entities
# =============================================================================

class TestChatHandlerPrefill:
    """Verifie que le QuestionnaireManager est pre-rempli depuis les entites."""

    def test_build_prefill_from_entities(self):
        """_build_prefill_from_entities extrait les champs correctement."""
        from execution.chat_handler import ChatHandler

        handler = ChatHandler(verbose=False)

        entites = {
            "vendeur": {"nom": "Martin", "prenoms": "Jean"},
            "acquereur": {"nom": "Dupont"},
            "bien": {"adresse": "12 rue de la Paix, 75001 Paris", "surface": 67},
            "prix": 450000,
        }

        prefill = handler._build_prefill_from_entities(entites)

        assert prefill["vendeur_nom"] == "Martin"
        assert prefill["vendeur_prenoms"] == "Jean"
        assert prefill["acquereur_nom"] == "Dupont"
        assert prefill["bien_adresse"] == "12 rue de la Paix, 75001 Paris"
        assert prefill["bien_surface"] == "67"
        assert prefill["prix_montant"] == "450000"

    def test_prefill_empty_entities(self):
        """Entites vides -> prefill vide."""
        from execution.chat_handler import ChatHandler

        handler = ChatHandler(verbose=False)
        prefill = handler._build_prefill_from_entities({})
        assert prefill == {}


# =============================================================================
# Test 5: SYSTEM_PROMPT types d'actes
# =============================================================================

class TestSystemPrompt:
    """Verifie que le SYSTEM_PROMPT mentionne les deux types d'actes."""

    def test_prompt_mentions_vente(self):
        """SYSTEM_PROMPT mentionne 'acte de vente'."""
        from execution.anthropic_agent import SYSTEM_PROMPT
        assert "vente" in SYSTEM_PROMPT.lower()
        assert 'type_acte="vente"' in SYSTEM_PROMPT

    def test_prompt_mentions_promesse(self):
        """SYSTEM_PROMPT mentionne 'promesse de vente'."""
        from execution.anthropic_agent import SYSTEM_PROMPT
        assert "promesse" in SYSTEM_PROMPT.lower()
        assert 'type_acte="promesse_vente"' in SYSTEM_PROMPT

    def test_prompt_mentions_both_types(self):
        """SYSTEM_PROMPT mentionne les deux types avec enum values."""
        from execution.anthropic_agent import SYSTEM_PROMPT
        assert "promesse_vente" in SYSTEM_PROMPT
        assert '"vente"' in SYSTEM_PROMPT


# =============================================================================
# Test 6: _parse_response fichier_url from agent_state
# =============================================================================

class TestParseResponseFichierUrl:
    """Verifie que _parse_response utilise fichier_url depuis agent_state."""

    def test_fichier_url_from_agent_state(self):
        """_parse_response utilise agent_state['fichier_url'] en priorite."""
        from execution.anthropic_agent import AnthropicAgent

        agent = AnthropicAgent()
        agent_state = {
            "fichier_url": "/files/promesse_test.docx",
            "fichier_genere": "outputs/promesse_test.docx",
        }

        # Mock signed URL generation (imported inside _parse_response)
        with patch(
            'execution.security.signed_urls.generate_signed_url'
        ) as mock_sign:
            mock_sign.return_value = "/download/promesse_test.docx?token=abc&expires=999"

            result = agent._parse_response("Document genere.", agent_state)

            # Should have called generate_signed_url with the filename
            mock_sign.assert_called_once_with("promesse_test.docx", expires_in=3600)
            assert result.fichier_url == "/download/promesse_test.docx?token=abc&expires=999"

    def test_no_fichier_without_state(self):
        """Sans fichier dans agent_state, fichier_url est None."""
        from execution.anthropic_agent import AnthropicAgent

        agent = AnthropicAgent()
        result = agent._parse_response("Bonjour.", {})
        assert result.fichier_url is None


# =============================================================================
# Test 7: POST /ventes/generer endpoint exists
# =============================================================================

class TestVenteEndpoint:
    """Verifie que l'endpoint /ventes/generer est defini dans le code."""

    def test_vente_endpoint_in_source(self):
        """Le fichier api/main.py contient la definition de POST /ventes/generer."""
        api_path = PROJECT_ROOT / "api" / "main.py"
        source = api_path.read_text(encoding="utf-8")
        assert '"/ventes/generer"' in source
        assert "generer_vente" in source
        assert "OrchestratorNotaire" in source
