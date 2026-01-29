# -*- coding: utf-8 -*-
"""
Agent Autonome NotaireAI v1.2

Ce module implémente l'agent autonome capable de:
- Parser des demandes en langage naturel
- Support multi-parties: "Martin & Pierre → Dupont & Thomas" (v1.1)
- Validation intégrée avant génération avec 12 règles métier (v1.2)
- Score de confiance détaillé avec suggestions (v1.1)
- Validation avancée: quotités, cadastre, diagnostics, plus-value (v1.2)
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
import copy
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

# Import du validateur avancé
try:
    from valider_acte import ValidateurActe, RapportValidation, NiveauErreur
    VALIDATEUR_AVANCE_DISPONIBLE = True
except ImportError:
    try:
        from execution.core.valider_acte import ValidateurActe, RapportValidation, NiveauErreur
        VALIDATEUR_AVANCE_DISPONIBLE = True
    except ImportError:
        VALIDATEUR_AVANCE_DISPONIBLE = False
        print("⚠️ Validateur avancé non disponible - utilisation validation basique")


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

    # Multi-parties (v1.1)
    vendeurs_multiples: List[Dict[str, Any]] = field(default_factory=list)
    acquereurs_multiples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ScoreConfianceDetaille:
    """
    Score de confiance détaillé avec breakdown par catégorie.

    Permet de comprendre exactement pourquoi la confiance est haute ou basse.
    """
    score_global: float  # 0.0 à 1.0

    # Breakdown par catégorie
    score_vendeur: float = 0.0
    score_acquereur: float = 0.0
    score_bien: float = 0.0
    score_prix: float = 0.0
    score_type_acte: float = 0.0
    score_intention: float = 0.0

    # Détails
    champs_detectes: List[str] = field(default_factory=list)
    champs_manquants: List[str] = field(default_factory=list)
    champs_optionnels_manquants: List[str] = field(default_factory=list)

    # Suggestions
    suggestions: List[str] = field(default_factory=list)

    def explication(self) -> str:
        """Génère une explication lisible du score."""
        def indicateur(score: float) -> str:
            if score >= 0.8:
                return "✓"
            elif score >= 0.5:
                return "~"
            else:
                return "!"

        lignes = [
            f"Score global: {self.score_global:.0%}",
            f"",
            f"Détail par catégorie:",
            f"  • Vendeur:    {self.score_vendeur:.0%} {indicateur(self.score_vendeur)}",
            f"  • Acquéreur:  {self.score_acquereur:.0%} {indicateur(self.score_acquereur)}",
            f"  • Bien:       {self.score_bien:.0%} {indicateur(self.score_bien)}",
            f"  • Prix:       {self.score_prix:.0%} {indicateur(self.score_prix)}",
            f"  • Type acte:  {self.score_type_acte:.0%} {indicateur(self.score_type_acte)}",
        ]

        if self.champs_manquants:
            lignes.append(f"")
            lignes.append(f"Champs manquants: {', '.join(self.champs_manquants)}")

        if self.suggestions:
            lignes.append(f"")
            lignes.append(f"Suggestions:")
            for s in self.suggestions[:3]:
                lignes.append(f"  → {s}")

        return "\n".join(lignes)


@dataclass
class ResultatValidation:
    """Résultat de la validation des données."""
    valide: bool
    erreurs: List[str] = field(default_factory=list)
    avertissements: List[str] = field(default_factory=list)
    champs_manquants: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


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
        r'(?P<montant>\d[\d\s]*(?:[.,]\d+)?)\s*(?P<multiplicateur>k|K)?\s*(?P<devise>€|euros?|eur)\b'
        r'|'
        r'(?P<montant2>\d{4,}[\d\s]*)\b(?!\s*m)',  # Grand nombre sans 'm' après
        re.IGNORECASE
    )

    # Pattern pour "450k€" ou "1.2M€"
    PATTERN_PRIX_COURT = re.compile(
        r'(?P<montant>\d+(?:[.,]\d+)?)\s*(?P<mult>[kKmM])?\s*(?P<devise>€|euros?)',
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

    # Pattern multi-parties: "Martin & Pierre → Dupont & Thomas" ou "Martin et Pierre vers Dupont et Thomas"
    PATTERN_FLECHE_MULTI = re.compile(
        r'(?P<vendeurs>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?'
        r'(?:\s*(?:&|et)\s*[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)*)\s*'
        r'(?:→|->|vers|à|pour)\s*'
        r'(?P<acquereurs>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?'
        r'(?:\s*(?:&|et)\s*[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)*)',
        re.UNICODE | re.IGNORECASE
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

        # Extraire les entités (support multi-parties)
        vendeurs_multiples = self._extraire_vendeurs_multiples(texte)
        acquereurs_multiples = self._extraire_acquereurs_multiples(texte)
        vendeur = vendeurs_multiples[0] if vendeurs_multiples else None
        acquereur = acquereurs_multiples[0] if acquereurs_multiples else None
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
            champs_manquants=champs_manquants,
            vendeurs_multiples=vendeurs_multiples,
            acquereurs_multiples=acquereurs_multiples
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
        """Extrait le vendeur de la demande (premier vendeur si multiples)."""
        vendeurs = self._extraire_vendeurs_multiples(texte)
        return vendeurs[0] if vendeurs else None

    def _extraire_acquereur(self, texte: str) -> Optional[Dict[str, Any]]:
        """Extrait l'acquéreur de la demande (premier acquéreur si multiples)."""
        acquereurs = self._extraire_acquereurs_multiples(texte)
        return acquereurs[0] if acquereurs else None

    def _extraire_vendeurs_multiples(self, texte: str) -> List[Dict[str, Any]]:
        """
        Extrait tous les vendeurs d'une demande.

        Supporte:
        - "Martin → Dupont" (un vendeur)
        - "Martin & Pierre → Dupont" (deux vendeurs)
        - "Martin et Pierre → Dupont et Thomas" (deux vendeurs)
        """
        vendeurs = []

        # Essayer d'abord le pattern multi-parties
        match = self.PATTERN_FLECHE_MULTI.search(texte)
        if match:
            vendeurs_str = match.group('vendeurs')
            noms = self._parser_liste_noms(vendeurs_str)
            for nom in noms:
                vendeurs.append(self._creer_personne(nom, 'vendeur'))
            return vendeurs

        # Fallback: pattern simple
        match = self.PATTERN_FLECHE.search(texte)
        if match:
            nom = match.group('vendeur')
            vendeurs.append(self._creer_personne(nom, 'vendeur'))
            return vendeurs

        # Pattern explicite: vendeur Martin
        match = re.search(
            r'\bvendeur\s+(?P<nom>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
            texte, re.IGNORECASE | re.UNICODE
        )
        if match:
            vendeurs.append(self._creer_personne(match.group('nom'), 'vendeur'))

        return vendeurs

    def _extraire_acquereurs_multiples(self, texte: str) -> List[Dict[str, Any]]:
        """
        Extrait tous les acquéreurs d'une demande.

        Supporte:
        - "Martin → Dupont" (un acquéreur)
        - "Martin → Dupont & Thomas" (deux acquéreurs)
        - "Martin et Pierre → Dupont et Thomas" (deux acquéreurs)
        """
        acquereurs = []

        # Essayer d'abord le pattern multi-parties
        match = self.PATTERN_FLECHE_MULTI.search(texte)
        if match:
            acquereurs_str = match.group('acquereurs')
            noms = self._parser_liste_noms(acquereurs_str)
            for nom in noms:
                acquereurs.append(self._creer_personne(nom, 'acquereur'))
            return acquereurs

        # Fallback: pattern simple
        match = self.PATTERN_FLECHE.search(texte)
        if match:
            nom = match.group('acquereur')
            acquereurs.append(self._creer_personne(nom, 'acquereur'))
            return acquereurs

        # Pattern explicite: acquéreur Dupont
        match = re.search(
            r'\b(?:acqu[ée]reur|acheteur|b[ée]n[ée]ficiaire)\s+'
            r'(?P<nom>[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
            texte, re.IGNORECASE | re.UNICODE
        )
        if match:
            acquereurs.append(self._creer_personne(match.group('nom'), 'acquereur'))

        return acquereurs

    def _parser_liste_noms(self, texte: str) -> List[str]:
        """
        Parse une liste de noms séparés par '&' ou 'et'.

        Args:
            texte: "Martin & Pierre" ou "Martin et Pierre"

        Returns:
            ["Martin", "Pierre"]
        """
        # Remplacer 'et' par '&' pour uniformiser
        texte_norm = re.sub(r'\s+et\s+', ' & ', texte, flags=re.IGNORECASE)

        # Séparer par '&'
        noms = [nom.strip() for nom in texte_norm.split('&')]

        # Filtrer les noms vides
        return [nom for nom in noms if nom]

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
        # Essayer d'abord le pattern court (450k€, 1.2M€)
        match_court = self.PATTERN_PRIX_COURT.search(texte)
        if match_court:
            try:
                montant_str = match_court.group('montant').replace(' ', '').replace(',', '.')
                montant = float(montant_str)

                # Appliquer le multiplicateur
                mult = match_court.group('mult')
                if mult:
                    mult = mult.lower()
                    if mult == 'k':
                        montant *= 1000
                    elif mult == 'm':
                        montant *= 1000000

                return {
                    "montant": int(montant),
                    "devise": "EUR",
                    "en_lettres": self._nombre_en_lettres(int(montant))
                }
            except (ValueError, AttributeError):
                pass

        # Chercher les montants avec €/euros (pattern standard)
        for match in self.PATTERN_PRIX.finditer(texte):
            # Priorité: groupe avec devise explicite
            montant_str = match.group('montant') or match.group('montant2')

            if not montant_str:
                continue

            # Nettoyer: retirer espaces et convertir virgule en point
            montant_str = montant_str.replace(' ', '').replace(',', '.')

            try:
                montant = float(montant_str)

                # Appliquer multiplicateur k/K si présent
                try:
                    mult = match.group('multiplicateur')
                    if mult and mult.lower() == 'k':
                        montant *= 1000
                except IndexError:
                    pass

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
            from execution.gestionnaires.orchestrateur import OrchestratorNotaire
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

    def valider_donnees(self, donnees: Dict[str, Any], type_acte: str) -> ResultatValidation:
        """
        Valide les données avant génération avec validation avancée v1.5.1.

        Utilise le ValidateurActe complet si disponible, sinon validation basique.

        Args:
            donnees: Données à valider
            type_acte: Type d'acte (promesse_vente, vente, etc.)

        Returns:
            ResultatValidation avec erreurs et suggestions
        """
        erreurs = []
        avertissements = []
        champs_manquants = []
        suggestions = []

        # =========================================================================
        # VALIDATION AVANCÉE (v1.5.1) si disponible
        # =========================================================================
        if VALIDATEUR_AVANCE_DISPONIBLE:
            try:
                validateur = ValidateurActe(type_acte)
                rapport: RapportValidation = validateur.valider_complet(donnees)

                # Convertir le rapport avancé vers le format agent
                for err in rapport.erreurs:
                    erreurs.append(f"[{err.code}] {err.message}")
                    if err.chemin:
                        champs_manquants.append(err.chemin.split('.')[0])
                    if err.suggestion:
                        suggestions.append(err.suggestion)

                for warn in rapport.avertissements:
                    avertissements.append(f"[{warn.code}] {warn.message}")
                    if warn.suggestion:
                        suggestions.append(warn.suggestion)

                # Dédupliquer les suggestions
                suggestions = list(dict.fromkeys(suggestions))[:8]

                return ResultatValidation(
                    valide=rapport.valide,
                    erreurs=erreurs,
                    avertissements=avertissements,
                    champs_manquants=list(set(champs_manquants)),
                    suggestions=suggestions
                )
            except Exception as e:
                print(f"⚠️ Erreur validation avancée: {e} - fallback validation basique")

        # =========================================================================
        # VALIDATION BASIQUE (fallback)
        # =========================================================================

        # Champs obligatoires par type d'acte
        champs_obligatoires = {
            'promesse_vente': ['promettants', 'beneficiaires', 'bien', 'prix'],
            'vente': ['vendeurs', 'acquereurs', 'bien', 'prix'],
            'reglement_copropriete': ['immeuble', 'lots'],
            'modificatif_edd': ['immeuble', 'modifications'],
        }

        # Aliases pour normalisation
        aliases = {
            'promettants': ['vendeurs', 'promettant'],
            'beneficiaires': ['acquereurs', 'acquéreurs', 'beneficiaire'],
            'vendeurs': ['promettants', 'vendeur'],
            'acquereurs': ['beneficiaires', 'bénéficiaires', 'acquereur'],
        }

        # Vérifier les champs obligatoires
        champs_requis = champs_obligatoires.get(type_acte, [])
        for champ in champs_requis:
            valeur = donnees.get(champ)

            # Vérifier les aliases si non trouvé
            if not valeur:
                for alias in aliases.get(champ, []):
                    valeur = donnees.get(alias)
                    if valeur:
                        break

            if not valeur:
                champs_manquants.append(champ)
                erreurs.append(f"Champ obligatoire manquant: {champ}")

        # Validations spécifiques
        if type_acte in ('promesse_vente', 'vente'):
            # Vérifier le prix
            prix = donnees.get('prix', {})
            if prix and prix.get('montant', 0) <= 0:
                erreurs.append("Le prix doit être supérieur à 0")

            # Vérifier le bien
            bien = donnees.get('bien', {})
            if bien:
                if not bien.get('adresse') and not bien.get('adresse_complete'):
                    avertissements.append("Adresse du bien non spécifiée")
                    suggestions.append("Ajouter l'adresse complète du bien")

            # Vérifier les quotités si multiples parties
            vendeurs = donnees.get('promettants') or donnees.get('vendeurs') or []
            acquereurs = donnees.get('beneficiaires') or donnees.get('acquereurs') or []

            if len(vendeurs) > 1:
                suggestions.append("Vérifier les quotités vendues pour chaque vendeur")

            if len(acquereurs) > 1:
                suggestions.append("Vérifier les quotités acquises pour chaque acquéreur")

        # Avertissements contextuels
        if type_acte == 'promesse_vente':
            if not donnees.get('conditions_suspensives'):
                avertissements.append("Aucune condition suspensive définie")
                suggestions.append("Ajouter une condition suspensive de prêt si applicable")

            if not donnees.get('indemnite_immobilisation'):
                avertissements.append("Indemnité d'immobilisation non définie")
                suggestions.append("Définir l'indemnité d'immobilisation (généralement 5-10% du prix)")

        return ResultatValidation(
            valide=len(erreurs) == 0,
            erreurs=erreurs,
            avertissements=avertissements,
            champs_manquants=champs_manquants,
            suggestions=suggestions
        )

    def calculer_score_confiance_detaille(self, analyse: DemandeAnalysee) -> ScoreConfianceDetaille:
        """
        Calcule un score de confiance détaillé avec breakdown.

        Args:
            analyse: Résultat de l'analyse

        Returns:
            ScoreConfianceDetaille avec toutes les métriques
        """
        scores = {}
        champs_detectes = []
        champs_manquants = []
        suggestions = []

        # Score vendeur
        if analyse.vendeur:
            champs_detectes.append('vendeur')
            nom = analyse.vendeur.get('nom', '')
            prenom = analyse.vendeur.get('prenom', '')
            scores['vendeur'] = 0.5 + (0.25 if nom else 0) + (0.25 if prenom else 0)
        else:
            champs_manquants.append('vendeur')
            scores['vendeur'] = 0.0
            suggestions.append("Préciser le nom du vendeur (ex: Martin → ...)")

        # Score acquéreur
        if analyse.acquereur:
            champs_detectes.append('acquereur')
            nom = analyse.acquereur.get('nom', '')
            prenom = analyse.acquereur.get('prenom', '')
            scores['acquereur'] = 0.5 + (0.25 if nom else 0) + (0.25 if prenom else 0)
        else:
            champs_manquants.append('acquereur')
            scores['acquereur'] = 0.0
            suggestions.append("Préciser le nom de l'acquéreur (ex: ... → Dupont)")

        # Score bien
        if analyse.bien:
            champs_detectes.append('bien')
            bien_score = 0.3
            if analyse.bien.get('type'):
                bien_score += 0.2
            if analyse.bien.get('superficie'):
                bien_score += 0.25
            if analyse.bien.get('ville') or analyse.bien.get('code_postal'):
                bien_score += 0.25
            scores['bien'] = bien_score
        else:
            champs_manquants.append('bien')
            scores['bien'] = 0.0
            suggestions.append("Préciser le type de bien et sa localisation")

        # Score prix
        if analyse.prix and analyse.prix.get('montant', 0) > 0:
            champs_detectes.append('prix')
            scores['prix'] = 1.0
        else:
            champs_manquants.append('prix')
            scores['prix'] = 0.0
            suggestions.append("Indiquer le prix de vente (ex: 450000€)")

        # Score type acte
        if analyse.type_acte != TypeActeAgent.AUTO:
            champs_detectes.append('type_acte')
            scores['type_acte'] = 1.0
        else:
            scores['type_acte'] = 0.5
            suggestions.append("Préciser le type d'acte (promesse ou vente)")

        # Score intention
        if analyse.intention != IntentionAgent.INCONNU:
            champs_detectes.append('intention')
            scores['intention'] = 1.0
        else:
            scores['intention'] = 0.3

        # Calculer score global (moyenne pondérée)
        poids = {
            'vendeur': 0.2,
            'acquereur': 0.2,
            'bien': 0.15,
            'prix': 0.2,
            'type_acte': 0.15,
            'intention': 0.1
        }

        score_global = sum(scores[k] * poids[k] for k in poids)

        return ScoreConfianceDetaille(
            score_global=score_global,
            score_vendeur=scores['vendeur'],
            score_acquereur=scores['acquereur'],
            score_bien=scores['bien'],
            score_prix=scores['prix'],
            score_type_acte=scores['type_acte'],
            score_intention=scores['intention'],
            champs_detectes=champs_detectes,
            champs_manquants=champs_manquants,
            suggestions=suggestions[:5]  # Limiter à 5 suggestions
        )

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

        # Calculer le score détaillé
        score_detaille = self.calculer_score_confiance_detaille(analyse)

        print(f"🔍 Analyse:")
        print(f"   • Intention: {analyse.intention.value}")
        print(f"   • Type acte: {analyse.type_acte.value}")
        print(f"   • Confiance: {score_detaille.score_global:.0%}")

        # Afficher les vendeurs (support multi-parties)
        if analyse.vendeurs_multiples:
            if len(analyse.vendeurs_multiples) == 1:
                print(f"   • Vendeur: {analyse.vendeurs_multiples[0].get('nom', '?')}")
            else:
                noms = [v.get('nom', '?') for v in analyse.vendeurs_multiples]
                print(f"   • Vendeurs ({len(noms)}): {' & '.join(noms)}")
        elif analyse.vendeur:
            print(f"   • Vendeur: {analyse.vendeur.get('nom', '?')}")

        # Afficher les acquéreurs (support multi-parties)
        if analyse.acquereurs_multiples:
            if len(analyse.acquereurs_multiples) == 1:
                print(f"   • Acquéreur: {analyse.acquereurs_multiples[0].get('nom', '?')}")
            else:
                noms = [a.get('nom', '?') for a in analyse.acquereurs_multiples]
                print(f"   • Acquéreurs ({len(noms)}): {' & '.join(noms)}")
        elif analyse.acquereur:
            print(f"   • Acquéreur: {analyse.acquereur.get('nom', '?')}")

        if analyse.bien:
            print(f"   • Bien: {analyse.bien}")
        if analyse.prix:
            print(f"   • Prix: {analyse.prix.get('montant', 0):,.0f}€")
        if analyse.reference_dossier:
            print(f"   • Référence: {analyse.reference_dossier}")

        if analyse.champs_manquants:
            print(f"   ⚠️ Champs manquants: {', '.join(analyse.champs_manquants)}")

        # Afficher les suggestions si confiance faible
        if score_detaille.score_global < 0.7 and score_detaille.suggestions:
            print(f"\n   💡 Suggestions:")
            for suggestion in score_detaille.suggestions[:3]:
                print(f"      → {suggestion}")

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

        # Construire les données (avec support multi-parties)
        etapes.append("Construction des données")
        donnees = self._construire_donnees(analyse)

        # Déterminer le type d'acte
        type_acte = self._resoudre_type_acte(analyse)

        # Valider les données avant génération (v1.5.1 - validation avancée)
        etapes.append("Validation des données (v1.5.1)")
        validation = self.valider_donnees(donnees, type_acte)

        # Afficher le résultat de validation de manière structurée
        print(f"\n{'─'*50}")
        print(f"📋 VALIDATION MÉTIER" + (" (avancée)" if VALIDATEUR_AVANCE_DISPONIBLE else ""))
        print(f"{'─'*50}")

        if not validation.valide:
            print(f"\n❌ ERREURS BLOQUANTES ({len(validation.erreurs)}):")
            for erreur in validation.erreurs[:10]:
                print(f"   • {erreur}")

            if len(validation.erreurs) > 10:
                print(f"   ... et {len(validation.erreurs) - 10} autres erreurs")

            return ResultatAgent(
                succes=False,
                message=f"Validation échouée: {len(validation.erreurs)} erreur(s)",
                intention=analyse.intention,
                donnees=donnees
            )

        print(f"✅ Validation réussie")

        # Afficher les avertissements
        if validation.avertissements:
            print(f"\n⚠️ AVERTISSEMENTS ({len(validation.avertissements)}):")
            for avert in validation.avertissements[:5]:
                print(f"   • {avert}")

        # Afficher les suggestions
        if validation.suggestions:
            print(f"\n💡 SUGGESTIONS ({len(validation.suggestions)}):")
            for suggestion in validation.suggestions[:4]:
                print(f"   → {suggestion}")

        print(f"{'─'*50}")

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
        # Support multi-parties: utiliser vendeurs_multiples si disponibles

        # Gestion des vendeurs/promettants (multi-parties)
        vendeurs_a_traiter = analyse.vendeurs_multiples if analyse.vendeurs_multiples else (
            [analyse.vendeur] if analyse.vendeur else []
        )

        if vendeurs_a_traiter:
            if type_acte == 'promesse_vente':
                cle_vendeur = 'promettants'
            else:
                cle_vendeur = 'vendeurs'

            # Si multi-parties, remplacer toute la liste
            if len(vendeurs_a_traiter) > 1:
                # Charger les données d'exemple pour chaque vendeur supplémentaire
                donnees_exemple = donnees.get(cle_vendeur, [{}])
                modele_personne = donnees_exemple[0] if donnees_exemple else {}

                nouvelles_personnes = []
                for i, vendeur in enumerate(vendeurs_a_traiter):
                    if i < len(donnees_exemple):
                        # Fusionner avec l'existant
                        personne = copy.deepcopy(donnees_exemple[i])
                        self._fusionner_personne(personne, vendeur)
                    else:
                        # Créer une nouvelle personne basée sur le modèle
                        personne = copy.deepcopy(modele_personne)
                        self._fusionner_personne(personne, vendeur)
                    nouvelles_personnes.append(personne)

                donnees[cle_vendeur] = nouvelles_personnes
            else:
                # Un seul vendeur: modifier le premier existant
                if donnees.get(cle_vendeur) and len(donnees[cle_vendeur]) > 0:
                    self._fusionner_personne(donnees[cle_vendeur][0], vendeurs_a_traiter[0])
                else:
                    donnees[cle_vendeur] = vendeurs_a_traiter

        # Gestion des acquéreurs/bénéficiaires (multi-parties)
        acquereurs_a_traiter = analyse.acquereurs_multiples if analyse.acquereurs_multiples else (
            [analyse.acquereur] if analyse.acquereur else []
        )

        if acquereurs_a_traiter:
            if type_acte == 'promesse_vente':
                cle_acquereur = 'beneficiaires'
            else:
                cle_acquereur = 'acquereurs'

            # Si multi-parties, remplacer toute la liste
            if len(acquereurs_a_traiter) > 1:
                donnees_exemple = donnees.get(cle_acquereur, [{}])
                modele_personne = donnees_exemple[0] if donnees_exemple else {}

                nouvelles_personnes = []
                for i, acquereur in enumerate(acquereurs_a_traiter):
                    if i < len(donnees_exemple):
                        personne = copy.deepcopy(donnees_exemple[i])
                        self._fusionner_personne(personne, acquereur)
                    else:
                        personne = copy.deepcopy(modele_personne)
                        self._fusionner_personne(personne, acquereur)
                    nouvelles_personnes.append(personne)

                donnees[cle_acquereur] = nouvelles_personnes
            else:
                # Un seul acquéreur: modifier le premier existant
                if donnees.get(cle_acquereur) and len(donnees[cle_acquereur]) > 0:
                    self._fusionner_personne(donnees[cle_acquereur][0], acquereurs_a_traiter[0])
                else:
                    donnees[cle_acquereur] = acquereurs_a_traiter

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

        # Générer les quotités si multi-parties (v1.2)
        donnees = self._generer_quotites_multi_parties(donnees, type_acte)

        return donnees

    def _generer_quotites_multi_parties(self, donnees: Dict[str, Any], type_acte: str) -> Dict[str, Any]:
        """
        Génère les quotités vendues/acquises pour multi-parties.

        Répartition égale par défaut (ex: 2 vendeurs → 50%/50%).
        """
        import copy

        # Déterminer les clés selon le type d'acte
        if type_acte == 'promesse_vente':
            cle_vendeurs = 'promettants'
            cle_acquereurs = 'beneficiaires'
        else:
            cle_vendeurs = 'vendeurs'
            cle_acquereurs = 'acquereurs'

        vendeurs = donnees.get(cle_vendeurs, [])
        acquereurs = donnees.get(cle_acquereurs, [])

        # Quotités vendues
        if len(vendeurs) > 1 and 'quotites_vendues' not in donnees:
            nb = len(vendeurs)
            quotites = []
            for i, v in enumerate(vendeurs):
                nom = v.get('nom', '')
                prenom = v.get('prenom', v.get('prenoms', ''))
                pp = v.get('personne_physique', {})
                if pp:
                    nom = pp.get('nom', nom)
                    prenom = pp.get('prenom', pp.get('prenoms', prenom))

                quotites.append({
                    'nom': f"{prenom} {nom}".strip(),
                    'pourcentage': round(100 / nb, 2),
                    'fraction': f"1/{nb}",
                    'type_droit': 'pleine propriété'
                })
            donnees['quotites_vendues'] = quotites
            print(f"   📊 Quotités vendues générées: {nb} vendeurs → {100/nb:.1f}% chacun")

        # Quotités acquises
        if len(acquereurs) > 1 and 'quotites_acquises' not in donnees:
            nb = len(acquereurs)
            quotites = []
            for i, a in enumerate(acquereurs):
                nom = a.get('nom', '')
                prenom = a.get('prenom', a.get('prenoms', ''))
                pp = a.get('personne_physique', {})
                if pp:
                    nom = pp.get('nom', nom)
                    prenom = pp.get('prenom', pp.get('prenoms', prenom))

                quotites.append({
                    'nom': f"{prenom} {nom}".strip(),
                    'pourcentage': round(100 / nb, 2),
                    'fraction': f"1/{nb}",
                    'type_droit': 'pleine propriété'
                })
            donnees['quotites_acquises'] = quotites
            print(f"   📊 Quotités acquises générées: {nb} acquéreurs → {100/nb:.1f}% chacun")

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

    # =========================================================================
    # Mode Interactif Q&R (v1.3 - Sprint 3)
    # =========================================================================

    def executer_interactif(
        self,
        type_acte: str = 'promesse_vente',
        prefill: Optional[Dict[str, Any]] = None,
        mode: str = 'cli'
    ) -> ResultatAgent:
        """
        Mode interactif Q&R: collecte les données par questions-réponses.

        Charge le schéma de questions, parcourt les sections,
        pré-remplit depuis les données existantes, puis génère l'acte.

        Args:
            type_acte: 'promesse_vente' ou 'vente'
            prefill: Données pré-remplies (titre extrait, etc.)
            mode: 'cli' (interactif), 'prefill_only' (auto, pas de questions)

        Returns:
            ResultatAgent
        """
        import time
        debut = time.time()
        etapes = ['Initialisation mode Q&R']

        print(f"\n{'='*60}")
        print(f"  AGENT NOTAIRE - Mode Interactif Q&R")
        print(f"  Type: {type_acte}")
        print(f"{'='*60}")

        try:
            collecteur = CollecteurInteractif(type_acte, prefill=prefill)
            etapes.append('Schema questions charge')

            donnees = collecteur.collecter(mode=mode)
            etapes.append('Collecte terminee')

            rapport = collecteur.rapport_json()

            # Valider
            etapes.append('Validation des donnees')
            validation = self.valider_donnees(donnees, type_acte)

            if not validation.valide:
                print(f"\n  Validation echouee: {len(validation.erreurs)} erreur(s)")
                for e in validation.erreurs[:5]:
                    print(f"    - {e}")

                return ResultatAgent(
                    succes=False,
                    message=f"Validation echouee apres collecte Q&R ({len(validation.erreurs)} erreurs)",
                    intention=IntentionAgent.CREER,
                    donnees=donnees
                )

            # Générer
            etapes.append("Generation de l'acte")
            reference = f"{datetime.now().strftime('%Y')}-{datetime.now().strftime('%m%d%H%M')}"
            fichier_sortie = self.project_root / 'outputs' / f'{type_acte}_{reference}.docx'

            if self.orchestrateur:
                try:
                    resultat_wf = self.orchestrateur.generer_acte_complet(
                        type_acte, donnees, str(fichier_sortie)
                    )
                    succes = resultat_wf.statut == "succes"
                except Exception as e:
                    print(f"  Erreur orchestrateur: {e}")
                    succes = False
            else:
                # Mode dégradé: sauvegarder les données
                donnees_path = self.project_root / '.tmp' / 'dossiers' / f'{reference}.json'
                donnees_path.parent.mkdir(parents=True, exist_ok=True)
                donnees_path.write_text(
                    json.dumps(donnees, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                fichier_sortie = donnees_path
                succes = True

            duree = int((time.time() - debut) * 1000)

            return ResultatAgent(
                succes=succes,
                message=f"{'Acte genere' if succes else 'Erreur generation'} via Q&R ({rapport['taux_preremplissage']}% pre-rempli)",
                intention=IntentionAgent.CREER,
                reference=reference,
                fichier_genere=str(fichier_sortie),
                donnees=donnees,
                duree_ms=duree,
                etapes=etapes
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ResultatAgent(
                succes=False,
                message=f"Erreur Q&R: {str(e)}",
                intention=IntentionAgent.CREER
            )

    def executer_depuis_titre(
        self,
        titre_data: Dict[str, Any],
        beneficiaires: Optional[List[Dict]] = None,
        prix: Optional[int] = None,
        mode: str = 'cli'
    ) -> ResultatAgent:
        """
        Génère une promesse depuis les données extraites d'un titre.

        1. Mappe titre → données promesse (vendeur, bien, copropriété)
        2. Pré-remplit avec bénéficiaires et prix si fournis
        3. Lance le Q&R pour les champs manquants
        4. Génère la promesse DOCX

        Args:
            titre_data: Données extraites du titre de propriété
            beneficiaires: Info bénéficiaires (optionnel)
            prix: Prix de vente (optionnel)
            mode: 'cli' ou 'prefill_only'
        """
        print(f"\n{'='*60}")
        print(f"  AGENT NOTAIRE - Titre -> Promesse")
        print(f"{'='*60}")

        prefill = self._mapper_titre_vers_promesse(titre_data, beneficiaires, prix)

        nb_keys = len([k for k in prefill if prefill[k]])
        print(f"  Donnees pre-remplies depuis titre: {nb_keys} sections")

        return self.executer_interactif(
            type_acte='promesse_vente',
            prefill=prefill,
            mode=mode
        )

    def _mapper_titre_vers_promesse(
        self,
        titre: Dict[str, Any],
        beneficiaires: Optional[List[Dict]] = None,
        prix: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Mappe les données d'un titre de propriété vers le format promesse.

        Le titre contient typiquement: vendeur, bien, copropriété, origine.
        Les bénéficiaires et le prix sont fournis séparément.
        """
        promesse: Dict[str, Any] = {}

        # Acte (notaire, date)
        if 'acte' in titre:
            promesse['acte'] = copy.deepcopy(titre['acte'])

        # Promettants = propriétaires du titre (vendeurs)
        for key in ('promettants', 'vendeurs', 'proprietaires'):
            if key in titre and titre[key]:
                promesse['promettants'] = copy.deepcopy(titre[key])
                break

        # Bénéficiaires (fournis séparément ou déjà dans le titre)
        if beneficiaires:
            promesse['beneficiaires'] = copy.deepcopy(beneficiaires)
        else:
            for key in ('beneficiaires', 'acquereurs'):
                if key in titre and titre[key]:
                    promesse['beneficiaires'] = copy.deepcopy(titre[key])
                    break

        # Bien immobilier
        if 'bien' in titre:
            promesse['bien'] = copy.deepcopy(titre['bien'])

        # Copropriété
        if 'copropriete' in titre:
            promesse['copropriete'] = copy.deepcopy(titre['copropriete'])

        # Diagnostics
        if 'diagnostics' in titre:
            promesse['diagnostics'] = copy.deepcopy(titre['diagnostics'])

        # Origine de propriété
        if 'origine_propriete' in titre:
            promesse['origine_propriete'] = copy.deepcopy(titre['origine_propriete'])

        # Prix
        if prix:
            promesse['prix'] = {'montant': prix, 'devise': 'EUR'}
        elif 'prix' in titre:
            promesse['prix'] = copy.deepcopy(titre['prix'])

        # Financement
        if 'financement' in titre:
            promesse['financement'] = copy.deepcopy(titre['financement'])

        # Conditions suspensives
        if 'conditions_suspensives' in titre:
            promesse['conditions_suspensives'] = copy.deepcopy(titre['conditions_suspensives'])
        elif 'condition_suspensive_pret' in titre:
            promesse['condition_suspensive_pret'] = copy.deepcopy(titre['condition_suspensive_pret'])

        # Indemnité d'immobilisation
        if 'indemnite_immobilisation' in titre:
            promesse['indemnite_immobilisation'] = copy.deepcopy(titre['indemnite_immobilisation'])

        # Urbanisme
        if 'urbanisme' in titre:
            promesse['urbanisme'] = copy.deepcopy(titre['urbanisme'])

        # Fiscalité
        if 'fiscalite' in titre:
            promesse['fiscalite'] = copy.deepcopy(titre['fiscalite'])

        # Négociation
        if 'negociation' in titre:
            promesse['negociation'] = copy.deepcopy(titre['negociation'])

        # Délai de réalisation
        if 'delai_realisation' in titre:
            promesse['delai_realisation'] = titre['delai_realisation']

        # RGPD
        if 'rgpd' in titre:
            promesse['rgpd'] = copy.deepcopy(titre['rgpd'])

        # Champs promesse-spécifiques (délais, séquestre, clauses, etc.)
        CHAMPS_PROMESSE = [
            'delais', 'propriete_jouissance', 'meubles', 'sequestre',
            'restitution', 'clause_penale', 'faculte_substitution',
            'provision_frais', 'communication_pieces', 'carence',
            'avenant_eventuel', 'quotites_a_determiner',
            'situation_environnementale', 'travaux_recents',
            'paiement', 'publication', 'avant_contrat', 'jouissance',
            'quotites_vendues', 'quotites_acquises',
        ]
        for champ in CHAMPS_PROMESSE:
            if champ in titre and champ not in promesse:
                promesse[champ] = copy.deepcopy(titre[champ])

        # Aliases vendeurs/acquereurs pour compatibilité validateur
        # Le validateur attend vendeurs/acquereurs, la promesse utilise promettants/beneficiaires
        if 'promettants' in promesse and 'vendeurs' not in promesse:
            promesse['vendeurs'] = promesse['promettants']
        if 'beneficiaires' in promesse and 'acquereurs' not in promesse:
            promesse['acquereurs'] = promesse['beneficiaires']

        return promesse


# =============================================================================
# Collecteur Interactif Q&R (v1.3 - Sprint 3)
# =============================================================================

class CollecteurInteractif:
    """
    Collecteur interactif de données par questions-réponses.

    Charge les questions depuis les schémas JSON et guide l'utilisateur
    section par section. Supporte le pré-remplissage depuis un titre
    de propriété extrait ou des données existantes.

    Usage:
        collecteur = CollecteurInteractif('promesse_vente', prefill=titre_data)
        donnees = collecteur.collecter(mode='cli')

    Modes:
        - 'cli': interactif avec input() pour chaque question manquante
        - 'prefill_only': utilise uniquement les données pré-remplies + défauts
    """

    # Mapping singulier (schema) → pluriel (données pipeline)
    PLURIELS = {
        'promettant': 'promettants',
        'beneficiaire': 'beneficiaires',
        'vendeur': 'vendeurs',
        'acquereur': 'acquereurs',
    }

    SCHEMAS = {
        'promesse_vente': 'questions_promesse_vente.json',
        'vente': 'questions_notaire.json',
    }

    def __init__(self, type_acte: str, prefill: Optional[Dict[str, Any]] = None):
        self.type_acte = type_acte
        self.prefill = prefill or {}
        self.donnees = copy.deepcopy(self.prefill)
        self.questions_posees = 0
        self.questions_preremplies = 0
        self.questions_ignorees = 0
        self._compteurs_repeter: Dict[str, int] = {}

        schema_nom = self.SCHEMAS.get(type_acte)
        if not schema_nom:
            raise ValueError(f"Type d'acte non supporte pour Q&R: {type_acte}. "
                             f"Supportes: {list(self.SCHEMAS.keys())}")

        schema_path = PROJECT_ROOT / 'schemas' / schema_nom
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema Q&R introuvable: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)

    def collecter(
        self,
        mode: str = 'cli',
        sections_a_ignorer: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Collecte les données section par section.

        Args:
            mode: 'cli' ou 'prefill_only'
            sections_a_ignorer: Clés de sections à sauter

        Returns:
            Dictionnaire de données complet pour le pipeline
        """
        sections = self.schema.get('sections', {})
        ignorer = set(sections_a_ignorer or [])

        print(f"\n{'='*60}")
        print(f"  COLLECTE - {self.schema.get('titre', self.type_acte)}")
        print(f"{'='*60}")

        if self.prefill:
            nb = len([k for k in self.prefill if self.prefill[k]])
            print(f"  Donnees pre-remplies: {nb} sections detectees")
            print(f"  Les champs deja renseignes seront auto-valides\n")

        for section_key in sorted(sections.keys()):
            if section_key in ignorer:
                continue

            section = sections[section_key]

            # Ignorer les sections conditionnelles non applicables
            condition = section.get('condition', '')
            if condition and not self._evaluer_condition_section(condition):
                continue

            self._traiter_section(section_key, section, mode)

        self._afficher_rapport()
        return self.donnees

    def _traiter_section(self, key: str, section: Dict, mode: str):
        """Traite une section complète de questions."""
        titre = section.get('titre', key)
        questions = section.get('questions', [])

        if not questions:
            return

        print(f"\n{'─'*50}")
        print(f"  [{key}] {titre}")
        print(f"{'─'*50}")

        # Pré-scan: identifier les compteurs pour les questions répétées
        self._prescan_compteurs(questions, mode)

        for q in questions:
            q_id = q.get('id', '')
            repeter = q.get('repeter', '')

            # Skip les compteurs déjà traités par le pre-scan
            if '_nombre' in q_id and q.get('type') == 'nombre' and q.get('minimum', 0) >= 1:
                continue

            if repeter and repeter in self._compteurs_repeter:
                count = self._compteurs_repeter[repeter]
                group_label = repeter.replace('par_', '')
                for idx in range(count):
                    if count > 1:
                        print(f"\n    --- {group_label} {idx+1}/{count} ---")
                    self._traiter_question(q, mode, index=idx)
            else:
                self._traiter_question(q, mode)

    def _prescan_compteurs(self, questions: List[Dict], mode: str = 'cli'):
        """Pré-scanne les questions de comptage (nombre de parties, lots, etc.)."""
        for q in questions:
            q_id = q.get('id', '')
            if '_nombre' not in q_id or q.get('type') != 'nombre':
                continue
            if q.get('minimum', 0) < 1:
                continue

            group = q_id.replace('_nombre', '')
            repeter_key = f'par_{group}'

            # Déjà compté?
            if repeter_key in self._compteurs_repeter:
                continue

            # Vérifier depuis les données pré-remplies (top-level et nested)
            prefill_key = self.PLURIELS.get(group, group + 's')
            prefill_list = self.donnees.get(prefill_key, [])

            # Aussi checker les listes imbriquées (ex: bien.lots)
            if not prefill_list:
                for parent_key in ('bien', 'copropriete', 'diagnostics'):
                    parent = self.donnees.get(parent_key, {})
                    if isinstance(parent, dict) and prefill_key in parent:
                        nested = parent[prefill_key]
                        if isinstance(nested, list) and nested:
                            prefill_list = nested
                            break

            if prefill_list and isinstance(prefill_list, list):
                count = len(prefill_list)
                self._compteurs_repeter[repeter_key] = count
                print(f"  [OK] Nombre de {group}s: {count}")
                self.questions_preremplies += 1
            elif mode == 'prefill_only':
                # Mode auto: utiliser 1 par défaut
                self._compteurs_repeter[repeter_key] = 1
                self.questions_ignorees += 1
            else:
                # Demander le nombre
                q_text = q.get('question', f"Combien de {group}s ?")
                rep = input(f"  {q_text}: ").strip()
                count = int(rep) if rep.isdigit() and int(rep) >= 1 else 1
                self._compteurs_repeter[repeter_key] = count
                self.questions_posees += 1

                # Initialiser la liste
                if prefill_key not in self.donnees:
                    self.donnees[prefill_key] = [{} for _ in range(count)]

    def _traiter_question(
        self,
        question: Dict,
        mode: str,
        index: Optional[int] = None
    ) -> Any:
        """Traite une question individuelle."""
        variable = question.get('variable', '')
        q_text = question.get('question', '?')
        defaut = question.get('defaut', None)

        # Vérifier pré-remplissage
        if variable:
            chemin = self._parse_variable(variable, index)
            valeur_existante = self._get_deep(self.donnees, chemin)
            if valeur_existante is not None:
                self.questions_preremplies += 1
                affichage = str(valeur_existante)
                if len(affichage) > 60:
                    affichage = affichage[:57] + '...'
                print(f"  [OK] {q_text} -> {affichage}")

                # Traiter les sous-questions même si pré-rempli
                self._traiter_sous_questions(question, valeur_existante, mode, index)
                return valeur_existante

        # Poser la question ou utiliser le défaut
        if mode == 'prefill_only':
            if defaut is not None:
                reponse = defaut
                if variable:
                    chemin = self._parse_variable(variable, index)
                    self._set_deep(self.donnees, chemin, reponse)
                self.questions_preremplies += 1
            else:
                self.questions_ignorees += 1
                return None
        else:
            reponse = self._poser_question_cli(question)
            self.questions_posees += 1

            if reponse is not None and variable:
                chemin = self._parse_variable(variable, index)
                self._set_deep(self.donnees, chemin, reponse)

        # Traiter les sous-questions
        self._traiter_sous_questions(question, reponse, mode, index)
        return reponse

    def _traiter_sous_questions(
        self,
        question: Dict,
        reponse: Any,
        mode: str,
        index: Optional[int]
    ):
        """Traite les sous-questions conditionnelles."""
        sous_questions = question.get('sous_questions', {})
        if not isinstance(sous_questions, dict) or reponse is None:
            return

        for condition_key, sq_list in sous_questions.items():
            if self._evaluer_condition_reponse(condition_key, reponse):
                for sq in sq_list:
                    self._traiter_question(sq, mode, index)

    def _parse_variable(self, variable: str, index: Optional[int] = None) -> List:
        """
        Parse un chemin de variable schema en chemin de données.

        'promettant[].nom' + index=0 → ['promettants', 0, 'nom']
        'bien.adresse.numero'        → ['bien', 'adresse', 'numero']
        'prix.montant'               → ['prix', 'montant']
        'bien.lots[].numero' + idx=1 → ['bien', 'lots', 1, 'numero']
        """
        parts = variable.split('.')
        result = []

        for part in parts:
            if '[]' in part:
                base = part.replace('[]', '')
                # Mapper singulier → pluriel si applicable
                plural = self.PLURIELS.get(base, base)
                result.append(plural)
                result.append(index if index is not None else 0)
            else:
                result.append(part)

        return result

    def _get_deep(self, data: Any, path: List) -> Any:
        """Récupère une valeur profonde dans un dict/list imbriqué."""
        current = data
        for key in path:
            if isinstance(key, int):
                if isinstance(current, list) and key < len(current):
                    current = current[key]
                else:
                    return None
            elif isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

    def _set_deep(self, data: Dict, path: List, value: Any):
        """Définit une valeur profonde dans un dict/list imbriqué."""
        current = data
        for i, key in enumerate(path[:-1]):
            next_key = path[i + 1]
            if isinstance(key, int):
                while isinstance(current, list) and len(current) <= key:
                    current.append({})
                if isinstance(current, list):
                    current = current[key]
            else:
                if key not in current:
                    if isinstance(next_key, int):
                        current[key] = []
                    else:
                        current[key] = {}
                current = current[key]

        final = path[-1]
        if isinstance(final, int):
            while isinstance(current, list) and len(current) <= final:
                current.append(None)
            if isinstance(current, list):
                current[final] = value
        else:
            current[final] = value

    def _poser_question_cli(self, question: Dict) -> Any:
        """Pose une question en CLI avec input()."""
        q_text = question.get('question', '?')
        q_type = question.get('type', 'texte')
        defaut = question.get('defaut', None)
        options = question.get('options', [])

        if q_type in ('choix', 'choix_unique') and options:
            print(f"  {q_text}")
            for i, opt in enumerate(options, 1):
                marker = '*' if defaut and opt == defaut else ' '
                print(f"   {marker}{i}. {opt}")
            prompt = f"  > Choix (1-{len(options)})"
            if defaut:
                idx_defaut = next((i for i, o in enumerate(options, 1) if o == defaut), '')
                prompt += f" [{idx_defaut}]"
            rep = input(f"{prompt}: ").strip()
            if rep.isdigit() and 1 <= int(rep) <= len(options):
                return options[int(rep) - 1]
            return defaut or (options[0] if options else None)

        elif q_type == 'booleen':
            default_str = 'O' if defaut else 'N'
            rep = input(f"  {q_text} (O/N) [{default_str}]: ").strip().lower()
            if rep in ('o', 'oui', 'y', 'yes', '1'):
                return True
            elif rep in ('n', 'non', 'no', '0'):
                return False
            return defaut if defaut is not None else False

        elif q_type in ('nombre', 'nombre_decimal'):
            prompt = f"  {q_text}"
            if defaut is not None:
                prompt += f" [{defaut}]"
            rep = input(f"{prompt}: ").strip()
            try:
                val = float(rep.replace(',', '.'))
                return int(val) if q_type == 'nombre' else val
            except ValueError:
                if defaut is not None:
                    return int(defaut) if q_type == 'nombre' else float(defaut)
                return None

        else:  # texte, date, publication, contact, texte_long, etc.
            prompt = f"  {q_text}"
            if defaut is not None:
                prompt += f" [{defaut}]"
            rep = input(f"{prompt}: ").strip()
            return rep if rep else (str(defaut) if defaut is not None else None)

    def _evaluer_condition_reponse(self, condition_key: str, valeur: Any) -> bool:
        """Évalue si une sous-condition est satisfaite."""
        ck = condition_key.lower()
        if ck == 'si_oui' and valeur is True:
            return True
        if ck == 'si_non' and valeur is False:
            return True
        if ck == 'si_marie' and isinstance(valeur, str) and 'marié' in valeur.lower():
            return True
        if ck == 'si_pacse' and isinstance(valeur, str) and 'pacsé' in valeur.lower():
            return True
        if ck.startswith('si_superieur_a_'):
            try:
                seuil = int(ck.split('_')[-1])
                return isinstance(valeur, (int, float)) and valeur > seuil
            except ValueError:
                pass
        return False

    def _evaluer_condition_section(self, condition: str) -> bool:
        """Évalue une condition de section (ex: 'mobilier.existe == true')."""
        try:
            match = re.match(r'([\w.]+)\s*(==|!=|>|<)\s*(.+)', condition)
            if not match:
                return True

            var_path, op, val_attendue = match.groups()
            val_attendue = val_attendue.strip().strip("'\"")
            chemin = var_path.split('.')
            val_actuelle = self._get_deep(self.donnees, chemin)

            if val_actuelle is None:
                return False

            if op == '==':
                return str(val_actuelle).lower() == val_attendue.lower()
            elif op == '!=':
                return str(val_actuelle).lower() != val_attendue.lower()
            elif op == '>':
                return float(val_actuelle) > float(val_attendue)
            elif op == '<':
                return float(val_actuelle) < float(val_attendue)
        except Exception:
            pass
        return True

    def _afficher_rapport(self):
        """Affiche le rapport de collecte."""
        total = self.questions_posees + self.questions_preremplies + self.questions_ignorees
        print(f"\n{'='*60}")
        print(f"  RAPPORT DE COLLECTE")
        print(f"{'='*60}")
        print(f"  Questions pre-remplies : {self.questions_preremplies}")
        print(f"  Questions posees       : {self.questions_posees}")
        print(f"  Questions ignorees     : {self.questions_ignorees}")
        print(f"  Total                  : {total}")
        if total > 0:
            pct = (self.questions_preremplies / total) * 100
            print(f"  Taux pre-remplissage   : {pct:.0f}%")
        print(f"{'='*60}")

    def rapport_json(self) -> Dict[str, Any]:
        """Retourne le rapport sous forme de dict."""
        total = self.questions_posees + self.questions_preremplies + self.questions_ignorees
        return {
            'questions_preremplies': self.questions_preremplies,
            'questions_posees': self.questions_posees,
            'questions_ignorees': self.questions_ignorees,
            'total': total,
            'taux_preremplissage': round(
                (self.questions_preremplies / total) * 100
            ) if total > 0 else 0
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Agent Autonome NotaireAI v1.3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Créer une promesse (langage naturel)
  python agent_autonome.py creer "Promesse Martin→Dupont, appart 67m² Paris, 450000€"

  # Mode interactif Q&R (questions guidées)
  python agent_autonome.py interactif-qr --type promesse_vente
  python agent_autonome.py interactif-qr --type promesse_vente --prefill titre.json

  # Demo: titre → promesse (avec pré-remplissage)
  python agent_autonome.py demo --titre donnees.json --prix 450000

  # Modifier un acte existant
  python agent_autonome.py modifier "Changer le prix à 460000€ dans le dossier 2026-001"

  # Mode interactif libre
  python agent_autonome.py
        """
    )

    parser.add_argument('commande', nargs='?', default='interactif',
                        choices=['creer', 'modifier', 'rechercher', 'generer',
                                 'lister', 'aide', 'interactif',
                                 'interactif-qr', 'demo'],
                        help='Commande à exécuter')
    parser.add_argument('demande', nargs='*', help='Demande en langage naturel')
    parser.add_argument('--type', '-t', default='promesse_vente',
                        choices=['promesse_vente', 'vente'],
                        help="Type d'acte pour le mode Q&R (defaut: promesse_vente)")
    parser.add_argument('--prefill', '-p', type=str, default=None,
                        help='Fichier JSON de pre-remplissage (titre extrait, etc.)')
    parser.add_argument('--titre', type=str, default=None,
                        help='Fichier JSON du titre de propriete (mode demo)')
    parser.add_argument('--prix', type=int, default=None,
                        help='Prix de vente en euros (mode demo)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Fichier de sortie JSON (sauvegarde des donnees collectees)')
    parser.add_argument('--auto', action='store_true',
                        help='Mode automatique sans questions (prefill + defauts uniquement)')

    args = parser.parse_args()

    agent = AgentNotaire()

    if args.commande == 'interactif-qr':
        # ─── Mode Q&R interactif ───
        prefill = None
        if args.prefill:
            prefill_path = Path(args.prefill)
            if prefill_path.exists():
                with open(prefill_path, 'r', encoding='utf-8') as f:
                    prefill = json.load(f)
                print(f"  Pre-remplissage depuis: {prefill_path}")
            else:
                print(f"  Fichier prefill introuvable: {prefill_path}")

        mode = 'prefill_only' if args.auto else 'cli'
        resultat = agent.executer_interactif(
            type_acte=args.type,
            prefill=prefill,
            mode=mode
        )

        # Sauvegarder les données collectées
        if resultat.donnees and args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(resultat.donnees, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            print(f"  Donnees sauvegardees: {output_path}")

    elif args.commande == 'demo':
        # ─── Mode demo: titre → Q&R → promesse ───
        titre_data = {}
        if args.titre:
            titre_path = Path(args.titre)
            if titre_path.exists():
                with open(titre_path, 'r', encoding='utf-8') as f:
                    titre_data = json.load(f)
                print(f"  Titre charge: {titre_path}")
            else:
                print(f"  Fichier titre introuvable: {titre_path}")
                return 1

        mode = 'prefill_only' if args.auto else 'cli'
        resultat = agent.executer_depuis_titre(
            titre_data=titre_data,
            prix=args.prix,
            mode=mode
        )

        if resultat.donnees and args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(resultat.donnees, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            print(f"  Donnees sauvegardees: {output_path}")

    elif args.commande == 'interactif' or not args.demande:
        # ─── Mode interactif libre (NL) ───
        print("\n  Agent NotaireAI v1.3 - Mode interactif")
        print("   Commandes: 'aide', 'qr' (mode Q&R), 'q' (quitter)\n")

        while True:
            try:
                demande = input(">>> ").strip()

                if demande.lower() in ('q', 'quit', 'exit'):
                    print("Au revoir!")
                    break

                if demande.lower() in ('qr', 'q&r', 'interactif-qr'):
                    print("  Lancement du mode Q&R...")
                    agent.executer_interactif(type_acte='promesse_vente', mode='cli')
                    continue

                if not demande:
                    continue

                agent.executer(demande)

            except KeyboardInterrupt:
                print("\nAu revoir!")
                break
            except EOFError:
                break
    else:
        # ─── Mode commande directe ───
        demande_complete = ' '.join(args.demande)

        if args.commande not in demande_complete.lower():
            demande_complete = f"{args.commande} {demande_complete}"

        agent.executer(demande_complete)


if __name__ == '__main__':
    main()
