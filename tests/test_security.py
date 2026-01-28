#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_security.py
----------------
Tests de securite et chiffrement pour l'integration Supabase NotaireAI.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def encryption_key():
    """Genere une cle de chiffrement de test."""
    from execution.security.encryption_service import EncryptionService
    return EncryptionService.generate_master_key()


@pytest.fixture
def encryption_service(encryption_key):
    """Cree une instance du service de chiffrement."""
    from execution.security.encryption_service import EncryptionService
    return EncryptionService(master_key=encryption_key)


@pytest.fixture
def mock_supabase_env(encryption_key):
    """Configure l'environnement pour Supabase mock."""
    env_vars = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "ENCRYPTION_MASTER_KEY": encryption_key,
        "AGENT_USER_ID": "test-agent"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def offline_env(encryption_key):
    """Configure l'environnement en mode offline."""
    env_vars = {
        "SUPABASE_URL": "",
        "SUPABASE_SERVICE_KEY": "",
        "ENCRYPTION_MASTER_KEY": encryption_key,
        "AGENT_USER_ID": "test-agent"
    }
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


# =============================================================================
# TESTS ENCRYPTION SERVICE
# =============================================================================

class TestEncryptionService:
    """Tests pour le service de chiffrement."""

    def test_generate_key(self):
        """Test: la generation de cle produit une cle 256-bit valide."""
        from execution.security.encryption_service import EncryptionService
        import base64

        key = EncryptionService.generate_master_key()

        assert len(key) > 0
        decoded = base64.b64decode(key)
        assert len(decoded) == 32  # 256 bits

    def test_encrypt_decrypt_roundtrip(self, encryption_service):
        """Test: chiffrement puis dechiffrement retourne la valeur originale."""
        original = "Jean Dupont"

        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == original
        assert encrypted != original

    def test_encrypt_produces_json(self, encryption_service):
        """Test: la valeur chiffree est un JSON valide avec les champs attendus."""
        encrypted = encryption_service.encrypt("test")
        data = json.loads(encrypted)

        assert "c" in data  # ciphertext
        assert "n" in data  # nonce
        assert "k" in data  # key_id
        assert "v" in data  # version
        assert "t" in data  # timestamp

    def test_different_encryptions_differ(self, encryption_service):
        """Test: le meme texte produit des chiffrements differents (nonce aleatoire)."""
        original = "Meme texte"

        enc1 = encryption_service.encrypt(original)
        enc2 = encryption_service.encrypt(original)

        # Doivent etre differents a cause du nonce
        assert enc1 != enc2

        # Mais dechiffrent vers la meme valeur
        assert encryption_service.decrypt(enc1) == encryption_service.decrypt(enc2) == original

    def test_encrypt_empty_string(self, encryption_service):
        """Test: gestion des chaines vides."""
        assert encryption_service.encrypt("") == ""
        assert encryption_service.decrypt("") == ""

    def test_encrypt_unicode(self, encryption_service):
        """Test: gestion des caracteres Unicode."""
        original = "Jean-Pierre Hébert éàüö"

        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)

        assert decrypted == original

    def test_encrypt_dict(self, encryption_service):
        """Test: chiffrement de dictionnaire."""
        data = {
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean@example.com",
            "profession": "Ingenieur"  # Non sensible
        }

        encrypted = encryption_service.encrypt_dict(data)

        # Champs sensibles chiffres
        assert "nom_encrypted" in encrypted
        assert "prenom_encrypted" in encrypted
        assert "email_encrypted" in encrypted
        assert "nom" not in encrypted
        assert "prenom" not in encrypted
        assert "email" not in encrypted

        # Champs non-sensibles conserves
        assert encrypted.get("profession") == "Ingenieur"

    def test_decrypt_dict(self, encryption_service):
        """Test: dechiffrement de dictionnaire."""
        original = {
            "nom": "Dupont",
            "prenom": "Jean"
        }

        encrypted = encryption_service.encrypt_dict(original)
        decrypted = encryption_service.decrypt_dict(encrypted)

        assert decrypted["nom"] == original["nom"]
        assert decrypted["prenom"] == original["prenom"]

    def test_hash_for_search(self, encryption_service):
        """Test: generation de hash recherchable."""
        hash1 = encryption_service.hash_for_search("Dupont")
        hash2 = encryption_service.hash_for_search("dupont")  # Casse differente
        hash3 = encryption_service.hash_for_search(" Dupont ")  # Espaces

        # Doit produire le meme hash (normalise)
        assert hash1 == hash2 == hash3

        # Valeur differente = hash different
        hash4 = encryption_service.hash_for_search("Martin")
        assert hash4 != hash1

    def test_hash_empty_returns_none(self, encryption_service):
        """Test: hash d'une valeur vide retourne None."""
        assert encryption_service.hash_for_search("") is None
        assert encryption_service.hash_for_search(None) is None

    def test_invalid_key_raises_error(self):
        """Test: une cle invalide leve une erreur."""
        from execution.security.encryption_service import EncryptionService

        with pytest.raises(ValueError):
            EncryptionService(master_key="invalid-key")

    def test_wrong_key_fails_decrypt(self, encryption_key):
        """Test: dechiffrer avec la mauvaise cle echoue."""
        from execution.security.encryption_service import EncryptionService

        service1 = EncryptionService(master_key=encryption_key)
        encrypted = service1.encrypt("Secret data")

        # Autre cle
        other_key = EncryptionService.generate_master_key()
        service2 = EncryptionService(master_key=other_key)

        with pytest.raises(Exception):
            service2.decrypt(encrypted)


class TestMaskPII:
    """Tests pour le masquage PII."""

    def test_mask_short_values(self):
        """Test: masquage des valeurs courtes."""
        from execution.security.encryption_service import mask_pii

        data = {"nom": "Jo"}
        masked = mask_pii(data)

        assert masked["nom"] == "****"

    def test_mask_long_values(self):
        """Test: masquage des valeurs longues."""
        from execution.security.encryption_service import mask_pii

        data = {"nom": "Dupont"}
        masked = mask_pii(data)

        assert masked["nom"] == "Du**nt"

    def test_mask_preserves_non_sensitive(self):
        """Test: les champs non-sensibles ne sont pas masques."""
        from execution.security.encryption_service import mask_pii

        data = {
            "nom": "Dupont",
            "type_acte": "vente"
        }
        masked = mask_pii(data)

        assert masked["type_acte"] == "vente"


# =============================================================================
# TESTS SECURE CLIENT MANAGER
# =============================================================================

class TestSecureClientManager:
    """Tests pour le gestionnaire de clients securise."""

    def test_offline_mode_when_no_config(self, offline_env):
        """Test: mode offline active sans configuration."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        assert manager._offline_mode is True

    def test_client_data_encrypted_before_storage(self, offline_env):
        """Test: PII chiffre avant stockage."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test")

        # Chiffrer les donnees
        data = {"nom": "Dupont", "prenom": "Jean"}
        encrypted = manager._encrypt_client_data(data)

        # Verifier le chiffrement
        assert "nom_encrypted" in encrypted
        assert "nom" not in encrypted
        assert encrypted["nom_encrypted"] != "Dupont"

    def test_create_client_offline(self, offline_env):
        """Test: creation de client en mode offline."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        client_id = manager.create_client({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean@example.com"
        })

        assert client_id is not None
        assert client_id.startswith("offline_") or len(client_id) > 10

    def test_get_client_offline(self, offline_env):
        """Test: recuperation de client en mode offline."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        # Creer
        client_id = manager.create_client({
            "nom": "Martin",
            "prenom": "Sophie"
        })

        # Recuperer
        client = manager.get_client(client_id)

        assert client is not None
        assert client.nom == "Martin"
        assert client.prenom == "Sophie"

    def test_search_clients_offline(self, offline_env):
        """Test: recherche de clients en mode offline."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        # Creer quelques clients
        manager.create_client({"nom": "Dupont", "prenom": "Jean"})
        manager.create_client({"nom": "Martin", "prenom": "Sophie"})

        # Rechercher
        results = manager.search_clients(nom="Dupont")

        assert len(results) >= 1
        assert any(c.nom == "Dupont" for c in results)

    def test_anonymize_client(self, offline_env):
        """Test: anonymisation de client."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        # Creer
        client_id = manager.create_client({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean@example.com"
        })

        # Anonymiser
        result = manager._anonymize_client(client_id)

        assert result is True

        # Verifier
        client = manager._offline_storage.get(client_id)
        assert client is not None
        assert client.get("anonymized") is True
        assert client.get("deleted_at") is not None

    def test_scan_sensitive_data(self, offline_env):
        """Test: detection de donnees sensibles."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test")

        # NIR (numero secu)
        warnings = manager._scan_sensitive_data("1 85 12 75 108 789 45")
        assert "nir" in warnings

        # IBAN
        warnings = manager._scan_sensitive_data("FR76 1234 5678 9012 3456 7890 123")
        assert "iban" in warnings

        # Donnees medicales
        warnings = manager._scan_sensitive_data("Patient atteint de cancer")
        assert "medical" in warnings

        # Texte normal
        warnings = manager._scan_sensitive_data("Jean Dupont, 123 rue de Paris")
        assert len(warnings) == 0


# =============================================================================
# TESTS AGENT CLIENT ACCESS
# =============================================================================

class TestAgentClientAccess:
    """Tests pour l'interface Agent."""

    def test_collect_field_valid(self, offline_env):
        """Test: collecte d'un champ valide."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        result = agent.collect_field("nom", "Dupont")

        assert result["valid"] is True

    def test_collect_field_empty_required(self, offline_env):
        """Test: collecte d'un champ requis vide."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        result = agent.collect_field("nom", "")

        assert result["valid"] is False

    def test_collect_field_invalid_email(self, offline_env):
        """Test: validation format email."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        result = agent.collect_field("email", "invalid-email")

        assert result["valid"] is False

    def test_get_missing_fields(self, offline_env):
        """Test: detection des champs manquants."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        missing = agent.get_missing_fields("basic")
        assert "nom" in missing
        assert "prenom" in missing

        agent.collect_field("nom", "Dupont")
        missing = agent.get_missing_fields("basic")
        assert "nom" not in missing
        assert "prenom" in missing

    def test_get_next_question(self, offline_env):
        """Test: generation de questions."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        question = agent.get_next_question("basic")

        assert question is not None
        assert hasattr(question, "field")
        assert hasattr(question, "question")

    def test_collection_summary_masks_pii(self, offline_env):
        """Test: le resume masque les PII."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        agent.collect_field("nom", "Dupont")
        agent.collect_field("email", "jean@example.com")

        summary = agent.get_collection_summary()

        # PII doit etre masque
        assert "Dupont" not in str(summary["data_preview"].get("nom", ""))

    def test_save_collected_client(self, offline_env):
        """Test: sauvegarde des donnees collectees."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        agent.collect_field("nom", "Dupont")
        agent.collect_field("prenom", "Jean")

        client_id = agent.save_collected_client()

        assert client_id is not None

    def test_save_incomplete_fails(self, offline_env):
        """Test: sauvegarde echoue si incomplet."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        # Seulement nom, prenom manquant
        agent.collect_field("nom", "Dupont")

        client_id = agent.save_collected_client()

        assert client_id is None

    def test_create_dossier(self, offline_env):
        """Test: creation de dossier."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        dossier_id = agent.create_dossier(
            numero="D2024-001",
            type_acte="vente"
        )

        assert dossier_id is not None

    def test_client_to_variables(self, offline_env):
        """Test: conversion client vers variables template."""
        from execution.security.agent_client_access import AgentClientAccess
        from execution.security.secure_client_manager import ClientData

        agent = AgentClientAccess(etude_id="test-etude")

        client = ClientData(
            id="test-id",
            nom="Dupont",
            prenom="Jean",
            adresse="123 rue de Paris"
        )

        variables = agent._client_to_variables(client, "vendeur")

        assert variables["vendeur_nom"] == "Dupont"
        assert variables["vendeur_prenom"] == "Jean"
        assert variables["vendeur_adresse"] == "123 rue de Paris"
        assert variables["personne_physique"]["nom"] == "Dupont"


# =============================================================================
# TESTS INTEGRATION
# =============================================================================

class TestIntegration:
    """Tests d'integration complets."""

    def test_full_workflow_offline(self, offline_env):
        """Test: workflow complet en mode offline."""
        from execution.security.agent_client_access import AgentClientAccess

        agent = AgentClientAccess(etude_id="test-etude")

        # 1. Collecter les donnees du vendeur
        agent.start_collection(context="vendeur")
        agent.collect_field("nom", "Dupont")
        agent.collect_field("prenom", "Jean")
        agent.collect_field("adresse", "123 rue de Paris, 75001 Paris")
        agent.collect_field("situation_matrimoniale", "Marie(e)")

        vendeur_id = agent.save_collected_client()
        assert vendeur_id is not None

        # 2. Collecter les donnees de l'acquereur
        agent.start_collection(context="acquereur")
        agent.collect_field("nom", "Martin")
        agent.collect_field("prenom", "Sophie")
        agent.collect_field("adresse", "456 avenue des Champs, 75008 Paris")
        agent.collect_field("situation_matrimoniale", "Celibataire")

        acquereur_id = agent.save_collected_client()
        assert acquereur_id is not None

        # 3. Creer un dossier
        dossier_id = agent.create_dossier(
            numero="D2024-TEST",
            type_acte="vente",
            parties=[
                {"client_id": vendeur_id, "role": "vendeur"},
                {"client_id": acquereur_id, "role": "acquereur"}
            ]
        )
        assert dossier_id is not None

        # 4. Recuperer le vendeur
        vendeur = agent.get_client_by_id(vendeur_id)
        assert vendeur.nom == "Dupont"

        # 5. Rechercher
        results = agent.search_clients(nom="Dupont")
        assert len(results) >= 1

    def test_gdpr_workflow(self, offline_env):
        """Test: workflow RGPD complet."""
        from execution.security.secure_client_manager import SecureClientManager

        manager = SecureClientManager(etude_id="test-etude")

        # 1. Creer un client
        client_id = manager.create_client({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean@example.com",
            "telephone": "0612345678"
        })

        # 2. Demande d'acces (Art. 15)
        access_response = manager.handle_gdpr_request(
            client_id=client_id,
            request_type="access",
            requested_by="jean@example.com"
        )
        assert access_response["status"] == "completed"
        assert "data" in access_response
        assert access_response["data"]["client"]["nom"] == "Dupont"

        # 3. Demande de portabilite (Art. 20)
        port_response = manager.handle_gdpr_request(
            client_id=client_id,
            request_type="portability",
            requested_by="jean@example.com"
        )
        assert port_response["status"] == "completed"
        assert port_response["content_type"] == "application/json"

        # 4. Demande d'opposition (Art. 21)
        opp_response = manager.handle_gdpr_request(
            client_id=client_id,
            request_type="opposition",
            requested_by="jean@example.com"
        )
        assert opp_response["status"] == "completed"

        # Verifier opt-out
        client = manager.get_client(client_id)
        assert client.ai_enrichments.get("opt_out") is True

        # 5. Demande d'effacement (Art. 17)
        erasure_response = manager.handle_gdpr_request(
            client_id=client_id,
            request_type="erasure",
            requested_by="jean@example.com"
        )
        assert erasure_response["status"] == "completed"

        # Verifier anonymisation
        raw_data = manager._offline_storage.get(client_id)
        assert raw_data.get("anonymized") is True


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
