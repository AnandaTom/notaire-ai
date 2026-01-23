# -*- coding: utf-8 -*-
"""
Processeur OCR pour les PDF scannés.

Ce module permet d'extraire le texte des PDF scannés en utilisant
pytesseract et pdf2image.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

# Configuration encodage Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)


@dataclass
class OCRPage:
    """Résultat OCR d'une page."""
    numero: int
    texte: str
    confiance: float
    langue: str
    resolution: int


@dataclass
class OCRResult:
    """Résultat complet de l'OCR."""
    texte_complet: str
    pages: List[OCRPage]
    confiance_moyenne: float
    est_scanne: bool
    temps_traitement: float


class OCRProcessor:
    """Processeur OCR pour PDF scannés."""

    # Langues supportées pour Tesseract
    LANGUES_SUPPORTEES = {
        'fra': 'Français',
        'eng': 'English',
        'deu': 'Deutsch',
        'fra+eng': 'Français + English'
    }

    def __init__(
        self,
        langue: str = 'fra',
        dpi: int = 300,
        tesseract_path: Optional[str] = None
    ):
        """
        Initialise le processeur OCR.

        Args:
            langue: Code langue Tesseract (fra, eng, etc.)
            dpi: Résolution pour la conversion PDF → Image
            tesseract_path: Chemin vers l'exécutable Tesseract (optionnel)
        """
        self.langue = langue
        self.dpi = dpi
        self.tesseract_path = tesseract_path
        self._verifier_dependances()

    def _verifier_dependances(self) -> Dict[str, bool]:
        """Vérifie que les dépendances OCR sont installées."""
        deps = {
            'pdf2image': False,
            'pytesseract': False,
            'PIL': False,
            'poppler': False,
            'tesseract': False
        }

        # Vérifier pdf2image
        try:
            import pdf2image
            deps['pdf2image'] = True
        except ImportError:
            logger.warning("pdf2image non installé. Installation: pip install pdf2image")

        # Vérifier pytesseract
        try:
            import pytesseract
            deps['pytesseract'] = True
            if self.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        except ImportError:
            logger.warning("pytesseract non installé. Installation: pip install pytesseract")

        # Vérifier PIL/Pillow
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            deps['PIL'] = True
        except ImportError:
            logger.warning("Pillow non installé. Installation: pip install Pillow")

        # Vérifier Poppler (nécessaire pour pdf2image)
        if deps['pdf2image']:
            try:
                from pdf2image import convert_from_path
                # Test basique
                deps['poppler'] = True
            except Exception as e:
                logger.warning(f"Poppler non installé ou non accessible: {e}")
                logger.info("Windows: Télécharger depuis https://github.com/oschwartz10612/poppler-windows/releases")
                logger.info("Ajouter le dossier bin/ au PATH")

        # Vérifier Tesseract
        if deps['pytesseract']:
            try:
                import pytesseract
                version = pytesseract.get_tesseract_version()
                deps['tesseract'] = True
                logger.info(f"Tesseract version: {version}")
            except Exception as e:
                logger.warning(f"Tesseract non installé ou non accessible: {e}")
                logger.info("Windows: Télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki")

        self._deps = deps
        return deps

    @property
    def est_disponible(self) -> bool:
        """Vérifie si l'OCR est utilisable."""
        return all([
            self._deps.get('pdf2image', False),
            self._deps.get('pytesseract', False),
            self._deps.get('PIL', False),
            self._deps.get('poppler', False),
            self._deps.get('tesseract', False)
        ])

    def detecter_pdf_scanne(self, pdf_path: str, seuil_texte: int = 100) -> Tuple[bool, str]:
        """
        Détecte si un PDF est scanné (image) ou textuel.

        Args:
            pdf_path: Chemin du PDF
            seuil_texte: Nombre minimum de caractères pour considérer comme textuel

        Returns:
            Tuple (est_scanne, raison)
        """
        try:
            import pdfplumber

            texte_total = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages[:3]:  # Vérifier les 3 premières pages
                    texte = page.extract_text() or ""
                    texte_total += texte

            # Si très peu de texte extractible, probablement scanné
            if len(texte_total.strip()) < seuil_texte:
                return True, f"Peu de texte extractible ({len(texte_total)} caractères)"

            # Vérifier si le texte semble cohérent
            mots = texte_total.split()
            if len(mots) < 20:
                return True, f"Peu de mots extractibles ({len(mots)} mots)"

            # Vérifier les caractères illisibles (signe de mauvaise extraction)
            chars_illisibles = sum(1 for c in texte_total if ord(c) > 127 and c not in 'éèêëàâäùûüôöîïçÉÈÊËÀÂÄÙÛÜÔÖÎÏÇœŒ€')
            ratio_illisibles = chars_illisibles / len(texte_total) if texte_total else 0

            if ratio_illisibles > 0.1:
                return True, f"Trop de caractères illisibles ({ratio_illisibles:.1%})"

            return False, "PDF textuel"

        except Exception as e:
            logger.error(f"Erreur détection PDF scanné: {e}")
            return True, f"Erreur détection: {e}"

    def pretraiter_image(self, image) -> 'Image':
        """
        Prétraite une image pour améliorer l'OCR.

        Applique:
        - Conversion en niveaux de gris
        - Augmentation du contraste
        - Binarisation (si nécessaire)
        - Réduction du bruit

        Args:
            image: Image PIL

        Returns:
            Image prétraitée
        """
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps

        # Conversion en niveaux de gris
        if image.mode != 'L':
            image = image.convert('L')

        # Augmenter le contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)

        # Augmenter la netteté
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)

        # Binarisation adaptative (Otsu)
        # Utiliser un seuil simple pour la binarisation
        threshold = 128
        image = image.point(lambda x: 255 if x > threshold else 0, '1')

        # Reconvertir en niveaux de gris pour Tesseract
        image = image.convert('L')

        # Réduction du bruit (médian filter)
        image = image.filter(ImageFilter.MedianFilter(size=3))

        return image

    def extraire_texte_page(
        self,
        image,
        pretraitement: bool = True
    ) -> Tuple[str, float]:
        """
        Extrait le texte d'une image de page.

        Args:
            image: Image PIL de la page
            pretraitement: Appliquer le prétraitement

        Returns:
            Tuple (texte, confiance)
        """
        import pytesseract
        from PIL import Image

        if pretraitement:
            image = self.pretraiter_image(image)

        # Configuration Tesseract
        config = f'--oem 3 --psm 6 -l {self.langue}'

        # Extraction avec données de confiance
        try:
            data = pytesseract.image_to_data(
                image,
                config=config,
                output_type=pytesseract.Output.DICT
            )

            # Calculer la confiance moyenne
            confiances = [
                int(c) for c in data['conf']
                if str(c).isdigit() and int(c) > 0
            ]
            confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0

            # Extraire le texte
            texte = pytesseract.image_to_string(image, config=config)

            return texte, confiance_moyenne / 100

        except Exception as e:
            logger.error(f"Erreur OCR: {e}")
            return "", 0.0

    def traiter_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None,
        pretraitement: bool = True
    ) -> OCRResult:
        """
        Traite un PDF avec OCR.

        Args:
            pdf_path: Chemin du PDF
            pages: Liste des pages à traiter (None = toutes)
            pretraitement: Appliquer le prétraitement d'image

        Returns:
            OCRResult avec le texte extrait
        """
        import time
        from pdf2image import convert_from_path

        debut = time.time()

        if not self.est_disponible:
            raise RuntimeError(
                "OCR non disponible. Vérifier l'installation de: "
                "pdf2image, pytesseract, Pillow, Poppler, Tesseract"
            )

        # Détecter si réellement scanné
        est_scanne, raison = self.detecter_pdf_scanne(pdf_path)
        logger.info(f"Détection PDF: {raison}")

        # Convertir PDF en images
        logger.info(f"Conversion PDF → Images (DPI={self.dpi})...")
        images = convert_from_path(pdf_path, dpi=self.dpi)

        # Filtrer les pages si spécifié
        if pages:
            images = [images[i-1] for i in pages if 0 < i <= len(images)]

        # Traiter chaque page
        resultats_pages = []
        textes = []

        for i, image in enumerate(images, 1):
            logger.info(f"OCR page {i}/{len(images)}...")
            texte, confiance = self.extraire_texte_page(image, pretraitement)

            resultats_pages.append(OCRPage(
                numero=i,
                texte=texte,
                confiance=confiance,
                langue=self.langue,
                resolution=self.dpi
            ))
            textes.append(texte)

        # Calculer la confiance moyenne
        confiances = [p.confiance for p in resultats_pages if p.confiance > 0]
        confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0

        temps_traitement = time.time() - debut

        return OCRResult(
            texte_complet='\n\n'.join(textes),
            pages=resultats_pages,
            confiance_moyenne=confiance_moyenne,
            est_scanne=est_scanne,
            temps_traitement=temps_traitement
        )

    def extraire_zones(
        self,
        pdf_path: str,
        zones: List[Dict[str, int]]
    ) -> List[Tuple[str, float]]:
        """
        Extrait le texte de zones spécifiques d'un PDF.

        Args:
            pdf_path: Chemin du PDF
            zones: Liste de dicts avec {page, x, y, width, height}

        Returns:
            Liste de (texte, confiance) pour chaque zone
        """
        from pdf2image import convert_from_path
        from PIL import Image

        images = convert_from_path(pdf_path, dpi=self.dpi)
        resultats = []

        for zone in zones:
            page_num = zone.get('page', 1)
            if page_num > len(images):
                resultats.append(("", 0.0))
                continue

            image = images[page_num - 1]

            # Calculer les coordonnées en pixels
            x = int(zone['x'] * self.dpi / 72)
            y = int(zone['y'] * self.dpi / 72)
            w = int(zone['width'] * self.dpi / 72)
            h = int(zone['height'] * self.dpi / 72)

            # Découper la zone
            zone_image = image.crop((x, y, x + w, y + h))

            # OCR sur la zone
            texte, confiance = self.extraire_texte_page(zone_image)
            resultats.append((texte, confiance))

        return resultats


def installer_dependances():
    """Installe les dépendances Python nécessaires."""
    import subprocess

    packages = [
        'pdf2image',
        'pytesseract',
        'Pillow'
    ]

    for package in packages:
        print(f"Installation de {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package])

    print("\n⚠️  Dépendances système requises:")
    print("  - Poppler: https://github.com/oschwartz10612/poppler-windows/releases")
    print("  - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
    print("\nAjouter les dossiers bin/ au PATH système.")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='OCR pour PDF scannés')
    parser.add_argument('-i', '--input', help='Fichier PDF à traiter')
    parser.add_argument('-o', '--output', help='Fichier texte de sortie')
    parser.add_argument('--install', action='store_true', help='Installer les dépendances')
    parser.add_argument('--check', action='store_true', help='Vérifier les dépendances')
    parser.add_argument('--dpi', type=int, default=300, help='Résolution (défaut: 300)')
    parser.add_argument('--lang', default='fra', help='Langue Tesseract (défaut: fra)')

    args = parser.parse_args()

    if args.install:
        installer_dependances()
    elif args.check:
        processor = OCRProcessor()
        print("\n📋 Statut des dépendances OCR:")
        for dep, status in processor._deps.items():
            emoji = "✅" if status else "❌"
            print(f"  {emoji} {dep}")
        print(f"\n{'✅ OCR disponible' if processor.est_disponible else '❌ OCR non disponible'}")
    elif args.input:
        processor = OCRProcessor(langue=args.lang, dpi=args.dpi)

        if not processor.est_disponible:
            print("❌ OCR non disponible. Utilisez --install pour installer les dépendances.")
            sys.exit(1)

        print(f"🔍 Traitement OCR de {args.input}...")
        result = processor.traiter_pdf(args.input)

        print(f"\n📊 Résultats:")
        print(f"  - Pages traitées: {len(result.pages)}")
        print(f"  - Confiance moyenne: {result.confiance_moyenne:.1%}")
        print(f"  - PDF scanné: {'Oui' if result.est_scanne else 'Non'}")
        print(f"  - Temps: {result.temps_traitement:.1f}s")

        if args.output:
            Path(args.output).write_text(result.texte_complet, encoding='utf-8')
            print(f"\n✅ Texte sauvegardé dans {args.output}")
        else:
            print(f"\n📝 Extrait du texte:\n{result.texte_complet[:500]}...")
    else:
        parser.print_help()
