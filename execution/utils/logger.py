"""
Module de logging standardisé pour Notomai.

Ce module fournit une configuration unifiée du système de logging avec support
optionnel de Rich pour un affichage coloré et des tracebacks améliorés.

Usage basique:
    from execution.utils.logger import setup_logger

    logger = setup_logger(__name__)
    logger.info("Message d'information")
    logger.warning("Avertissement")
    logger.error("Erreur critique")

Usage avancé avec fichier:
    from pathlib import Path
    from execution.utils.logger import setup_logger

    logger = setup_logger(
        __name__,
        level=logging.DEBUG,
        log_file=Path(".tmp/logs/app.log")
    )
    logger.debug("Message de debug")

Niveaux de logging:
    - DEBUG: Détails internes pour diagnostic
    - INFO: Informations générales sur le déroulement
    - WARNING: Situations anormales mais gérables
    - ERROR: Erreurs nécessitant attention
    - CRITICAL: Erreurs critiques bloquantes

Features:
    - Support Rich (optionnel) pour output coloré
    - Format structuré avec timestamp
    - Support fichier de log
    - Évite les doublons de handlers
    - Encodage UTF-8 pour Windows

Example de migration depuis print():
    # Avant
    print(f"✅ Génération réussie: {fichier}")

    # Après
    logger = setup_logger(__name__)
    logger.info(f"Génération réussie: {fichier}")
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    force_reconfigure: bool = False
) -> logging.Logger:
    """
    Configure un logger avec RichHandler (si disponible) et format structuré.

    Cette fonction crée ou récupère un logger avec une configuration standardisée
    pour l'ensemble du projet Notomai. Elle utilise Rich pour un affichage amélioré
    si la bibliothèque est disponible, sinon revient à StreamHandler standard.

    Args:
        name: Nom du logger (utiliser __name__ pour auto-namespacing)
        level: Niveau minimum de logging (défaut: logging.INFO)
               Valeurs: DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
        log_file: Chemin optionnel pour écrire les logs dans un fichier.
                 Le fichier sera créé avec encodage UTF-8.
        force_reconfigure: Force la reconfiguration même si handlers existent
                          (utile pour tests). Défaut: False

    Returns:
        logging.Logger: Logger configuré et prêt à l'emploi

    Raises:
        OSError: Si log_file spécifié mais répertoire parent inexistant

    Example:
        >>> # Usage simple
        >>> logger = setup_logger(__name__)
        >>> logger.info("Démarrage du pipeline")

        >>> # Usage avec fichier
        >>> from pathlib import Path
        >>> logger = setup_logger(
        ...     "notomai.extraction",
        ...     level=logging.DEBUG,
        ...     log_file=Path(".tmp/logs/extraction.log")
        ... )
        >>> logger.debug("Extraction titre: détails internes")

        >>> # Vérification Rich
        >>> logger = setup_logger(__name__)
        >>> logger.info("Rich disponible" if RICH_AVAILABLE else "Rich non installé")

    Notes:
        - Les loggers sont cachés par Python, appels multiples avec même nom
          retournent le même objet
        - Par défaut, évite d'ajouter des handlers en double (sauf si force_reconfigure)
        - Rich est optionnel: si absent, utilise StreamHandler standard
        - Format timestamp: YYYY-MM-DD HH:MM:SS (ISO 8601 tronqué)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Éviter les doublons si logger déjà configuré (sauf force)
    if logger.handlers and not force_reconfigure:
        return logger

    # Nettoyer handlers existants si force_reconfigure
    if force_reconfigure:
        logger.handlers.clear()

    # Handler console avec Rich (si disponible)
    if RICH_AVAILABLE:
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=True,
            markup=True,  # Support Rich markup [bold], [green], etc.
            tracebacks_show_locals=False  # Évite fuites données sensibles
        )
    else:
        handler = logging.StreamHandler(sys.stdout)

    # Format structuré (timestamp + name + level + message)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rich gère son propre format, seulement pour StreamHandler
    if not RICH_AVAILABLE:
        handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Handler fichier optionnel (toujours avec format structuré)
    if log_file:
        log_file = Path(log_file)

        # Créer répertoire parent si nécessaire
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8',
            mode='a'  # Append mode
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un avec config par défaut.

    Fonction de commodité pour récupérer un logger sans spécifier
    tous les paramètres. Utilise setup_logger() en interne.

    Args:
        name: Nom du logger (utiliser __name__)

    Returns:
        logging.Logger: Logger configuré

    Example:
        >>> from execution.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Message rapide")
    """
    return setup_logger(name)


# Configuration globale pour le projet
# Peut être importé et modifié au démarrage de l'application
DEFAULT_LOG_DIR = Path(".tmp/logs")
DEFAULT_LOG_LEVEL = logging.INFO


def setup_project_logging(
    level: int = DEFAULT_LOG_LEVEL,
    log_dir: Optional[Path] = None,
    enable_file_logging: bool = False
) -> logging.Logger:
    """
    Configure le logging au niveau projet (root logger).

    Cette fonction configure le logger racine pour l'ensemble du projet,
    affectant tous les sous-modules. À appeler une seule fois au démarrage.

    Args:
        level: Niveau minimum global
        log_dir: Répertoire pour fichiers de log (défaut: .tmp/logs)
        enable_file_logging: Activer l'écriture dans fichier (défaut: False)

    Returns:
        logging.Logger: Logger racine configuré

    Example:
        >>> # Dans notaire.py ou main.py
        >>> from execution.utils.logger import setup_project_logging
        >>>
        >>> if __name__ == "__main__":
        ...     setup_project_logging(
        ...         level=logging.DEBUG if args.debug else logging.INFO,
        ...         enable_file_logging=True
        ...     )
        ...     # Tous les modules héritent cette config
    """
    log_file = None
    if enable_file_logging:
        log_dir = log_dir or DEFAULT_LOG_DIR
        log_file = log_dir / "notomai.log"

    return setup_logger(
        "notomai",  # Logger racine du projet
        level=level,
        log_file=log_file,
        force_reconfigure=True
    )


if __name__ == "__main__":
    # Fix encodage Windows pour démo
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    # Demo du module
    print("=== Demo Module de Logging Notomai ===\n")

    # Test 1: Logger basique
    print("1. Logger basique:")
    logger = setup_logger("demo.basic")
    logger.debug("Message DEBUG (non affiché avec level=INFO)")
    logger.info("Message INFO")
    logger.warning("Message WARNING")
    logger.error("Message ERROR")
    logger.critical("Message CRITICAL")

    print("\n2. Logger avec niveau DEBUG:")
    logger_debug = setup_logger("demo.debug", level=logging.DEBUG)
    logger_debug.debug("Maintenant DEBUG est visible")
    logger_debug.info("Assemblage template: promesse_viager.md")

    print("\n3. Logger avec fichier:")
    log_file = Path(".tmp/logs/demo.log")
    logger_file = setup_logger("demo.file", log_file=log_file)
    logger_file.info(f"Ce message est aussi écrit dans {log_file}")

    if log_file.exists():
        print(f"   [OK] Fichier créé: {log_file}")
        print(f"   Contenu: {log_file.read_text(encoding='utf-8').strip()}")

    print("\n4. Rich disponible?")
    if RICH_AVAILABLE:
        print("   [OK] Rich installé - output coloré activé")
        logger.info("[bold green]Message avec Rich markup[/bold green]")
    else:
        print("   [!] Rich non installé - output standard")

    print("\n5. Hiérarchie de loggers:")
    parent = setup_logger("notomai")
    child = setup_logger("notomai.extraction")
    grandchild = setup_logger("notomai.extraction.titre")

    parent.info("Message parent")
    child.info("Message enfant")
    grandchild.info("Message petit-enfant")

    print("\n=== Fin Demo ===")
