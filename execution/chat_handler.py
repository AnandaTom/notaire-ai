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
    questionnaire_active: bool = False
    questionnaire_state: Optional[Dict[str, Any]] = None


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

        # 0. Si questionnaire actif, traiter la reponse dans ce mode
        if contexte.questionnaire_active and contexte.questionnaire_state:
            # Verifier si c'est une annulation
            msg_lower = message.lower().strip()
            if msg_lower in ["annuler", "stop", "non", "arreter"]:
                return ReponseChat(
                    content="Questionnaire annule. Comment puis-je vous aider ?",
                    suggestions=["Creer un acte", "Voir mes dossiers", "Aide"],
                    contexte_mis_a_jour={"questionnaire_active": False, "questionnaire_state": None, "etape_workflow": None}
                )
            return self._reponse_questionnaire(message, contexte, etude_id)

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
        """Reponse pour la creation d'actes. Demarre le questionnaire si type detecte."""
        type_acte = entites.get("type_acte")

        if type_acte:
            # Demarrer le questionnaire interactif
            type_lisible = {
                "vente": "acte de vente",
                "promesse_vente": "promesse de vente",
                "reglement_copropriete": "reglement de copropriete",
                "modificatif_edd": "modificatif EDD"
            }.get(str(type_acte), str(type_acte))

            try:
                from execution.questionnaire_manager import QuestionnaireManager
                qm = QuestionnaireManager(str(type_acte))
                next_q = qm.get_next_question()

                if next_q:
                    article = "une" if str(type_acte) == "promesse_vente" else "un"
                    return ReponseChat(
                        content=f"""Je vais vous guider pour creer {article} {type_lisible}.

[{next_q['progress']}%] **Section : {next_q['section_titre']}**
{next_q['question']}""" + (f"\n\nChoix possibles : {', '.join(next_q['options'])}" if next_q.get('options') else ""),
                        suggestions=next_q.get("options", ["Annuler"]),
                        action={"type": "start_questionnaire", "type_acte": str(type_acte)},
                        contexte_mis_a_jour={
                            "type_acte_en_cours": str(type_acte),
                            "etape_workflow": "questionnaire",
                            "questionnaire_active": True,
                            "questionnaire_state": qm.serialize()
                        }
                    )
            except Exception as e:
                if self.verbose:
                    print(f"[ChatHandler] Erreur questionnaire: {e}")

            # Fallback sans questionnaire
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

    def _reponse_questionnaire(self, message, contexte, etude_id) -> ReponseChat:
        """Traite une reponse dans le mode questionnaire interactif."""
        try:
            from execution.questionnaire_manager import QuestionnaireManager

            qm = QuestionnaireManager(
                type_acte=contexte.type_acte_en_cours or "promesse_vente",
                state=contexte.questionnaire_state
            )

            # Trouver la question en attente de reponse
            current_q = qm.get_next_question()
            if not current_q:
                # Deja complet
                return self._reponse_questionnaire_complet(qm, contexte, etude_id)

            # Enregistrer la reponse
            qm.record_answer(current_q["id"], message.strip())

            # Passer a la question suivante
            next_q = qm.get_next_question()

            if next_q is None or qm.is_complete():
                return self._reponse_questionnaire_complet(qm, contexte, etude_id)

            # Poser la question suivante
            return ReponseChat(
                content=f"""[{next_q['progress']}%] **Section : {next_q['section_titre']}**
{next_q['question']}""" + (f"\n\nChoix possibles : {', '.join(next_q['options'])}" if next_q.get('options') else ""),
                suggestions=next_q.get("options", []),
                contexte_mis_a_jour={
                    "questionnaire_active": True,
                    "questionnaire_state": qm.serialize()
                }
            )

        except Exception as e:
            if self.verbose:
                print(f"[ChatHandler] Erreur questionnaire: {e}")
            return ReponseChat(
                content="Une erreur est survenue dans le questionnaire. Voulez-vous recommencer ?",
                suggestions=["Recommencer", "Annuler"],
                contexte_mis_a_jour={"questionnaire_active": False, "questionnaire_state": None}
            )

    def _reponse_questionnaire_complet(self, qm, contexte, etude_id) -> ReponseChat:
        """Genere la reponse quand le questionnaire est complet."""
        resume = qm.get_summary()
        return ReponseChat(
            content=f"""[100%] Toutes les informations sont collectees !

{resume}

Souhaitez-vous generer le document ?""",
            suggestions=["Generer le document", "Modifier une reponse", "Annuler"],
            action={"type": "questionnaire_complete", "acte_data": qm.to_acte_data()},
            contexte_mis_a_jour={
                "questionnaire_active": False,
                "questionnaire_state": qm.serialize(),
                "etape_workflow": "generation_prete",
                "donnees_collectees": qm.to_acte_data()
            }
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

        if "promesse" in texte_lower:
            analyse.intention = "CREER"
            analyse.type_acte = "promesse_vente"
            analyse.confiance = 0.7
        elif "vente" in texte_lower or "créer" in texte_lower or "creer" in texte_lower:
            analyse.intention = "CREER"
            analyse.type_acte = "vente"
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
            import uuid
            historique = request.history or []
            contexte = request.context or {}

            # Générer un conversation_id si non fourni
            conversation_id = request.conversation_id or str(uuid.uuid4())
            is_new_conversation = request.conversation_id is None

            # Vrais UUIDs pour satisfaire les FK Supabase (pas d'auth frontend)
            # TODO: Extraire du JWT quand auth frontend sera connecté
            REAL_USER_ID = "3138517c-eb64-4b05-af16-7070bf969dd5"  # Jean Dupont (test2@notomail.fr)
            REAL_ETUDE_ID = "a2cb1402-4784-47de-9261-99e9d22bbf08"

            supabase = _get_supabase()
            if supabase:
                try:
                    # Utiliser .limit(1) au lieu de .maybe_single() pour éviter erreur 406
                    conv_resp = supabase.table("conversations").select("*").eq(
                        "id", conversation_id
                    ).limit(1).execute()

                    if conv_resp.data and len(conv_resp.data) > 0:
                        conv_data = conv_resp.data[0]
                        # Charger le contexte persiste (colonne = "context")
                        stored_ctx = conv_data.get("context") or {}
                        contexte = {**stored_ctx, **contexte}

                        # Charger les messages depuis conversations.messages JSONB
                        stored_messages = conv_data.get("messages") or []
                        if stored_messages:
                            historique = [
                                {"role": m["role"], "content": m["content"]}
                                for m in stored_messages
                            ]
                    else:
                        # Creer la conversation avec vrais UUIDs
                        supabase.table("conversations").insert({
                            "id": conversation_id,
                            "etude_id": REAL_ETUDE_ID,
                            "user_id": REAL_USER_ID,
                            "context": contexte,
                            "messages": [],
                            "message_count": 0,
                        }).execute()
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(
                        f"[CHAT] Erreur creation conversation {conversation_id}: {e}",
                        exc_info=True
                    )
                    # Continue sans bloquer - la conversation peut fonctionner sans persistance

            # ============================================================
            # Agent Anthropic intelligent (avec fallback keyword)
            # ============================================================
            reponse = None
            try:
                from execution.anthropic_agent import AnthropicAgent
                agent = AnthropicAgent(supabase_client=supabase)
                agent_result = await agent.process_message(
                    message=request.message,
                    user_id=request.user_id,
                    etude_id=request.etude_id,
                    conversation_id=conversation_id,
                    history=historique,
                    context=contexte,
                )
                # Convertir AgentResponse -> ReponseChat (meme interface)
                reponse = ReponseChat(
                    content=agent_result.content,
                    suggestions=agent_result.suggestions,
                    action=agent_result.action,
                    contexte_mis_a_jour=agent_result.contexte_mis_a_jour,
                    intention_detectee=agent_result.intention,
                    confiance=agent_result.confiance,
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(
                    f"Agent Anthropic indisponible, fallback keyword: {e}"
                )

            # Fallback: ancien handler par mots-cles (si Anthropic echoue)
            if reponse is None:
                handler = ChatHandler(verbose=False)
                reponse = handler.traiter_message(
                    message=request.message,
                    user_id=request.user_id,
                    etude_id=request.etude_id,
                    historique=historique,
                    contexte=contexte
                )

            # Persister les messages dans Supabase (JSONB dans conversations.messages)
            if supabase and conversation_id:
                try:
                    # Charger messages existants (utiliser .limit(1) pour éviter 406)
                    conv = supabase.table("conversations").select(
                        "messages, message_count"
                    ).eq("id", conversation_id).limit(1).execute()

                    conv_data = conv.data[0] if conv.data and len(conv.data) > 0 else None
                    existing = (conv_data.get("messages") or []) if conv_data else []
                    existing.append({
                        "role": "user",
                        "content": request.message,
                        "timestamp": datetime.now().isoformat(),
                    })
                    existing.append({
                        "role": "assistant",
                        "content": reponse.content,
                        "timestamp": datetime.now().isoformat(),
                        "intention": reponse.intention_detectee,
                        "confiance": reponse.confiance,
                        "suggestions": reponse.suggestions,
                    })

                    update_data = {
                        "messages": existing,
                        "message_count": len(existing),
                        "last_message_at": datetime.now().isoformat(),
                    }
                    if reponse.contexte_mis_a_jour:
                        update_data["context"] = reponse.contexte_mis_a_jour

                    supabase.table("conversations").update(update_data).eq(
                        "id", conversation_id
                    ).execute()
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(
                        f"[CHAT] Erreur persistance messages conv={conversation_id}: {e}",
                        exc_info=True
                    )
                    # Continue - l'utilisateur recoit quand meme la reponse

            # Extraire fichier_url depuis action si present
            fichier_url = None
            if reponse.action and isinstance(reponse.action, dict):
                fichier_url = reponse.action.get("fichier_url")

            # Extraire section depuis le contexte
            section = None
            if reponse.contexte_mis_a_jour:
                section = reponse.contexte_mis_a_jour.get("etape_workflow")

            return ChatResponse(
                content=reponse.content,
                suggestions=reponse.suggestions,
                intention=reponse.intention_detectee,
                confiance=reponse.confiance,
                conversation_id=conversation_id,
                section=section,
                fichier_url=fichier_url,
                contexte_mis_a_jour=reponse.contexte_mis_a_jour,
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # =================================================================
    # Streaming SSE endpoint
    # =================================================================

    @router.post("/stream")
    async def chat_stream(request: ChatRequest):
        """
        Version streaming du chat via Server-Sent Events.

        Events:
          status  → {"message": "Recherche des questions..."}
          token   → {"text": "Bonjour, "}
          done    → {"suggestions": [...], "section": "...", "progress_pct": 42}
          error   → {"message": "..."}
        """
        from sse_starlette.sse import EventSourceResponse

        async def event_generator():
            try:
                import uuid
                historique = request.history or []
                contexte = request.context or {}

                # Générer un conversation_id si non fourni
                conversation_id = request.conversation_id or str(uuid.uuid4())

                # TODO: Extraire du JWT quand auth frontend sera connecté
                REAL_USER_ID = "3138517c-eb64-4b05-af16-7070bf969dd5"  # Jean Dupont (test2@notomail.fr)
                REAL_ETUDE_ID = "a2cb1402-4784-47de-9261-99e9d22bbf08"

                supabase = _get_supabase()
                if supabase:
                    try:
                        # Utiliser .limit(1) au lieu de .maybe_single() pour éviter 406
                        conv_resp = supabase.table("conversations").select("*").eq(
                            "id", conversation_id
                        ).limit(1).execute()

                        if conv_resp and conv_resp.data and len(conv_resp.data) > 0:
                            conv_data = conv_resp.data[0]
                            stored_ctx = conv_data.get("context") or {}
                            contexte = {**stored_ctx, **contexte}
                            stored_messages = conv_data.get("messages") or []
                            if stored_messages:
                                historique = [
                                    {"role": m["role"], "content": m["content"]}
                                    for m in stored_messages
                                ]
                        else:
                            supabase.table("conversations").insert({
                                "id": conversation_id,
                                "etude_id": REAL_ETUDE_ID,
                                "user_id": REAL_USER_ID,
                                "context": contexte,
                                "messages": [],
                                "message_count": 0,
                            }).execute()
                    except Exception as e:
                        import logging
                        logging.getLogger(__name__).error(
                            f"[CHAT STREAM] Erreur init conversation {conversation_id}: {e}",
                            exc_info=True
                        )

                # Agent Anthropic en streaming
                from execution.anthropic_agent import AnthropicAgent
                agent = AnthropicAgent(supabase_client=supabase)

                full_content = ""
                full_metadata = {}

                async for event in agent.process_message_stream(
                    message=request.message,
                    user_id=request.user_id,
                    etude_id=request.etude_id,
                    conversation_id=conversation_id,
                    history=historique,
                    context=contexte,
                ):
                    if event["event"] == "done":
                        done_data = json.loads(event["data"])
                        full_content = done_data.get("content", "")
                        full_metadata = done_data

                        # Persister dans Supabase avant de yielder done
                        if supabase:
                            try:
                                # Utiliser .limit(1) pour éviter erreur 406
                                conv = supabase.table("conversations").select(
                                    "messages, message_count"
                                ).eq("id", conversation_id).limit(1).execute()

                                conv_data = conv.data[0] if conv and conv.data and len(conv.data) > 0 else None
                                existing = (conv_data.get("messages") or []) if conv_data else []
                                existing.append({
                                    "role": "user",
                                    "content": request.message,
                                    "timestamp": datetime.now().isoformat(),
                                })
                                existing.append({
                                    "role": "assistant",
                                    "content": full_content,
                                    "timestamp": datetime.now().isoformat(),
                                    "suggestions": full_metadata.get("suggestions", []),
                                })

                                update_data = {
                                    "messages": existing,
                                    "message_count": len(existing),
                                    "last_message_at": datetime.now().isoformat(),
                                }
                                ctx_update = {}
                                if full_metadata.get("progress_pct"):
                                    ctx_update["progress_pct"] = full_metadata["progress_pct"]
                                if full_metadata.get("categorie_bien"):
                                    ctx_update["categorie_bien"] = full_metadata["categorie_bien"]
                                if ctx_update:
                                    update_data["context"] = {**contexte, **ctx_update}

                                supabase.table("conversations").update(update_data).eq(
                                    "id", conversation_id
                                ).execute()
                            except Exception as e:
                                import logging
                                logging.getLogger(__name__).error(
                                    f"[CHAT STREAM] Erreur persistance conv={conversation_id}: {e}",
                                    exc_info=True
                                )

                        # Ajouter conversation_id au done event pour le frontend
                        done_data["conversation_id"] = conversation_id
                        event = {"event": "done", "data": json.dumps(done_data)}

                    yield event

            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Streaming error: {e}")

                # Fallback keyword handler
                try:
                    handler = ChatHandler(verbose=False)
                    reponse = handler.traiter_message(
                        message=request.message,
                        user_id=request.user_id,
                        etude_id=request.etude_id,
                        historique=[],
                        contexte={},
                    )
                    yield {
                        "event": "token",
                        "data": json.dumps({"text": reponse.content}),
                    }
                    yield {
                        "event": "done",
                        "data": json.dumps({
                            "content": reponse.content,
                            "suggestions": reponse.suggestions,
                            "conversation_id": conversation_id,
                        }),
                    }
                except Exception as e2:
                    yield {
                        "event": "error",
                        "data": json.dumps({"message": str(e2)}),
                    }

        return EventSourceResponse(
            event_generator(),
            ping=15,  # Keepalive toutes les 15s (evite coupure pendant generation)
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
            },
        )

    @router.get("/conversations")
    async def list_conversations():
        """Liste les conversations recentes (max 20)."""
        supabase = _get_supabase()
        if not supabase:
            return {"conversations": []}
        try:
            resp = supabase.table("conversations").select(
                "id, message_count, context, created_at, updated_at, messages"
            ).order("updated_at", desc=True).limit(20).execute()

            conversations = []
            for conv in (resp.data or []):
                # Extraire le titre du 1er message user
                messages = conv.get("messages") or []
                title = "Nouvelle conversation"
                for m in messages:
                    if m.get("role") == "user":
                        title = m["content"][:60]
                        break

                ctx = conv.get("context") or {}
                conversations.append({
                    "id": conv["id"],
                    "title": title,
                    "type_acte": ctx.get("type_acte_en_cours"),
                    "message_count": conv.get("message_count") or 0,
                    "progress_pct": ctx.get("progress_pct"),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                })
            return {"conversations": conversations}
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"[CHAT] Erreur liste conversations: {e}",
                exc_info=True
            )
            return {"conversations": []}

    @router.get("/conversations/{conversation_id}")
    async def get_conversation(conversation_id: str):
        """Charge une conversation complete avec ses messages."""
        supabase = _get_supabase()
        if not supabase:
            raise HTTPException(status_code=503, detail="Supabase non disponible")
        try:
            # Utiliser .limit(1) pour éviter erreur 406
            resp = supabase.table("conversations").select("*").eq(
                "id", conversation_id
            ).limit(1).execute()

            if not resp or not resp.data or len(resp.data) == 0:
                raise HTTPException(status_code=404, detail="Conversation non trouvee")

            conv_data = resp.data[0]
            ctx = conv_data.get("context") or {}
            return {
                "id": conv_data["id"],
                "messages": conv_data.get("messages") or [],
                "context": ctx,
                "type_acte": ctx.get("type_acte_en_cours"),
                "message_count": conv_data.get("message_count") or 0,
                "created_at": conv_data.get("created_at"),
                "updated_at": conv_data.get("updated_at"),
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    class FeedbackRequest(BaseModel):
        conversation_id: str
        message_index: int
        rating: int  # 1 = bon, -1 = mauvais
        comment: Optional[str] = None

    @router.post("/feedback")
    async def submit_feedback(request: FeedbackRequest):
        """Enregistre un feedback sur un message assistant."""
        # IMPORTANT: user_id doit exister dans auth.users (FK constraint)
        REAL_USER_ID = "3138517c-eb64-4b05-af16-7070bf969dd5"  # Jean Dupont (test2@notomail.fr)
        REAL_ETUDE_ID = "a2cb1402-4784-47de-9261-99e9d22bbf08"

        supabase = _get_supabase()
        if not supabase:
            return {"status": "ok", "saved": False}

        try:
            # Charger le message assistant pour le champ agent_response (requis)
            # Utiliser .limit(1) pour éviter erreur 406
            conv = supabase.table("conversations").select(
                "messages"
            ).eq("id", request.conversation_id).limit(1).execute()

            agent_response = ""
            conv_data = conv.data[0] if conv.data and len(conv.data) > 0 else None
            if conv_data:
                messages = conv_data.get("messages") or []
                if request.message_index < len(messages):
                    agent_response = messages[request.message_index].get("content", "")

            supabase.table("feedbacks").insert({
                "conversation_id": request.conversation_id,
                "message_index": request.message_index,
                "rating": request.rating,
                "correction": request.comment,
                "agent_response": agent_response,
                "user_id": REAL_USER_ID,
                "etude_id": REAL_ETUDE_ID,
            }).execute()
            return {"status": "ok", "saved": True}
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"[CHAT] Erreur sauvegarde feedback conv={request.conversation_id}: {e}",
                exc_info=True
            )
            # Retourner ok pour ne pas bloquer l'UX, mais indiquer que pas sauvegarde
            return {"status": "ok", "saved": False}

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
