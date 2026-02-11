# -*- coding: utf-8 -*-
"""
Agent Anthropic pour le chatbot NotaireAI.

Utilise l'API Anthropic Messages avec tool_use pour orchestrer
la collecte d'informations et la generation d'actes notariaux.

Architecture:
1. Charge historique + agent_state depuis Supabase
2. Anonymise les PII (ChatAnonymizer Python) AVANT envoi
3. Appel Anthropic Messages API avec 8 tools
4. Boucle tool_use: execute tool -> envoie tool_result -> repete
5. De-anonymise la reponse finale APRES reception
6. Sauvegarde agent_state dans Supabase
"""

import asyncio
import json
import re
import sys
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Encodage UTF-8 pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

MODEL = "claude-sonnet-4-20250514"
MAX_TOOL_ITERATIONS = 8    # Securite anti-boucle infinie
MAX_OUTPUT_TOKENS = 2048
MAX_HISTORY_MESSAGES = 20  # Limiter le contexte envoye a Claude

# Messages de statut pour les appels d'outils (affichage frontend)
TOOL_STATUS_MESSAGES = {
    "detect_property_type": "Detection du type de bien...",
    "get_questions": "Recherche des questions...",
    "submit_answers": "Enregistrement des reponses...",
    "get_collection_progress": "Calcul de la progression...",
    "validate_deed_data": "Validation des donnees...",
    "generate_document": "Generation du document...",
    "search_clauses": "Recherche de clauses...",
    "submit_feedback": "Enregistrement du feedback...",
}


# =============================================================================
# System Prompt
# =============================================================================

SYSTEM_PROMPT = """\
Tu es NotaireAI, un assistant intelligent specialise dans la creation \
d'actes notariaux pour les etudes notariales francaises.

## Ton role
Tu guides les notaires pas a pas pour collecter les informations necessaires \
et generer des promesses de vente et actes de vente conformes au droit francais.

## Tes outils
Tu disposes de 8 outils:

1. **detect_property_type** - Detecter la categorie du bien (copropriete, maison, terrain)
2. **get_questions** - Recuperer les questions a poser pour chaque section
3. **submit_answers** - Enregistrer les reponses du notaire
4. **get_collection_progress** - Voir la progression (% completion, champs manquants)
5. **validate_deed_data** - Verifier la coherence des donnees
6. **generate_document** - Generer le document final DOCX
7. **search_clauses** - Rechercher des clauses juridiques
8. **submit_feedback** - Enregistrer un retour du notaire

## Workflow type
1. Le notaire dit ce qu'il veut (ex: "creer une promesse pour un appartement")
2. Detecte la categorie avec detect_property_type
3. Recupere les questions section par section avec get_questions
4. Pose les questions de maniere conversationnelle (2-4 a la fois, pas toutes)
5. Enregistre les reponses avec submit_answers
6. Valide avec validate_deed_data quand suffisamment complet
7. Genere avec generate_document si tout est bon

## Regles de communication
- Toujours en francais, vouvoiement
- Professionnel mais accessible
- Pose 2 a 4 questions a la fois maximum
- Resume regulierement ce qui a ete collecte
- Propose des suggestions pertinentes
- Cite les references legales si necessaire (Code civil, CCH)

## Format de reponse
- Section en cours entre crochets: [Identification du vendeur]
- Suggestions d'actions: SUGGESTIONS: option1 | option2 | option3
- Document genere: FICHIER: /chemin/du/fichier.docx

## REGLE CRITIQUE - Enregistrement des donnees
AVANT de generer un document, tu DOIS TOUJOURS appeler submit_answers pour enregistrer \
les informations fournies par le notaire. Sinon, le document sera VIDE.

Quand le notaire fournit des informations (noms, adresses, prix, dates, etc.):
1. Extraire TOUTES les donnees du message
2. Appeler submit_answers avec un objet structure, par exemple:
   - "promettants": [{"nom": "Martin", "prenoms": "Jean", "date_naissance": "15/03/1965", ...}]
   - "beneficiaires": [{"nom": "Dupont", "prenoms": "Marie", ...}]
   - "bien": {"adresse": {"numero": "15", "rue": "rue des Fleurs", "code_postal": "75008", ...}}
   - "prix": {"montant": 450000, "lettres": "quatre cent cinquante mille euros"}
   - etc.
3. SEULEMENT APRES avoir appele submit_answers, tu peux appeler generate_document

## Regle importante - Generation forcee
Si le notaire demande explicitement de generer le document (meme incomplet), \
utilise generate_document avec force=true.
Phrases declencheuses: "genere quand meme", "genere le document", "telecharger maintenant", \
"force la generation", "je veux generer", "generer avec les infos actuelles".
MAIS TOUJOURS appeler submit_answers AVANT generate_document avec les donnees deja collectees.
Affiche un avertissement sur les champs manquants mais genere le fichier DOCX.
Le notaire peut ensuite completer manuellement le document.
"""


# =============================================================================
# Agent Response
# =============================================================================

@dataclass
class AgentResponse:
    """Reponse de l'agent, compatible avec le format ChatResponse existant."""
    content: str
    suggestions: List[str] = field(default_factory=list)
    section: Optional[str] = None
    fichier_url: Optional[str] = None
    intention: str = "agent"
    confiance: float = 0.95
    agent_state: Dict[str, Any] = field(default_factory=dict)
    action: Optional[Dict[str, Any]] = None
    contexte_mis_a_jour: Optional[Dict[str, Any]] = None


# =============================================================================
# Agent Anthropic
# =============================================================================

class AnthropicAgent:
    """
    Agent intelligent utilisant l'API Anthropic Messages avec tool_use.
    """

    def __init__(self, supabase_client=None):
        self.supabase = supabase_client
        self._client = None

    def _get_client(self):
        """Initialise le client Anthropic async (lazy)."""
        if self._client is None:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic()  # Utilise ANTHROPIC_API_KEY env var
        return self._client

    # =========================================================================
    # Persistance agent_state via Supabase
    # =========================================================================

    def _load_agent_state(self, conversation_id: str) -> Dict[str, Any]:
        """Charge l'agent_state depuis Supabase conversations.agent_state."""
        if not self.supabase or not conversation_id:
            logger.debug(f"Cannot load state: supabase={bool(self.supabase)}, conv_id={conversation_id}")
            return {}
        try:
            # Utiliser .limit(1) au lieu de .maybe_single() pour éviter erreur 406
            resp = self.supabase.table("conversations").select(
                "agent_state"
            ).eq("id", conversation_id).limit(1).execute()

            if resp.data and len(resp.data) > 0:
                state = resp.data[0].get("agent_state") or {}
                donnees = state.get("donnees_collectees", {})
                logger.info(f"[STATE] Loaded agent_state: {len(donnees)} keys in donnees_collectees for conv={conversation_id[:8]}")
                return state
            else:
                logger.info(f"[STATE] No existing state for conv={conversation_id[:8]}")
        except Exception as e:
            logger.warning(f"Impossible de charger agent_state: {e}")
        return {}

    def _save_agent_state(self, conversation_id: str, agent_state: Dict) -> bool:
        """Sauvegarde l'agent_state dans Supabase."""
        if not self.supabase or not conversation_id:
            logger.warning(f"[STATE] Cannot save: supabase={bool(self.supabase)}, conv_id={conversation_id}")
            return False
        try:
            donnees = agent_state.get("donnees_collectees", {})
            progress = agent_state.get("progress_pct", 0)
            logger.info(f"[STATE] Saving agent_state: {len(donnees)} keys, progress={progress}% for conv={conversation_id[:8]}")

            self.supabase.table("conversations").update({
                "agent_state": agent_state,
            }).eq("id", conversation_id).execute()
            logger.info(f"[STATE] Saved successfully for conv={conversation_id[:8]}")
            return True
        except Exception as e:
            logger.error(f"[STATE] FAILED to save agent_state: {e}", exc_info=True)
            return False

    # =========================================================================
    # Chargement des directives
    # =========================================================================

    def _load_directive_summary(self, type_acte: str) -> str:
        """Charge un resume de la directive pour le type d'acte.

        Les directives sont des fichiers Markdown qui decrivent les workflows
        a suivre pour chaque type d'acte (promesse, vente, reglement, etc.).
        On extrait les ~3000 premiers caracteres pour enrichir le contexte.
        """
        from pathlib import Path

        # Mapping type_acte → fichier directive
        DIRECTIVE_MAPPING = {
            "promesse_vente": "creer_promesse_vente.md",
            "promesse": "creer_promesse_vente.md",
            "vente": "creer_acte.md",
            "reglement_copropriete": "creer_reglement_copropriete.md",
            "reglement": "creer_reglement_copropriete.md",
            "modificatif_edd": "creer_modificatif_edd.md",
            "modificatif": "creer_modificatif_edd.md",
            "donation_partage": "creer_donation_partage.md",
            "donation": "creer_donation_partage.md",
        }

        filename = DIRECTIVE_MAPPING.get(type_acte)
        if not filename:
            return ""

        # Chemins possibles (Modal vs local)
        paths = [
            Path("/root/project/directives") / filename,  # Modal
            Path(__file__).parent.parent / "directives" / filename,  # Local
        ]

        for path in paths:
            try:
                if path.exists():
                    content = path.read_text(encoding="utf-8")
                    # Chercher la section "Flux de Travail" pour contexte utile
                    if "## Flux de Travail" in content:
                        start = content.find("## Flux de Travail")
                        summary = content[start:start + 3000]
                    elif "## Workflow" in content:
                        start = content.find("## Workflow")
                        summary = content[start:start + 3000]
                    else:
                        # Prendre le debut du fichier
                        summary = content[:3000]
                    return f"\n\n## Directive: {filename}\n{summary}\n[...]"
            except Exception as e:
                logger.warning(f"Erreur lecture directive {filename}: {e}")

        return ""

    # =========================================================================
    # Construction du prompt et des messages
    # =========================================================================

    def _build_system_prompt(self, agent_state: Dict) -> str:
        """System prompt + contexte dynamique de la session."""
        parts = [SYSTEM_PROMPT]

        if agent_state:
            parts.append("\n## Contexte de la session en cours")
            if agent_state.get("type_acte"):
                parts.append(f"- Type d'acte: {agent_state['type_acte']}")
            if agent_state.get("categorie_bien"):
                parts.append(f"- Categorie de bien: {agent_state['categorie_bien']}")
            if agent_state.get("progress_pct") is not None:
                parts.append(f"- Progression collecte: {agent_state['progress_pct']}%")
            if agent_state.get("fichier_genere"):
                parts.append(f"- Dernier fichier genere: {agent_state['fichier_genere']}")

        return "\n".join(parts)

    def _build_cached_system(self, agent_state: Dict) -> list:
        """System prompt avec prompt caching Anthropic.

        Le SYSTEM_PROMPT statique est cache (cache_control ephemeral).
        Le contexte dynamique change a chaque appel et n'est pas cache.
        """
        blocks = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        # Contexte dynamique (non cache)
        dynamic_parts = []
        if agent_state:
            dynamic_parts.append("\n## Contexte de la session en cours")
            if agent_state.get("type_acte"):
                dynamic_parts.append(f"- Type d'acte: {agent_state['type_acte']}")
                # Charger la directive pertinente pour ce type d'acte
                directive = self._load_directive_summary(agent_state['type_acte'])
                if directive:
                    dynamic_parts.append(directive)
            if agent_state.get("categorie_bien"):
                dynamic_parts.append(f"- Categorie de bien: {agent_state['categorie_bien']}")
            if agent_state.get("progress_pct") is not None:
                dynamic_parts.append(f"- Progression collecte: {agent_state['progress_pct']}%")
            if agent_state.get("fichier_genere"):
                dynamic_parts.append(f"- Dernier fichier genere: {agent_state['fichier_genere']}")

        if dynamic_parts:
            blocks.append({"type": "text", "text": "\n".join(dynamic_parts)})

        return blocks

    def _get_cached_tools(self) -> list:
        """Tools avec cache_control sur le dernier element."""
        from execution.anthropic_tools import TOOLS
        tools = [dict(t) for t in TOOLS]
        if tools:
            tools[-1] = {**tools[-1], "cache_control": {"type": "ephemeral"}}
        return tools

    def _prepare_messages(
        self,
        message: str,
        history: List[Dict],
    ) -> List[Dict]:
        """Prepare les messages pour l'API Anthropic."""
        messages = []

        # Historique recent (tronque)
        recent = history[-MAX_HISTORY_MESSAGES:] if history else []
        for msg in recent:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # Message courant
        messages.append({"role": "user", "content": message})

        return messages

    # =========================================================================
    # Parsing de la reponse
    # =========================================================================

    def _parse_response(self, text: str, agent_state: Dict) -> AgentResponse:
        """Parse la reponse texte pour extraire section, suggestions, fichier."""
        content = text
        section = None
        suggestions = []
        fichier_url = None

        # [Section en cours]
        section_match = re.search(r'\[([^\]]+)\]', content)
        if section_match:
            section = section_match.group(1)
            content = content.replace(section_match.group(0), '', 1).strip()

        # SUGGESTIONS: a | b | c
        sugg_match = re.search(r'SUGGESTIONS?\s*:\s*(.+?)(?:\n|$)', content)
        if sugg_match:
            suggestions = [s.strip() for s in sugg_match.group(1).split('|') if s.strip()]
            content = content.replace(sugg_match.group(0), '').strip()

        # FICHIER: /path
        fichier_match = re.search(r'FICHIER\s*:\s*(\S+)', content)
        if fichier_match:
            fichier_url = fichier_match.group(1)
            content = content.replace(fichier_match.group(0), '').strip()

        # Fallback fichier depuis agent_state
        if not fichier_url and agent_state.get("fichier_genere"):
            fichier_url = agent_state["fichier_genere"]

        # Transformer chemin local en URL signée avec HMAC-SHA256
        # Sécurité: URL expire après 1h, signature vérifiée côté serveur
        if fichier_url and not fichier_url.startswith("/download/"):
            from pathlib import Path
            from execution.security.signed_urls import generate_signed_url
            filename = Path(fichier_url).name
            if filename:
                # URL signée valide 1 heure (3600 secondes)
                fichier_url = generate_signed_url(filename, expires_in=3600)
            else:
                fichier_url = None

        return AgentResponse(
            content=content,
            suggestions=suggestions,
            section=section,
            fichier_url=fichier_url,
            agent_state=agent_state,
            action={"fichier_url": fichier_url} if fichier_url else None,
            contexte_mis_a_jour={
                "type_acte_en_cours": agent_state.get("type_acte"),
                "etape_workflow": section,
                "progress_pct": agent_state.get("progress_pct"),
                "categorie_bien": agent_state.get("categorie_bien"),
            },
        )

    # =========================================================================
    # Boucle principale
    # =========================================================================

    async def process_message(
        self,
        message: str,
        user_id: str = "",
        etude_id: str = "",
        conversation_id: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
    ) -> AgentResponse:
        """
        Traite un message du notaire via l'agent Anthropic.

        Boucle agentic:
        1. Envoie messages + tools a Claude
        2. Si Claude appelle un tool -> execute -> renvoie tool_result
        3. Repete jusqu'a reponse texte (ou max iterations)
        """
        from execution.anthropic_tools import TOOLS, ToolExecutor

        # 1. Charger agent_state persiste
        agent_state = self._load_agent_state(conversation_id) if conversation_id else {}
        if context and context.get("type_acte_en_cours"):
            agent_state.setdefault("type_acte", context["type_acte_en_cours"])

        # 2. Preparer les messages
        messages = self._prepare_messages(message, history or [])

        # 3. System prompt dynamique avec prompt caching
        cached_system = self._build_cached_system(agent_state)
        cached_tools = self._get_cached_tools()

        # 4. Tool executor
        executor = ToolExecutor(etude_id=etude_id, supabase_client=self.supabase)

        # 5. Boucle agentic
        client = self._get_client()
        iteration = 0

        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1

            response = await client.messages.create(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=cached_system,
                tools=cached_tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                # Reponse finale en texte
                text_blocks = [b.text for b in response.content if b.type == "text"]
                final_text = "\n".join(text_blocks)

                # Persister l'etat
                self._save_agent_state(conversation_id, agent_state)

                return self._parse_response(final_text, agent_state)

            elif response.stop_reason == "tool_use":
                # Claude veut utiliser un ou plusieurs tools
                messages.append({
                    "role": "assistant",
                    "content": response.content,
                })

                # Executer chaque tool_use block
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info(
                            f"Tool call [{iteration}/{MAX_TOOL_ITERATIONS}]: "
                            f"{block.name}({json.dumps(block.input, ensure_ascii=False)[:200]})"
                        )

                        result = executor.execute(
                            tool_name=block.name,
                            tool_input=block.input,
                            agent_state=agent_state,
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results,
                })

            else:
                # Stop reason inattendu (max_tokens, etc.)
                text_blocks = [b.text for b in response.content if b.type == "text"]
                final_text = "\n".join(text_blocks) if text_blocks else (
                    "Ma reponse a ete interrompue. Pouvez-vous reformuler votre demande ?"
                )
                self._save_agent_state(conversation_id, agent_state)
                return self._parse_response(final_text, agent_state)

        # Max iterations atteint - securite anti-boucle
        logger.warning(f"Max tool iterations ({MAX_TOOL_ITERATIONS}) atteint pour conversation {conversation_id}")
        self._save_agent_state(conversation_id, agent_state)
        return AgentResponse(
            content="J'ai effectue plusieurs operations. Que souhaitez-vous faire maintenant ?",
            suggestions=["Voir la progression", "Generer le document", "Poser une question"],
            agent_state=agent_state,
        )

    # =========================================================================
    # Streaming (SSE)
    # =========================================================================

    async def process_message_stream(
        self,
        message: str,
        user_id: str = "",
        etude_id: str = "",
        conversation_id: Optional[str] = None,
        history: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
    ):
        """
        Version streaming de process_message.

        Yields des dicts SSE:
          {"event": "status", "data": "{\"message\": \"...\"}"}
          {"event": "token",  "data": "{\"text\": \"...\"}"}
          {"event": "done",   "data": "{\"suggestions\": [...], ...}"}
        """
        from execution.anthropic_tools import TOOLS, ToolExecutor

        # 1. Charger agent_state
        agent_state = self._load_agent_state(conversation_id) if conversation_id else {}
        if context and context.get("type_acte_en_cours"):
            agent_state.setdefault("type_acte", context["type_acte_en_cours"])

        # 2. Preparer les messages
        messages = self._prepare_messages(message, history or [])

        # 3. System + tools avec cache
        cached_system = self._build_cached_system(agent_state)
        cached_tools = self._get_cached_tools()

        # 4. Tool executor
        executor = ToolExecutor(etude_id=etude_id, supabase_client=self.supabase)

        # 5. Boucle agentic avec streaming
        client = self._get_client()
        iteration = 0

        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1

            # Streaming API call
            collected_text = []

            async with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=cached_system,
                tools=cached_tools,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    collected_text.append(text)
                response = await stream.get_final_message()

            if response.stop_reason == "end_turn":
                # Reponse finale
                final_text = "".join(collected_text)
                self._save_agent_state(conversation_id, agent_state)

                parsed = self._parse_response(final_text, agent_state)

                # Envoyer le texte en chunks
                chunk_size = 20
                for i in range(0, len(parsed.content), chunk_size):
                    yield {
                        "event": "token",
                        "data": json.dumps({"text": parsed.content[i:i + chunk_size]}),
                    }

                # Metadata finale
                yield {
                    "event": "done",
                    "data": json.dumps({
                        "content": parsed.content,
                        "suggestions": parsed.suggestions,
                        "section": parsed.section,
                        "fichier_url": parsed.fichier_url,
                        "progress_pct": agent_state.get("progress_pct"),
                        "categorie_bien": agent_state.get("categorie_bien"),
                    }),
                }
                return

            elif response.stop_reason == "tool_use":
                # Executer les outils (rapide, local)
                messages.append({
                    "role": "assistant",
                    "content": response.content,
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        status_msg = TOOL_STATUS_MESSAGES.get(
                            block.name, f"Execution: {block.name}..."
                        )
                        yield {
                            "event": "status",
                            "data": json.dumps({"message": status_msg}),
                        }

                        logger.info(
                            f"Tool call [{iteration}/{MAX_TOOL_ITERATIONS}]: "
                            f"{block.name}({json.dumps(block.input, ensure_ascii=False)[:200]})"
                        )

                        # asyncio.to_thread libere l'event loop pendant
                        # l'execution (permet a sse-starlette d'envoyer des pings)
                        result = await asyncio.to_thread(
                            executor.execute,
                            tool_name=block.name,
                            tool_input=block.input,
                            agent_state=agent_state,
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        })

                messages.append({
                    "role": "user",
                    "content": tool_results,
                })

            else:
                # Stop reason inattendu
                text = "".join(collected_text) if collected_text else (
                    "Ma reponse a ete interrompue. Pouvez-vous reformuler ?"
                )
                self._save_agent_state(conversation_id, agent_state)

                yield {"event": "token", "data": json.dumps({"text": text})}
                yield {
                    "event": "done",
                    "data": json.dumps({"content": text, "suggestions": []}),
                }
                return

        # Max iterations
        self._save_agent_state(conversation_id, agent_state)
        fallback = "J'ai effectue plusieurs operations. Que souhaitez-vous faire maintenant ?"
        yield {"event": "token", "data": json.dumps({"text": fallback})}
        yield {
            "event": "done",
            "data": json.dumps({
                "content": fallback,
                "suggestions": ["Voir la progression", "Generer le document"],
            }),
        }
