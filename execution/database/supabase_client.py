#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
supabase_client.py
------------------

NOTE: Pour Windows, force l'encodage UTF-8
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

"""
Module centralisé pour la connexion Supabase.

Ce module est utilisé par TOUS les scripts et par l'agent en production.
Il garantit une connexion unique et cohérente à la base de données.

Configuration requise dans .env:
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-anon-key  (pour le frontend)
    SUPABASE_SERVICE_KEY=your-service-key  (pour le backend/agent)

Usage:
    from supabase_client import get_supabase_client, SupabaseManager

    # Client simple
    client = get_supabase_client()

    # Manager avec helpers
    manager = SupabaseManager()
    clients = manager.get_clients()
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from functools import lru_cache

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Charge les variables d'environnement
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

# Import Supabase
try:
    from supabase import create_client, Client
except ImportError:
    print("ERREUR: supabase n'est pas installé. Exécutez: pip install supabase")
    create_client = None
    Client = None


@lru_cache(maxsize=1)
def get_supabase_client(use_service_key: bool = True) -> Optional[Client]:
    """
    Retourne un client Supabase singleton.

    Args:
        use_service_key: Si True, utilise la clé service (bypass RLS).
                        Si False, utilise la clé anon (respecte RLS).

    Returns:
        Client Supabase ou None si non configuré
    """
    if create_client is None:
        return None

    url = os.getenv("SUPABASE_URL")

    if use_service_key:
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    else:
        key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("AVERTISSEMENT: Variables SUPABASE_URL/SUPABASE_KEY non configurées")
        return None

    try:
        from supabase.lib.client_options import ClientOptions
        options = ClientOptions(
            postgrest_client_timeout=30,    # 30s timeout on DB queries
        )
        return create_client(url, key, options=options)
    except Exception as e:
        print(f"ERREUR connexion Supabase: {e}")
        return None


class SupabaseManager:
    """
    Gestionnaire haut niveau pour les opérations Supabase.

    Fournit des méthodes CRUD pour toutes les tables du projet:
    - etudes: Études notariales
    - clients: Clients avec données chiffrées
    - dossiers: Dossiers/actes
    - audit_logs: Logs d'audit
    - rgpd_requests: Demandes RGPD
    """

    def __init__(self, use_service_key: bool = True):
        """
        Initialise le manager.

        Args:
            use_service_key: Utiliser la clé service (recommandé pour l'agent)
        """
        self.client = get_supabase_client(use_service_key)
        self._offline_mode = self.client is None
        self._cache = {}

    @property
    def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        return not self._offline_mode

    # =========================================================================
    # ETUDES
    # =========================================================================

    def get_etude(self, etude_id: str) -> Optional[Dict]:
        """Récupère une étude par son ID."""
        if self._offline_mode:
            return None

        try:
            result = self.client.table("etudes").select("*").eq("id", etude_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_etude: {e}")
            return None

    def create_etude(self, nom: str, siret: str = None, **kwargs) -> Optional[str]:
        """Crée une nouvelle étude."""
        if self._offline_mode:
            return None

        try:
            data = {"nom": nom, "siret": siret, **kwargs}
            result = self.client.table("etudes").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"Erreur create_etude: {e}")
            return None

    # =========================================================================
    # CLIENTS
    # =========================================================================

    def get_clients(self, etude_id: str, limit: int = 100) -> List[Dict]:
        """Récupère les clients d'une étude."""
        if self._offline_mode:
            return []

        try:
            result = (
                self.client.table("clients")
                .select("*")
                .eq("etude_id", etude_id)
                .is_("deleted_at", "null")
                .eq("anonymized", False)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"Erreur get_clients: {e}")
            return []

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Récupère un client par son ID."""
        if self._offline_mode:
            return None

        try:
            result = self.client.table("clients").select("*").eq("id", client_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_client: {e}")
            return None

    def search_clients(self, etude_id: str, nom_hash: str) -> List[Dict]:
        """Recherche des clients par hash du nom."""
        if self._offline_mode:
            return []

        try:
            result = (
                self.client.table("clients")
                .select("*")
                .eq("etude_id", etude_id)
                .eq("nom_hash", nom_hash)
                .is_("deleted_at", "null")
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"Erreur search_clients: {e}")
            return []

    def create_client(self, etude_id: str, nom_encrypted: str, **kwargs) -> Optional[str]:
        """Crée un nouveau client."""
        if self._offline_mode:
            return None

        try:
            data = {"etude_id": etude_id, "nom_encrypted": nom_encrypted, **kwargs}
            result = self.client.table("clients").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"Erreur create_client: {e}")
            return None

    def update_client(self, client_id: str, **kwargs) -> bool:
        """Met à jour un client."""
        if self._offline_mode:
            return False

        try:
            self.client.table("clients").update(kwargs).eq("id", client_id).execute()
            return True
        except Exception as e:
            print(f"Erreur update_client: {e}")
            return False

    # =========================================================================
    # DOSSIERS
    # =========================================================================

    def get_dossiers(self, etude_id: str, limit: int = 100) -> List[Dict]:
        """Récupère les dossiers d'une étude."""
        if self._offline_mode:
            return []

        try:
            result = (
                self.client.table("dossiers")
                .select("*")
                .eq("etude_id", etude_id)
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"Erreur get_dossiers: {e}")
            return []

    def get_dossier(self, dossier_id: str) -> Optional[Dict]:
        """Récupère un dossier par son ID."""
        if self._offline_mode:
            return None

        try:
            result = self.client.table("dossiers").select("*").eq("id", dossier_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_dossier: {e}")
            return None

    def get_dossier_by_numero(self, etude_id: str, numero: str) -> Optional[Dict]:
        """Récupère un dossier par son numéro."""
        if self._offline_mode:
            return None

        try:
            result = (
                self.client.table("dossiers")
                .select("*")
                .eq("etude_id", etude_id)
                .eq("numero", numero)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur get_dossier_by_numero: {e}")
            return None

    def create_dossier(self, etude_id: str, numero: str, type_acte: str, **kwargs) -> Optional[str]:
        """Crée un nouveau dossier."""
        if self._offline_mode:
            return None

        try:
            data = {
                "etude_id": etude_id,
                "numero": numero,
                "type_acte": type_acte,
                **kwargs
            }
            result = self.client.table("dossiers").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"Erreur create_dossier: {e}")
            return None

    def update_dossier(self, dossier_id: str, **kwargs) -> bool:
        """Met à jour un dossier."""
        if self._offline_mode:
            return False

        try:
            self.client.table("dossiers").update(kwargs).eq("id", dossier_id).execute()
            return True
        except Exception as e:
            print(f"Erreur update_dossier: {e}")
            return False

    # =========================================================================
    # AUDIT LOGS
    # =========================================================================

    def log_action(
        self,
        action: str,
        resource_type: str,
        etude_id: str = None,
        resource_id: str = None,
        details: Dict = None
    ) -> Optional[str]:
        """Enregistre une action dans les logs d'audit."""
        if self._offline_mode:
            return None

        try:
            data = {
                "action": action,
                "resource_type": resource_type,
                "etude_id": etude_id,
                "resource_id": resource_id,
                "details": details or {}
            }
            result = self.client.table("audit_logs").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"Erreur log_action: {e}")
            return None

    # =========================================================================
    # RGPD
    # =========================================================================

    def get_pending_rgpd_requests(self, etude_id: str) -> List[Dict]:
        """Récupère les demandes RGPD en attente."""
        if self._offline_mode:
            return []

        try:
            result = (
                self.client.table("rgpd_requests")
                .select("*")
                .eq("etude_id", etude_id)
                .eq("status", "pending")
                .order("deadline_at")
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"Erreur get_pending_rgpd_requests: {e}")
            return []


# =========================================================================
# TEST DE CONNEXION
# =========================================================================

def test_connection() -> bool:
    """Teste la connexion à Supabase."""
    client = get_supabase_client()
    if client is None:
        print("ERREUR: Impossible de se connecter à Supabase")
        return False

    try:
        # Teste une requête simple
        result = client.table("etudes").select("id").limit(1).execute()
        print("OK: Connexion Supabase réussie")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        return False


if __name__ == "__main__":
    # Test de connexion
    print("Test de connexion Supabase...")
    print(f"URL: {os.getenv('SUPABASE_URL', 'NON CONFIGURÉE')}")
    print(f"KEY: {'****' + os.getenv('SUPABASE_KEY', '')[-8:] if os.getenv('SUPABASE_KEY') else 'NON CONFIGURÉE'}")
    print()

    if test_connection():
        print("\n✓ Supabase est prêt à être utilisé!")

        # Test du manager
        manager = SupabaseManager()
        print(f"\nManager connecté: {manager.is_connected}")
    else:
        print("\n✗ Vérifiez votre configuration .env")
        sys.exit(1)
