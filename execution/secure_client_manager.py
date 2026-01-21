#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
secure_client_manager.py
------------------------
Gestion securisee des donnees clients avec chiffrement et conformite RGPD.
Etend historique_supabase.py avec:
- Chiffrement au niveau des champs pour les PII
- Gestion des droits RGPD
- Soft delete avec anonymisation
- Isolation multi-tenant
- Journalisation d'audit complete

Usage:
    from secure_client_manager import SecureClientManager

    manager = SecureClientManager(etude_id="...")
    manager.create_client({"nom": "Dupont", "prenom": "Jean", ...})
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import encryption service
from encryption_service import (
    EncryptionService,
    SENSITIVE_FIELDS,
    mask_pii,
    CRYPTO_AVAILABLE
)

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None
    Client = None

# Try to import Rich for console output
try:
    from rich.console import Console
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            # Remove rich markup
            text = str(args[0]) if args else ""
            text = re.sub(r'\[.*?\]', '', text)
            print(text)
    console = Console()


@dataclass
class ClientData:
    """Represente un client avec PII dechiffre."""
    id: Optional[str] = None
    etude_id: str = ""

    # Champs chiffres (stockes chiffres, retournes dechiffres)
    nom: str = ""
    prenom: str = ""
    email: str = ""
    telephone: str = ""
    adresse: str = ""

    # Champs non-sensibles
    type_personne: str = "physique"
    civilite: str = ""
    date_naissance: str = ""
    lieu_naissance: str = ""
    nationalite: str = ""
    profession: str = ""
    situation_matrimoniale: str = ""

    # GenApi sync
    genapi_id: str = ""
    last_genapi_sync: str = ""

    # Metadata
    source: str = "manual"
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""

    # Enrichissements IA
    ai_enrichments: Dict = field(default_factory=dict)
    ai_summary: str = ""

    # RGPD
    deleted_at: str = ""
    anonymized: bool = False


@dataclass
class GDPRRequestData:
    """Represente une demande de droits RGPD."""
    id: Optional[str] = None
    client_id: str = ""
    etude_id: str = ""
    request_type: str = ""  # access, rectification, erasure, portability, opposition
    status: str = "pending"
    requested_at: str = ""
    completed_at: str = ""
    deadline_at: str = ""
    requested_by: str = ""
    processed_by: str = ""
    response_data: Dict = None
    rejection_reason: str = ""


class SecureClientManager:
    """
    Gestion securisee des clients avec chiffrement et conformite RGPD.
    """

    # Patterns pour detection de donnees sensibles
    SENSITIVE_PATTERNS = {
        'nir': r'\b[1-2]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b',
        'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b',
        'carte_bancaire': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'medical': r'\b(cancer|vih|sida|depression|traitement|medic)\b'
    }

    def __init__(
        self,
        etude_id: str,
        user_id: str = None,
        encryption_key: str = None
    ):
        """
        Initialise le gestionnaire de clients securise.

        Args:
            etude_id: UUID de l'etude (pour isolation multi-tenant)
            user_id: UUID de l'utilisateur courant (pour audit)
            encryption_key: Cle de chiffrement optionnelle
        """
        self.etude_id = etude_id
        self.user_id = user_id or os.getenv("AGENT_USER_ID", "system")

        # Initialiser le chiffrement
        if CRYPTO_AVAILABLE:
            try:
                self.encryption = EncryptionService(master_key=encryption_key)
                self._encryption_enabled = True
            except ValueError as e:
                console.print(f"[yellow]Chiffrement desactive: {e}[/yellow]")
                self._encryption_enabled = False
                self.encryption = None
        else:
            console.print("[yellow]Package cryptography non installe. Chiffrement desactive.[/yellow]")
            self._encryption_enabled = False
            self.encryption = None

        # Initialiser le client Supabase
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

        self._offline_mode = False
        self._offline_storage: Dict[str, Dict] = {}

        if not SUPABASE_AVAILABLE:
            console.print("[yellow]Package supabase non installe. Mode offline.[/yellow]")
            self._offline_mode = True
        elif not self.url or not self.key:
            console.print("[yellow]Supabase non configure. Mode offline.[/yellow]")
            self._offline_mode = True
        else:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                console.print(f"[red]Erreur connexion Supabase: {e}[/red]")
                self._offline_mode = True

    # =========================================================================
    # CRUD CLIENTS AVEC CHIFFREMENT
    # =========================================================================

    def create_client(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Cree un nouveau client avec PII chiffre.

        Args:
            data: Dictionnaire des donnees client

        Returns:
            ID du client ou None si erreur
        """
        # Verifier les donnees sensibles
        warnings = self._scan_sensitive_data(json.dumps(data))
        if warnings:
            console.print(f"[yellow]Donnees sensibles detectees: {warnings}[/yellow]")

        # Chiffrer les champs sensibles
        encrypted_data = self._encrypt_client_data(data)

        # Ajouter metadata
        encrypted_data.update({
            "etude_id": self.etude_id,
            "created_by": self.user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "source": data.get("source", "manual")
        })

        # Generer le hash pour recherche
        if 'nom' in data and data['nom']:
            encrypted_data["nom_hash"] = self._hash_for_search(data['nom'])

        if self._offline_mode:
            client_id = str(uuid4())
            self._offline_storage[client_id] = encrypted_data
            console.print(f"[green]Client cree (offline): {client_id}[/green]")
            return client_id

        try:
            result = self.client.table("clients").insert(encrypted_data).execute()

            if result.data:
                client_id = result.data[0]["id"]
                self._log_audit("create", "client", client_id, {
                    "fields": list(data.keys())
                })
                console.print(f"[green]Client cree: {client_id}[/green]")
                return client_id

            return None

        except Exception as e:
            console.print(f"[red]Erreur creation client: {e}[/red]")
            return None

    def get_client(self, client_id: str) -> Optional[ClientData]:
        """
        Recupere un client par ID avec PII dechiffre.

        Args:
            client_id: UUID du client

        Returns:
            Objet ClientData ou None
        """
        if self._offline_mode:
            data = self._offline_storage.get(client_id)
            if data:
                return self._to_client_object(data)
            return None

        try:
            result = self.client.table("clients")\
                .select("*")\
                .eq("id", client_id)\
                .eq("etude_id", self.etude_id)\
                .is_("deleted_at", "null")\
                .single()\
                .execute()

            if result.data:
                self._log_audit("read", "client", client_id, {
                    "fields_accessed": SENSITIVE_FIELDS
                })
                return self._to_client_object(result.data)

            return None

        except Exception as e:
            console.print(f"[red]Erreur lecture client: {e}[/red]")
            return None

    def update_client(self, client_id: str, data: Dict[str, Any]) -> bool:
        """
        Met a jour un client avec PII chiffre.

        Args:
            client_id: UUID du client
            data: Champs a mettre a jour

        Returns:
            True si mis a jour
        """
        # Chiffrer les champs sensibles
        encrypted_data = self._encrypt_client_data(data)
        encrypted_data["updated_at"] = datetime.utcnow().isoformat()

        # Mettre a jour le hash si nom change
        if 'nom' in data and data['nom']:
            encrypted_data["nom_hash"] = self._hash_for_search(data['nom'])

        if self._offline_mode:
            if client_id in self._offline_storage:
                self._offline_storage[client_id].update(encrypted_data)
                return True
            return False

        try:
            result = self.client.table("clients")\
                .update(encrypted_data)\
                .eq("id", client_id)\
                .eq("etude_id", self.etude_id)\
                .execute()

            if result.data:
                self._log_audit("update", "client", client_id, {
                    "fields_updated": list(data.keys())
                })
                return True

            return False

        except Exception as e:
            console.print(f"[red]Erreur mise a jour client: {e}[/red]")
            return False

    def search_clients(
        self,
        nom: str = None,
        limit: int = 50
    ) -> List[ClientData]:
        """
        Recherche des clients par champs hashes.

        Args:
            nom: Nom a rechercher (sera hashe)
            limit: Nombre max de resultats

        Returns:
            Liste des clients correspondants
        """
        if self._offline_mode:
            results = []
            for client_id, data in list(self._offline_storage.items())[:limit]:
                if nom:
                    nom_hash = self._hash_for_search(nom)
                    if data.get("nom_hash") == nom_hash:
                        data_with_id = {**data, "id": client_id}
                        results.append(self._to_client_object(data_with_id))
                else:
                    data_with_id = {**data, "id": client_id}
                    results.append(self._to_client_object(data_with_id))
            return results

        try:
            query = self.client.table("clients")\
                .select("*")\
                .eq("etude_id", self.etude_id)\
                .is_("deleted_at", "null")\
                .eq("anonymized", False)

            if nom:
                nom_hash = self._hash_for_search(nom)
                query = query.eq("nom_hash", nom_hash)

            result = query.limit(limit).execute()

            self._log_audit("search", "client", None, {
                "search_params": mask_pii({"nom": nom}),
                "results_count": len(result.data) if result.data else 0
            })

            return [self._to_client_object(row) for row in (result.data or [])]

        except Exception as e:
            console.print(f"[red]Erreur recherche clients: {e}[/red]")
            return []

    def list_clients(self, limit: int = 100, offset: int = 0) -> List[ClientData]:
        """
        Liste les clients de l'etude.

        Args:
            limit: Nombre max de resultats
            offset: Offset pour pagination

        Returns:
            Liste des clients
        """
        if self._offline_mode:
            clients = list(self._offline_storage.items())[offset:offset + limit]
            return [self._to_client_object({**data, "id": cid}) for cid, data in clients]

        try:
            result = self.client.table("clients")\
                .select("*")\
                .eq("etude_id", self.etude_id)\
                .is_("deleted_at", "null")\
                .eq("anonymized", False)\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            return [self._to_client_object(row) for row in (result.data or [])]

        except Exception as e:
            console.print(f"[red]Erreur liste clients: {e}[/red]")
            return []

    # =========================================================================
    # GESTION DES DROITS RGPD
    # =========================================================================

    def handle_gdpr_request(
        self,
        client_id: str,
        request_type: str,
        requested_by: str
    ) -> Dict[str, Any]:
        """
        Traite une demande de droits RGPD.

        Args:
            client_id: UUID du client
            request_type: 'access', 'rectification', 'erasure', 'portability', 'opposition'
            requested_by: Email du demandeur

        Returns:
            Dictionnaire avec statut et donnees
        """
        valid_types = ['access', 'rectification', 'erasure', 'portability', 'opposition']
        if request_type not in valid_types:
            return {"error": f"Type de demande invalide. Valides: {valid_types}"}

        # Enregistrer la demande
        request_id = self._create_gdpr_request(client_id, request_type, requested_by)

        if request_type == 'access':
            return self._handle_access_request(client_id, request_id)
        elif request_type == 'erasure':
            return self._handle_erasure_request(client_id, request_id)
        elif request_type == 'portability':
            return self._handle_portability_request(client_id, request_id)
        elif request_type == 'opposition':
            return self._handle_opposition_request(client_id, request_id)
        elif request_type == 'rectification':
            return {
                "status": "pending",
                "request_id": request_id,
                "message": "Les demandes de rectification necessitent un traitement manuel"
            }

        return {"error": "Type de demande inconnu"}

    def _handle_access_request(self, client_id: str, request_id: str) -> Dict:
        """Fournit toutes les donnees d'un client (RGPD Art. 15)."""
        client = self.get_client(client_id)
        if not client:
            return {"error": "Client non trouve"}

        # Recuperer toutes les donnees liees
        client_data = asdict(client)

        # Recuperer les dossiers
        dossiers = self._get_client_dossiers(client_id)

        # Recuperer l'historique d'audit
        audit = self._get_client_audit(client_id)

        response = {
            "status": "completed",
            "request_id": request_id,
            "gdpr_article": "Art. 15 - Droit d'acces",
            "data": {
                "client": client_data,
                "dossiers": dossiers,
                "audit_trail": audit,
                "export_date": datetime.utcnow().isoformat()
            }
        }

        self._complete_gdpr_request(request_id, response)
        return response

    def _handle_erasure_request(self, client_id: str, request_id: str) -> Dict:
        """
        Anonymise les donnees client (RGPD Art. 17).
        Note: Soft delete + anonymisation, pas de suppression definitive.
        """
        # Verifier si l'effacement est autorise
        if self._is_under_legal_hold(client_id):
            self._complete_gdpr_request(request_id, {
                "status": "rejected",
                "reason": "Donnees sous obligation legale de conservation (Art. 17.3.b)"
            })
            return {
                "status": "rejected",
                "request_id": request_id,
                "reason": "Donnees sous obligation legale de conservation (Art. 17.3.b RGPD)"
            }

        # Anonymiser
        if self._anonymize_client(client_id):
            self._complete_gdpr_request(request_id, {"status": "completed"})
            return {
                "status": "completed",
                "request_id": request_id,
                "message": "Les donnees client ont ete anonymisees"
            }

        return {"error": "Echec de l'anonymisation"}

    def _handle_portability_request(self, client_id: str, request_id: str) -> Dict:
        """Exporte les donnees client en format lisible (RGPD Art. 20)."""
        client = self.get_client(client_id)
        if not client:
            return {"error": "Client non trouve"}

        export_data = {
            "format": "JSON",
            "version": "1.0",
            "gdpr_article": "Art. 20 - Droit a la portabilite",
            "export_date": datetime.utcnow().isoformat(),
            "client": asdict(client),
            "dossiers": self._get_client_dossiers(client_id)
        }

        self._complete_gdpr_request(request_id, {"status": "completed"})

        return {
            "status": "completed",
            "request_id": request_id,
            "data": export_data,
            "content_type": "application/json"
        }

    def _handle_opposition_request(self, client_id: str, request_id: str) -> Dict:
        """Marque le client comme opt-out du traitement IA (RGPD Art. 21)."""
        update_result = self.update_client(client_id, {
            "ai_enrichments": {
                "opt_out": True,
                "opt_out_date": datetime.utcnow().isoformat(),
                "opt_out_reason": "GDPR opposition request"
            }
        })

        if update_result:
            self._complete_gdpr_request(request_id, {"status": "completed"})
            return {
                "status": "completed",
                "request_id": request_id,
                "message": "Client exclu du traitement IA"
            }

        return {"error": "Echec du traitement de l'opposition"}

    def _anonymize_client(self, client_id: str) -> bool:
        """Anonymise les PII d'un client."""
        anonymized_data = {
            "nom_encrypted": "ANONYMISE" if not self._encryption_enabled else self.encryption.encrypt("ANONYMISE"),
            "prenom_encrypted": "ANONYMISE" if not self._encryption_enabled else self.encryption.encrypt("ANONYMISE"),
            "email_encrypted": None,
            "telephone_encrypted": None,
            "adresse_encrypted": None,
            "nom_hash": self._hash_for_search("ANONYMISE"),
            "genapi_id": None,
            "genapi_data": None,
            "ai_enrichments": {"anonymized_reason": "GDPR erasure request"},
            "ai_summary": None,
            "anonymized": True,
            "anonymized_at": datetime.utcnow().isoformat(),
            "deleted_at": datetime.utcnow().isoformat()
        }

        if self._offline_mode:
            if client_id in self._offline_storage:
                self._offline_storage[client_id].update(anonymized_data)
                return True
            return False

        try:
            result = self.client.table("clients")\
                .update(anonymized_data)\
                .eq("id", client_id)\
                .eq("etude_id", self.etude_id)\
                .execute()

            if result.data:
                self._log_audit("anonymize", "client", client_id, {
                    "reason": "GDPR erasure request"
                })
                return True

            return False

        except Exception as e:
            console.print(f"[red]Erreur anonymisation client: {e}[/red]")
            return False

    # =========================================================================
    # IMPORT (Approche 1: Import Manuel Securise)
    # =========================================================================

    def import_from_csv(
        self,
        file_path: str,
        mapping: Dict[str, List[str]] = None,
        source: str = "genapi_import"
    ) -> Dict[str, Any]:
        """
        Importe des clients depuis un CSV avec mapping automatique.

        Args:
            file_path: Chemin vers le fichier CSV
            mapping: Mapping optionnel des noms de colonnes
            source: Identifiant de la source

        Returns:
            Resultats d'import
        """
        import csv

        default_mapping = {
            'nom': ['nom', 'name', 'lastname', 'nom_client', 'NOM'],
            'prenom': ['prenom', 'firstname', 'prenom_client', 'PRENOM'],
            'email': ['email', 'mail', 'e-mail', 'courriel', 'EMAIL'],
            'telephone': ['telephone', 'tel', 'phone', 'portable', 'TELEPHONE'],
            'adresse': ['adresse', 'address', 'rue', 'ADRESSE'],
            'date_naissance': ['date_naissance', 'naissance', 'birth_date', 'DATE_NAISSANCE'],
            'lieu_naissance': ['lieu_naissance', 'birthplace', 'LIEU_NAISSANCE'],
            'nationalite': ['nationalite', 'nationality', 'NATIONALITE'],
            'profession': ['profession', 'job', 'PROFESSION'],
            'situation_matrimoniale': ['situation_matrimoniale', 'statut_marital', 'SITUATION_MATRIMONIALE']
        }

        results = {
            "total": 0,
            "imported": 0,
            "errors": [],
            "duplicates": 0,
            "warnings": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    results["total"] += 1

                    # Mapper les champs
                    client_data = self._map_import_row(row, mapping or default_mapping)
                    client_data["source"] = source

                    # Verifier les donnees sensibles
                    warnings = self._scan_sensitive_data(str(row))
                    if warnings:
                        results["warnings"].append({
                            "row": results["total"],
                            "warnings": warnings
                        })
                        # Continuer quand meme, mais logger

                    # Creer le client
                    client_id = self.create_client(client_data)

                    if client_id:
                        results["imported"] += 1
                    else:
                        results["duplicates"] += 1

            self._log_audit("import", "client", None, {
                "file": file_path,
                "results": results
            })

            console.print(f"[green]Import termine: {results['imported']}/{results['total']} clients[/green]")
            return results

        except FileNotFoundError:
            return {"error": f"Fichier non trouve: {file_path}"}
        except Exception as e:
            return {"error": str(e)}

    def _map_import_row(
        self,
        row: Dict,
        mapping: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Mappe une ligne d'import vers les champs client."""
        result = {}
        row_lower = {k.lower(): v for k, v in row.items()}

        for field, variants in mapping.items():
            for variant in variants:
                if variant.lower() in row_lower:
                    value = row_lower[variant.lower()]
                    if value and value.strip():
                        result[field] = value.strip()
                    break

        return result

    def _scan_sensitive_data(self, text: str) -> List[str]:
        """Detecte les donnees potentiellement sensibles."""
        warnings = []
        for name, pattern in self.SENSITIVE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(name)
        return warnings

    # =========================================================================
    # METHODES UTILITAIRES
    # =========================================================================

    def _encrypt_client_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Chiffre les champs sensibles des donnees client."""
        result = data.copy()

        if not self._encryption_enabled:
            # Sans chiffrement, juste renommer les champs
            for field in SENSITIVE_FIELDS:
                if field in result and result[field]:
                    result[f"{field}_encrypted"] = result[field]
                    del result[field]
            return result

        for field in SENSITIVE_FIELDS:
            if field in result and result[field]:
                result[f"{field}_encrypted"] = self.encryption.encrypt(str(result[field]))
                del result[field]

        return result

    def _decrypt_client_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Dechiffre les champs sensibles des donnees client."""
        result = data.copy()

        for field in SENSITIVE_FIELDS:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in result and result[encrypted_field]:
                try:
                    if self._encryption_enabled:
                        result[field] = self.encryption.decrypt(result[encrypted_field])
                    else:
                        result[field] = result[encrypted_field]
                except Exception:
                    result[field] = "[ERREUR DECHIFFREMENT]"
                del result[encrypted_field]

        return result

    def _hash_for_search(self, value: str) -> str:
        """Cree un hash recherchable."""
        if self._encryption_enabled:
            return self.encryption.hash_for_search(value)
        else:
            import hashlib
            normalized = value.strip().lower()
            return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def _to_client_object(self, data: Dict[str, Any]) -> ClientData:
        """Convertit une ligne DB en objet ClientData avec dechiffrement."""
        decrypted = self._decrypt_client_data(data)

        return ClientData(
            id=decrypted.get("id"),
            etude_id=decrypted.get("etude_id", ""),
            nom=decrypted.get("nom", ""),
            prenom=decrypted.get("prenom", ""),
            email=decrypted.get("email", ""),
            telephone=decrypted.get("telephone", ""),
            adresse=decrypted.get("adresse", ""),
            type_personne=decrypted.get("type_personne", "physique"),
            civilite=decrypted.get("civilite", ""),
            date_naissance=str(decrypted.get("date_naissance", "")),
            lieu_naissance=decrypted.get("lieu_naissance", ""),
            nationalite=decrypted.get("nationalite", ""),
            profession=decrypted.get("profession", ""),
            situation_matrimoniale=decrypted.get("situation_matrimoniale", ""),
            genapi_id=decrypted.get("genapi_id", ""),
            last_genapi_sync=str(decrypted.get("last_genapi_sync", "")),
            source=decrypted.get("source", ""),
            created_at=str(decrypted.get("created_at", "")),
            updated_at=str(decrypted.get("updated_at", "")),
            created_by=decrypted.get("created_by", ""),
            ai_enrichments=decrypted.get("ai_enrichments", {}),
            ai_summary=decrypted.get("ai_summary", ""),
            deleted_at=str(decrypted.get("deleted_at", "")),
            anonymized=decrypted.get("anonymized", False)
        )

    def _log_audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Dict = None
    ):
        """Enregistre un evenement d'audit."""
        if self._offline_mode:
            return

        try:
            self.client.table("audit_logs").insert({
                "user_id": self.user_id,
                "etude_id": self.etude_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {}
            }).execute()
        except Exception:
            pass  # Non-bloquant

    def _create_gdpr_request(
        self,
        client_id: str,
        request_type: str,
        requested_by: str
    ) -> str:
        """Cree un enregistrement de demande RGPD."""
        if self._offline_mode:
            return f"offline_gdpr_{datetime.utcnow().timestamp()}"

        try:
            result = self.client.table("rgpd_requests").insert({
                "client_id": client_id,
                "etude_id": self.etude_id,
                "request_type": request_type,
                "status": "processing",
                "requested_at": datetime.utcnow().isoformat(),
                "requested_by": requested_by,
                "processed_by": self.user_id
            }).execute()

            return result.data[0]["id"] if result.data else None
        except Exception:
            return None

    def _complete_gdpr_request(self, request_id: str, response: Dict):
        """Marque une demande RGPD comme terminee."""
        if self._offline_mode or not request_id:
            return

        try:
            self.client.table("rgpd_requests").update({
                "status": response.get("status", "completed"),
                "completed_at": datetime.utcnow().isoformat(),
                "response_data": response,
                "rejection_reason": response.get("reason")
            }).eq("id", request_id).execute()
        except Exception:
            pass

    def _get_client_dossiers(self, client_id: str) -> List[Dict]:
        """Recupere tous les dossiers impliquant un client."""
        if self._offline_mode:
            return []

        try:
            result = self.client.table("dossiers")\
                .select("*")\
                .eq("etude_id", self.etude_id)\
                .execute()

            # Filtrer ceux qui contiennent le client dans parties
            dossiers = []
            for d in (result.data or []):
                parties = d.get("parties", [])
                for p in parties:
                    if p.get("client_id") == client_id:
                        dossiers.append(d)
                        break

            return dossiers
        except Exception:
            return []

    def _get_client_audit(self, client_id: str) -> List[Dict]:
        """Recupere l'historique d'audit pour un client."""
        if self._offline_mode:
            return []

        try:
            result = self.client.table("audit_logs")\
                .select("action, created_at, details")\
                .eq("resource_type", "client")\
                .eq("resource_id", client_id)\
                .order("created_at", desc=True)\
                .limit(100)\
                .execute()

            return result.data or []
        except Exception:
            return []

    def _is_under_legal_hold(self, client_id: str) -> bool:
        """Verifie si les donnees client sont sous obligation legale."""
        dossiers = self._get_client_dossiers(client_id)

        for dossier in dossiers:
            if dossier.get("statut") in ["en_cours", "termine"]:
                return True

        return False


# CLI pour tests
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gestionnaire de clients securise")
    parser.add_argument("--etude", default="test-etude", help="ID de l'etude")
    parser.add_argument("--action", choices=["create", "list", "search", "import"],
                       default="list", help="Action a effectuer")
    parser.add_argument("--file", help="Fichier CSV pour import")
    parser.add_argument("--nom", help="Nom pour recherche")

    args = parser.parse_args()

    manager = SecureClientManager(etude_id=args.etude)

    if args.action == "create":
        client_id = manager.create_client({
            "nom": "Dupont",
            "prenom": "Jean",
            "email": "jean.dupont@example.com"
        })
        print(f"Client cree: {client_id}")

    elif args.action == "list":
        clients = manager.list_clients(limit=10)
        for c in clients:
            print(f"- {c.nom} {c.prenom} ({c.id})")

    elif args.action == "search":
        if args.nom:
            clients = manager.search_clients(nom=args.nom)
            for c in clients:
                print(f"- {c.nom} {c.prenom} ({c.id})")
        else:
            print("--nom requis pour la recherche")

    elif args.action == "import":
        if args.file:
            results = manager.import_from_csv(args.file)
            print(json.dumps(results, indent=2))
        else:
            print("--file requis pour l'import")
