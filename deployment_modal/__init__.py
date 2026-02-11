# -*- coding: utf-8 -*-
"""
Module Modal - Déploiement Serverless NotaireAI
===============================================

Ce module contient tous les fichiers de déploiement Modal.com:
- modal_app.py: Application principale avec FastAPI, CRON jobs, scaling
- modal_app_legacy.py: Version simplifiée (génération, chat, sync)

Déploiement:
    modal deploy modal/modal_app.py

Test local:
    modal serve modal/modal_app.py

Endpoint production:
    https://notaire-ai--fastapi-app.modal.run/
"""

from pathlib import Path

MODAL_DIR = Path(__file__).parent
