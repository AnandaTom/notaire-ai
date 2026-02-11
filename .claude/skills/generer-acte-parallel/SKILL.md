---
name: generer-acte-parallel
description: Generate notarial deed using PARALLEL agent coordination (Opus 4.6 Agent Teams). 3-5x faster than sequential. Use when user says "generer acte parallel", "generation parallele", "fast generation", "agent teams".
disable-model-invocation: true
allowed-tools: Task, Bash, Read, Write, Grep, Glob
---

# Generate Notarial Deed - Parallel Mode (Opus 4.6)

Generate a complete notarial deed using **parallel agent coordination** for 3-5x speedup.

## Arguments
- `$ARGUMENTS` - The type and context, e.g., "promesse Martin→Dupont 67m² Paris 450k€" or "vente avec mobilier"

## How It Works (Agent Teams)

This skill spawns the **workflow-orchestrator** agent (Opus 4.6) which coordinates 5+ specialized agents in parallel:

```
START
  ├─ [Agent 1] cadastre-enricher (Haiku)      ┐
  ├─ [Agent 2] data-collector-qr (Sonnet)      ├─ PARALLEL (3-5s)
  ├─ [Agent 3] template-auditor (Sonnet)       ┘
  └─ WAIT ALL →
      ├─ [Agent 4] schema-validator (Haiku)    ← Sequential (2s)
      └─ IF PASS →
          ├─ Assemble Jinja2 (1.5s)
          ├─ [Agent 5] clause-suggester (Opus) ← Parallel with export (2s)
          ├─ Export DOCX (3.5s)
          └─ [Agent 6] post-generation-reviewer (Sonnet) ← Final QA (1s)
END

Total: ~8s (vs ~20s sequential)
```

## Workflow

### Step 1: Parse Request & Spawn Orchestrator

```markdown
I'm going to generate your acte using parallel agent coordination (Opus 4.6).

Parsing request: "$ARGUMENTS"
```

Use the **Task tool** to spawn the workflow-orchestrator:

```
Task(
  agent_type="workflow-orchestrator",
  description="Orchestrate parallel acte generation",
  prompt="""
  Generate a complete notarial deed with these specifications:

  Request: $ARGUMENTS

  Use FULL PARALLEL strategy:
  1. Parse request → extract type, parties, bien, prix
  2. Spawn agents in parallel:
     - cadastre-enricher (enrich address/cadastre via API)
     - data-collector-qr (collect missing data, auto mode if possible)
     - template-auditor (verify template conformity >=80%)
  3. Wait for all → schema-validator
  4. If PASS → Assemble + clause-suggester (parallel) + Export
  5. post-generation-reviewer (final QA)
  6. Return comprehensive report with:
     - Execution time per agent
     - Speedup vs sequential
     - QA score
     - Final file path

  IMPORTANT:
  - Use parallel execution for maximum speed
  - If an agent fails, log warning and continue (unless critical)
  - Return detailed performance metrics
  """
)
```

### Step 2: Monitor Orchestrator

The orchestrator will return a structured result:

```json
{
  "status": "SUCCESS",
  "workflow_id": "wf-20260211-143052",
  "duration_seconds": 7.8,
  "speedup_vs_sequential": 2.6,

  "agents_executed": [
    {"name": "cadastre-enricher", "status": "success", "duration_ms": 487},
    {"name": "data-collector-qr", "status": "success", "duration_ms": 3214},
    {"name": "template-auditor", "status": "success", "duration_ms": 1821},
    {"name": "schema-validator", "status": "success", "duration_ms": 124},
    {"name": "clause-suggester", "status": "success", "duration_ms": 1650},
    {"name": "post-generation-reviewer", "status": "success", "duration_ms": 892}
  ],

  "output": {
    "file_path": "outputs/promesse_Martin_Dupont_20260211.docx",
    "file_size_kb": 92,
    "pages": 24,
    "qa_score": 94,
    "qa_status": "PASS"
  },

  "data_quality": {
    "completion": 100,
    "validation_errors": 0,
    "warnings": 3
  },

  "suggestions": [
    {
      "clause": "Condition suspensive d'obtention de prêt",
      "score": 95,
      "justification": "Prêt de 350k€ → obligatoire (art. 1589-1)"
    }
  ]
}
```

### Step 3: Present Results to User

Format the orchestrator's output into a user-friendly report:

```markdown
## ✅ Acte Généré en Mode Parallèle

**Type**: Promesse de vente
**Parties**: Martin → Dupont
**Bien**: 67m² Paris 15e
**Prix**: 450 000€

---

### ⚡ Performance

- **Durée totale**: 7.8s
- **Mode**: Parallèle (6 agents)
- **Speedup**: **2.6x plus rapide** vs séquentiel (20.3s)
- **Time saved**: 12.5s

---

### 🤖 Agents Exécutés

| Agent | Status | Durée | Rôle |
|-------|--------|-------|------|
| cadastre-enricher | ✅ | 487ms | Enrichissement cadastre API |
| data-collector-qr | ✅ | 3.2s | Collecte données (64% pré-rempli) |
| template-auditor | ✅ | 1.8s | Vérification conformité 88.9% |
| schema-validator | ✅ | 124ms | Validation cohérence |
| clause-suggester | ✅ | 1.7s | Suggestions clauses (3) |
| post-generation-reviewer | ✅ | 892ms | QA final |

**Exécution parallèle**: Agents 1-3 simultanés = gain 5.2s

---

### 📋 Qualité

**Score QA**: 94/100 ✅

- ✅ 298/298 bookmarks remplis
- ✅ Quotités = 100%
- ✅ Formatage conforme
- ⚠️ 3 avertissements mineurs:
  - Diagnostic termites manquant (zone non concernée)
  - Indemnité 11% prix (élevé mais légal)
  - CNI ancienne (>10 ans, renouvellement recommandé)

---

### 💡 Clauses Suggérées (3)

#### 🔴 CRITIQUE: Condition suspensive d'obtention de prêt [Score: 95]
Prêt de 350k€ → obligatoire (art. 1589-1 Code Civil)

#### 🟡 RECOMMANDÉE: Garantie bancaire [Score: 65]
Prix >500k€ → sécurisation vendeur recommandée

#### 🟢 OPTIONNELLE: Clause pénale [Score: 45]
Dissuasion abandon (10% prix suggéré)

---

### 📁 Fichier Généré

**Chemin**: [outputs/promesse_Martin_Dupont_20260211.docx](outputs/promesse_Martin_Dupont_20260211.docx)
**Taille**: 92 KB
**Pages**: 24

---

### 📊 Comparaison Mode Sequential vs Parallèle

| Métrique | Séquentiel | Parallèle | Gain |
|----------|-----------|-----------|------|
| Durée | 20.3s | **7.8s** | **-61%** ⚡ |
| Agents | 6 (séquence) | 6 (3 parallel) | - |
| QA Score | 91/100 | **94/100** | +3% |
| User wait time | 20.3s | **7.8s** | **-12.5s** |

---

## 🎉 Prêt pour livraison !

Le document a passé tous les contrôles qualité et est prêt à être téléchargé par le notaire.
```

---

## Advanced Options

### Option 1: Specify Strategy
```
/generer-acte-parallel promesse "Martin→Dupont" --strategy=sequential
```
Forces sequential execution (debugging, agent failures)

### Option 2: Disable Specific Agents
```
/generer-acte-parallel vente --no-clauses
```
Skip clause-suggester (faster, no suggestions)

### Option 3: Verbose Mode
```
/generer-acte-parallel promesse --verbose
```
Show detailed agent logs and intermediate results

---

## When to Use Parallel vs Sequential

### ✅ Use Parallel (Default)
- Standard promesse/vente generation
- All agents available and functional
- Need fast turnaround (<10s)
- Production environment

### ⚠️ Use Sequential (Fallback)
- Debugging specific agent issues
- Agent failures or timeouts
- Need detailed step-by-step logs
- Development/testing environment

---

## Error Handling

### Scenario 1: Non-Critical Agent Fails
```
⚠️ Agent cadastre-enricher failed (timeout 5s)
→ Continuing with existing data
→ Warning: Cadastre non enrichi - API gouv indisponible
```
**Action**: Continue workflow, log warning

### Scenario 2: Critical Agent Fails
```
❌ Agent schema-validator failed
→ Attempting retry (1/1)...
→ Retry successful
✅ Continuing workflow
```
**Action**: Retry once, then escalate

### Scenario 3: QA Blocks Delivery
```
🔴 post-generation-reviewer: BLOCKED
→ 2 erreurs critiques détectées:
  - Bookmark vide: vendeur_conjoint_nom
  - Quotités acquises = 150% (≠ 100%)
→ Action: Corriger données et relancer
```
**Action**: Return errors, don't generate file

---

## Performance Targets

| Acte Type | Sequential | Parallel | Target Speedup |
|-----------|-----------|----------|---------------|
| Promesse standard | 15-20s | **5-8s** | **2.5-3x** |
| Vente standard | 18-25s | **6-10s** | **2.5-3x** |
| Titre → Promesse | 20-30s | **8-15s** | **2-3x** |
| Règlement copro | 12-18s | **4-7s** | **2.5-3x** |

---

## Critical Rules

1. **Always read `directives/workflow_notaire.md` first**
2. **Use Task tool to spawn workflow-orchestrator** (Opus model)
3. **Never modify agents or templates directly** - they're production code
4. **Report performance metrics** to user (speedup, time saved)
5. **Show QA score and warnings** - transparency on quality
6. **If orchestrator fails** → fallback to `/generer-acte` (sequential)

---

## Troubleshooting

### Orchestrator Timeout (>30s)
```bash
# Check if agents are stuck
ps aux | grep python

# Kill hung processes
pkill -f "agent_autonome.py"

# Retry with sequential
/generer-acte promesse "same args"
```

### Agent Not Found
```
Error: Agent 'cadastre-enricher' not found
```
**Fix**: Verify `.claude/agents/cadastre-enricher.md` exists

### Parallel Execution Not Working
```
Warning: Parallel execution disabled - using sequential fallback
```
**Reason**: Claude Code agent teams in research preview, may not be available
**Action**: Sequential mode auto-activated

---

## References
- **Agents**: `.claude/agents/*.md` - 6 specialized agents
- **Workflow Guide**: `directives/workflow_notaire.md`
- **Architecture**: `CLAUDE.md` - 3-layer system
- **Performance**: This skill targets 2.5-3x speedup via parallelization
