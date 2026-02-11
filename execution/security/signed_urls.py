"""
Module de signature d'URLs pour téléchargement sécurisé.

Sécurité:
- HMAC-SHA256 avec clé secrète
- Expiration automatique (1h par défaut)
- Comparaison timing-safe contre attaques temporelles
- Logging pour audit

RGPD: Les URLs signées garantissent que seul le destinataire légitime
peut télécharger les documents notariaux sensibles.
"""

import hmac
import hashlib
import time
import os
import logging
from urllib.parse import urlencode, parse_qs, urlparse
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Clé secrète pour signer les URLs (32 bytes minimum recommandé)
# IMPORTANT: En production, cette clé DOIT être définie dans les secrets Modal
SIGNING_KEY = os.getenv("URL_SIGNING_KEY")

if not SIGNING_KEY:
    logger.warning(
        "URL_SIGNING_KEY non définie! Utilisation d'une clé temporaire. "
        "CRITIQUE: Définir URL_SIGNING_KEY dans les secrets Modal pour la production."
    )
    # Clé temporaire pour dev uniquement - NE PAS utiliser en prod
    SIGNING_KEY = "dev_only_key_change_in_production_immediately"


def _get_signing_key() -> bytes:
    """Retourne la clé de signature en bytes."""
    key = SIGNING_KEY
    if isinstance(key, str):
        return key.encode('utf-8')
    return key


def generate_signed_url(filename: str, expires_in: int = 3600) -> str:
    """
    Génère une URL signée pour télécharger un fichier.

    Args:
        filename: Nom du fichier à télécharger (sans chemin)
        expires_in: Durée de validité en secondes (défaut: 1 heure)

    Returns:
        URL relative signée: /download/{filename}?token=xxx&expires=yyy

    Security:
        - Token HMAC-SHA256 de "{filename}:{expires}"
        - Expiration incluse dans la signature (anti-tampering)
    """
    if not filename:
        raise ValueError("filename ne peut pas être vide")

    # Calculer timestamp d'expiration
    expires = int(time.time()) + expires_in

    # Message à signer: filename + timestamp
    message = f"{filename}:{expires}"

    # Signature HMAC-SHA256
    signature = hmac.new(
        _get_signing_key(),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Construire l'URL avec paramètres
    params = urlencode({
        "token": signature,
        "expires": expires
    })

    signed_url = f"/download/{filename}?{params}"

    logger.info(f"[SIGNED_URL] Générée pour {filename}, expire dans {expires_in}s")

    return signed_url


def verify_signed_url(filename: str, token: str, expires: int) -> Tuple[bool, str]:
    """
    Vérifie la validité d'une URL signée.

    Args:
        filename: Nom du fichier demandé
        token: Signature fournie dans l'URL
        expires: Timestamp d'expiration fourni

    Returns:
        Tuple (is_valid, error_message)
        - (True, "") si valide
        - (False, "raison") si invalide

    Security:
        - Vérifie expiration AVANT signature (fail fast)
        - Comparaison timing-safe avec hmac.compare_digest()
        - Logging pour audit de sécurité
    """
    # 1. Vérifier expiration d'abord (fail fast, évite calcul HMAC inutile)
    current_time = int(time.time())
    if current_time > expires:
        time_expired = current_time - expires
        logger.warning(
            f"[SIGNED_URL] REJETÉ: Lien expiré pour {filename} "
            f"(expiré depuis {time_expired}s)"
        )
        return False, "Lien expiré. Veuillez régénérer le document."

    # 2. Recalculer la signature attendue
    message = f"{filename}:{expires}"
    expected_signature = hmac.new(
        _get_signing_key(),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 3. Comparaison timing-safe (protection contre timing attacks)
    if not hmac.compare_digest(token, expected_signature):
        logger.warning(
            f"[SIGNED_URL] REJETÉ: Signature invalide pour {filename}"
        )
        return False, "Lien invalide. Veuillez régénérer le document."

    # 4. Succès
    time_remaining = expires - current_time
    logger.info(
        f"[SIGNED_URL] VALIDÉ: {filename} "
        f"(expire dans {time_remaining}s)"
    )
    return True, ""


def extract_params_from_url(url: str) -> Optional[Tuple[str, str, int]]:
    """
    Extrait les paramètres d'une URL signée.

    Args:
        url: URL complète ou relative (ex: /download/file.docx?token=xxx&expires=123)

    Returns:
        Tuple (filename, token, expires) ou None si format invalide
    """
    try:
        parsed = urlparse(url)

        # Extraire filename du path
        path = parsed.path
        if path.startswith("/download/"):
            filename = path[len("/download/"):]
        else:
            return None

        # Extraire query params
        params = parse_qs(parsed.query)
        token = params.get("token", [None])[0]
        expires_str = params.get("expires", [None])[0]

        if not token or not expires_str:
            return None

        expires = int(expires_str)

        return filename, token, expires

    except (ValueError, TypeError) as e:
        logger.error(f"[SIGNED_URL] Erreur parsing URL: {e}")
        return None


def is_url_signed(url: str) -> bool:
    """
    Vérifie si une URL contient une signature.

    Args:
        url: URL à vérifier

    Returns:
        True si l'URL contient token et expires
    """
    return "token=" in url and "expires=" in url


# Pour tests rapides
if __name__ == "__main__":
    # Test génération
    test_file = "test_document.docx"
    signed = generate_signed_url(test_file, expires_in=60)
    print(f"URL signée: {signed}")

    # Test extraction
    params = extract_params_from_url(signed)
    if params:
        filename, token, expires = params
        print(f"Filename: {filename}")
        print(f"Token: {token[:20]}...")
        print(f"Expires: {expires}")

        # Test vérification
        is_valid, error = verify_signed_url(filename, token, expires)
        print(f"Valide: {is_valid}, Erreur: {error or 'aucune'}")

    # Test URL expirée
    print("\n--- Test expiration ---")
    expired_url = generate_signed_url("old.docx", expires_in=-10)  # Déjà expiré
    params = extract_params_from_url(expired_url)
    if params:
        is_valid, error = verify_signed_url(*params)
        print(f"URL expirée - Valide: {is_valid}, Erreur: {error}")
