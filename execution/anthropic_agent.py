# -*- coding: utf-8 -*-
"""
Agent Anthropic pour le chatbot NotaireAI.

Utilise l'API Anthropic Messages avec tool_use pour orchestrer
la collecte d'informations et la generation d'actes notariaux.

Architecture:
1. Charge historique + agent_state depuis Supabase
2. Anonymise les PII (ChatAnonymizer Python) AVANT envoi
3. Appel Anthropic Messages API avec 8 tools (3-tier prompt caching)
4. Boucle tool_use: execute tool -> envoie tool_result -> repete (max 15 iterations)
5. De-anonymise la reponse finale APRES reception
6. Sauvegarde agent_state dans Supabase

Constantes:
- MAX_TOOL_ITERATIONS = 15  (workflow complet = ~10 appels tools minimum)
- MAX_OUTPUT_TOKENS = 4096  (eviter truncations sur rapports de validation)
- MAX_HISTORY_MESSAGES = 30 (plus de contexte pour conversations longues)

Methodes de chargement de directives:
- _load_full_directive(): charge une directive complete depuis directives/
- _read_directive_file(): lit le contenu brut d'un fichier directive
- _filter_directive_sections(): filtre les sections selon le type d'acte
- _build_session_context(): construit le contexte de session avec directives
- _build_cached_system(): construit le prompt systeme 3-tier avec cache Anthropic
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

# PII anonymization for RGPD compliance
try:
    from execution.security.chat_anonymizer import ChatAnonymizer
    ANONYMIZER_AVAILABLE = True
except ImportError:
    ANONYMIZER_AVAILABLE = False
    logger.warning("ChatAnonymizer non disponible — PII envoyés en clair")


# =============================================================================
# Configuration
# =============================================================================

MODEL = "claude-sonnet-4-20250514"
MAX_TOOL_ITERATIONS = 15   # Workflow complet = ~10 appels tools minimum
MAX_OUTPUT_TOKENS = 4096   # Eviter truncations sur rapports de validation
MAX_HISTORY_MESSAGES = 30  # Plus de contexte pour conversations longues

# DEPRECATED: Messages statiques remplacés par _get_tool_status() dynamique
# Conservé pour référence historique
# TOOL_STATUS_MESSAGES = {
#     "detect_property_type": "Detection du type de bien...",
#     "get_questions": "Recherche des questions...",
#     ...
# }


# =============================================================================
# System Prompt
# =============================================================================

SYSTEM_PROMPT = """\
Tu es NotaireAI, un assistant intelligent specialise dans la creation \
d'actes notariaux pour les etudes notariales francaises.

## Ton role
Tu guides les notaires pas a pas pour collecter les informations necessaires \
et generer des promesses de vente et actes de vente 100% conformes aux trames originales.
Tu es un expert du droit immobilier francais et de la redaction notariale.

## Types d'actes supportes
- **Promesse de vente** (type_acte="promesse_vente"): couvre TOUTES les categories de bien
- **Acte de vente definitif** (type_acte="vente"): lots de copropriete

Quand le notaire demande un "acte de vente" ou une "vente", utilise type_acte="vente".
Quand il demande une "promesse" ou un "compromis", utilise type_acte="promesse_vente".

---

## Architecture de detection 3 niveaux (CRITIQUE)

Le systeme selectionne automatiquement le bon template via 3 niveaux de detection:

### Niveau 1 — Categorie de bien (determine le template)
| Categorie | Marqueurs | Template |
|-----------|-----------|----------|
| **Copropriete** | syndic, lots, tantiemes, EDD, numero lot | promesse_vente_lots_copropriete.md |
| **Hors copropriete** | maison, villa, local commercial, copropriete=false | promesse_hors_copropriete.md |
| **Terrain a batir** | lotissement, viabilisation, constructibilite, COS | promesse_terrain_a_batir.md |

### Niveau 2 — Type de transaction (sections conditionnelles)
standard, premium, avec_mobilier, multi_biens

### Niveau 3 — Sous-types (sections speciales)
| Sous-type | Marqueurs | Effet |
|-----------|-----------|-------|
| **viager** | prix.type_vente="viager", rente_viagere, bouquet (dict), DUH | **PRIORITAIRE** — template viager dedie (promesse_viager.md) |
| **creation** | pas syndic + pas reglement + lots, en_creation=true | Sections creation copro |
| **lotissement** | bien.lotissement | Section dispositions lotissement |
| **groupe_habitations** | bien.groupe_habitations | Section groupe habitations |
| **avec_servitudes** | bien.servitudes[] | Section servitudes actives/passives |

**REGLE VIAGER** : Le viager est PRIORITAIRE sur la categorie de bien. Un viager en copro, \
hors copro ou terrain utilise TOUJOURS le template viager. Detection par 6 marqueurs ponderes, seuil >= 2.

---

## Tes 8 outils — Guide d'utilisation

### 1. detect_property_type
**Quand** : Des que le notaire mentionne le type de bien.
**Input** : {"bien": {"type": "appartement"}, "copropriete": {"syndic": {...}}}
**Output** : categorie (copropriete/hors_copropriete/terrain_a_batir) + description

### 2. get_questions
**Quand** : Apres detection, pour obtenir les questions d'une section.
**Input** : {"section_key": "1_identification_parties"}
**Sections principales** : 1_identification_parties, 2_designation_bien, 3_prix_paiement, \
4_conditions_suspensives, 5_diagnostics, 6_copropriete, 7_urbanisme, 8_origine_propriete, \
8f_creation_copropriete, 15_viager
**Output** : liste de questions avec conditions d'affichage

### 3. submit_answers (CRITIQUE)
**Quand** : A CHAQUE fois que le notaire fournit des informations. Ne jamais accumuler.
**Input** : objet structure avec les donnees extraites du message.
**IMPORTANT — Structure des parties** :
  - Pour promesse : "promettants" (vendeurs) et "beneficiaires" (acquereurs)
  - Pour vente : "vendeurs" et "acquereurs"
  - NE PAS melanger les deux schemas
**Exemple** :
```json
{
  "promettants": [{"nom": "Martin", "prenoms": "Jean", "date_naissance": "15/03/1965",
    "lieu_naissance": "Paris", "nationalite": "francaise",
    "adresse": {"voie": "12 rue des Lilas", "code_postal": "75008", "ville": "Paris"},
    "situation_matrimoniale": {"statut": "marie", "regime": "communaute_legale",
      "conjoint": {"nom": "Martin", "prenoms": "Sophie"}}}],
  "beneficiaires": [{"nom": "Dupont", "prenoms": "Marie"}],
  "bien": {"adresse": {"numero": "15", "rue": "rue des Fleurs", "code_postal": "75008",
    "ville": "Paris"}, "type_bien": "appartement"},
  "prix": {"montant": 450000, "lettres": "quatre cent cinquante mille euros"}
}
```

### 4. get_collection_progress
**Quand** : Pour savoir ce qui manque. Utiliser apres 3-4 submit_answers.
**Output** : pourcentage, sections completees, champs_manquants

### 5. validate_deed_data
**Quand** : Quand progression >= 70% ou avant generation.
**Regles verifiees** :
  - Quotites vendues ET acquises = 100% exactement
  - Prix > 0 et coherent avec le type de bien
  - Carrez obligatoire pour lots de copropriete > 8 m2
  - Regime matrimonial renseigne si marie/pacse
  - Diagnostics obligatoires presents
**Output** : valide (bool), erreurs[], avertissements[]

### 6. generate_document
**Quand** : SEULEMENT apres submit_answers + validate_deed_data.
**Input** : {"type_acte": "promesse_vente"} ou {"type_acte": "vente"}
**Avec force=true** : genere meme si donnees incompletes (notaire complete manuellement)
**Output** : succes, fichier_docx, fichier_url, duree_generation

### 7. search_clauses
**Quand** : Si le notaire demande une clause specifique, ou pour enrichir l'acte.
**Input** : {"query": "condition suspensive pret", "type_acte": "promesse_vente"}
**Output** : clauses correspondantes avec texte, categorie, priorite

### 8. submit_feedback
**Quand** : Si le notaire signale une erreur ou demande une amelioration.
**Input** : {"action": "corriger", "cible": "clause", "contenu": "...", "raison": "..."}

---

## Workflow en 7 etapes

1. **Identifier** : Le notaire dit ce qu'il veut → determiner type_acte
2. **Detecter** : Appeler detect_property_type avec les infos du bien
3. **Collecter section par section** :
   - Appeler get_questions pour la section courante
   - Poser 2-4 questions de maniere conversationnelle
   - Appeler submit_answers IMMEDIATEMENT avec les reponses
   - Passer a la section suivante
4. **Verifier** : Appeler get_collection_progress regulierement (tous les 3-4 echanges)
5. **Valider** : Appeler validate_deed_data quand >= 70%
6. **Generer** : Appeler generate_document si validation OK
7. **Livrer** : Presenter le lien de telechargement + resume

---

## Regles de communication
- TOUJOURS en francais, vouvoiement
- Professionnel mais accessible — ne pas etre trop verbeux
- Poser 2 a 4 questions a la fois maximum, pas plus
- Resumer regulierement ce qui a ete collecte (tous les 3-4 echanges)
- Proposer des suggestions pertinentes
- Citer les references legales si necessaire (Code civil, CCH)

## Format de reponse
- Section en cours entre crochets: [Identification du vendeur]
- Suggestions d'actions: SUGGESTIONS: option1 | option2 | option3
- Document genere: FICHIER: /chemin/du/fichier.docx

---

## REGLE CRITIQUE N°1 — Enregistrement des donnees
AVANT de generer un document, tu DOIS TOUJOURS appeler submit_answers pour enregistrer \
les informations fournies par le notaire. Sinon, le document sera VIDE.

Quand le notaire fournit des informations :
1. Extraire TOUTES les donnees du message
2. Appeler submit_answers avec un objet structure (voir exemples ci-dessus)
3. SEULEMENT APRES avoir appele submit_answers, appeler generate_document

## REGLE CRITIQUE N°2 — Validation avant generation
TOUJOURS appeler validate_deed_data AVANT generate_document (sauf si force=true).
Les erreurs de quotites (!=100%) ou de prix manquant produisent un document invalide.

## REGLE CRITIQUE N°3 — Generation forcee
Si le notaire demande explicitement de generer (meme incomplet), utilise force=true.
Phrases declencheuses: "genere quand meme", "genere le document", "telecharger maintenant", \
"force la generation", "je veux generer", "generer avec les infos actuelles".
MAIS TOUJOURS appeler submit_answers AVANT generate_document avec les donnees deja collectees.
Affiche un avertissement sur les champs manquants mais genere le fichier DOCX.

---

## Regles de validation metier
- **Quotites** : quotites_vendues ET quotites_acquises doivent totaliser exactement 100%
- **Carrez** : obligatoire pour tout lot de copropriete > 8 m2
- **Regime matrimonial** : si statut=marie ou pacse → regime et conjoint obligatoires
- **Viager** : bouquet ET rente_viagere obligatoires si type_vente=viager
- **Creation copro** : verifier qu'il n'y a PAS de syndic/immatriculation existants
- **Prix** : montant > 0, coherent avec lettres si fourni
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

    # Sections a exclure des directives (historique, liens, metriques)
    _DIRECTIVE_SKIP_SECTIONS = {
        "## Historique", "## Version", "## Changelog", "## Voir aussi",
        "## Liens", "## Performance", "## Metriques", "## Tests",
        "## Commandes CLI", "## API Endpoints", "## Frontend",
    }

    # Mapping type_acte → fichiers directives (principal + complementaire)
    _DIRECTIVE_MAPPING = {
        "promesse_vente": ["creer_promesse_vente.md", "workflow_notaire.md"],
        "promesse": ["creer_promesse_vente.md", "workflow_notaire.md"],
        "vente": ["creer_acte.md", "workflow_notaire.md"],
        "reglement_copropriete": ["creer_reglement_copropriete.md"],
        "reglement": ["creer_reglement_copropriete.md"],
        "modificatif_edd": ["creer_modificatif_edd.md"],
        "modificatif": ["creer_modificatif_edd.md"],
        "donation_partage": ["creer_donation_partage.md"],
        "donation": ["creer_donation_partage.md"],
    }

    def _load_full_directive(self, type_acte: str) -> str:
        """Charge les directives completes pour le type d'acte.

        Contrairement a l'ancien _load_directive_summary() qui tronquait a 3KB,
        cette methode charge le contenu complet en filtrant les sections
        non-pertinentes (historique, version, liens, CLI, API).

        Le contenu est cache via prompt caching Anthropic (cache_control ephemeral)
        donc le cout supplementaire est negligeable apres le 1er message.

        Cap: ~32000 chars (~8000 tokens) par directive.
        """
        from pathlib import Path

        filenames = self._DIRECTIVE_MAPPING.get(type_acte, [])
        if not filenames:
            return ""

        parts = []
        total_chars = 0
        max_chars = 32000  # ~8000 tokens

        for filename in filenames:
            if total_chars >= max_chars:
                break

            content = self._read_directive_file(filename)
            if not content:
                continue

            # Filtrer les sections non-pertinentes
            filtered = self._filter_directive_sections(content)
            remaining = max_chars - total_chars
            if len(filtered) > remaining:
                filtered = filtered[:remaining]

            parts.append(f"\n## Directive: {filename}\n{filtered}")
            total_chars += len(filtered)

        return "\n".join(parts) if parts else ""

    def _read_directive_file(self, filename: str) -> str:
        """Lit un fichier directive depuis le filesystem (Modal ou local)."""
        from pathlib import Path

        paths = [
            Path("/root/project/directives") / filename,  # Modal
            Path(__file__).parent.parent / "directives" / filename,  # Local
        ]

        for path in paths:
            try:
                if path.exists():
                    return path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Erreur lecture directive {filename}: {e}")

        return ""

    def _filter_directive_sections(self, content: str) -> str:
        """Filtre les sections non-pertinentes d'une directive.

        Garde: workflow, detection, validation, structures, regles.
        Supprime: historique, version, liens, CLI, API, metriques.
        """
        lines = content.split("\n")
        result = []
        skip = False

        for line in lines:
            # Detecter les headings de niveau 2
            if line.startswith("## "):
                heading = line.strip()
                skip = any(heading.startswith(s) for s in self._DIRECTIVE_SKIP_SECTIONS)

            if not skip:
                result.append(line)

        return "\n".join(result)

    # =========================================================================
    # Construction du prompt et des messages
    # =========================================================================

    def _build_system_prompt(self, agent_state: Dict) -> str:
        """System prompt complet (fallback sans prompt caching)."""
        parts = [SYSTEM_PROMPT]

        # Directives completes si type_acte connu
        if agent_state.get("type_acte"):
            directive = self._load_full_directive(agent_state['type_acte'])
            if directive:
                parts.append(directive)

        # Contexte dynamique
        parts.append(self._build_session_context(agent_state))

        return "\n".join(parts)

    def _build_session_context(self, agent_state: Dict) -> str:
        """Construit le contexte dynamique de la session."""
        if not agent_state:
            return ""

        parts = ["\n## Contexte de la session en cours"]
        if agent_state.get("type_acte"):
            parts.append(f"- Type d'acte: {agent_state['type_acte']}")
        if agent_state.get("categorie_bien"):
            parts.append(f"- Categorie de bien: {agent_state['categorie_bien']}")
        if agent_state.get("progress_pct") is not None:
            parts.append(f"- Progression collecte: {agent_state['progress_pct']}%")
        if agent_state.get("fichier_genere"):
            parts.append(f"- Dernier fichier genere: {agent_state['fichier_genere']}")

        # Resume des donnees collectees (aide l'agent a ne pas re-demander)
        donnees = agent_state.get("donnees_collectees", {})
        if donnees:
            collected = []
            if donnees.get("promettants") or donnees.get("vendeurs"):
                vendeurs = donnees.get("promettants") or donnees.get("vendeurs") or []
                noms = [v.get("nom", "?") for v in vendeurs if v.get("nom")]
                if noms:
                    collected.append(f"Vendeur(s): {', '.join(noms)}")
            if donnees.get("beneficiaires") or donnees.get("acquereurs"):
                acquereurs = donnees.get("beneficiaires") or donnees.get("acquereurs") or []
                noms = [a.get("nom", "?") for a in acquereurs if a.get("nom")]
                if noms:
                    collected.append(f"Acquereur(s): {', '.join(noms)}")
            bien = donnees.get("bien", {})
            adresse = bien.get("adresse", {})
            if adresse.get("voie") or adresse.get("rue"):
                collected.append(f"Bien: {adresse.get('voie') or adresse.get('rue')}, {adresse.get('ville', '')}")
            prix = donnees.get("prix", {})
            if prix.get("montant"):
                collected.append(f"Prix: {prix['montant']:,} EUR".replace(",", " "))
            if collected:
                parts.append("- Donnees deja collectees: " + " | ".join(collected))

        return "\n".join(parts)

    def _build_cached_system(self, agent_state: Dict) -> list:
        """System prompt avec prompt caching Anthropic en 3 tiers.

        Tier 1 (cache): SYSTEM_PROMPT core — identite, detection, outils, workflow, regles.
        Tier 2 (cache): Directive complete pour le type_acte detecte.
        Tier 3 (dynamique): Contexte session — progression, donnees collectees.

        Les tiers 1 et 2 sont caches (cache_control ephemeral, TTL 5 min).
        Apres le 1er message, ils coutent 1/10e du prix.
        """
        # Tier 1: Core system prompt (toujours cache)
        blocks = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ]

        # Tier 2: Directive complete (cache, charge quand type_acte connu)
        if agent_state.get("type_acte"):
            directive = self._load_full_directive(agent_state['type_acte'])
            if directive:
                blocks.append({
                    "type": "text",
                    "text": directive,
                    "cache_control": {"type": "ephemeral"},
                })

        # Tier 3: Contexte dynamique de la session (jamais cache)
        session_ctx = self._build_session_context(agent_state)
        if session_ctx:
            blocks.append({"type": "text", "text": session_ctx})

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

        # Fallback fichier depuis agent_state (fichier_url > fichier_genere)
        if not fichier_url and agent_state.get("fichier_url"):
            fichier_url = agent_state["fichier_url"]
        elif not fichier_url and agent_state.get("fichier_genere"):
            fichier_url = agent_state["fichier_genere"]

        # Transformer chemin local ou /files/ en URL signée avec HMAC-SHA256
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
            suggestions=suggestions or self._generate_suggestions(agent_state),
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
    # Suggestions et résumés intelligents (SANS appel API)
    # =========================================================================

    def _generate_suggestions(self, agent_state: Dict) -> List[str]:
        """
        Génère des suggestions contextuelles basées sur l'état de l'agent.
        SANS appel API - 100% local.
        """
        suggestions = []

        progress = agent_state.get("progress", {})
        pct = progress.get("pourcentage", 0)
        type_acte = agent_state.get("type_acte")
        donnees = agent_state.get("donnees_collectees", {})
        manquants = progress.get("champs_manquants", [])

        # Cas 1: Document prêt
        if pct >= 100:
            suggestions.append("Générer le document")
            suggestions.append("Vérifier les données")
            if type_acte:
                suggestions.append(f"Modifier le {type_acte}")

        # Cas 2: Collecte en cours
        elif pct > 0:
            if manquants:
                # Suggestion basée sur le premier champ manquant
                premier_manquant = manquants[0]
                if "prix" in premier_manquant.lower():
                    suggestions.append("Renseigner le prix")
                elif "vendeur" in premier_manquant.lower() or "promettant" in premier_manquant.lower():
                    suggestions.append("Ajouter un vendeur")
                elif "acquereur" in premier_manquant.lower() or "beneficiaire" in premier_manquant.lower():
                    suggestions.append("Ajouter un acquéreur")
                elif "bien" in premier_manquant.lower() or "adresse" in premier_manquant.lower():
                    suggestions.append("Décrire le bien")
                else:
                    suggestions.append(f"Renseigner {premier_manquant}")
            suggestions.append("Voir la progression")
            if pct >= 70:
                suggestions.append("Générer un brouillon")

        # Cas 3: Type d'acte connu mais pas de données
        elif type_acte:
            suggestions.append("Commencer par le vendeur")
            suggestions.append("Commencer par l'acquéreur")
            suggestions.append("Décrire le bien")

        # Cas 4: Début de conversation
        else:
            suggestions.append("Créer une promesse de vente")
            suggestions.append("Créer un acte de vente")
            suggestions.append("Voir mes dossiers")

        return suggestions[:4]  # Max 4 suggestions

    def _build_smart_summary(self, agent_state: Dict) -> str:
        """
        Génère un résumé intelligent de ce qui a été collecté.
        SANS appel API - 100% local, économise ~500-1000 tokens.
        """
        donnees = agent_state.get("donnees_collectees", {})
        type_acte = agent_state.get("type_acte", "l'acte")
        progress = agent_state.get("progress", {})

        # Construire les parties collectées
        parts = []

        # Vendeurs/Promettants
        promettants = donnees.get("promettants", [])
        if promettants:
            noms = [p.get("nom", "?") for p in promettants if p.get("nom")]
            if noms:
                parts.append(f"Vendeur(s) : {', '.join(noms)}")

        # Acquéreurs/Bénéficiaires
        beneficiaires = donnees.get("beneficiaires", [])
        if beneficiaires:
            noms = [b.get("nom", "?") for b in beneficiaires if b.get("nom")]
            if noms:
                parts.append(f"Acquéreur(s) : {', '.join(noms)}")

        # Bien
        bien = donnees.get("bien", {})
        adresse = bien.get("adresse", {})
        if adresse.get("voie"):
            parts.append(f"Bien : {adresse.get('voie')}, {adresse.get('ville', '')}")

        # Prix
        prix = donnees.get("prix", {})
        if prix.get("montant"):
            parts.append(f"Prix : {prix['montant']:,} €".replace(",", " "))

        # Construire le message selon la progression
        pct = progress.get("pourcentage", 0)
        manquants = progress.get("champs_manquants", [])[:3]

        if pct >= 100:
            resume = "Toutes les informations sont collectées :\n"
            resume += "\n".join(f"• {p}" for p in parts)
            resume += "\n\nSouhaitez-vous générer le document ?"
        elif pct > 50 and parts:
            resume = f"J'ai enregistré {pct}% des informations :\n"
            resume += "\n".join(f"• {p}" for p in parts)
            if manquants:
                resume += f"\n\nIl me manque encore : {', '.join(manquants[:3])}"
        elif parts:
            resume = "J'ai noté :\n"
            resume += "\n".join(f"• {p}" for p in parts)
            resume += f"\n\nContinuons avec les détails de {type_acte}."
        else:
            resume = f"Je suis prêt à vous aider avec {type_acte}. Par quoi souhaitez-vous commencer ?"

        return resume

    def _get_tool_status(self, tool_name: str, agent_state: Dict) -> str:
        """
        Génère un message de statut contextuel pour un outil.
        Remplace les messages génériques statiques.
        """
        type_acte = agent_state.get("type_acte", "l'acte")
        section = agent_state.get("section_courante", "")
        categorie = agent_state.get("categorie_bien", "")

        templates = {
            "detect_property_type": f"Analyse du type de bien{' (' + categorie + ')' if categorie else ''}...",
            "get_questions": f"Chargement des questions{' pour ' + section if section else ''}...",
            "submit_answers": "Enregistrement de vos réponses...",
            "get_collection_progress": f"Calcul de l'avancement de {type_acte}...",
            "validate_deed_data": "Vérification de la cohérence des données...",
            "generate_document": f"Génération de {type_acte}...",
            "search_clauses": "Recherche de clauses adaptées...",
            "submit_feedback": "Enregistrement de votre retour...",
        }

        return templates.get(tool_name, f"Traitement en cours...")

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

        # 1b. Anonymiser les PII avant envoi (RGPD)
        anon_mapping = None
        if ANONYMIZER_AVAILABLE:
            try:
                anonymizer = ChatAnonymizer()
                message, anon_mapping = anonymizer.anonymiser(message)
                if history:
                    history_anonyme = []
                    for msg in history:
                        if isinstance(msg.get("content"), str):
                            msg_anon, _ = anonymizer.anonymiser(msg["content"])
                            history_anonyme.append({**msg, "content": msg_anon})
                        else:
                            history_anonyme.append(msg)
                    history = history_anonyme
            except Exception as e:
                logger.warning(f"Anonymisation échouée, envoi en clair: {e}")

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

                # De-anonymiser la reponse (RGPD)
                if ANONYMIZER_AVAILABLE and anon_mapping:
                    try:
                        final_text = anonymizer.deanonymiser(final_text, anon_mapping)
                    except Exception as e:
                        logger.warning(f"De-anonymisation échouée: {e}")

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

        # Max iterations atteint - résumé intelligent SANS appel API
        logger.warning(f"Max tool iterations ({MAX_TOOL_ITERATIONS}) atteint pour conversation {conversation_id}")

        # Générer un résumé local à partir de agent_state (économise ~500-1000 tokens)
        summary_text = self._build_smart_summary(agent_state)

        self._save_agent_state(conversation_id, agent_state)
        return self._parse_response(summary_text, agent_state)

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

        # 1b. Anonymiser les PII avant envoi (RGPD)
        anon_mapping = None
        anonymizer = None
        if ANONYMIZER_AVAILABLE:
            try:
                anonymizer = ChatAnonymizer()
                message, anon_mapping = anonymizer.anonymiser(message)
                if history:
                    history_anonyme = []
                    for msg in history:
                        if isinstance(msg.get("content"), str):
                            msg_anon, _ = anonymizer.anonymiser(msg["content"])
                            history_anonyme.append({**msg, "content": msg_anon})
                        else:
                            history_anonyme.append(msg)
                    history = history_anonyme
            except Exception as e:
                logger.warning(f"Anonymisation stream échouée, envoi en clair: {e}")

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

                # De-anonymiser la reponse (RGPD)
                if ANONYMIZER_AVAILABLE and anon_mapping and anonymizer:
                    try:
                        final_text = anonymizer.deanonymiser(final_text, anon_mapping)
                    except Exception as e:
                        logger.warning(f"De-anonymisation stream échouée: {e}")

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
                        # Message de statut contextuel (dynamique selon agent_state)
                        status_msg = self._get_tool_status(block.name, agent_state)
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

                        # Emettre un event file_ready si document genere
                        if block.name == "generate_document" and result.get("succes"):
                            yield {
                                "event": "file_ready",
                                "data": json.dumps({
                                    "fichier_url": result.get("fichier_url"),
                                    "type_acte": result.get("type_acte"),
                                }),
                            }

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

        # Max iterations - résumé intelligent SANS appel API (économise ~500-1000 tokens)
        logger.warning(f"Max tool iterations atteint (stream) pour conversation {conversation_id}")

        # Générer un résumé local à partir de agent_state
        summary_text = self._build_smart_summary(agent_state)

        self._save_agent_state(conversation_id, agent_state)
        yield {"event": "token", "data": json.dumps({"text": summary_text})}
        yield {
            "event": "done",
            "data": json.dumps({
                "content": summary_text,
                "suggestions": self._generate_suggestions(agent_state),
            }),
        }
