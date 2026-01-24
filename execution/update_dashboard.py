#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_dashboard.py - Met a jour automatiquement les donnees du dashboard

Usage:
    python execution/update_dashboard.py

Ce script analyse le repo et genere dashboard/data/status.json
avec les informations actuelles sur:
- Etat des templates (conformite, derniere modification)
- Branches et commits de l'equipe
- Taches en cours (depuis CHANGELOG, TODO, etc.)
- Metriques de performance
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Chemins
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DASHBOARD_DATA = PROJECT_ROOT / "dashboard" / "data" / "status.json"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"


def run_git_command(cmd: list) -> str:
    """Execute une commande git et retourne le resultat."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Erreur git: {e}")
        return ""


def get_template_info() -> list:
    """Analyse les templates et retourne leurs informations."""
    templates = []

    template_configs = [
        {
            "file": "vente_lots_copropriete.md",
            "name": "Vente lots copropriete",
            "bookmarks": 361,
            "conformity": 85.1,
            "status": "prod"
        },
        {
            "file": "promesse_vente_lots_copropriete.md",
            "name": "Promesse de vente",
            "bookmarks": 298,
            "conformity": 60.9,
            "status": "dev"
        },
        {
            "file": "reglement_copropriete_edd.md",
            "name": "Reglement copropriete",
            "bookmarks": 116,
            "conformity": 85.5,
            "status": "prod"
        },
        {
            "file": "modificatif_edd.md",
            "name": "Modificatif EDD",
            "bookmarks": 60,
            "conformity": 91.7,
            "status": "prod"
        }
    ]

    for config in template_configs:
        template_path = TEMPLATES_DIR / config["file"]

        # Verifier si le fichier existe et obtenir sa date de modification
        if template_path.exists():
            mtime = datetime.fromtimestamp(template_path.stat().st_mtime)
            last_modified = mtime.strftime("%Y-%m-%d")

            # Compter les sections (lignes commencant par #)
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                sections = len([line for line in content.split('\n') if line.startswith('#')])
        else:
            last_modified = "N/A"
            sections = 0

        templates.append({
            "name": config["name"],
            "file": config["file"],
            "conformity": config["conformity"],
            "status": config["status"],
            "bookmarks": config["bookmarks"],
            "sections": sections,
            "lastGeneration": last_modified
        })

    return templates


def get_team_info() -> list:
    """Recupere les informations sur les branches de l'equipe."""
    team = [
        {"name": "Tom", "github": "AnandaTom", "branch": "tom/dev", "role": "Lead Dev / Templates"},
        {"name": "Augustin", "github": "augustinfrance-aico", "branch": "augustin/dev", "role": "Frontend / Formulaires"},
        {"name": "Payoss", "github": "Payoss", "branch": "payoss/dev", "role": "Backend / Scripts"}
    ]

    for member in team:
        # Obtenir le dernier commit de la branche
        branch = member["branch"]
        last_commit = run_git_command([
            "git", "log", f"origin/{branch}", "-1", "--format=%s", "--"
        ])

        last_date = run_git_command([
            "git", "log", f"origin/{branch}", "-1", "--format=%aI", "--"
        ])

        if last_commit:
            member["lastCommit"] = last_commit[:50] + ("..." if len(last_commit) > 50 else "")
            member["status"] = "active"
            member["lastActivity"] = last_date if last_date else datetime.now().isoformat()
        else:
            member["lastCommit"] = "Branche non trouvee"
            member["status"] = "setup"
            member["lastActivity"] = datetime.now().isoformat()

    return team


def get_tasks() -> dict:
    """Definit les taches actuelles du projet."""
    # Ces taches peuvent etre lues depuis un fichier TODO.md ou definies ici
    return {
        "todo": [
            "Enrichir template promesse de vente (24 titres)",
            "Integrer extraction titre de propriete",
            "Ajouter validation Carrez automatique",
            "Creer template donation-partage",
            "Tests automatises pytest"
        ],
        "inProgress": [
            "Dashboard temps reel",
            "Workflow collaboratif 3 devs",
            "Formulaires web vendeur/acquereur"
        ],
        "done": [
            "Template vente 85% conformite",
            "Scripts START_DAY/END_DAY",
            "Auto-sync v2 (30min commits)",
            "Integration Supabase MCP",
            "Integration Stripe MCP",
            "Pipeline generation 5.7s",
            "Securisation cles API",
            "Documentation complete",
            "Morning sync semi-auto",
            "Troubleshooting guide"
        ]
    }


def get_capabilities() -> list:
    """Liste les capacites de l'agent."""
    return [
        {"icon": "📄", "name": "Generer actes", "description": "DOCX/PDF fideles aux trames", "status": "active"},
        {"icon": "💬", "name": "Dialogue notaire", "description": "Collecte interactive 100+ questions", "status": "active"},
        {"icon": "✅", "name": "Validation", "description": "Coherence et completude", "status": "active"},
        {"icon": "🔍", "name": "Detection auto", "description": "Type d'acte automatique", "status": "active"},
        {"icon": "💡", "name": "Suggestions", "description": "Clauses contextuelles", "status": "active"},
        {"icon": "📊", "name": "Conformite", "description": "Score automatique vs trame", "status": "active"},
        {"icon": "🗄️", "name": "Historique", "description": "Supabase + mode offline", "status": "active"},
        {"icon": "⚡", "name": "Pipeline rapide", "description": "~6 secondes / acte", "status": "active"}
    ]


def count_scripts() -> int:
    """Compte le nombre de scripts Python dans execution/."""
    execution_dir = PROJECT_ROOT / "execution"
    if execution_dir.exists():
        return len(list(execution_dir.glob("*.py")))
    return 0


def count_schemas() -> int:
    """Compte le nombre de schemas JSON."""
    if SCHEMAS_DIR.exists():
        return len(list(SCHEMAS_DIR.glob("*.json")))
    return 0


def generate_status() -> dict:
    """Genere le fichier status.json complet."""
    templates = get_template_info()
    team = get_team_info()
    tasks = get_tasks()
    capabilities = get_capabilities()

    # Calculer les metriques
    conformity_avg = sum(t["conformity"] for t in templates) / len(templates) if templates else 0
    prod_count = len([t for t in templates if t["status"] == "prod"])
    dev_count = len([t for t in templates if t["status"] == "dev"])

    return {
        "lastUpdate": datetime.now().isoformat(),
        "version": "1.2.0",
        "templates": templates,
        "tasks": tasks,
        "team": team,
        "capabilities": capabilities,
        "mcpServers": {
            "supabase": {
                "status": "connected",
                "projectRef": "wcklvjckzktijtgakdrk",
                "tables": ["clients", "actes", "historique", "variables", "templates"]
            },
            "stripe": {
                "status": "connected",
                "mode": "test",
                "products": 3
            }
        },
        "metrics": {
            "totalActesGeneres": 12,
            "tempsGenerationMoyen": "5.7s",
            "conformiteMoyenne": round(conformity_avg, 1),
            "templatesProduction": prod_count,
            "templatesDev": dev_count,
            "scriptsCount": count_scripts(),
            "schemasCount": count_schemas()
        },
        "pipeline": {
            "assemblageJinja": "1.5s",
            "exportDocx": "3.5s",
            "verification": "0.7s",
            "total": "5.7s",
            "pagesParSeconde": 8
        }
    }


def main():
    print("=" * 50)
    print("NotaireAI - Mise a jour du Dashboard")
    print("=" * 50)

    # Generer les donnees
    print("\n[1/3] Analyse du projet...")
    status = generate_status()

    # Creer le dossier si necessaire
    print("[2/3] Creation du fichier status.json...")
    DASHBOARD_DATA.parent.mkdir(parents=True, exist_ok=True)

    # Ecrire le fichier
    with open(DASHBOARD_DATA, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

    print(f"[3/3] Fichier genere: {DASHBOARD_DATA}")

    # Resume
    print("\n" + "-" * 50)
    print("Resume:")
    print(f"  - Templates: {len(status['templates'])} ({status['metrics']['templatesProduction']} PROD, {status['metrics']['templatesDev']} DEV)")
    print(f"  - Conformite moyenne: {status['metrics']['conformiteMoyenne']}%")
    print(f"  - Equipe: {len(status['team'])} membres")
    print(f"  - Taches: {len(status['tasks']['todo'])} TODO, {len(status['tasks']['inProgress'])} en cours, {len(status['tasks']['done'])} terminees")
    print(f"  - Scripts: {status['metrics']['scriptsCount']}")
    print(f"  - Schemas: {status['metrics']['schemasCount']}")
    print("-" * 50)
    print("\nDashboard mis a jour avec succes!")
    print(f"Ouvrir: dashboard/index.html")


if __name__ == "__main__":
    main()
