# -*- coding: utf-8 -*-
"""
Agent LLM - Cerveau intelligent de NotaireAI

Remplace le keyword matching de chat_handler.py par un vrai agent
Anthropic Messages API avec 9 tools qui wrappent les fonctions Python existantes.

Usage:
    from execution.agent_llm import run_agent, build_system_prompt

    messages = [{"role": "user", "content": "Bonjour, promesse pour un appart"}]
    result = run_agent(messages, build_system_prompt(), {"etude_id": "test"})
    print(result["content"])
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Chemin racine du projet
PROJECT_ROOT = Path(__file__).parent.parent


# =============================================================================
# Section A: System Prompt Builder
# =============================================================================

_SYSTEM_PROMPT_CACHE: Optional[str] = None


def _load_file_safe(filepath: Path, max_lines: int = 0) -> str:
    """Charge un fichier texte, retourne '' si introuvable."""
    try:
        text = filepath.read_text(encoding="utf-8")
        if max_lines > 0:
            lines = text.split("\n")
            text = "\n".join(lines[:max_lines])
        return text
    except Exception:
        return ""


def _build_condensed_claude_md() -> str:
    """Extrait les sections essentielles de CLAUDE.md pour le system prompt."""
    full = _load_file_safe(PROJECT_ROOT / "CLAUDE.md")
    if not full:
        return ""

    # Garder les sections cles, supprimer l'historique de versions et le code
    lines = full.split("\n")
    keep = []
    skip_section = False
    for line in lines:
        # Sauter les gros blocs de code et historique de versions
        if any(h in line for h in [
            "## Version 1.2.0", "## Version 1.3.0", "## Version 1.3.1",
            "## Version 1.6.0", "## Version 1.7.0", "## Version 1.8.0",
        ]):
            skip_section = True
            continue
        if skip_section and line.startswith("## ") and "Version" not in line:
            skip_section = False
        if skip_section:
            continue
        # Sauter les blocs de code longs
        if line.startswith("```") and len(keep) > 0 and keep[-1].startswith("```"):
            continue
        keep.append(line)

    return "\n".join(keep[:500])  # Limiter a ~500 lignes


def build_system_prompt() -> str:
    """
    Construit le system prompt complet pour l'agent NotaireAI.
    Cache le resultat apres le premier appel.
    """
    global _SYSTEM_PROMPT_CACHE
    if _SYSTEM_PROMPT_CACHE is not None:
        return _SYSTEM_PROMPT_CACHE

    parts = []

    # Identite et role
    parts.append("""# NotaireAI - Assistant Intelligent pour Actes Notariaux

Tu es NotaireAI, l'assistant intelligent de l'etude notariale. Tu aides les notaires
a generer des actes notariaux (promesses de vente, actes de vente, reglements de
copropriete) 100% conformes aux trames originales.

## Regles imperatives
- TOUJOURS vouvoyer le notaire
- TOUJOURS utiliser les outils disponibles plutot que deviner
- Poser les questions par groupes logiques (3-5 questions maximum par message)
- Valider les donnees AVANT de generer un document
- En cas de doute, DEMANDER plutot que supposer

## Capacites
Tu disposes de 9 outils pour:
1. Detecter automatiquement la categorie de bien (copropriete, hors copro, terrain)
2. Obtenir la liste des questions a poser au notaire
3. Enregistrer les reponses et suivre la progression
4. Valider la coherence des donnees (quotites, prix, champs obligatoires)
5. Generer le document DOCX final
6. Enrichir les donnees cadastrales via les APIs gouvernementales
7. Rechercher des clauses dans le catalogue (45+ clauses)
8. Enregistrer les feedbacks pour amelioration continue

## Workflow de generation
1. Identifier le type d'acte demande
2. Detecter la categorie de bien avec l'outil `detecter_categorie_bien`
3. Charger les questions pertinentes avec `get_sections_list` puis `get_questions_for_section`
4. Poser les questions au notaire section par section
5. Enregistrer les reponses au fur et a mesure
6. Quand les donnees sont suffisantes, valider avec `valider_donnees`
7. Generer le document avec `generer_promesse`
8. Proposer de relire le document section par section

## 3 categories de biens
Le systeme selectionne automatiquement le bon template:
- **Copropriete**: appartement, lots de copro → template avec EDD, syndic, tantiemes
- **Hors copropriete**: maison, villa, local → template sans sections copro
- **Terrain a batir**: terrain, lotissement → template avec viabilisation, permis""")

    # Contexte projet condense
    condensed = _build_condensed_claude_md()
    if condensed:
        parts.append("\n\n## Contexte du projet\n" + condensed[:3000])

    # Workflow notaire (extrait)
    workflow = _load_file_safe(
        PROJECT_ROOT / "directives" / "workflow_notaire.md", max_lines=100
    )
    if workflow:
        parts.append("\n\n## Workflow Notaire (extrait)\n" + workflow)

    _SYSTEM_PROMPT_CACHE = "\n".join(parts)
    return _SYSTEM_PROMPT_CACHE


# =============================================================================
# Section B: Tool Definitions (9 schemas Anthropic format)
# =============================================================================

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "detecter_categorie_bien",
        "description": (
            "Detecte la categorie de bien immobilier (copropriete, hors_copropriete, "
            "terrain_a_batir) a partir des donnees du dossier. Utilise les marqueurs: "
            "syndic/lots/tantiemes pour copro, maison/villa pour hors-copro, "
            "lotissement/viabilisation pour terrain."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "donnees": {
                    "type": "object",
                    "description": "Donnees du bien (bien.type_bien, copropriete.syndic, bien.lotissement, etc.)",
                }
            },
            "required": ["donnees"],
        },
    },
    {
        "name": "detecter_type_promesse",
        "description": (
            "Detection 2 niveaux: categorie de bien + type de transaction "
            "(standard, premium, avec_mobilier, multi_biens). Retourne le template "
            "recommande, confiance, et sections."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "donnees": {
                    "type": "object",
                    "description": "Donnees completes de la promesse.",
                }
            },
            "required": ["donnees"],
        },
    },
    {
        "name": "valider_donnees",
        "description": (
            "Valide les donnees d'une promesse. Verifie les champs obligatoires, "
            "la coherence (quotites = 100%, prix > 0), et retourne erreurs et "
            "champs manquants."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "donnees": {
                    "type": "object",
                    "description": "Donnees de la promesse a valider.",
                }
            },
            "required": ["donnees"],
        },
    },
    {
        "name": "generer_promesse",
        "description": (
            "Genere une promesse de vente DOCX complete. Detecte le type, valide, "
            "selectionne le template par categorie de bien, assemble, et exporte. "
            "Retourne le chemin du fichier DOCX."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "donnees": {
                    "type": "object",
                    "description": (
                        "Donnees completes: promettants, beneficiaires, bien, "
                        "prix, copropriete, conditions_suspensives, etc."
                    ),
                },
                "type_force": {
                    "type": "string",
                    "enum": ["standard", "premium", "avec_mobilier", "multi_biens"],
                    "description": "Forcer un type de promesse specifique (optionnel).",
                },
            },
            "required": ["donnees"],
        },
    },
    {
        "name": "get_sections_list",
        "description": (
            "Retourne la liste des sections du questionnaire Q&R avec progression "
            "(nb_questions, nb_repondues, complete). Utiliser pour guider la collecte "
            "section par section."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type_acte": {
                    "type": "string",
                    "enum": ["promesse_vente", "vente"],
                    "description": "Type d'acte pour charger le bon schema.",
                },
                "donnees_existantes": {
                    "type": "object",
                    "description": "Donnees deja collectees pour calculer la progression.",
                },
            },
            "required": ["type_acte"],
        },
    },
    {
        "name": "get_questions_for_section",
        "description": (
            "Retourne les questions d'une section specifique avec statut "
            "pre-remplissage, type (texte, nombre, oui_non, choix), options, "
            "et valeur actuelle."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type_acte": {
                    "type": "string",
                    "enum": ["promesse_vente", "vente"],
                },
                "section_key": {
                    "type": "string",
                    "description": "Cle de la section (ex: '2_promettant', '5_bien', '7_prix').",
                },
                "donnees_existantes": {
                    "type": "object",
                    "description": "Donnees deja collectees.",
                },
            },
            "required": ["type_acte", "section_key"],
        },
    },
    {
        "name": "enrichir_cadastre",
        "description": (
            "Enrichit les donnees cadastrales via les APIs gouvernementales "
            "francaises (BAN geocoding + API Carto IGN). Geocode l'adresse, "
            "trouve les parcelles, enrichit le dossier."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "donnees": {
                    "type": "object",
                    "description": "Donnees du dossier avec bien.adresse et/ou bien.cadastre.",
                }
            },
            "required": ["donnees"],
        },
    },
    {
        "name": "rechercher_clauses",
        "description": (
            "Recherche des clauses dans le catalogue (45+ clauses, 12 categories). "
            "Cherche par mots-cles. Categories: conditions_suspensives, urbanisme, "
            "servitudes, copropriete, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "mots_cles": {
                    "type": "string",
                    "description": "Mots-cles de recherche (ex: 'pret PTZ', 'preemption').",
                },
                "type_acte": {
                    "type": "string",
                    "enum": ["promesse_vente", "vente", "compromis"],
                    "description": "Filtrer par type d'acte compatible.",
                },
                "limite": {
                    "type": "integer",
                    "description": "Nombre max de resultats (defaut: 5).",
                },
            },
            "required": ["mots_cles"],
        },
    },
    {
        "name": "soumettre_feedback",
        "description": (
            "Enregistre un feedback du notaire dans Supabase pour "
            "l'apprentissage continu. Actions: ajouter, modifier, supprimer, suggerer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ajouter", "modifier", "supprimer", "suggerer"],
                },
                "section_id": {
                    "type": "string",
                    "description": "Section concernee (ex: 'conditions_suspensives').",
                },
                "contenu": {
                    "type": "string",
                    "description": "Contenu du feedback ou texte de la clause.",
                },
                "raison": {
                    "type": "string",
                    "description": "Raison du feedback.",
                },
            },
            "required": ["action", "section_id", "contenu"],
        },
    },
]


# =============================================================================
# Section C: Tool Dispatcher
# =============================================================================


def handle_tool_call(
    tool_name: str, tool_input: Dict[str, Any], context: Dict[str, Any]
) -> str:
    """
    Dispatch un appel d'outil vers la fonction Python correspondante.

    Args:
        tool_name: Nom de l'outil appele par Claude
        tool_input: Parametres de l'outil
        context: Contexte de la conversation (etude_id, supabase, donnees accumulees)

    Returns:
        JSON string avec le resultat
    """
    try:
        if tool_name == "detecter_categorie_bien":
            from execution.gestionnaires.gestionnaire_promesses import (
                GestionnairePromesses,
            )

            g = GestionnairePromesses(supabase_client=context.get("supabase"))
            categorie = g.detecter_categorie_bien(tool_input["donnees"])
            return json.dumps({"categorie": categorie.value}, ensure_ascii=False)

        elif tool_name == "detecter_type_promesse":
            from execution.gestionnaires.gestionnaire_promesses import (
                GestionnairePromesses,
            )

            g = GestionnairePromesses(supabase_client=context.get("supabase"))
            result = g.detecter_type(tool_input["donnees"])
            return json.dumps(
                {
                    "type_promesse": result.type_promesse.value,
                    "categorie_bien": result.categorie_bien.value,
                    "raison": result.raison,
                    "confiance": result.confiance,
                    "sections_recommandees": result.sections_recommandees,
                    "warnings": result.warnings,
                },
                ensure_ascii=False,
            )

        elif tool_name == "valider_donnees":
            from execution.gestionnaires.gestionnaire_promesses import (
                GestionnairePromesses,
            )

            g = GestionnairePromesses(supabase_client=context.get("supabase"))
            v = g.valider(tool_input["donnees"])
            return json.dumps(
                {
                    "valide": v.valide,
                    "erreurs": v.erreurs,
                    "warnings": v.warnings,
                    "champs_manquants": v.champs_manquants,
                    "suggestions": v.suggestions,
                },
                ensure_ascii=False,
            )

        elif tool_name == "generer_promesse":
            from execution.gestionnaires.gestionnaire_promesses import (
                GestionnairePromesses,
                TypePromesse,
            )

            g = GestionnairePromesses(supabase_client=context.get("supabase"))
            type_force = (
                TypePromesse(tool_input["type_force"])
                if tool_input.get("type_force")
                else None
            )
            output_dir = Path(os.getenv("NOTAIRE_OUTPUT_DIR", "outputs"))
            result = g.generer(tool_input["donnees"], type_force, output_dir)
            return json.dumps(
                {
                    "succes": result.succes,
                    "type_promesse": result.type_promesse.value if result.type_promesse else None,
                    "categorie_bien": result.categorie_bien.value if result.categorie_bien else None,
                    "fichier_docx": result.fichier_docx,
                    "sections_incluses": result.sections_incluses,
                    "erreurs": result.erreurs,
                    "warnings": result.warnings,
                    "duree_generation": result.duree_generation,
                },
                ensure_ascii=False,
                default=str,
            )

        elif tool_name == "get_sections_list":
            from execution.agent_autonome import CollecteurInteractif

            c = CollecteurInteractif(
                tool_input["type_acte"],
                prefill=tool_input.get("donnees_existantes", {}),
            )
            sections = c.get_sections_list()
            return json.dumps(sections, ensure_ascii=False)

        elif tool_name == "get_questions_for_section":
            from execution.agent_autonome import CollecteurInteractif

            c = CollecteurInteractif(
                tool_input["type_acte"],
                prefill=tool_input.get("donnees_existantes", {}),
            )
            questions = c.get_questions_for_section(tool_input["section_key"])
            return json.dumps(questions, ensure_ascii=False)

        elif tool_name == "enrichir_cadastre":
            from execution.services.cadastre_service import CadastreService

            svc = CadastreService()
            result = svc.enrichir_cadastre(tool_input["donnees"])
            return json.dumps(result, ensure_ascii=False, default=str)

        elif tool_name == "rechercher_clauses":
            return _rechercher_clauses(tool_input)

        elif tool_name == "soumettre_feedback":
            return _soumettre_feedback(tool_input, context)

        else:
            return json.dumps({"error": f"Outil inconnu: {tool_name}"})

    except Exception as e:
        logger.error(f"Erreur tool {tool_name}: {e}", exc_info=True)
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _rechercher_clauses(tool_input: Dict[str, Any]) -> str:
    """Recherche dans le catalogue de clauses."""
    catalogue_path = PROJECT_ROOT / "schemas" / "clauses_catalogue.json"
    try:
        catalogue = json.loads(catalogue_path.read_text(encoding="utf-8"))
    except Exception:
        return json.dumps({"error": "Catalogue de clauses introuvable"})

    mots = tool_input["mots_cles"].lower().split()
    type_filtre = tool_input.get("type_acte")
    limite = tool_input.get("limite", 5)
    resultats = []

    categories = catalogue.get("categories", catalogue.get("clauses", {}))
    if isinstance(categories, list):
        # Format plat: liste de clauses
        clauses_list = categories
    else:
        # Format imbriqué: categories -> clauses
        clauses_list = []
        for cat_key, cat_val in categories.items():
            if isinstance(cat_val, dict):
                for clause in cat_val.get("clauses", []):
                    clause["_categorie"] = cat_key
                    clauses_list.append(clause)
            elif isinstance(cat_val, list):
                for clause in cat_val:
                    clause["_categorie"] = cat_key
                    clauses_list.append(clause)

    for clause in clauses_list:
        if type_filtre and type_filtre not in clause.get("type_acte", []):
            continue
        text_search = (
            clause.get("nom", "") + " " + clause.get("texte", "")
        ).lower()
        score = sum(1 for m in mots if m in text_search)
        if score > 0:
            resultats.append(
                {
                    "id": clause.get("id"),
                    "nom": clause.get("nom"),
                    "categorie": clause.get("_categorie", ""),
                    "texte_extrait": clause.get("texte", "")[:200],
                    "variables_requises": clause.get("variables_requises", []),
                    "score": score,
                }
            )

    resultats.sort(key=lambda x: x["score"], reverse=True)
    return json.dumps(resultats[:limite], ensure_ascii=False)


def _soumettre_feedback(
    tool_input: Dict[str, Any], context: Dict[str, Any]
) -> str:
    """Enregistre un feedback dans Supabase."""
    supabase = context.get("supabase")
    if not supabase:
        return json.dumps(
            {"succes": False, "message": "Supabase non disponible en mode local."}
        )

    try:
        supabase.table("feedbacks_promesse").insert(
            {
                "etude_id": context.get("etude_id"),
                "section_id": tool_input.get("section_id"),
                "action": tool_input["action"],
                "contenu": tool_input.get("contenu"),
                "raison": tool_input.get("raison", ""),
                "metadata": {"source": "agent_llm"},
            }
        ).execute()
        return json.dumps({"succes": True, "message": "Feedback enregistre."})
    except Exception as e:
        return json.dumps({"succes": False, "message": str(e)})


# =============================================================================
# Section D: Boucle Agent (Anthropic Messages API + Tool Use)
# =============================================================================

# Limite de securite contre les boucles infinies
MAX_ITERATIONS = 10

# Modele par defaut
DEFAULT_MODEL = "claude-sonnet-4-20250514"


def run_agent(
    messages: List[Dict[str, Any]],
    system_prompt: str,
    context: Dict[str, Any],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4096,
) -> Dict[str, Any]:
    """
    Execute la boucle agentic: appelle Claude, gere les tool_use, repete.

    Args:
        messages: Historique de conversation format Anthropic
        system_prompt: Prompt systeme complet
        context: {"etude_id": str, "supabase": client, ...}
        model: Modele Anthropic a utiliser
        max_tokens: Limite de tokens par reponse

    Returns:
        {
            "content": str,          # Reponse texte finale
            "tool_calls_made": int,  # Nombre d'outils appeles
            "tools_used": list,      # Noms des outils utilises
            "usage": dict,           # Tokens consommes
            "fichier_url": str|None, # URL du fichier genere (si applicable)
        }
    """
    try:
        import anthropic
    except ImportError:
        logger.error("Module anthropic non installe")
        return {
            "content": "Erreur: le module Anthropic n'est pas installe.",
            "tool_calls_made": 0,
            "tools_used": [],
            "usage": {},
            "fichier_url": None,
        }

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY non definie")
        return {
            "content": "Erreur: cle API Anthropic non configuree.",
            "tool_calls_made": 0,
            "tools_used": [],
            "usage": {},
            "fichier_url": None,
        }

    client = anthropic.Anthropic(
        api_key=api_key,
        timeout=120.0,     # 2 min max per request (default 600s)
        max_retries=2,     # Built-in retry with backoff on 429/5xx
    )
    iteration = 0
    tools_used = []
    fichier_url = None
    total_input_tokens = 0
    total_output_tokens = 0

    # Copie des messages pour ne pas muter l'original
    messages = list(messages)

    while iteration < MAX_ITERATIONS:
        iteration += 1

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                tools=TOOLS,
                messages=messages,
            )
        except anthropic.APIError as e:
            logger.error(f"Erreur API Anthropic: {e}")
            return {
                "content": f"Erreur de communication avec l'IA: {e}",
                "tool_calls_made": iteration - 1,
                "tools_used": tools_used,
                "usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                },
                "fichier_url": fichier_url,
            }

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Fin de conversation: extraire le texte
        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            return {
                "content": "\n".join(text_blocks),
                "tool_calls_made": iteration - 1,
                "tools_used": tools_used,
                "usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                },
                "fichier_url": fichier_url,
            }

        # Tool use: executer les outils et continuer
        if response.stop_reason == "tool_use":
            # Ajouter la reponse assistant (contient les blocs tool_use)
            messages.append({"role": "assistant", "content": response.content})

            # Executer chaque tool call
            tool_results = []
            for block in response.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    logger.info(f"Tool call: {block.name}({json.dumps(block.input, ensure_ascii=False)[:200]})")
                    tools_used.append(block.name)

                    result_str = handle_tool_call(block.name, block.input, context)

                    # Detecter si un fichier a ete genere
                    try:
                        result_data = json.loads(result_str)
                        if isinstance(result_data, dict) and result_data.get("fichier_docx"):
                            fichier_url = result_data["fichier_docx"]
                    except (json.JSONDecodeError, TypeError):
                        pass

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str,
                        }
                    )

            # Ajouter les resultats comme message user
            messages.append({"role": "user", "content": tool_results})
            continue

        # Stop reason inattendu (max_tokens, etc.)
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        return {
            "content": "\n".join(text_blocks) if text_blocks else "Reponse interrompue.",
            "tool_calls_made": iteration,
            "tools_used": tools_used,
            "usage": {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            },
            "fichier_url": fichier_url,
        }

    # Securite: limite d'iterations atteinte
    return {
        "content": "La conversation a atteint la limite d'iterations. Veuillez reformuler votre demande.",
        "tool_calls_made": MAX_ITERATIONS,
        "tools_used": tools_used,
        "usage": {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
        },
        "fichier_url": fichier_url,
    }
