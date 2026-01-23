#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_database.py
-----------------
Interface Supabase pour l'agent NotaireAI.

Ce module est utilisé par l'agent en production (Modal) pour:
- Rechercher des clients par nom
- Récupérer les dossiers d'un client
- Sauvegarder les nouvelles données

Fonctionne partout: local, Claude Code, Modal, etc.

Configuration via variables d'environnement:
    SUPABASE_URL=https://xxx.supabase.co
    SUPABASE_SERVICE_KEY=eyJhbG...  (clé Legacy JWT service_role)

Usage:
    from agent_database import AgentDB

    db = AgentDB()

    # Rechercher un client
    clients = db.search_client("Dupont", etude_id="xxx")

    # Récupérer les dossiers d'un client
    dossiers = db.get_client_dossiers(client_id="xxx")

    # Créer un nouveau dossier
    dossier_id = db.create_dossier(etude_id, numero, type_acte, parties, donnees)
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Charge .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# Import Supabase (optionnel - mode offline si non disponible)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("INFO: supabase non installé - mode offline activé")


class AgentDB:
    """
    Interface base de données pour l'agent NotaireAI.

    Gère automatiquement:
    - Connexion à Supabase via variables d'environnement
    - Mode offline si Supabase non disponible
    - Hachage des noms pour recherche sécurisée
    """

    def __init__(self):
        """Initialise la connexion à Supabase."""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self._offline = True

        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                self._offline = False
            except Exception as e:
                print(f"WARN: Connexion Supabase échouée: {e}")

    @property
    def is_connected(self) -> bool:
        """Vérifie si la connexion est active."""
        return not self._offline

    # =========================================================================
    # RECHERCHE CLIENTS
    # =========================================================================

    def search_client(
        self,
        nom: str,
        etude_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recherche des clients par nom (via hash sécurisé).

        Args:
            nom: Nom à rechercher
            etude_id: ID de l'étude
            limit: Nombre max de résultats

        Returns:
            Liste de clients correspondants
        """
        if self._offline:
            return []

        # Hash du nom pour recherche
        nom_hash = self._hash_nom(nom)

        try:
            result = (
                self.client.table("clients")
                .select("*")
                .eq("etude_id", etude_id)
                .eq("nom_hash", nom_hash)
                .is_("deleted_at", "null")
                .eq("anonymized", False)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"ERREUR search_client: {e}")
            return []

    def get_client(self, client_id: str) -> Optional[Dict]:
        """Récupère un client par son ID."""
        if self._offline:
            return None

        try:
            result = (
                self.client.table("clients")
                .select("*")
                .eq("id", client_id)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"ERREUR get_client: {e}")
            return None

    def get_all_clients(self, etude_id: str, limit: int = 100) -> List[Dict]:
        """Récupère tous les clients actifs d'une étude."""
        if self._offline:
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
            print(f"ERREUR get_all_clients: {e}")
            return []

    # =========================================================================
    # DOSSIERS
    # =========================================================================

    def get_client_dossiers(self, client_id: str) -> List[Dict]:
        """
        Récupère tous les dossiers où un client est partie.

        Args:
            client_id: ID du client

        Returns:
            Liste des dossiers
        """
        if self._offline:
            return []

        try:
            # Recherche dans le champ JSONB parties
            result = (
                self.client.table("dossiers")
                .select("*")
                .contains("parties", [{"client_id": client_id}])
                .is_("deleted_at", "null")
                .order("created_at", desc=True)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"ERREUR get_client_dossiers: {e}")
            return []

    def get_dossier(self, dossier_id: str) -> Optional[Dict]:
        """Récupère un dossier par son ID."""
        if self._offline:
            return None

        try:
            result = (
                self.client.table("dossiers")
                .select("*")
                .eq("id", dossier_id)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"ERREUR get_dossier: {e}")
            return None

    def get_dossier_by_numero(self, etude_id: str, numero: str) -> Optional[Dict]:
        """Récupère un dossier par son numéro."""
        if self._offline:
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
            print(f"ERREUR get_dossier_by_numero: {e}")
            return None

    def get_all_dossiers(
        self,
        etude_id: str,
        statut: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Récupère les dossiers d'une étude."""
        if self._offline:
            return []

        try:
            query = (
                self.client.table("dossiers")
                .select("*")
                .eq("etude_id", etude_id)
                .is_("deleted_at", "null")
            )

            if statut:
                query = query.eq("statut", statut)

            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"ERREUR get_all_dossiers: {e}")
            return []

    def create_dossier(
        self,
        etude_id: str,
        numero: str,
        type_acte: str,
        parties: List[Dict] = None,
        donnees_metier: Dict = None
    ) -> Optional[str]:
        """
        Crée un nouveau dossier.

        Args:
            etude_id: ID de l'étude
            numero: Numéro du dossier (ex: "VTE-2026-001")
            type_acte: Type d'acte (vente, promesse, etc.)
            parties: Liste des parties [{client_id, role}]
            donnees_metier: Données métier du dossier

        Returns:
            ID du dossier créé ou None
        """
        if self._offline:
            return None

        try:
            data = {
                "etude_id": etude_id,
                "numero": numero,
                "type_acte": type_acte,
                "parties": parties or [],
                "donnees_metier": donnees_metier or {},
                "statut": "brouillon"
            }

            result = self.client.table("dossiers").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            print(f"ERREUR create_dossier: {e}")
            return None

    def update_dossier(self, dossier_id: str, **kwargs) -> bool:
        """Met à jour un dossier."""
        if self._offline:
            return False

        try:
            self.client.table("dossiers").update(kwargs).eq("id", dossier_id).execute()
            return True
        except Exception as e:
            print(f"ERREUR update_dossier: {e}")
            return False

    # =========================================================================
    # ETUDES
    # =========================================================================

    def get_etude(self, etude_id: str) -> Optional[Dict]:
        """Récupère une étude par son ID."""
        if self._offline:
            return None

        try:
            result = (
                self.client.table("etudes")
                .select("*")
                .eq("id", etude_id)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"ERREUR get_etude: {e}")
            return None

    def get_all_etudes(self) -> List[Dict]:
        """Récupère toutes les études (admin only)."""
        if self._offline:
            return []

        try:
            result = self.client.table("etudes").select("*").execute()
            return result.data
        except Exception as e:
            print(f"ERREUR get_all_etudes: {e}")
            return []

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _hash_nom(self, nom: str) -> str:
        """
        Hash un nom pour recherche sécurisée.

        Le hash est normalisé (minuscules, sans accents) pour
        permettre des recherches insensibles à la casse.
        """
        import unicodedata

        # Normalise: minuscules, sans accents, sans espaces multiples
        nom_normalise = unicodedata.normalize('NFKD', nom.lower())
        nom_normalise = ''.join(c for c in nom_normalise if not unicodedata.combining(c))
        nom_normalise = ' '.join(nom_normalise.split())

        return hashlib.sha256(nom_normalise.encode()).hexdigest()

    def log_action(
        self,
        action: str,
        resource_type: str,
        etude_id: str = None,
        resource_id: str = None,
        details: Dict = None
    ) -> None:
        """Enregistre une action dans les logs d'audit."""
        if self._offline:
            return

        try:
            self.client.table("audit_logs").insert({
                "action": action,
                "resource_type": resource_type,
                "etude_id": etude_id,
                "resource_id": resource_id,
                "details": details or {}
            }).execute()
        except Exception:
            pass  # Non bloquant


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("Test AgentDB...")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NON CONFIGURÉ')}")

    db = AgentDB()
    print(f"Connecté: {db.is_connected}")

    if db.is_connected:
        # Test récupération études
        etudes = db.get_all_etudes()
        print(f"Études trouvées: {len(etudes)}")

        print("\n✓ AgentDB prêt pour la production!")
    else:
        print("\n⚠ Mode offline - configurez les variables d'environnement")
