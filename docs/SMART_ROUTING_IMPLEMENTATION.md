# Smart Routing de Modèles LLM - Implémentation v2.1.0

**Date**: 11 février 2026
**Sprint Plan**: JOUR 1 MATIN
**Objectif**: Réduire les coûts API de 60% en sélectionnant intelligemment le modèle Claude selon le type d'opération

---

## Vue d'ensemble

Le smart routing permet de router automatiquement chaque appel LLM vers le modèle optimal (Haiku, Sonnet ou Opus) selon le type d'opération et la complexité des données.

### Économie attendue

| Métrique | Valeur |
|----------|--------|
| Économie globale | **60-65%** vs baseline Opus uniquement |
| Distribution Haiku | 35-40% des appels (validation) |
| Distribution Sonnet | 55-60% des appels (détection + génération std) |
| Distribution Opus | 5% des appels (génération complexe) |

### Coûts indicatifs (par appel)

| Modèle | Coût | Économie vs Opus |
|--------|------|------------------|
| **Opus** | $0.005 | 0% (baseline) |
| **Sonnet** | $0.002 | **60%** |
| **Haiku** | $0.001 | **80%** |

---

## Règles de Routing

### Règle 1: Validation → Haiku (80% économie)

```python
modele = orchestrateur._choisir_modele(type_operation="validation")
# → claude-haiku-4-5-20251001
```

**Justification**: La validation est déterministe (vérification de champs obligatoires, cohérence). Haiku suffit amplement.

### Règle 2: Détection haute confiance → Sonnet (60% économie)

```python
modele = orchestrateur._choisir_modele(
    type_operation="detection",
    confiance=0.85  # >80%
)
# → claude-sonnet-4-5-20250929
```

**Justification**: Quand la détection est quasi-certaine (ex: regex match + contexte), Sonnet est aussi performant qu'Opus.

### Règle 3: Suggestion clauses → Opus (créativité)

```python
modele = orchestrateur._choisir_modele(type_operation="suggestion_clauses")
# → claude-opus-4-6
```

**Justification**: Suggérer des clauses juridiques personnalisées nécessite créativité et raisonnement avancé.

### Règle 4: Génération → Analyse de complexité

#### 4a. Génération standard → Sonnet (60% économie)

```python
donnees = {
    "acte": {"type": "vente"},  # Type fréquent
    "vendeurs": [{"nom": "Dupont"}],  # 1-2 parties
    "acquereurs": [{"nom": "Martin"}],
    "bien": {"adresse": "12 rue Test"},
    "prix": {"montant": 350000}  # <1M€
}

modele = orchestrateur._choisir_modele(type_operation="generation", donnees=donnees)
# → claude-sonnet-4-5-20250929
```

**Critères "standard"**:
- Type acte fréquent (vente, promesse)
- 1-2 vendeurs ET 1-2 acquéreurs
- Données complètes (tous champs critiques présents)
- Prix < 1M€

#### 4b. Génération complexe → Opus (qualité max)

**Cas 1: Type acte rare/complexe**

```python
donnees = {"acte": {"type": "viager"}, ...}
# → claude-opus-4-6 (types complexes: viager, donation_partage, sci)
```

**Cas 2: Multi-parties (>2 vendeurs OU >2 acquéreurs)**

```python
donnees = {
    "vendeurs": [
        {"nom": "Dupont"},
        {"nom": "Martin"},
        {"nom": "Bernard"}  # >2 vendeurs
    ],
    ...
}
# → claude-opus-4-6
```

**Cas 3: Prix élevé (>1M€)**

```python
donnees = {"prix": {"montant": 1_500_000}, ...}
# → claude-opus-4-6 (enjeux importants)
```

**Cas 4: Données incomplètes (≥2 champs critiques manquants)**

```python
donnees = {"acte": {"type": "vente"}}  # Manquants: vendeurs, acquereurs, bien, prix
# → claude-opus-4-6 (nécessite raisonnement avancé)
```

### Règle 5: Fallback → Opus (sécurité)

Pour toute opération non catégorisée, Opus est utilisé par défaut pour garantir la qualité.

---

## Implémentation

### Méthode principale

**Fichier**: `execution/gestionnaires/orchestrateur.py`

```python
def _choisir_modele(
    self,
    type_operation: str,
    confiance: float = 1.0,
    donnees: Optional[Dict[str, Any]] = None
) -> str:
    """
    Sélectionne le modèle optimal selon le type d'opération et la confiance.

    Args:
        type_operation: Type d'opération ("detection", "validation", "generation", etc.)
        confiance: Score de confiance (0-1) pour l'opération
        donnees: Données optionnelles pour analyser la complexité

    Returns:
        str: Model ID Claude (format "claude-{modele}-{version}")
    """
    # ... (voir code source)
```

### Statistiques d'utilisation

```python
# Afficher les stats dans le dashboard
orchestrateur = OrchestratorNotaire()
orchestrateur.afficher_stats_modeles()
```

**Sortie exemple**:

```
💰 Statistiques Modèles LLM (v2.1.0):
   Total appels: 100
   Haiku    ████████░░░░░░░░░░░░  40 ( 40.0%) - 80% économie vs Opus
   Sonnet   ███████████░░░░░░░░░  55 ( 55.0%) - 60% économie vs Opus
   Opus     █░░░░░░░░░░░░░░░░░░░   5 (  5.0%) - baseline

   Économie estimée: 65% vs 100 appels Opus
   Coût estimé: $0.18 (vs $0.50 baseline)
```

---

## Tests

### Tests unitaires

**Fichier**: `tests/test_orchestrateur.py`

**Résultats**: ✅ **12 tests passed** (0 failures)

| Test | Description |
|------|-------------|
| `test_validation_utilise_haiku` | Validation → Haiku |
| `test_detection_haute_confiance_utilise_sonnet` | Détection >80% → Sonnet |
| `test_detection_faible_confiance_utilise_opus` | Détection ≤80% → Opus |
| `test_suggestion_clauses_utilise_opus` | Suggestion → Opus |
| `test_generation_cas_standard_utilise_sonnet` | Génération std → Sonnet |
| `test_generation_type_complexe_utilise_opus` | Génération viager → Opus |
| `test_generation_multi_parties_utilise_opus` | >2 parties → Opus |
| `test_generation_prix_eleve_utilise_opus` | Prix >1M€ → Opus |
| `test_generation_donnees_incompletes_utilise_opus` | Données incomplètes → Opus |
| `test_fallback_opus_pour_operation_inconnue` | Fallback → Opus |
| `test_stats_modeles_cumul` | Cumul stats |
| `test_scenario_100_generations_mixtes` | Scénario 100 opérations |

**Lancement**:

```bash
python -m pytest tests/test_orchestrateur.py -v
```

### Démonstration interactive

**Fichier**: `execution/gestionnaires/demo_smart_routing.py`

**Lancement**:

```bash
python execution/gestionnaires/demo_smart_routing.py
```

**Démos incluses**:
1. Validation (→ Haiku)
2. Détection haute confiance (→ Sonnet)
3. Génération standard (→ Sonnet)
4. Génération complexe (→ Opus)
5. Suggestion de clauses (→ Opus)
6. Workflow complet (4 appels: Haiku, Sonnet, Sonnet, Opus)
7. Comparaison économie (100 opérations)

---

## Intégration dans les workflows existants

### Exemple 1: Validation avant génération

```python
from execution.gestionnaires.orchestrateur import OrchestratorNotaire, TypeActe

orch = OrchestratorNotaire(verbose=True)

donnees = {
    "acte": {"type": "vente"},
    "vendeurs": [{"nom": "Dupont"}],
    "acquereurs": [{"nom": "Martin"}],
    "bien": {"adresse": "12 rue Test"},
    "prix": {"montant": 350000}
}

# Validation (utilise automatiquement Haiku)
validation = orch._valider_donnees(donnees, TypeActe.VENTE)
# → Logs: "Modèle: HAIKU (validation déterministe)"
```

### Exemple 2: Détection type acte

```python
# Détection rapide par regex (0 coût LLM)
type_detecte = OrchestratorNotaire.detecter_type_acte_rapide("Je veux générer une promesse de vente")

if type_detecte:
    print(f"Type détecté (regex): {type_detecte}")
else:
    # Fallback LLM (avec smart routing)
    orch = OrchestratorNotaire()
    modele = orch._choisir_modele(type_operation="detection", confiance=0.65)
    # → claude-opus-4-6 (confiance <80%)
```

### Exemple 3: Génération acte

```python
orch = OrchestratorNotaire(verbose=True)

# Cas standard (→ Sonnet, 60% économie)
donnees_std = {
    "acte": {"type": "vente"},
    "vendeurs": [{"nom": "Dupont"}],
    "acquereurs": [{"nom": "Martin"}],
    "bien": {"adresse": "12 rue Test"},
    "prix": {"montant": 350000}
}
modele = orch._choisir_modele(type_operation="generation", donnees=donnees_std)
# → Logs: "Modèle: SONNET (génération cas standard)"

# Cas complexe (→ Opus, qualité max)
donnees_viager = {
    "acte": {"type": "viager"},
    "promettants": [{"nom": "Dupont"}],
    "beneficiaires": [{"nom": "Martin"}],
    "bien": {"adresse": "12 rue Test"},
    "prix": {"montant": 250000}
}
modele = orch._choisir_modele(type_operation="generation", donnees=donnees_viager)
# → Logs: "Modèle: OPUS (type complexe: viager)"
```

---

## Monitoring et Optimisation

### Collecte des statistiques

Les statistiques sont automatiquement collectées dans `orchestrateur.stats_modeles`:

```python
{
    "haiku": 40,   # 40 appels Haiku
    "sonnet": 55,  # 55 appels Sonnet
    "opus": 5      # 5 appels Opus
}
```

### Dashboard

```python
orchestrateur = OrchestratorNotaire()

# ... exécuter plusieurs workflows ...

# Afficher les stats
orchestrateur.afficher_dashboard()
```

### Métriques clés à surveiller

| Métrique | Objectif Sprint Plan | Valeur actuelle (démo 100 ops) |
|----------|---------------------|--------------------------------|
| **% Haiku** | 35% | 40% ✅ |
| **% Sonnet** | 60% | 55% ✅ |
| **% Opus** | 5% | 5% ✅ |
| **Économie globale** | 60% | 65% ✅ |

---

## Prochaines étapes (Sprint Plan JOUR 1 APRÈS-MIDI)

### Phase 2: Intégration dans l'API Modal

1. **Ajouter le smart routing dans les endpoints API** (`modal/modal_app.py`)
2. **Logger les choix de modèles** dans Supabase pour analytics
3. **Exposer les stats via endpoint** `/api/stats/modeles`

### Phase 3: Optimisation avancée

1. **Caching intelligent** (éviter appels LLM redondants)
2. **Batch processing** (grouper appels similaires)
3. **A/B testing** (comparer qualité Sonnet vs Opus sur cas limites)

---

## Changelog

### v2.1.0 (11 février 2026)

- ✅ Ajout méthode `_choisir_modele()` dans `orchestrateur.py`
- ✅ Intégration dans `_valider_donnees()`
- ✅ Ajout méthode `afficher_stats_modeles()`
- ✅ Intégration dashboard
- ✅ 12 tests unitaires (100% pass)
- ✅ Script démo interactif
- ✅ Documentation complète

### Résultats Sprint JOUR 1 MATIN

| Livrable | Statut | Remarques |
|----------|--------|-----------|
| Méthode `_choisir_modele()` | ✅ | 85 lignes, 5 règles |
| Intégration workflows | ✅ | `_valider_donnees()` intégré |
| Tests unitaires | ✅ | 12 tests, 0 failures |
| Documentation | ✅ | README + démo + inline comments |

**Économie attendue**: **60-65%** des coûts API ✅

---

## Références

- **Code source**: `execution/gestionnaires/orchestrateur.py` (lignes 893-1024)
- **Tests**: `tests/test_orchestrateur.py`
- **Démo**: `execution/gestionnaires/demo_smart_routing.py`
- **Sprint Plan**: `docs/SPRINT_PLAN_V2.1.md` (JOUR 1 MATIN)

---

**Auteur**: Sprint Team Notomai
**Date**: 11 février 2026
**Version**: 2.1.0
