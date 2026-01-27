# -*- coding: utf-8 -*-
"""
API NotaireAI - Module d'interface REST

Ce module expose l'agent autonome via HTTP pour:
- Le front-end des notaires
- Les intégrations tierces
- Le déploiement Modal (serverless)
"""

from .main import app

__all__ = ["app"]
