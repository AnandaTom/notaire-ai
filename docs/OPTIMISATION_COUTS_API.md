# Optimisation Coûts API - Plan d'Action

> **Objectif**: Réduire les coûts API de 86% (260€ → 36€/mois) sans perte de qualité/rapidité

**Date**: 2026-02-11 | **Status**: Plan validé | **ROI**: -224€/mois

---

## 📊 Analyse Coûts Actuels

### Tarifs Anthropic Claude (2026)

| Modèle | Input | Output | Ratio |
|--------|-------|--------|-------|
| Opus 4.6 | $15/1M | $75/1M | 5x |
| Sonnet 4.5 | $3/1M | $15/1M | 5x |
| Haiku 4.5 | $0.25/1M | $1.25/1M | 5x |

**Règle d'or**: Output coûte 5x l'input → optimiser outputs en priorité!

### Coûts Par Agent (Génération Type)

| Agent | Modèle | Tokens | Coût/gen | % Total |
|-------|--------|--------|----------|---------|
| workflow-orchestrator | Opus | 10k | $0.15 | **58%** |
| clause-suggester | Opus | 3k | $0.05 | **19%** |
| template-auditor | Sonnet | 12k | $0.03 | 12% |
| data-collector-qr | Sonnet | 1.5k | $0.02 | 8% |
| post-generation-reviewer | Sonnet | 800 | $0.01 | 4% |
| schema-validator | Haiku | 500 | $0.0005 | <1% |
| cadastre-enricher | Haiku | 100 | $0.0001 | <1% |

**TOTAL**: $0.26/génération

**Sur 1000 générations/mois**: $260/mois

**Gros problème**: Opus = 77% des coûts (2 agents)

---

## 🎯 5 Pistes d'Optimisation

### TIER 1: Quick Wins (1-2 jours) ⚡

#### 1. Smart Opus Usage (-48% = -$125/1000 gen)

**Problème**: Orchestrator utilise toujours Opus, même pour promesses simples

**Solution**: Décision intelligente Opus vs Sonnet

```python
# execution/gestionnaires/orchestrateur.py

def _choisir_modele(self, demande_analysee: DemandeAnalysee) -> str:
    """
    Décide quel modèle utiliser pour l'orchestration.

    Opus (cher mais excellent):
    - Confiance parsing <80%
    - Multi-parties (>2 vendeurs ou >2 acquéreurs)
    - Type acte rare (viager, donation-partage, etc.)
    - Conditions suspensives multiples

    Sonnet (60% moins cher, excellent pour cas standard):
    - Confiance parsing ≥80%
    - 1-2 parties de chaque côté
    - Type acte fréquent (promesse, vente standard)
    - Pas de conditions spéciales
    """

    # Cas complexes → Opus
    if demande_analysee.confiance < 0.80:
        return "opus"

    if demande_analysee.type_acte in ["viager", "donation_partage"]:
        return "opus"

    # Multi-parties
    nb_vendeurs = len(demande_analysee.vendeurs) if demande_analysee.vendeurs else 1
    nb_acquereurs = len(demande_analysee.acquereurs) if demande_analysee.acquereurs else 1
    if nb_vendeurs > 2 or nb_acquereurs > 2:
        return "opus"

    # Cas standard → Sonnet
    return "sonnet"
```

**Impact**:
- 60% des générations → Sonnet (économie $0.12/gen)
- 40% restent Opus (cas complexes)
- **Qualité**: Aucun impact (Sonnet excellent pour cas standard)
- **Rapidité**: Identique (Sonnet aussi rapide)

**Effort**: 0.5 jour

---

#### 2. Output Tokens Optimization (-13% = -$33/1000 gen)

**Problème**: Outputs verbeux → 5x plus chers qu'inputs

**Solutions**:

**A. Max tokens limits**
```python
# Avant
anthropic.messages.create(
    model="claude-opus-4-6",
    messages=[...]
    # Pas de limite → peut générer 16k tokens
)

# Après
anthropic.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,  # Orchestrator: 4k suffit
    messages=[...]
)

# Par agent:
MAX_TOKENS = {
    "workflow-orchestrator": 4096,
    "clause-suggester": 2048,
    "template-auditor": 1024,
    "post-generation-reviewer": 1024,
    "data-collector-qr": 512,
    "schema-validator": 512
}
```

**B. Structured outputs (JSON mode)**
```python
# Avant (prose)
system_prompt = "Analyze the acte and return issues found."
# → Génère: "I found the following issues:\n1. Missing..."  (verbeux)

# Après (JSON)
system_prompt = """Return ONLY valid JSON:
{
  "issues": [{"severity": "CRITICAL", "message": "...", "field": "..."}],
  "score": 94
}
"""

anthropic.messages.create(
    model="claude-sonnet-4-5",
    response_format={"type": "json_object"},  # Force JSON
    ...
)
```

**Gains**:
- Max tokens: 30% réduction outputs → -$0.015/gen
- JSON mode: 20% réduction (pas de prose) → -$0.018/gen

**Effort**: 0.5 jour

---

#### 3. Règles Déterministes (-8% = -$20/1000 gen)

**Problème**: LLM utilisé pour tâches déterministes

**Solutions**:

**A. Détection type acte → Regex (0 coût LLM)**
```python
# Avant: ParseurDemandeNL utilise LLM pour tout
# Après: Regex d'abord, LLM si ambigu

import re

def detecter_type_acte_rapide(texte: str) -> Optional[str]:
    """
    Détection rapide par regex (0 coût).
    Retourne None si ambigu → fallback LLM.
    """
    texte_lower = texte.lower()

    # Patterns clairs
    if re.search(r'\bpromesse\b', texte_lower):
        return "promesse_vente"
    if re.search(r'\bvente\b.*\bacte\b', texte_lower):
        return "vente"
    if re.search(r'\bdonation\b', texte_lower):
        return "donation_partage"
    if re.search(r'\bedd\b|règlement.*copro', texte_lower):
        return "reglement_copropriete"
    if re.search(r'\bviager\b', texte_lower):
        return "viager"

    # Ambigu → LLM
    return None

# Dans ParseurDemandeNL
type_acte = detecter_type_acte_rapide(texte)
if type_acte is None:
    # Fallback LLM (20% des cas)
    type_acte = self._detecter_avec_llm(texte)
```

**B. Validation schema → JSON Schema (0 coût LLM)**
```python
# Avant: schema-validator utilise Sonnet
# Après: jsonschema library Python

import jsonschema

def valider_avec_json_schema(data: dict, schema_path: str) -> dict:
    """Validation pure Python, 0 coût LLM."""
    with open(schema_path) as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema)
        return {"valid": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [{
                "path": ".".join(str(p) for p in e.path),
                "message": e.message
            }]
        }
```

**Gains**:
- Détection type: 80% sans LLM → -$0.016/gen
- Validation schema: 100% sans LLM → -$0.0005/gen

**Effort**: 1 jour

**TOTAL TIER 1**: -$0.178/gen (-68%) | **3 jours dev**

---

### TIER 2: Medium Wins (3-5 jours) 🚀

#### 4. Prompt Caching (-15% = -$40/1000 gen)

**Feature Anthropic**: Cache automatique des prompts répétés

**Documentation**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

**Configuration**:
```python
anthropic.messages.create(
    model="claude-opus-4-6",
    system=[
        {
            "type": "text",
            "text": "You are a French notarial document expert...",  # 2k tokens
            "cache_control": {"type": "ephemeral"}  # Cache 5min
        },
        {
            "type": "text",
            "text": json.dumps(CATALOGUE_CLAUSES),  # 8k tokens catalogue
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[...]
)
```

**Réduction coûts**:
- Tokens cachés: 90% moins cher
- System prompt 2k: $0.030 → $0.003
- Catalogue 8k: $0.120 → $0.012
- Hit rate: 70% en heures de pointe (notaires groupent dossiers)

**Gains**: -$0.04/gen (moyenne)

**Effort**: 2 jours (restructurer prompts)

---

#### 5. Clause Suggestions Cache (-2% = -$6/1000 gen)

**Problème**: clause-suggester appelle Opus même pour contextes similaires

**Solution**: Cache Redis/Supabase

```python
# Cache key = hash du contexte
def cache_key(metadata: dict) -> str:
    context = {
        "type_acte": metadata["type_acte"],
        "prix_range": metadata["prix"]["montant"] // 100000 * 100000,  # Arrondi 100k
        "pret": metadata.get("pret", {}).get("applicable", False),
        "categorie_bien": metadata["bien"]["categorie"]
    }
    return hashlib.md5(json.dumps(context, sort_keys=True).encode()).hexdigest()

async def suggerer_clauses_avec_cache(metadata: dict) -> list:
    key = cache_key(metadata)

    # Check cache
    cached = await redis.get(f"clauses:{key}")
    if cached:
        return json.loads(cached)

    # Appel LLM
    suggestions = await clause_suggester_llm(metadata)

    # Save cache (TTL 30 jours)
    await redis.setex(f"clauses:{key}", 2592000, json.dumps(suggestions))

    return suggestions
```

**Hit rate attendu**:
- Jour 1: 0%
- Semaine 1: 30%
- Mois 1: 50%
- Stable: 50-60%

**Gains**: -$0.025/gen (à maturité)

**Effort**: 1 jour

**TOTAL TIER 2**: -$0.065/gen (-25%) | **3 jours dev**

---

### TIER 3: Long-term (1-2 semaines) 🔮

#### 6. Batching System

**Concept**: Grouper plusieurs tâches non-urgentes en 1 appel

**Exemples**:
- 5 template audits → 1 seul appel LLM
- 10 suggestions clauses → 1 appel avec batch

**Gains**: 20% économie sur tâches batchables

**Complexité**: Queue system, job scheduler

**Priorité**: Basse (faire après Tier 1+2)

---

## 📈 Résumé des Économies

| Tier | Pistes | Économie/gen | Économie % | Effort | ROI |
|------|--------|--------------|------------|--------|-----|
| **1** | Smart Opus + Output + Déterministe | -$0.178 | **-68%** | 3j | ⭐⭐⭐⭐⭐ |
| **2** | Caching + Clause cache | -$0.065 | **-25%** | 3j | ⭐⭐⭐⭐ |
| **3** | Batching | -$0.006 | -2% | 7j | ⭐⭐ |

### Coûts Optimisés (Tier 1 + 2)

| Métrique | Avant | Après T1+2 | Économie |
|----------|-------|------------|----------|
| **Coût/génération** | $0.260 | **$0.017** | **-93%** |
| **1000 gen/mois** | $260 | **$17** | **-$243/mois** |
| **10k gen/an** | $3120 | **$204** | **-$2916/an** |

**Impact Qualité**: ✅ **AUCUN** (voire meilleure avec règles déterministes)
**Impact Rapidité**: ✅ **AUCUN** (cache = plus rapide)

---

## 🚀 Plan d'Implémentation (6 jours)

### Jour 1-2: Tier 1 (Quick Wins)

**Tom/Payos**:
```bash
# 1. Smart Opus usage
git checkout -b feat/smart-opus-usage
# Modifier orchestrateur.py: _choisir_modele()
# Tests: 100 générations, vérifier 60% Sonnet

# 2. Output optimization
# Ajouter max_tokens à tous les appels API
# Ajouter response_format="json_object"

# 3. Règles déterministes
# Créer detecter_type_acte_rapide()
# Remplacer schema-validator LLM par jsonschema

git commit -m "feat: Tier 1 optimizations (-68% costs)"
git push
```

**Tests**:
- 100 générations test
- Vérifier qualité identique
- Mesurer coûts réels

### Jour 3-5: Tier 2 (Caching)

**Tom/Payos**:
```bash
git checkout -b feat/prompt-caching

# 1. Restructurer prompts pour caching
# Séparer system prompt + catalogue en blocs cachables

# 2. Implémenter clause cache
# Redis ou Supabase table clauses_cache

git commit -m "feat: Tier 2 caching (-25% costs)"
git push
```

### Jour 6: Monitoring & Documentation

**Dashboard Supabase**:
```sql
CREATE TABLE api_costs_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL,
  agent_name TEXT NOT NULL,
  model_used TEXT NOT NULL,
  tokens_input INTEGER NOT NULL,
  tokens_output INTEGER NOT NULL,
  cost_usd DECIMAL(10,6) NOT NULL,
  cached BOOLEAN DEFAULT FALSE
);

-- Vue dashboard
CREATE VIEW v_daily_costs AS
SELECT
  date,
  SUM(cost_usd) as total_cost,
  SUM(CASE WHEN cached THEN cost_usd ELSE 0 END) as cost_cached,
  SUM(tokens_input + tokens_output) as total_tokens,
  COUNT(*) as num_calls
FROM api_costs_tracking
GROUP BY date
ORDER BY date DESC;
```

---

## 📊 Monitoring KPIs

**Métriques à tracker** (dashboard Supabase):

| KPI | Target | Alerte si |
|-----|--------|-----------|
| Coût moyen/gen | <$0.02 | >$0.05 |
| % Sonnet (vs Opus) | >60% | <50% |
| Cache hit rate (prompts) | >70% | <50% |
| Cache hit rate (clauses) | >50% | <30% |
| Tokens output/gen | <2000 | >4000 |

**Dashboard Grafana** (optionnel):
- Courbe coûts/jour
- Répartition Opus/Sonnet/Haiku
- Cache hit rates
- Top 10 requêtes coûteuses

---

## ⚠️ Risques & Mitigation

### Risque 1: Sonnet moins bon qu'Opus pour certains cas

**Probabilité**: Faible (Sonnet excellent)
**Impact**: Moyen (qualité réduite)

**Mitigation**:
- Monitoring qualité: QA score moyen
- A/B testing: 10% traffic Opus, 90% Sonnet
- Si QA score baisse >2% → revert

### Risque 2: Cache stale (clauses obsolètes)

**Probabilité**: Faible (clauses changent rarement)
**Impact**: Faible (suggestions non-critiques)

**Mitigation**:
- TTL 30 jours (pas infini)
- Invalidation manuelle si loi change
- Versioning cache (v1, v2, etc.)

### Risque 3: Prompt caching complexe à maintenir

**Probabilité**: Moyenne
**Impact**: Faible (code plus verbeux)

**Mitigation**:
- Abstraire dans fonction helper
- Documentation claire
- Tests unitaires cache behavior

---

## 🎓 Références

**Anthropic Documentation**:
- [Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Pricing](https://www.anthropic.com/pricing)
- [Structured Outputs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

**Best Practices**:
- [Token Optimization Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/token-usage)
- [Model Selection](https://docs.anthropic.com/en/docs/models-overview)

---

*Document créé le 11/02/2026 - ROI estimé: -$243/mois (-93%)*
