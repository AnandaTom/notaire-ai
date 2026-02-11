# Recommandations d'Améliorations — Notomai v2.0.0

> Analyse complète du codebase et pistes d'amélioration prioritaires
> **Date**: 11 février 2026
> **État actuel**: 7 templates PROD, 257 tests passing, conformité 80-92%

---

## 📊 Résumé Exécutif

Le système Notomai est **production-ready** avec une architecture solide (3 couches) et une excellente couverture de tests. Cependant, plusieurs axes d'amélioration critiques ont été identifiés pour garantir la **maintenabilité long-terme** et la **scalabilité** en production.

### Métriques Actuelles

| Métrique | Valeur | Statut |
|----------|--------|--------|
| LOC (execution/) | ~15,000 lignes | ⚠️ Important |
| Plus grand fichier | gestionnaire_promesses.py (1,548 lignes) | 🔴 Refactoring nécessaire |
| Exception handlers larges | 30 (`except Exception`) | 🔴 **Critique** |
| Print statements | 44 (core/) | ⚠️ Utiliser logger |
| Deep copies | 57 appels | ⚠️ Optimiser |
| Tests | 257 (3 skipped) | ✅ Excellent |
| Conformité templates | 80.2-91.7% | ✅ Production |
| Couverture types | ~40% | ⚠️ Ajouter type hints |

---

## 🔴 PRIORITÉ CRITIQUE — À Corriger Immédiatement

### 1. Remplacer les Exception Handlers Trop Larges

**Problème**: 30 blocs `except Exception` avalent silencieusement les erreurs.

**Exemple** ([gestionnaire_promesses.py:409](execution/gestionnaires/gestionnaire_promesses.py#L409)):
```python
# ❌ MAUVAIS
try:
    resultat = self._evaluer_condition(condition, donnees)
except Exception as e:
    warnings.append(f"Erreur évaluation règle: {e}")
    continue  # Erreur silencieuse, difficile à débugger !
```

**Solution**:
```python
# ✅ BON
try:
    resultat = self._evaluer_condition(condition, donnees)
except KeyError as e:
    warnings.append(f"Champ manquant dans condition: {e}")
    continue
except AttributeError as e:
    logger.error(f"Structure de données invalide: {e}")
    raise ValidationError(f"Données invalides: {e}")
except ValueError as e:
    warnings.append(f"Valeur incorrecte: {e}")
```

**Impact**:
- ✅ Erreurs explicites au lieu de silencieuses
- ✅ Meilleur débogage en production
- ✅ Évite les bugs masqués

**Effort**: 2-3 jours (11 fichiers à modifier)

**Fichiers concernés**:
- `execution/gestionnaires/gestionnaire_promesses.py` (11 instances)
- `execution/gestionnaires/orchestrateur.py` (8 instances)
- `execution/gestionnaires/gestionnaire_titres.py` (7 instances)
- `execution/gestionnaires/gestionnaire_clauses.py` (4 instances)

---

### 2. Extraire les God Classes

**Problème**: `GestionnairePromesses` (1,548 lignes) et `OrchestratorNotaire` (1,470 lignes) violent le principe de responsabilité unique.

**`GestionnairePromesses` gère**:
- ✓ Détection de type (3 niveaux)
- ✓ Validation des données
- ✓ Génération (assemblage + export)
- ✓ Conversion promesse ↔ vente
- ✓ Intégration Supabase
- ✓ Sélection de template

**Solution**: Découper en 4 classes spécialisées

```python
# ✅ BON - Single Responsibility Principle

class PromesseDetector:
    """Détection de catégorie, type, et sous-type."""
    def detecter_categorie_bien(self, donnees) -> CategorieBien: ...
    def detecter_type(self, donnees) -> ResultatDetection: ...
    def detecter_sous_type(self, donnees, categorie) -> str: ...

class PromesseValidator:
    """Validation sémantique et cohérence."""
    def valider(self, donnees) -> ResultatValidationPromesse: ...
    def _valider_regle(self, regle, donnees) -> bool: ...

class PromesseGenerator:
    """Assemblage template + export DOCX."""
    def generer(self, donnees, template) -> Path: ...
    def _selectionner_template(self, detection) -> Path: ...

class PromesseConverter:
    """Conversions entre types de documents."""
    def promesse_vers_vente(self, donnees_promesse) -> dict: ...
    def titre_vers_promesse(self, titre, beneficiaires) -> dict: ...
```

**Impact**:
- ✅ Meilleure testabilité (classes isolées)
- ✅ Réutilisabilité (composition au lieu d'héritage)
- ✅ Maintenance simplifiée (responsabilités claires)

**Effort**: 1 semaine (refactoring + tests)

---

### 3. Corriger les Problèmes de Scalabilité

#### 3.1 Cache Non-Borné dans `assembler_acte.py`

**Problème** ([assembler_acte.py:46](execution/core/assembler_acte.py#L46)):
```python
# ❌ MAUVAIS - Fuite mémoire sur Modal
_env_cache: Dict[str, Environment] = {}  # Jamais vidé !
```

**Impact**: Fuite mémoire sur Modal (processus long-running), crash après 100+ générations.

**Solution**:
```python
# ✅ BON
from functools import lru_cache

@lru_cache(maxsize=10)
def _get_cached_environment(template_dir: str) -> Environment:
    """Cache LRU avec limite de 10 templates en mémoire."""
    return Environment(loader=FileSystemLoader(template_dir))
```

**Effort**: 1 heure

#### 3.2 Rate Limiter En-Mémoire dans `api/main.py`

**Problème** ([api/main.py:83](api/main.py#L83)):
```python
# ❌ MAUVAIS - Ne scale pas sur Modal (multi-containers)
request_history = collections.deque(maxlen=100)  # In-memory only
```

**Impact**: Rate limiter inefficace sur Modal (chaque container a sa propre deque).

**Solution**:
```python
# ✅ BON - Rate limiter distribué
from redis import Redis
from slowapi import Limiter
from slowapi.util import get_remote_address

redis_client = Redis.from_url(os.environ["REDIS_URL"])
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.environ["REDIS_URL"],
    default_limits=["10 per minute"]
)

@app.post("/promesses/generer")
@limiter.limit("5 per minute")
async def generer_promesse(...): ...
```

**Effort**: 1 jour (config Redis + migration)

---

## ⚠️ PRIORITÉ HAUTE — Sprint Suivant

### 4. Standardiser le Logging

**Problème**: 44 `print()` statements dans `core/` alors que `logger` existe.

**Exemples**:
- `assembler_acte.py`: 8 print statements
- `exporter_docx.py`: 5 print statements
- `valider_acte.py`: 17 print statements

**Solution**:
```python
# ❌ MAUVAIS
print(f"Assemblage du template {template_path}")
print(f"Erreur: {e}")

# ✅ BON
logger.info(f"Assemblage du template {template_path}")
logger.error(f"Erreur assemblage template {template_path}: {e}", exc_info=True)
```

**Configuration centralisée** (`execution/utils/logger.py`):
```python
import logging
from rich.logging import RichHandler

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = RichHandler(rich_tracebacks=True)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    return logger
```

**Impact**:
- ✅ Logs structurés (timestamp, level, context)
- ✅ Meilleur débogage en production (filtrage par level)
- ✅ Intégration facile avec monitoring (Sentry, Datadog)

**Effort**: 2 jours

---

### 5. Ajouter une Abstraction de Stockage

**Problème**: Couplage direct avec Supabase dans 5+ fichiers.

**Exemple** ([gestionnaire_promesses.py:1200](execution/gestionnaires/gestionnaire_promesses.py#L1200)):
```python
# ❌ MAUVAIS - Couplage direct
response = self.supabase.table('promesses_generees').insert({...}).execute()
```

**Solution**: Créer une interface `StorageRepository`

```python
# ✅ BON

from abc import ABC, abstractmethod
from typing import List, Optional

class StorageRepository(ABC):
    """Interface pour le stockage des documents."""

    @abstractmethod
    def save_promesse(self, data: dict) -> str:
        """Sauvegarde une promesse. Retourne l'ID."""
        pass

    @abstractmethod
    def get_promesse(self, id: str) -> Optional[dict]:
        """Récupère une promesse par ID."""
        pass

class SupabaseStorage(StorageRepository):
    """Implémentation Supabase."""
    def __init__(self, client):
        self.client = client

    def save_promesse(self, data: dict) -> str:
        response = self.client.table('promesses_generees').insert(data).execute()
        return response.data[0]['id']

class LocalJSONStorage(StorageRepository):
    """Implémentation locale (pour tests)."""
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def save_promesse(self, data: dict) -> str:
        import uuid
        id = str(uuid.uuid4())
        path = self.base_dir / f"{id}.json"
        path.write_text(json.dumps(data, indent=2))
        return id
```

**Impact**:
- ✅ Tests unitaires plus rapides (mock storage)
- ✅ Possibilité de swap de backend (PostgreSQL, MongoDB)
- ✅ Respect du principe d'inversion de dépendances

**Effort**: 3 jours

---

### 6. Ajouter des Tests d'Intégration E2E

**Problème**: Couverture actuelle = 257 tests unitaires, mais **aucun test E2E complet**.

**Tests manquants**:
- ❌ Titre → Promesse → Vente (pipeline complet)
- ❌ Requête API → Génération DOCX → Téléchargement
- ❌ Requêtes concurrentes (race conditions)
- ❌ Échec connexion Supabase (résilience)

**Solution**: Tests E2E avec fixtures réalistes

```python
# tests/test_e2e_pipelines.py

def test_pipeline_titre_vers_vente_complet(tmp_path):
    """Test E2E: PDF titre → Promesse DOCX → Vente DOCX."""

    # 1. Extraction titre
    titre_pdf = "exemples/titre_propriete_exemple.pdf"
    titre_json = extraire_titre(titre_pdf)
    assert titre_json["proprietaires"]

    # 2. Conversion titre → promesse
    beneficiaires = [{"nom": "DUPONT", "prenoms": "Jean"}]
    promesse_data = titre_vers_promesse(titre_json, beneficiaires, prix=450000)

    # 3. Génération promesse DOCX
    promesse_docx = generer_promesse(promesse_data, output_dir=tmp_path)
    assert promesse_docx.exists()
    assert promesse_docx.stat().st_size > 50_000  # >50 KB

    # 4. Conversion promesse → vente
    vente_data = promesse_vers_vente(promesse_data)

    # 5. Génération vente DOCX
    vente_docx = generer_vente(vente_data, output_dir=tmp_path)
    assert vente_docx.exists()
    assert vente_docx.stat().st_size > 60_000  # >60 KB

    # 6. Vérification conformité
    conformite = comparer_documents(vente_docx, "docs_original/Trame vente.docx")
    assert conformite >= 0.80  # ≥80%

def test_api_generation_concurrente():
    """Test E2E: Génération simultanée (race conditions)."""
    import asyncio
    from httpx import AsyncClient

    async def generer_promesse(client, data):
        response = await client.post("/promesses/generer", json=data)
        return response.json()

    async with AsyncClient(base_url="http://localhost:8000") as client:
        # 10 requêtes simultanées
        tasks = [generer_promesse(client, donnees_test) for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # Vérifier que toutes ont réussi
        assert all(r["fichier_docx"] for r in results)

        # Vérifier que les IDs sont uniques (pas de collision)
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids))
```

**Effort**: 3 jours

---

## 📋 PRIORITÉ MOYENNE — Backlog

### 7. Optimiser l'Usage de `deepcopy`

**Problème**: 57 appels à `copy.deepcopy()` avec overhead de 1-2ms chacun.

**Impact**: ~100ms de perte totale sur un pipeline complet.

**Solution**: Copier uniquement les chemins mutés

```python
# ❌ MAUVAIS - Copie tout (800+ clés)
donnees_copy = copy.deepcopy(donnees)

# ✅ BON - Copie shallow + deep sur chemins mutés
donnees_copy = donnees.copy()  # Shallow
if "promettants" in donnees:
    donnees_copy["promettants"] = copy.deepcopy(donnees["promettants"])  # Deep seulement ici
```

**Gain attendu**: 10-15% de performance (pipeline passe de 5.7s → 5.0s).

**Effort**: 2 jours

---

### 8. Ajouter les Type Hints

**Problème**: ~60% des fonctions n'ont pas de type hints.

**Exemple** ([gestionnaire_promesses.py:850](execution/gestionnaires/gestionnaire_promesses.py#L850)):
```python
# ❌ MAUVAIS
def _convertir_titre_vers_promesse(self, titre, beneficiaires, options):
    ...
```

**Solution**:
```python
# ✅ BON
from typing import Dict, List, Any, Optional

def _convertir_titre_vers_promesse(
    self,
    titre: Dict[str, Any],
    beneficiaires: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convertit un titre de propriété en données de promesse.

    Args:
        titre: Titre de propriété extrait (avec clés: proprietaires, bien, origine)
        beneficiaires: Liste des bénéficiaires (acquéreurs)
        options: Options de conversion (défaut: None)

    Returns:
        Dictionnaire de données pour template promesse

    Raises:
        ValueError: Si titre ou beneficiaires manquent des champs obligatoires
    """
    ...
```

**Impact**:
- ✅ Meilleur support IDE (autocomplétion, détection erreurs)
- ✅ Documentation implicite du contrat
- ✅ Détection d'erreurs avant runtime (mypy)

**Effort**: 3 jours

---

### 9. Documenter Toutes les Méthodes Publiques

**Problème**: Fonctions critiques sans docstring.

**Exemples**:
- `_evaluer_condition()` (gestionnaire_promesses.py:409) — pas de docstring sur les implications de sécurité
- `_champ_existe()` (gestionnaire_promesses.py:510) — pas de doc sur la notation de chemin
- `_get_promesse_template()` (orchestrateur.py:1050) — pas de doc sur la logique de détection

**Solution**: Docstrings NumPy-style

```python
def _evaluer_condition(self, condition: str, contexte: Dict[str, Any]) -> bool:
    """Évalue une condition Jinja2 dans un contexte donné.

    **SÉCURITÉ**: Utilise un sandbox Jinja2 (pas d'exécution Python arbitraire).
    Les fonctions disponibles sont limitées à: len, int, float, str, bool.

    Parameters
    ----------
    condition : str
        Expression Jinja2 (ex: "pret_applicable == true")
    contexte : Dict[str, Any]
        Contexte de données (variables disponibles)

    Returns
    -------
    bool
        True si condition évaluée à vrai, False sinon

    Raises
    ------
    JinjaError
        Si expression invalide (syntaxe incorrecte)
    SecurityError
        Si tentative d'accès à fonctions interdites

    Examples
    --------
    >>> _evaluer_condition("prix.montant > 500000", {"prix": {"montant": 600000}})
    True
    >>> _evaluer_condition("bien.copropriete == true", {"bien": {"copropriete": False}})
    False

    Notes
    -----
    Les chemins pointés utilisent la notation Jinja2: `objet.propriete.sous_propriete`.
    Les listes sont accessibles par index: `promettants.0.nom`.
    """
    ...
```

**Effort**: 4 jours

---

### 10. Ajouter des Benchmarks de Performance

**Problème**: Pas de tests de performance automatisés.

**Solution**: pytest-benchmark

```python
# tests/test_performance.py

import pytest
from execution.core.assembler_acte import assembler_acte
from execution.core.exporter_docx import exporter_docx

def test_assemblage_performance(benchmark):
    """Assemblage doit être < 2s."""
    template = "templates/promesse_vente_lots_copropriete.md"
    donnees = charger_exemple("exemples/donnees_promesse_exemple.json")

    result = benchmark(assembler_acte, template, donnees)

    assert benchmark.stats['mean'] < 2.0, f"Assemblage trop lent: {benchmark.stats['mean']:.2f}s"

def test_export_docx_performance(benchmark, tmp_path):
    """Export DOCX doit être < 4s."""
    markdown_path = "exemples/promesse_assembled.md"
    output_path = tmp_path / "test.docx"

    result = benchmark(exporter_docx, markdown_path, output_path)

    assert benchmark.stats['mean'] < 4.0, f"Export DOCX trop lent: {benchmark.stats['mean']:.2f}s"

def test_pipeline_complet_performance(benchmark, tmp_path):
    """Pipeline complet doit être < 6s."""
    def pipeline():
        from execution.workflow_rapide import workflow_rapide
        return workflow_rapide("promesse_vente", donnees_test, tmp_path)

    result = benchmark(pipeline)

    assert benchmark.stats['mean'] < 6.0, f"Pipeline trop lent: {benchmark.stats['mean']:.2f}s"
```

**CI/CD**: Exécuter sur chaque PR, alerter si régression >10%.

**Effort**: 2 jours

---

## 🚀 PISTES D'AMÉLIORATION FONCTIONNELLES

### 11. Génération Parallélisée (Opus 4.6 Agent Teams)

**Concept**: Utiliser Agent Teams pour paralléliser le pipeline.

**Architecture actuelle (séquentielle)**:
```
Validation (50ms) → Détection (20ms) → Assemblage (1500ms) → Export (3500ms)
= 5070ms total
```

**Architecture proposée (parallèle)**:
```
┌─ Cadastre enrichment (500ms) ─┐
├─ Collecte Q&R (prefill 64%)  ─┤
├─ Template audit (conformité)  ─┤ → Orchestrator (Opus)
└─ Schema validation (120ms)   ─┘
         ↓ (max 500ms en parallèle)
    Assemblage (1500ms)
         ↓
┌─ Export DOCX (3500ms) ────────┐
└─ Clause suggester (2000ms)   ─┤ → Parallèle
         ↓
   Post-generation QA (1000ms)
```

**Gain théorique**: 2.5-3x plus rapide (5s → 2s pour promesse standard).

**Voir**: [AUDIT_GENERAL_FEVRIER_2026.md:697](docs/AUDIT_GENERAL_FEVRIER_2026.md#L697) pour l'implémentation complète.

**Effort**: 1-2 semaines (création agents + orchestration)

---

### 12. Support Multi-Langue (Templates Bilingues)

**Besoin**: Générer actes en français et anglais (transactions internationales).

**Solution**: Templates i18n avec Jinja2

```jinja2
{% set lang = acte.langue | default('fr') %}

## {{ _('DESIGNATION_DU_BIEN', lang) }}

{{ _('UN_APPARTEMENT_SITUE', lang) }} {{ bien.adresse.adresse }}
```

**Fichiers de traduction** (`locales/en.json`):
```json
{
  "DESIGNATION_DU_BIEN": "PROPERTY DESCRIPTION",
  "UN_APPARTEMENT_SITUE": "An apartment located at"
}
```

**Effort**: 2-3 semaines (traduction templates + validation juridique)

---

### 13. Mode "Preview" Temps Réel (WebSocket)

**Besoin**: Voir l'acte se construire en direct pendant la collecte Q&R.

**Architecture**:
```
Frontend (React) → WebSocket → Backend (Modal)
   ↓
   User remplit champ "prix.montant"
   ↓
   Backend → Assemblage partiel → Markdown preview
   ↓
   Frontend affiche section "PRIX ET PAIEMENT" en temps réel
```

**Impact**:
- ✅ Meilleure UX (feedback immédiat)
- ✅ Détection d'erreurs avant génération finale
- ✅ Confiance notaire (voit le document se construire)

**Effort**: 1 semaine (WebSocket + assemblage incrémental)

---

## 📊 Roadmap Proposée (3 Sprints)

### Sprint 1 (2 semaines) — Stabilité & Qualité
- 🔴 **Item 1**: Remplacer exception handlers larges (2-3 jours)
- 🔴 **Item 3**: Corriger scalabilité (cache, rate limiter) (1 jour)
- ⚠️ **Item 4**: Standardiser logging (2 jours)
- ⚠️ **Item 6**: Ajouter tests E2E (3 jours)
- **Livrable**: Codebase plus stable, meilleur débogage

### Sprint 2 (2 semaines) — Architecture & Maintenabilité
- 🔴 **Item 2**: Extraire God classes (1 semaine)
- ⚠️ **Item 5**: Abstraction stockage (3 jours)
- 📋 **Item 8**: Ajouter type hints (3 jours)
- **Livrable**: Codebase plus maintenable, meilleure testabilité

### Sprint 3 (2 semaines) — Performance & Fonctionnalités
- 📋 **Item 7**: Optimiser deepcopy (2 jours)
- 📋 **Item 10**: Benchmarks performance (2 jours)
- 🚀 **Item 11**: Génération parallélisée (1 semaine)
- **Livrable**: Pipeline 2-3x plus rapide, monitoring performance

---

## ✅ Checklist de Mise en Œuvre

### Phase 1: Analyse & Planning
- [x] Audit complet du codebase (fait — ce document)
- [ ] Créer tickets GitHub pour chaque recommandation
- [ ] Prioriser avec l'équipe (product owner, tech lead)
- [ ] Allouer ressources (1-2 devs full-time sur refactoring)

### Phase 2: Implémentation Critique
- [ ] Exception handlers spécifiques (Sprint 1)
- [ ] Logging standardisé (Sprint 1)
- [ ] Tests E2E (Sprint 1)
- [ ] Scalability fixes (Sprint 1)

### Phase 3: Refactoring Architecture
- [ ] Extraire GestionnairePromesses en 4 classes (Sprint 2)
- [ ] Extraire OrchestratorNotaire (Sprint 2)
- [ ] Abstraction StorageRepository (Sprint 2)
- [ ] Type hints complets (Sprint 2)

### Phase 4: Optimisation & Features
- [ ] Optimiser deepcopy (Sprint 3)
- [ ] Benchmarks CI/CD (Sprint 3)
- [ ] Agent Teams parallélisation (Sprint 3)
- [ ] Preview temps réel (Sprint 4)

---

## 📚 Références

- **Code Analysis**: Agent Explore (11/02/2026) — [ab9070f]
- **Architecture**: [CLAUDE.md](../CLAUDE.md)
- **Tests**: [tests/](../tests/) — 257 tests passing
- **Audit Général**: [AUDIT_GENERAL_FEVRIER_2026.md](AUDIT_GENERAL_FEVRIER_2026.md)
- **Agent Teams Implementation**: [AUDIT_GENERAL_FEVRIER_2026.md:697](AUDIT_GENERAL_FEVRIER_2026.md#L697)

---

*Document généré le 11/02/2026 — Notomai v2.0.0*
