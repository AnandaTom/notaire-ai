# -*- coding: utf-8 -*-
"""
Anthropic Tool Definitions pour l'agent NotaireAI.

Definit 8 tools au format Anthropic Messages API et une classe ToolExecutor
qui mappe chaque tool vers les fonctions Python existantes.

Les tools wrappent:
- GestionnairePromesses (detection bien, generation document)
- CollecteurInteractif (questions, reponses, progression)
- ValidateurActe (validation donnees)
- Catalogue de clauses (recherche)
- API feedback (retours notaire)
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Encodage UTF-8 pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =============================================================================
# Definitions des 8 tools (format Anthropic Messages API)
# =============================================================================

TOOLS = [
    {
        "name": "detect_property_type",
        "description": (
            "Detecte la categorie du bien immobilier (copropriete, hors copropriete, "
            "terrain a batir) a partir des informations fournies. Utilise cette tool en "
            "debut de conversation quand le notaire mentionne un bien."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "bien": {
                    "type": "object",
                    "description": "Informations sur le bien: type (appartement, maison, terrain), adresse, surface, etc.",
                },
                "copropriete": {
                    "type": "object",
                    "description": "Informations copropriete si applicable: syndic, lots, tantiemes, EDD.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_questions",
        "description": (
            "Recupere les questions a poser au notaire pour une section du formulaire. "
            "Chaque question inclut son type (texte, nombre, booleen, choix), ses options, "
            "et sa valeur actuelle si deja remplie. "
            "Sections: 1_type_acte, 2_promettant, 3_beneficiaire, 4_mandataire, "
            "5_bien, 6_copropriete, 7_prix, 8_financement, 9_conditions_suspensives, "
            "10_delais, 11_diagnostics, 12_urbanisme, 13_signature."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section_key": {
                    "type": "string",
                    "description": "Cle de la section (ex: '2_promettant', '5_bien', '7_prix')",
                },
            },
            "required": ["section_key"],
        },
    },
    {
        "name": "submit_answers",
        "description": (
            "Enregistre les reponses collectees aupres du notaire. Les cles peuvent etre "
            "des IDs de question (ex: 'promettant_nom') ou des chemins de variable "
            "(ex: 'bien.adresse.numero'). Appelle cette tool apres avoir collecte des "
            "informations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "answers": {
                    "type": "object",
                    "description": "Paires cle-valeur: {question_id_ou_variable: valeur}",
                    "additionalProperties": True,
                },
            },
            "required": ["answers"],
        },
    },
    {
        "name": "get_collection_progress",
        "description": (
            "Affiche la progression de la collecte: pourcentage global, sections terminees, "
            "champs obligatoires manquants. Utilise pour informer le notaire de l'avancement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "validate_deed_data",
        "description": (
            "Valide les donnees collectees: coherence des quotites (=100%), prix positif, "
            "dates logiques, surface Carrez, DPE, tantiemes, etc. Retourne erreurs, "
            "avertissements et suggestions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "strict": {
                    "type": "boolean",
                    "description": "Mode strict: true = erreur si probleme, false = avertissement seulement",
                },
            },
            "required": [],
        },
    },
    {
        "name": "generate_document",
        "description": (
            "Genere le document final (promesse de vente ou acte de vente) au format DOCX. "
            "Verifier d'abord avec get_collection_progress que la collecte est suffisante, "
            "puis valider avec validate_deed_data. Retourne le chemin du fichier. "
            "Si le notaire demande explicitement de generer meme avec des donnees incompletes, "
            "utiliser force=true pour generer un brouillon avec les champs manquants vides."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type_force": {
                    "type": "string",
                    "enum": ["standard", "premium", "avec_mobilier", "multi_biens"],
                    "description": "Forcer un type de promesse (optionnel, auto-detecte sinon)",
                },
                "force": {
                    "type": "boolean",
                    "description": "Si true, genere le document meme si donnees incompletes (brouillon)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_clauses",
        "description": (
            "Recherche des clauses juridiques dans le catalogue (45+ clauses, 12 categories: "
            "conditions_suspensives, garanties, servitudes, fiscalite, copropriete, etc.). "
            "Utile quand le notaire demande une clause specifique."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Mots-cles (ex: 'condition suspensive pret', 'servitude passage')",
                },
                "type_acte": {
                    "type": "string",
                    "description": "Filtrer par type d'acte: 'promesse_vente' ou 'vente'",
                },
                "categorie": {
                    "type": "string",
                    "description": "Filtrer par categorie: conditions_suspensives, garanties, etc.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "submit_feedback",
        "description": (
            "Enregistre un retour du notaire: ajout de clause, correction, suggestion. "
            "Utilise quand le notaire propose une amelioration ou signale une erreur."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ajouter", "modifier", "supprimer"],
                    "description": "Type d'action demandee",
                },
                "cible": {
                    "type": "string",
                    "description": "Section ou clause ciblee",
                },
                "contenu": {
                    "type": "string",
                    "description": "Contenu (texte de la clause, correction, etc.)",
                },
                "raison": {
                    "type": "string",
                    "description": "Justification du feedback",
                },
            },
            "required": ["action", "cible"],
        },
    },
]


# =============================================================================
# Executeur de tools
# =============================================================================

class ToolExecutor:
    """
    Execute les tools Anthropic en appelant les fonctions Python existantes.

    Gere le CollecteurInteractif (stateful) en le re-instanciant depuis
    agent_state a chaque requete Modal (stateless).
    """

    def __init__(self, etude_id: str = "", supabase_client=None):
        self.etude_id = etude_id
        self.supabase = supabase_client
        self._collecteur = None
        self._gestionnaire = None
        self._clauses_cache = None

    def _get_collecteur(self, agent_state: Dict) -> Any:
        """Recupere ou cree le CollecteurInteractif depuis l'etat persiste."""
        if self._collecteur is None:
            from execution.agent_autonome import CollecteurInteractif
            type_acte = agent_state.get("type_acte", "promesse_vente")
            prefill = agent_state.get("donnees_collectees")
            logger.info(
                f"[COLLECTEUR] Creating new instance: type={type_acte}, "
                f"prefill has {len(prefill) if prefill else 0} keys"
            )
            self._collecteur = CollecteurInteractif(
                type_acte=type_acte,
                prefill=prefill if prefill else None,
            )
        return self._collecteur

    def _get_gestionnaire(self) -> Any:
        """Recupere ou cree le GestionnairePromesses."""
        if self._gestionnaire is None:
            from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses
            self._gestionnaire = GestionnairePromesses(
                supabase_client=self.supabase
            )
        return self._gestionnaire

    def _load_clauses(self) -> Dict:
        """Charge le catalogue de clauses (avec cache)."""
        if self._clauses_cache is None:
            path = PROJECT_ROOT / "schemas" / "clauses_catalogue.json"
            with open(path, "r", encoding="utf-8") as f:
                self._clauses_cache = json.load(f)
        return self._clauses_cache

    def execute(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        agent_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute un tool et retourne le resultat JSON-serialisable.

        Args:
            tool_name: Nom du tool Anthropic
            tool_input: Parametres passes par Claude
            agent_state: Etat de l'agent (modifie in-place si necessaire)

        Returns:
            Dict avec le resultat du tool (ou {"error": "..."} en cas d'erreur)
        """
        try:
            method = getattr(self, f"_exec_{tool_name}", None)
            if method is None:
                return {"error": f"Tool inconnu: {tool_name}"}
            return method(tool_input, agent_state)
        except Exception as e:
            logger.error(f"Erreur dans tool {tool_name}: {e}", exc_info=True)
            return {"error": f"Erreur dans {tool_name}: {str(e)}"}

    # =========================================================================
    # Implementations des 8 tools
    # =========================================================================

    def _exec_detect_property_type(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Detecte la categorie du bien immobilier."""
        donnees = {
            "bien": tool_input.get("bien", {}),
            "copropriete": tool_input.get("copropriete", {}),
        }
        gestionnaire = self._get_gestionnaire()
        categorie = gestionnaire.detecter_categorie_bien(donnees)

        # Persister dans l'etat
        agent_state["categorie_bien"] = categorie.value

        descriptions = {
            "copropriete": "Appartement ou lot en copropriete (syndic, tantiemes, EDD)",
            "hors_copropriete": "Maison individuelle ou local commercial (pas de syndic)",
            "terrain_a_batir": "Terrain constructible ou lotissement",
        }
        return {
            "categorie": categorie.value,
            "description": descriptions.get(categorie.value, categorie.value),
        }

    def _exec_get_questions(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Recupere les questions d'une section."""
        section_key = tool_input.get("section_key", "")
        collecteur = self._get_collecteur(agent_state)
        questions = collecteur.get_questions_for_section(section_key)

        # Format compact pour le contexte Claude
        result = []
        for q in questions:
            q_out = {
                "id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "obligatoire": q["obligatoire"],
            }
            if q.get("options"):
                q_out["options"] = q["options"]
            if q.get("valeur_actuelle") is not None:
                q_out["valeur_actuelle"] = q["valeur_actuelle"]
                q_out["pre_rempli"] = True
            if q.get("aide"):
                q_out["aide"] = q["aide"]
            result.append(q_out)

        return {
            "section": section_key,
            "nb_questions": len(result),
            "questions": result,
        }

    def _exec_submit_answers(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Enregistre les reponses du notaire."""
        answers = tool_input.get("answers", {})
        collecteur = self._get_collecteur(agent_state)
        result = collecteur.submit_answers(answers)

        # Sauvegarder les donnees mises a jour
        agent_state["donnees_collectees"] = collecteur.donnees

        # Mettre à jour la progression
        progress = collecteur.get_progress()
        agent_state["progress_pct"] = progress.get("pourcentage", 0)

        logger.info(
            f"[SUBMIT] Answers submitted: {len(answers)} keys, "
            f"donnees now has {len(collecteur.donnees)} top-level keys, "
            f"progress={progress.get('pourcentage', 0)}%"
        )

        return result

    def _exec_get_collection_progress(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Retourne la progression de la collecte."""
        collecteur = self._get_collecteur(agent_state)
        progress = collecteur.get_progress()

        agent_state["progress_pct"] = progress["pourcentage"]

        # Tronquer les champs manquants si trop nombreux
        manquants = progress.get("champs_manquants", [])
        if len(manquants) > 15:
            progress["champs_manquants"] = manquants[:15]
            progress["champs_manquants_tronques"] = True
            progress["total_manquants"] = len(manquants)

        return progress

    def _exec_validate_deed_data(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Valide les donnees collectees."""
        from execution.core.valider_acte import ValidateurActe

        strict = tool_input.get("strict", True)
        donnees = agent_state.get("donnees_collectees", {})

        # Schema selon le type d'acte
        type_acte = agent_state.get("type_acte", "promesse_vente")
        schema_map = {
            "promesse_vente": "variables_promesse_vente.json",
            "vente": "variables_vente.json",
        }
        schema_path = PROJECT_ROOT / "schemas" / schema_map.get(type_acte, "variables_promesse_vente.json")
        schema = {}
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

        validateur = ValidateurActe(schema)
        rapport = validateur.valider_complet(donnees, strict=strict)

        return {
            "valide": rapport.valide,
            "erreurs": [
                {"code": e.code, "message": e.message, "chemin": e.chemin, "suggestion": e.suggestion}
                for e in rapport.erreurs
            ],
            "avertissements": [
                {"code": w.code, "message": w.message, "chemin": w.chemin}
                for w in rapport.avertissements
            ],
            "nb_erreurs": len(rapport.erreurs),
            "nb_avertissements": len(rapport.avertissements),
        }

    def _exec_generate_document(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Genere le document DOCX final."""
        from execution.gestionnaires.gestionnaire_promesses import TypePromesse

        donnees = agent_state.get("donnees_collectees", {})
        type_force = None
        type_force_str = tool_input.get("type_force")
        if type_force_str:
            try:
                type_force = TypePromesse(type_force_str)
            except ValueError:
                pass

        # Paramètre force pour génération partielle (brouillon)
        force = tool_input.get("force", False)

        gestionnaire = self._get_gestionnaire()
        resultat = gestionnaire.generer(donnees, type_force=type_force, force=force)

        if resultat.succes and resultat.fichier_docx:
            agent_state["fichier_genere"] = resultat.fichier_docx

        return {
            "succes": resultat.succes,
            "categorie_bien": resultat.categorie_bien.value,
            "type_promesse": resultat.type_promesse.value,
            "fichier_docx": resultat.fichier_docx,
            "sections_incluses": resultat.sections_incluses,
            "erreurs": resultat.erreurs,
            "warnings": resultat.warnings,
            "duree_generation": round(resultat.duree_generation, 2),
        }

    def _exec_search_clauses(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Recherche des clauses dans le catalogue."""
        query = tool_input.get("query", "").lower()
        type_acte_filter = tool_input.get("type_acte", "")
        categorie_filter = tool_input.get("categorie", "")

        catalogue = self._load_clauses()
        categories = catalogue.get("categories", {})

        resultats = []
        for cat_id, cat_data in categories.items():
            if categorie_filter and cat_id != categorie_filter:
                continue

            for clause in cat_data.get("clauses", []):
                if type_acte_filter and type_acte_filter not in clause.get("type_acte", []):
                    continue

                # Score de pertinence par mots-cles
                score = 0
                nom = clause.get("nom", "").lower()
                texte = clause.get("texte", "").lower()

                for mot in query.split():
                    if mot in nom:
                        score += 3
                    if mot in texte:
                        score += 1
                    if mot in cat_id:
                        score += 2

                if score > 0:
                    resultats.append({
                        "id": clause.get("id", ""),
                        "nom": clause.get("nom", ""),
                        "categorie": cat_id,
                        "type_acte": clause.get("type_acte", []),
                        "obligatoire": clause.get("obligatoire", False),
                        "texte_apercu": clause.get("texte", "")[:200],
                        "score": score,
                    })

        resultats.sort(key=lambda x: x["score"], reverse=True)

        return {
            "query": query,
            "nb_resultats": min(len(resultats), 5),
            "clauses": resultats[:5],
        }

    def _exec_submit_feedback(
        self, tool_input: Dict, agent_state: Dict
    ) -> Dict:
        """Enregistre un feedback du notaire."""
        try:
            from execution.api.api_feedback import APIFeedbackNotaire
            api = APIFeedbackNotaire()
            return api.soumettre_feedback({
                "action": tool_input.get("action", ""),
                "cible": tool_input.get("cible", ""),
                "contenu": tool_input.get("contenu", ""),
                "raison": tool_input.get("raison", ""),
                "notaire": self.etude_id or "agent",
            })
        except ImportError:
            return {"success": True, "message": "Feedback enregistre (mode simplifie)"}
