#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de déploiement Modal avec fix encodage Windows.

Usage: python deploy_modal.py
"""

import sys
import os
import io

# Fix encodage Windows AVANT tout import
if sys.platform == "win32":
    # Force UTF-8 pour stdout/stderr
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Variable d'environnement
    os.environ['PYTHONUTF8'] = '1'

# Maintenant on peut importer Modal
import subprocess

def main():
    print("🚀 Déploiement Modal avec fix encodage Windows...")
    print()

    # Lancer modal deploy avec la configuration UTF-8
    result = subprocess.run(
        [sys.executable, "-m", "modal", "deploy", "deployment_modal/modal_app.py"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    # Afficher la sortie
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        print()
        print("✅ Déploiement réussi!")
        print()
        print("📡 Votre API est maintenant accessible à:")
        print("   https://notaire-ai--fastapi-app.modal.run/")
        print()
        print("🔍 Testez avec:")
        print("   curl https://notaire-ai--fastapi-app.modal.run/health")
        print("   curl https://notaire-ai--fastapi-app.modal.run/agents")
    else:
        print()
        print("❌ Erreur lors du déploiement")
        print(f"   Code de sortie: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
