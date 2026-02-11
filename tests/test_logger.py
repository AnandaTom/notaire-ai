"""
Tests unitaires pour le module de logging standardisé.

Lance avec: pytest tests/test_logger.py -v
"""

import logging
import sys
from pathlib import Path
import pytest

# Import du module à tester
sys.path.insert(0, str(Path(__file__).parent.parent))
from execution.utils.logger import (
    setup_logger,
    get_logger,
    setup_project_logging,
    RICH_AVAILABLE,
    DEFAULT_LOG_DIR,
    DEFAULT_LOG_LEVEL
)


class TestSetupLogger:
    """Tests pour la fonction setup_logger()."""

    def test_logger_creation_basique(self):
        """Vérifie qu'un logger est créé avec paramètres par défaut."""
        logger = setup_logger("test.basic")

        assert logger is not None
        assert logger.name == "test.basic"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_logger_avec_niveau_custom(self):
        """Vérifie que le niveau de logging est respecté."""
        logger = setup_logger("test.custom_level", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_logger_avec_fichier(self, tmp_path):
        """Vérifie qu'un logger peut écrire dans un fichier."""
        log_file = tmp_path / "test.log"
        logger = setup_logger("test.file", log_file=log_file)

        # Écrire un message
        test_message = "Message de test pour fichier"
        logger.info(test_message)

        # Vérifier que le fichier existe et contient le message
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert test_message in content
        assert "test.file" in content  # Nom du logger
        assert "INFO" in content  # Niveau

    def test_logger_singleton_behavior(self):
        """Vérifie que plusieurs appels avec même nom retournent le même logger."""
        logger1 = setup_logger("test.singleton")
        logger2 = setup_logger("test.singleton")

        assert logger1 is logger2
        assert id(logger1) == id(logger2)

    def test_logger_pas_de_doublons_handlers(self):
        """Vérifie qu'on n'ajoute pas de handlers en double."""
        logger = setup_logger("test.no_duplicates")
        initial_handler_count = len(logger.handlers)

        # Appeler setup_logger plusieurs fois
        setup_logger("test.no_duplicates")
        setup_logger("test.no_duplicates")

        # Le nombre de handlers ne doit pas augmenter
        assert len(logger.handlers) == initial_handler_count

    def test_logger_force_reconfigure(self):
        """Vérifie que force_reconfigure nettoie les handlers existants."""
        logger = setup_logger("test.force")
        initial_count = len(logger.handlers)

        # Force reconfigure devrait réinitialiser
        logger = setup_logger("test.force", force_reconfigure=True)

        # Devrait avoir le même nombre de handlers (recréés)
        assert len(logger.handlers) == initial_count

    def test_logger_creation_repertoire_parent(self, tmp_path):
        """Vérifie que le répertoire parent est créé si nécessaire."""
        log_file = tmp_path / "subdir" / "nested" / "test.log"
        assert not log_file.parent.exists()

        logger = setup_logger("test.mkdir", log_file=log_file)
        logger.info("Test message")

        # Le répertoire et le fichier doivent être créés
        assert log_file.parent.exists()
        assert log_file.exists()

    def test_logger_utf8_encoding(self, tmp_path):
        """Vérifie que l'encodage UTF-8 fonctionne pour caractères spéciaux."""
        log_file = tmp_path / "test_utf8.log"
        logger = setup_logger("test.utf8", log_file=log_file)

        # Messages avec caractères spéciaux
        test_messages = [
            "Créé par notaire Müller",
            "Prix: 500 000 €",
            "Propriété à Genève"
        ]

        for msg in test_messages:
            logger.info(msg)

        # Vérifier lecture UTF-8
        content = log_file.read_text(encoding='utf-8')
        for msg in test_messages:
            assert msg in content


class TestGetLogger:
    """Tests pour la fonction get_logger()."""

    def test_get_logger_shortcut(self):
        """Vérifie que get_logger() est un raccourci vers setup_logger()."""
        logger = get_logger("test.shortcut")

        assert logger is not None
        assert logger.name == "test.shortcut"
        assert logger.level == logging.INFO


class TestSetupProjectLogging:
    """Tests pour la fonction setup_project_logging()."""

    def test_project_logging_basique(self):
        """Vérifie la configuration au niveau projet."""
        logger = setup_project_logging(level=logging.WARNING)

        assert logger.name == "notomai"
        assert logger.level == logging.WARNING

    def test_project_logging_avec_fichier(self, tmp_path):
        """Vérifie que le fichier projet est créé."""
        logger = setup_project_logging(
            log_dir=tmp_path,
            enable_file_logging=True
        )

        logger.info("Message projet")

        log_file = tmp_path / "notomai.log"
        assert log_file.exists()
        assert "Message projet" in log_file.read_text(encoding='utf-8')

    def test_project_logging_sans_fichier(self):
        """Vérifie que enable_file_logging=False ne crée pas de fichier."""
        logger = setup_project_logging(enable_file_logging=False)

        # Devrait avoir seulement handler console, pas fichier
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 0


class TestLoggerIntegration:
    """Tests d'intégration pour scénarios réels."""

    def test_hierarchie_loggers(self):
        """Vérifie la hiérarchie parent-enfant des loggers."""
        parent = setup_logger("notomai")
        child = setup_logger("notomai.extraction")
        grandchild = setup_logger("notomai.extraction.titre")

        assert child.parent.name == "notomai"
        assert grandchild.parent.name == "notomai.extraction"

    def test_logger_avec_rich_si_disponible(self):
        """Vérifie le comportement selon disponibilité de Rich."""
        logger = setup_logger("test.rich")

        if RICH_AVAILABLE:
            # Devrait avoir RichHandler
            from rich.logging import RichHandler
            rich_handlers = [h for h in logger.handlers if isinstance(h, RichHandler)]
            assert len(rich_handlers) > 0
        else:
            # Devrait avoir StreamHandler standard
            stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            assert len(stream_handlers) > 0

    def test_logger_multiples_niveaux(self, tmp_path, caplog):
        """Teste que seuls les messages au-dessus du niveau sont loggés."""
        log_file = tmp_path / "levels.log"
        logger = setup_logger("test.levels", level=logging.WARNING, log_file=log_file)

        with caplog.at_level(logging.WARNING):
            logger.debug("DEBUG - ne devrait pas apparaître")
            logger.info("INFO - ne devrait pas apparaître")
            logger.warning("WARNING - devrait apparaître")
            logger.error("ERROR - devrait apparaître")

        content = log_file.read_text(encoding='utf-8')

        # DEBUG et INFO ne doivent pas être dans le fichier
        assert "DEBUG" not in content
        assert "INFO" not in content

        # WARNING et ERROR doivent être présents
        assert "WARNING" in content
        assert "ERROR" in content

    def test_logger_format_timestamp(self, tmp_path):
        """Vérifie le format du timestamp (YYYY-MM-DD HH:MM:SS)."""
        log_file = tmp_path / "timestamp.log"
        logger = setup_logger("test.timestamp", log_file=log_file)

        logger.info("Message avec timestamp")

        content = log_file.read_text(encoding='utf-8')

        # Vérifier format timestamp (regex simple)
        import re
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(pattern, content) is not None


class TestLoggerEdgeCases:
    """Tests des cas limites et erreurs."""

    def test_logger_nom_vide(self):
        """Vérifie comportement avec nom vide."""
        # Python permet les noms vides (root logger)
        logger = setup_logger("")
        assert logger is not None

    def test_logger_nom_unicode(self):
        """Vérifie support noms de logger avec Unicode."""
        logger = setup_logger("test.notaire_müller_€")
        assert logger.name == "test.notaire_müller_€"

    def test_logger_fichier_readonly_directory(self, tmp_path):
        """Teste comportement si répertoire non accessible (skip si Windows)."""
        if sys.platform == "win32":
            pytest.skip("Test non pertinent sur Windows (permissions différentes)")

        # Créer répertoire read-only
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        log_file = readonly_dir / "test.log"

        # Devrait lever OSError
        with pytest.raises(OSError):
            logger = setup_logger("test.readonly", log_file=log_file)
            logger.info("Test")


# Tests de migration depuis print() (examples)
class TestMigrationExamples:
    """Exemples de migration depuis print() vers logger."""

    def test_example_migration_simple(self, tmp_path):
        """Exemple: print() → logger.info()"""
        log_file = tmp_path / "migration.log"
        logger = setup_logger("test.migration", log_file=log_file)

        # Avant: print(f"✅ Génération réussie: {fichier}")
        # Après:
        fichier = "promesse_vente_20260210.docx"
        logger.info(f"Génération réussie: {fichier}")

        content = log_file.read_text(encoding='utf-8')
        assert "Génération réussie" in content
        assert fichier in content

    def test_example_migration_erreur(self, tmp_path):
        """Exemple: print(f"❌ Erreur: ...") → logger.error()"""
        log_file = tmp_path / "erreur.log"
        logger = setup_logger("test.erreur", log_file=log_file)

        # Avant: print(f"❌ Erreur lors de la validation: {err}")
        # Après:
        err = "Champ 'prix.montant' manquant"
        logger.error(f"Erreur lors de la validation: {err}")

        content = log_file.read_text(encoding='utf-8')
        assert "ERROR" in content
        assert err in content


if __name__ == "__main__":
    # Lancer les tests avec pytest
    pytest.main([__file__, "-v", "--tb=short"])
