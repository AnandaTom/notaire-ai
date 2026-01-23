# -*- coding: utf-8 -*-
"""
Module d'extraction avancée des titres de propriété.

Composants:
- patterns_avances.py: Patterns regex améliorés
- ocr_processor.py: Support OCR pour PDF scannés
- ml_extractor.py: Machine Learning pour améliorer l'extraction
- extracteur_v2.py: Extracteur principal combinant les 3 modules

Usage:
    from execution.extraction import ExtracteurV2

    extracteur = ExtracteurV2()
    resultat = extracteur.extraire_fichier("document.pdf", verbose=True)
"""

from pathlib import Path

MODULE_DIR = Path(__file__).parent
PROJECT_ROOT = MODULE_DIR.parent.parent

# Imports principaux
from .patterns_avances import PatternsAvances, PatternResult
from .ocr_processor import OCRProcessor, OCRResult
from .ml_extractor import MLExtractor, BaseApprentissage
from .extracteur_v2 import ExtracteurV2, ResultatExtraction

__all__ = [
    'ExtracteurV2',
    'ResultatExtraction',
    'PatternsAvances',
    'PatternResult',
    'OCRProcessor',
    'OCRResult',
    'MLExtractor',
    'BaseApprentissage',
]

__version__ = '2.0.0'
