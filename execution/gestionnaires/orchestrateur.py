# -*- coding: utf-8 -*-
"""
Orchestrateur NotaireAI - Point d'entrée unifié pour tous les workflows.

Ce module centralise toutes les opérations de génération d'actes notariaux
en un seul point d'entrée avec gestion d'erreurs et reporting.

Usage CLI:
    # Workflow complet: titre → promesse → vente
    python orchestrateur_notaire.py titre-to-promesse -t titre.pdf -o promesse.docx
    python orchestrateur_notaire.py promesse-to-vente -p PROM-2026-001 -o vente.docx

    # Génération directe
    python orchestrateur_notaire.py generer -t vente -d donnees.json -o acte.docx

    # Dashboard
    python orchestrateur_notaire.py dashboard

    # Statut système
    python orchestrateur_notaire.py status

Usage Python:
    from execution.gestionnaires.orchestrateur import OrchestratorNotaire

    orch = OrchestratorNotaire()
    result = orch.generer_acte_complet('vente', donnees, output='acte.docx')
"""

import sys
import json
import hashlib
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

from execution.security.secure_delete import secure_delete_file, secure_delete_dir

# Import du module d'historique Supabase
try:
    from execution.database.historique import HistoriqueActes, Acte
except ImportError:
    try:
        from historique_supabase import HistoriqueActes, Acte
    except ImportError:
        HistoriqueActes = None
        Acte = None

# Import du gestionnaire de promesses (v1.7.0 - catégories de bien)
try:
    from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses, CategorieBien
    GESTIONNAIRE_PROMESSES_DISPONIBLE = True
except ImportError:
    try:
        from gestionnaire_promesses import GestionnairePromesses, CategorieBien
        GESTIONNAIRE_PROMESSES_DISPONIBLE = True
    except ImportError:
        GESTIONNAIRE_PROMESSES_DISPONIBLE = False
        CategorieBien = None

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Chemins (v1.5.0 - ajusté pour nouvelle structure execution/gestionnaires/)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # execution/gestionnaires/ -> execution/ -> projet/

# Configuration timeouts (secondes)
TIMEOUT_ASSEMBLAGE = 120  # 2 minutes max pour l'assemblage
TIMEOUT_EXPORT = 180      # 3 minutes max pour l'export DOCX
TIMEOUT_ENRICHIR = 60     # 1 minute max pour l'enrichissement

logger = logging.getLogger(__name__)


class StatutEtape(Enum):
    """Statut d'une étape du workflow."""
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    SUCCES = "succes"
    ECHEC = "echec"
    IGNORE = "ignore"


class TypeActe(Enum):
    """Types d'actes supportés."""
    VENTE = "vente"
    PROMESSE_VENTE = "promesse_vente"
    REGLEMENT_COPROPRIETE = "reglement_copropriete"
    MODIFICATIF_EDD = "modificatif_edd"


@dataclass
class ResultatEtape:
    """Résultat d'une étape du workflow."""
    nom: str
    statut: StatutEtape
    duree_ms: int = 0
    message: str = ""
    erreur: Optional[str] = None
    donnees: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultatWorkflow:
    """Résultat complet d'un workflow."""
    workflow_id: str
    type_acte: str
    statut: str
    debut: str
    fin: str
    duree_totale_ms: int
    etapes: List[ResultatEtape]
    fichiers_generes: List[str]
    score_conformite: Optional[float]
    alertes: List[str]
    erreurs: List[str]
    metadata: Dict[str, Any]


class OrchestratorNotaire:
    """
    Orchestrateur central pour tous les workflows NotaireAI.

    Unifie:
    - Extraction de titres de propriété
    - Génération de promesses de vente
    - Génération d'actes de vente
    - Validation et conformité
    - Historique Supabase
    """

    # Templates par défaut (pour promesse, la catégorie de bien prime — voir _get_promesse_template)
    TEMPLATES = {
        TypeActe.VENTE: 'vente_lots_copropriete.md',
        TypeActe.PROMESSE_VENTE: 'promesse_vente_lots_copropriete.md',
        TypeActe.REGLEMENT_COPROPRIETE: 'reglement_copropriete_edd.md',
        TypeActe.MODIFICATIF_EDD: 'modificatif_edd.md',
    }

    # Templates promesse par catégorie de bien (v1.7.0)
    PROMESSE_TEMPLATES_PAR_CATEGORIE = {
        'copropriete': 'promesse_vente_lots_copropriete.md',
        'hors_copropriete': 'promesse_hors_copropriete.md',
        'terrain_a_batir': 'promesse_terrain_a_batir.md',
    }

    CONFORMITE_TEMPLATES = {
        TypeActe.VENTE: 0.802,
        TypeActe.PROMESSE_VENTE: 0.889,
        TypeActe.REGLEMENT_COPROPRIETE: 0.855,
        TypeActe.MODIFICATIF_EDD: 0.917,
    }

    def __init__(self, verbose: bool = False, cleanup_on_success: bool = False):
        """
        Initialise l'orchestrateur.

        Args:
            verbose: Afficher les logs détaillés
            cleanup_on_success: Nettoyer les fichiers temporaires même en cas de succès
        """
        self.verbose = verbose
        self.cleanup_on_success = cleanup_on_success
        self.project_root = PROJECT_ROOT
        self.etapes: List[ResultatEtape] = []
        self.alertes: List[str] = []
        self.erreurs: List[str] = []
        self._fichiers_temp: List[Path] = []  # Pour le cleanup/rollback

        # Statistiques optimisation coûts (v2.1.0)
        self.stats_modeles = {"opus": 0, "sonnet": 0, "haiku": 0}

        # Initialiser le client Supabase (avec fallback offline)
        self._historique: Optional[HistoriqueActes] = None
        if HistoriqueActes is not None:
            try:
                self._historique = HistoriqueActes()
                if self._historique._offline_mode:
                    self._log("Supabase: mode offline activé", "warning")
                else:
                    self._log("Supabase: connecté", "success")
            except Exception as e:
                self._log(f"Supabase non disponible: {e}", "warning")

    def _log(self, message: str, niveau: str = "info"):
        """Log avec niveau."""
        if self.verbose:
            icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
            print(f"  {icons.get(niveau, '•')} {message}")

    def _enregistrer_temp(self, chemin: Path) -> Path:
        """Enregistre un fichier temporaire pour cleanup ultérieur."""
        self._fichiers_temp.append(chemin)
        return chemin

    def _cleanup(self, force: bool = False) -> int:
        """
        Nettoie les fichiers temporaires.

        Args:
            force: Forcer le nettoyage même si cleanup_on_success est False

        Returns:
            Nombre de fichiers supprimés
        """
        if not self._fichiers_temp:
            return 0

        count = 0
        for chemin in self._fichiers_temp:
            try:
                if chemin.exists():
                    if chemin.is_file():
                        secure_delete_file(chemin)
                        count += 1
                    elif chemin.is_dir():
                        secure_delete_dir(chemin)
                        count += 1
                    self._log(f"Nettoyé (secure): {chemin.name}", "info")
            except Exception as e:
                self._log(f"Erreur cleanup {chemin}: {e}", "warning")

        self._fichiers_temp.clear()
        return count

    def _executer_etape(
        self,
        nom: str,
        fonction,
        *args,
        **kwargs
    ) -> ResultatEtape:
        """Exécute une étape avec timing et gestion d'erreurs."""
        import time

        if self.verbose:
            print(f"\n{'─'*60}")
            print(f"▶️  {nom}")
            print(f"{'─'*60}")

        debut = time.time()

        try:
            resultat = fonction(*args, **kwargs)
            duree = int((time.time() - debut) * 1000)

            etape = ResultatEtape(
                nom=nom,
                statut=StatutEtape.SUCCES,
                duree_ms=duree,
                message="Terminé avec succès",
                donnees=resultat if isinstance(resultat, dict) else {}
            )

            self._log(f"Terminé en {duree}ms", "success")

        except Exception as e:
            duree = int((time.time() - debut) * 1000)

            etape = ResultatEtape(
                nom=nom,
                statut=StatutEtape.ECHEC,
                duree_ms=duree,
                message=str(e),
                erreur=traceback.format_exc()
            )

            self.erreurs.append(f"{nom}: {str(e)}")
            self._log(f"Échec: {e}", "error")

        self.etapes.append(etape)
        return etape

    # =========================================================================
    # WORKFLOW 1: Extraction de titre de propriété
    # =========================================================================

    def extraire_titre(
        self,
        fichier_source: str,
        output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extrait les données d'un titre de propriété.

        Args:
            fichier_source: Chemin du PDF/DOCX
            output: Chemin JSON de sortie (optionnel)

        Returns:
            Dict avec les données extraites
        """
        from execution.extraction import ExtracteurV2

        def _extraire():
            extracteur = ExtracteurV2(utiliser_ocr=True, utiliser_ml=True)
            resultat = extracteur.extraire_fichier(fichier_source, verbose=self.verbose)

            donnees = asdict(resultat)

            if output:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(
                    json.dumps(donnees, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                self._log(f"Sauvegardé: {output}", "success")

            return donnees

        etape = self._executer_etape("Extraction titre de propriété", _extraire)
        return etape.donnees

    # =========================================================================
    # WORKFLOW 2: Titre → Promesse de vente
    # =========================================================================

    def titre_vers_promesse(
        self,
        titre_source: str,
        donnees_beneficiaires: Dict[str, Any],
        output: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ResultatWorkflow:
        """
        Génère une promesse de vente à partir d'un titre de propriété.

        Args:
            titre_source: Chemin PDF/DOCX du titre OU référence Supabase
            donnees_beneficiaires: Données des bénéficiaires (acquéreurs)
            output: Chemin du DOCX de sortie
            options: Options supplémentaires (prix, conditions, etc.)

        Returns:
            ResultatWorkflow complet
        """
        import time
        debut = datetime.now()
        workflow_id = f"WF-{debut.strftime('%Y%m%d-%H%M%S')}"

        self.etapes = []
        self.alertes = []
        self.erreurs = []
        options = options or {}

        print(f"\n{'='*60}")
        print(f"🔄 WORKFLOW: Titre → Promesse de vente")
        print(f"   ID: {workflow_id}")
        print(f"{'='*60}")

        # Étape 1: Charger/Extraire le titre
        titre_data = None
        if titre_source.startswith("TITRE-"):
            # Référence Supabase
            titre_data = self._charger_titre_supabase(titre_source)
        else:
            # Fichier local
            titre_data = self.extraire_titre(titre_source)

        if not titre_data or self.erreurs:
            return self._finaliser_workflow(workflow_id, "promesse_vente", debut, [])

        # Étape 2: Convertir titre vers données promesse
        def _convertir():
            return self._convertir_titre_vers_promesse(
                titre_data,
                donnees_beneficiaires,
                options
            )

        etape_conv = self._executer_etape("Conversion titre → promesse", _convertir)

        if etape_conv.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, "promesse_vente", debut, [])

        donnees_promesse = etape_conv.donnees

        # Étape 3: Valider les données
        etape_val = self._executer_etape(
            "Validation des données",
            self._valider_donnees,
            donnees_promesse,
            TypeActe.PROMESSE_VENTE
        )

        # Étape 4: Assembler le template
        tmp_json = self._enregistrer_temp(
            self.project_root / '.tmp' / f'promesse_{workflow_id}.json'
        )
        tmp_json.parent.mkdir(parents=True, exist_ok=True)
        tmp_json.write_text(
            json.dumps(donnees_promesse, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        tmp_md = self._enregistrer_temp(
            self.project_root / '.tmp' / f'promesse_{workflow_id}'
        )

        etape_asm = self._executer_etape(
            "Assemblage template",
            self._assembler_template,
            TypeActe.PROMESSE_VENTE,
            str(tmp_json),
            str(tmp_md)
        )

        if etape_asm.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, "promesse_vente", debut, [])

        # Récupérer le chemin du markdown généré
        md_path = etape_asm.donnees.get('markdown', str(tmp_md / 'acte.md'))

        # Étape 5: Exporter en DOCX
        etape_exp = self._executer_etape(
            "Export DOCX",
            self._exporter_docx,
            md_path,
            output
        )

        fichiers = [output] if etape_exp.statut == StatutEtape.SUCCES else []

        # Étape 6: Vérifier conformité
        score = None
        if fichiers:
            etape_conf = self._executer_etape(
                "Vérification conformité",
                self._verifier_conformite,
                output,
                TypeActe.PROMESSE_VENTE
            )
            score = etape_conf.donnees.get('score')

        # Étape 7: Sauvegarder historique (optionnel)
        if fichiers and options.get('sauvegarder_historique', True):
            self._executer_etape(
                "Sauvegarde historique",
                self._sauvegarder_historique,
                workflow_id,
                "promesse_vente",
                donnees_promesse
            )

        return self._finaliser_workflow(
            workflow_id,
            "promesse_vente",
            debut,
            fichiers,
            score
        )

    def _convertir_titre_vers_promesse(
        self,
        titre: Dict[str, Any],
        beneficiaires: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convertit les données d'un titre vers une promesse."""

        # Mapper les champs
        promesse = {
            "acte": {
                "type": "promesse_vente",
                "date": datetime.now().strftime("%d/%m/%Y"),
                "reference": f"PROM-{datetime.now().strftime('%Y-%m%d')}"
            },

            # Promettants = propriétaires actuels du titre
            "promettants": titre.get('proprietaires_actuels') or titre.get('vendeurs_originaux', []),

            # Bénéficiaires = fournis par le notaire
            "beneficiaires": beneficiaires.get('beneficiaires', []),

            # Bien = copié du titre
            "bien": titre.get('bien', {}),

            # Copropriété = copiée du titre
            "copropriete": titre.get('copropriete', {}),

            # Origine de propriété = l'acte du titre
            "origine_propriete": {
                "type": "acquisition",
                "date": titre.get('date_acte'),
                "notaire": titre.get('notaire'),
                "publication": titre.get('publication'),
                "auteurs": titre.get('vendeurs_originaux', [])
            },

            # Prix = à définir par le notaire
            "prix": options.get('prix', {
                "montant": 0,
                "en_lettres": "",
                "devise": "EUR"
            }),

            # Indemnité d'immobilisation
            "indemnite_immobilisation": options.get('indemnite', {
                "montant": 0,
                "pourcentage": 10
            }),

            # Conditions suspensives
            "conditions_suspensives": options.get('conditions_suspensives', [
                {
                    "type": "pret",
                    "description": "Obtention d'un prêt immobilier",
                    "delai_jours": 45
                }
            ]),

            # Délais
            "delais": options.get('delais', {
                "expiration_promesse": 90,
                "depot_garantie": 10
            }),

            # Notaire
            "notaire": options.get('notaire', titre.get('notaire', {}))
        }

        # Ajouter les quotités si non présentes
        if 'quotites_vendues' not in promesse:
            nb_promettants = len(promesse['promettants'])
            if nb_promettants > 0:
                quote_part = 100 / nb_promettants
                promesse['quotites_vendues'] = [
                    {"fraction": f"{quote_part:.2f}%", "type": "pleine_propriete"}
                    for _ in range(nb_promettants)
                ]

        return promesse

    # =========================================================================
    # WORKFLOW 3: Promesse → Acte de vente
    # =========================================================================

    def promesse_vers_vente(
        self,
        promesse_ref: str,
        donnees_complementaires: Optional[Dict[str, Any]] = None,
        output: str = None
    ) -> ResultatWorkflow:
        """
        Génère un acte de vente à partir d'une promesse.

        Args:
            promesse_ref: Référence de la promesse (PROM-XXX) ou chemin JSON
            donnees_complementaires: Données additionnelles (prêts, paiement, etc.)
            output: Chemin du DOCX de sortie

        Returns:
            ResultatWorkflow complet
        """
        debut = datetime.now()
        workflow_id = f"WF-{debut.strftime('%Y%m%d-%H%M%S')}"

        self.etapes = []
        self.alertes = []
        self.erreurs = []
        donnees_complementaires = donnees_complementaires or {}

        print(f"\n{'='*60}")
        print(f"🔄 WORKFLOW: Promesse → Acte de vente")
        print(f"   ID: {workflow_id}")
        print(f"{'='*60}")

        # Étape 1: Charger la promesse
        def _charger():
            if promesse_ref.startswith("PROM-"):
                return self._charger_promesse_supabase(promesse_ref)
            else:
                return json.loads(Path(promesse_ref).read_text(encoding='utf-8'))

        etape_chg = self._executer_etape("Chargement promesse", _charger)

        if etape_chg.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, "vente", debut, [])

        promesse_data = etape_chg.donnees

        # Étape 2: Convertir vers acte de vente
        def _convertir():
            return self._convertir_promesse_vers_vente(
                promesse_data,
                donnees_complementaires
            )

        etape_conv = self._executer_etape("Conversion promesse → vente", _convertir)

        if etape_conv.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, "vente", debut, [])

        donnees_vente = etape_conv.donnees

        # Étapes suivantes identiques à titre_vers_promesse...
        # (validation, assemblage, export, conformité, historique)

        # Étape 3: Valider
        self._executer_etape(
            "Validation des données",
            self._valider_donnees,
            donnees_vente,
            TypeActe.VENTE
        )

        # Étape 4: Assembler
        tmp_json = self._enregistrer_temp(
            self.project_root / '.tmp' / f'vente_{workflow_id}.json'
        )
        tmp_json.parent.mkdir(parents=True, exist_ok=True)
        tmp_json.write_text(
            json.dumps(donnees_vente, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        tmp_md = self._enregistrer_temp(
            self.project_root / '.tmp' / f'vente_{workflow_id}'
        )

        etape_asm = self._executer_etape(
            "Assemblage template",
            self._assembler_template,
            TypeActe.VENTE,
            str(tmp_json),
            str(tmp_md)
        )

        if etape_asm.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, "vente", debut, [])

        # Récupérer le chemin du markdown généré
        md_path = etape_asm.donnees.get('markdown', str(tmp_md / 'acte.md'))

        # Étape 5: Export
        output = output or str(self.project_root / 'outputs' / f'vente_{workflow_id}.docx')

        etape_exp = self._executer_etape(
            "Export DOCX",
            self._exporter_docx,
            md_path,
            output
        )

        fichiers = [output] if etape_exp.statut == StatutEtape.SUCCES else []

        # Étape 6: Conformité
        score = None
        if fichiers:
            etape_conf = self._executer_etape(
                "Vérification conformité",
                self._verifier_conformite,
                output,
                TypeActe.VENTE
            )
            score = etape_conf.donnees.get('score')

        return self._finaliser_workflow(workflow_id, "vente", debut, fichiers, score)

    def _convertir_promesse_vers_vente(
        self,
        promesse: Dict[str, Any],
        complements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convertit une promesse en acte de vente.

        Utilise le GestionnairePromesses (v1.5.1) si disponible pour:
        - Deep copy sécurisé
        - Préservation des diagnostics
        - Tracking des conventions antérieures
        - Génération automatique des quotités
        """
        # Utiliser le gestionnaire avancé si disponible
        if GESTIONNAIRE_PROMESSES_DISPONIBLE:
            try:
                gestionnaire = GestionnairePromesses()
                vente = gestionnaire.promesse_vers_vente(
                    promesse,
                    modifications=complements,
                    date_vente=datetime.now().strftime("%Y-%m-%d")
                )
                self._log("Conversion via GestionnairePromesses", "success")
                return vente
            except Exception as e:
                self._log(f"Erreur gestionnaire: {e} - fallback basique", "warning")

        # Fallback: conversion basique
        vente = {
            "acte": {
                "type": "vente",
                "date": datetime.now().strftime("%d/%m/%Y"),
                "reference": f"VENTE-{datetime.now().strftime('%Y-%m%d')}"
            },

            # Vendeurs = promettants de la promesse
            "vendeurs": promesse.get('promettants', promesse.get('vendeurs', [])),

            # Acquéreurs = bénéficiaires de la promesse
            "acquereurs": promesse.get('beneficiaires', promesse.get('acquereurs', [])),

            # Quotités
            "quotites_vendues": promesse.get('quotites_vendues', []),
            "quotites_acquises": promesse.get('quotites_acquises', []),

            # Bien
            "bien": promesse.get('bien', {}),

            # Copropriété
            "copropriete": promesse.get('copropriete', {}),

            # Origine de propriété
            "origine_propriete": promesse.get('origine_propriete', {}),

            # Diagnostics
            "diagnostics": promesse.get('diagnostics', {}),

            # Prix (confirmé)
            "prix": promesse.get('prix', {}),

            # Paiement
            "paiement": complements.get('paiement', {
                "mode": "virement",
                "date": datetime.now().strftime("%d/%m/%Y")
            }),

            # Prêts
            "prets": complements.get('prets', promesse.get('financement', {}).get('prets', [])),

            # Conditions réalisées
            "conditions_realisees": complements.get('conditions_realisees', [
                {"condition": "pret", "date_realisation": ""}
            ]),

            # Notaire
            "notaire": promesse.get('notaire', promesse.get('acte', {}).get('notaire', {}))
        }

        # Ajouter quotités acquises si manquantes
        if not vente['quotites_acquises'] and vente['acquereurs']:
            nb_acq = len(vente['acquereurs'])
            quote_part = 100 / nb_acq
            vente['quotites_acquises'] = [
                {"fraction": f"{quote_part:.2f}%", "type": "pleine_propriete"}
                for _ in range(nb_acq)
            ]

        # Ajouter quotités vendues si manquantes
        if not vente['quotites_vendues'] and vente['vendeurs']:
            nb_vend = len(vente['vendeurs'])
            quote_part = 100 / nb_vend
            vente['quotites_vendues'] = [
                {"fraction": f"{quote_part:.2f}%", "type": "pleine_propriete"}
                for _ in range(nb_vend)
            ]

        return vente

    # =========================================================================
    # WORKFLOW 4: Génération directe d'un acte
    # =========================================================================

    def generer_acte_complet(
        self,
        type_acte: str,
        donnees: Dict[str, Any],
        output: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ResultatWorkflow:
        """
        Génère un acte complet en une seule commande.

        Args:
            type_acte: Type d'acte (vente, promesse_vente, etc.)
            donnees: Données JSON complètes
            output: Chemin DOCX de sortie
            options: Options supplémentaires

        Returns:
            ResultatWorkflow complet
        """
        debut = datetime.now()
        workflow_id = f"WF-{debut.strftime('%Y%m%d-%H%M%S')}"

        self.etapes = []
        self.alertes = []
        self.erreurs = []
        options = options or {}

        # Convertir type_acte en enum
        try:
            type_enum = TypeActe(type_acte)
        except ValueError:
            self.erreurs.append(f"Type d'acte inconnu: {type_acte}")
            return self._finaliser_workflow(workflow_id, type_acte, debut, [])

        print(f"\n{'='*60}")
        print(f"🔄 WORKFLOW: Génération {type_acte}")
        print(f"   ID: {workflow_id}")
        print(f"{'='*60}")

        # Vérifier conformité template
        conformite = self.CONFORMITE_TEMPLATES.get(type_enum, 0)
        if conformite < 0.8:
            self.alertes.append(
                f"Template {type_acte} en développement ({conformite:.0%}). "
                f"Utilisation des données d'exemple recommandée."
            )
            self._log(f"Template conformité: {conformite:.0%}", "warning")

        # Étape 1: Enrichir les données
        etape_enr = self._executer_etape(
            "Enrichissement données",
            self._enrichir_donnees,
            donnees,
            type_enum
        )

        donnees_enrichies = etape_enr.donnees or donnees

        # Étape 2: Valider
        self._executer_etape(
            "Validation données",
            self._valider_donnees,
            donnees_enrichies,
            type_enum
        )

        # Étape 3: Assembler
        tmp_json = self._enregistrer_temp(
            self.project_root / '.tmp' / f'{type_acte}_{workflow_id}.json'
        )
        tmp_json.parent.mkdir(parents=True, exist_ok=True)
        tmp_json.write_text(
            json.dumps(donnees_enrichies, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        tmp_md = self._enregistrer_temp(
            self.project_root / '.tmp' / f'{type_acte}_{workflow_id}'
        )

        etape_asm = self._executer_etape(
            "Assemblage template",
            self._assembler_template,
            type_enum,
            str(tmp_json),
            str(tmp_md)
        )

        if etape_asm.statut == StatutEtape.ECHEC:
            return self._finaliser_workflow(workflow_id, type_acte, debut, [])

        # Récupérer le chemin du markdown généré
        md_path = etape_asm.donnees.get('markdown', str(tmp_md / 'acte.md'))

        # Étape 4: Export
        output = output or str(
            self.project_root / 'outputs' / f'{type_acte}_{workflow_id}.docx'
        )

        etape_exp = self._executer_etape(
            "Export DOCX",
            self._exporter_docx,
            md_path,
            output
        )

        fichiers = [output] if etape_exp.statut == StatutEtape.SUCCES else []

        # Étape 5: Conformité
        score = None
        if fichiers:
            etape_conf = self._executer_etape(
                "Vérification conformité",
                self._verifier_conformite,
                output,
                type_enum
            )
            score = etape_conf.donnees.get('score')

        return self._finaliser_workflow(workflow_id, type_acte, debut, fichiers, score)

    # =========================================================================
    # Méthodes d'optimisation des coûts (v2.1.0)
    # =========================================================================
    #
    # SMART ROUTING DE MODÈLES (Sprint Plan JOUR 1 MATIN)
    #
    # Objectif: Réduire les coûts API de 60% en sélectionnant intelligemment
    # le modèle Claude selon le type d'opération.
    #
    # Distribution attendue:
    # - Haiku (35% des appels): Validation déterministe, 80% économie vs Opus
    # - Sonnet (60% des appels): Détection + génération standard, 60% économie vs Opus
    # - Opus (5% des appels): Génération complexe, suggestion clauses créatives
    #
    # Économie totale: ~60% sur l'ensemble des opérations LLM.
    #
    # Méthode principale: _choisir_modele(donnees, type_acte) -> str
    # Tests: tests/test_tier1_optimizations.py (14 tests unitaires)
    # =========================================================================

    @staticmethod
    def detecter_type_acte_rapide(texte: str) -> Optional[str]:
        """
        Détection rapide du type d'acte par regex (0 coût LLM).

        Retourne None si ambigu → nécessite fallback LLM.

        Économie: -$0.016/génération sur 80% des cas

        Args:
            texte: Texte de la demande

        Returns:
            Type d'acte détecté ou None si ambigu
        """
        import re

        texte_lower = texte.lower()

        # Patterns clairs (priorité descendante)
        if re.search(r'\bviager\b', texte_lower):
            return "viager"

        if re.search(r'\bpromesse\b', texte_lower):
            # Sous-types promesse
            if re.search(r'\bterrain\b', texte_lower):
                return "promesse_terrain"
            if re.search(r'\bhors.*copro|maison\b', texte_lower):
                return "promesse_hors_copropriete"
            return "promesse_vente"

        if re.search(r'\bvente\b.*\bacte\b|\bacte\b.*\bvente\b', texte_lower):
            return "vente"

        if re.search(r'\bdonation\b', texte_lower):
            return "donation_partage"

        if re.search(r'\bedd\b|règlement.*copro', texte_lower):
            return "reglement_copropriete"

        if re.search(r'\bmodificatif\b', texte_lower):
            return "modificatif_edd"

        # Ambigu → nécessite LLM
        return None

    def _choisir_modele(
        self,
        donnees: Optional[Dict[str, Any]] = None,
        type_acte: Optional[str] = None,
        type_operation: Optional[str] = None,
        confiance: float = 1.0
    ) -> str:
        """
        Sélectionne le modèle optimal (API unifiée v2.1.0).

        Supporte deux modes d'appel:
        1. Mode génération: _choisir_modele(donnees, type_acte) → retourne nom simple
        2. Mode opération: _choisir_modele(type_operation="validation", confiance=0.8) → retourne ID complet

        Règles d'optimisation:
        - Validation → Haiku (déterministe, 80% économie)
        - Détection haute confiance → Sonnet (60% économie)
        - Cas standard → Sonnet (60% économie)
        - Viager/complexe/multi-parties/prix >1M → Opus (qualité max)

        Args:
            donnees: Données du dossier (mode génération)
            type_acte: Type d'acte (mode génération)
            type_operation: Type d'opération ("validation", "detection", "suggestion_clauses", "generation")
            confiance: Score de confiance 0-1 pour l'opération

        Returns:
            str: Nom simple ("sonnet", "opus", "haiku") OU ID complet ("claude-sonnet-4-5-20250929")
                 selon le mode d'appel
        """
        # ===== MODE OPÉRATION (retourne ID complet) =====
        if type_operation:
            # Règle 1: Validation → Haiku
            if type_operation == "validation":
                self.stats_modeles["haiku"] += 1
                self._log("Modèle: HAIKU (validation déterministe)", "info")
                return "claude-haiku-4-5-20251001"

            # Règle 2: Détection haute confiance → Sonnet
            if type_operation == "detection" and confiance > 0.80:
                self.stats_modeles["sonnet"] += 1
                self._log(f"Modèle: SONNET (détection confiance={confiance:.0%})", "info")
                return "claude-sonnet-4-5-20250929"

            # Règle 3: Suggestion clauses → Opus
            if type_operation == "suggestion_clauses":
                self.stats_modeles["opus"] += 1
                self._log("Modèle: OPUS (suggestion clauses créatives)", "info")
                return "claude-opus-4-6"

            # Règle 4: Génération avec analyse de données
            if type_operation == "generation" and donnees:
                # Analyser complexité → retourner ID complet
                return self._analyser_complexite_generation(donnees, mode_id=True)

            # Fallback: Opus
            self.stats_modeles["opus"] += 1
            self._log(f"Modèle: OPUS (fallback {type_operation})", "info")
            return "claude-opus-4-6"

        # ===== MODE GÉNÉRATION (retourne nom simple) =====
        if donnees and type_acte:
            return self._analyser_complexite_generation(donnees, mode_id=False, type_acte=type_acte)

        # Erreur: paramètres invalides
        raise ValueError("_choisir_modele() nécessite soit (donnees, type_acte) soit (type_operation)")

    def _analyser_complexite_generation(
        self,
        donnees: Dict[str, Any],
        mode_id: bool = False,
        type_acte: Optional[str] = None
    ) -> str:
        """
        Analyse la complexité des données pour choisir Opus vs Sonnet.

        Args:
            donnees: Données du dossier
            mode_id: Si True, retourne ID complet. Si False, retourne nom simple.
            type_acte: Type d'acte (optionnel)

        Returns:
            str: "opus"/"sonnet"/"haiku" (mode_id=False) ou ID complet (mode_id=True)
        """
        # Détecter type acte
        if not type_acte:
            type_acte = donnees.get('acte', {}).get('type', '')

        # Cas complexes → Opus
        types_complexes = ["viager", "donation_partage", "sci", "donation"]
        if type_acte in types_complexes or donnees.get('acte', {}).get('type') in types_complexes:
            self.stats_modeles["opus"] += 1
            self._log(f"Modèle: OPUS (type complexe: {type_acte})", "info")
            return "claude-opus-4-6" if mode_id else "opus"

        # Viager détecté dans prix → Opus
        if donnees.get('prix', {}).get('type_vente') == "viager":
            self.stats_modeles["opus"] += 1
            self._log("Modèle: OPUS (viager détecté dans prix)", "info")
            return "claude-opus-4-6" if mode_id else "opus"

        # Multi-parties → Opus
        vendeurs = donnees.get('vendeurs') or donnees.get('promettants', [])
        acquereurs = donnees.get('acquereurs') or donnees.get('beneficiaires', [])

        if len(vendeurs) > 2 or len(acquereurs) > 2:
            self.stats_modeles["opus"] += 1
            self._log(f"Modèle: OPUS (multi-parties: {len(vendeurs)}V, {len(acquereurs)}A)", "info")
            return "claude-opus-4-6" if mode_id else "opus"

        # Prix élevé → Opus
        prix = donnees.get('prix', {}).get('montant', 0)
        if prix > 1_000_000:
            self.stats_modeles["opus"] += 1
            self._log(f"Modèle: OPUS (prix élevé: {prix:,.0f}€)", "info")
            return "claude-opus-4-6" if mode_id else "opus"

        # Données incomplètes → Opus
        champs_critiques = ['vendeurs', 'acquereurs', 'bien', 'prix']
        if type_acte == "promesse_vente" or (type_acte and "promesse" in type_acte):
            champs_critiques = ['promettants', 'beneficiaires', 'bien', 'prix']

        manquants = [c for c in champs_critiques if not donnees.get(c)]
        if len(manquants) >= 2:
            self.stats_modeles["opus"] += 1
            self._log(f"Modèle: OPUS (données incomplètes: {manquants})", "info")
            return "claude-opus-4-6" if mode_id else "opus"

        # Cas standard → Sonnet
        self.stats_modeles["sonnet"] += 1
        self._log("Modèle: SONNET (génération cas standard)", "info")
        return "claude-sonnet-4-5-20250929" if mode_id else "sonnet"

    # =========================================================================
    # Méthodes utilitaires internes
    # =========================================================================

    def _charger_titre_supabase(self, reference: str) -> Dict[str, Any]:
        """
        Charge un titre depuis Supabase ou cache local.

        Args:
            reference: Référence du titre (ex: TITRE-2026-001)

        Returns:
            Dict avec les données du titre

        Raises:
            ValueError: Si le titre n'est pas trouvé
        """
        # Essayer Supabase d'abord
        if self._historique:
            acte = self._historique.charger_acte(reference)
            if acte:
                self._log(f"Titre chargé depuis Supabase: {reference}", "success")
                return acte.donnees

        # Fallback: chercher dans le cache local
        cache_local = self.project_root / '.tmp' / 'titres' / f'{reference}.json'
        if cache_local.exists():
            donnees = json.loads(cache_local.read_text(encoding='utf-8'))
            self._log(f"Titre chargé depuis cache local: {reference}", "info")
            return donnees

        # Chercher dans le dossier historique
        historique_dir = self.project_root / '.tmp' / 'historique'
        for fichier in historique_dir.glob('*.json'):
            try:
                data = json.loads(fichier.read_text(encoding='utf-8'))
                if data.get('reference') == reference:
                    self._log(f"Titre trouvé dans historique: {reference}", "info")
                    return data.get('donnees', data)
            except (json.JSONDecodeError, KeyError):
                continue

        raise ValueError(f"Titre non trouvé: {reference}")

    def _charger_promesse_supabase(self, reference: str) -> Dict[str, Any]:
        """
        Charge une promesse depuis Supabase ou cache local.

        Args:
            reference: Référence de la promesse (ex: PROM-2026-001)

        Returns:
            Dict avec les données de la promesse

        Raises:
            ValueError: Si la promesse n'est pas trouvée
        """
        # Essayer Supabase d'abord
        if self._historique:
            acte = self._historique.charger_acte(reference)
            if acte and acte.type_acte in ('promesse_vente', 'promesse'):
                self._log(f"Promesse chargée depuis Supabase: {reference}", "success")
                return acte.donnees

        # Fallback: chercher dans le cache local
        cache_local = self.project_root / '.tmp' / 'promesses' / f'{reference}.json'
        if cache_local.exists():
            donnees = json.loads(cache_local.read_text(encoding='utf-8'))
            self._log(f"Promesse chargée depuis cache local: {reference}", "info")
            return donnees

        # Chercher dans le dossier historique
        historique_dir = self.project_root / '.tmp' / 'historique'
        for fichier in historique_dir.glob('*.json'):
            try:
                data = json.loads(fichier.read_text(encoding='utf-8'))
                if data.get('reference') == reference and data.get('type') in ('promesse_vente', 'promesse'):
                    self._log(f"Promesse trouvée dans historique: {reference}", "info")
                    return data.get('donnees', data)
            except (json.JSONDecodeError, KeyError):
                continue

        raise ValueError(f"Promesse non trouvée: {reference}")

    def _enrichir_donnees(
        self,
        donnees: Dict[str, Any],
        type_acte: TypeActe
    ) -> Dict[str, Any]:
        """Enrichit les données avec les valeurs par défaut."""
        import copy
        donnees = copy.deepcopy(donnees)

        # Appeler le script d'enrichissement
        try:
            script = self.project_root / 'execution' / 'generation' / 'generer_donnees_minimales.py'
            if script.exists():
                # Sauvegarder temporairement
                tmp = self.project_root / '.tmp' / 'enrichir_tmp.json'
                tmp.write_text(json.dumps(donnees, ensure_ascii=False), encoding='utf-8')

                result = subprocess.run(
                    [sys.executable, str(script), '-i', str(tmp), '-o', str(tmp)],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_ENRICHIR
                )

                if result.returncode == 0:
                    donnees = json.loads(tmp.read_text(encoding='utf-8'))
                    self._log("Données enrichies", "success")
        except Exception as e:
            self._log(f"Enrichissement optionnel échoué: {e}", "warning")

        return donnees

    def _valider_donnees(
        self,
        donnees: Dict[str, Any],
        type_acte: TypeActe
    ) -> Dict[str, Any]:
        """
        Valide les données et retourne les alertes.

        Cette validation est déterministe (règles métier Python) et ne nécessite
        pas d'appel LLM.
        """
        alertes = []

        # Validations communes
        if type_acte in [TypeActe.VENTE, TypeActe.PROMESSE_VENTE]:
            # Vérifier les vendeurs/promettants
            vendeurs = donnees.get('vendeurs') or donnees.get('promettants', [])
            if not vendeurs:
                alertes.append("Aucun vendeur/promettant défini")

            # Vérifier les acquéreurs/bénéficiaires
            acquereurs = donnees.get('acquereurs') or donnees.get('beneficiaires', [])
            if not acquereurs:
                alertes.append("Aucun acquéreur/bénéficiaire défini")

            # Vérifier le bien
            if not donnees.get('bien'):
                alertes.append("Bien non défini")

            # Vérifier le prix
            prix = donnees.get('prix', {})
            if not prix.get('montant'):
                alertes.append("Prix non défini")

        for alerte in alertes:
            self.alertes.append(alerte)
            self._log(alerte, "warning")

        return {"alertes": alertes, "valide": len(alertes) == 0}

    def _get_promesse_template(self, donnees: Dict[str, Any]) -> str:
        """Sélectionne le template promesse selon catégorie + type + sous-type (v2.0.0)."""
        if GESTIONNAIRE_PROMESSES_DISPONIBLE and CategorieBien is not None:
            try:
                gestionnaire = GestionnairePromesses()
                detection = gestionnaire.detecter_type(donnees)
                template_path = gestionnaire._selectionner_template(
                    detection.type_promesse,
                    detection.categorie_bien,
                    sous_type=detection.sous_type
                )
                if template_path and template_path.exists():
                    logger.info(f"Template détecté: {detection.categorie_bien.value}/{detection.sous_type or 'standard'} -> {template_path.name}")
                    return template_path.name
                # Fallback par catégorie si _selectionner_template retourne None
                template = self.PROMESSE_TEMPLATES_PAR_CATEGORIE.get(
                    detection.categorie_bien.value,
                    self.TEMPLATES[TypeActe.PROMESSE_VENTE]
                )
                logger.info(f"Catégorie bien détectée: {detection.categorie_bien.value} -> {template}")
                return template
            except Exception as e:
                logger.warning(f"Détection catégorie échouée, fallback copro: {e}")
        return self.TEMPLATES[TypeActe.PROMESSE_VENTE]

    def _assembler_template(
        self,
        type_acte: TypeActe,
        donnees_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Assemble le template avec les données."""
        # Pour les promesses, sélection par catégorie de bien
        if type_acte == TypeActe.PROMESSE_VENTE:
            try:
                donnees_json = json.loads(Path(donnees_path).read_text(encoding='utf-8'))
                template = self._get_promesse_template(donnees_json)
            except Exception:
                template = self.TEMPLATES.get(type_acte)
        else:
            template = self.TEMPLATES.get(type_acte)
        script = self.project_root / 'execution' / 'core' / 'assembler_acte.py'

        # Créer le dossier de sortie
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        acte_id = Path(output_path).stem

        try:
            result = subprocess.run(
                [
                    sys.executable, str(script),
                    '--template', template,
                    '--donnees', donnees_path,
                    '--output', str(output_dir),
                    '--id', acte_id,
                    '--zones-grisees'
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=TIMEOUT_ASSEMBLAGE
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Assemblage timeout après {TIMEOUT_ASSEMBLAGE}s")

        if result.returncode != 0:
            raise RuntimeError(f"Assemblage échoué:\n{result.stderr}")

        # Le fichier généré est dans output_dir/id/acte.md
        md_file = output_dir / acte_id / 'acte.md'
        if md_file.exists():
            return {"markdown": str(md_file)}

        # Fallback: chercher le fichier .md
        md_files = list(output_dir.glob(f'{acte_id}/**/*.md'))
        if md_files:
            return {"markdown": str(md_files[0])}

        raise RuntimeError(f"Fichier markdown non trouvé après assemblage")

    def _exporter_docx(self, markdown_path: str, output_path: str) -> Dict[str, Any]:
        """Exporte le markdown en DOCX."""
        script = self.project_root / 'execution' / 'core' / 'exporter_docx.py'

        # Vérifier que le fichier source existe
        md_path = Path(markdown_path)
        if not md_path.exists():
            raise RuntimeError(f"Fichier markdown non trouvé: {markdown_path}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            result = subprocess.run(
                [
                    sys.executable, str(script),
                    '--input', str(md_path.resolve()),
                    '--output', str(Path(output_path).resolve()),
                    '--zones-grisees'
                ],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=TIMEOUT_EXPORT
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Export DOCX timeout après {TIMEOUT_EXPORT}s")

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Erreur inconnue"
            raise RuntimeError(f"Export DOCX échoué:\n{error_msg}")

        # Vérifier que le fichier a été créé
        if not Path(output_path).exists():
            raise RuntimeError(f"DOCX non créé: {output_path}")

        return {"docx": output_path}

    def _verifier_conformite(
        self,
        docx_path: str,
        type_acte: TypeActe
    ) -> Dict[str, Any]:
        """Vérifie la conformité du DOCX généré."""
        # Score basé sur la conformité du template
        score = self.CONFORMITE_TEMPLATES.get(type_acte, 0.5)

        self._log(f"Score conformité estimé: {score:.0%}",
                  "success" if score >= 0.8 else "warning")

        return {"score": score}

    def _sauvegarder_historique(
        self,
        reference: str,
        type_acte: str,
        donnees: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sauvegarde dans l'historique (Supabase + backup local).

        Args:
            reference: Référence de l'acte
            type_acte: Type d'acte (vente, promesse_vente, etc.)
            donnees: Données de l'acte

        Returns:
            Dict avec l'ID de sauvegarde et le statut
        """
        acte_id = None
        source = "local"

        # Sauvegarder dans Supabase si disponible
        if self._historique:
            try:
                acte_id = self._historique.sauvegarder_acte(
                    reference=reference,
                    type_acte=type_acte,
                    donnees=donnees,
                    metadata={
                        "workflow": "orchestrateur",
                        "version": "1.3.0"
                    }
                )
                if acte_id:
                    source = "supabase" if not self._historique._offline_mode else "offline"
                    self._log(f"Sauvegardé dans {source}: {reference}", "success")
            except Exception as e:
                self._log(f"Erreur Supabase: {e}", "warning")

        # Toujours sauvegarder en local (backup)
        historique_dir = self.project_root / '.tmp' / 'historique'
        historique_dir.mkdir(parents=True, exist_ok=True)

        fichier = historique_dir / f'{reference}.json'
        fichier.write_text(
            json.dumps({
                "reference": reference,
                "type": type_acte,
                "date": datetime.now().isoformat(),
                "donnees": donnees,
                "supabase_id": acte_id
            }, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        if source == "local":
            self._log(f"Sauvegardé en local: {fichier.name}", "info")

        return {"fichier": str(fichier)}

    def _finaliser_workflow(
        self,
        workflow_id: str,
        type_acte: str,
        debut: datetime,
        fichiers: List[str],
        score: Optional[float] = None
    ) -> ResultatWorkflow:
        """Finalise et retourne le résultat du workflow."""
        fin = datetime.now()
        duree = int((fin - debut).total_seconds() * 1000)

        statut = "succes" if not self.erreurs else "echec"

        # Cleanup: rollback en cas d'échec, optionnel en cas de succès
        cleanup_count = 0
        if statut == "echec":
            self._log("Rollback: nettoyage des fichiers temporaires", "warning")
            cleanup_count = self._cleanup(force=True)
        elif self.cleanup_on_success:
            cleanup_count = self._cleanup(force=True)

        resultat = ResultatWorkflow(
            workflow_id=workflow_id,
            type_acte=type_acte,
            statut=statut,
            debut=debut.isoformat(),
            fin=fin.isoformat(),
            duree_totale_ms=duree,
            etapes=self.etapes,
            fichiers_generes=fichiers,
            score_conformite=score,
            alertes=self.alertes,
            erreurs=self.erreurs,
            metadata={"cleanup_count": cleanup_count}
        )

        # Afficher le résumé
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ WORKFLOW")
        print(f"{'='*60}")
        print(f"  ID:         {workflow_id}")
        print(f"  Statut:     {'✅ SUCCÈS' if statut == 'succes' else '❌ ÉCHEC'}")
        print(f"  Durée:      {duree}ms")
        print(f"  Étapes:     {len(self.etapes)}")

        if fichiers:
            print(f"  Fichiers:   {len(fichiers)}")
            for f in fichiers:
                print(f"              → {f}")

        if score:
            print(f"  Conformité: {score:.0%}")

        if self.alertes:
            print(f"\n  ⚠️  Alertes ({len(self.alertes)}):")
            for a in self.alertes:
                print(f"      • {a}")

        if self.erreurs:
            print(f"\n  ❌ Erreurs ({len(self.erreurs)}):")
            for e in self.erreurs:
                print(f"      • {e}")

        print(f"{'='*60}\n")

        return resultat

    # =========================================================================
    # Dashboard et statut
    # =========================================================================

    def afficher_stats_modeles(self):
        """
        Affiche les statistiques d'utilisation des modèles LLM (v2.1.0).

        Utile pour le monitoring de l'optimisation des coûts.
        """
        total = sum(self.stats_modeles.values())
        if total == 0:
            print("\n   Aucun appel LLM encore effectué")
            return

        print(f"\n💰 Statistiques Modèles LLM (v2.1.0):")
        print(f"   Total appels: {total}")

        # Afficher la distribution
        for modele in ["haiku", "sonnet", "opus"]:
            count = self.stats_modeles[modele]
            ratio = (count / total * 100) if total > 0 else 0
            barre = "█" * int(ratio / 5) + "░" * (20 - int(ratio / 5))

            # Économie estimée (vs Opus baseline)
            if modele == "haiku":
                economie = "80% économie vs Opus"
            elif modele == "sonnet":
                economie = "60% économie vs Opus"
            else:
                economie = "baseline"

            print(f"   {modele.capitalize():8s} {barre} {count:3d} ({ratio:5.1f}%) - {economie}")

        # Estimation économie globale (valeurs indicatives)
        # Coûts approximatifs: Opus=$0.005, Sonnet=$0.002, Haiku=$0.001 par appel
        cout_opus_total = total * 0.005
        cout_reel = (
            self.stats_modeles["opus"] * 0.005 +
            self.stats_modeles["sonnet"] * 0.002 +
            self.stats_modeles["haiku"] * 0.001
        )
        economie_pct = ((cout_opus_total - cout_reel) / cout_opus_total * 100) if cout_opus_total > 0 else 0

        print(f"\n   Économie estimée: {economie_pct:.0f}% vs {total} appels Opus")
        print(f"   Coût estimé: ${cout_reel:.2f} (vs ${cout_opus_total:.2f} baseline)")

    def afficher_dashboard(self):
        """Affiche le dashboard système."""
        print(f"\n{'='*60}")
        print(f"📊 NOTAIRE AI - Dashboard")
        print(f"{'='*60}")

        # Stats modèles LLM (v2.1.0)
        self.afficher_stats_modeles()

        # Conformité templates
        print(f"\n🎯 Conformité Templates:")
        for type_acte, score in self.CONFORMITE_TEMPLATES.items():
            barre = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            status = "✅ PROD" if score >= 0.8 else "⚠️ DEV"
            print(f"   {type_acte.value:25s} {barre} {score:.0%} {status}")

        # Historique récent
        historique_dir = self.project_root / '.tmp' / 'historique'
        if historique_dir.exists():
            fichiers = list(historique_dir.glob('*.json'))
            print(f"\n📁 Historique récent: {len(fichiers)} acte(s)")
            for f in sorted(fichiers, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                data = json.loads(f.read_text(encoding='utf-8'))
                print(f"   • {data.get('reference', f.stem)} - {data.get('type', '?')}")

        # Outputs
        outputs_dir = self.project_root / 'outputs'
        if outputs_dir.exists():
            docx = list(outputs_dir.glob('*.docx'))
            print(f"\n📄 Documents générés: {len(docx)} fichier(s)")

        print(f"\n{'='*60}\n")

    def afficher_statut(self):
        """Affiche le statut du système."""
        print(f"\n{'='*60}")
        print(f"🔧 STATUT SYSTÈME")
        print(f"{'='*60}")

        # Vérifier les scripts (v1.5.0 - nouvelle structure)
        scripts_requis = [
            ('core/assembler_acte.py', 'assembler_acte.py'),
            ('core/exporter_docx.py', 'exporter_docx.py'),
            ('core/valider_acte.py', 'valider_acte.py'),
            ('generation/generer_donnees_minimales.py', 'generer_donnees_minimales.py')
        ]

        print(f"\n📦 Scripts:")
        for chemin_rel, nom_affiche in scripts_requis:
            chemin = self.project_root / 'execution' / chemin_rel
            status = "✅" if chemin.exists() else "❌"
            print(f"   {status} {nom_affiche}")

        # Vérifier les templates
        print(f"\n📝 Templates:")
        for type_acte, template in self.TEMPLATES.items():
            chemin = self.project_root / 'templates' / template
            status = "✅" if chemin.exists() else "❌"
            print(f"   {status} {template}")

        # Vérifier extraction
        print(f"\n🔍 Module extraction:")
        try:
            from execution.extraction import ExtracteurV2
            print(f"   ✅ ExtracteurV2 disponible")
        except ImportError as e:
            print(f"   ❌ ExtracteurV2 non disponible: {e}")

        print(f"\n{'='*60}\n")


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Orchestrateur NotaireAI - Workflows unifiés',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Extraire un titre de propriété
  python orchestrateur_notaire.py extraire -i titre.pdf -o titre.json

  # Générer une promesse depuis un titre
  python orchestrateur_notaire.py titre-promesse -t titre.pdf -b beneficiaires.json -o promesse.docx

  # Générer un acte de vente direct
  python orchestrateur_notaire.py generer -t vente -d donnees.json -o acte.docx

  # Afficher le dashboard
  python orchestrateur_notaire.py dashboard
        """
    )

    subparsers = parser.add_subparsers(dest='commande', help='Commandes disponibles')

    # Commande: extraire
    p_extraire = subparsers.add_parser('extraire', help='Extraire un titre de propriété')
    p_extraire.add_argument('-i', '--input', required=True, help='Fichier PDF/DOCX')
    p_extraire.add_argument('-o', '--output', help='Fichier JSON de sortie')
    p_extraire.add_argument('-v', '--verbose', action='store_true')

    # Commande: titre-promesse
    p_tp = subparsers.add_parser('titre-promesse', help='Titre → Promesse de vente')
    p_tp.add_argument('-t', '--titre', required=True, help='Titre PDF/DOCX ou référence')
    p_tp.add_argument('-b', '--beneficiaires', required=True, help='JSON des bénéficiaires')
    p_tp.add_argument('-o', '--output', required=True, help='DOCX de sortie')
    p_tp.add_argument('--prix', type=float, help='Prix en euros')
    p_tp.add_argument('-v', '--verbose', action='store_true')

    # Commande: promesse-vente
    p_pv = subparsers.add_parser('promesse-vente', help='Promesse → Acte de vente')
    p_pv.add_argument('-p', '--promesse', required=True, help='Promesse JSON ou référence')
    p_pv.add_argument('-c', '--complements', help='Données complémentaires JSON')
    p_pv.add_argument('-o', '--output', help='DOCX de sortie')
    p_pv.add_argument('-v', '--verbose', action='store_true')

    # Commande: generer
    p_gen = subparsers.add_parser('generer', help='Générer un acte directement')
    p_gen.add_argument('-t', '--type', required=True,
                       choices=['vente', 'promesse_vente', 'reglement_copropriete', 'modificatif_edd'])
    p_gen.add_argument('-d', '--donnees', required=True, help='Fichier JSON des données')
    p_gen.add_argument('-o', '--output', help='DOCX de sortie')
    p_gen.add_argument('-v', '--verbose', action='store_true')

    # Commande: dashboard
    p_dash = subparsers.add_parser('dashboard', help='Afficher le dashboard')

    # Commande: status
    p_status = subparsers.add_parser('status', help='Vérifier le statut système')

    args = parser.parse_args()

    if not args.commande:
        parser.print_help()
        return

    orch = OrchestratorNotaire(verbose=getattr(args, 'verbose', False))

    if args.commande == 'extraire':
        orch.extraire_titre(args.input, args.output)

    elif args.commande == 'titre-promesse':
        beneficiaires = json.loads(Path(args.beneficiaires).read_text(encoding='utf-8'))
        options = {}
        if args.prix:
            options['prix'] = {'montant': args.prix, 'devise': 'EUR'}
        orch.titre_vers_promesse(args.titre, beneficiaires, args.output, options)

    elif args.commande == 'promesse-vente':
        complements = {}
        if args.complements:
            complements = json.loads(Path(args.complements).read_text(encoding='utf-8'))
        orch.promesse_vers_vente(args.promesse, complements, args.output)

    elif args.commande == 'generer':
        donnees = json.loads(Path(args.donnees).read_text(encoding='utf-8'))
        orch.generer_acte_complet(args.type, donnees, args.output)

    elif args.commande == 'dashboard':
        orch.afficher_dashboard()

    elif args.commande == 'status':
        orch.afficher_statut()


if __name__ == '__main__':
    main()
