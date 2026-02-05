"""
Suppression securisee de fichiers et repertoires.

Ecrase le contenu des fichiers avec des donnees aleatoires puis des zeros
AVANT de les supprimer, pour eviter la recuperation de donnees sensibles
(noms, adresses, patrimoine des clients) depuis le disque.

Utilisation:
    from execution.security.secure_delete import secure_delete_file, secure_delete_dir

    secure_delete_file(Path(".tmp/actes_generes/dossier/donnees.json"))
    secure_delete_dir(Path(".tmp/actes_generes/dossier"))
"""

import os
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# Nombre de passes d'ecrasement (1 aleatoire + 1 zeros = suffisant pour SSD/HDD modernes)
_OVERWRITE_PASSES = 2
_BLOCK_SIZE = 65536  # 64 Ko


def _overwrite_file(filepath: Path) -> None:
    """Ecrase le contenu d'un fichier avant suppression."""
    try:
        size = filepath.stat().st_size
        if size == 0:
            return

        with open(filepath, "r+b") as f:
            # Passe 1 : donnees aleatoires
            remaining = size
            while remaining > 0:
                chunk = min(_BLOCK_SIZE, remaining)
                f.write(os.urandom(chunk))
                remaining -= chunk
            f.flush()
            os.fsync(f.fileno())

            # Passe 2 : zeros
            f.seek(0)
            remaining = size
            while remaining > 0:
                chunk = min(_BLOCK_SIZE, remaining)
                f.write(b'\x00' * chunk)
                remaining -= chunk
            f.flush()
            os.fsync(f.fileno())

    except (OSError, PermissionError) as e:
        logger.warning(f"Impossible d'ecraser {filepath}: {e}")


def secure_delete_file(filepath: Union[str, Path]) -> bool:
    """
    Supprime un fichier de maniere securisee (ecrasement puis suppression).

    Returns:
        True si le fichier a ete supprime, False sinon.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        return False

    if not filepath.is_file():
        logger.warning(f"secure_delete_file: {filepath} n'est pas un fichier")
        return False

    try:
        _overwrite_file(filepath)
        filepath.unlink()
        return True
    except Exception as e:
        logger.warning(f"Erreur suppression securisee {filepath}: {e}")
        # Fallback : suppression simple
        try:
            filepath.unlink(missing_ok=True)
            return True
        except Exception:
            return False


def secure_delete_dir(dirpath: Union[str, Path]) -> int:
    """
    Supprime un repertoire et tout son contenu de maniere securisee.
    Ecrase chaque fichier avant de supprimer l'arborescence.

    Returns:
        Nombre de fichiers supprimes de maniere securisee.
    """
    dirpath = Path(dirpath)
    if not dirpath.exists():
        return 0

    if not dirpath.is_dir():
        logger.warning(f"secure_delete_dir: {dirpath} n'est pas un repertoire")
        return 0

    count = 0

    # Ecraser tous les fichiers d'abord (parcours en profondeur)
    for item in sorted(dirpath.rglob("*"), reverse=True):
        if item.is_file():
            if secure_delete_file(item):
                count += 1
        elif item.is_dir():
            try:
                item.rmdir()
            except OSError:
                pass

    # Supprimer le repertoire racine
    try:
        dirpath.rmdir()
    except OSError as e:
        logger.warning(f"Impossible de supprimer le repertoire {dirpath}: {e}")

    return count
