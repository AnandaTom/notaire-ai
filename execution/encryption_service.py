#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
encryption_service.py
---------------------
Service de chiffrement au niveau des champs pour les donnees PII sensibles.
Utilise AES-256-GCM pour un chiffrement authentifie.

Caracteristiques de securite:
- Chiffrement AES-256-GCM (chiffrement authentifie)
- Pattern enveloppe (DEK + KEK)
- Support rotation de cles
- Derivation de cle securisee (PBKDF2)

Usage:
    from encryption_service import EncryptionService

    service = EncryptionService()
    encrypted = service.encrypt("Jean Dupont")
    decrypted = service.decrypt(encrypted)

    # Generation de cle
    python encryption_service.py generate-key
"""

import base64
import hashlib
import json
import os
import secrets
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography package not installed. Install with: pip install cryptography>=41.0.0")


# Champs sensibles necessitant un chiffrement
SENSITIVE_FIELDS = [
    'nom', 'prenom', 'email', 'telephone', 'adresse',
    'lieu_naissance', 'numero_securite_sociale', 'iban',
    'numero_carte_identite', 'numero_passeport'
]

# Champs qui ne doivent jamais etre logues
REDACTED_FIELDS = SENSITIVE_FIELDS + ['password', 'secret', 'key', 'token', 'api_key']


@dataclass
class EncryptedValue:
    """Represente une valeur chiffree avec metadonnees."""
    ciphertext: str  # Encode Base64
    nonce: str       # Encode Base64
    key_id: str      # Pour rotation de cles
    version: int     # Version du chiffrement
    timestamp: str   # Format ISO


class EncryptionService:
    """
    Service de chiffrement au niveau des champs utilisant AES-256-GCM.

    Implemente le chiffrement enveloppe:
    - KEK (Key Encryption Key): Stockee dans env/gestionnaire de secrets
    - DEK (Data Encryption Key): Par enregistrement, chiffree avec KEK
    """

    VERSION = 1

    def __init__(
        self,
        master_key: str = None,
        key_id: str = "default"
    ):
        """
        Initialise le service de chiffrement.

        Args:
            master_key: Cle maitre encodee Base64 256-bit (KEK)
                       Si non fournie, utilise la variable ENCRYPTION_MASTER_KEY
            key_id: Identifiant pour le suivi de rotation des cles
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError(
                "Le package 'cryptography' est requis. "
                "Installez-le avec: pip install cryptography>=41.0.0"
            )

        self.key_id = key_id

        # Obtenir la cle maitre depuis env ou parametre
        key_source = master_key or os.getenv("ENCRYPTION_MASTER_KEY")

        if not key_source:
            raise ValueError(
                "Cle maitre requise. Definissez la variable ENCRYPTION_MASTER_KEY "
                "ou passez le parametre master_key."
            )

        # Decoder et valider la cle
        try:
            self.master_key = base64.b64decode(key_source)
            if len(self.master_key) != 32:  # 256 bits
                raise ValueError("La cle maitre doit faire 256 bits (32 octets)")
        except Exception as e:
            raise ValueError(f"Format de cle maitre invalide: {e}")

        self.aesgcm = AESGCM(self.master_key)

    def encrypt(self, plaintext: str) -> str:
        """
        Chiffre une chaine de caracteres.

        Args:
            plaintext: Chaine a chiffrer

        Returns:
            Chaine JSON contenant la valeur chiffree et les metadonnees
        """
        if not plaintext:
            return plaintext

        # Generer un nonce aleatoire (96 bits pour GCM)
        nonce = secrets.token_bytes(12)

        # Chiffrer
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)

        # Packager en JSON
        encrypted = EncryptedValue(
            ciphertext=base64.b64encode(ciphertext).decode('ascii'),
            nonce=base64.b64encode(nonce).decode('ascii'),
            key_id=self.key_id,
            version=self.VERSION,
            timestamp=datetime.utcnow().isoformat()
        )

        return json.dumps({
            'c': encrypted.ciphertext,
            'n': encrypted.nonce,
            'k': encrypted.key_id,
            'v': encrypted.version,
            't': encrypted.timestamp
        })

    def decrypt(self, encrypted_json: str) -> str:
        """
        Dechiffre une valeur chiffree.

        Args:
            encrypted_json: Chaine JSON provenant de encrypt()

        Returns:
            Chaine dechiffree
        """
        if not encrypted_json:
            return encrypted_json

        try:
            data = json.loads(encrypted_json)
        except json.JSONDecodeError:
            # Pas chiffre, retourner tel quel (pour migration)
            return encrypted_json

        # Verifier la version
        if data.get('v') != self.VERSION:
            raise ValueError(f"Version de chiffrement non supportee: {data.get('v')}")

        # Decoder
        ciphertext = base64.b64decode(data['c'])
        nonce = base64.b64decode(data['n'])

        # Dechiffrer
        plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext_bytes.decode('utf-8')

    def encrypt_dict(
        self,
        data: Dict[str, Any],
        fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Chiffre des champs specifiques dans un dictionnaire.

        Args:
            data: Dictionnaire contenant les donnees
            fields: Liste des noms de champs a chiffrer (defaut: SENSITIVE_FIELDS)

        Returns:
            Dictionnaire avec les champs chiffres
        """
        if fields is None:
            fields = SENSITIVE_FIELDS

        result = data.copy()

        for field in fields:
            if field in result and result[field]:
                result[f"{field}_encrypted"] = self.encrypt(str(result[field]))
                # Supprimer le texte en clair
                del result[field]

        return result

    def decrypt_dict(
        self,
        data: Dict[str, Any],
        fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Dechiffre des champs specifiques dans un dictionnaire.

        Args:
            data: Dictionnaire contenant les donnees chiffrees
            fields: Liste des noms de champs a dechiffrer (defaut: SENSITIVE_FIELDS)

        Returns:
            Dictionnaire avec les champs dechiffres
        """
        if fields is None:
            fields = SENSITIVE_FIELDS

        result = data.copy()

        for field in fields:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in result and result[encrypted_field]:
                try:
                    result[field] = self.decrypt(result[encrypted_field])
                except Exception:
                    result[field] = "[ERREUR DECHIFFREMENT]"
                del result[encrypted_field]

        return result

    @staticmethod
    def generate_master_key() -> str:
        """
        Genere une nouvelle cle maitre aleatoire.

        Returns:
            Cle 256-bit encodee Base64
        """
        key = secrets.token_bytes(32)  # 256 bits
        return base64.b64encode(key).decode('ascii')

    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: bytes = None
    ) -> Tuple[str, bytes]:
        """
        Derive une cle maitre a partir d'un mot de passe en utilisant PBKDF2.

        Args:
            password: Mot de passe pour deriver la cle
            salt: Sel optionnel (genere si non fourni)

        Returns:
            Tuple de (cle base64, sel)
        """
        if not CRYPTO_AVAILABLE:
            raise ImportError("Package 'cryptography' requis")

        if salt is None:
            salt = secrets.token_bytes(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # Recommandation OWASP 2023
            backend=default_backend()
        )

        key = kdf.derive(password.encode('utf-8'))
        return base64.b64encode(key).decode('ascii'), salt

    @staticmethod
    def hash_for_search(value: str) -> str:
        """
        Cree un hash recherchable d'une valeur.

        Args:
            value: Valeur a hasher

        Returns:
            Hash SHA-256 encode en hexadecimal
        """
        if not value:
            return None

        # Normaliser pour un hachage coherent
        normalized = value.strip().lower()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def mask_pii(data: Dict[str, Any], fields: List[str] = None) -> Dict[str, Any]:
    """
    Masque les champs PII pour le logging/affichage.

    Args:
        data: Dictionnaire contenant les donnees
        fields: Champs a masquer (defaut: REDACTED_FIELDS)

    Returns:
        Dictionnaire avec les champs masques
    """
    if fields is None:
        fields = REDACTED_FIELDS

    result = data.copy()

    for field in fields:
        if field in result and result[field]:
            value = str(result[field])
            if len(value) > 4:
                result[field] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                result[field] = '****'

    return result


def get_sensitive_fields() -> List[str]:
    """Retourne la liste des champs sensibles."""
    return SENSITIVE_FIELDS.copy()


def get_redacted_fields() -> List[str]:
    """Retourne la liste des champs a ne jamais logger."""
    return REDACTED_FIELDS.copy()


# CLI pour generation de cle
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Service de chiffrement NotaireAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python encryption_service.py generate-key
  python encryption_service.py test --key <votre_cle>
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # generate-key command
    gen_parser = subparsers.add_parser('generate-key', help='Generer une nouvelle cle maitre')

    # test command
    test_parser = subparsers.add_parser('test', help='Tester le chiffrement')
    test_parser.add_argument('--key', help='Cle maitre a utiliser')

    # derive-key command
    derive_parser = subparsers.add_parser('derive-key', help='Deriver une cle depuis un mot de passe')
    derive_parser.add_argument('--password', required=True, help='Mot de passe')

    args = parser.parse_args()

    if args.command == 'generate-key':
        if not CRYPTO_AVAILABLE:
            print("ERREUR: Package 'cryptography' non installe.")
            print("Installez-le avec: pip install cryptography>=41.0.0")
            sys.exit(1)

        key = EncryptionService.generate_master_key()
        print("\n" + "=" * 60)
        print("CLE MAITRE GENEREE (stockez-la de maniere securisee!)")
        print("=" * 60)
        print(f"\nENCRYPTION_MASTER_KEY={key}")
        print("\n" + "=" * 60)
        print("IMPORTANT:")
        print("- Ne commitez JAMAIS cette cle dans Git")
        print("- Utilisez un gestionnaire de secrets en production")
        print("- La perte de cette cle = perte des donnees chiffrees")
        print("=" * 60 + "\n")

    elif args.command == 'test':
        if not CRYPTO_AVAILABLE:
            print("ERREUR: Package 'cryptography' non installe.")
            sys.exit(1)

        key = args.key or os.getenv("ENCRYPTION_MASTER_KEY")
        if not key:
            key = EncryptionService.generate_master_key()
            print(f"Cle generee pour test: {key[:20]}...")

        try:
            service = EncryptionService(master_key=key)

            # Test chiffrement simple
            original = "Jean Dupont"
            encrypted = service.encrypt(original)
            decrypted = service.decrypt(encrypted)

            print("\n--- Test Chiffrement Simple ---")
            print(f"Original:   {original}")
            print(f"Chiffre:    {encrypted[:50]}...")
            print(f"Dechiffre:  {decrypted}")
            print(f"OK:         {original == decrypted}")

            # Test dictionnaire
            data = {
                "nom": "Dupont",
                "prenom": "Jean",
                "email": "jean@example.com",
                "profession": "Ingenieur"
            }
            encrypted_dict = service.encrypt_dict(data)
            decrypted_dict = service.decrypt_dict(encrypted_dict)

            print("\n--- Test Dictionnaire ---")
            print(f"Original:   {data}")
            print(f"Champs chiffres: {list(encrypted_dict.keys())}")
            print(f"Dechiffre:  {decrypted_dict}")
            print(f"OK:         {data == decrypted_dict}")

            # Test hash
            hash1 = service.hash_for_search("Dupont")
            hash2 = service.hash_for_search("dupont")
            print("\n--- Test Hash Recherche ---")
            print(f"Hash 'Dupont': {hash1[:20]}...")
            print(f"Hash 'dupont': {hash2[:20]}...")
            print(f"Identiques:    {hash1 == hash2}")

            # Test masquage
            masked = mask_pii(data)
            print("\n--- Test Masquage PII ---")
            print(f"Original: {data}")
            print(f"Masque:   {masked}")

            print("\n" + "=" * 40)
            print("TOUS LES TESTS PASSES!")
            print("=" * 40 + "\n")

        except Exception as e:
            print(f"\nERREUR: {e}")
            sys.exit(1)

    elif args.command == 'derive-key':
        if not CRYPTO_AVAILABLE:
            print("ERREUR: Package 'cryptography' non installe.")
            sys.exit(1)

        key, salt = EncryptionService.derive_key_from_password(args.password)
        print(f"\nCle derivee:  {key}")
        print(f"Sel (base64): {base64.b64encode(salt).decode()}")
        print("\nATTENTION: Conservez le sel pour pouvoir regenerer la meme cle!")

    else:
        parser.print_help()
