# Guide de Migration vers le Logger Standardisé

**Version**: 2.0.0
**Date**: Février 2026
**Auteur**: Sprint Plan JOUR 2
**Objectif**: Remplacer les 44+ print() par un système de logging structuré avec Rich

---

## Table des Matières

1. [Pourquoi Migrer?](#pourquoi-migrer)
2. [Installation](#installation)
3. [Usage Basique](#usage-basique)
4. [Patterns de Migration](#patterns-de-migration)
5. [Configuration Avancée](#configuration-avancée)
6. [Best Practices](#best-practices)
7. [Checklist Migration](#checklist-migration)

---

## Pourquoi Migrer?

### Problèmes avec `print()`

```python
# ❌ Avant: print() partout
print(f"✅ Génération réussie: {fichier}")
print(f"❌ Erreur: {err}")
print(f"Assemblage du template {template}...")
```

**Inconvénients:**
- ❌ Pas de niveaux de sévérité (INFO, WARNING, ERROR)
- ❌ Pas de timestamp
- ❌ Pas de contexte (module source)
- ❌ Difficile à filtrer en production
- ❌ Problèmes d'encodage Windows (emojis)
- ❌ Impossible de rediriger vers fichier log
- ❌ Difficile à tester

### Avantages du Logger

```python
# ✅ Après: logger structuré
from execution.utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info(f"Génération réussie: {fichier}")
logger.error(f"Erreur: {err}")
logger.debug(f"Assemblage du template {template}...")
```

**Avantages:**
- ✅ 5 niveaux de sévérité (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Timestamp automatique (YYYY-MM-DD HH:MM:SS)
- ✅ Nom du module dans chaque message
- ✅ Filtrage par niveau (`--debug`, `--quiet`)
- ✅ Output coloré avec Rich (si installé)
- ✅ Écriture fichier automatique si activée
- ✅ Testable (caplog dans pytest)

---

## Installation

Le module `execution/utils/logger.py` utilise **uniquement la stdlib** par défaut.

### Rich (Optionnel, Recommandé)

Pour output coloré et tracebacks améliorés:

```bash
pip install rich
```

Si Rich n'est pas installé, le logger utilise `StreamHandler` standard (fonctionne quand même).

---

## Usage Basique

### 1. Importer et Configurer

```python
from execution.utils.logger import setup_logger

# En haut du fichier, après les imports
logger = setup_logger(__name__)
```

**Pourquoi `__name__`?**
- Crée une hiérarchie de loggers
- Permet de filtrer par module (`notomai.extraction.*`)
- Facilite le debug (on sait quel fichier a loggé)

### 2. Remplacer les print()

| Avant (print) | Après (logger) | Niveau |
|---------------|----------------|--------|
| `print("Démarrage...")` | `logger.info("Démarrage...")` | INFO |
| `print(f"Debug: {var}")` | `logger.debug(f"Debug: {var}")` | DEBUG |
| `print("⚠️ Attention")` | `logger.warning("Attention")` | WARNING |
| `print("❌ Erreur")` | `logger.error("Erreur")` | ERROR |
| `print("💥 Critique")` | `logger.critical("Critique")` | CRITICAL |

### 3. Niveaux de Logging

```python
logger.debug("Détails internes (désactivé par défaut)")  # 10
logger.info("Informations générales (défaut)")          # 20
logger.warning("Situation anormale mais gérable")       # 30
logger.error("Erreur nécessitant attention")            # 40
logger.critical("Erreur critique bloquante")            # 50
```

**Règle d'Or:**
- `DEBUG`: Détails internes pour diagnostiquer (variables, étapes détaillées)
- `INFO`: Informations générales sur le déroulement (étapes principales)
- `WARNING`: Situations anormales mais non-bloquantes (champ optionnel manquant)
- `ERROR`: Erreurs nécessitant intervention (validation échouée, fichier manquant)
- `CRITICAL`: Erreurs critiques bloquant l'exécution (dépendance manquante)

---

## Patterns de Migration

### Pattern 1: print() Simple

```python
# ❌ Avant
print("Démarrage de l'assemblage")

# ✅ Après
logger.info("Démarrage de l'assemblage")
```

### Pattern 2: print() avec Variables

```python
# ❌ Avant
print(f"Génération de {fichier} terminée")

# ✅ Après
logger.info(f"Génération de {fichier} terminée")
```

### Pattern 3: print() avec Emojis

```python
# ❌ Avant (problèmes Windows)
print(f"✅ Succès: {msg}")
print(f"❌ Erreur: {err}")

# ✅ Après (pas besoin d'emojis, les niveaux suffisent)
logger.info(f"Succès: {msg}")
logger.error(f"Erreur: {err}")
```

**Output avec Rich:**
```
[19:15:30] INFO     Succès: promesse_viager.docx     gestionnaire_promesses.py:123
[19:15:30] ERROR    Erreur: champ manquant           valider_acte.py:45
```

### Pattern 4: Messages Conditionnels

```python
# ❌ Avant
if debug:
    print(f"Variable x = {x}")

# ✅ Après (automatique selon niveau)
logger.debug(f"Variable x = {x}")
```

**Configuration du niveau:**
```python
# Dans notaire.py ou main
import logging
logger = setup_logger(__name__, level=logging.DEBUG if args.debug else logging.INFO)
```

### Pattern 5: Erreurs avec Stack Trace

```python
# ❌ Avant
try:
    process()
except Exception as e:
    print(f"❌ Erreur: {e}")

# ✅ Après (avec traceback automatique)
try:
    process()
except Exception as e:
    logger.error(f"Erreur: {e}", exc_info=True)
    # exc_info=True inclut le stack trace
```

### Pattern 6: Boucles avec Progression

```python
# ❌ Avant
for i, item in enumerate(items):
    print(f"Traitement {i+1}/{len(items)}: {item}")

# ✅ Après
for i, item in enumerate(items):
    logger.info(f"Traitement {i+1}/{len(items)}: {item}")
```

---

## Configuration Avancée

### 1. Logger avec Fichier

```python
from pathlib import Path
from execution.utils.logger import setup_logger

logger = setup_logger(
    __name__,
    log_file=Path(".tmp/logs/extraction.log")
)

logger.info("Ce message va dans stdout ET fichier")
```

### 2. Logger au Niveau Projet

```python
# Dans notaire.py ou orchestrateur.py
from execution.utils.logger import setup_project_logging

# Configuration globale (affecte tous les modules)
setup_project_logging(
    level=logging.DEBUG if args.debug else logging.INFO,
    enable_file_logging=True
)

# Tous les sous-modules héritent cette config
```

### 3. Logger avec Niveau Custom

```python
import logging

# DEBUG pour ce module uniquement
logger = setup_logger(__name__, level=logging.DEBUG)

# Ou niveau variable selon args
logger = setup_logger(
    __name__,
    level=logging.DEBUG if verbose else logging.INFO
)
```

### 4. Hiérarchie de Loggers

```python
# Parent
parent = setup_logger("notomai")

# Enfants (héritent config parent)
extraction = setup_logger("notomai.extraction")
titre = setup_logger("notomai.extraction.titre")
promesse = setup_logger("notomai.generation.promesse")
```

**Avantage:**
```bash
# Filtrer tous les logs extraction
python notaire.py --log-filter notomai.extraction.*

# Ou désactiver un module bruyant
logging.getLogger("notomai.database").setLevel(logging.WARNING)
```

---

## Best Practices

### 1. Une Import en Haut de Fichier

```python
"""
Module de génération de promesses.
"""
from execution.utils.logger import setup_logger

logger = setup_logger(__name__)

def generer_promesse(...):
    logger.info("Démarrage génération promesse")
    ...
```

**Pourquoi pas dans chaque fonction?**
- Performance: création logger une seule fois
- Namespace cohérent: tous les messages du module ont même nom

### 2. Utiliser __name__ Toujours

```python
# ✅ Bon
logger = setup_logger(__name__)

# ❌ Mauvais
logger = setup_logger("mon_logger")
```

**Pourquoi?**
- `__name__` = `notomai.extraction.titre` (namespace automatique)
- Permet filtrage et debug faciles

### 3. Éviter les Calculs Lourds dans Messages

```python
# ❌ Mauvais (calcul même si DEBUG désactivé)
logger.debug(f"Données complètes: {process_heavy_data()}")

# ✅ Bon (lazy evaluation)
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Données complètes: {process_heavy_data()}")
```

### 4. Logs Structurés pour Parsing

```python
# ✅ Format cohérent pour parsing automatique
logger.info(f"Generation | type={type_acte} | fichier={output} | duree={elapsed:.2f}s")

# Facile à parser avec regex ou log analyzer
```

### 5. Contexte dans les Erreurs

```python
# ❌ Mauvais
logger.error("Validation échouée")

# ✅ Bon (avec contexte)
logger.error(f"Validation échouée pour {type_acte}: {erreur.message}")
```

### 6. Ne Pas Logger des Données Sensibles

```python
# ❌ MAUVAIS (fuite PII/credentials)
logger.info(f"Données client: {client.dict()}")
logger.debug(f"API key: {api_key}")

# ✅ Bon (anonymisé)
logger.info(f"Traitement client ID={client.id}")
logger.debug("API authentifiée")
```

---

## Checklist Migration

### Par Fichier

- [ ] Importer `setup_logger`
- [ ] Créer logger avec `setup_logger(__name__)`
- [ ] Remplacer tous les `print()` par `logger.info/debug/error/...`
- [ ] Supprimer les emojis (✅❌⚠️💥)
- [ ] Ajuster les niveaux (info vs debug vs error)
- [ ] Vérifier encodage Windows si nécessaire
- [ ] Tester le fichier modifié
- [ ] Commit avec message clair: `chore: migrate {module} to logger`

### Projet Global

- [ ] Migrer modules critiques (`execution/core/`)
- [ ] Migrer gestionnaires (`execution/gestionnaires/`)
- [ ] Migrer utilitaires (`execution/utils/`)
- [ ] Configurer `notaire.py` avec `setup_project_logging()`
- [ ] Ajouter flag `--debug` pour DEBUG level
- [ ] Ajouter flag `--log-file` pour output fichier
- [ ] Tester pipeline complet
- [ ] Mettre à jour documentation (`CLAUDE.md`, `CONTRIBUTING.md`)
- [ ] Tests E2E avec nouveau logging

---

## Exemples Concrets Notomai

### 1. assembler_acte.py

```python
# ❌ Avant
print(f"Assemblage du template {template_name}...")
print(f"✅ Acte assemblé: {fichier_sortie}")

# ✅ Après
logger = setup_logger(__name__)
logger.info(f"Assemblage du template {template_name}")
logger.info(f"Acte assemblé: {fichier_sortie}")
```

### 2. valider_acte.py

```python
# ❌ Avant
if erreurs:
    print(f"❌ {len(erreurs)} erreurs de validation:")
    for err in erreurs:
        print(f"  - {err}")

# ✅ Après
logger = setup_logger(__name__)
if erreurs:
    logger.error(f"{len(erreurs)} erreurs de validation")
    for err in erreurs:
        logger.error(f"  - {err}")
```

### 3. gestionnaire_promesses.py

```python
# ❌ Avant
print(f"Détection type promesse: {type_detecte}")
print(f"Confiance: {confiance}%")

# ✅ Après
logger = setup_logger(__name__)
logger.info(f"Détection type promesse: {type_detecte}")
logger.debug(f"Confiance: {confiance}%")  # DEBUG car détail interne
```

### 4. orchestrateur.py

```python
# ❌ Avant
print("\n=== WORKFLOW GÉNÉRATION PROMESSE ===")
print(f"1. Détection type: {type_detecte}")
print(f"2. Validation données: {'✅' if valide else '❌'}")

# ✅ Après
logger = setup_logger(__name__)
logger.info("=== WORKFLOW GÉNÉRATION PROMESSE ===")
logger.info(f"1. Détection type: {type_detecte}")
if valide:
    logger.info("2. Validation données: OK")
else:
    logger.error("2. Validation données: ECHEC")
```

---

## Support et Questions

### Rich non installé?

Le logger fonctionne sans Rich (fallback sur `StreamHandler`). Pour installer:

```bash
pip install rich
```

### Problèmes d'encodage Windows?

Si vous voyez des caractères bizarres (�):

```python
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
```

Déjà configuré dans le logger, mais si problème dans votre code:

```python
# En haut du fichier
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

### Logger ne s'affiche pas?

Vérifier le niveau:

```python
import logging

# Forcer DEBUG pour voir tous les messages
logger = setup_logger(__name__, level=logging.DEBUG)

# Ou au runtime
logger.setLevel(logging.DEBUG)
```

### Tests avec logger?

Utiliser `caplog` dans pytest:

```python
def test_with_logging(caplog):
    logger = setup_logger("test")

    with caplog.at_level(logging.INFO):
        logger.info("Test message")

    assert "Test message" in caplog.text
```

---

## Roadmap

### Phase 1: Core Modules (JOUR 2)

- [ ] `execution/core/assembler_acte.py`
- [ ] `execution/core/exporter_docx.py`
- [ ] `execution/core/valider_acte.py`
- [ ] `execution/gestionnaires/orchestrateur.py`

### Phase 2: Gestionnaires (JOUR 2-3)

- [ ] `execution/gestionnaires/gestionnaire_promesses.py`
- [ ] `execution/gestionnaires/gestionnaire_titres.py`
- [ ] `execution/gestionnaires/gestionnaire_clauses.py`

### Phase 3: Utilitaires (JOUR 3)

- [ ] `execution/utils/collecter_informations.py`
- [ ] `execution/utils/extraire_titre.py`
- [ ] Tous les scripts `execution/utils/*.py`

### Phase 4: API & Services (JOUR 4)

- [ ] `execution/api/*.py`
- [ ] `execution/services/*.py`
- [ ] `notaire.py` (CLI principal)

---

## Ressources

- **Module logger**: `execution/utils/logger.py`
- **Tests**: `tests/test_logger.py`
- **Rich docs**: https://rich.readthedocs.io/
- **Python logging**: https://docs.python.org/3/library/logging.html

---

**Version**: 2.0.0
**Dernière mise à jour**: Février 2026
**Auteur**: Sprint Plan - JOUR 2 Préparation
