#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API de Feedback Notaire pour Apprentissage Continu
===================================================

Ce module fournit une API REST pour:
1. Recevoir les feedbacks des notaires depuis le frontend
2. Proposer des suggestions d'amélioration
3. Gérer l'approbation/rejet des modifications
4. Synchroniser avec le catalogue de clauses

Conçu pour être déployé sur Modal.com

Auteur: Notomai
Version: 1.0.0
Date: 28 janvier 2026
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class ActionType(Enum):
    AJOUTER = "ajouter"
    MODIFIER = "modifier"
    SUPPRIMER = "supprimer"
    ACTIVER = "activer"
    DESACTIVER = "desactiver"


class StatutFeedback(Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REJETE = "rejete"
    EN_REVISION = "en_revision"


@dataclass
class FeedbackNotaire:
    """Structure d'un feedback notaire"""
    id: str
    action: str
    cible: str
    contenu: Optional[str] = None
    raison: str = ""
    source_notaire: str = ""
    date_creation: str = ""
    dossier_reference: Optional[str] = None
    statut: str = StatutFeedback.EN_ATTENTE.value
    date_traitement: Optional[str] = None
    traite_par: Optional[str] = None
    commentaire_traitement: Optional[str] = None
    impact_estime: Optional[str] = None
    sections_affectees: List[str] = None

    def __post_init__(self):
        if not self.id:
            # Générer un ID unique
            content = f"{self.action}{self.cible}{self.source_notaire}{datetime.now().isoformat()}"
            self.id = hashlib.md5(content.encode()).hexdigest()[:12]
        if not self.date_creation:
            self.date_creation = datetime.now().isoformat()
        if self.sections_affectees is None:
            self.sections_affectees = []


@dataclass
class SuggestionAmelioration:
    """Suggestion automatique d'amélioration"""
    id: str
    type: str  # "nouvelle_clause", "modification", "question_manquante"
    titre: str
    description: str
    source: str  # "analyse_trame", "pattern_correction", "feedback_similaire"
    confiance: float  # 0.0 à 1.0
    contenu_suggere: Optional[str] = None
    date_creation: str = ""
    statut: str = "proposee"

    def __post_init__(self):
        if not self.date_creation:
            self.date_creation = datetime.now().isoformat()


class APIFeedbackNotaire:
    """
    API pour la gestion des feedbacks notaires et l'apprentissage continu.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialise l'API.

        Args:
            base_dir: Répertoire de base du projet
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent.parent

        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        self.feedback_path = self.data_dir / "feedback_notaires.json"
        self.suggestions_path = self.data_dir / "suggestions_amelioration.json"
        self.catalogue_path = self.base_dir / "schemas" / "clauses_promesse_catalogue.json"
        self.stats_path = self.data_dir / "stats_apprentissage.json"

    # =========================================================================
    # GESTION DES FEEDBACKS
    # =========================================================================

    def soumettre_feedback(self, feedback_data: Dict) -> Dict:
        """
        Soumet un nouveau feedback depuis le frontend.

        Args:
            feedback_data: Données du feedback

        Returns:
            Dict avec le résultat de la soumission
        """
        try:
            feedback = FeedbackNotaire(
                id="",  # Sera généré automatiquement
                action=feedback_data.get("action", ""),
                cible=feedback_data.get("cible", ""),
                contenu=feedback_data.get("contenu"),
                raison=feedback_data.get("raison", ""),
                source_notaire=feedback_data.get("notaire", "Anonyme"),
                dossier_reference=feedback_data.get("dossier_reference"),
                sections_affectees=feedback_data.get("sections_affectees", [])
            )

            # Estimer l'impact
            feedback.impact_estime = self._estimer_impact(feedback)

            # Sauvegarder
            feedbacks = self._charger_feedbacks()
            feedbacks.append(asdict(feedback))
            self._sauvegarder_feedbacks(feedbacks)

            # Mettre à jour les stats
            self._incrementer_stat("feedbacks_recus")

            return {
                "success": True,
                "feedback_id": feedback.id,
                "message": f"Feedback enregistré avec succès (ID: {feedback.id})",
                "impact_estime": feedback.impact_estime
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erreur lors de l'enregistrement du feedback"
            }

    def lister_feedbacks(self, statut: Optional[str] = None,
                         notaire: Optional[str] = None,
                         limite: int = 50) -> List[Dict]:
        """
        Liste les feedbacks avec filtres optionnels.

        Args:
            statut: Filtrer par statut
            notaire: Filtrer par notaire
            limite: Nombre maximum de résultats

        Returns:
            Liste des feedbacks
        """
        feedbacks = self._charger_feedbacks()

        # Filtrer
        if statut:
            feedbacks = [f for f in feedbacks if f.get("statut") == statut]
        if notaire:
            feedbacks = [f for f in feedbacks if f.get("source_notaire") == notaire]

        # Trier par date (plus récent en premier)
        feedbacks.sort(key=lambda x: x.get("date_creation", ""), reverse=True)

        return feedbacks[:limite]

    def obtenir_feedback(self, feedback_id: str) -> Optional[Dict]:
        """
        Obtient un feedback spécifique.

        Args:
            feedback_id: ID du feedback

        Returns:
            Dict du feedback ou None
        """
        feedbacks = self._charger_feedbacks()
        for f in feedbacks:
            if f.get("id") == feedback_id:
                return f
        return None

    def traiter_feedback(self, feedback_id: str, decision: str,
                         traite_par: str, commentaire: str = "") -> Dict:
        """
        Traite un feedback (approuver/rejeter).

        Args:
            feedback_id: ID du feedback
            decision: "approuve" ou "rejete"
            traite_par: Nom de l'admin
            commentaire: Commentaire optionnel

        Returns:
            Dict avec le résultat
        """
        feedbacks = self._charger_feedbacks()

        for i, f in enumerate(feedbacks):
            if f.get("id") == feedback_id:
                f["statut"] = decision
                f["date_traitement"] = datetime.now().isoformat()
                f["traite_par"] = traite_par
                f["commentaire_traitement"] = commentaire

                feedbacks[i] = f
                self._sauvegarder_feedbacks(feedbacks)

                # Si approuvé, appliquer au catalogue
                if decision == StatutFeedback.APPROUVE.value:
                    self._appliquer_au_catalogue(f)
                    self._incrementer_stat("feedbacks_appliques")

                return {
                    "success": True,
                    "message": f"Feedback {decision} par {traite_par}"
                }

        return {
            "success": False,
            "error": f"Feedback {feedback_id} non trouvé"
        }

    # =========================================================================
    # SUGGESTIONS AUTOMATIQUES
    # =========================================================================

    def generer_suggestions(self, donnees_dossier: Dict) -> List[Dict]:
        """
        Génère des suggestions d'amélioration basées sur l'analyse.

        Args:
            donnees_dossier: Données du dossier actuel

        Returns:
            Liste de suggestions
        """
        suggestions = []

        # 1. Analyser les patterns des feedbacks passés
        feedbacks_approuves = self.lister_feedbacks(statut=StatutFeedback.APPROUVE.value)
        patterns = self._extraire_patterns(feedbacks_approuves)

        # 2. Comparer avec le dossier actuel
        for pattern in patterns:
            if self._pattern_applicable(pattern, donnees_dossier):
                suggestion = SuggestionAmelioration(
                    id=hashlib.md5(pattern["description"].encode()).hexdigest()[:8],
                    type=pattern.get("type", "modification"),
                    titre=pattern.get("titre", "Suggestion automatique"),
                    description=pattern.get("description", ""),
                    source="feedback_similaire",
                    confiance=pattern.get("confiance", 0.7),
                    contenu_suggere=pattern.get("contenu")
                )
                suggestions.append(asdict(suggestion))

        # 3. Suggestions basées sur les données manquantes
        suggestions.extend(self._suggerer_sections_manquantes(donnees_dossier))

        return suggestions

    def proposer_clause_similaire(self, contexte: str) -> List[Dict]:
        """
        Propose des clauses similaires basées sur le contexte.

        Args:
            contexte: Description du contexte ou mots-clés

        Returns:
            Liste de clauses suggérées
        """
        # Charger le catalogue
        try:
            with open(self.catalogue_path, 'r', encoding='utf-8') as f:
                catalogue = json.load(f)
        except:
            return []

        suggestions = []
        contexte_lower = contexte.lower()

        # Chercher dans les sections variables
        for section in catalogue.get("sections_variables", {}).get("sections", []):
            titre = section.get("titre", "").lower()
            description = section.get("description", "").lower()

            # Score de pertinence simple
            score = 0
            for mot in contexte_lower.split():
                if mot in titre:
                    score += 2
                if mot in description:
                    score += 1

            if score > 0:
                suggestions.append({
                    "section_id": section.get("id"),
                    "titre": section.get("titre"),
                    "description": section.get("description"),
                    "condition": section.get("condition"),
                    "score_pertinence": score
                })

        # Trier par score
        suggestions.sort(key=lambda x: x["score_pertinence"], reverse=True)

        return suggestions[:5]  # Top 5

    # =========================================================================
    # STATISTIQUES ET MÉTRIQUES
    # =========================================================================

    def obtenir_statistiques(self) -> Dict:
        """
        Retourne les statistiques d'apprentissage.

        Returns:
            Dict avec les métriques
        """
        stats = self._charger_stats()
        feedbacks = self._charger_feedbacks()

        # Calculer les métriques
        total_feedbacks = len(feedbacks)
        en_attente = len([f for f in feedbacks if f.get("statut") == StatutFeedback.EN_ATTENTE.value])
        approuves = len([f for f in feedbacks if f.get("statut") == StatutFeedback.APPROUVE.value])
        rejetes = len([f for f in feedbacks if f.get("statut") == StatutFeedback.REJETE.value])

        # Notaires les plus actifs
        notaires = {}
        for f in feedbacks:
            notaire = f.get("source_notaire", "Anonyme")
            notaires[notaire] = notaires.get(notaire, 0) + 1

        top_notaires = sorted(notaires.items(), key=lambda x: x[1], reverse=True)[:5]

        # Types d'actions les plus fréquents
        actions = {}
        for f in feedbacks:
            action = f.get("action", "inconnu")
            actions[action] = actions.get(action, 0) + 1

        return {
            "total_feedbacks": total_feedbacks,
            "en_attente": en_attente,
            "approuves": approuves,
            "rejetes": rejetes,
            "taux_approbation": approuves / total_feedbacks * 100 if total_feedbacks > 0 else 0,
            "top_notaires": top_notaires,
            "actions_frequentes": actions,
            "derniere_mise_a_jour": stats.get("derniere_mise_a_jour"),
            "feedbacks_cette_semaine": stats.get("feedbacks_cette_semaine", 0)
        }

    # =========================================================================
    # MÉTHODES INTERNES
    # =========================================================================

    def _charger_feedbacks(self) -> List[Dict]:
        """Charge les feedbacks depuis le fichier."""
        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _sauvegarder_feedbacks(self, feedbacks: List[Dict]):
        """Sauvegarde les feedbacks."""
        with open(self.feedback_path, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

    def _charger_stats(self) -> Dict:
        """Charge les statistiques."""
        if self.stats_path.exists():
            try:
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _sauvegarder_stats(self, stats: Dict):
        """Sauvegarde les statistiques."""
        stats["derniere_mise_a_jour"] = datetime.now().isoformat()
        with open(self.stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

    def _incrementer_stat(self, cle: str):
        """Incrémente une statistique."""
        stats = self._charger_stats()
        stats[cle] = stats.get(cle, 0) + 1
        self._sauvegarder_stats(stats)

    def _estimer_impact(self, feedback: FeedbackNotaire) -> str:
        """Estime l'impact d'un feedback."""
        if feedback.action == ActionType.AJOUTER.value:
            return "moyen"  # Nouvelle section
        elif feedback.action == ActionType.MODIFIER.value:
            return "faible"  # Modification existante
        elif feedback.action == ActionType.SUPPRIMER.value:
            return "élevé"  # Suppression nécessite validation
        return "inconnu"

    def _appliquer_au_catalogue(self, feedback: Dict):
        """Applique un feedback approuvé au catalogue."""
        try:
            with open(self.catalogue_path, 'r', encoding='utf-8') as f:
                catalogue = json.load(f)

            action = feedback.get("action")
            cible = feedback.get("cible")
            contenu = feedback.get("contenu")

            if action == ActionType.AJOUTER.value:
                nouvelle_section = {
                    "id": cible,
                    "titre": contenu or cible,
                    "niveau": "H2",
                    "condition": "true",
                    "priorite": "moyenne",
                    "source": f"Feedback: {feedback.get('source_notaire')}",
                    "date_ajout": feedback.get("date_creation"),
                    "description": feedback.get("raison", "")
                }
                catalogue["sections_variables"]["sections"].append(nouvelle_section)

            elif action == ActionType.MODIFIER.value:
                for section in catalogue["sections_variables"]["sections"]:
                    if section.get("id") == cible:
                        if contenu:
                            section["contenu_personnalise"] = contenu
                        section["derniere_modification"] = datetime.now().isoformat()
                        break

            elif action == ActionType.SUPPRIMER.value:
                for section in catalogue["sections_variables"]["sections"]:
                    if section.get("id") == cible:
                        section["obsolete"] = True
                        section["raison_obsolete"] = feedback.get("raison")
                        section["date_obsolete"] = datetime.now().isoformat()
                        break

            # Sauvegarder
            with open(self.catalogue_path, 'w', encoding='utf-8') as f:
                json.dump(catalogue, f, ensure_ascii=False, indent=2)

            print(f"[OK] Catalogue mis à jour: {action} sur {cible}")

        except Exception as e:
            print(f"[ERROR] Erreur mise à jour catalogue: {e}")

    def _extraire_patterns(self, feedbacks: List[Dict]) -> List[Dict]:
        """Extrait les patterns des feedbacks approuvés."""
        patterns = []

        # Grouper par type d'action
        groupes = {}
        for f in feedbacks:
            action = f.get("action", "")
            if action not in groupes:
                groupes[action] = []
            groupes[action].append(f)

        # Créer des patterns
        for action, items in groupes.items():
            if len(items) >= 2:  # Au moins 2 occurrences
                patterns.append({
                    "type": action,
                    "titre": f"Pattern: {action}",
                    "description": f"Action '{action}' fréquemment demandée ({len(items)} fois)",
                    "confiance": min(len(items) / 10, 1.0),
                    "exemples": [i.get("cible") for i in items[:3]]
                })

        return patterns

    def _pattern_applicable(self, pattern: Dict, donnees: Dict) -> bool:
        """Vérifie si un pattern est applicable aux données."""
        # Logique simplifiée - à enrichir
        return pattern.get("confiance", 0) > 0.5

    def _suggerer_sections_manquantes(self, donnees: Dict) -> List[Dict]:
        """Suggère des sections basées sur les données manquantes."""
        suggestions = []

        # Vérifier les données courantes qui déclenchent des sections
        checks = [
            ("meubles", "meubles.inclus", "Vous n'avez pas précisé si des meubles sont inclus"),
            ("pret", "conditions_suspensives.pret", "Condition suspensive de prêt non définie"),
            ("indemnite", "indemnite_immobilisation", "Indemnité d'immobilisation non définie"),
        ]

        for check_id, key, description in checks:
            # Vérifier si la clé existe dans les données
            keys = key.split(".")
            value = donnees
            exists = True
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    exists = False
                    break

            if not exists:
                suggestions.append({
                    "id": f"suggest_{check_id}",
                    "type": "donnee_manquante",
                    "titre": f"Information manquante: {check_id}",
                    "description": description,
                    "source": "analyse_donnees",
                    "confiance": 0.9
                })

        return suggestions


# =============================================================================
# ENDPOINTS FASTAPI (pour Modal)
# =============================================================================

def creer_app_fastapi():
    """Crée l'application FastAPI pour déploiement sur Modal."""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        from typing import Optional, List
    except ImportError:
        print("[WARN] FastAPI non installé. Utilisez: pip install fastapi uvicorn")
        return None

    app = FastAPI(
        title="API Feedback Notaire",
        description="API pour l'apprentissage continu du système Notomai",
        version="1.0.0"
    )

    # CORS pour le frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIFeedbackNotaire()

    class FeedbackRequest(BaseModel):
        action: str
        cible: str
        contenu: Optional[str] = None
        raison: str = ""
        notaire: str = "Anonyme"
        dossier_reference: Optional[str] = None
        sections_affectees: List[str] = []

    class TraitementRequest(BaseModel):
        decision: str  # "approuve" ou "rejete"
        traite_par: str
        commentaire: str = ""

    @app.post("/api/feedback")
    async def soumettre_feedback(request: FeedbackRequest):
        result = api.soumettre_feedback(request.dict())
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    @app.get("/api/feedbacks")
    async def lister_feedbacks(statut: Optional[str] = None,
                               notaire: Optional[str] = None,
                               limite: int = 50):
        return api.lister_feedbacks(statut, notaire, limite)

    @app.get("/api/feedback/{feedback_id}")
    async def obtenir_feedback(feedback_id: str):
        result = api.obtenir_feedback(feedback_id)
        if not result:
            raise HTTPException(status_code=404, detail="Feedback non trouvé")
        return result

    @app.post("/api/feedback/{feedback_id}/traiter")
    async def traiter_feedback(feedback_id: str, request: TraitementRequest):
        result = api.traiter_feedback(
            feedback_id,
            request.decision,
            request.traite_par,
            request.commentaire
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    @app.get("/api/suggestions")
    async def obtenir_suggestions(contexte: str = ""):
        if contexte:
            return api.proposer_clause_similaire(contexte)
        return []

    @app.get("/api/stats")
    async def obtenir_statistiques():
        return api.obtenir_statistiques()

    return app


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="API de feedback notaire pour apprentissage continu"
    )

    subparsers = parser.add_subparsers(dest="commande", help="Commandes disponibles")

    # Commande: soumettre
    soumettre = subparsers.add_parser("soumettre", help="Soumettre un feedback")
    soumettre.add_argument("--action", required=True, choices=["ajouter", "modifier", "supprimer"])
    soumettre.add_argument("--cible", required=True)
    soumettre.add_argument("--contenu")
    soumettre.add_argument("--raison", default="")
    soumettre.add_argument("--notaire", default="CLI")

    # Commande: lister
    lister = subparsers.add_parser("lister", help="Lister les feedbacks")
    lister.add_argument("--statut", choices=["en_attente", "approuve", "rejete"])
    lister.add_argument("--notaire")
    lister.add_argument("--limite", type=int, default=50)

    # Commande: traiter
    traiter = subparsers.add_parser("traiter", help="Traiter un feedback")
    traiter.add_argument("--id", required=True)
    traiter.add_argument("--decision", required=True, choices=["approuve", "rejete"])
    traiter.add_argument("--par", required=True)
    traiter.add_argument("--commentaire", default="")

    # Commande: stats
    stats = subparsers.add_parser("stats", help="Afficher les statistiques")

    # Commande: serveur
    serveur = subparsers.add_parser("serveur", help="Lancer le serveur API")
    serveur.add_argument("--port", type=int, default=8000)
    serveur.add_argument("--host", default="0.0.0.0")

    args = parser.parse_args()

    api = APIFeedbackNotaire()

    if args.commande == "soumettre":
        result = api.soumettre_feedback({
            "action": args.action,
            "cible": args.cible,
            "contenu": args.contenu,
            "raison": args.raison,
            "notaire": args.notaire
        })
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.commande == "lister":
        feedbacks = api.lister_feedbacks(args.statut, args.notaire, args.limite)
        for f in feedbacks:
            statut = f.get("statut", "?")
            emoji = {"en_attente": "⏳", "approuve": "✅", "rejete": "❌"}.get(statut, "?")
            print(f"{emoji} [{f.get('id')}] {f.get('action')} sur {f.get('cible')} - {f.get('source_notaire')}")

    elif args.commande == "traiter":
        result = api.traiter_feedback(args.id, args.decision, args.par, args.commentaire)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.commande == "stats":
        stats = api.obtenir_statistiques()
        print(f"\n{'='*50}")
        print("STATISTIQUES D'APPRENTISSAGE")
        print(f"{'='*50}\n")
        print(f"Total feedbacks: {stats['total_feedbacks']}")
        print(f"  - En attente: {stats['en_attente']}")
        print(f"  - Approuvés: {stats['approuves']}")
        print(f"  - Rejetés: {stats['rejetes']}")
        print(f"Taux d'approbation: {stats['taux_approbation']:.1f}%")
        print(f"\nTop notaires contributeurs:")
        for notaire, count in stats.get("top_notaires", []):
            print(f"  - {notaire}: {count} feedbacks")

    elif args.commande == "serveur":
        app = creer_app_fastapi()
        if app:
            import uvicorn
            print(f"[INFO] Démarrage du serveur sur http://{args.host}:{args.port}")
            uvicorn.run(app, host=args.host, port=args.port)
        else:
            print("[ERROR] Impossible de créer l'application. Installez FastAPI.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
