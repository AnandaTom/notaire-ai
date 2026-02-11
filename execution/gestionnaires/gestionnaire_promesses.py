# -*- coding: utf-8 -*-
"""
Gestionnaire de Promesses Intelligent
=====================================

Ce module gère la génération de tous types de promesses de vente:
- Standard (1 bien simple)
- Premium (diagnostics exhaustifs, localisation détaillée)
- Avec mobilier (liste des meubles vendus)
- Multi-biens (plusieurs propriétés)

Il intègre:
- Détection automatique du type de promesse
- Génération depuis un titre de propriété
- Validation des données
- Sélection des sections appropriées
- Intégration Supabase pour stockage/récupération

Usage:
    from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

    gestionnaire = GestionnairePromesses()

    # Depuis des données
    resultat = gestionnaire.generer(donnees)

    # Depuis un titre de propriété
    resultat = gestionnaire.generer_depuis_titre(titre_id, beneficiaires, prix)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import copy

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Chemins
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # execution/gestionnaires/ -> execution/ -> racine
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
TEMPLATES_DIR = PROJECT_ROOT / "templates"


class TypePromesse(Enum):
    """Types de promesse disponibles."""
    STANDARD = "standard"
    PREMIUM = "premium"
    AVEC_MOBILIER = "avec_mobilier"
    MULTI_BIENS = "multi_biens"


class CategorieBien(Enum):
    """Catégorie de bien immobilier — détermine la trame de base.

    Classification issue de l'analyse des 8 trames originales:
    - COPROPRIETE: Trames Principale, A, B, C (lots, tantièmes, EDD, syndic)
    - HORS_COPROPRIETE: Trames E, F (maison individuelle, local commercial)
    - TERRAIN_A_BATIR: Trames D, PUV GUNTZER (lotissement, parcelles, viabilisation)
    """
    COPROPRIETE = "copropriete"
    HORS_COPROPRIETE = "hors_copropriete"
    TERRAIN_A_BATIR = "terrain_a_batir"


@dataclass
class ResultatDetection:
    """Résultat de la détection du type de promesse (détection 3 niveaux v1.9.0)."""
    type_promesse: TypePromesse
    categorie_bien: CategorieBien = CategorieBien.COPROPRIETE
    sous_type: Optional[str] = None  # v1.9.0: lotissement, groupe_habitations, servitudes, viager, creation
    raison: str = ""
    confiance: float = 0.5
    sections_recommandees: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ResultatValidationPromesse:
    """Résultat de la validation des données de promesse.

    Note: Distinct de valider_acte.ResultatValidation qui utilise des objets structurés
    (niveau, code, message, chemin, suggestion). Ici les erreurs sont des strings simples.
    Utiliser to_rapport() pour convertir vers le format structuré.
    """
    valide: bool
    erreurs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    champs_manquants: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_rapport(self) -> Dict[str, Any]:
        """Convertit vers le format structuré compatible avec valider_acte.RapportValidation."""
        erreurs_structurees = []
        for err in self.erreurs:
            erreurs_structurees.append({
                "niveau": "ERREUR",
                "code": "VALIDATION_PROMESSE",
                "message": err,
                "chemin": "",
                "suggestion": ""
            })
        for warn in self.warnings:
            erreurs_structurees.append({
                "niveau": "AVERTISSEMENT",
                "code": "VALIDATION_PROMESSE",
                "message": warn,
                "chemin": "",
                "suggestion": ""
            })
        return {
            "valide": self.valide,
            "erreurs": erreurs_structurees,
            "champs_manquants": self.champs_manquants,
            "suggestions": self.suggestions
        }


# Alias backward compat
ResultatValidation = ResultatValidationPromesse


@dataclass
class ResultatGeneration:
    """Résultat de la génération d'une promesse."""
    succes: bool
    type_promesse: TypePromesse
    categorie_bien: CategorieBien = CategorieBien.COPROPRIETE
    fichier_md: Optional[str] = None
    fichier_docx: Optional[str] = None
    sections_incluses: List[str] = field(default_factory=list)
    erreurs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duree_generation: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class GestionnairePromesses:
    """
    Gestionnaire intelligent pour la génération de promesses de vente.

    Gère:
    - Détection automatique du type
    - Sélection des sections
    - Validation des données
    - Génération du document
    - Intégration Supabase
    """

    def __init__(self, supabase_client=None):
        """
        Initialise le gestionnaire.

        Args:
            supabase_client: Client Supabase optionnel pour l'intégration
        """
        self.supabase = supabase_client
        self.catalogue = self._charger_catalogue()
        self.templates_disponibles = self._scanner_templates()

    def _charger_catalogue(self) -> Dict:
        """Charge le catalogue unifié des promesses."""
        catalogue_path = SCHEMAS_DIR / "promesse_catalogue_unifie.json"

        if catalogue_path.exists():
            with open(catalogue_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"[WARNING] Catalogue non trouvé: {catalogue_path}")
            return {}

    def _scanner_templates(self) -> Dict[str, Path]:
        """Scanne les templates de promesse disponibles."""
        templates = {}

        # Template principal existant
        main_template = TEMPLATES_DIR / "promesse_vente_lots_copropriete.md"
        if main_template.exists():
            templates["standard"] = main_template

        # Templates spécialisés (dans sous-dossier promesse/)
        promesse_dir = TEMPLATES_DIR / "promesse"
        if promesse_dir.exists():
            for template_file in promesse_dir.glob("*.md"):
                type_name = template_file.stem.replace("promesse_", "")
                templates[type_name] = template_file

        return templates

    # =========================================================================
    # DÉTECTION 2 NIVEAUX: CATÉGORIE BIEN + TYPE TRANSACTION
    # =========================================================================

    def detecter_categorie_bien(self, donnees: Dict) -> CategorieBien:
        """
        Détecte la catégorie de bien immobilier (niveau 1 de détection).

        Priorités:
        1. Lotissement/terrain explicite → TERRAIN_A_BATIR
        2. Copropriété explicite ou marqueurs copro → COPROPRIETE
        3. Maison/local/hors-copro explicite → HORS_COPROPRIETE
        4. Défaut → COPROPRIETE (rétrocompatibilité)

        Args:
            donnees: Données de la promesse

        Returns:
            CategorieBien détectée
        """
        bien = donnees.get("bien", {})
        biens = donnees.get("biens", [])
        copro = donnees.get("copropriete", {})

        # Si multi-biens, examiner le premier bien
        if biens and not bien:
            bien = biens[0] if biens else {}

        # --- Priorité 1: Terrain à bâtir / Lotissement ---
        # Note: lotissement seul NE suffit PAS pour catégoriser en TERRAIN
        # (une maison dans un lotissement = HORS_COPRO, pas TERRAIN)
        # Vérifions d'abord les marqueurs terrain EXPLICITES

        type_bien = str(bien.get("type_bien", "")).lower()
        nature = str(bien.get("nature", "")).lower()
        usage = str(bien.get("usage_actuel", "")).lower()

        terrain_keywords = ("terrain", "parcelle", "lot a batir",
                            "lot à bâtir", "terrain a batir", "terrain à bâtir")
        if type_bien in terrain_keywords or nature in terrain_keywords or usage in terrain_keywords:
            return CategorieBien.TERRAIN_A_BATIR

        # Marqueurs lotissement dans les données
        if bien.get("permis_amenager") or bien.get("cahier_charges_lotissement"):
            return CategorieBien.TERRAIN_A_BATIR
        if bien.get("viabilisation") or bien.get("constructibilite"):
            return CategorieBien.TERRAIN_A_BATIR

        # --- Priorité 2: Copropriété ---
        if bien.get("copropriete") is True:
            return CategorieBien.COPROPRIETE
        if copro.get("syndic") or copro.get("nom_syndic"):
            return CategorieBien.COPROPRIETE
        if bien.get("lots") and isinstance(bien.get("lots"), list):
            return CategorieBien.COPROPRIETE
        if bien.get("tantiemes") or copro.get("immatriculation"):
            return CategorieBien.COPROPRIETE
        if bien.get("edd") or copro.get("reglement"):
            return CategorieBien.COPROPRIETE

        # --- Priorité 3: Hors copropriété ---
        if bien.get("copropriete") is False:
            return CategorieBien.HORS_COPROPRIETE

        hors_copro_types = ("maison", "villa", "pavillon", "local_commercial",
                            "local commercial", "hangar", "entrepot", "entrepôt",
                            "immeuble", "corps de ferme")
        if type_bien in hors_copro_types or nature in hors_copro_types:
            return CategorieBien.HORS_COPROPRIETE

        # Marqueurs maison individuelle
        if bien.get("surface_terrain") and not bien.get("lots"):
            return CategorieBien.HORS_COPROPRIETE

        # Marqueurs groupe habitations / lotissement hors copro (v1.9.0)
        if bien.get("groupe_habitations") or bien.get("lotissement"):
            return CategorieBien.HORS_COPROPRIETE

        # --- Défaut: copropriété (rétrocompatibilité) ---
        return CategorieBien.COPROPRIETE

    def detecter_sous_type(self, donnees: Dict, categorie: CategorieBien) -> Optional[str]:
        """
        Détecte les sous-types spécifiques au sein d'une catégorie de bien (v1.9.0).

        Sous-types supportés:
        - Toutes catégories: "viager" (priorité absolue, détection multi-marqueurs)
        - Hors copro: "lotissement", "groupe_habitations", "avec_servitudes"
        - Copro: "creation" (création de copropriété)
        - Terrain: "lotissement"

        Args:
            donnees: Données de la promesse
            categorie: Catégorie de bien détectée

        Returns:
            Sous-type détecté ou None
        """
        bien = donnees.get("bien", {})
        prix = donnees.get("prix", {})

        # Viager: priorité absolue, toutes catégories (maison, appartement, terrain)
        viager_marqueurs = 0
        if prix.get("type_vente") == "viager":
            viager_marqueurs += 2  # marqueur explicite = double poids
        if prix.get("rente_viagere"):
            viager_marqueurs += 1
        if prix.get("bouquet") and isinstance(prix.get("bouquet"), dict):
            viager_marqueurs += 1
        if bien.get("droit_usage_habitation", {}).get("reserve") is True:
            viager_marqueurs += 1
        modalites = str(prix.get("modalites_paiement", "")).lower()
        if "viager" in modalites or "rente" in modalites:
            viager_marqueurs += 1

        if viager_marqueurs >= 2:
            return "viager"

        # Sous-types hors copropriété
        if categorie == CategorieBien.HORS_COPROPRIETE:
            # Lotissement (priorité haute)
            if bien.get("lotissement"):
                return "lotissement"

            description = str(bien.get("description", "")).lower()
            type_bien = str(bien.get("type_bien", "")).lower()

            if "lotissement" in description or "lotissement" in type_bien:
                return "lotissement"
            if "ASL" in description or "association syndicale" in description:
                return "lotissement"

            # Groupe d'habitations
            if bien.get("groupe_habitations"):
                return "groupe_habitations"
            if "groupe" in description or "groupe d'habitations" in description:
                return "groupe_habitations"

            # Servitudes (priorité basse - souvent combiné avec autres)
            if bien.get("servitudes") and len(bien.get("servitudes", [])) > 0:
                return "avec_servitudes"

        # Sous-types copropriété
        elif categorie == CategorieBien.COPROPRIETE:
            copro = donnees.get("copropriete", {})

            # Création de copropriété
            if copro.get("en_creation") is True:
                return "creation"
            if bien.get("etat") == "creation" or copro.get("creation") is True:
                return "creation"
            # Inférence: pas de règlement NI syndic mais des lots = création probable
            if not copro.get("reglement") and not copro.get("syndic") and bien.get("lots"):
                return "creation"

        # Sous-types terrain
        elif categorie == CategorieBien.TERRAIN_A_BATIR:
            # Lotissement (déjà détecté au niveau catégorie normalement)
            if bien.get("lotissement"):
                return "lotissement"

        return None

    def detecter_type(self, donnees: Dict) -> ResultatDetection:
        """
        Détecte automatiquement le type de promesse approprié (détection 3 niveaux v1.9.0).

        Niveau 1: Catégorie de bien (copropriété, hors copro, terrain)
        Niveau 2: Type de transaction (standard, premium, mobilier, multi-biens)
        Niveau 3: Sous-type (lotissement, groupe habitations, servitudes, viager, création)

        Args:
            donnees: Données de la promesse

        Returns:
            ResultatDetection avec le type, la catégorie, le sous-type et les détails
        """
        # Niveau 1: Catégorie de bien
        categorie = self.detecter_categorie_bien(donnees)

        # Niveau 3: Sous-type (v1.9.0)
        sous_type = self.detecter_sous_type(donnees, categorie)

        # Niveau 2: Type de transaction (logique existante)
        regles = self.catalogue.get("detection_automatique", {}).get("regles", [])
        warnings = []

        # Évaluer chaque règle par priorité
        for regle in sorted(regles, key=lambda r: r.get("priorite", 99)):
            condition = regle.get("condition", "False")

            try:
                # Évaluer la condition avec les données
                if self._evaluer_condition(condition, donnees):
                    type_str = regle.get("type", "standard")
                    type_promesse = TypePromesse(type_str)

                    # Récupérer les sections recommandées
                    type_config = self.catalogue.get("types_promesse", {}).get(type_str, {})

                    # Calculer la confiance
                    confiance = self._calculer_confiance(donnees, type_promesse)

                    return ResultatDetection(
                        type_promesse=type_promesse,
                        categorie_bien=categorie,
                        sous_type=sous_type,
                        raison=regle.get("raison", "Détection automatique"),
                        confiance=confiance,
                        sections_recommandees=self._get_sections_pour_type(type_promesse, donnees),
                        warnings=warnings
                    )
            except Exception as e:
                warnings.append(f"Erreur évaluation règle: {e}")
                continue

        # Par défaut: standard
        return ResultatDetection(
            type_promesse=TypePromesse.STANDARD,
            categorie_bien=categorie,
            sous_type=sous_type,
            raison="Type par défaut",
            confiance=0.5,
            sections_recommandees=self._get_sections_pour_type(TypePromesse.STANDARD, donnees),
            warnings=warnings
        )

    def _evaluer_condition(self, condition: str, donnees: Dict) -> bool:
        """Évalue une condition Python sur les données."""
        try:
            # Contexte d'évaluation sécurisé — merge des données pour accès direct
            contexte = {
                "donnees": donnees,
                "len": len,
                "True": True,
                "False": False,
                "None": None
            }
            # Rendre les clés de premier niveau accessibles directement
            # (ex: "len(promettants) >= 1" fonctionne sans "donnees.get(...)")
            contexte.update(donnees)
            return eval(condition, {"__builtins__": {}}, contexte)
        except Exception:
            return False

    def _calculer_confiance(self, donnees: Dict, type_promesse: TypePromesse) -> float:
        """Calcule un score de confiance pour le type détecté."""
        confiance = 0.5

        # Bonus selon la complétude des données
        champs_remplis = self._compter_champs_remplis(donnees)
        confiance += min(0.3, champs_remplis / 100)

        # Bonus si les champs spécifiques au type sont présents
        if type_promesse == TypePromesse.AVEC_MOBILIER:
            if donnees.get("mobilier", {}).get("liste"):
                confiance += 0.2
        elif type_promesse == TypePromesse.MULTI_BIENS:
            biens = donnees.get("biens", [])
            if len(biens) > 1:
                confiance += 0.2
        elif type_promesse == TypePromesse.PREMIUM:
            if donnees.get("diagnostics", {}).get("exhaustifs"):
                confiance += 0.1
            if donnees.get("bien", {}).get("localisation_detaillee"):
                confiance += 0.1

        return min(1.0, confiance)

    def _compter_champs_remplis(self, donnees: Dict, prefix: str = "") -> int:
        """Compte récursivement les champs remplis."""
        count = 0
        for key, value in donnees.items():
            if isinstance(value, dict):
                count += self._compter_champs_remplis(value, f"{prefix}{key}.")
            elif isinstance(value, list):
                count += len(value)
            elif value is not None and value != "":
                count += 1
        return count

    def _get_sections_pour_type(self, type_promesse: TypePromesse, donnees: Dict) -> List[str]:
        """Retourne les sections à inclure pour un type donné."""
        sections = []

        # Sections fixes (toujours présentes)
        sections_fixes = self.catalogue.get("sections", {}).get("fixes", {}).get("liste", [])
        sections.extend([s.get("id") for s in sections_fixes])

        # Sections variables (selon conditions)
        sections_variables = self.catalogue.get("sections", {}).get("variables", {}).get("liste", [])

        for section in sections_variables:
            # Vérifier si la section s'applique à ce type de trame
            trames_section = section.get("trames", ["all"])
            type_str = type_promesse.value

            trame_mapping = {
                "standard": "ORIGINAL",
                "premium": "B",
                "avec_mobilier": "C",
                "multi_biens": "A"
            }

            trame_code = trame_mapping.get(type_str, "ORIGINAL")

            if "all" in trames_section or trame_code in trames_section:
                # Évaluer la condition
                condition = section.get("condition", "True")
                if self._evaluer_condition(condition, donnees):
                    sections.append(section.get("id"))

        return sections

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def valider(self, donnees: Dict, type_promesse: Optional[TypePromesse] = None) -> ResultatValidationPromesse:
        """
        Valide les données pour une promesse.

        Args:
            donnees: Données à valider
            type_promesse: Type de promesse (détecté si non fourni)

        Returns:
            ResultatValidation avec erreurs et warnings
        """
        erreurs = []
        warnings = []
        champs_manquants = []
        suggestions = []

        # Détecter le type si non fourni
        if type_promesse is None:
            detection = self.detecter_type(donnees)
            type_promesse = detection.type_promesse

        # Règles obligatoires
        regles_oblig = self.catalogue.get("validation", {}).get("regles_obligatoires", [])

        for regle in regles_oblig:
            champ = regle.get("champ")
            condition = regle.get("regle")
            message = regle.get("message")

            try:
                if not self._evaluer_condition(condition, donnees):
                    erreurs.append(message)
                    champs_manquants.append(champ)
            except Exception:
                erreurs.append(f"Erreur validation {champ}: {message}")
                champs_manquants.append(champ)

        # Règles conditionnelles
        regles_cond = self.catalogue.get("validation", {}).get("regles_conditionnelles", [])

        for regle in regles_cond:
            condition = regle.get("condition")

            try:
                if self._evaluer_condition(condition, donnees):
                    champs_requis = regle.get("champs_requis", [])
                    for champ in champs_requis:
                        if not self._champ_existe(donnees, champ):
                            warnings.append(f"{regle.get('message')}: {champ}")
                            champs_manquants.append(champ)
            except Exception:
                pass

        # Validation spécifique au type
        if type_promesse == TypePromesse.AVEC_MOBILIER:
            if not donnees.get("mobilier", {}).get("liste"):
                warnings.append("Liste de mobilier vide pour une promesse avec mobilier")
                suggestions.append("Ajouter la liste des meubles vendus")

        elif type_promesse == TypePromesse.MULTI_BIENS:
            biens = donnees.get("biens", [])
            if len(biens) < 2:
                warnings.append("Moins de 2 biens pour une promesse multi-biens")
            for i, bien in enumerate(biens):
                if not bien.get("adresse"):
                    champs_manquants.append(f"biens[{i}].adresse")
                if not bien.get("cadastre"):
                    champs_manquants.append(f"biens[{i}].cadastre")

        elif type_promesse == TypePromesse.PREMIUM:
            if not donnees.get("diagnostics", {}).get("exhaustifs"):
                suggestions.append("Activer les diagnostics exhaustifs pour promesse premium")

        # Validation viager (sous-type, indépendant du type de transaction)
        prix = donnees.get("prix", {})
        if prix.get("type_vente") == "viager":
            # Bouquet obligatoire
            bouquet = prix.get("bouquet", {})
            if not bouquet or not bouquet.get("montant"):
                erreurs.append("Bouquet obligatoire pour une vente en viager")
                champs_manquants.append("prix.bouquet.montant")

            # Rente viagère obligatoire
            rente = prix.get("rente_viagere", {})
            if not rente or not rente.get("montant_mensuel"):
                erreurs.append("Rente viagère obligatoire pour une vente en viager")
                champs_manquants.append("prix.rente_viagere.montant_mensuel")

            # Indexation fortement recommandée
            if rente and not rente.get("indexation", {}).get("applicable", False):
                warnings.append("Indexation de la rente non prévue — risque de dévaluation pour le crédirentier")
                suggestions.append("Ajouter une clause d'indexation INSEE pour protéger le crédirentier")

            # Certificat médical recommandé (article 1975 Code civil)
            promettants = donnees.get("promettants", [])
            if promettants:
                sante = promettants[0].get("sante", {})
                if not sante.get("certificat_medical", {}).get("existe", False):
                    warnings.append("Pas de certificat médical — risque de nullité si décès dans les 20 jours (art. 1975 C. civ.)")
                    suggestions.append("Produire un certificat médical pour sécuriser la vente viager")

            # Âge du crédirentier recommandé
            if promettants and not promettants[0].get("age"):
                warnings.append("Âge du crédirentier non renseigné — nécessaire pour calcul fiscal de la rente")
                suggestions.append("Renseigner l'âge du crédirentier (promettants[0].age)")

        return ResultatValidationPromesse(
            valide=len(erreurs) == 0,
            erreurs=erreurs,
            warnings=warnings,
            champs_manquants=champs_manquants,
            suggestions=suggestions
        )

    def _champ_existe(self, donnees: Dict, chemin: str) -> bool:
        """Vérifie si un champ existe dans les données (notation pointée)."""
        parties = chemin.replace("[*]", ".0").split(".")
        obj = donnees

        for partie in parties:
            if isinstance(obj, dict):
                obj = obj.get(partie)
            elif isinstance(obj, list):
                try:
                    obj = obj[int(partie)]
                except (ValueError, IndexError):
                    return False
            else:
                return False

            if obj is None:
                return False

        return True

    # =========================================================================
    # GÉNÉRATION DEPUIS TITRE DE PROPRIÉTÉ
    # =========================================================================

    def generer_depuis_titre(
        self,
        titre_data: Dict,
        beneficiaires: List[Dict],
        prix: Dict,
        financement: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> Tuple[Dict, ResultatGeneration]:
        """
        Génère une promesse à partir d'un titre de propriété extrait.

        Args:
            titre_data: Données extraites du titre (ou ID Supabase)
            beneficiaires: Liste des bénéficiaires
            prix: Informations sur le prix
            financement: Financement optionnel (prêt, etc.)
            options: Options supplémentaires

        Returns:
            Tuple (données complètes, résultat génération)
        """
        options = options or {}

        # Si titre_data est un ID, récupérer depuis Supabase
        if isinstance(titre_data, str):
            titre_data = self._charger_titre_supabase(titre_data)
            if titre_data is None:
                return None, ResultatGeneration(
                    succes=False,
                    type_promesse=TypePromesse.STANDARD,
                    erreurs=[f"Titre non trouvé: {titre_data}"]
                )

        # Mapper les données du titre vers le format promesse
        donnees = self._mapper_titre_vers_promesse(titre_data, beneficiaires, prix, financement)

        # Ajouter les options
        if options.get("mobilier"):
            donnees["mobilier"] = options["mobilier"]
        if options.get("conditions_suspensives"):
            donnees["conditions_suspensives"] = options["conditions_suspensives"]
        if options.get("indemnite"):
            donnees["indemnite"] = options["indemnite"]
        if options.get("delai_realisation"):
            donnees["delai_realisation"] = options["delai_realisation"]

        # Générer
        return donnees, self.generer(donnees, options.get("type_force"))

    def _mapper_titre_vers_promesse(
        self,
        titre: Dict,
        beneficiaires: List[Dict],
        prix: Dict,
        financement: Optional[Dict]
    ) -> Dict:
        """Mappe les données d'un titre vers le format promesse."""
        mappings = self.catalogue.get("mapping_titre_propriete", {}).get("mappings", [])

        donnees = {
            "promettants": [],
            "beneficiaires": beneficiaires,
            "bien": {},
            "prix": prix,
            "financement": financement or {"pret": False},
            "copropriete": {},
            "origine_propriete": {},
            "date_promesse": datetime.now().strftime("%Y-%m-%d")
        }

        # Appliquer les mappings
        for mapping in mappings:
            source = mapping.get("source")
            cible = mapping.get("cible")
            transformation = mapping.get("transformation", "copy")

            valeur_source = self._get_valeur_chemin(titre, source)

            if valeur_source is not None:
                if transformation == "copy":
                    self._set_valeur_chemin(donnees, cible, copy.deepcopy(valeur_source))
                elif transformation == "format_origine":
                    # Formater l'origine de propriété
                    origine_formatee = self._formater_origine(valeur_source)
                    self._set_valeur_chemin(donnees, cible, origine_formatee)

        return donnees

    def _get_valeur_chemin(self, obj: Dict, chemin: str) -> Any:
        """Récupère une valeur par chemin pointé."""
        parties = chemin.split(".")
        for partie in parties:
            if isinstance(obj, dict):
                obj = obj.get(partie)
            else:
                return None
        return obj

    def _set_valeur_chemin(self, obj: Dict, chemin: str, valeur: Any):
        """Définit une valeur par chemin pointé."""
        parties = chemin.split(".")
        for partie in parties[:-1]:
            if partie not in obj:
                obj[partie] = {}
            obj = obj[partie]
        obj[parties[-1]] = valeur

    def _formater_origine(self, origine: Dict) -> Dict:
        """Formate les données d'origine de propriété."""
        return {
            "type_acte": origine.get("type", "Vente"),
            "date": origine.get("date"),
            "notaire": origine.get("notaire"),
            "reference": origine.get("reference"),
            "details": origine.get("details", "")
        }

    def _charger_titre_supabase(self, titre_id: str) -> Optional[Dict]:
        """Charge un titre depuis Supabase."""
        if not self.supabase:
            print("[WARNING] Supabase non configuré")
            return None

        try:
            response = self.supabase.table("titres_propriete")\
                .select("*")\
                .eq("id", titre_id)\
                .single()\
                .execute()
            return response.data
        except Exception as e:
            print(f"[ERROR] Chargement titre: {e}")
            return None

    def rechercher_titre_par_adresse(self, adresse: str) -> List[Dict]:
        """Recherche des titres par adresse dans Supabase."""
        if not self.supabase:
            return []

        try:
            response = self.supabase.table("titres_propriete")\
                .select("id, reference, proprietaires, bien")\
                .ilike("bien->>adresse", f"%{adresse}%")\
                .execute()
            return response.data or []
        except Exception as e:
            print(f"[ERROR] Recherche titre: {e}")
            return []

    def rechercher_titre_par_proprietaire(self, nom: str) -> List[Dict]:
        """Recherche des titres par nom de propriétaire."""
        if not self.supabase:
            return []

        try:
            # Recherche dans le JSON des propriétaires
            response = self.supabase.table("titres_propriete")\
                .select("id, reference, proprietaires, bien")\
                .execute()

            resultats = []
            for titre in response.data or []:
                proprietaires = titre.get("proprietaires", [])
                for prop in proprietaires:
                    nom_complet = f"{prop.get('nom', '')} {prop.get('prenoms', '')}".lower()
                    if nom.lower() in nom_complet:
                        resultats.append(titre)
                        break

            return resultats
        except Exception as e:
            print(f"[ERROR] Recherche propriétaire: {e}")
            return []

    # =========================================================================
    # CONVERSION PROMESSE → VENTE
    # =========================================================================

    def promesse_vers_vente(
        self,
        promesse_data: Dict,
        modifications: Optional[Dict] = None,
        date_vente: Optional[str] = None
    ) -> Dict:
        """
        Convertit une promesse signée en données pour acte de vente.

        Mappings:
        - promettants → vendeurs
        - beneficiaires → acquereurs
        - Conserve: bien, prix, cadastre, copropriete
        - Ajoute: date_vente, modifications post-promesse

        Args:
            promesse_data: Données de la promesse signée
            modifications: Modifications à appliquer (prix, conditions, etc.)
            date_vente: Date de l'acte de vente (défaut: aujourd'hui)

        Returns:
            Dict des données formatées pour acte de vente
        """
        modifications = modifications or {}
        date_vente = date_vente or datetime.now().strftime("%Y-%m-%d")

        # Deep copy pour éviter mutations
        vente_data = {
            "acte": {
                "type": "vente",
                "date": self._parser_date_dict(date_vente),
                "notaire": promesse_data.get("acte", {}).get("notaire", {})
            },

            # Mapping promettants → vendeurs
            "vendeurs": copy.deepcopy(
                promesse_data.get("promettants", promesse_data.get("vendeurs", []))
            ),

            # Mapping beneficiaires → acquereurs
            "acquereurs": copy.deepcopy(
                promesse_data.get("beneficiaires", promesse_data.get("acquereurs", []))
            ),

            # Conserver les données du bien
            "bien": copy.deepcopy(promesse_data.get("bien", {})),

            # Prix (peut être modifié)
            "prix": copy.deepcopy(promesse_data.get("prix", {})),

            # Copropriété
            "copropriete": copy.deepcopy(promesse_data.get("copropriete", {})),

            # Origine de propriété
            "origine_propriete": copy.deepcopy(promesse_data.get("origine_propriete", {})),

            # Diagnostics
            "diagnostics": copy.deepcopy(promesse_data.get("diagnostics", {})),

            # Paiement/Financement
            "paiement": copy.deepcopy(
                promesse_data.get("paiement", promesse_data.get("financement", {}))
            ),

            # Référence à la promesse
            "conventions_anterieures": {
                "compromis": {
                    "date": promesse_data.get("date_promesse", promesse_data.get("acte", {}).get("date")),
                    "conditions_suspensives": promesse_data.get("conditions_suspensives", {}),
                    "conditions_realisees": True  # Par défaut
                }
            },

            # Metadata
            "_source_promesse": True,
            "_date_conversion": datetime.now().isoformat()
        }

        # Générer les quotités si manquantes
        vente_data = self._generer_quotites_si_manquantes(vente_data)

        # Appliquer les modifications
        if modifications:
            vente_data = self._appliquer_modifications(vente_data, modifications)

            # Tracker les modifications
            vente_data["_modifications_appliquees"] = modifications

        return vente_data

    def _parser_date_dict(self, date_str: str) -> Dict:
        """Parse une date string vers format dict."""
        try:
            if "-" in date_str:
                parts = date_str.split("-")
                return {
                    "annee": int(parts[0]),
                    "mois": int(parts[1]),
                    "jour": int(parts[2].split("T")[0])
                }
            elif "/" in date_str:
                parts = date_str.split("/")
                return {
                    "jour": int(parts[0]),
                    "mois": int(parts[1]),
                    "annee": int(parts[2])
                }
        except (ValueError, IndexError):
            pass

        now = datetime.now()
        return {"annee": now.year, "mois": now.month, "jour": now.day}

    def _generer_quotites_si_manquantes(self, donnees: Dict) -> Dict:
        """Génère les quotités vendues/acquises si manquantes."""
        vendeurs = donnees.get("vendeurs", [])
        acquereurs = donnees.get("acquereurs", [])

        # Quotités vendues
        if "quotites_vendues" not in donnees and vendeurs:
            nb_vendeurs = len(vendeurs)
            donnees["quotites_vendues"] = [
                {
                    "nom": f"{v.get('nom', '')} {v.get('prenoms', '')}".strip(),
                    "pourcentage": 100 / nb_vendeurs,
                    "fraction": f"1/{nb_vendeurs}" if nb_vendeurs > 1 else "1/1",
                    "type_droit": "pleine propriété"
                }
                for v in vendeurs
            ]

        # Quotités acquises
        if "quotites_acquises" not in donnees and acquereurs:
            nb_acquereurs = len(acquereurs)
            donnees["quotites_acquises"] = [
                {
                    "nom": f"{a.get('nom', '')} {a.get('prenoms', '')}".strip(),
                    "pourcentage": 100 / nb_acquereurs,
                    "fraction": f"1/{nb_acquereurs}" if nb_acquereurs > 1 else "1/1",
                    "type_droit": "pleine propriété"
                }
                for a in acquereurs
            ]

        return donnees

    def _appliquer_modifications(self, donnees: Dict, modifications: Dict) -> Dict:
        """Applique les modifications à des données de vente."""
        for chemin, valeur in modifications.items():
            self._set_valeur_chemin(donnees, chemin, valeur)
        return donnees

    def comparer_promesse_vente(self, promesse: Dict, vente: Dict) -> Dict:
        """
        Compare une promesse et un acte de vente pour détecter les différences.

        Args:
            promesse: Données de la promesse
            vente: Données de l'acte de vente

        Returns:
            Dict avec les différences détectées
        """
        differences = {
            "prix": self._comparer_prix(promesse, vente),
            "parties": self._comparer_parties(promesse, vente),
            "bien": self._comparer_bien(promesse, vente),
            "financement": self._comparer_financement(promesse, vente),
            "autres": []
        }

        # Calculer si avenant nécessaire
        differences["avenant_necessaire"] = (
            differences["prix"].get("modifie", False) or
            differences["parties"].get("modifie", False) or
            len(differences["autres"]) > 0
        )

        return differences

    def _comparer_prix(self, promesse: Dict, vente: Dict) -> Dict:
        """Compare les prix entre promesse et vente."""
        prix_promesse = promesse.get("prix", {}).get("montant", 0)
        prix_vente = vente.get("prix", {}).get("montant", 0)

        return {
            "promesse": prix_promesse,
            "vente": prix_vente,
            "difference": prix_vente - prix_promesse,
            "modifie": abs(prix_vente - prix_promesse) > 0.01
        }

    def _comparer_parties(self, promesse: Dict, vente: Dict) -> Dict:
        """Compare les parties entre promesse et vente."""
        promettants = promesse.get("promettants", promesse.get("vendeurs", []))
        vendeurs = vente.get("vendeurs", [])

        beneficiaires = promesse.get("beneficiaires", promesse.get("acquereurs", []))
        acquereurs = vente.get("acquereurs", [])

        return {
            "vendeurs_modifies": len(promettants) != len(vendeurs),
            "acquereurs_modifies": len(beneficiaires) != len(acquereurs),
            "modifie": len(promettants) != len(vendeurs) or len(beneficiaires) != len(acquereurs)
        }

    def _comparer_bien(self, promesse: Dict, vente: Dict) -> Dict:
        """Compare les biens entre promesse et vente."""
        bien_promesse = promesse.get("bien", {})
        bien_vente = vente.get("bien", {})

        return {
            "adresse_modifiee": bien_promesse.get("adresse") != bien_vente.get("adresse"),
            "lots_modifies": bien_promesse.get("lots") != bien_vente.get("lots"),
            "modifie": bien_promesse != bien_vente
        }

    def _comparer_financement(self, promesse: Dict, vente: Dict) -> Dict:
        """Compare le financement entre promesse et vente."""
        fin_promesse = promesse.get("financement", promesse.get("paiement", {}))
        fin_vente = vente.get("paiement", vente.get("financement", {}))

        prets_promesse = fin_promesse.get("prets", [])
        prets_vente = fin_vente.get("prets", [])

        total_promesse = sum(p.get("montant", 0) for p in prets_promesse)
        total_vente = sum(p.get("montant", 0) for p in prets_vente)

        return {
            "total_prets_promesse": total_promesse,
            "total_prets_vente": total_vente,
            "modifie": abs(total_promesse - total_vente) > 0.01
        }

    # =========================================================================
    # GÉNÉRATION
    # =========================================================================

    def generer(
        self,
        donnees: Dict,
        type_force: Optional[TypePromesse] = None,
        output_dir: Optional[Path] = None
    ) -> ResultatGeneration:
        """
        Génère une promesse de vente.

        Args:
            donnees: Données de la promesse
            type_force: Forcer un type spécifique
            output_dir: Dossier de sortie

        Returns:
            ResultatGeneration avec fichiers générés
        """
        import time
        start = time.time()

        errors = []
        warnings = []

        # 1. Détecter le type (3 niveaux: catégorie + type transaction + sous-type)
        sous_type = None
        if type_force:
            type_promesse = type_force
            categorie = self.detecter_categorie_bien(donnees)
            sous_type = self.detecter_sous_type(donnees, categorie)
            raison = "Type forcé par l'utilisateur"
        else:
            detection = self.detecter_type(donnees)
            type_promesse = detection.type_promesse
            categorie = detection.categorie_bien
            sous_type = detection.sous_type
            raison = detection.raison
            warnings.extend(detection.warnings)

        # 2. Valider les données
        validation = self.valider(donnees, type_promesse)
        if not validation.valide:
            return ResultatGeneration(
                succes=False,
                type_promesse=type_promesse,
                categorie_bien=categorie,
                erreurs=validation.erreurs,
                warnings=validation.warnings
            )
        warnings.extend(validation.warnings)

        # 2b. Enrichir le cadastre via API gouvernementale
        try:
            from execution.services.cadastre_service import CadastreService
            cadastre_svc = CadastreService()
            resultat_cadastre = cadastre_svc.enrichir_cadastre(donnees)
            donnees = resultat_cadastre["donnees"]
            rapport_cad = resultat_cadastre["rapport"]
            if rapport_cad["cadastre_enrichi"]:
                print(f"[INFO] Cadastre enrichi: {rapport_cad['parcelles_validees']} parcelle(s) "
                      f"validee(s), INSEE {rapport_cad['code_insee']}")
            for w in rapport_cad.get("warnings", []):
                warnings.append(f"Cadastre: {w}")
        except ImportError:
            pass
        except Exception as e:
            warnings.append(f"Enrichissement cadastre echoue: {e}")

        # 3. Sélectionner les sections
        sections = self._get_sections_pour_type(type_promesse, donnees)

        # 4. Sélectionner le template (catégorie + type + sous-type viager)
        template_path = self._selectionner_template(type_promesse, categorie, sous_type=sous_type)
        if not template_path:
            errors.append(f"Template non trouvé pour {categorie.value}/{type_promesse.value}")
            return ResultatGeneration(
                succes=False,
                type_promesse=type_promesse,
                categorie_bien=categorie,
                erreurs=errors,
                warnings=warnings
            )

        # 5. Préparer le dossier de sortie
        if output_dir is None:
            output_dir = PROJECT_ROOT / ".tmp" / "promesses_generees"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 6. Générer le markdown via assembler_acte.py
        try:
            from execution.core.assembler_acte import assembler_acte

            # Enrichir les données avec les sections actives et la catégorie
            donnees_enrichies = copy.deepcopy(donnees)
            donnees_enrichies["_sections_actives"] = sections
            donnees_enrichies["_type_promesse"] = type_promesse.value
            donnees_enrichies["_categorie_bien"] = categorie.value

            # Assembler
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"promesse_{type_promesse.value}_{timestamp}"

            fichier_md = output_dir / f"{output_name}.md"

            assembler_acte(
                template=template_path.name,
                donnees=donnees_enrichies,
                output_path=fichier_md
            )

        except ImportError:
            # Fallback: génération simple
            fichier_md = self._generer_markdown_simple(
                donnees, type_promesse, sections, output_dir
            )
        except Exception as e:
            errors.append(f"Erreur assemblage: {e}")
            return ResultatGeneration(
                succes=False,
                type_promesse=type_promesse,
                categorie_bien=categorie,
                erreurs=errors,
                warnings=warnings
            )

        # 7. Exporter en DOCX
        fichier_docx = None
        try:
            from execution.core.exporter_docx import exporter_docx

            fichier_docx = output_dir / f"{output_name}.docx"
            exporter_docx(fichier_md, fichier_docx)

        except ImportError:
            warnings.append("Exporteur DOCX non disponible")
        except Exception as e:
            warnings.append(f"Erreur export DOCX: {e}")

        # 8. Sauvegarder dans Supabase si configuré
        if self.supabase:
            try:
                self._sauvegarder_promesse_supabase(
                    donnees, type_promesse, fichier_md, fichier_docx
                )
            except Exception as e:
                warnings.append(f"Erreur sauvegarde Supabase: {e}")

        duree = time.time() - start

        return ResultatGeneration(
            succes=True,
            type_promesse=type_promesse,
            categorie_bien=categorie,
            fichier_md=str(fichier_md) if fichier_md else None,
            fichier_docx=str(fichier_docx) if fichier_docx else None,
            sections_incluses=sections,
            erreurs=errors,
            warnings=warnings,
            duree_generation=duree,
            metadata={
                "raison_type": raison,
                "categorie_bien": categorie.value,
                "template": str(template_path),
                "timestamp": datetime.now().isoformat()
            }
        )

    def _selectionner_template(
        self,
        type_promesse: TypePromesse,
        categorie_bien: CategorieBien = CategorieBien.COPROPRIETE,
        sous_type: Optional[str] = None
    ) -> Optional[Path]:
        """Sélectionne le template approprié selon catégorie + type + sous-type.

        Détection 3 niveaux:
        - Niveau 1 (catégorie): copropriété, hors copro, terrain → template de base
        - Niveau 2 (type): standard, premium, mobilier, multi-biens → variante
        - Niveau 3 (sous-type): viager → template séparé (prioritaire)
        """
        # Viager: template séparé (priorité absolue — +25% contenu unique)
        if sous_type == "viager":
            viager_template = TEMPLATES_DIR / "promesse_viager.md"
            if viager_template.exists():
                return viager_template

        # Templates par catégorie de bien
        category_templates = {
            CategorieBien.COPROPRIETE: TEMPLATES_DIR / "promesse_vente_lots_copropriete.md",
            CategorieBien.HORS_COPROPRIETE: TEMPLATES_DIR / "promesse_hors_copropriete.md",
            CategorieBien.TERRAIN_A_BATIR: TEMPLATES_DIR / "promesse_terrain_a_batir.md",
        }

        # Essayer le template spécifique à la catégorie
        template_categorie = category_templates.get(categorie_bien)
        if template_categorie and template_categorie.exists():
            return template_categorie

        # Fallback: template copropriété principal (88.9% conformité)
        main_template = TEMPLATES_DIR / "promesse_vente_lots_copropriete.md"
        if main_template.exists():
            return main_template

        # Fallback: chercher template spécialisé par type de transaction
        type_str = type_promesse.value
        if type_str in self.templates_disponibles:
            return self.templates_disponibles[type_str]

        if "standard" in self.templates_disponibles:
            return self.templates_disponibles["standard"]

        return None

    def _generer_markdown_simple(
        self,
        donnees: Dict,
        type_promesse: TypePromesse,
        sections: List[str],
        output_dir: Path
    ) -> Path:
        """Génère un markdown simple en fallback."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fichier = output_dir / f"promesse_{type_promesse.value}_{timestamp}.md"

        contenu = f"""# PROMESSE UNILATÉRALE DE VENTE

**Type**: {type_promesse.value}
**Date**: {datetime.now().strftime("%d/%m/%Y")}

---

## PARTIES

### Promettant(s)
{self._formater_parties(donnees.get("promettants", []))}

### Bénéficiaire(s)
{self._formater_parties(donnees.get("beneficiaires", []))}

---

## DÉSIGNATION DU BIEN

{self._formater_bien(donnees.get("bien", {}))}

---

## PRIX

Prix de vente: {donnees.get("prix", {}).get("montant", "À définir")} EUR

---

## SECTIONS INCLUSES

{chr(10).join(f"- {s}" for s in sections)}

---

*Document généré automatiquement par Notomai*
"""

        with open(fichier, 'w', encoding='utf-8') as f:
            f.write(contenu)

        return fichier

    def _formater_parties(self, parties: List[Dict]) -> str:
        """Formate une liste de parties."""
        if not parties:
            return "*Aucune partie définie*"

        lignes = []
        for p in parties:
            nom = f"{p.get('nom', '')} {p.get('prenoms', '')}".strip()
            if p.get("adresse"):
                nom += f"\n  Demeurant: {p.get('adresse')}"
            lignes.append(f"- {nom}")

        return "\n".join(lignes)

    def _formater_bien(self, bien: Dict) -> str:
        """Formate la désignation d'un bien."""
        if not bien:
            return "*Bien non défini*"

        lignes = []
        if bien.get("adresse"):
            lignes.append(f"**Adresse**: {bien.get('adresse')}")
        if bien.get("ville"):
            lignes.append(f"**Ville**: {bien.get('code_postal', '')} {bien.get('ville')}")
        if bien.get("cadastre"):
            cad = bien.get("cadastre", {})
            lignes.append(f"**Cadastre**: Section {cad.get('section')}, n°{cad.get('numero')}")

        return "\n".join(lignes) if lignes else "*Bien non défini*"

    def _sauvegarder_promesse_supabase(
        self,
        donnees: Dict,
        type_promesse: TypePromesse,
        fichier_md: Path,
        fichier_docx: Optional[Path]
    ):
        """Sauvegarde la promesse générée dans Supabase."""
        if not self.supabase:
            return

        self.supabase.table("promesses_generees").insert({
            "type_promesse": type_promesse.value,
            "promettants": donnees.get("promettants"),
            "beneficiaires": donnees.get("beneficiaires"),
            "bien": donnees.get("bien"),
            "prix": donnees.get("prix"),
            "fichier_md": str(fichier_md) if fichier_md else None,
            "fichier_docx": str(fichier_docx) if fichier_docx else None,
            "created_at": datetime.now().isoformat()
        }).execute()

    # =========================================================================
    # PROFILS PRÉDÉFINIS
    # =========================================================================

    def get_profils_disponibles(self) -> List[Dict]:
        """Retourne la liste des profils prédéfinis."""
        profils = self.catalogue.get("profils_predefinits", {})
        return [
            {
                "id": pid,
                "description": pdata.get("description"),
                "type_promesse": pdata.get("type_promesse"),
                "sections_count": len(pdata.get("sections_actives", []))
            }
            for pid, pdata in profils.items()
        ]

    def appliquer_profil(self, donnees: Dict, profil_id: str) -> Dict:
        """Applique un profil prédéfini aux données."""
        profil = self.catalogue.get("profils_predefinits", {}).get(profil_id)
        if not profil:
            raise ValueError(f"Profil non trouvé: {profil_id}")

        donnees_enrichies = copy.deepcopy(donnees)
        donnees_enrichies["_profil"] = profil_id
        donnees_enrichies["_type_promesse"] = profil.get("type_promesse")
        donnees_enrichies["_sections_actives"] = profil.get("sections_actives", [])
        donnees_enrichies["_sections_exclues"] = profil.get("sections_exclues", [])

        return donnees_enrichies


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Gestionnaire de Promesses Intelligent")

    subparsers = parser.add_subparsers(dest="commande", help="Commande à exécuter")

    # Commande: detecter
    p_detect = subparsers.add_parser("detecter", help="Détecter le type de promesse")
    p_detect.add_argument("--donnees", "-d", required=True, help="Fichier JSON des données")

    # Commande: valider
    p_valid = subparsers.add_parser("valider", help="Valider les données")
    p_valid.add_argument("--donnees", "-d", required=True, help="Fichier JSON des données")
    p_valid.add_argument("--type", "-t", help="Type de promesse (optionnel)")

    # Commande: generer
    p_gen = subparsers.add_parser("generer", help="Générer une promesse")
    p_gen.add_argument("--donnees", "-d", required=True, help="Fichier JSON des données")
    p_gen.add_argument("--type", "-t", help="Forcer un type de promesse")
    p_gen.add_argument("--output", "-o", help="Dossier de sortie")

    # Commande: profils
    p_profils = subparsers.add_parser("profils", help="Lister les profils disponibles")

    # Commande: depuis-titre
    p_titre = subparsers.add_parser("depuis-titre", help="Générer depuis un titre")
    p_titre.add_argument("--titre", "-t", required=True, help="Fichier JSON du titre extrait")
    p_titre.add_argument("--beneficiaires", "-b", required=True, help="Fichier JSON des bénéficiaires")
    p_titre.add_argument("--prix", "-p", required=True, help="Prix de vente (chiffre ou JSON)")
    p_titre.add_argument("--output", "-o", help="Dossier de sortie")

    args = parser.parse_args()

    gestionnaire = GestionnairePromesses()

    if args.commande == "detecter":
        with open(args.donnees, 'r', encoding='utf-8') as f:
            donnees = json.load(f)

        resultat = gestionnaire.detecter_type(donnees)
        print(f"\n[DÉTECTION]")
        print(f"  Catégorie bien: {resultat.categorie_bien.value}")
        print(f"  Type transaction: {resultat.type_promesse.value}")
        print(f"  Raison: {resultat.raison}")
        print(f"  Confiance: {resultat.confiance:.0%}")
        print(f"  Sections: {len(resultat.sections_recommandees)}")
        if resultat.warnings:
            print(f"  Warnings: {resultat.warnings}")

    elif args.commande == "valider":
        with open(args.donnees, 'r', encoding='utf-8') as f:
            donnees = json.load(f)

        type_promesse = TypePromesse(args.type) if args.type else None
        resultat = gestionnaire.valider(donnees, type_promesse)

        print(f"\n[VALIDATION]")
        print(f"  Valide: {'✓' if resultat.valide else '✗'}")
        if resultat.erreurs:
            print(f"  Erreurs: {resultat.erreurs}")
        if resultat.warnings:
            print(f"  Warnings: {resultat.warnings}")
        if resultat.suggestions:
            print(f"  Suggestions: {resultat.suggestions}")

    elif args.commande == "generer":
        with open(args.donnees, 'r', encoding='utf-8') as f:
            donnees = json.load(f)

        type_force = TypePromesse(args.type) if args.type else None
        output_dir = Path(args.output) if args.output else None

        resultat = gestionnaire.generer(donnees, type_force, output_dir)

        print(f"\n[GÉNÉRATION]")
        print(f"  Succès: {'✓' if resultat.succes else '✗'}")
        print(f"  Type: {resultat.type_promesse.value}")
        print(f"  Durée: {resultat.duree_generation:.2f}s")
        if resultat.fichier_md:
            print(f"  Markdown: {resultat.fichier_md}")
        if resultat.fichier_docx:
            print(f"  DOCX: {resultat.fichier_docx}")
        if resultat.erreurs:
            print(f"  Erreurs: {resultat.erreurs}")

    elif args.commande == "profils":
        profils = gestionnaire.get_profils_disponibles()
        print(f"\n[PROFILS DISPONIBLES]")
        for p in profils:
            print(f"  - {p['id']}: {p['description']} ({p['type_promesse']}, {p['sections_count']} sections)")

    elif args.commande == "depuis-titre":
        with open(args.titre, 'r', encoding='utf-8') as f:
            titre = json.load(f)
        with open(args.beneficiaires, 'r', encoding='utf-8') as f:
            beneficiaires = json.load(f)

        # Prix: soit un nombre, soit un JSON
        try:
            prix = {"montant": int(args.prix)}
        except ValueError:
            with open(args.prix, 'r', encoding='utf-8') as f:
                prix = json.load(f)

        output_dir = Path(args.output) if args.output else None

        donnees, resultat = gestionnaire.generer_depuis_titre(
            titre, beneficiaires, prix, output_dir=output_dir
        )

        print(f"\n[GÉNÉRATION DEPUIS TITRE]")
        print(f"  Succès: {'✓' if resultat.succes else '✗'}")
        print(f"  Type: {resultat.type_promesse.value}")
        if resultat.fichier_docx:
            print(f"  DOCX: {resultat.fichier_docx}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
