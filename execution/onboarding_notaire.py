#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
onboarding_notaire.py
---------------------
Script d'onboarding automatique pour un nouveau notaire.

Ce script:
1. Crée une nouvelle étude dans Supabase
2. Génère une clé API sécurisée pour l'agent
3. Retourne les credentials à configurer

Usage:
    python execution/onboarding_notaire.py --nom "Maître Dupont" --siret "12345678901234"

    # Mode interactif
    python execution/onboarding_notaire.py
"""

import os
import sys
import json
import secrets
import hashlib
import argparse
from pathlib import Path
from datetime import datetime

# Encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Charge .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    # dotenv est optionnel : si non installé, on suppose que les variables d'environnement
    # nécessaires sont déjà définies dans l'environnement du processus.
    pass

# Import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("ERREUR: supabase non installé. Lancez: pip install supabase")
    sys.exit(1)


def generate_api_key() -> tuple[str, str, str]:
    """
    Génère une clé API sécurisée.

    Returns:
        tuple: (clé_complete, prefix, hash)
        - clé_complete: "nai_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" (à donner au client)
        - prefix: "xxxxxxxx" (8 chars pour identification)
        - hash: SHA256 de la clé (stocké en DB)
    """
    # Génère 32 bytes aléatoires = 64 chars hex
    random_part = secrets.token_hex(24)  # 48 chars

    # Format: nai_<prefix><rest>
    prefix = random_part[:8]
    full_key = f"nai_{random_part}"

    # Hash pour stockage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    return full_key, prefix, key_hash


def create_etude(client: Client, nom: str, siret: str = None,
                 email: str = None, adresse: str = None, telephone: str = None) -> dict:
    """
    Crée une nouvelle étude dans Supabase.

    Returns:
        dict: L'étude créée avec son ID
    """
    data = {
        "nom": nom,
        "siret": siret,
        "email_contact": email,
        "adresse": adresse,
        "telephone": telephone,
        "rgpd_consent": True,
        "dpa_signed_at": datetime.now().isoformat()
    }

    # Retire les None
    data = {k: v for k, v in data.items() if v is not None}

    result = client.table("etudes").insert(data).execute()

    if not result.data:
        raise Exception("Erreur création étude")

    return result.data[0]


def create_api_key(client: Client, etude_id: str, name: str = "Agent Principal") -> dict:
    """
    Crée une clé API pour une étude.

    Returns:
        dict: {
            "api_key": "nai_xxx..." (à donner au client - UNIQUE AFFICHAGE),
            "key_id": "uuid",
            "etude_id": "uuid"
        }
    """
    full_key, prefix, key_hash = generate_api_key()

    data = {
        "etude_id": etude_id,
        "name": name,
        "key_hash": key_hash,
        "key_prefix": prefix,
        "permissions": {"read": True, "write": True, "delete": False},
        "allowed_tables": ["clients", "dossiers"],
        "rate_limit_rpm": 60
    }

    result = client.table("agent_api_keys").insert(data).execute()

    if not result.data:
        raise Exception("Erreur création clé API")

    return {
        "api_key": full_key,  # NE SERA PLUS JAMAIS AFFICHÉ
        "key_id": result.data[0]["id"],
        "key_prefix": prefix,
        "etude_id": etude_id
    }


def onboard_notaire(nom: str, siret: str = None, email: str = None,
                    adresse: str = None, telephone: str = None) -> dict:
    """
    Processus complet d'onboarding d'un notaire.

    Returns:
        dict: Toutes les informations nécessaires pour configurer l'agent
    """
    # Connexion Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise Exception("Variables SUPABASE_URL et SUPABASE_SERVICE_KEY requises")

    client = create_client(url, key)

    # 1. Créer l'étude
    print(f"\n[1/3] Création de l'étude '{nom}'...")
    etude = create_etude(client, nom, siret, email, adresse, telephone)
    print(f"      Étude créée: {etude['id']}")

    # 2. Créer la clé API
    print(f"[2/3] Génération de la clé API...")
    api_key_info = create_api_key(client, etude["id"])
    print(f"      Clé créée: {api_key_info['key_prefix']}...")

    # 3. Préparer la config
    print(f"[3/3] Préparation de la configuration...")

    config = {
        "etude": {
            "id": etude["id"],
            "nom": etude["nom"],
            "siret": etude.get("siret")
        },
        "agent_config": {
            "NOTAIRE_API_KEY": api_key_info["api_key"],
            "NOTAIRE_ETUDE_ID": etude["id"],
            "SUPABASE_URL": url
        },
        "created_at": datetime.now().isoformat()
    }

    return config


def print_config(config: dict):
    """Affiche la configuration de manière lisible."""
    print("\n" + "=" * 60)
    print("  ONBOARDING TERMINÉ - CONFIGURATION AGENT")
    print("=" * 60)

    print(f"\n📋 Étude: {config['etude']['nom']}")
    print(f"   ID: {config['etude']['id']}")
    if config['etude'].get('siret'):
        print(f"   SIRET: {config['etude']['siret']}")

    print("\n🔑 Variables d'environnement pour l'agent:")
    print("-" * 60)
    for key, value in config['agent_config'].items():
        print(f"{key}={value}")
    print("-" * 60)

    print("\n⚠️  IMPORTANT:")
    print("   - La clé API ne sera PLUS JAMAIS affichée")
    print("   - Copiez-la maintenant dans le .env de l'agent")
    print("   - En cas de perte, générez une nouvelle clé")

    print("\n" + "=" * 60)


def interactive_mode():
    """Mode interactif pour collecter les informations."""
    print("\n" + "=" * 60)
    print("  ONBOARDING NOUVEAU NOTAIRE")
    print("=" * 60)

    print("\nEntrez les informations du notaire:\n")

    nom = input("Nom de l'étude (ex: Maître Dupont - Paris): ").strip()
    if not nom:
        print("ERREUR: Le nom est obligatoire")
        sys.exit(1)

    siret = input("SIRET (optionnel): ").strip() or None
    email = input("Email contact (optionnel): ").strip() or None
    adresse = input("Adresse (optionnel): ").strip() or None
    telephone = input("Téléphone (optionnel): ").strip() or None

    return nom, siret, email, adresse, telephone


def main():
    parser = argparse.ArgumentParser(description="Onboarding nouveau notaire")
    parser.add_argument("--nom", help="Nom de l'étude")
    parser.add_argument("--siret", help="SIRET de l'étude")
    parser.add_argument("--email", help="Email de contact")
    parser.add_argument("--adresse", help="Adresse")
    parser.add_argument("--telephone", help="Téléphone")
    parser.add_argument("--output", help="Fichier JSON de sortie (optionnel)")

    args = parser.parse_args()

    # Mode interactif ou ligne de commande
    if args.nom:
        nom = args.nom
        siret = args.siret
        email = args.email
        adresse = args.adresse
        telephone = args.telephone
    else:
        nom, siret, email, adresse, telephone = interactive_mode()

    try:
        # Exécuter l'onboarding
        config = onboard_notaire(nom, siret, email, adresse, telephone)

        # Afficher
        print_config(config)

        # Sauvegarder si demandé
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
            print(f"\n📁 Configuration sauvegardée: {output_path}")

        return 0

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
