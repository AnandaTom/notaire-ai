#!/usr/bin/env python3
"""
Générateur de données pour le dashboard Notomai.
Analyse le codebase et génère des fichiers JSON pour le dashboard dynamique.

Usage:
    python execution/generer_dashboard_data.py

Output:
    docs/data/dashboard.json - Données complètes du dashboard
"""

import json
import os
import sys
import subprocess

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DATA_DIR = PROJECT_ROOT / "docs" / "data"
OUTPUT_FILE = DOCS_DATA_DIR / "dashboard.json"


def count_files(directory: Path, pattern: str) -> int:
    """Compte les fichiers correspondant au pattern."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def get_git_info() -> dict:
    """Récupère les informations Git."""
    try:
        # Dernier commit
        last_commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H|%s|%ai"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip()

        if last_commit:
            parts = last_commit.split("|")
            commit_hash = parts[0][:7]
            commit_msg = parts[1] if len(parts) > 1 else ""
            commit_date = parts[2][:10] if len(parts) > 2 else ""
        else:
            commit_hash, commit_msg, commit_date = "", "", ""

        # Branche actuelle
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip()

        # Nombre de commits total
        commit_count = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip()

        # Contributeurs
        contributors = subprocess.check_output(
            ["git", "shortlog", "-sn", "--all"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip().split("\n")

        team = []
        for line in contributors[:5]:  # Top 5
            if line.strip():
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    commits = int(parts[0].strip())
                    name = parts[1].strip()
                    team.append({"name": name, "commits": commits})

        return {
            "branch": branch,
            "last_commit": {
                "hash": commit_hash,
                "message": commit_msg,
                "date": commit_date
            },
            "total_commits": int(commit_count) if commit_count else 0,
            "team": team
        }
    except Exception as e:
        print(f"Warning: Could not get git info: {e}", file=sys.stderr)
        return {
            "branch": "unknown",
            "last_commit": {"hash": "", "message": "", "date": ""},
            "total_commits": 0,
            "team": []
        }


def analyze_templates() -> list:
    """Analyse les templates et leur conformité."""
    templates_dir = PROJECT_ROOT / "templates"
    templates = []

    template_info = {
        "vente_lots_copropriete.md": {
            "name": "Vente lots copropriété",
            "conformity": 85.1,
            "status": "prod",
            "bookmarks": 361,
            "sections": 37
        },
        "promesse_vente_lots_copropriete.md": {
            "name": "Promesse de vente",
            "conformity": 60.9,
            "status": "dev",
            "bookmarks": 298,
            "sections": 127
        },
        "reglement_copropriete_edd.md": {
            "name": "Règlement copropriété",
            "conformity": 85.5,
            "status": "prod",
            "bookmarks": 116,
            "sections": 111
        },
        "modificatif_edd.md": {
            "name": "Modificatif EDD",
            "conformity": 91.7,
            "status": "prod",
            "bookmarks": 60,
            "sections": 13
        }
    }

    for template_file, info in template_info.items():
        template_path = templates_dir / template_file
        if template_path.exists():
            # Compter les lignes
            with open(template_path, "r", encoding="utf-8") as f:
                lines = len(f.readlines())

            # Récupérer la date de modification
            mtime = datetime.fromtimestamp(template_path.stat().st_mtime)

            templates.append({
                "file": template_file,
                "name": info["name"],
                "conformity": info["conformity"],
                "status": info["status"],
                "bookmarks": info["bookmarks"],
                "sections": info["sections"],
                "lines": lines,
                "last_modified": mtime.strftime("%Y-%m-%d")
            })

    return templates


def analyze_scripts() -> dict:
    """Analyse les scripts Python."""
    execution_dir = PROJECT_ROOT / "execution"

    scripts = []
    total_lines = 0
    categories = defaultdict(int)

    if execution_dir.exists():
        for py_file in execution_dir.glob("**/*.py"):
            if py_file.name.startswith("__"):
                continue

            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = len(f.readlines())

            total_lines += lines

            # Catégoriser
            name = py_file.stem
            if "test" in name:
                categories["tests"] += 1
            elif "export" in name:
                categories["export"] += 1
            elif "valid" in name:
                categories["validation"] += 1
            elif "generer" in name or "assembler" in name:
                categories["generation"] += 1
            else:
                categories["utils"] += 1

            scripts.append({
                "name": py_file.name,
                "lines": lines,
                "path": str(py_file.relative_to(PROJECT_ROOT))
            })

    return {
        "total": len(scripts),
        "total_lines": total_lines,
        "categories": dict(categories),
        "scripts": sorted(scripts, key=lambda x: x["lines"], reverse=True)[:10]
    }


def analyze_schemas() -> dict:
    """Analyse les schémas JSON."""
    schemas_dir = PROJECT_ROOT / "schemas"

    schemas = []
    total_variables = 0

    if schemas_dir.exists():
        for json_file in schemas_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Compter les variables/questions
                if isinstance(data, dict):
                    count = len(data.get("properties", data.get("questions", data)))
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = 0

                total_variables += count

                schemas.append({
                    "name": json_file.name,
                    "count": count
                })
            except Exception:
                continue

    return {
        "total": len(schemas),
        "total_variables": total_variables,
        "schemas": schemas
    }


def analyze_docs() -> dict:
    """Analyse la documentation."""
    docs_dir = PROJECT_ROOT / "docs"
    directives_dir = PROJECT_ROOT / "directives"

    legal_docs = list((docs_dir / "legal").glob("*.md")) if (docs_dir / "legal").exists() else []
    directive_docs = list(directives_dir.glob("*.md")) if directives_dir.exists() else []

    return {
        "legal": [f.name for f in legal_docs],
        "directives": [f.name for f in directive_docs],
        "total_legal": len(legal_docs),
        "total_directives": len(directive_docs)
    }


def get_project_tasks() -> dict:
    """Récupère les tâches du projet depuis TODO.md ou génère depuis le code."""
    tasks = {
        "todo": [],
        "in_progress": [],
        "done": []
    }

    # Tâches basées sur l'analyse du projet
    # TODO: Améliorer en lisant depuis un fichier TODO.md

    # Tâches terminées (basées sur les fichiers existants)
    done_indicators = [
        ("templates/vente_lots_copropriete.md", "Template vente 85% conformité"),
        ("execution/workflow_rapide.py", "Pipeline génération rapide"),
        ("docs/legal/REGISTRE_TRAITEMENTS.md", "Documentation RGPD"),
        ("docs/legal/CGU_TEMPLATE.md", "Template CGU créé"),
        (".mcp.json", "Intégration Supabase MCP"),
        ("execution/historique_supabase.py", "Historique Supabase"),
        ("docs/index.html", "Dashboard v2.3"),
        ("execution/comparer_documents.py", "Comparaison conformité"),
        ("execution/test_fiabilite.py", "Tests automatisés"),
        ("docs/legal/OBLIGATIONS_CSN.md", "Analyse obligations CSN"),
    ]

    for path, task in done_indicators:
        if (PROJECT_ROOT / path).exists():
            tasks["done"].append(task)

    # Tâches en cours (templates < 80%)
    tasks["in_progress"] = [
        "Enrichir template promesse (60.9% → 80%)",
        "Dashboard temps réel",
        "Formulaires web notaire"
    ]

    # Tâches à faire
    tasks["todo"] = [
        "Créer structure juridique (SAS/SASU)",
        "Souscrire RC Pro",
        "Valider CGU avec avocat",
        "Template donation-partage",
        "Intégration extraction titre propriété",
        "Label ETIK (optionnel)"
    ]

    return tasks


def get_capabilities() -> list:
    """Liste les capacités du système."""
    capabilities = [
        {"icon": "📄", "name": "Générer actes", "description": "DOCX/PDF fidèles aux trames", "active": True},
        {"icon": "💬", "name": "Dialogue notaire", "description": "Collecte interactive 100+ questions", "active": True},
        {"icon": "✅", "name": "Validation", "description": "Cohérence et complétude", "active": True},
        {"icon": "🔍", "name": "Détection auto", "description": "Type d'acte automatique", "active": True},
        {"icon": "💡", "name": "Suggestions", "description": "Clauses contextuelles", "active": True},
        {"icon": "📊", "name": "Conformité", "description": "Score automatique vs trame", "active": True},
        {"icon": "🗄️", "name": "Historique", "description": "Supabase + mode offline", "active": True},
        {"icon": "⚡", "name": "Pipeline rapide", "description": "~6 secondes / acte", "active": True},
    ]

    return capabilities


def get_launch_status() -> dict:
    """Récupère le statut de lancement."""
    return {
        "score": 60,
        "status": "PRE-LANCEMENT",
        "message": "Structure juridique requise avant facturation",
        "address": "2B chemin des Garennes, 69260 Charbonnières",
        "email": "contact@notomai.fr",
        "items": [
            {
                "id": "structure",
                "title": "Structure Juridique",
                "status": "blocked",
                "icon": "🏢",
                "details": "Recommandé: SAS ou SASU",
                "cost": "150-300€"
            },
            {
                "id": "rcpro",
                "title": "Assurance RC Pro",
                "status": "blocked",
                "icon": "🛡️",
                "details": "Requiert structure juridique",
                "cost": "800-2000€/an"
            },
            {
                "id": "cgu",
                "title": "CGU / CGV",
                "status": "pending",
                "icon": "📜",
                "details": "Template créé, validation avocat requise",
                "cost": "500-800€"
            },
            {
                "id": "rgpd",
                "title": "Conformité RGPD",
                "status": "done",
                "icon": "✅",
                "details": "Documentation complète",
                "progress": 95
            },
            {
                "id": "security",
                "title": "Sécurité Technique",
                "status": "done",
                "icon": "🔐",
                "details": "Infrastructure sécurisée",
                "progress": 95
            },
            {
                "id": "etik",
                "title": "Label ETIK (CSN)",
                "status": "optional",
                "icon": "🏆",
                "details": "Non obligatoire pour vendre",
                "cost": "8000-10000€"
            }
        ],
        "budget": {
            "min": 1450,
            "max": 3100
        }
    }


def get_security_status() -> dict:
    """Récupère le statut de sécurité."""
    return {
        "score": 95,
        "items": [
            {"name": "Chiffrement AES-256", "status": "ok"},
            {"name": "TLS 1.3", "status": "ok"},
            {"name": "Row Level Security", "status": "ok"},
            {"name": "2FA", "status": "ok"},
            {"name": "Hébergement UE", "status": "ok"},
            {"name": "RGPD", "status": "ok"}
        ],
        "mcp_servers": [
            {"name": "Supabase", "status": "connected", "mode": "production"},
            {"name": "Stripe", "status": "connected", "mode": "test"}
        ]
    }


def generate_dashboard_data() -> dict:
    """Génère toutes les données du dashboard."""
    print("[*] Generation des donnees du dashboard...")

    git_info = get_git_info()
    templates = analyze_templates()
    scripts = analyze_scripts()
    schemas = analyze_schemas()
    docs = analyze_docs()
    tasks = get_project_tasks()
    capabilities = get_capabilities()
    launch = get_launch_status()
    security = get_security_status()

    # Calculer les métriques
    prod_templates = sum(1 for t in templates if t["status"] == "prod")
    avg_conformity = sum(t["conformity"] for t in templates) / len(templates) if templates else 0

    data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.3.0",
            "dashboard_version": "2.4"
        },
        "metrics": {
            "templates_count": len(templates),
            "templates_prod": prod_templates,
            "avg_conformity": round(avg_conformity, 1),
            "scripts_count": scripts["total"],
            "schemas_count": schemas["total"],
            "generation_time": "5.7s",
            "commits": git_info["total_commits"]
        },
        "git": git_info,
        "templates": templates,
        "scripts": scripts,
        "schemas": schemas,
        "docs": docs,
        "tasks": tasks,
        "capabilities": capabilities,
        "launch": launch,
        "security": security,
        "team": [
            {"name": "Tom", "branch": "tom/dev", "role": "Lead Dev / Templates", "status": "active"},
            {"name": "Augustin", "branch": "augustin/dev", "role": "Frontend / Formulaires", "status": "active"},
            {"name": "Payoss", "branch": "payoss/dev", "role": "Backend / Scripts", "status": "active"}
        ]
    }

    return data


def main():
    """Point d'entrée principal."""
    # Créer le répertoire de sortie
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Générer les données
    data = generate_dashboard_data()

    # Écrire le fichier JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Donnees generees: {OUTPUT_FILE}")
    print(f"   - {data['metrics']['templates_count']} templates")
    print(f"   - {data['metrics']['scripts_count']} scripts")
    print(f"   - {data['metrics']['schemas_count']} schémas")
    print(f"   - Conformité moyenne: {data['metrics']['avg_conformity']}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
