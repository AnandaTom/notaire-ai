#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chat_handler.py
--------------------
Tests unitaires pour le gestionnaire de chat (v1.4.0).
Couvre: analyse d'intention, génération de réponses, structures de données.
"""

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from execution.chat_handler import (
    ChatHandler,
    IntentionChat,
    MessageChat,
    ContexteConversation,
    ReponseChat,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def handler():
    """ChatHandler sans Supabase."""
    return ChatHandler(supabase_client=None, verbose=False)


# =============================================================================
# TESTS STRUCTURES DE DONNÉES
# =============================================================================

class TestStructures:
    """Tests des dataclasses."""

    def test_message_chat_creation(self):
        msg = MessageChat(role="user", content="Bonjour")
        assert msg.role == "user"
        assert msg.content == "Bonjour"
        assert msg.timestamp  # auto-filled

    def test_contexte_conversation_defaults(self):
        ctx = ContexteConversation()
        assert ctx.dossier_actif is None
        assert ctx.type_acte_en_cours is None
        assert ctx.donnees_collectees == {}

    def test_reponse_chat_defaults(self):
        rep = ReponseChat(content="Test")
        assert rep.content == "Test"
        assert rep.suggestions == []
        assert rep.action is None
        assert rep.confiance == 0.0

    def test_intention_chat_enum(self):
        assert IntentionChat.CREER.value == "creer"
        assert IntentionChat.SALUTATION.value == "salutation"


# =============================================================================
# TESTS ANALYSE D'INTENTION
# =============================================================================

class TestAnalyseIntention:
    """Tests de la détection d'intention."""

    def test_salutation_bonjour(self, handler):
        intention, confiance, _ = handler._analyser_intention("Bonjour")
        assert intention == IntentionChat.SALUTATION
        assert confiance >= 0.9

    def test_salutation_bonsoir(self, handler):
        intention, confiance, _ = handler._analyser_intention("Bonsoir Maître")
        assert intention == IntentionChat.SALUTATION

    def test_aide_detection(self, handler):
        intention, confiance, _ = handler._analyser_intention("Comment faire une promesse ?")
        assert intention == IntentionChat.AIDE

    def test_creation_promesse(self, handler):
        intention, _, _ = handler._analyser_intention(
            "Je veux créer une promesse de vente"
        )
        assert intention == IntentionChat.CREER

    def test_creation_acte(self, handler):
        intention, _, _ = handler._analyser_intention(
            "Générer un acte de vente"
        )
        assert intention == IntentionChat.CREER

    def test_recherche(self, handler):
        intention, _, _ = handler._analyser_intention(
            "Cherche le dossier Dupont"
        )
        assert intention == IntentionChat.RECHERCHER


# =============================================================================
# TESTS TRAITEMENT MESSAGE
# =============================================================================

class TestTraiterMessage:
    """Tests du traitement complet d'un message."""

    def test_reponse_type(self, handler):
        """Le handler retourne un ReponseChat."""
        reponse = handler.traiter_message(
            message="Bonjour",
            user_id="test",
            etude_id="test-etude"
        )
        assert isinstance(reponse, ReponseChat)
        assert reponse.content
        assert len(reponse.content) > 0

    def test_reponse_salutation_contient_texte(self, handler):
        reponse = handler.traiter_message(
            message="Bonjour",
            user_id="test",
            etude_id="test-etude"
        )
        assert reponse.intention_detectee == "salutation"

    def test_reponse_creation_suggestions(self, handler):
        """Une demande de création retourne des suggestions."""
        reponse = handler.traiter_message(
            message="Je veux créer une promesse de vente",
            user_id="test",
            etude_id="test-etude"
        )
        assert reponse.intention_detectee == "creer"

    def test_reponse_avec_historique(self, handler):
        """Le handler accepte un historique."""
        historique = [
            {"role": "assistant", "content": "Bonjour"},
            {"role": "user", "content": "Je veux un acte"},
        ]
        reponse = handler.traiter_message(
            message="De vente",
            user_id="test",
            etude_id="test-etude",
            historique=historique
        )
        assert isinstance(reponse, ReponseChat)

    def test_reponse_avec_contexte(self, handler):
        """Le handler accepte un contexte."""
        reponse = handler.traiter_message(
            message="Continuons",
            user_id="test",
            etude_id="test-etude",
            contexte={"type_acte_en_cours": "promesse_vente"}
        )
        assert isinstance(reponse, ReponseChat)
