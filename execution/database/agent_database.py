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
from datetime import datetime, timezone

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
    - Authentification par clé API (NOTAIRE_API_KEY)
    - Isolation des données par étude (multi-tenant)
    - Mode offline si Supabase non disponible
    - Hachage des noms pour recherche sécurisée

    Configuration:
        # Option 1: Clé API spécifique notaire (recommandé pour production)
        NOTAIRE_API_KEY=nai_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # Option 2: Credentials Supabase directs + etude_id
        SUPABASE_URL=https://xxx.supabase.co
        SUPABASE_SERVICE_KEY=eyJhbG...
        NOTAIRE_ETUDE_ID=uuid-de-l-etude
    """

    def __init__(self, api_key: str = None, etude_id: str = None):
        """
        Initialise la connexion à Supabase.

        Args:
            api_key: Clé API notaire (optionnel, sinon utilise env)
            etude_id: ID de l'étude (optionnel, sinon déduit de la clé API)
        """
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self._offline = True
        self._etude_id: Optional[str] = None
        self._permissions: Dict = {"read": True, "write": True, "delete": False}
        self._rate_limit: int = 60

        # Clé API notaire (prioritaire)
        self._api_key = api_key or os.getenv("NOTAIRE_API_KEY")

        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                self._offline = False

                # Valider la clé API et récupérer l'etude_id
                if self._api_key:
                    self._validate_api_key()
                elif etude_id:
                    self._etude_id = etude_id
                else:
                    self._etude_id = os.getenv("NOTAIRE_ETUDE_ID")

            except Exception as e:
                print(f"WARN: Connexion Supabase échouée: {e}")

    def _validate_api_key(self) -> bool:
        """Valide la clé API et récupère les permissions."""
        if not self._api_key or not self.client:
            return False

        try:
            result = self.client.rpc(
                "validate_agent_api_key",
                {"api_key": self._api_key}
            ).execute()

            if result.data and len(result.data) > 0:
                self._etude_id = result.data[0]["etude_id"]
                self._permissions = result.data[0]["permissions"]
                self._rate_limit = result.data[0]["rate_limit"]
                return True
            else:
                print("WARN: Clé API invalide ou expirée")
                return False
        except Exception as e:
            print(f"WARN: Erreur validation clé API: {e}")
            return False

    @property
    def etude_id(self) -> Optional[str]:
        """Retourne l'ID de l'étude courante."""
        return self._etude_id

    @property
    def permissions(self) -> Dict:
        """Retourne les permissions de l'agent."""
        return self._permissions

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
        etude_id: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recherche des clients par nom (via hash sécurisé).

        Args:
            nom: Nom à rechercher
            etude_id: ID de l'étude (optionnel, utilise celui de la clé API)
            limit: Nombre max de résultats

        Returns:
            Liste de clients correspondants
        """
        if self._offline:
            return []

        # Utilise l'etude_id de la clé API si non fourni
        etude_id = etude_id or self._etude_id
        if not etude_id:
            print("ERREUR: etude_id requis (via clé API ou paramètre)")
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

    def get_all_clients(self, etude_id: str = None, limit: int = 100) -> List[Dict]:
        """Récupère tous les clients actifs d'une étude."""
        if self._offline:
            return []

        etude_id = etude_id or self._etude_id
        if not etude_id:
            print("ERREUR: etude_id requis")
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

    def get_dossier_by_numero(self, numero: str, etude_id: str = None) -> Optional[Dict]:
        """Récupère un dossier par son numéro."""
        if self._offline:
            return None

        etude_id = etude_id or self._etude_id
        if not etude_id:
            print("ERREUR: etude_id requis")
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
        etude_id: str = None,
        statut: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Récupère les dossiers d'une étude."""
        if self._offline:
            return []

        etude_id = etude_id or self._etude_id
        if not etude_id:
            print("ERREUR: etude_id requis")
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
        numero: str,
        type_acte: str,
        parties: List[Dict] = None,
        donnees_metier: Dict = None,
        etude_id: str = None
    ) -> Optional[str]:
        """
        Crée un nouveau dossier.

        Args:
            numero: Numéro du dossier (ex: "VTE-2026-001")
            type_acte: Type d'acte (vente, promesse, etc.)
            parties: Liste des parties [{client_id, role}]
            donnees_metier: Données métier du dossier
            etude_id: ID de l'étude (optionnel, utilise celui de la clé API)

        Returns:
            ID du dossier créé ou None
        """
        if self._offline:
            return None

        etude_id = etude_id or self._etude_id
        if not etude_id:
            print("ERREUR: etude_id requis")
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
        """Enregistre une action dans les logs d'audit.

        Si Supabase est indisponible, ecrit dans un fichier local de fallback
        pour ne jamais perdre de logs de securite.
        """
        log_entry = {
            "action": action,
            "resource_type": resource_type,
            "etude_id": etude_id,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if self._offline:
            self._write_local_audit_log(log_entry)
            return

        try:
            self.client.table("audit_logs").insert({
                "action": action,
                "resource_type": resource_type,
                "etude_id": etude_id,
                "resource_id": resource_id,
                "details": details or {}
            }).execute()
        except Exception as e:
            # Fallback: ecrire en local pour ne jamais perdre un log de securite
            log_entry["supabase_error"] = str(e)
            self._write_local_audit_log(log_entry)
            print(f"[AUDIT] Echec Supabase, log sauvegarde localement: {action} {resource_type}")

    def _write_local_audit_log(self, entry: Dict) -> None:
        """Ecrit un log d'audit dans un fichier local de fallback."""
        try:
            log_dir = Path(__file__).parent.parent.parent / ".tmp" / "audit_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        except Exception:
            # Dernier recours: stderr pour ne jamais perdre silencieusement
            import sys
            print(f"[AUDIT CRITICAL] Impossible d'ecrire le log: {entry}", file=sys.stderr)


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Test AgentDB - Multi-tenant")
    print("=" * 60)

    print(f"\nSUPABASE_URL: {os.getenv('SUPABASE_URL', 'NON CONFIGURÉ')}")
    print(f"NOTAIRE_API_KEY: {'Configuré' if os.getenv('NOTAIRE_API_KEY') else 'Non configuré'}")
    print(f"NOTAIRE_ETUDE_ID: {os.getenv('NOTAIRE_ETUDE_ID', 'Non configuré')}")

    db = AgentDB()

    print(f"\nConnecté: {db.is_connected}")
    print(f"Étude ID: {db.etude_id or 'Non défini'}")
    print(f"Permissions: {db.permissions}")

    if db.is_connected:
        if db.etude_id:
            # Test avec étude spécifique
            print(f"\n--- Test avec étude {db.etude_id} ---")
            dossiers = db.get_all_dossiers(limit=5)
            print(f"Dossiers trouvés: {len(dossiers)}")

            clients = db.get_all_clients(limit=5)
            print(f"Clients trouvés: {len(clients)}")
        else:
            # Mode admin - liste toutes les études
            print("\n--- Mode Admin (pas de clé API) ---")
            etudes = db.get_all_etudes()
            print(f"Études trouvées: {len(etudes)}")
            for etude in etudes[:3]:
                print(f"  - {etude['nom']} ({etude['id'][:8]}...)")

        print("\n✓ AgentDB prêt pour la production!")
    else:
        print("\n⚠ Mode offline - configurez les variables d'environnement")
        print("  Option 1: NOTAIRE_API_KEY=nai_xxx...")
        print("  Option 2: SUPABASE_URL + SUPABASE_SERVICE_KEY + NOTAIRE_ETUDE_ID")
