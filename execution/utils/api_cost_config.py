# -*- coding: utf-8 -*-
"""
Configuration optimisation coûts API Anthropic.

Tier 1+2 optimizations (-93% coûts):
- Max tokens par agent (éviter outputs trop longs)
- System prompt caching
- Model selection par complexité

Version: 2.1.0
Date: 2026-02-11
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ConfigAgent:
    """Configuration d'un agent pour optimisation coûts."""
    nom: str
    modele_defaut: str  # "opus", "sonnet", "haiku"
    max_tokens: int
    cache_system_prompt: bool
    timeout_seconds: int


# =============================================================================
# Max Tokens par Agent (Tier 1 - Output Optimization)
# =============================================================================

MAX_TOKENS_PAR_AGENT: Dict[str, int] = {
    # Orchestrateur (coordonne tout, needs context)
    "workflow-orchestrator": 4096,

    # Agents avec outputs structurés (JSON)
    "clause-suggester": 2048,      # 3-5 clauses + justifications
    "post-generation-reviewer": 1024,  # QA report structuré
    "template-auditor": 1024,      # Conformité report
    "cadastre-enricher": 512,      # Données cadastrales enrichies
    "data-collector-qr": 512,      # Questions + réponses
    "schema-validator": 512,       # Validation errors
}

# Default si agent non listé
MAX_TOKENS_DEFAULT = 2048


# =============================================================================
# Configuration Agents (complète)
# =============================================================================

CONFIGS_AGENTS: Dict[str, ConfigAgent] = {
    "workflow-orchestrator": ConfigAgent(
        nom="workflow-orchestrator",
        modele_defaut="opus",  # Complexe, mais peut fallback Sonnet
        max_tokens=4096,
        cache_system_prompt=True,
        timeout_seconds=60
    ),

    "clause-suggester": ConfigAgent(
        nom="clause-suggester",
        modele_defaut="opus",  # Nécessite raisonnement avancé
        max_tokens=2048,
        cache_system_prompt=True,  # Catalogue clauses cachable
        timeout_seconds=30
    ),

    "post-generation-reviewer": ConfigAgent(
        nom="post-generation-reviewer",
        modele_defaut="sonnet",  # QA peut être Sonnet
        max_tokens=1024,
        cache_system_prompt=False,
        timeout_seconds=15
    ),

    "template-auditor": ConfigAgent(
        nom="template-auditor",
        modele_defaut="sonnet",
        max_tokens=1024,
        cache_system_prompt=True,  # Template ref cachable
        timeout_seconds=20
    ),

    "data-collector-qr": ConfigAgent(
        nom="data-collector-qr",
        modele_defaut="sonnet",
        max_tokens=512,
        cache_system_prompt=True,  # Schema questions cachable
        timeout_seconds=45
    ),

    "cadastre-enricher": ConfigAgent(
        nom="cadastre-enricher",
        modele_defaut="haiku",  # Simple API call
        max_tokens=512,
        cache_system_prompt=False,
        timeout_seconds=10
    ),

    "schema-validator": ConfigAgent(
        nom="schema-validator",
        modele_defaut="haiku",  # Validation simple
        max_tokens=512,
        cache_system_prompt=False,
        timeout_seconds=10
    ),
}


# =============================================================================
# System Prompts Cachables (Tier 2 - Prompt Caching)
# =============================================================================

def get_cachable_system_prompt(agent_name: str, catalogue_data: Any = None) -> List[Dict[str, Any]]:
    """
    Retourne le system prompt structuré pour caching Anthropic.

    Format Anthropic:
    system=[
        {"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": "..."}  # Pas caché
    ]

    Args:
        agent_name: Nom de l'agent
        catalogue_data: Données de catalogue (clauses, sections, etc.)

    Returns:
        Liste de blocs system prompt
    """
    config = CONFIGS_AGENTS.get(agent_name)

    if not config or not config.cache_system_prompt:
        # Pas de caching
        return []

    # Prompts de base (toujours cachés)
    base_prompts = {
        "workflow-orchestrator": """You are the workflow orchestrator for Notomai, a French notarial document generation system.

Your role:
- Parse notary requests (natural language → structured intent)
- Plan optimal execution strategy (parallel/sequential/auto)
- Coordinate 5+ specialized agents
- Aggregate results and make go/no-go decisions
- Generate comprehensive performance reports

3-layer architecture:
1. Directives (Markdown SOPs)
2. Orchestration (YOU - intelligent routing)
3. Execution (Python scripts)

Key principles:
- Use parallel execution when possible (3-5x speedup)
- Fallback gracefully on agent failures
- Validate data quality at each step
- Return structured JSON outputs
""",

        "clause-suggester": """You are the clause suggestion expert for Notomai.

Your role:
- Analyze acte context (price, parties, property type, loan)
- Suggest 3-5 relevant clauses from catalog (45+ available)
- Score each clause 0-100 based on relevance
- Provide legal justification (Code Civil articles)
- Prioritize: CRITIQUE (mandatory) > RECOMMANDÉE > OPTIONNELLE

Catalog includes:
- Suspensive conditions (loan, sale, urbanism)
- Guarantees (bank, deposit)
- Special clauses (penalty, substitution)
- Viager-specific (rent, DUH, health)

Return structured JSON with scores and justifications.
""",

        "template-auditor": """You are the template conformity auditor for Notomai.

Your role:
- Compare generated template vs original trame
- Verify structure conformity ≥80%
- Check all bookmarks are guarded with {% if %}
- Validate no Jinja2 syntax in final output
- Report missing sections and unguarded variables

Templates must match original notarial documents exactly.
Quality threshold: ≥80% for PROD deployment.
""",

        "data-collector-qr": """You are the interactive data collector for Notomai.

Your role:
- Follow schema-driven questions (97 questions, 21 sections)
- Auto-prefill 64% from existing data
- Skip conditional questions (e.g., spouse if single)
- Validate responses in real-time
- Handle viager-specific questions (section 15_viager)

Modes:
- CLI: interactive prompts
- API: prefill_only (no user interaction)

Return structured data matching schema exactly.
"""
    }

    base_text = base_prompts.get(agent_name, "")

    # Construire les blocs
    blocks = []

    if base_text:
        blocks.append({
            "type": "text",
            "text": base_text,
            "cache_control": {"type": "ephemeral"}
        })

    # Ajouter catalogue si fourni
    if catalogue_data and agent_name == "clause-suggester":
        import json
        blocks.append({
            "type": "text",
            "text": f"CATALOGUE CLAUSES:\n{json.dumps(catalogue_data, ensure_ascii=False, indent=2)}",
            "cache_control": {"type": "ephemeral"}
        })

    return blocks


# =============================================================================
# Fonctions utilitaires
# =============================================================================

def get_max_tokens(agent_name: str) -> int:
    """Retourne max_tokens pour un agent."""
    return MAX_TOKENS_PAR_AGENT.get(agent_name, MAX_TOKENS_DEFAULT)


def get_model(agent_name: str, fallback_sonnet: bool = False) -> str:
    """
    Retourne le modèle à utiliser pour un agent.

    Args:
        agent_name: Nom de l'agent
        fallback_sonnet: Si True, utilise Sonnet au lieu d'Opus (économie)

    Returns:
        "claude-opus-4-6", "claude-sonnet-4-5", ou "claude-haiku-4-5"
    """
    config = CONFIGS_AGENTS.get(agent_name)
    if not config:
        return "claude-sonnet-4-5"  # Default safe

    model = config.modele_defaut

    # Fallback Opus → Sonnet (économie 60%)
    if fallback_sonnet and model == "opus":
        model = "sonnet"

    # Mapping vers model IDs Anthropic
    mapping = {
        "opus": "claude-opus-4-6",
        "sonnet": "claude-sonnet-4-5",
        "haiku": "claude-haiku-4-5"
    }

    return mapping.get(model, "claude-sonnet-4-5")


def get_timeout(agent_name: str) -> int:
    """Retourne timeout en secondes pour un agent."""
    config = CONFIGS_AGENTS.get(agent_name)
    return config.timeout_seconds if config else 30


def should_cache(agent_name: str) -> bool:
    """Retourne si l'agent doit utiliser le prompt caching."""
    config = CONFIGS_AGENTS.get(agent_name)
    return config.cache_system_prompt if config else False


# =============================================================================
# Coûts estimés (tracking)
# =============================================================================

COUT_PAR_1M_TOKENS = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0, "cached": 1.5},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0, "cached": 0.3},
    "claude-haiku-4-5": {"input": 0.25, "output": 1.25, "cached": 0.025}
}


def estimer_cout(
    model: str,
    tokens_input: int,
    tokens_output: int,
    tokens_cached: int = 0
) -> float:
    """
    Estime le coût d'un appel API.

    Args:
        model: Model ID Anthropic
        tokens_input: Tokens d'input
        tokens_output: Tokens d'output
        tokens_cached: Tokens cachés (input)

    Returns:
        Coût en USD
    """
    tarifs = COUT_PAR_1M_TOKENS.get(model)
    if not tarifs:
        return 0.0

    cout_input = (tokens_input - tokens_cached) * tarifs["input"] / 1_000_000
    cout_cached = tokens_cached * tarifs["cached"] / 1_000_000
    cout_output = tokens_output * tarifs["output"] / 1_000_000

    return cout_input + cout_cached + cout_output


# =============================================================================
# Tests
# =============================================================================

if __name__ == '__main__':
    print("💰 Tests configuration coûts API\n")

    # Test 1: Max tokens
    print("1️⃣  Max tokens par agent:")
    for agent, max_t in MAX_TOKENS_PAR_AGENT.items():
        print(f"   {agent:30s} → {max_t:5d} tokens")

    # Test 2: Modèles
    print("\n2️⃣  Sélection modèles:")
    agents_test = ["workflow-orchestrator", "clause-suggester", "cadastre-enricher"]
    for agent in agents_test:
        model_normal = get_model(agent, fallback_sonnet=False)
        model_fallback = get_model(agent, fallback_sonnet=True)
        print(f"   {agent:30s} → {model_normal:25s} (fallback: {model_fallback})")

    # Test 3: Estimation coûts
    print("\n3️⃣  Estimation coûts:")
    scenarios = [
        ("Opus full", "claude-opus-4-6", 10000, 3000, 0),
        ("Opus cached", "claude-opus-4-6", 10000, 3000, 8000),
        ("Sonnet full", "claude-sonnet-4-5", 10000, 3000, 0),
        ("Sonnet cached", "claude-sonnet-4-5", 10000, 3000, 8000),
    ]

    for nom, model, input_t, output_t, cached_t in scenarios:
        cout = estimer_cout(model, input_t, output_t, cached_t)
        print(f"   {nom:20s} → ${cout:.4f}")

    # Test 4: Prompts cachables
    print("\n4️⃣  Agents avec caching:")
    for agent, config in CONFIGS_AGENTS.items():
        if config.cache_system_prompt:
            print(f"   ✅ {agent}")

    print("\n✅ Tests terminés")
