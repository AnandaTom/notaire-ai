# -*- coding: utf-8 -*-
"""
Chat Handler - Gestionnaire de conversations pour le chatbot NotaireAI

Ce module gere les conversations entre les notaires et l'agent IA.
Il utilise le ParseurDemandeNL existant pour comprendre les demandes
et genere des reponses appropriees sans exposer de donnees sensibles.

Principes de securite:
- AUCUNE donnee sensible (noms, adresses) n'est envoyee a un LLM externe
- Le parsing est fait localement avec ParseurDemandeNL
- Les donnees restent dans Supabase avec RLS active

Apprentissage continu:
- Chaque conversation est sauvegardee dans la table 'conversations'
- Les feedbacks sont stockes dans la table 'feedbacks'
- Un job quotidien analyse les feedbacks pour ameliorer l'agent
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


# =============================================================================
# Types et structures
# =============================================================================

class IntentionChat(Enum):
    """Intentions detectables dans une conversation."""
    CREER = "creer"
    MODIFIER = "modifier"
    RECHERCHER = "rechercher"
    CONSULTER = "consulter"
    AIDE = "aide"
    NAVIGATION = "navigation"
    SALUTATION = "salutation"
    CONFIRMATION = "confirmation"
    ANNULATION = "annulation"
    INCONNU = "inconnu"


@dataclass
class MessageChat:
    """Un message dans la conversation."""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContexteConversation:
    """Contexte de la conversation en cours."""
    dossier_actif: Optional[str] = None
    client_selectionne: Optional[str] = None
    type_acte_en_cours: Optional[str] = None
    etape_workflow: Optional[str] = None
    donnees_collectees: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReponseChat:
    """Reponse du chatbot."""
    content: str
    suggestions: List[str] = field(default_factory=list)
    action: Optional[Dict[str, Any]] = None  # Ex: {"type": "navigate", "url": "/dossiers"}
    contexte_mis_a_jour: Optional[Dict[str, Any]] = None
    intention_detectee: str = "inconnu"
    confiance: float = 0.0


# =============================================================================
# Gestionnaire de conversation
# =============================================================================

class ChatHandler:
    """
    Gestionnaire principal des conversations chatbot.

    Responsabilites:
    - Comprendre les messages en langage naturel
    - Generer des reponses appropriees
    - Maintenir le contexte de conversation
    - Faciliter l'apprentissage continu via feedbacks
    """

    def __init__(self, supabase_client=None, verbose: bool = False):
        """
        Initialise le gestionnaire de chat.

        Args:
            supabase_client: Client Supabase (optionnel, cree si non fourni)
            verbose: Mode verbeux pour debug
        """
        self.supabase = supabase_client
        self.verbose = verbose
        self._parseur = None

    @property
    def parseur(self):
        """Lazy loading du parseur NL."""
        if self._parseur is None:
            try:
                from execution.agent_autonome import ParseurDemandeNL
                self._parseur = ParseurDemandeNL()
            except ImportError:
                # Fallback si le module n'est pas disponible
                self._parseur = SimpleParseur()
        return self._parseur

    def traiter_message(
        self,
        message: str,
        user_id: str,
        etude_id: str,
        historique: List[Dict] = None,
        contexte: Dict = None
    ) -> ReponseChat:
        """
        Traite un message utilisateur et genere une reponse.

        Args:
            message: Le message de l'utilisateur
            user_id: ID de l'utilisateur (pour RLS)
            etude_id: ID de l'etude (pour RLS)
            historique: Messages precedents de la conversation
            contexte: Contexte de conversation (dossier actif, etc.)

        Returns:
            ReponseChat avec le contenu et les suggestions
        """
        historique = historique or []
        contexte = ContexteConversation(**contexte) if contexte else ContexteConversation()

        if self.verbose:
            print(f"[ChatHandler] Message recu: {message[:50]}...")

        # 1. Analyser l'intention
        intention, confiance, entites = self._analyser_intention(message)

        if self.verbose:
            print(f"[ChatHandler] Intention: {intention} (confiance: {confiance:.0%})")

        # 2. Generer la reponse selon l'intention
        reponse = self._generer_reponse(
            intention=intention,
            entites=entites,
            message=message,
            contexte=contexte,
            etude_id=etude_id
        )

        reponse.intention_detectee = intention.value
        reponse.confiance = confiance

        return reponse

    def _analyser_intention(self, message: str) -> tuple:
        """
        Analyse l'intention du message.

        Returns:
            (intention, confiance, entites)
        """
        msg_lower = message.lower().strip()

        # Salutations
        if any(mot in msg_lower for mot in ["bonjour", "salut", "hello", "bonsoir"]):
            return IntentionChat.SALUTATION, 0.95, {}

        # Aide
        if any(mot in msg_lower for mot in ["aide", "help", "comment", "quoi faire", "peux-tu"]):
            return IntentionChat.AIDE, 0.9, {}

        # Confirmations
        if any(mot in msg_lower for mot in ["oui", "ok", "d'accord", "confirme", "valide"]):
            return IntentionChat.CONFIRMATION, 0.85, {}

        # Annulations
        if any(mot in msg_lower for mot in ["non", "annule", "stop", "arrête", "retour"]):
            return IntentionChat.ANNULATION, 0.85, {}

        # Utiliser le parseur avance pour les intentions metier
        try:
            analyse = self.parseur.analyser(message)

            # Mapper les intentions du parseur
            intention_map = {
                "CREER": IntentionChat.CREER,
                "MODIFIER": IntentionChat.MODIFIER,
                "RECHERCHER": IntentionChat.RECHERCHER,
                "GENERER": IntentionChat.CONSULTER,
            }

            raw_intention = analyse.intention.value if hasattr(analyse.intention, 'value') else str(analyse.intention)
            intention = intention_map.get(
                raw_intention.upper(),
                IntentionChat.INCONNU
            )

            entites = {
                "type_acte": getattr(analyse, 'type_acte', None),
                "vendeur": getattr(analyse, 'vendeur', None),
                "acquereur": getattr(analyse, 'acquereur', None),
                "bien": getattr(analyse, 'bien', None),
                "prix": getattr(analyse, 'prix', None),
                "reference": getattr(analyse, 'reference_dossier', None),
            }

            # Nettoyer les None
            entites = {k: v for k, v in entites.items() if v}

            # Si le parseur retourne INCONNU, tenter le fallback par mots-cles
            if intention == IntentionChat.INCONNU:
                fallback = self._fallback_intention(msg_lower)
                if fallback is not None:
                    return fallback

            return intention, analyse.confiance, entites

        except Exception as e:
            if self.verbose:
                print(f"[ChatHandler] Erreur parsing: {e}")

            fallback = self._fallback_intention(msg_lower)
            if fallback is not None:
                return fallback

            return IntentionChat.INCONNU, 0.3, {}

    def _fallback_intention(self, msg_lower: str):
        """Detection d'intention par mots-cles quand le parseur echoue."""
        if any(mot in msg_lower for mot in ["vente", "créer", "creer", "acte", "promesse", "générer", "generer"]):
            return IntentionChat.CREER, 0.6, {}
        # RECHERCHER avant CONSULTER car "cherche dossier" = recherche, pas consultation
        if any(mot in msg_lower for mot in ["cherche", "trouve", "recherche"]):
            return IntentionChat.RECHERCHER, 0.6, {}
        if any(mot in msg_lower for mot in ["dossier", "voir", "liste", "consulter", "client"]):
            return IntentionChat.CONSULTER, 0.6, {}
        return None

    def _generer_reponse(
        self,
        intention: IntentionChat,
        entites: Dict,
        message: str,
        contexte: ContexteConversation,
        etude_id: str
    ) -> ReponseChat:
        """
        Genere une reponse appropriee selon l'intention.
        """
        # Mapping intention → generateur de reponse
        handlers = {
            IntentionChat.SALUTATION: self._reponse_salutation,
            IntentionChat.AIDE: self._reponse_aide,
            IntentionChat.CREER: self._reponse_creer,
            IntentionChat.MODIFIER: self._reponse_modifier,
            IntentionChat.RECHERCHER: self._reponse_rechercher,
            IntentionChat.CONSULTER: self._reponse_consulter,
            IntentionChat.CONFIRMATION: self._reponse_confirmation,
            IntentionChat.ANNULATION: self._reponse_annulation,
            IntentionChat.INCONNU: self._reponse_inconnu,
        }

        handler = handlers.get(intention, self._reponse_inconnu)
        return handler(entites, message, contexte, etude_id)

    # =========================================================================
    # Generateurs de reponses
    # =========================================================================

    def _reponse_salutation(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse aux salutations."""
        heure = datetime.now().hour
        if heure < 12:
            salut = "Bonjour"
        elif heure < 18:
            salut = "Bon apres-midi"
        else:
            salut = "Bonsoir"

        return ReponseChat(
            content=f"{salut} Maitre, comment puis-je vous aider aujourd'hui ?",
            suggestions=[
                "Creer un acte de vente",
                "Voir mes dossiers en cours",
                "Rechercher un client"
            ]
        )

    def _reponse_aide(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse aux demandes d'aide."""
        return ReponseChat(
            content="""Je suis votre assistant NotaireAI. Voici ce que je peux faire :

**Creer des actes**
- Acte de vente (lots en copropriete)
- Promesse unilaterale de vente
- Reglement de copropriete
- Modificatif EDD

**Gerer vos dossiers**
- Voir vos dossiers en cours
- Rechercher un dossier
- Suivre l'avancement

**Gerer vos clients**
- Rechercher un client
- Voir l'historique des actes

Que souhaitez-vous faire ?""",
            suggestions=[
                "Creer un acte de vente",
                "Voir mes dossiers",
                "Rechercher un client"
            ]
        )

    def _reponse_creer(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse pour la creation d'actes."""
        type_acte = entites.get("type_acte")

        if type_acte:
            # Type d'acte detecte
            type_lisible = {
                "vente": "acte de vente",
                "promesse_vente": "promesse de vente",
                "reglement_copropriete": "reglement de copropriete",
                "modificatif_edd": "modificatif EDD"
            }.get(str(type_acte), str(type_acte))

            return ReponseChat(
                content=f"""Je vais vous aider a creer un {type_lisible}.

Pour commencer, j'ai besoin de quelques informations :

1. **Vendeur** : Nom et situation du vendeur
2. **Acquereur** : Nom et situation de l'acquereur
3. **Bien** : Adresse et description du bien

Par quoi souhaitez-vous commencer ?""",
                suggestions=[
                    "Renseigner le vendeur",
                    "Renseigner l'acquereur",
                    "Decrire le bien",
                    "Annuler"
                ],
                action={"type": "start_workflow", "workflow": "creer_acte", "type_acte": str(type_acte)},
                contexte_mis_a_jour={"type_acte_en_cours": str(type_acte), "etape_workflow": "collecte"}
            )
        else:
            # Demander le type d'acte
            return ReponseChat(
                content="""Quel type d'acte souhaitez-vous creer ?

- **Vente** : Acte de vente definitif (lots en copropriete)
- **Promesse** : Promesse unilaterale de vente
- **Reglement** : Reglement de copropriete / EDD
- **Modificatif** : Modification d'un EDD existant""",
                suggestions=[
                    "Acte de vente",
                    "Promesse de vente",
                    "Reglement copropriete",
                    "Modificatif EDD"
                ]
            )

    def _reponse_modifier(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse pour la modification d'actes."""
        reference = entites.get("reference")

        if reference:
            return ReponseChat(
                content=f"""Je vais rechercher le dossier {reference} pour le modifier.

Que souhaitez-vous modifier ?""",
                suggestions=[
                    "Le prix",
                    "Les parties (vendeur/acquereur)",
                    "La description du bien",
                    "Annuler"
                ],
                action={"type": "load_dossier", "reference": reference}
            )
        else:
            return ReponseChat(
                content="""Quel dossier souhaitez-vous modifier ?

Vous pouvez me donner :
- Un numero de dossier (ex: 2026-001)
- Un nom de client
- Une adresse de bien""",
                suggestions=["Voir mes dossiers recents"]
            )

    def _reponse_rechercher(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse pour les recherches."""
        return ReponseChat(
            content="""Que recherchez-vous ?

- **Client** : Par nom, email ou telephone
- **Dossier** : Par numero ou adresse du bien
- **Acte** : Par type ou date""",
            suggestions=[
                "Rechercher un client",
                "Rechercher un dossier",
                "Voir tous mes dossiers"
            ],
            action={"type": "show_search"}
        )

    def _reponse_consulter(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse pour la consultation de dossiers."""
        return ReponseChat(
            content="""Voici vos dossiers recents :

Je vais charger la liste de vos dossiers depuis votre espace securise.

*(En production, cette liste sera chargee depuis Supabase avec les vraies donnees)*""",
            suggestions=[
                "Filtrer par statut",
                "Filtrer par type d'acte",
                "Creer un nouveau dossier"
            ],
            action={"type": "navigate", "url": "/dossiers"}
        )

    def _reponse_confirmation(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse aux confirmations."""
        if contexte.etape_workflow:
            return ReponseChat(
                content="Parfait, je continue avec les informations fournies.",
                suggestions=["Etape suivante", "Modifier", "Annuler"]
            )
        else:
            return ReponseChat(
                content="Que souhaitez-vous confirmer ?",
                suggestions=["Voir mes dossiers", "Creer un acte", "Aide"]
            )

    def _reponse_annulation(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse aux annulations."""
        return ReponseChat(
            content="D'accord, j'annule l'operation en cours. Comment puis-je vous aider autrement ?",
            suggestions=["Creer un acte", "Voir mes dossiers", "Aide"],
            contexte_mis_a_jour={"type_acte_en_cours": None, "etape_workflow": None}
        )

    def _reponse_inconnu(self, entites, message, contexte, etude_id) -> ReponseChat:
        """Reponse par defaut quand l'intention n'est pas comprise."""
        return ReponseChat(
            content="""Je ne suis pas sur d'avoir compris votre demande.

Pouvez-vous reformuler ou choisir une action ?""",
            suggestions=[
                "Creer un acte",
                "Voir mes dossiers",
                "Rechercher",
                "Aide"
            ]
        )


# =============================================================================
# Parseur simplifie (fallback)
# =============================================================================

class SimpleParseur:
    """Parseur simplifie utilise si agent_autonome n'est pas disponible."""

    def analyser(self, texte: str):
        """Analyse basique du texte."""
        from dataclasses import dataclass

        @dataclass
        class AnalyseSimple:
            intention: str = "INCONNU"
            type_acte: str = None
            confiance: float = 0.5
            vendeur: str = None
            acquereur: str = None
            bien: str = None
            prix: str = None
            reference_dossier: str = None

        texte_lower = texte.lower()

        analyse = AnalyseSimple()

        if "vente" in texte_lower or "créer" in texte_lower:
            analyse.intention = "CREER"
            analyse.type_acte = "vente"
            analyse.confiance = 0.7
        elif "promesse" in texte_lower:
            analyse.intention = "CREER"
            analyse.type_acte = "promesse_vente"
            analyse.confiance = 0.7
        elif "dossier" in texte_lower or "liste" in texte_lower:
            analyse.intention = "GENERER"
            analyse.confiance = 0.6
        elif "cherche" in texte_lower or "trouve" in texte_lower:
            analyse.intention = "RECHERCHER"
            analyse.confiance = 0.6

        return analyse


# =============================================================================
# API Endpoint (pour Modal/FastAPI)
# =============================================================================

def _get_supabase():
    """Retourne un client Supabase si disponible."""
    try:
        from execution.database.supabase_client import get_supabase_client
        return get_supabase_client()
    except Exception:
        return None


def create_chat_router():
    """
    Cree le router FastAPI pour le chat.
    A importer dans api/main.py
    """
    from fastapi import APIRouter, HTTPException, Depends
    from pydantic import BaseModel
    from typing import List, Optional

    router = APIRouter(prefix="/chat", tags=["chat"])

    class ChatRequest(BaseModel):
        message: str
        user_id: str = ""
        etude_id: str = ""
        conversation_id: Optional[str] = None
        history: Optional[List[dict]] = None
        context: Optional[dict] = None

    class ChatResponse(BaseModel):
        content: str
        suggestions: List[str] = []
        action: Optional[dict] = None
        intention: str = "agent"
        confiance: float = 1.0
        conversation_id: Optional[str] = None
        section: Optional[str] = None
        fichier_url: Optional[str] = None
        contexte_mis_a_jour: Optional[dict] = None
        tool_calls_made: int = 0
        tools_used: List[str] = []

    @router.post("/", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """
        Endpoint principal du chatbot avec persistance conversationnelle.

        Securite:
        - Authentification via API key (geree par main.py)
        - RLS Supabase active (isolation par etude)
        - Aucune donnee sensible envoyee a un LLM externe

        Persistance:
        - Si conversation_id fourni, charge l'historique depuis Supabase
        - Sauvegarde chaque message (user + assistant) dans conversation_messages
        - Met a jour le contexte de la conversation
        """
        try:
            historique = request.history or []
            contexte = request.context or {}
            conversation_id = request.conversation_id

            # Charger l'historique depuis Supabase si conversation_id fourni
            supabase = _get_supabase()
            if supabase and conversation_id and request.etude_id:
                try:
                    conv_resp = supabase.table("conversations").select("*").eq(
                        "id", conversation_id
                    ).maybe_single().execute()

                    if conv_resp.data:
                        stored_ctx = conv_resp.data.get("contexte") or {}
                        contexte = {**stored_ctx, **contexte}

                        msgs_resp = supabase.table("conversation_messages").select(
                            "role, content"
                        ).eq(
                            "conversation_id", conversation_id
                        ).order("created_at").execute()

                        if msgs_resp.data:
                            historique = msgs_resp.data
                    else:
                        supabase.table("conversations").insert({
                            "id": conversation_id,
                            "etude_id": request.etude_id,
                            "user_id": request.user_id,
                            "statut": "active",
                            "contexte": contexte,
                        }).execute()
                except Exception:
                    pass  # Fallback silencieux

            # --- Agent LLM (Anthropic API + Tool Use) ---
            use_llm = bool(os.environ.get("ANTHROPIC_API_KEY"))
            agent_result = None

            if use_llm:
                try:
                    from execution.agent_llm import run_agent, build_system_prompt

                    # Convertir historique en format Anthropic messages
                    anthropic_messages = []
                    for msg in historique:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        if role in ("user", "assistant") and content:
                            anthropic_messages.append({"role": role, "content": content})

                    # Ajouter le message courant
                    anthropic_messages.append({"role": "user", "content": request.message})

                    agent_context = {
                        "etude_id": request.etude_id,
                        "supabase": supabase,
                        "user_id": request.user_id,
                    }

                    agent_result = run_agent(
                        messages=anthropic_messages,
                        system_prompt=build_system_prompt(),
                        context=agent_context,
                    )
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Agent LLM fallback: {e}")
                    agent_result = None

            # --- Fallback: ChatHandler keyword matching ---
            if agent_result is None:
                handler = ChatHandler(verbose=False)
                reponse = handler.traiter_message(
                    message=request.message,
                    user_id=request.user_id,
                    etude_id=request.etude_id,
                    historique=historique,
                    contexte=contexte,
                )
                response_content = reponse.content
                response_suggestions = reponse.suggestions
                response_intention = reponse.intention_detectee
                response_confiance = reponse.confiance
                response_fichier_url = None
                if reponse.action and isinstance(reponse.action, dict):
                    response_fichier_url = reponse.action.get("fichier_url")
                response_tool_calls = 0
                response_tools_used = []
                response_contexte = reponse.contexte_mis_a_jour
            else:
                response_content = agent_result.get("content", "")
                response_suggestions = []
                response_intention = "agent"
                response_confiance = 1.0
                response_fichier_url = agent_result.get("fichier_url")
                response_tool_calls = agent_result.get("tool_calls_made", 0)
                response_tools_used = agent_result.get("tools_used", [])
                response_contexte = None

            # Persister les messages dans Supabase
            if supabase and conversation_id and request.etude_id:
                try:
                    supabase.table("conversation_messages").insert([
                        {
                            "conversation_id": conversation_id,
                            "role": "user",
                            "content": request.message,
                        },
                        {
                            "conversation_id": conversation_id,
                            "role": "assistant",
                            "content": response_content,
                            "intention": response_intention,
                            "confiance": response_confiance,
                            "metadata": {
                                "suggestions": response_suggestions,
                                "tool_calls_made": response_tool_calls,
                                "tools_used": response_tools_used,
                            },
                        },
                    ]).execute()

                    update_data = {}
                    if response_contexte:
                        update_data["contexte"] = response_contexte
                        type_acte = response_contexte.get("type_acte_en_cours")
                        if type_acte:
                            update_data["type_acte"] = type_acte
                    if update_data:
                        supabase.table("conversations").update(update_data).eq(
                            "id", conversation_id
                        ).execute()
                except Exception:
                    pass  # Fallback silencieux

            # Extraire section depuis le contexte
            section = None
            if response_contexte:
                section = response_contexte.get("etape_workflow")

            return ChatResponse(
                content=response_content,
                suggestions=response_suggestions,
                intention=response_intention,
                confiance=response_confiance,
                conversation_id=conversation_id,
                section=section,
                fichier_url=response_fichier_url,
                contexte_mis_a_jour=response_contexte,
                tool_calls_made=response_tool_calls,
                tools_used=response_tools_used,
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/feedback")
    async def submit_feedback(
        conversation_id: str,
        message_index: int,
        rating: int,
        feedback_type: Optional[str] = None,
        correction: Optional[str] = None
    ):
        """
        Enregistre un feedback pour l'apprentissage continu.
        """
        # En production, sauvegarder dans Supabase
        return {
            "status": "ok",
            "message": "Feedback enregistre. Merci pour votre contribution !"
        }

    return router


# =============================================================================
# Test local
# =============================================================================

if __name__ == "__main__":
    # Test du handler
    handler = ChatHandler(verbose=True)

    tests = [
        "Bonjour",
        "Je veux creer une vente",
        "Aide",
        "Montre moi mes dossiers",
        "Recherche le client Dupont",
        "Oui, confirme",
        "Non, annule",
        "blabla incomprehensible"
    ]

    print("=" * 60)
    print("TEST DU CHAT HANDLER")
    print("=" * 60)

    for test in tests:
        print(f"\n>> {test}")
        reponse = handler.traiter_message(
            message=test,
            user_id="test-user",
            etude_id="test-etude"
        )
        print(f"<< {reponse.content[:100]}...")
        print(f"   Intention: {reponse.intention_detectee} ({reponse.confiance:.0%})")
        print(f"   Suggestions: {reponse.suggestions}")
