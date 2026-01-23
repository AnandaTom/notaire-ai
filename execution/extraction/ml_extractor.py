# -*- coding: utf-8 -*-
"""
Machine Learning pour améliorer l'extraction des titres de propriété.

Ce module implémente:
- Apprentissage des patterns à partir des extractions validées
- Analyse de fréquence pour corriger les erreurs courantes
- Scoring de confiance amélioré
- Détection d'anomalies
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import Counter, defaultdict
import logging
import re

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

# Chemin vers la base d'apprentissage
MODULE_DIR = Path(__file__).parent
DATA_DIR = MODULE_DIR.parent.parent / '.tmp' / 'ml_data'


@dataclass
class ExtractionValidee:
    """Une extraction validée par un notaire."""
    id: str
    date_validation: str
    champ: str  # Ex: "notaire.nom", "bien.adresse.code_postal"
    valeur_extraite: Any
    valeur_corrigee: Optional[Any]  # None si extraction correcte
    contexte: str  # Texte source autour de l'extraction
    pattern_utilise: str
    est_correcte: bool


@dataclass
class PatternAppris:
    """Un pattern appris à partir des extractions."""
    pattern: str
    champ: str
    nb_succes: int = 0
    nb_echecs: int = 0
    derniere_utilisation: str = ""
    exemples_succes: List[str] = field(default_factory=list)
    exemples_echecs: List[str] = field(default_factory=list)

    @property
    def taux_succes(self) -> float:
        total = self.nb_succes + self.nb_echecs
        return self.nb_succes / total if total > 0 else 0.0


@dataclass
class CorrectionFrequente:
    """Une correction fréquemment appliquée."""
    valeur_incorrecte: str
    valeur_correcte: str
    champ: str
    nb_occurrences: int = 0


class BaseApprentissage:
    """Base de données des apprentissages."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.fichier_extractions = self.data_dir / 'extractions_validees.json'
        self.fichier_patterns = self.data_dir / 'patterns_appris.json'
        self.fichier_corrections = self.data_dir / 'corrections_frequentes.json'
        self.fichier_stats = self.data_dir / 'stats_extraction.json'

        self._charger_donnees()

    def _charger_donnees(self):
        """Charge les données depuis les fichiers JSON."""
        # Extractions validées
        if self.fichier_extractions.exists():
            data = json.loads(self.fichier_extractions.read_text(encoding='utf-8'))
            self.extractions = [ExtractionValidee(**e) for e in data]
        else:
            self.extractions = []

        # Patterns appris
        if self.fichier_patterns.exists():
            data = json.loads(self.fichier_patterns.read_text(encoding='utf-8'))
            self.patterns = [PatternAppris(**p) for p in data]
        else:
            self.patterns = []

        # Corrections fréquentes
        if self.fichier_corrections.exists():
            data = json.loads(self.fichier_corrections.read_text(encoding='utf-8'))
            self.corrections = [CorrectionFrequente(**c) for c in data]
        else:
            self.corrections = []

        # Statistiques
        if self.fichier_stats.exists():
            self.stats = json.loads(self.fichier_stats.read_text(encoding='utf-8'))
        else:
            self.stats = {
                'total_extractions': 0,
                'extractions_correctes': 0,
                'par_champ': {}
            }

    def sauvegarder(self):
        """Sauvegarde les données dans les fichiers JSON."""
        # Extractions
        data = [asdict(e) for e in self.extractions]
        self.fichier_extractions.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Patterns
        data = [asdict(p) for p in self.patterns]
        self.fichier_patterns.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Corrections
        data = [asdict(c) for c in self.corrections]
        self.fichier_corrections.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # Stats
        self.fichier_stats.write_text(
            json.dumps(self.stats, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def ajouter_extraction(self, extraction: ExtractionValidee):
        """Ajoute une extraction validée."""
        self.extractions.append(extraction)

        # Mettre à jour les stats
        self.stats['total_extractions'] += 1
        if extraction.est_correcte:
            self.stats['extractions_correctes'] += 1

        # Stats par champ
        if extraction.champ not in self.stats['par_champ']:
            self.stats['par_champ'][extraction.champ] = {
                'total': 0, 'correctes': 0
            }
        self.stats['par_champ'][extraction.champ]['total'] += 1
        if extraction.est_correcte:
            self.stats['par_champ'][extraction.champ]['correctes'] += 1

        # Mettre à jour les patterns
        self._mettre_a_jour_pattern(extraction)

        # Mettre à jour les corrections fréquentes
        if not extraction.est_correcte:
            self._ajouter_correction(extraction)

        self.sauvegarder()

    def _mettre_a_jour_pattern(self, extraction: ExtractionValidee):
        """Met à jour le pattern utilisé."""
        pattern_existant = next(
            (p for p in self.patterns
             if p.pattern == extraction.pattern_utilise and p.champ == extraction.champ),
            None
        )

        if pattern_existant:
            if extraction.est_correcte:
                pattern_existant.nb_succes += 1
                if len(pattern_existant.exemples_succes) < 10:
                    pattern_existant.exemples_succes.append(extraction.contexte[:200])
            else:
                pattern_existant.nb_echecs += 1
                if len(pattern_existant.exemples_echecs) < 10:
                    pattern_existant.exemples_echecs.append(extraction.contexte[:200])
            pattern_existant.derniere_utilisation = datetime.now().isoformat()
        else:
            nouveau_pattern = PatternAppris(
                pattern=extraction.pattern_utilise,
                champ=extraction.champ,
                nb_succes=1 if extraction.est_correcte else 0,
                nb_echecs=0 if extraction.est_correcte else 1,
                derniere_utilisation=datetime.now().isoformat(),
                exemples_succes=[extraction.contexte[:200]] if extraction.est_correcte else [],
                exemples_echecs=[extraction.contexte[:200]] if not extraction.est_correcte else []
            )
            self.patterns.append(nouveau_pattern)

    def _ajouter_correction(self, extraction: ExtractionValidee):
        """Ajoute une correction fréquente."""
        if extraction.valeur_corrigee is None:
            return

        val_incorrecte = str(extraction.valeur_extraite)
        val_correcte = str(extraction.valeur_corrigee)

        correction_existante = next(
            (c for c in self.corrections
             if c.valeur_incorrecte == val_incorrecte
             and c.champ == extraction.champ),
            None
        )

        if correction_existante:
            correction_existante.nb_occurrences += 1
            # Mettre à jour si la correction est différente
            if correction_existante.valeur_correcte != val_correcte:
                # Garder la plus fréquente
                logger.warning(
                    f"Correction conflictuelle pour '{val_incorrecte}': "
                    f"'{correction_existante.valeur_correcte}' vs '{val_correcte}'"
                )
        else:
            self.corrections.append(CorrectionFrequente(
                valeur_incorrecte=val_incorrecte,
                valeur_correcte=val_correcte,
                champ=extraction.champ,
                nb_occurrences=1
            ))


class MLExtractor:
    """Extracteur utilisant l'apprentissage machine."""

    def __init__(self, base: Optional[BaseApprentissage] = None):
        self.base = base or BaseApprentissage()

    def obtenir_confiance_pattern(self, pattern: str, champ: str) -> float:
        """
        Calcule la confiance d'un pattern basée sur l'historique.

        Args:
            pattern: Le pattern regex
            champ: Le champ extrait

        Returns:
            Score de confiance entre 0 et 1
        """
        pattern_appris = next(
            (p for p in self.base.patterns
             if p.pattern == pattern and p.champ == champ),
            None
        )

        if pattern_appris:
            # Score basé sur le taux de succès historique
            return pattern_appris.taux_succes
        else:
            # Pattern inconnu: confiance par défaut
            return 0.5

    def corriger_valeur(self, valeur: Any, champ: str) -> Tuple[Any, bool]:
        """
        Corrige une valeur si une correction fréquente existe.

        Args:
            valeur: La valeur extraite
            champ: Le champ concerné

        Returns:
            Tuple (valeur_corrigee, a_ete_corrigee)
        """
        val_str = str(valeur)

        correction = next(
            (c for c in self.base.corrections
             if c.valeur_incorrecte == val_str and c.champ == champ),
            None
        )

        if correction and correction.nb_occurrences >= 2:
            logger.info(f"Correction automatique: '{val_str}' → '{correction.valeur_correcte}'")
            return correction.valeur_correcte, True

        return valeur, False

    def calculer_score_confiance(
        self,
        extractions: Dict[str, Any],
        patterns_utilises: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Calcule un score de confiance pour chaque extraction.

        Args:
            extractions: Dict des valeurs extraites par champ
            patterns_utilises: Dict des patterns utilisés par champ

        Returns:
            Dict des scores de confiance par champ
        """
        scores = {}

        for champ, valeur in extractions.items():
            pattern = patterns_utilises.get(champ, '')

            # Score de base du pattern
            score_pattern = self.obtenir_confiance_pattern(pattern, champ)

            # Bonus si valeur non vide
            score_valeur = 0.2 if valeur else 0.0

            # Bonus si format attendu
            score_format = self._verifier_format(valeur, champ)

            # Score final pondéré
            score_final = (
                score_pattern * 0.5 +
                score_valeur * 0.2 +
                score_format * 0.3
            )

            scores[champ] = min(1.0, max(0.0, score_final))

        return scores

    def _verifier_format(self, valeur: Any, champ: str) -> float:
        """Vérifie si la valeur a le format attendu."""
        if valeur is None:
            return 0.0

        val_str = str(valeur)

        # Formats par type de champ
        formats = {
            'code_postal': r'^\d{5}$',
            'date': r'\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{1,2}\s+[a-zéèêë]+\s+\d{4}',
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'telephone': r'^0\d{9}$|^\+33\d{9}$',
            'crpcen': r'^\d+$',
            'prix': r'^\d+(?:[,\.]\d+)?$',
        }

        for type_champ, pattern in formats.items():
            if type_champ in champ.lower():
                if re.match(pattern, val_str, re.IGNORECASE):
                    return 1.0
                else:
                    return 0.3

        # Format inconnu: score neutre
        return 0.5

    def detecter_anomalies(
        self,
        extraction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Détecte les anomalies dans une extraction.

        Args:
            extraction: Dict des valeurs extraites

        Returns:
            Liste des anomalies détectées
        """
        anomalies = []

        # Règles de validation
        regles = [
            # Prix cohérent
            {
                'condition': lambda e: e.get('prix', {}).get('montant_total', 0) < 1000,
                'message': "Prix anormalement bas (< 1000€)",
                'champ': 'prix.montant_total',
                'severite': 'warning'
            },
            {
                'condition': lambda e: e.get('prix', {}).get('montant_total', 0) > 50000000,
                'message': "Prix anormalement élevé (> 50M€)",
                'champ': 'prix.montant_total',
                'severite': 'warning'
            },
            # Date cohérente
            {
                'condition': lambda e: self._date_future(e.get('date_acte')),
                'message': "Date de l'acte dans le futur",
                'champ': 'date_acte',
                'severite': 'error'
            },
            # Tantièmes cohérents
            {
                'condition': lambda e: self._tantiemes_invalides(e.get('bien', {}).get('lots', [])),
                'message': "Tantièmes incohérents (somme > base)",
                'champ': 'bien.lots',
                'severite': 'error'
            },
            # Code postal valide
            {
                'condition': lambda e: not self._code_postal_valide(
                    e.get('bien', {}).get('adresse', {}).get('code_postal')
                ),
                'message': "Code postal invalide",
                'champ': 'bien.adresse.code_postal',
                'severite': 'warning'
            },
        ]

        for regle in regles:
            try:
                if regle['condition'](extraction):
                    anomalies.append({
                        'champ': regle['champ'],
                        'message': regle['message'],
                        'severite': regle['severite']
                    })
            except Exception:
                pass  # Ignorer les erreurs de validation

        return anomalies

    def _date_future(self, date_str: Optional[str]) -> bool:
        """Vérifie si une date est dans le futur."""
        if not date_str:
            return False
        # Extraction simple de l'année
        match = re.search(r'(\d{4})', str(date_str))
        if match:
            annee = int(match.group(1))
            return annee > datetime.now().year
        return False

    def _tantiemes_invalides(self, lots: List[Dict]) -> bool:
        """Vérifie si les tantièmes sont cohérents."""
        if not lots:
            return False

        for lot in lots:
            tantiemes = lot.get('tantiemes', {})
            valeur = tantiemes.get('valeur', 0)
            base = tantiemes.get('base', 10000)
            if valeur > base:
                return True
        return False

    def _code_postal_valide(self, code: Optional[str]) -> bool:
        """Vérifie si un code postal français est valide."""
        if not code:
            return True  # Pas d'erreur si absent
        return bool(re.match(r'^\d{5}$', str(code)))

    def suggerer_ameliorations(self) -> List[Dict[str, Any]]:
        """
        Suggère des améliorations basées sur les données d'apprentissage.

        Returns:
            Liste de suggestions d'amélioration
        """
        suggestions = []

        # Patterns avec mauvais taux de succès
        for pattern in self.base.patterns:
            if pattern.taux_succes < 0.7 and (pattern.nb_succes + pattern.nb_echecs) >= 5:
                suggestions.append({
                    'type': 'pattern_faible',
                    'pattern': pattern.pattern,
                    'champ': pattern.champ,
                    'taux_succes': pattern.taux_succes,
                    'suggestion': f"Améliorer le pattern pour '{pattern.champ}' (taux: {pattern.taux_succes:.0%})"
                })

        # Champs avec beaucoup de corrections
        corrections_par_champ = defaultdict(int)
        for correction in self.base.corrections:
            corrections_par_champ[correction.champ] += correction.nb_occurrences

        for champ, nb_corrections in corrections_par_champ.items():
            if nb_corrections >= 5:
                suggestions.append({
                    'type': 'corrections_frequentes',
                    'champ': champ,
                    'nb_corrections': nb_corrections,
                    'suggestion': f"Revoir l'extraction de '{champ}' ({nb_corrections} corrections)"
                })

        # Champs avec faible taux de succès global
        for champ, stats in self.base.stats.get('par_champ', {}).items():
            if stats['total'] >= 10:
                taux = stats['correctes'] / stats['total']
                if taux < 0.8:
                    suggestions.append({
                        'type': 'champ_problematique',
                        'champ': champ,
                        'taux_succes': taux,
                        'suggestion': f"Améliorer l'extraction de '{champ}' (taux: {taux:.0%})"
                    })

        return suggestions

    def valider_extraction(
        self,
        extraction_id: str,
        champ: str,
        valeur_extraite: Any,
        valeur_corrigee: Optional[Any],
        contexte: str,
        pattern_utilise: str
    ):
        """
        Enregistre une validation d'extraction (feedback du notaire).

        Args:
            extraction_id: ID unique de l'extraction
            champ: Champ concerné
            valeur_extraite: Valeur extraite automatiquement
            valeur_corrigee: Valeur corrigée par le notaire (None si correcte)
            contexte: Texte source
            pattern_utilise: Pattern regex utilisé
        """
        extraction = ExtractionValidee(
            id=extraction_id,
            date_validation=datetime.now().isoformat(),
            champ=champ,
            valeur_extraite=valeur_extraite,
            valeur_corrigee=valeur_corrigee,
            contexte=contexte,
            pattern_utilise=pattern_utilise,
            est_correcte=(valeur_corrigee is None)
        )

        self.base.ajouter_extraction(extraction)

    def obtenir_statistiques(self) -> Dict[str, Any]:
        """Retourne les statistiques d'extraction."""
        stats = self.base.stats.copy()

        # Calculer le taux de succès global
        if stats['total_extractions'] > 0:
            stats['taux_succes_global'] = (
                stats['extractions_correctes'] / stats['total_extractions']
            )
        else:
            stats['taux_succes_global'] = 0.0

        # Ajouter les stats des patterns
        stats['patterns'] = {
            'total': len(self.base.patterns),
            'efficaces': len([p for p in self.base.patterns if p.taux_succes >= 0.8]),
            'a_ameliorer': len([p for p in self.base.patterns if p.taux_succes < 0.7])
        }

        # Ajouter les stats des corrections
        stats['corrections'] = {
            'total': len(self.base.corrections),
            'frequentes': len([c for c in self.base.corrections if c.nb_occurrences >= 3])
        }

        return stats


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='ML pour extraction de titres')
    parser.add_argument('--stats', action='store_true', help='Afficher les statistiques')
    parser.add_argument('--suggestions', action='store_true', help='Afficher les suggestions')
    parser.add_argument('--reset', action='store_true', help='Réinitialiser la base')

    args = parser.parse_args()

    ml = MLExtractor()

    if args.reset:
        import shutil
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR)
        print("✅ Base d'apprentissage réinitialisée")

    elif args.stats:
        stats = ml.obtenir_statistiques()
        print("\n📊 Statistiques d'extraction:")
        print(f"  - Total extractions: {stats['total_extractions']}")
        print(f"  - Taux de succès: {stats['taux_succes_global']:.1%}")
        print(f"\n📈 Patterns:")
        print(f"  - Total: {stats['patterns']['total']}")
        print(f"  - Efficaces (≥80%): {stats['patterns']['efficaces']}")
        print(f"  - À améliorer (<70%): {stats['patterns']['a_ameliorer']}")
        print(f"\n🔧 Corrections:")
        print(f"  - Total: {stats['corrections']['total']}")
        print(f"  - Fréquentes (≥3x): {stats['corrections']['frequentes']}")

    elif args.suggestions:
        suggestions = ml.suggerer_ameliorations()
        if suggestions:
            print("\n💡 Suggestions d'amélioration:")
            for s in suggestions:
                print(f"\n  [{s['type']}] {s['suggestion']}")
        else:
            print("\n✅ Aucune amélioration suggérée")

    else:
        parser.print_help()
