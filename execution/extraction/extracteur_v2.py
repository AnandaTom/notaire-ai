# -*- coding: utf-8 -*-
"""
Extracteur v2 - Module d'extraction avancée des titres de propriété.

Combine:
- Patterns regex avancés
- OCR pour PDF scannés
- Machine Learning pour améliorer l'extraction

Usage:
    python extracteur_v2.py -i document.pdf -o resultat.json -v
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import logging
import argparse

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import des modules locaux
from .patterns_avances import PatternsAvances, PatternResult
from .ocr_processor import OCRProcessor, OCRResult
from .ml_extractor import MLExtractor, BaseApprentissage

logger = logging.getLogger(__name__)

# Chemins
MODULE_DIR = Path(__file__).parent
PROJECT_ROOT = MODULE_DIR.parent.parent


@dataclass
class ResultatExtraction:
    """Résultat complet d'une extraction."""
    reference: str
    source: Dict[str, Any]
    date_acte: Optional[str]
    notaire: Optional[Dict[str, Any]]
    publication: Optional[Dict[str, Any]]
    vendeurs_originaux: List[Dict[str, Any]]
    proprietaires_actuels: List[Dict[str, Any]]
    bien: Dict[str, Any]
    prix: Optional[Dict[str, Any]]
    copropriete: Optional[Dict[str, Any]]
    origine_propriete: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


class ExtracteurV2:
    """Extracteur avancé de titres de propriété."""

    def __init__(
        self,
        utiliser_ocr: bool = True,
        utiliser_ml: bool = True,
        langue_ocr: str = 'fra',
        dpi_ocr: int = 300
    ):
        """
        Initialise l'extracteur.

        Args:
            utiliser_ocr: Activer l'OCR pour PDF scannés
            utiliser_ml: Activer le ML pour améliorer l'extraction
            langue_ocr: Langue pour l'OCR
            dpi_ocr: Résolution pour l'OCR
        """
        self.patterns = PatternsAvances()

        self.utiliser_ocr = utiliser_ocr
        if utiliser_ocr:
            self.ocr = OCRProcessor(langue=langue_ocr, dpi=dpi_ocr)
        else:
            self.ocr = None

        self.utiliser_ml = utiliser_ml
        if utiliser_ml:
            self.ml = MLExtractor()
        else:
            self.ml = None

        self.patterns_utilises = {}  # Pour le ML

    def extraire_fichier(
        self,
        chemin: str,
        verbose: bool = False
    ) -> ResultatExtraction:
        """
        Extrait les données d'un fichier PDF ou DOCX.

        Args:
            chemin: Chemin du fichier
            verbose: Afficher les détails

        Returns:
            ResultatExtraction avec toutes les données
        """
        chemin = Path(chemin)

        if not chemin.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {chemin}")

        # Calculer le hash du fichier
        hash_fichier = self._calculer_hash(chemin)

        # Extraire le texte selon le type
        extension = chemin.suffix.lower()

        if extension == '.pdf':
            texte = self._extraire_texte_pdf(chemin, verbose)
        elif extension in ['.docx', '.doc']:
            texte = self._extraire_texte_docx(chemin, verbose)
        else:
            raise ValueError(f"Format non supporté: {extension}")

        if verbose:
            print(f"📝 Texte extrait: {len(texte)} caractères")

        # Extraire les données avec les patterns avancés
        donnees = self._extraire_donnees(texte, verbose)

        # Appliquer le ML si activé
        if self.utiliser_ml and self.ml:
            donnees = self._appliquer_ml(donnees, verbose)

        # Construire le résultat
        resultat = ResultatExtraction(
            reference=f"TITRE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            source={
                'type_fichier': extension[1:],
                'nom_fichier': chemin.name,
                'date_upload': datetime.now().isoformat(),
                'hash_fichier': hash_fichier
            },
            date_acte=donnees.get('date_acte'),
            notaire=donnees.get('notaire'),
            publication=donnees.get('publication'),
            vendeurs_originaux=donnees.get('vendeurs_originaux', []),
            proprietaires_actuels=donnees.get('proprietaires_actuels', []),
            bien=donnees.get('bien', {}),
            prix=donnees.get('prix'),
            copropriete=donnees.get('copropriete'),
            origine_propriete=donnees.get('origine_propriete'),
            metadata=donnees.get('metadata', {})
        )

        return resultat

    def _calculer_hash(self, chemin: Path) -> str:
        """Calcule le hash SHA256 d'un fichier."""
        sha256 = hashlib.sha256()
        with open(chemin, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _extraire_texte_pdf(self, chemin: Path, verbose: bool) -> str:
        """Extrait le texte d'un PDF."""
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber non installé. Installation: pip install pdfplumber")

        texte_pages = []

        # D'abord essayer l'extraction directe
        with pdfplumber.open(chemin) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                texte = page.extract_text() or ""
                texte_pages.append(texte)
                if verbose:
                    print(f"  📄 Page {i}: {len(texte)} caractères")

        texte_total = '\n\n'.join(texte_pages)

        # Vérifier si OCR nécessaire
        if self.utiliser_ocr and self.ocr and self.ocr.est_disponible:
            est_scanne, raison = self.ocr.detecter_pdf_scanne(str(chemin))

            if est_scanne:
                if verbose:
                    print(f"  🔍 PDF scanné détecté: {raison}")
                    print("  🔄 Application de l'OCR...")

                resultat_ocr = self.ocr.traiter_pdf(str(chemin))
                texte_total = resultat_ocr.texte_complet

                if verbose:
                    print(f"  ✅ OCR terminé: confiance {resultat_ocr.confiance_moyenne:.0%}")

        return texte_total

    def _extraire_texte_docx(self, chemin: Path, verbose: bool) -> str:
        """Extrait le texte d'un DOCX."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("python-docx non installé. Installation: pip install python-docx")

        doc = Document(str(chemin))
        paragraphes = [p.text for p in doc.paragraphs if p.text.strip()]

        if verbose:
            print(f"  📄 DOCX: {len(paragraphes)} paragraphes")

        return '\n\n'.join(paragraphes)

    def _extraire_donnees(self, texte: str, verbose: bool) -> Dict[str, Any]:
        """Extrait toutes les données du texte."""
        donnees = {
            'metadata': {
                'date_extraction': datetime.now().isoformat(),
                'methode_extraction': 'automatique_v2',
                'champs_extraits': [],
                'champs_manquants': []
            }
        }

        # 1. Dates
        dates = self.patterns.extraire_date(texte)
        if dates:
            meilleure = max(dates, key=lambda d: d.confiance)
            donnees['date_acte'] = meilleure.valeur
            self.patterns_utilises['date_acte'] = meilleure.pattern_id
            donnees['metadata']['champs_extraits'].append('date_acte')
            if verbose:
                print(f"  📅 Date: {meilleure.valeur} ({meilleure.confiance:.0%})")
        else:
            donnees['metadata']['champs_manquants'].append('date_acte')

        # 2. Notaire
        notaires = self.patterns.extraire_notaire(texte)
        if notaires:
            meilleur = max(notaires, key=lambda n: n.confiance)
            if isinstance(meilleur.valeur, dict):
                donnees['notaire'] = meilleur.valeur
            else:
                donnees['notaire'] = {'info': meilleur.valeur}
            self.patterns_utilises['notaire'] = meilleur.pattern_id
            donnees['metadata']['champs_extraits'].append('notaire')
            if verbose:
                print(f"  👨‍⚖️ Notaire: {meilleur.valeur} ({meilleur.confiance:.0%})")
        else:
            donnees['metadata']['champs_manquants'].append('notaire')

        # 3. Publication
        publications = self.patterns.extraire_publication(texte)
        if publications:
            meilleure = max(publications, key=lambda p: p.confiance)
            if isinstance(meilleure.valeur, dict):
                donnees['publication'] = meilleure.valeur
            else:
                donnees['publication'] = {'reference': meilleure.valeur}
            self.patterns_utilises['publication'] = meilleure.pattern_id
            donnees['metadata']['champs_extraits'].append('publication')
            if verbose:
                print(f"  📋 Publication: {meilleure.valeur} ({meilleure.confiance:.0%})")
        else:
            donnees['metadata']['champs_manquants'].append('publication')

        # 4. Personnes
        personnes = self.patterns.extraire_personnes(texte)
        vendeurs = []
        for p in personnes:
            if isinstance(p.valeur, dict):
                personne = p.valeur.copy()
                personne['type'] = 'physique'

                # Extraire régime matrimonial
                regimes = self.patterns.extraire_regime_matrimonial(texte)
                if regimes:
                    regime = max(regimes, key=lambda r: r.confiance)
                    if isinstance(regime.valeur, dict):
                        personne['situation_matrimoniale'] = regime.valeur
                    else:
                        personne['situation_matrimoniale'] = {'statut': str(regime.valeur)}

                vendeurs.append(personne)

        if vendeurs:
            donnees['vendeurs_originaux'] = vendeurs
            donnees['metadata']['champs_extraits'].append('vendeurs_originaux')
            if verbose:
                print(f"  👥 Vendeurs: {len(vendeurs)} personne(s)")
        else:
            donnees['metadata']['champs_manquants'].append('vendeurs_originaux')

        # 5. Lots
        lots = self.patterns.extraire_lots(texte)
        bien = {'lots': []}
        for lot in lots:
            if isinstance(lot.valeur, dict):
                bien['lots'].append(lot.valeur)

        if bien['lots']:
            donnees['bien'] = bien
            donnees['metadata']['champs_extraits'].append('bien.lots')
            if verbose:
                print(f"  🏠 Lots: {len(bien['lots'])} lot(s)")
        else:
            donnees['metadata']['champs_manquants'].append('bien.lots')

        # 6. Prix
        prix_resultats = self.patterns.extraire_prix(texte)
        if prix_resultats:
            meilleur = max(prix_resultats, key=lambda p: p.confiance)
            if isinstance(meilleur.valeur, dict):
                donnees['prix'] = meilleur.valeur
            else:
                donnees['prix'] = {'montant': meilleur.valeur}
            self.patterns_utilises['prix'] = meilleur.pattern_id
            donnees['metadata']['champs_extraits'].append('prix')
            if verbose:
                print(f"  💰 Prix: {meilleur.valeur} ({meilleur.confiance:.0%})")
        else:
            donnees['metadata']['champs_manquants'].append('prix')

        # 7. Calculer la confiance globale
        champs_extraits = len(donnees['metadata']['champs_extraits'])
        champs_total = champs_extraits + len(donnees['metadata']['champs_manquants'])
        donnees['metadata']['confiance'] = champs_extraits / champs_total if champs_total > 0 else 0

        return donnees

    def _appliquer_ml(self, donnees: Dict[str, Any], verbose: bool) -> Dict[str, Any]:
        """Applique les corrections ML aux données."""
        if not self.ml:
            return donnees

        # Corriger les valeurs connues
        champs_a_corriger = ['date_acte', 'notaire.nom', 'bien.adresse.code_postal']

        for champ in champs_a_corriger:
            # Naviguer dans la structure
            valeur = self._get_nested(donnees, champ)
            if valeur:
                valeur_corrigee, corrigee = self.ml.corriger_valeur(valeur, champ)
                if corrigee:
                    self._set_nested(donnees, champ, valeur_corrigee)
                    if verbose:
                        print(f"  🔧 ML correction: {champ}")

        # Détecter les anomalies
        anomalies = self.ml.detecter_anomalies(donnees)
        if anomalies:
            donnees['metadata']['anomalies'] = anomalies
            if verbose:
                for a in anomalies:
                    print(f"  ⚠️ Anomalie [{a['severite']}]: {a['message']}")

        # Ajuster les scores de confiance
        scores = self.ml.calculer_score_confiance(
            donnees,
            self.patterns_utilises
        )
        donnees['metadata']['scores_confiance'] = scores

        return donnees

    def _get_nested(self, data: Dict, path: str) -> Any:
        """Récupère une valeur imbriquée."""
        keys = path.split('.')
        result = data
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return None
        return result

    def _set_nested(self, data: Dict, path: str, value: Any):
        """Définit une valeur imbriquée."""
        keys = path.split('.')
        result = data
        for key in keys[:-1]:
            if key not in result:
                result[key] = {}
            result = result[key]
        result[keys[-1]] = value

    def valider_extraction(
        self,
        resultat: ResultatExtraction,
        corrections: Dict[str, Any]
    ):
        """
        Enregistre les corrections du notaire pour l'apprentissage.

        Args:
            resultat: Résultat de l'extraction
            corrections: Dict des corrections {champ: valeur_corrigee}
        """
        if not self.ml:
            return

        for champ, valeur_corrigee in corrections.items():
            valeur_extraite = self._get_nested(asdict(resultat), champ)
            pattern = self.patterns_utilises.get(champ, 'unknown')

            self.ml.valider_extraction(
                extraction_id=resultat.reference,
                champ=champ,
                valeur_extraite=valeur_extraite,
                valeur_corrigee=valeur_corrigee if valeur_extraite != valeur_corrigee else None,
                contexte="",  # TODO: garder le contexte
                pattern_utilise=pattern
            )


def main():
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description='Extracteur v2 - Extraction avancée des titres de propriété'
    )
    parser.add_argument('-i', '--input', required=True, help='Fichier PDF ou DOCX')
    parser.add_argument('-o', '--output', help='Fichier JSON de sortie')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbeux')
    parser.add_argument('--no-ocr', action='store_true', help='Désactiver l\'OCR')
    parser.add_argument('--no-ml', action='store_true', help='Désactiver le ML')
    parser.add_argument('--dpi', type=int, default=300, help='Résolution OCR')
    parser.add_argument('--lang', default='fra', help='Langue OCR')
    parser.add_argument('--stats', action='store_true', help='Afficher les stats ML')

    args = parser.parse_args()

    # Créer l'extracteur
    extracteur = ExtracteurV2(
        utiliser_ocr=not args.no_ocr,
        utiliser_ml=not args.no_ml,
        langue_ocr=args.lang,
        dpi_ocr=args.dpi
    )

    if args.stats:
        if extracteur.ml:
            stats = extracteur.ml.obtenir_statistiques()
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print("ML désactivé")
        return

    # Extraire
    print(f"🔍 Extraction de {args.input}...")
    resultat = extracteur.extraire_fichier(args.input, verbose=args.verbose)

    # Convertir en dict
    resultat_dict = asdict(resultat)

    # Sauvegarder ou afficher
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(resultat_dict, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"\n✅ Résultat sauvegardé: {args.output}")
    else:
        print(json.dumps(resultat_dict, ensure_ascii=False, indent=2))

    # Afficher le résumé
    print(f"\n📊 Résumé:")
    print(f"  - Référence: {resultat.reference}")
    print(f"  - Confiance: {resultat.metadata.get('confiance', 0):.0%}")
    print(f"  - Champs extraits: {len(resultat.metadata.get('champs_extraits', []))}")
    print(f"  - Champs manquants: {len(resultat.metadata.get('champs_manquants', []))}")

    if resultat.metadata.get('anomalies'):
        print(f"  - Anomalies: {len(resultat.metadata['anomalies'])}")


if __name__ == '__main__':
    main()
