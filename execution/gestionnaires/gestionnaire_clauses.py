#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionnaire de Clauses Intelligent pour Promesses de Vente
============================================================

Ce module permet de:
1. Sélectionner automatiquement les sections en fonction des données
2. Ajouter/retirer des clauses dynamiquement
3. Apprendre des retours des notaires
4. Générer des promesses simples ou complexes

Auteur: Notomai
Version: 1.0.0
Date: 28 janvier 2026
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy

# Encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class ActionType(Enum):
    """Types d'actions sur les clauses"""
    AJOUTER = "ajouter"
    MODIFIER = "modifier"
    SUPPRIMER = "supprimer"
    DEPLACER = "deplacer"
    ACTIVER = "activer"
    DESACTIVER = "desactiver"


class Priorite(Enum):
    """Niveaux de priorité des sections"""
    CRITIQUE = "critique"
    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"


@dataclass
class Section:
    """Représente une section du document"""
    id: str
    titre: str
    niveau: str
    obligatoire: bool = False
    condition: Optional[str] = None
    contenu: Optional[str] = None
    sous_sections: List[str] = field(default_factory=list)
    titre_alternatif: Optional[str] = None
    auto_pluriel: bool = False
    condition_pluriel: Optional[str] = None
    priorite: str = "moyenne"
    active: bool = True


@dataclass
class FeedbackNotaire:
    """Feedback d'un notaire pour amélioration continue"""
    action: str
    cible: str
    contenu: Optional[str] = None
    raison: str = ""
    source_notaire: str = ""
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    approuve: bool = False
    dossier_reference: Optional[str] = None


class GestionnaireClausesIntelligent:
    """
    Gestionnaire intelligent de clauses pour promesses de vente.

    Fonctionnalités:
    - Sélection automatique des sections basée sur les données
    - Ajout/suppression dynamique de clauses
    - Apprentissage continu via feedback notaire
    - Support des profils pré-configurés
    """

    def __init__(self, catalogue_path: Optional[str] = None):
        """
        Initialise le gestionnaire.

        Args:
            catalogue_path: Chemin vers le catalogue de clauses
        """
        self.base_dir = Path(__file__).parent.parent

        if catalogue_path:
            self.catalogue_path = Path(catalogue_path)
        else:
            self.catalogue_path = self.base_dir / "schemas" / "clauses_promesse_catalogue.json"

        self.feedback_path = self.base_dir / "data" / "feedback_notaires.json"
        self.historique_path = self.base_dir / "data" / "historique_modifications.json"

        # Charger le catalogue
        self.catalogue = self._charger_catalogue()
        self.sections_fixes = self._parser_sections(self.catalogue.get("sections_fixes", {}).get("sections", []))
        self.sections_variables = self._parser_sections(self.catalogue.get("sections_variables", {}).get("sections", []))
        self.regles = self.catalogue.get("regles_selection", {}).get("regles", [])
        self.profils = self.catalogue.get("profils_type", {}).get("profils", [])

        # État courant
        self.sections_actives: Dict[str, Section] = {}
        self.modifications: List[Dict] = []

    def _charger_catalogue(self) -> Dict:
        """Charge le catalogue de clauses depuis le fichier JSON."""
        try:
            with open(self.catalogue_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[WARN] Catalogue non trouvé: {self.catalogue_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"[ERROR] Erreur JSON dans le catalogue: {e}")
            return {}

    def _parser_sections(self, sections_data: List[Dict]) -> Dict[str, Section]:
        """Parse les sections depuis le JSON vers des objets Section."""
        sections = {}
        for s in sections_data:
            section = Section(
                id=s.get("id", ""),
                titre=s.get("titre", ""),
                niveau=s.get("niveau", "H1"),
                obligatoire=s.get("obligatoire", False),
                condition=s.get("condition"),
                contenu=s.get("contenu"),
                sous_sections=s.get("sous_sections", []),
                titre_alternatif=s.get("titre_alternatif"),
                auto_pluriel=s.get("auto_pluriel", False),
                condition_pluriel=s.get("condition_pluriel"),
                priorite=s.get("priorite", "moyenne")
            )
            sections[section.id] = section
        return sections

    def _evaluer_condition(self, condition: str, donnees: Dict) -> bool:
        """
        Évalue une condition Jinja2-like sur les données.

        Args:
            condition: Expression de condition
            donnees: Données du dossier

        Returns:
            bool: Résultat de l'évaluation
        """
        if not condition or condition == "true":
            return True

        try:
            # Convertir la syntaxe Jinja2 en Python
            condition_py = condition
            condition_py = condition_py.replace("|length", ").__len__()")
            condition_py = condition_py.replace(" > ", " > ")
            condition_py = condition_py.replace(" is defined", " is not None")
            condition_py = condition_py.replace(" == true", " == True")
            condition_py = condition_py.replace(" == false", " == False")

            # Aplatir les données pour accès simplifié
            flat_data = self._aplatir_donnees(donnees)

            # Évaluation sécurisée
            return self._eval_safe(condition_py, flat_data)
        except Exception as e:
            # En cas d'erreur, inclure par défaut
            return True

    def _aplatir_donnees(self, donnees: Dict, prefix: str = "") -> Dict:
        """Aplatit un dictionnaire imbriqué."""
        flat = {}
        for key, value in donnees.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._aplatir_donnees(value, new_key))
            else:
                flat[new_key] = value
            flat[key] = value  # Aussi sans préfixe
        return flat

    def _eval_safe(self, condition: str, data: Dict) -> bool:
        """Évaluation sécurisée d'une condition."""
        # Remplacements pour accès aux données
        for key, value in data.items():
            condition = condition.replace(key, repr(value))

        try:
            # Liste blanche d'opérateurs
            allowed = set("()><=!andornot ")
            clean_condition = ''.join(c for c in condition if c.isalnum() or c in allowed or c in "._'\"[]")
            return eval(clean_condition, {"__builtins__": {}}, {})
        except:
            return True

    def selectionner_sections(self, donnees: Dict, profil: Optional[str] = None) -> Dict[str, Section]:
        """
        Sélectionne automatiquement les sections en fonction des données.

        Args:
            donnees: Données du dossier
            profil: Nom du profil pré-configuré (optionnel)

        Returns:
            Dict des sections actives
        """
        self.sections_actives = {}

        # 1. Toujours inclure les sections fixes
        for section_id, section in self.sections_fixes.items():
            section_copy = copy.deepcopy(section)
            section_copy.active = True

            # Gérer le pluriel automatique
            if section.auto_pluriel and section.condition_pluriel:
                if self._evaluer_condition(section.condition_pluriel, donnees):
                    if hasattr(section, 'titre_pluriel'):
                        section_copy.titre = self.sections_fixes[section_id].__dict__.get('titre_pluriel', section.titre)

            self.sections_actives[section_id] = section_copy

        # 2. Évaluer les sections variables
        for section_id, section in self.sections_variables.items():
            if section.condition:
                if self._evaluer_condition(section.condition, donnees):
                    section_copy = copy.deepcopy(section)
                    section_copy.active = True
                    self.sections_actives[section_id] = section_copy
                elif section.titre_alternatif:
                    # Utiliser la version alternative
                    section_copy = copy.deepcopy(section)
                    section_copy.titre = section.titre_alternatif
                    section_copy.active = True
                    self.sections_actives[section_id] = section_copy

        # 3. Appliquer le profil si spécifié
        if profil:
            self._appliquer_profil(profil)

        # 4. Appliquer les règles de sélection
        self._appliquer_regles(donnees)

        return self.sections_actives

    def _appliquer_profil(self, profil_nom: str):
        """Applique un profil pré-configuré."""
        profil = next((p for p in self.profils if p.get("id") == profil_nom), None)
        if not profil:
            print(f"[WARN] Profil non trouvé: {profil_nom}")
            return

        # Désactiver les sections exclues
        for section_id in profil.get("sections_exclues", []):
            if section_id in self.sections_actives:
                self.sections_actives[section_id].active = False

    def _appliquer_regles(self, donnees: Dict):
        """Applique les règles de sélection mutuellement exclusives."""
        for regle in self.regles:
            condition = regle.get("condition", "")
            if self._evaluer_condition(condition, donnees):
                si_vrai = regle.get("si_vrai")
                si_faux = regle.get("si_faux")

                if si_vrai and si_vrai in self.sections_actives:
                    self.sections_actives[si_vrai].active = True
                if si_faux and si_faux in self.sections_actives:
                    self.sections_actives[si_faux].active = False
            else:
                si_faux = regle.get("si_faux")
                si_vrai = regle.get("si_vrai")

                if si_faux and si_faux in self.sections_actives:
                    self.sections_actives[si_faux].active = True
                if si_vrai and si_vrai in self.sections_actives:
                    # Ne pas désactiver automatiquement si c'est fixe
                    pass

    # =========================================================================
    # MÉTHODES POUR MODIFICATION DYNAMIQUE
    # =========================================================================

    def ajouter_section(self, section_id: str, titre: str, niveau: str = "H1",
                       contenu: Optional[str] = None, apres: Optional[str] = None) -> bool:
        """
        Ajoute une nouvelle section personnalisée.

        Args:
            section_id: Identifiant unique
            titre: Titre de la section
            niveau: Niveau hiérarchique (H1, H2, H3, H4)
            contenu: Contenu Jinja2 de la section
            apres: ID de la section après laquelle insérer

        Returns:
            bool: Succès de l'opération
        """
        if section_id in self.sections_actives:
            print(f"[WARN] Section {section_id} existe déjà")
            return False

        nouvelle_section = Section(
            id=section_id,
            titre=titre,
            niveau=niveau,
            contenu=contenu,
            obligatoire=False,
            active=True,
            priorite="moyenne"
        )

        self.sections_actives[section_id] = nouvelle_section

        self._enregistrer_modification({
            "action": ActionType.AJOUTER.value,
            "section_id": section_id,
            "titre": titre,
            "niveau": niveau,
            "contenu": contenu,
            "apres": apres,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def supprimer_section(self, section_id: str) -> bool:
        """
        Supprime (désactive) une section.

        Args:
            section_id: Identifiant de la section

        Returns:
            bool: Succès de l'opération
        """
        if section_id not in self.sections_actives:
            print(f"[WARN] Section {section_id} non trouvée")
            return False

        section = self.sections_actives[section_id]

        if section.obligatoire:
            print(f"[ERROR] Section {section_id} est obligatoire, impossible de la supprimer")
            return False

        section.active = False

        self._enregistrer_modification({
            "action": ActionType.SUPPRIMER.value,
            "section_id": section_id,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def modifier_section(self, section_id: str, nouveau_titre: Optional[str] = None,
                        nouveau_contenu: Optional[str] = None) -> bool:
        """
        Modifie une section existante.

        Args:
            section_id: Identifiant de la section
            nouveau_titre: Nouveau titre (optionnel)
            nouveau_contenu: Nouveau contenu (optionnel)

        Returns:
            bool: Succès de l'opération
        """
        if section_id not in self.sections_actives:
            print(f"[WARN] Section {section_id} non trouvée")
            return False

        section = self.sections_actives[section_id]
        ancien_titre = section.titre
        ancien_contenu = section.contenu

        if nouveau_titre:
            section.titre = nouveau_titre
        if nouveau_contenu:
            section.contenu = nouveau_contenu

        self._enregistrer_modification({
            "action": ActionType.MODIFIER.value,
            "section_id": section_id,
            "ancien_titre": ancien_titre,
            "nouveau_titre": nouveau_titre,
            "ancien_contenu": ancien_contenu,
            "nouveau_contenu": nouveau_contenu,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def activer_section(self, section_id: str) -> bool:
        """Active une section désactivée."""
        if section_id not in self.sections_actives:
            # Chercher dans les variables
            if section_id in self.sections_variables:
                self.sections_actives[section_id] = copy.deepcopy(self.sections_variables[section_id])
            else:
                print(f"[WARN] Section {section_id} non trouvée")
                return False

        self.sections_actives[section_id].active = True

        self._enregistrer_modification({
            "action": ActionType.ACTIVER.value,
            "section_id": section_id,
            "timestamp": datetime.now().isoformat()
        })

        return True

    def desactiver_section(self, section_id: str) -> bool:
        """Désactive une section sans la supprimer."""
        return self.supprimer_section(section_id)

    # =========================================================================
    # SYSTÈME D'APPRENTISSAGE CONTINU
    # =========================================================================

    def enregistrer_feedback(self, feedback: FeedbackNotaire) -> bool:
        """
        Enregistre le feedback d'un notaire pour amélioration continue.

        Args:
            feedback: Objet FeedbackNotaire

        Returns:
            bool: Succès de l'enregistrement
        """
        # S'assurer que le répertoire data existe
        data_dir = self.base_dir / "data"
        data_dir.mkdir(exist_ok=True)

        # Charger les feedbacks existants
        feedbacks = []
        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, 'r', encoding='utf-8') as f:
                    feedbacks = json.load(f)
            except:
                feedbacks = []

        # Ajouter le nouveau feedback
        feedbacks.append(asdict(feedback))

        # Sauvegarder
        with open(self.feedback_path, 'w', encoding='utf-8') as f:
            json.dump(feedbacks, f, ensure_ascii=False, indent=2)

        print(f"[OK] Feedback enregistré: {feedback.action} sur {feedback.cible}")

        # Appliquer le feedback si approuvé
        if feedback.approuve:
            self._appliquer_feedback(feedback)

        return True

    def _appliquer_feedback(self, feedback: FeedbackNotaire):
        """Applique un feedback approuvé au système."""
        if feedback.action == ActionType.AJOUTER.value:
            # Ajouter au catalogue
            nouvelle_section = {
                "id": feedback.cible,
                "titre": feedback.contenu or feedback.cible,
                "niveau": "H2",
                "condition": "true",
                "priorite": "moyenne",
                "source": f"Feedback notaire: {feedback.source_notaire}",
                "date_ajout": feedback.date
            }
            self.catalogue["sections_variables"]["sections"].append(nouvelle_section)
            self._sauvegarder_catalogue()

        elif feedback.action == ActionType.MODIFIER.value:
            # Modifier dans le catalogue
            for section in self.catalogue["sections_variables"]["sections"]:
                if section.get("id") == feedback.cible:
                    if feedback.contenu:
                        section["contenu_personnalise"] = feedback.contenu
                    break
            self._sauvegarder_catalogue()

        elif feedback.action == ActionType.SUPPRIMER.value:
            # Marquer comme obsolète
            for section in self.catalogue["sections_variables"]["sections"]:
                if section.get("id") == feedback.cible:
                    section["obsolete"] = True
                    section["raison_obsolete"] = feedback.raison
                    break
            self._sauvegarder_catalogue()

    def _sauvegarder_catalogue(self):
        """Sauvegarde le catalogue mis à jour."""
        with open(self.catalogue_path, 'w', encoding='utf-8') as f:
            json.dump(self.catalogue, f, ensure_ascii=False, indent=2)
        print(f"[OK] Catalogue mis à jour: {self.catalogue_path}")

    def _enregistrer_modification(self, modification: Dict):
        """Enregistre une modification dans l'historique."""
        self.modifications.append(modification)

        # Sauvegarder l'historique
        data_dir = self.base_dir / "data"
        data_dir.mkdir(exist_ok=True)

        historique = []
        if self.historique_path.exists():
            try:
                with open(self.historique_path, 'r', encoding='utf-8') as f:
                    historique = json.load(f)
            except:
                historique = []

        historique.append(modification)

        with open(self.historique_path, 'w', encoding='utf-8') as f:
            json.dump(historique, f, ensure_ascii=False, indent=2)

    # =========================================================================
    # GÉNÉRATION DE CONFIGURATION TEMPLATE
    # =========================================================================

    def generer_config_template(self) -> Dict[str, Any]:
        """
        Génère la configuration pour le template Jinja2.

        Returns:
            Dict avec la configuration des sections actives
        """
        config = {
            "sections_actives": {},
            "sections_desactivees": [],
            "ordre_sections": [],
            "metadata": {
                "generee_le": datetime.now().isoformat(),
                "nombre_sections": 0,
                "modifications_appliquees": len(self.modifications)
            }
        }

        for section_id, section in self.sections_actives.items():
            if section.active:
                config["sections_actives"][section_id] = {
                    "titre": section.titre,
                    "niveau": section.niveau,
                    "obligatoire": section.obligatoire,
                    "contenu_personnalise": section.contenu
                }
                config["ordre_sections"].append(section_id)
            else:
                config["sections_desactivees"].append(section_id)

        config["metadata"]["nombre_sections"] = len(config["sections_actives"])

        return config

    def obtenir_sections_actives(self) -> List[Dict]:
        """
        Retourne la liste des sections actives avec leurs détails.

        Returns:
            Liste de dictionnaires décrivant chaque section active
        """
        return [
            {
                "id": s.id,
                "titre": s.titre,
                "niveau": s.niveau,
                "obligatoire": s.obligatoire,
                "priorite": s.priorite
            }
            for s in self.sections_actives.values()
            if s.active
        ]

    def obtenir_sections_disponibles(self) -> List[Dict]:
        """
        Retourne toutes les sections disponibles (actives et inactives).

        Returns:
            Liste de toutes les sections avec leur statut
        """
        toutes = {}

        for section_id, section in self.sections_fixes.items():
            toutes[section_id] = {
                "id": section_id,
                "titre": section.titre,
                "niveau": section.niveau,
                "obligatoire": True,
                "type": "fixe",
                "active": section_id in self.sections_actives and self.sections_actives[section_id].active
            }

        for section_id, section in self.sections_variables.items():
            toutes[section_id] = {
                "id": section_id,
                "titre": section.titre,
                "niveau": section.niveau,
                "obligatoire": False,
                "type": "variable",
                "condition": section.condition,
                "active": section_id in self.sections_actives and self.sections_actives[section_id].active
            }

        return list(toutes.values())


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Gestionnaire de clauses intelligent pour promesses de vente"
    )

    subparsers = parser.add_subparsers(dest="commande", help="Commandes disponibles")

    # Commande: analyser
    analyser = subparsers.add_parser("analyser", help="Analyser les données et sélectionner les sections")
    analyser.add_argument("--donnees", "-d", required=True, help="Fichier JSON des données")
    analyser.add_argument("--profil", "-p", help="Profil pré-configuré")
    analyser.add_argument("--output", "-o", help="Fichier de sortie")

    # Commande: lister
    lister = subparsers.add_parser("lister", help="Lister les sections disponibles")
    lister.add_argument("--type", choices=["fixes", "variables", "toutes"], default="toutes")

    # Commande: profils
    profils = subparsers.add_parser("profils", help="Lister les profils disponibles")

    # Commande: feedback
    feedback_cmd = subparsers.add_parser("feedback", help="Enregistrer un feedback notaire")
    feedback_cmd.add_argument("--action", required=True, choices=["ajouter", "modifier", "supprimer"])
    feedback_cmd.add_argument("--cible", required=True, help="ID de la section")
    feedback_cmd.add_argument("--contenu", help="Nouveau contenu")
    feedback_cmd.add_argument("--raison", help="Raison du changement")
    feedback_cmd.add_argument("--notaire", default="CLI", help="Nom du notaire")
    feedback_cmd.add_argument("--approuve", action="store_true", help="Approuver automatiquement")

    args = parser.parse_args()

    gestionnaire = GestionnaireClausesIntelligent()

    if args.commande == "analyser":
        with open(args.donnees, 'r', encoding='utf-8') as f:
            donnees = json.load(f)

        sections = gestionnaire.selectionner_sections(donnees, args.profil)
        config = gestionnaire.generer_config_template()

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"[OK] Configuration générée: {args.output}")
        else:
            print(json.dumps(config, ensure_ascii=False, indent=2))

    elif args.commande == "lister":
        sections = gestionnaire.obtenir_sections_disponibles()

        if args.type == "fixes":
            sections = [s for s in sections if s["type"] == "fixe"]
        elif args.type == "variables":
            sections = [s for s in sections if s["type"] == "variable"]

        print(f"\n{'='*60}")
        print(f"SECTIONS DISPONIBLES ({len(sections)})")
        print(f"{'='*60}\n")

        for s in sections:
            status = "✓" if s.get("active", True) else "✗"
            oblig = "[OBLIGATOIRE]" if s.get("obligatoire") else ""
            print(f"  {status} {s['id']}: {s['titre']} ({s['niveau']}) {oblig}")

    elif args.commande == "profils":
        print(f"\n{'='*60}")
        print(f"PROFILS PRÉ-CONFIGURÉS ({len(gestionnaire.profils)})")
        print(f"{'='*60}\n")

        for p in gestionnaire.profils:
            print(f"  • {p['id']}: {p['nom']}")
            print(f"    {p['description']}")
            print()

    elif args.commande == "feedback":
        feedback = FeedbackNotaire(
            action=args.action,
            cible=args.cible,
            contenu=args.contenu,
            raison=args.raison or "",
            source_notaire=args.notaire,
            approuve=args.approuve
        )
        gestionnaire.enregistrer_feedback(feedback)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
