#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_client_access.py
----------------------
Interface de haut niveau pour l'Agent IA pour acceder aux donnees clients.
Fournit la collecte conversationnelle et les requetes structurees.

Ce module fait le pont entre:
- Les interactions en langage naturel de l'Agent IA
- Les operations de base de donnees chiffrees et securisees
- La gestion des donnees conforme au RGPD

Usage:
    from agent_client_access import AgentClientAccess

    agent = AgentClientAccess(etude_id="...", conversation_id="...")

    # Collecte conversationnelle
    agent.collect_field("nom", "Dupont")
    agent.collect_field("prenom", "Jean")
    client_id = agent.save_collected_client()

    # Requetes structurees
    client = agent.get_client_for_dossier("D2024-001", "vendeur")
    variables = agent.get_variables_for_acte("D2024-001", "vente")
"""

import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import du gestionnaire de clients securise
from secure_client_manager import SecureClientManager, ClientData
from encryption_service import mask_pii

# Try to import Rich for console output
try:
    from rich.console import Console
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            text = str(args[0]) if args else ""
            text = re.sub(r'\[.*?\]', '', text)
            print(text)
    console = Console()


@dataclass
class CollectedData:
    """Contient les donnees collectees pendant une conversation."""
    client_data: Dict[str, Any] = field(default_factory=dict)
    dossier_data: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    collected_at: List[Dict] = field(default_factory=list)


@dataclass
class Question:
    """Represente une question a poser."""
    field: str
    question: str
    type: str  # text, email, phone, date, choice
    options: List[str] = field(default_factory=list)
    required: bool = True
    validation_pattern: str = ""


class AgentClientAccess:
    """
    Interface Agent pour l'acces securise aux donnees clients.

    Supporte deux approches:
    1. Collecte conversationnelle (Approche 2)
    2. Acces base sur import (Approche 1)
    """

    # Champs requis par contexte
    REQUIRED_FIELDS = {
        "vendeur": ["nom", "prenom", "adresse", "situation_matrimoniale"],
        "acquereur": ["nom", "prenom", "adresse", "situation_matrimoniale"],
        "promettant": ["nom", "prenom", "adresse"],
        "beneficiaire": ["nom", "prenom", "adresse"],
        "donateur": ["nom", "prenom", "adresse", "situation_matrimoniale"],
        "donataire": ["nom", "prenom", "adresse"],
        "basic": ["nom", "prenom"]
    }

    # Regles de validation
    VALIDATION_RULES = {
        "email": r"^[^@]+@[^@]+\.[^@]+$",
        "telephone": r"^[\d\s\+\-\.]+$",
        "date_naissance": r"^\d{4}-\d{2}-\d{2}$"
    }

    # Questions predefinies
    QUESTIONS = {
        "nom": Question(
            field="nom",
            question="Quel est le nom de famille du client ?",
            type="text",
            required=True
        ),
        "prenom": Question(
            field="prenom",
            question="Quel est le prenom du client ?",
            type="text",
            required=True
        ),
        "civilite": Question(
            field="civilite",
            question="Quelle est la civilite du client ?",
            type="choice",
            options=["Monsieur", "Madame", "Autre"],
            required=False
        ),
        "adresse": Question(
            field="adresse",
            question="Quelle est l'adresse complete du client ?",
            type="text_long",
            required=True
        ),
        "email": Question(
            field="email",
            question="Quelle est l'adresse email du client ?",
            type="email",
            required=False,
            validation_pattern=r"^[^@]+@[^@]+\.[^@]+$"
        ),
        "telephone": Question(
            field="telephone",
            question="Quel est le numero de telephone du client ?",
            type="phone",
            required=False,
            validation_pattern=r"^[\d\s\+\-\.]+$"
        ),
        "date_naissance": Question(
            field="date_naissance",
            question="Quelle est la date de naissance du client ? (AAAA-MM-JJ)",
            type="date",
            required=False,
            validation_pattern=r"^\d{4}-\d{2}-\d{2}$"
        ),
        "lieu_naissance": Question(
            field="lieu_naissance",
            question="Quel est le lieu de naissance du client ?",
            type="text",
            required=False
        ),
        "nationalite": Question(
            field="nationalite",
            question="Quelle est la nationalite du client ?",
            type="text",
            required=False
        ),
        "profession": Question(
            field="profession",
            question="Quelle est la profession du client ?",
            type="text",
            required=False
        ),
        "situation_matrimoniale": Question(
            field="situation_matrimoniale",
            question="Quelle est la situation matrimoniale du client ?",
            type="choice",
            options=["Celibataire", "Marie(e)", "Pacse(e)", "Divorce(e)", "Veuf(ve)"],
            required=True
        )
    }

    def __init__(
        self,
        etude_id: str,
        conversation_id: str = None,
        user_id: str = None
    ):
        """
        Initialise l'acces client pour l'agent.

        Args:
            etude_id: UUID de l'etude
            conversation_id: ID de conversation optionnel pour tracking
            user_id: UUID utilisateur optionnel (defaut: agent)
        """
        self.etude_id = etude_id
        self.conversation_id = conversation_id or f"conv_{uuid4().hex[:8]}"

        # Initialiser le gestionnaire de clients securise
        self.manager = SecureClientManager(
            etude_id=etude_id,
            user_id=user_id or os.getenv("AGENT_USER_ID", "agent")
        )

        # Collection en cours
        self._collected = CollectedData()
        self._current_client_id = None
        self._current_context = "basic"

    # =========================================================================
    # COLLECTE CONVERSATIONNELLE (Approche 2)
    # =========================================================================

    def start_collection(self, context: str = "basic") -> Dict[str, Any]:
        """
        Demarre une nouvelle collecte de donnees.

        Args:
            context: Contexte de collecte (vendeur, acquereur, basic, etc.)

        Returns:
            Premiere question a poser
        """
        self._collected = CollectedData()
        self._current_context = context
        self._current_client_id = None

        first_question = self.get_next_question()

        return {
            "status": "started",
            "context": context,
            "conversation_id": self.conversation_id,
            "next_question": asdict(first_question) if first_question else None
        }

    def collect_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """
        Collecte un champ depuis la conversation.

        Args:
            field_name: Nom du champ (ex: "nom", "prenom")
            value: Valeur saisie par l'utilisateur

        Returns:
            Resultat de validation: {"valid": bool, "error": str|None, "next_question": ...}
        """
        # Valider
        validation = self._validate_field(field_name, value)

        if validation["valid"]:
            self._collected.client_data[field_name] = value
            self._collected.collected_at.append({
                "field": field_name,
                "timestamp": datetime.utcnow().isoformat(),
                "conversation_id": self.conversation_id
            })
        else:
            self._collected.validation_errors.append(validation["error"])

        # Obtenir la prochaine question
        next_q = self.get_next_question()

        return {
            **validation,
            "next_question": asdict(next_q) if next_q else None,
            "is_complete": next_q is None
        }

    def get_missing_fields(self, context: str = None) -> List[str]:
        """
        Obtient la liste des champs requis manquants.

        Args:
            context: Contexte pour les champs requis

        Returns:
            Liste des noms de champs manquants
        """
        ctx = context or self._current_context
        required = self.REQUIRED_FIELDS.get(ctx, self.REQUIRED_FIELDS["basic"])
        collected = set(self._collected.client_data.keys())

        return [f for f in required if f not in collected]

    def get_next_question(self, context: str = None) -> Optional[Question]:
        """
        Obtient la prochaine question basee sur les champs manquants.

        Args:
            context: Contexte pour les champs requis

        Returns:
            Objet Question ou None si complet
        """
        missing = self.get_missing_fields(context)

        if not missing:
            return None

        field = missing[0]
        return self.QUESTIONS.get(field, Question(
            field=field,
            question=f"Quelle est la valeur pour {field} ?",
            type="text"
        ))

    def save_collected_client(self, source: str = "conversation") -> Optional[str]:
        """
        Sauvegarde les donnees collectees dans la base.

        Args:
            source: Identifiant de source

        Returns:
            ID du client ou None si validation echoue
        """
        # Verifier les champs requis
        missing = self.get_missing_fields("basic")
        if missing:
            console.print(f"[yellow]Champs requis manquants: {missing}[/yellow]")
            return None

        # Ajouter metadata
        self._collected.client_data["source"] = source
        self._collected.client_data["ai_enrichments"] = {
            "conversation_id": self.conversation_id,
            "collected_fields": self._collected.collected_at,
            "context": self._current_context
        }

        # Creer le client
        client_id = self.manager.create_client(self._collected.client_data)

        if client_id:
            self._current_client_id = client_id
            console.print(f"[green]Client sauvegarde: {client_id}[/green]")
            # Reset la collection
            self._collected = CollectedData()

        return client_id

    def get_collection_summary(self) -> Dict[str, Any]:
        """Obtient un resume des donnees collectees (PII masque pour affichage)."""
        return {
            "fields_collected": list(self._collected.client_data.keys()),
            "data_preview": mask_pii(self._collected.client_data),
            "validation_errors": self._collected.validation_errors,
            "is_complete": len(self.get_missing_fields("basic")) == 0,
            "context": self._current_context,
            "conversation_id": self.conversation_id
        }

    def cancel_collection(self) -> Dict[str, Any]:
        """Annule la collecte en cours."""
        collected_count = len(self._collected.client_data)
        self._collected = CollectedData()
        return {
            "status": "cancelled",
            "fields_discarded": collected_count
        }

    # =========================================================================
    # REQUETES STRUCTUREES
    # =========================================================================

    def get_client_by_id(self, client_id: str) -> Optional[ClientData]:
        """Recupere un client specifique par ID."""
        return self.manager.get_client(client_id)

    def search_clients(
        self,
        nom: str = None,
        limit: int = 10
    ) -> List[ClientData]:
        """Recherche des clients par nom."""
        return self.manager.search_clients(nom=nom, limit=limit)

    def get_client_for_dossier(
        self,
        dossier_numero: str,
        role: str
    ) -> Optional[ClientData]:
        """
        Recupere le client associe a un dossier dans un role specifique.

        Args:
            dossier_numero: Numero de reference du dossier
            role: Role dans le dossier ("vendeur", "acquereur", etc.)

        Returns:
            Objet ClientData ou None
        """
        if self.manager._offline_mode:
            return None

        try:
            # Recuperer le dossier
            result = self.manager.client.table("dossiers")\
                .select("parties")\
                .eq("numero", dossier_numero)\
                .eq("etude_id", self.etude_id)\
                .single()\
                .execute()

            if not result.data:
                return None

            # Trouver le client dans les parties
            parties = result.data.get("parties", [])
            for party in parties:
                if party.get("role") == role:
                    client_id = party.get("client_id")
                    if client_id:
                        return self.manager.get_client(client_id)

            return None

        except Exception as e:
            console.print(f"[red]Erreur recuperation client pour dossier: {e}[/red]")
            return None

    def get_variables_for_acte(
        self,
        dossier_numero: str,
        type_acte: str
    ) -> Dict[str, Any]:
        """
        Recupere toutes les variables necessaires pour un acte.

        Args:
            dossier_numero: Numero de reference du dossier
            type_acte: Type d'acte (vente, promesse, etc.)

        Returns:
            Dictionnaire des variables pour le remplissage du template
        """
        variables = {}

        # Definir les parties requises par type d'acte
        parties_config = {
            "vente": ["vendeur", "acquereur"],
            "promesse": ["promettant", "beneficiaire"],
            "donation": ["donateur", "donataire"],
            "succession": ["defunt", "heritier"],
            "reglement_copropriete": [],
            "modificatif_edd": []
        }

        required_parties = parties_config.get(type_acte, ["vendeur", "acquereur"])

        # Collecter les donnees client pour chaque partie
        for role in required_parties:
            client = self.get_client_for_dossier(dossier_numero, role)

            if client:
                variables[role] = self._client_to_variables(client, role)
            else:
                variables[role] = {"_missing": True, "_role": role}

        # Recuperer les donnees du dossier
        dossier_data = self._get_dossier_data(dossier_numero)
        variables["dossier"] = dossier_data

        # Ajouter metadata
        variables["_meta"] = {
            "type_acte": type_acte,
            "dossier_numero": dossier_numero,
            "generated_at": datetime.utcnow().isoformat(),
            "etude_id": self.etude_id
        }

        return variables

    def _client_to_variables(self, client: ClientData, role: str) -> Dict[str, Any]:
        """Convertit un objet ClientData en variables de template."""
        prefix = role.lower()

        # Variables avec prefix
        prefixed = {
            f"{prefix}_nom": client.nom,
            f"{prefix}_prenom": client.prenom,
            f"{prefix}_civilite": client.civilite,
            f"{prefix}_adresse": client.adresse,
            f"{prefix}_date_naissance": client.date_naissance,
            f"{prefix}_lieu_naissance": client.lieu_naissance,
            f"{prefix}_nationalite": client.nationalite,
            f"{prefix}_profession": client.profession,
            f"{prefix}_situation_matrimoniale": client.situation_matrimoniale,
        }

        # Structure imbriquee pour compatibilite templates existants
        nested = {
            "personne_physique": {
                "nom": client.nom,
                "prenom": client.prenom,
                "civilite": client.civilite,
                "adresse": client.adresse,
                "date_naissance": client.date_naissance,
                "lieu_naissance": client.lieu_naissance,
                "nationalite": client.nationalite,
                "profession": client.profession,
                "situation_matrimoniale": client.situation_matrimoniale,
            }
        }

        return {**prefixed, **nested, "_client_id": client.id}

    def _get_dossier_data(self, dossier_numero: str) -> Dict[str, Any]:
        """Recupere les metadonnees du dossier."""
        if self.manager._offline_mode:
            return {}

        try:
            result = self.manager.client.table("dossiers")\
                .select("*")\
                .eq("numero", dossier_numero)\
                .eq("etude_id", self.etude_id)\
                .single()\
                .execute()

            return result.data or {}

        except Exception:
            return {}

    # =========================================================================
    # GESTION DES DOSSIERS
    # =========================================================================

    def create_dossier(
        self,
        numero: str,
        type_acte: str,
        parties: List[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Cree un nouveau dossier.

        Args:
            numero: Numero de reference
            type_acte: Type d'acte
            parties: Liste de {client_id, role}

        Returns:
            ID du dossier ou None
        """
        if self.manager._offline_mode:
            dossier_id = f"offline_dossier_{uuid4().hex[:8]}"
            console.print(f"[green]Dossier cree (offline): {dossier_id}[/green]")
            return dossier_id

        try:
            result = self.manager.client.table("dossiers").insert({
                "etude_id": self.etude_id,
                "numero": numero,
                "type_acte": type_acte,
                "parties": parties or [],
                "created_by": self.manager.user_id
            }).execute()

            if result.data:
                dossier_id = result.data[0]["id"]
                self.manager._log_audit("create", "dossier", dossier_id, {
                    "numero": numero,
                    "type_acte": type_acte
                })
                console.print(f"[green]Dossier cree: {numero}[/green]")
                return dossier_id

            return None

        except Exception as e:
            console.print(f"[red]Erreur creation dossier: {e}[/red]")
            return None

    def link_client_to_dossier(
        self,
        dossier_id: str,
        client_id: str,
        role: str
    ) -> bool:
        """
        Lie un client a un dossier avec un role specifique.

        Args:
            dossier_id: UUID du dossier
            client_id: UUID du client
            role: Role dans le dossier

        Returns:
            True si lie avec succes
        """
        if self.manager._offline_mode:
            return True

        try:
            # Recuperer les parties actuelles
            result = self.manager.client.table("dossiers")\
                .select("parties")\
                .eq("id", dossier_id)\
                .single()\
                .execute()

            parties = result.data.get("parties", []) if result.data else []

            # Verifier si deja present
            for p in parties:
                if p.get("client_id") == client_id and p.get("role") == role:
                    console.print(f"[yellow]Client deja lie avec ce role[/yellow]")
                    return True

            # Ajouter la nouvelle partie
            parties.append({"client_id": client_id, "role": role})

            # Mettre a jour
            update_result = self.manager.client.table("dossiers")\
                .update({"parties": parties})\
                .eq("id", dossier_id)\
                .execute()

            if update_result.data:
                self.manager._log_audit("update", "dossier", dossier_id, {
                    "action": "link_client",
                    "client_id": client_id,
                    "role": role
                })
                return True

            return False

        except Exception as e:
            console.print(f"[red]Erreur liaison client: {e}[/red]")
            return False

    def get_dossier(self, numero: str) -> Optional[Dict[str, Any]]:
        """Recupere un dossier par son numero."""
        return self._get_dossier_data(numero)

    def list_dossiers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Liste les dossiers de l'etude."""
        if self.manager._offline_mode:
            return []

        try:
            result = self.manager.client.table("dossiers")\
                .select("*")\
                .eq("etude_id", self.etude_id)\
                .is_("deleted_at", "null")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            return result.data or []

        except Exception:
            return []

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def _validate_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """Valide une valeur de champ."""
        if not value or (isinstance(value, str) and not value.strip()):
            question = self.QUESTIONS.get(field_name)
            if question and question.required:
                return {"valid": False, "error": f"{field_name} est requis"}
            return {"valid": True, "error": None}  # Champ optionnel vide

        # Verifier le pattern de validation
        if field_name in self.VALIDATION_RULES:
            pattern = self.VALIDATION_RULES[field_name]
            if not re.match(pattern, str(value)):
                return {
                    "valid": False,
                    "error": f"Format de {field_name} invalide"
                }

        return {"valid": True, "error": None}

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def check_client_exists(self, nom: str, prenom: str = None) -> Optional[ClientData]:
        """
        Verifie si un client existe deja.

        Args:
            nom: Nom du client
            prenom: Prenom optionnel

        Returns:
            ClientData si trouve, None sinon
        """
        clients = self.search_clients(nom=nom, limit=10)

        if prenom:
            for c in clients:
                if c.prenom and c.prenom.lower() == prenom.lower():
                    return c

        return clients[0] if clients else None

    def get_or_create_client(
        self,
        nom: str,
        prenom: str = None,
        **extra_fields
    ) -> Optional[str]:
        """
        Recupere un client existant ou en cree un nouveau.

        Args:
            nom: Nom du client
            prenom: Prenom optionnel
            **extra_fields: Champs supplementaires

        Returns:
            ID du client
        """
        existing = self.check_client_exists(nom, prenom)
        if existing:
            console.print(f"[blue]Client existant trouve: {existing.id}[/blue]")
            return existing.id

        # Creer un nouveau client
        data = {"nom": nom, "source": "agent_ia"}
        if prenom:
            data["prenom"] = prenom
        data.update(extra_fields)

        return self.manager.create_client(data)


# CLI pour tests interactifs
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Interface Agent pour acces clients")
    parser.add_argument("--etude", default="test-etude", help="ID de l'etude")
    parser.add_argument("--action", choices=["collect", "search", "dossier", "variables"],
                       default="collect", help="Action a effectuer")
    parser.add_argument("--context", default="vendeur", help="Contexte de collecte")
    parser.add_argument("--nom", help="Nom pour recherche")
    parser.add_argument("--dossier", help="Numero de dossier")
    parser.add_argument("--type-acte", default="vente", help="Type d'acte")

    args = parser.parse_args()

    agent = AgentClientAccess(etude_id=args.etude)

    if args.action == "collect":
        # Demo de collecte interactive
        print(f"\n=== Collecte conversationnelle ({args.context}) ===\n")

        result = agent.start_collection(context=args.context)
        print(f"Conversation: {result['conversation_id']}")

        while True:
            question = agent.get_next_question()
            if not question:
                print("\n[Collecte complete!]")
                print(agent.get_collection_summary())

                save = input("\nSauvegarder? (o/n): ")
                if save.lower() == 'o':
                    client_id = agent.save_collected_client()
                    print(f"Client sauvegarde: {client_id}")
                break

            print(f"\n{question.question}")
            if question.options:
                for i, opt in enumerate(question.options, 1):
                    print(f"  {i}. {opt}")

            value = input("> ")

            if question.options and value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(question.options):
                    value = question.options[idx]

            result = agent.collect_field(question.field, value)

            if not result["valid"]:
                print(f"[Erreur: {result['error']}]")

    elif args.action == "search":
        if args.nom:
            clients = agent.search_clients(nom=args.nom)
            print(f"\n=== Resultats pour '{args.nom}' ===\n")
            for c in clients:
                print(f"- {c.nom} {c.prenom} ({c.id})")
        else:
            print("--nom requis pour la recherche")

    elif args.action == "dossier":
        if args.dossier:
            dossier = agent.get_dossier(args.dossier)
            print(f"\n=== Dossier {args.dossier} ===\n")
            print(json.dumps(dossier, indent=2, default=str))
        else:
            print("--dossier requis")

    elif args.action == "variables":
        if args.dossier:
            variables = agent.get_variables_for_acte(args.dossier, args.type_acte)
            print(f"\n=== Variables pour {args.type_acte} ({args.dossier}) ===\n")
            print(json.dumps(variables, indent=2, default=str))
        else:
            print("--dossier requis")
