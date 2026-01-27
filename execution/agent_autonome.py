# -*- coding: utf-8 -*-
"""
Agent Autonome NotaireAI v1.0

Ce module implémente l'agent autonome capable de:
- Parser des demandes en langage naturel
- Rechercher dans Supabase si un dossier existe
- Générer ou modifier des actes en une seule commande
- Sauvegarder l'historique dans Supabase

Usage CLI:
    # Créer une nouvelle promesse
    python agent_autonome.py creer "Promesse Martin→Dupont, appart 67m² Paris, 450000€"

    # Modifier un acte existant
    python agent_autonome.py modifier "Changer le prix à 460000€ dans le dossier 2026-001"

    # Rechercher des dossiers
    python agent_autonome.py rechercher "Tous les actes pour Martin"

    # Générer depuis un dossier Supabase
    python agent_autonome.py generer "2026-001"

Usage Python:
    from execution.agent_autonome import AgentNotaire

    agent = AgentNotaire()
    result = agent.executer("Crée une promesse pour Martin→Dupont, 450000€")
"""

import sys
import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Chemins
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


class IntentionAgent(Enum):
    """Types d'intentions détectables."""
    CREER = "creer"
    MODIFIER = "modifier"
    RECHERCHER = "rechercher"
    GENERER = "generer"
    CHARGER = "charger"
    LISTER = "lister"
    AIDE = "aide"
    INCONNU = "inconnu"


class TypeActeAgent(Enum):
    """Types d'actes supportés."""
    PROMESSE_VENTE = "promesse_vente"
    VENTE = "vente"
    REGLEMENT_COPROPRIETE = "reglement_copropriete"
    MODIFICATIF_EDD = "modificatif_edd"
    AUTO = "auto"  # Détection automatique


@dataclass
class DemandeAnalysee:
    """Résultat de l'analyse d'une demande."""
    intention: IntentionAgent
    type_acte: TypeActeAgent
    confiance: float  # 0.0 à 1.0

    # Entités extraites
    vendeur: Optional[Dict[str, Any]] = None
    acquereur: Optional[Dict[str, Any]] = None
    bien: Optional[Dict[str, Any]] = None
    prix: Optional[Dict[str, Any]] = None

    # Référence existante
    reference_dossier: Optional[str] = None

    # Modifications demandées
    modifications: List[Dict[str, Any]] = field(default_factory=list)

    # Texte original
    texte_original: str = ""

    # Champs manquants
    champs_manquants: List[str] = field(default_factory=list)


@dataclass
class ResultatAgent:
    """Résultat d'une exécution de l'agent."""
    succes: bool
    message: str
    intention: IntentionAgent

    # Données générées
    dossier_id: Optional[str] = None
    reference: Optional[str] = None
    fichier_genere: Optional[str] = None

    # Résultats de recherche
    resultats_recherche: List[Dict[str, Any]] = field(default_factory=list)

    # Données du dossier
    donnees: Optional[Dict[str, Any]] = None

    # Workflow
    workflow_id: Optional[str] = None
    duree_ms: int = 0
    etapes: List[str] = field(default_factory=list)


class ParseurDemandeNL:
    """
    Parseur de demandes en langage naturel.

    Extrait les entités et intentions d'une demande comme:
    "Crée une promesse de vente pour Martin→Dupont, appartement 67m² Paris, 450000€"
    """

    # Patterns pour détecter l'intention
    PATTERNS_INTENTION = {
        IntentionAgent.CREER: [
            r'\b(cr[ée]e|g[ée]n[èe]re|fais|nouveau|nouvelle)\b.*\b(promesse|vente|acte)\b',
            r'\b(promesse|vente|acte)\b.*\b(pour|entre)\b',
            r'\b(nouveau|nouvelle)\s+(dossier|acte|promesse)\b',
        ],
        IntentionAgent.MODIFIER: [
            r'\b(modifi|chang|corrig|mets?\s+[àa]\s+jour)\b',
            r'\b(prix|montant|date|nom|adresse)\b.*\b([àa]|vers|en)\b.*\b\d',
            r'\b(remplace|substitue)\b',
        ],
        IntentionAgent.RECHERCHER: [
            r'\b(cherch|trouv|recherch|list)\b',
            r'\b(tous?\s+les?|quels?)\b.*\b(actes?|dossiers?|promesses?)\b',
            r'\b(pour|de|du)\b.*\b(vendeur|acqu[ée]reur|client)\b',
        ],
        IntentionAgent.GENERER: [
            r'\b(g[ée]n[èe]re|exporte?|produis?)\b.*\b(docx?|document|pdf)\b',
            r'\b(dossier|ref|r[ée]f[ée]rence)\s*[:#]?\s*\d{4}[-/]\d{3}',
        ],
        IntentionAgent.CHARGER: [
            r'\b(charge|ouvre?|affiche|montre)\b.*\b(dossier|acte|promesse)\b',
            r'\b(dossier|ref)\s*[:#]?\s*\d{4}[-/]\d{3}',
        ],
        IntentionAgent.LISTER: [
            r'\b(liste|affiche|montre)\b.*\b(tous?|r[ée]cents?|derniers?)\b',
        ],
        IntentionAgent.AIDE: [
            r'\b(aide|help|comment|quoi)\b',
            r'\b(que\s+puis|peux[\s-]tu)\b',
        ],
    }

    # Patterns pour le type d'acte
    PATTERNS_TYPE_ACTE = {
        TypeActeAgent.PROMESSE_VENTE: [
            r'\bpromesse\b',
            r'\bpuv\b',  # Promesse Unilatérale de Vente
        ],
        TypeActeAgent.VENTE: [
            r'\b(acte\s+de\s+)?vente\b',
            r'\bvente\s+d[ée]finitive\b',
        ],
        TypeActeAgent.REGLEMENT_COPROPRIETE: [
            r'\br[èe]glement\s+(de\s+)?copropri[ée]t[ée]\b',
            r'\bedd\b',
            r'\b[ée]tat\s+descriptif\b',
        ],
        TypeActeAgent.MODIFICATIF_EDD: [
            r'\bmodificatif\b.*\bedd\b',
            r'\bmodification\s+(du\s+)?r[èe]glement\b',
        ],
    }

    # Patterns pour les entités
    # Prix: doit avoir €/euros OU être un grand nombre (>1000) sans unité de surface
    PATTERN_PRIX = re.compile(
        r'(?P<montant>\d[\d\s]*(?:[.,]\d+)?)\s*(?P<devise>€|euros?|eur)\b'
        r'|'
        r'(?P<montant2>\d{4,}[\d\s]*)\b(?!\s*m)',  # Grand nombre sans 'm' après
        re.IGNORECASE
    )

    PATTERN_SURFACE = re.compile(
        r'(?P<surface>\d+(?:[.,]\d+)?)\s*(?P<unite>m[²2]|m[èe]tres?\s*carr[ée]s?)',
        re.IGNORECASE
    )

    PATTERN_REFERENCE = re.compile(
        r'(?:dossier|ref|référence|n[°o])?\s*[:#]?\s*(?P<ref>\d{4}[-/]\d{3})',
        re.IGNORECASE
    )

    PATTERN_FLECHE = re.compile(
        r'(?P<vendeur>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)\s*'
        r'(?:→|->|vers|à|pour)\s*'
        r'(?P<acquereur>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
        re.UNICODE
    )

    PATTERN_VILLE = re.compile(
        r'\b(?P<ville>Paris|Lyon|Marseille|Toulouse|Nice|Nantes|'
        r'Strasbourg|Montpellier|Bordeaux|Lille|Rennes|Reims|'
        r'Le\s+Havre|Saint-[A-ZÀ-Ÿ][a-zà-ÿ-]+)\b',
        re.IGNORECASE
    )

    PATTERN_CODE_POSTAL = re.compile(r'\b(?P<cp>\d{5})\b')

    PATTERN_TYPE_BIEN = re.compile(
        r'\b(?P<type>appartement|appart|maison|studio|t[1-6]|f[1-6]|'
        r'local\s+commercial|bureau|terrain|parking|cave|box)\b',
        re.IGNORECASE
    )

    def analyser(self, texte: str) -> DemandeAnalysee:
        """
        Analyse une demande en langage naturel.

        Args:
            texte: Texte de la demande

        Returns:
            DemandeAnalysee avec toutes les entités extraites
        """
        texte_lower = texte.lower()

        # Détecter l'intention
        intention, confiance_intention = self._detecter_intention(texte_lower)

        # Détecter le type d'acte
        type_acte = self._detecter_type_acte(texte_lower)

        # Extraire les entités
        vendeur = self._extraire_vendeur(texte)
        acquereur = self._extraire_acquereur(texte)
        bien = self._extraire_bien(texte)
        prix = self._extraire_prix(texte)
        reference = self._extraire_reference(texte)
        modifications = self._extraire_modifications(texte)

        # Calculer les champs manquants
        champs_manquants = self._identifier_champs_manquants(
            intention, vendeur, acquereur, bien, prix, reference
        )

        # Calculer la confiance globale
        confiance = self._calculer_confiance(
            intention, confiance_intention, vendeur, acquereur, bien, prix
        )

        return DemandeAnalysee(
            intention=intention,
            type_acte=type_acte,
            confiance=confiance,
            vendeur=vendeur,
            acquereur=acquereur,
            bien=bien,
            prix=prix,
            reference_dossier=reference,
            modifications=modifications,
            texte_original=texte,
            champs_manquants=champs_manquants
        )

    def _detecter_intention(self, texte: str) -> Tuple[IntentionAgent, float]:
        """Détecte l'intention principale."""
        for intention, patterns in self.PATTERNS_INTENTION.items():
            for pattern in patterns:
                if re.search(pattern, texte, re.IGNORECASE):
                    return intention, 0.9
        return IntentionAgent.INCONNU, 0.3

    def _detecter_type_acte(self, texte: str) -> TypeActeAgent:
        """Détecte le type d'acte demandé."""
        for type_acte, patterns in self.PATTERNS_TYPE_ACTE.items():
            for pattern in patterns:
                if re.search(pattern, texte, re.IGNORECASE):
                    return type_acte

        # Par défaut: promesse si "pour" est présent, vente sinon
        if re.search(r'\bpour\b', texte):
            return TypeActeAgent.PROMESSE_VENTE
        return TypeActeAgent.AUTO

    def _extraire_vendeur(self, texte: str) -> Optional[Dict[str, Any]]:
        """Extrait le vendeur de la demande."""
        # Pattern flèche: Martin→Dupont
        match = self.PATTERN_FLECHE.search(texte)
        if match:
            nom = match.group('vendeur')
            return self._creer_personne(nom, 'vendeur')

        # Pattern explicite: vendeur Martin
        match = re.search(
            r'\bvendeur\s+(?P<nom>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
            texte, re.IGNORECASE | re.UNICODE
        )
        if match:
            return self._creer_personne(match.group('nom'), 'vendeur')

        return None

    def _extraire_acquereur(self, texte: str) -> Optional[Dict[str, Any]]:
        """Extrait l'acquéreur de la demande."""
        # Pattern flèche: Martin→Dupont
        match = self.PATTERN_FLECHE.search(texte)
        if match:
            nom = match.group('acquereur')
            return self._creer_personne(nom, 'acquereur')

        # Pattern explicite: acquéreur Dupont
        match = re.search(
            r'\b(?:acqu[ée]reur|acheteur|b[ée]n[ée]ficiaire)\s+'
            r'(?P<nom>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
            texte, re.IGNORECASE | re.UNICODE
        )
        if match:
            return self._creer_personne(match.group('nom'), 'acquereur')

        return None

    def _creer_personne(self, nom: str, role: str) -> Dict[str, Any]:
        """Crée une structure de personne à partir d'un nom."""
        parts = nom.strip().split()

        if len(parts) >= 2:
            prenom = parts[0]
            nom_famille = ' '.join(parts[1:]).upper()
        else:
            prenom = ""
            nom_famille = parts[0].upper() if parts else ""

        return {
            "role": role,
            "civilite": "Monsieur",  # Par défaut
            "nom": nom_famille,
            "prenom": prenom,
            "personne_physique": {
                "civilite": "Monsieur",
                "nom": nom_famille,
                "prenom": prenom,
            }
        }

    def _extraire_bien(self, texte: str) -> Optional[Dict[str, Any]]:
        """Extrait les informations sur le bien."""
        bien = {}

        # Type de bien
        match_type = self.PATTERN_TYPE_BIEN.search(texte)
        if match_type:
            type_brut = match_type.group('type').lower()
            bien['type'] = self._normaliser_type_bien(type_brut)

        # Surface
        match_surface = self.PATTERN_SURFACE.search(texte)
        if match_surface:
            surface = match_surface.group('surface').replace(',', '.').replace(' ', '')
            bien['superficie'] = float(surface)
            bien['superficie_carrez'] = float(surface)

        # Ville
        match_ville = self.PATTERN_VILLE.search(texte)
        if match_ville:
            bien['ville'] = match_ville.group('ville')

        # Code postal
        match_cp = self.PATTERN_CODE_POSTAL.search(texte)
        if match_cp:
            bien['code_postal'] = match_cp.group('cp')

        if bien:
            return bien
        return None

    def _normaliser_type_bien(self, type_brut: str) -> str:
        """Normalise le type de bien."""
        mapping = {
            'appart': 'appartement',
            'studio': 'appartement',
            't1': 'appartement',
            't2': 'appartement',
            't3': 'appartement',
            't4': 'appartement',
            't5': 'appartement',
            't6': 'appartement',
            'f1': 'appartement',
            'f2': 'appartement',
            'f3': 'appartement',
            'f4': 'appartement',
            'f5': 'appartement',
            'f6': 'appartement',
        }
        return mapping.get(type_brut, type_brut)

    def _extraire_prix(self, texte: str) -> Optional[Dict[str, Any]]:
        """Extrait le prix de la demande."""
        # Chercher les montants avec €/euros d'abord
        for match in self.PATTERN_PRIX.finditer(texte):
            # Priorité: groupe avec devise explicite
            montant_str = match.group('montant') or match.group('montant2')

            if not montant_str:
                continue

            # Nettoyer: retirer espaces et convertir virgule en point
            montant_str = montant_str.replace(' ', '').replace(',', '.')

            try:
                montant = float(montant_str)

                # Si le montant est < 10000, c'est probablement une surface, pas un prix
                if montant < 10000 and not match.group('devise'):
                    continue

                # Si le montant semble être en milliers (ex: "450" pour "450000")
                if montant < 1000 and match.group('devise'):
                    montant *= 1000

                return {
                    "montant": int(montant),
                    "devise": "EUR",
                    "en_lettres": self._nombre_en_lettres(int(montant))
                }
            except ValueError:
                continue

        return None

    def _nombre_en_lettres(self, n: int) -> str:
        """Convertit un nombre en lettres (simplifié)."""
        if n == 0:
            return "zéro"

        # Pour les grands nombres, on simplifie
        if n >= 1000000:
            return f"{n // 1000000} million(s) {self._nombre_en_lettres(n % 1000000)}".strip()
        if n >= 1000:
            return f"{n // 1000} mille {self._nombre_en_lettres(n % 1000)}".strip()

        # Simplifié pour les petits nombres
        return str(n)

    def _extraire_reference(self, texte: str) -> Optional[str]:
        """Extrait une référence de dossier."""
        match = self.PATTERN_REFERENCE.search(texte)
        if match:
            return match.group('ref').replace('/', '-')
        return None

    def _extraire_modifications(self, texte: str) -> List[Dict[str, Any]]:
        """Extrait les modifications demandées."""
        modifications = []

        # Pattern: changer X à Y / modifier X en Y
        pattern = re.compile(
            r'\b(?:chang|modifi|mets?)\w*\s+'
            r'(?:le\s+)?(?P<champ>prix|montant|date|nom|adresse)\s+'
            r'(?:[àa]|en|vers)\s+(?P<valeur>\S+)',
            re.IGNORECASE
        )

        for match in pattern.finditer(texte):
            modifications.append({
                "champ": match.group('champ').lower(),
                "nouvelle_valeur": match.group('valeur')
            })

        return modifications

    def _identifier_champs_manquants(
        self,
        intention: IntentionAgent,
        vendeur: Optional[Dict],
        acquereur: Optional[Dict],
        bien: Optional[Dict],
        prix: Optional[Dict],
        reference: Optional[str]
    ) -> List[str]:
        """Identifie les champs manquants pour l'intention."""
        manquants = []

        if intention == IntentionAgent.CREER:
            if not vendeur:
                manquants.append("vendeur")
            if not acquereur:
                manquants.append("acquéreur")
            if not bien:
                manquants.append("bien (type, surface, adresse)")
            if not prix:
                manquants.append("prix")

        elif intention == IntentionAgent.MODIFIER:
            if not reference:
                manquants.append("référence du dossier")

        elif intention == IntentionAgent.GENERER:
            if not reference:
                manquants.append("référence du dossier")

        return manquants

    def _calculer_confiance(
        self,
        intention: IntentionAgent,
        confiance_intention: float,
        vendeur: Optional[Dict],
        acquereur: Optional[Dict],
        bien: Optional[Dict],
        prix: Optional[Dict]
    ) -> float:
        """Calcule la confiance globale de l'analyse."""
        score = confiance_intention

        # Bonus pour chaque entité trouvée
        if vendeur:
            score += 0.1
        if acquereur:
            score += 0.1
        if bien:
            score += 0.1
        if prix:
            score += 0.1

        # Plafonner à 1.0
        return min(score, 1.0)


class AgentNotaire:
    """
    Agent autonome pour la génération d'actes notariaux.

    Capable de:
    - Comprendre des demandes en langage naturel
    - Rechercher dans Supabase
    - Générer des actes complets
    - Modifier des actes existants
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialise l'agent.

        Args:
            supabase_url: URL Supabase (optionnel, utilise .env si absent)
            supabase_key: Clé Supabase (optionnel, utilise .env si absent)
        """
        self.project_root = PROJECT_ROOT
        self.parseur = ParseurDemandeNL()

        # Import de l'orchestrateur
        try:
            from execution.orchestrateur_notaire import OrchestratorNotaire
            self.orchestrateur = OrchestratorNotaire(verbose=True)
        except ImportError:
            try:
                from orchestrateur_notaire import OrchestratorNotaire
                self.orchestrateur = OrchestratorNotaire(verbose=True)
            except ImportError:
                print("⚠️ Orchestrateur non disponible")
                self.orchestrateur = None

        # Client Supabase (optionnel)
        self._supabase = None
        self._init_supabase(supabase_url, supabase_key)

    def _init_supabase(self, url: Optional[str], key: Optional[str]):
        """Initialise la connexion Supabase."""
        try:
            from supabase import create_client, Client

            # Charger depuis .env si non fourni
            if not url or not key:
                env_path = self.project_root / '.env'
                if env_path.exists():
                    env_content = env_path.read_text(encoding='utf-8')
                    for line in env_content.split('\n'):
                        if line.startswith('SUPABASE_URL='):
                            url = url or line.split('=', 1)[1].strip().strip('"\'')
                        elif line.startswith('SUPABASE_KEY='):
                            key = key or line.split('=', 1)[1].strip().strip('"\'')

            if url and key:
                self._supabase: Client = create_client(url, key)
                print("✅ Supabase connecté")
        except ImportError:
            print("ℹ️ Module supabase non installé - mode local uniquement")
        except Exception as e:
            print(f"⚠️ Erreur Supabase: {e}")

    def executer(self, demande: str) -> ResultatAgent:
        """
        Exécute une demande en langage naturel.

        Args:
            demande: Texte de la demande

        Returns:
            ResultatAgent avec le résultat de l'exécution
        """
        import time
        debut = time.time()
        etapes = []

        print(f"\n{'='*60}")
        print(f"🤖 AGENT NOTAIRE - Exécution")
        print(f"{'='*60}")
        print(f"📝 Demande: {demande}")
        print(f"{'='*60}\n")

        # Étape 1: Analyser la demande
        etapes.append("Analyse de la demande")
        analyse = self.parseur.analyser(demande)

        print(f"🔍 Analyse:")
        print(f"   • Intention: {analyse.intention.value}")
        print(f"   • Type acte: {analyse.type_acte.value}")
        print(f"   • Confiance: {analyse.confiance:.0%}")

        if analyse.vendeur:
            print(f"   • Vendeur: {analyse.vendeur.get('nom', '?')}")
        if analyse.acquereur:
            print(f"   • Acquéreur: {analyse.acquereur.get('nom', '?')}")
        if analyse.bien:
            print(f"   • Bien: {analyse.bien}")
        if analyse.prix:
            print(f"   • Prix: {analyse.prix.get('montant', 0):,.0f}€")
        if analyse.reference_dossier:
            print(f"   • Référence: {analyse.reference_dossier}")

        if analyse.champs_manquants:
            print(f"   ⚠️ Champs manquants: {', '.join(analyse.champs_manquants)}")

        # Router vers la bonne action
        if analyse.intention == IntentionAgent.CREER:
            resultat = self._action_creer(analyse, etapes)

        elif analyse.intention == IntentionAgent.MODIFIER:
            resultat = self._action_modifier(analyse, etapes)

        elif analyse.intention == IntentionAgent.RECHERCHER:
            resultat = self._action_rechercher(analyse, etapes)

        elif analyse.intention == IntentionAgent.GENERER:
            resultat = self._action_generer(analyse, etapes)

        elif analyse.intention == IntentionAgent.CHARGER:
            resultat = self._action_charger(analyse, etapes)

        elif analyse.intention == IntentionAgent.LISTER:
            resultat = self._action_lister(analyse, etapes)

        elif analyse.intention == IntentionAgent.AIDE:
            resultat = self._action_aide(analyse, etapes)

        else:
            resultat = ResultatAgent(
                succes=False,
                message="Je n'ai pas compris la demande. Essayez 'aide' pour voir les commandes disponibles.",
                intention=analyse.intention
            )

        # Finaliser
        duree = int((time.time() - debut) * 1000)
        resultat.duree_ms = duree
        resultat.etapes = etapes

        # Afficher le résumé
        print(f"\n{'='*60}")
        print(f"📊 RÉSULTAT")
        print(f"{'='*60}")
        print(f"   Statut:   {'✅ Succès' if resultat.succes else '❌ Échec'}")
        print(f"   Message:  {resultat.message}")
        if resultat.fichier_genere:
            print(f"   Fichier:  {resultat.fichier_genere}")
        if resultat.reference:
            print(f"   Réf:      {resultat.reference}")
        print(f"   Durée:    {duree}ms")
        print(f"{'='*60}\n")

        return resultat

    def _action_creer(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: créer un nouvel acte."""
        etapes.append("Création d'un nouvel acte")

        # Vérifier les champs obligatoires
        if analyse.champs_manquants:
            return ResultatAgent(
                succes=False,
                message=f"Informations manquantes: {', '.join(analyse.champs_manquants)}",
                intention=analyse.intention
            )

        # Construire les données
        etapes.append("Construction des données")
        donnees = self._construire_donnees(analyse)

        # Déterminer le type d'acte
        type_acte = self._resoudre_type_acte(analyse)

        # Générer la référence
        reference = f"{datetime.now().strftime('%Y')}-{datetime.now().strftime('%m%d%H%M')}"

        # Sauvegarder dans Supabase si disponible
        dossier_id = None
        if self._supabase:
            etapes.append("Sauvegarde dans Supabase")
            try:
                dossier_id = self._sauvegarder_dossier_supabase(reference, type_acte, donnees)
            except Exception as e:
                print(f"⚠️ Erreur sauvegarde Supabase: {e}")

        # Générer l'acte via l'orchestrateur
        etapes.append("Génération de l'acte")

        fichier_sortie = self.project_root / 'outputs' / f'{type_acte}_{reference}.docx'

        if self.orchestrateur:
            try:
                resultat_wf = self.orchestrateur.generer_acte_complet(
                    type_acte,
                    donnees,
                    str(fichier_sortie)
                )

                if resultat_wf.statut == "succes":
                    return ResultatAgent(
                        succes=True,
                        message=f"Acte {type_acte} généré avec succès",
                        intention=analyse.intention,
                        dossier_id=dossier_id,
                        reference=reference,
                        fichier_genere=str(fichier_sortie),
                        donnees=donnees,
                        workflow_id=resultat_wf.workflow_id
                    )
                else:
                    return ResultatAgent(
                        succes=False,
                        message=f"Erreur génération: {', '.join(resultat_wf.erreurs)}",
                        intention=analyse.intention,
                        reference=reference,
                        donnees=donnees
                    )
            except Exception as e:
                return ResultatAgent(
                    succes=False,
                    message=f"Erreur: {str(e)}",
                    intention=analyse.intention
                )
        else:
            # Mode dégradé: sauvegarder les données seulement
            donnees_path = self.project_root / '.tmp' / 'dossiers' / f'{reference}.json'
            donnees_path.parent.mkdir(parents=True, exist_ok=True)
            donnees_path.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding='utf-8')

            return ResultatAgent(
                succes=True,
                message=f"Données sauvegardées (orchestrateur non disponible)",
                intention=analyse.intention,
                dossier_id=dossier_id,
                reference=reference,
                fichier_genere=str(donnees_path),
                donnees=donnees
            )

    def _action_modifier(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: modifier un acte existant."""
        etapes.append("Modification d'un acte")

        if not analyse.reference_dossier:
            return ResultatAgent(
                succes=False,
                message="Référence du dossier requise pour modification",
                intention=analyse.intention
            )

        # Charger le dossier
        etapes.append("Chargement du dossier")
        dossier = self._charger_dossier(analyse.reference_dossier)

        if not dossier:
            return ResultatAgent(
                succes=False,
                message=f"Dossier {analyse.reference_dossier} non trouvé",
                intention=analyse.intention
            )

        # Appliquer les modifications
        etapes.append("Application des modifications")
        donnees = dossier.get('donnees_metier', dossier.get('donnees', {}))

        for modif in analyse.modifications:
            champ = modif['champ']
            valeur = modif['nouvelle_valeur']

            if champ == 'prix':
                try:
                    montant = float(valeur.replace('€', '').replace(' ', '').replace(',', '.'))
                    if montant < 1000:
                        montant *= 1000
                    donnees.setdefault('prix', {})['montant'] = int(montant)
                    print(f"   ✓ Prix modifié: {int(montant):,}€")
                except ValueError:
                    print(f"   ⚠️ Valeur prix invalide: {valeur}")

        # Mettre à jour dans Supabase
        if self._supabase:
            etapes.append("Mise à jour Supabase")
            try:
                self._mettre_a_jour_dossier_supabase(
                    analyse.reference_dossier,
                    donnees
                )
            except Exception as e:
                print(f"⚠️ Erreur mise à jour Supabase: {e}")

        # Re-générer l'acte
        etapes.append("Re-génération de l'acte")
        type_acte = dossier.get('type_acte', 'promesse_vente')
        fichier_sortie = self.project_root / 'outputs' / f'{type_acte}_{analyse.reference_dossier}_v2.docx'

        if self.orchestrateur:
            try:
                resultat_wf = self.orchestrateur.generer_acte_complet(
                    type_acte,
                    donnees,
                    str(fichier_sortie)
                )

                return ResultatAgent(
                    succes=resultat_wf.statut == "succes",
                    message="Acte modifié et re-généré" if resultat_wf.statut == "succes" else "Erreur",
                    intention=analyse.intention,
                    reference=analyse.reference_dossier,
                    fichier_genere=str(fichier_sortie),
                    donnees=donnees
                )
            except Exception as e:
                return ResultatAgent(
                    succes=False,
                    message=f"Erreur re-génération: {str(e)}",
                    intention=analyse.intention
                )

        return ResultatAgent(
            succes=True,
            message="Modifications appliquées",
            intention=analyse.intention,
            reference=analyse.reference_dossier,
            donnees=donnees
        )

    def _action_rechercher(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: rechercher des dossiers."""
        etapes.append("Recherche de dossiers")

        resultats = []

        # Rechercher dans Supabase
        if self._supabase:
            etapes.append("Requête Supabase")
            try:
                query = self._supabase.table('dossiers').select('*')

                # Filtrer par vendeur si spécifié
                if analyse.vendeur:
                    nom = analyse.vendeur.get('nom', '')
                    query = query.ilike('parties', f'%{nom}%')

                response = query.order('created_at', desc=True).limit(10).execute()

                for row in response.data:
                    resultats.append({
                        'id': row['id'],
                        'numero': row['numero'],
                        'type_acte': row['type_acte'],
                        'statut': row['statut'],
                        'parties': row.get('parties', []),
                        'created_at': row['created_at']
                    })
            except Exception as e:
                print(f"⚠️ Erreur recherche Supabase: {e}")

        # Rechercher dans le cache local
        etapes.append("Recherche locale")
        cache_dir = self.project_root / '.tmp' / 'historique'
        if cache_dir.exists():
            for fichier in cache_dir.glob('*.json'):
                try:
                    data = json.loads(fichier.read_text(encoding='utf-8'))

                    # Filtrer
                    if analyse.vendeur:
                        nom_recherche = analyse.vendeur.get('nom', '').lower()
                        donnees_str = json.dumps(data.get('donnees', {})).lower()
                        if nom_recherche not in donnees_str:
                            continue

                    resultats.append({
                        'reference': data.get('reference', fichier.stem),
                        'type': data.get('type', '?'),
                        'date': data.get('date', '?'),
                        'source': 'local'
                    })
                except Exception:
                    continue

        message = f"{len(resultats)} dossier(s) trouvé(s)"
        if analyse.vendeur:
            message += f" pour '{analyse.vendeur.get('nom', '')}'"

        return ResultatAgent(
            succes=True,
            message=message,
            intention=analyse.intention,
            resultats_recherche=resultats
        )

    def _action_generer(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: générer un acte depuis une référence."""
        etapes.append("Génération depuis référence")

        if not analyse.reference_dossier:
            return ResultatAgent(
                succes=False,
                message="Référence du dossier requise",
                intention=analyse.intention
            )

        # Charger le dossier
        dossier = self._charger_dossier(analyse.reference_dossier)

        if not dossier:
            return ResultatAgent(
                succes=False,
                message=f"Dossier {analyse.reference_dossier} non trouvé",
                intention=analyse.intention
            )

        # Générer
        type_acte = dossier.get('type_acte', 'promesse_vente')
        donnees = dossier.get('donnees_metier', dossier.get('donnees', {}))
        fichier_sortie = self.project_root / 'outputs' / f'{type_acte}_{analyse.reference_dossier}.docx'

        if self.orchestrateur:
            resultat_wf = self.orchestrateur.generer_acte_complet(
                type_acte,
                donnees,
                str(fichier_sortie)
            )

            return ResultatAgent(
                succes=resultat_wf.statut == "succes",
                message="Document généré" if resultat_wf.statut == "succes" else "Erreur",
                intention=analyse.intention,
                reference=analyse.reference_dossier,
                fichier_genere=str(fichier_sortie) if resultat_wf.statut == "succes" else None,
                donnees=donnees
            )

        return ResultatAgent(
            succes=False,
            message="Orchestrateur non disponible",
            intention=analyse.intention
        )

    def _action_charger(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: charger un dossier."""
        etapes.append("Chargement du dossier")

        if not analyse.reference_dossier:
            return ResultatAgent(
                succes=False,
                message="Référence du dossier requise",
                intention=analyse.intention
            )

        dossier = self._charger_dossier(analyse.reference_dossier)

        if dossier:
            return ResultatAgent(
                succes=True,
                message=f"Dossier {analyse.reference_dossier} chargé",
                intention=analyse.intention,
                reference=analyse.reference_dossier,
                donnees=dossier
            )

        return ResultatAgent(
            succes=False,
            message=f"Dossier {analyse.reference_dossier} non trouvé",
            intention=analyse.intention
        )

    def _action_lister(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: lister les dossiers récents."""
        etapes.append("Liste des dossiers")

        resultats = []

        # Lister depuis Supabase
        if self._supabase:
            try:
                response = self._supabase.table('dossiers') \
                    .select('*') \
                    .order('created_at', desc=True) \
                    .limit(10) \
                    .execute()

                for row in response.data:
                    resultats.append({
                        'numero': row['numero'],
                        'type_acte': row['type_acte'],
                        'statut': row['statut'],
                        'created_at': row['created_at']
                    })
            except Exception as e:
                print(f"⚠️ Erreur Supabase: {e}")

        # Lister depuis le cache local
        cache_dir = self.project_root / '.tmp' / 'historique'
        if cache_dir.exists():
            for fichier in sorted(cache_dir.glob('*.json'),
                                  key=lambda x: x.stat().st_mtime,
                                  reverse=True)[:10]:
                try:
                    data = json.loads(fichier.read_text(encoding='utf-8'))
                    resultats.append({
                        'reference': data.get('reference', fichier.stem),
                        'type': data.get('type', '?'),
                        'date': data.get('date', '?'),
                        'source': 'local'
                    })
                except Exception:
                    continue

        return ResultatAgent(
            succes=True,
            message=f"{len(resultats)} dossier(s) trouvé(s)",
            intention=analyse.intention,
            resultats_recherche=resultats
        )

    def _action_aide(self, analyse: DemandeAnalysee, etapes: List[str]) -> ResultatAgent:
        """Action: afficher l'aide."""
        aide = """
🤖 Agent NotaireAI - Commandes disponibles

📝 CRÉER UN ACTE
   "Crée une promesse Martin→Dupont, appart 67m² Paris, 450000€"
   "Génère un acte de vente pour Durand→Petit, maison Lyon, 320000€"

✏️ MODIFIER UN ACTE
   "Change le prix à 460000€ dans le dossier 2026-001"
   "Modifie l'adresse dans la promesse 2026-0125"

🔍 RECHERCHER
   "Trouve tous les actes pour Martin"
   "Liste les promesses récentes"

📄 GÉNÉRER DOCUMENT
   "Génère le DOCX pour le dossier 2026-001"
   "Exporte la promesse 2026-0125"

📋 LISTER
   "Liste les 10 derniers dossiers"
   "Affiche les actes récents"

💡 SYNTAXE
   • Vendeur→Acquéreur : "Martin→Dupont"
   • Prix : "450000€" ou "450 000 euros"
   • Référence : "dossier 2026-001" ou "ref:2026-001"
        """

        return ResultatAgent(
            succes=True,
            message=aide,
            intention=analyse.intention
        )

    # =========================================================================
    # Méthodes utilitaires
    # =========================================================================

    # Mapping type_acte vers nom de fichier exemple
    FICHIERS_EXEMPLE = {
        'promesse_vente': 'donnees_promesse_exemple.json',
        'vente': 'donnees_vente_exemple.json',
        'reglement_copropriete': 'donnees_reglement_copropriete_exemple.json',
        'modificatif_edd': 'donnees_modificatif_edd_exemple.json',
    }

    def _construire_donnees(self, analyse: DemandeAnalysee) -> Dict[str, Any]:
        """Construit les données complètes depuis l'analyse."""
        import copy

        type_acte = self._resoudre_type_acte(analyse)

        # Charger les données d'exemple comme base (deep copy)
        nom_fichier = self.FICHIERS_EXEMPLE.get(type_acte, f'donnees_{type_acte}_exemple.json')
        exemple_path = self.project_root / 'exemples' / nom_fichier

        if exemple_path.exists():
            donnees = json.loads(exemple_path.read_text(encoding='utf-8'))
            donnees = copy.deepcopy(donnees)
        else:
            donnees = {}

        # Fusionner les données extraites (SANS écraser les données complètes)
        # On modifie uniquement les noms/infos de base dans les personnes existantes

        if analyse.vendeur:
            if type_acte == 'promesse_vente':
                # Modifier le premier promettant existant au lieu de le remplacer
                if donnees.get('promettants') and len(donnees['promettants']) > 0:
                    self._fusionner_personne(donnees['promettants'][0], analyse.vendeur)
                else:
                    donnees['promettants'] = [analyse.vendeur]
            else:
                if donnees.get('vendeurs') and len(donnees['vendeurs']) > 0:
                    self._fusionner_personne(donnees['vendeurs'][0], analyse.vendeur)
                else:
                    donnees['vendeurs'] = [analyse.vendeur]

        if analyse.acquereur:
            if type_acte == 'promesse_vente':
                if donnees.get('beneficiaires') and len(donnees['beneficiaires']) > 0:
                    self._fusionner_personne(donnees['beneficiaires'][0], analyse.acquereur)
                else:
                    donnees['beneficiaires'] = [analyse.acquereur]
            else:
                if donnees.get('acquereurs') and len(donnees['acquereurs']) > 0:
                    self._fusionner_personne(donnees['acquereurs'][0], analyse.acquereur)
                else:
                    donnees['acquereurs'] = [analyse.acquereur]

        # Fusionner les infos du bien (pas remplacer)
        if analyse.bien:
            donnees.setdefault('bien', {})
            for key, value in analyse.bien.items():
                if value:  # Seulement si la valeur n'est pas vide
                    donnees['bien'][key] = value

        # Fusionner le prix
        if analyse.prix:
            donnees.setdefault('prix', {})
            for key, value in analyse.prix.items():
                if value:
                    donnees['prix'][key] = value

        # Ajouter la date sous le bon format (objet, pas string)
        now = datetime.now()
        donnees.setdefault('acte', {})['date'] = {
            'jour': now.day,
            'mois': now.month,
            'annee': now.year
        }

        return donnees

    def _fusionner_personne(self, cible: Dict[str, Any], source: Dict[str, Any]):
        """Fusionne les données d'une personne (modifie cible en place)."""
        # Mettre à jour les champs de premier niveau
        if source.get('nom'):
            cible['nom'] = source['nom']
        if source.get('prenom'):
            cible['prenom'] = source['prenom']
            # Certains templates utilisent 'prenoms' au pluriel
            cible['prenoms'] = source['prenom']
        if source.get('civilite'):
            cible['civilite'] = source['civilite']

        # Mettre à jour personne_physique si existe dans la cible
        if 'personne_physique' in cible:
            pp_cible = cible['personne_physique']
            if source.get('nom'):
                pp_cible['nom'] = source['nom']
            if source.get('prenom'):
                pp_cible['prenom'] = source['prenom']
            if source.get('civilite'):
                pp_cible['civilite'] = source['civilite']

    def _resoudre_type_acte(self, analyse: DemandeAnalysee) -> str:
        """Résout le type d'acte final."""
        if analyse.type_acte == TypeActeAgent.AUTO:
            return 'promesse_vente'  # Par défaut
        return analyse.type_acte.value

    def _charger_dossier(self, reference: str) -> Optional[Dict[str, Any]]:
        """Charge un dossier depuis Supabase ou le cache local."""
        # Essayer Supabase
        if self._supabase:
            try:
                response = self._supabase.table('dossiers') \
                    .select('*') \
                    .eq('numero', reference) \
                    .single() \
                    .execute()

                if response.data:
                    return response.data
            except Exception:
                pass

        # Fallback: cache local
        cache_path = self.project_root / '.tmp' / 'historique' / f'{reference}.json'
        if cache_path.exists():
            return json.loads(cache_path.read_text(encoding='utf-8'))

        # Chercher avec le préfixe
        for fichier in (self.project_root / '.tmp' / 'historique').glob(f'*{reference}*.json'):
            return json.loads(fichier.read_text(encoding='utf-8'))

        return None

    def _sauvegarder_dossier_supabase(
        self,
        reference: str,
        type_acte: str,
        donnees: Dict[str, Any]
    ) -> Optional[str]:
        """Sauvegarde un nouveau dossier dans Supabase."""
        if not self._supabase:
            return None

        # Récupérer l'étude par défaut
        try:
            etudes = self._supabase.table('etudes').select('id').limit(1).execute()
            etude_id = etudes.data[0]['id'] if etudes.data else None
        except Exception:
            etude_id = None

        if not etude_id:
            print("⚠️ Aucune étude trouvée dans Supabase")
            return None

        # Préparer les parties
        parties = []

        if 'vendeurs' in donnees:
            for v in donnees['vendeurs']:
                parties.append({
                    'role': 'vendeur',
                    'civilite': v.get('civilite', 'Monsieur'),
                    'nom': v.get('nom', ''),
                    'prenom': v.get('prenom', '')
                })

        if 'promettants' in donnees:
            for p in donnees['promettants']:
                parties.append({
                    'role': 'vendeur',
                    'civilite': p.get('civilite', 'Monsieur'),
                    'nom': p.get('nom', ''),
                    'prenom': p.get('prenom', '')
                })

        if 'acquereurs' in donnees:
            for a in donnees['acquereurs']:
                parties.append({
                    'role': 'acquereur',
                    'civilite': a.get('civilite', 'Madame'),
                    'nom': a.get('nom', ''),
                    'prenom': a.get('prenom', '')
                })

        if 'beneficiaires' in donnees:
            for b in donnees['beneficiaires']:
                parties.append({
                    'role': 'acquereur',
                    'civilite': b.get('civilite', 'Madame'),
                    'nom': b.get('nom', ''),
                    'prenom': b.get('prenom', '')
                })

        # Préparer les biens
        biens = []
        if 'bien' in donnees:
            biens.append({
                'type': donnees['bien'].get('type', 'appartement'),
                'adresse': donnees['bien'].get('adresse', ''),
                'superficie': donnees['bien'].get('superficie', 0)
            })

        # Créer le dossier
        try:
            response = self._supabase.table('dossiers').insert({
                'etude_id': etude_id,
                'numero': reference,
                'type_acte': type_acte,
                'statut': 'brouillon',
                'parties': parties,
                'biens': biens,
                'donnees_metier': {
                    'prix': donnees.get('prix', {}),
                    'delais': donnees.get('delais', {})
                }
            }).execute()

            if response.data:
                print(f"   ✓ Dossier créé dans Supabase: {reference}")
                return response.data[0]['id']
        except Exception as e:
            print(f"   ⚠️ Erreur création dossier: {e}")

        return None

    def _mettre_a_jour_dossier_supabase(
        self,
        reference: str,
        donnees: Dict[str, Any]
    ) -> bool:
        """Met à jour un dossier existant dans Supabase."""
        if not self._supabase:
            return False

        try:
            response = self._supabase.table('dossiers') \
                .update({'donnees_metier': donnees, 'updated_at': 'now()'}) \
                .eq('numero', reference) \
                .execute()

            return len(response.data) > 0
        except Exception as e:
            print(f"⚠️ Erreur mise à jour: {e}")
            return False


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Agent Autonome NotaireAI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Créer une promesse
  python agent_autonome.py creer "Promesse Martin→Dupont, appart 67m² Paris, 450000€"

  # Modifier un acte
  python agent_autonome.py modifier "Changer le prix à 460000€ dans le dossier 2026-001"

  # Rechercher
  python agent_autonome.py rechercher "Actes pour Martin"

  # Générer un DOCX
  python agent_autonome.py generer "2026-001"

  # Mode interactif
  python agent_autonome.py
        """
    )

    parser.add_argument('commande', nargs='?', default='interactif',
                        choices=['creer', 'modifier', 'rechercher', 'generer', 'lister', 'aide', 'interactif'],
                        help='Commande à exécuter')
    parser.add_argument('demande', nargs='*', help='Demande en langage naturel')

    args = parser.parse_args()

    agent = AgentNotaire()

    if args.commande == 'interactif' or not args.demande:
        # Mode interactif
        print("\n🤖 Agent NotaireAI - Mode interactif")
        print("   Tapez 'aide' pour voir les commandes, 'q' pour quitter\n")

        while True:
            try:
                demande = input(">>> ").strip()

                if demande.lower() in ('q', 'quit', 'exit'):
                    print("Au revoir!")
                    break

                if not demande:
                    continue

                agent.executer(demande)

            except KeyboardInterrupt:
                print("\nAu revoir!")
                break
            except EOFError:
                break
    else:
        # Mode commande directe
        demande_complete = ' '.join(args.demande)

        # Préfixer avec la commande si pas déjà présent
        if args.commande not in demande_complete.lower():
            demande_complete = f"{args.commande} {demande_complete}"

        agent.executer(demande_complete)


if __name__ == '__main__':
    main()
