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


def get_recent_activity() -> list:
    """Récupère l'activité récente des développeurs depuis les commits."""
    try:
        # Récupérer les 30 derniers commits avec auteur, date, message
        commits_raw = subprocess.check_output(
            ["git", "log", "-30", "--format=%H|%an|%ai|%s"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip().split("\n")

        activity = []
        # Mapping des noms git vers noms courts
        name_map = {
            "AnandaTom": "Tom",
            "augustinfrance-aico": "Augustin",
            "Payoss": "Payoss",
            "Tom": "Tom",
            "Augustin": "Augustin"
        }

        # Types de commits basés sur les préfixes conventionnels
        type_map = {
            "feat": {"label": "Feature", "icon": "✨", "color": "green"},
            "fix": {"label": "Fix", "icon": "🐛", "color": "red"},
            "chore": {"label": "Maintenance", "icon": "🔧", "color": "blue"},
            "docs": {"label": "Documentation", "icon": "📝", "color": "purple"},
            "style": {"label": "Style", "icon": "💅", "color": "pink"},
            "refactor": {"label": "Refactor", "icon": "♻️", "color": "yellow"},
            "test": {"label": "Tests", "icon": "🧪", "color": "cyan"},
            "perf": {"label": "Performance", "icon": "⚡", "color": "orange"},
            "ci": {"label": "CI/CD", "icon": "🔄", "color": "gray"},
            "build": {"label": "Build", "icon": "📦", "color": "brown"}
        }

        for line in commits_raw:
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) < 4:
                continue

            commit_hash = parts[0][:7]
            author_raw = parts[1].strip()
            date_raw = parts[2][:10]
            message = parts[3].strip()

            # Mapper le nom d'auteur
            author = name_map.get(author_raw, author_raw.split()[0] if author_raw else "Unknown")

            # Détecter le type de commit
            commit_type = "other"
            for prefix, info in type_map.items():
                if message.lower().startswith(prefix + ":") or message.lower().startswith(prefix + "("):
                    commit_type = prefix
                    break

            # Nettoyer le message (enlever le préfixe)
            clean_message = message
            for prefix in type_map.keys():
                if message.lower().startswith(prefix + ":"):
                    clean_message = message[len(prefix)+1:].strip()
                    break
                elif message.lower().startswith(prefix + "("):
                    # Handle feat(scope): message
                    idx = message.find(":")
                    if idx > 0:
                        clean_message = message[idx+1:].strip()
                    break

            type_info = type_map.get(commit_type, {"label": "Autre", "icon": "📌", "color": "gray"})

            activity.append({
                "hash": commit_hash,
                "author": author,
                "date": date_raw,
                "message": clean_message[:80] + ("..." if len(clean_message) > 80 else ""),
                "type": commit_type,
                "type_label": type_info["label"],
                "type_icon": type_info["icon"],
                "type_color": type_info["color"]
            })

        return activity
    except Exception as e:
        print(f"Warning: Could not get recent activity: {e}", file=sys.stderr)
        return []


def get_dev_stats() -> dict:
    """Calcule les statistiques par développeur sur les 7 derniers jours."""
    try:
        # Commits des 7 derniers jours par auteur
        commits_7d = subprocess.check_output(
            ["git", "shortlog", "-sn", "--since=7 days ago"],
            cwd=PROJECT_ROOT,
            text=True
        ).strip().split("\n")

        name_map = {
            "AnandaTom": "Tom",
            "augustinfrance-aico": "Augustin",
            "Payoss": "Payoss"
        }

        stats = {}
        for line in commits_7d:
            if line.strip():
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    count = int(parts[0].strip())
                    author_raw = parts[1].strip()
                    author = name_map.get(author_raw, author_raw)
                    stats[author] = {"commits_7d": count}

        # Ajouter fichiers modifiés par dev (dernière semaine)
        for author in stats:
            stats[author]["files_changed"] = 0
            stats[author]["lines_added"] = 0

        return stats
    except Exception as e:
        print(f"Warning: Could not get dev stats: {e}", file=sys.stderr)
        return {}


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
    """Récupère les tâches du projet avec attribution développeur."""
    tasks = {
        "todo": [],
        "in_progress": [],
        "done": []
    }

    # Tâches terminées avec développeur (basées sur git blame/fichiers existants)
    done_indicators = [
        ("templates/vente_lots_copropriete.md", "Template vente 85% conformité", "Tom"),
        ("execution/workflow_rapide.py", "Pipeline génération rapide", "Tom"),
        ("docs/legal/REGISTRE_TRAITEMENTS.md", "Documentation RGPD", "Tom"),
        ("docs/legal/CGU_TEMPLATE.md", "Template CGU créé", "Tom"),
        (".mcp.json", "Intégration Supabase MCP", "Tom"),
        ("execution/historique_supabase.py", "Historique Supabase", "Payoss"),
        ("docs/index.html", "Dashboard v2.4 dynamique", "Tom"),
        ("execution/comparer_documents.py", "Comparaison conformité", "Tom"),
        ("execution/test_fiabilite.py", "Tests automatisés", "Payoss"),
        ("docs/legal/OBLIGATIONS_CSN.md", "Analyse obligations CSN", "Tom"),
        ("execution/generer_dashboard_data.py", "Script génération dashboard", "Tom"),
        (".github/workflows/update-dashboard.yml", "GitHub Actions auto-update", "Tom"),
    ]

    for item in done_indicators:
        path, task, dev = item[0], item[1], item[2] if len(item) > 2 else None
        if (PROJECT_ROOT / path).exists():
            tasks["done"].append({
                "task": task,
                "dev": dev,
                "path": path
            })

    # Tâches en cours avec assignation
    tasks["in_progress"] = [
        {"task": "Enrichir template promesse (60.9% → 80%)", "dev": "Tom", "progress": 60},
        {"task": "Formulaires web notaire", "dev": "Augustin", "progress": 40},
        {"task": "API backend génération", "dev": "Payoss", "progress": 30}
    ]

    # Tâches à faire avec priorité
    tasks["todo"] = [
        {"task": "Créer structure juridique (SAS/SASU)", "priority": "high", "assignee": None},
        {"task": "Souscrire RC Pro", "priority": "high", "assignee": None},
        {"task": "Valider CGU avec avocat", "priority": "medium", "assignee": None},
        {"task": "Template donation-partage", "priority": "medium", "assignee": "Tom"},
        {"task": "Intégration extraction titre propriété", "priority": "low", "assignee": "Payoss"},
        {"task": "Label ETIK (optionnel)", "priority": "low", "assignee": None}
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


def get_recommendations() -> dict:
    """Récupère les recommandations stratégiques par développeur."""

    # Analyse des templates pour déterminer les priorités dynamiques
    templates_dir = PROJECT_ROOT / "templates"
    promesse_conformity = 60.9  # Default

    # Vérifier si le fichier partie_developpee_promesse.md existe
    partie_dev_promesse_exists = (PROJECT_ROOT / "templates" / "sections" / "partie_developpee_promesse.md").exists()

    # Recommandations par priorité
    priorities = {
        "P0": {
            "label": "CRITIQUE",
            "color": "#ef4444",
            "items": []
        },
        "P1": {
            "label": "IMPORTANT",
            "color": "#f59e0b",
            "items": []
        },
        "P2": {
            "label": "NICE TO HAVE",
            "color": "#10b981",
            "items": []
        }
    }

    # P0 - Critique
    if not partie_dev_promesse_exists:
        priorities["P0"]["items"].append({
            "task": "Compléter template promesse (60.9% → 85%)",
            "dev": "Tom",
            "effort": "3j",
            "impact": 5,
            "details": "Créer sections/partie_developpee_promesse.md avec conditions suspensives, indemnité d'immobilisation"
        })

    # P1 - Important
    priorities["P1"]["items"].extend([
        {
            "task": "Intégrer validation dans l'agent",
            "dev": "Payoss",
            "effort": "2j",
            "impact": 4,
            "details": "Ajouter _valider_donnees() dans executer() avant génération"
        },
        {
            "task": "Support multi-parties (A & B → C)",
            "dev": "Payoss",
            "effort": "3j",
            "impact": 4,
            "details": "Parser 'Martin & Pierre → Dupont' avec PATTERN_FLECHE_MULTI"
        },
        {
            "task": "Formulaires web collecte données",
            "dev": "Augustin",
            "effort": "5j",
            "impact": 4,
            "details": "Interface React/Vue pour questionnaire notaire interactif"
        }
    ])

    # P2 - Nice to have
    priorities["P2"]["items"].extend([
        {
            "task": "Mode interactif agent",
            "dev": "Payoss",
            "effort": "3j",
            "impact": 3,
            "details": "Dialogue multi-tour avec questions/réponses"
        },
        {
            "task": "Suggestions contextuelles clauses",
            "dev": "Tom",
            "effort": "2j",
            "impact": 3,
            "details": "Suggérer clauses basées sur contexte (multi-acquéreurs, prix, etc.)"
        },
        {
            "task": "Dashboard analytics temps réel",
            "dev": "Augustin",
            "effort": "3j",
            "impact": 3,
            "details": "Graphiques d'utilisation, métriques génération"
        }
    ])

    # Recommandations par développeur
    dev_recommendations = {
        "Tom": {
            "role": "Lead Dev / Templates",
            "focus": "Templates & Conformité",
            "current_sprint": "Sprint 1",
            "priorities": [],
            "checklist": [
                {"item": "Ajouter {% include 'sections/partie_developpee_promesse.md' %}", "done": partie_dev_promesse_exists},
                {"item": "Créer sections spécifiques promesse", "done": partie_dev_promesse_exists},
                {"item": "Tester conformité ≥85%", "done": False},
                {"item": "Standardiser variables promesse/vente", "done": False}
            ],
            "next_actions": [
                "Créer partie_developpee_promesse.md avec conditions suspensives",
                "Ajouter indemnité d'immobilisation et délai réalisation",
                "Valider avec comparer_documents.py"
            ]
        },
        "Augustin": {
            "role": "Frontend / Formulaires",
            "focus": "Interface Utilisateur",
            "current_sprint": "Sprint 2",
            "priorities": [],
            "checklist": [
                {"item": "Maquette formulaire collecte", "done": False},
                {"item": "Composants React/Vue questionnaire", "done": False},
                {"item": "Intégration API backend", "done": False},
                {"item": "Validation côté client", "done": False}
            ],
            "next_actions": [
                "Designer wireframes formulaire notaire",
                "Créer composants pour 100+ questions",
                "Implémenter navigation conditionnelle"
            ]
        },
        "Payoss": {
            "role": "Backend / Scripts",
            "focus": "Agent & API",
            "current_sprint": "Sprint 1-2",
            "priorities": [],
            "checklist": [
                {"item": "Validation intégrée dans agent", "done": False},
                {"item": "Pattern multi-parties", "done": False},
                {"item": "Score confiance détaillé", "done": False},
                {"item": "API REST génération", "done": False}
            ],
            "next_actions": [
                "Ajouter _valider_donnees() dans agent_autonome.py",
                "Créer PATTERN_FLECHE_MULTI pour couples/indivisions",
                "Implémenter ScoreConfianceDetaille dataclass"
            ]
        }
    }

    # Assigner les priorités par dev
    for priority_key, priority_data in priorities.items():
        for item in priority_data["items"]:
            dev = item.get("dev")
            if dev and dev in dev_recommendations:
                dev_recommendations[dev]["priorities"].append({
                    **item,
                    "priority": priority_key,
                    "priority_label": priority_data["label"],
                    "priority_color": priority_data["color"]
                })

    # Sprints planning
    sprints = [
        {
            "name": "Sprint 1",
            "weeks": "Semaine 1-2",
            "objective": "Template promesse ≥85%",
            "status": "in_progress",
            "tasks": [
                {"task": "Compléter template promesse", "dev": "Tom", "effort": "3j", "status": "in_progress"},
                {"task": "Créer partie_developpee_promesse.md", "dev": "Tom", "effort": "2j", "status": "pending"},
                {"task": "Intégrer validation agent", "dev": "Payoss", "effort": "2j", "status": "pending"},
                {"task": "Tests génération promesse", "dev": "Payoss", "effort": "1j", "status": "pending"}
            ]
        },
        {
            "name": "Sprint 2",
            "weeks": "Semaine 3-4",
            "objective": "Agent gère 90% des cas",
            "status": "pending",
            "tasks": [
                {"task": "Support multi-parties", "dev": "Payoss", "effort": "3j", "status": "pending"},
                {"task": "Score confiance détaillé", "dev": "Payoss", "effort": "2j", "status": "pending"},
                {"task": "Formulaires web v1", "dev": "Augustin", "effort": "5j", "status": "pending"},
                {"task": "Documentation API", "dev": "Tom", "effort": "2j", "status": "pending"}
            ]
        },
        {
            "name": "Sprint 3",
            "weeks": "Semaine 5-6",
            "objective": "UX excellente, <2s",
            "status": "pending",
            "tasks": [
                {"task": "Mode interactif", "dev": "Payoss", "effort": "3j", "status": "pending"},
                {"task": "Suggestions contextuelles", "dev": "Tom", "effort": "2j", "status": "pending"},
                {"task": "Dashboard analytics", "dev": "Augustin", "effort": "3j", "status": "pending"},
                {"task": "Optimisations perf", "dev": "Payoss", "effort": "2j", "status": "pending"}
            ]
        }
    ]

    # Scores du système
    system_scores = {
        "architecture": {"score": 9, "max": 10, "label": "Architecture 3 couches"},
        "documentation": {"score": 8, "max": 10, "label": "Documentation"},
        "templates_vente": {"score": 8.5, "max": 10, "label": "Templates Vente"},
        "agent": {"score": 7, "max": 10, "label": "Agent Autonome"},
        "pipeline": {"score": 8, "max": 10, "label": "Pipeline Performance"}
    }

    # Faiblesses critiques
    weaknesses = [
        {"problem": "Template Promesse incomplet (60.9%)", "impact": "Bloque production", "priority": "P0"},
        {"problem": "Agent sans validation intégrée", "impact": "Erreurs silencieuses", "priority": "P1"},
        {"problem": "Pas de support multi-parties", "impact": "Limite cas réels", "priority": "P1"},
        {"problem": "Pas de dialogue multi-tour", "impact": "UX limitée", "priority": "P2"}
    ]

    return {
        "priorities": priorities,
        "dev_recommendations": dev_recommendations,
        "sprints": sprints,
        "system_scores": system_scores,
        "weaknesses": weaknesses,
        "source_file": "docs/RECOMMANDATIONS_STRATEGIQUES.md",
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }


def get_project_overview() -> dict:
    """Génère une vue d'ensemble complète du projet."""

    # Calculer le score de santé projet
    templates = analyze_templates()
    prod_templates = sum(1 for t in templates if t["status"] == "prod")
    avg_conformity = sum(t["conformity"] for t in templates) / len(templates) if templates else 0

    # Scores par domaine (0-100)
    tech_score = min(100, int(avg_conformity + (prod_templates / 4 * 20)))
    business_score = 30  # Pas encore de clients
    legal_score = 60  # RGPD fait, structure juridique manquante

    overall_score = int((tech_score * 0.4 + business_score * 0.3 + legal_score * 0.3))

    # Déterminer la phase
    if overall_score >= 80:
        phase = {"name": "Production", "color": "#10b981", "icon": "🚀"}
    elif overall_score >= 60:
        phase = {"name": "Beta", "color": "#06b6d4", "icon": "🔬"}
    elif overall_score >= 40:
        phase = {"name": "Alpha", "color": "#f59e0b", "icon": "⚙️"}
    else:
        phase = {"name": "MVP", "color": "#ef4444", "icon": "🔨"}

    # Milestones
    milestones = [
        {
            "name": "Architecture 3 couches",
            "status": "done",
            "date": "2025-12",
            "description": "Directives + Orchestration + Exécution"
        },
        {
            "name": "Templates Production",
            "status": "in_progress",
            "progress": int(prod_templates / 4 * 100),
            "description": f"{prod_templates}/4 templates ≥80% conformité"
        },
        {
            "name": "Premier client payant",
            "status": "blocked",
            "blocker": "Structure juridique requise",
            "description": "Objectif Q1 2026"
        },
        {
            "name": "10 clients actifs",
            "status": "pending",
            "description": "Objectif Q2 2026"
        }
    ]

    # OKRs du trimestre
    okrs = [
        {
            "objective": "Tous les templates en production",
            "key_results": [
                {"kr": "Template promesse ≥85%", "current": 60.9, "target": 85, "unit": "%"},
                {"kr": "Tests e2e couvrant 90% des cas", "current": 60, "target": 90, "unit": "%"},
                {"kr": "Temps génération <3s", "current": 5.7, "target": 3, "unit": "s", "lower_is_better": True}
            ]
        },
        {
            "objective": "Lancement commercial",
            "key_results": [
                {"kr": "Structure juridique créée", "current": 0, "target": 1, "unit": "done"},
                {"kr": "RC Pro souscrite", "current": 0, "target": 1, "unit": "done"},
                {"kr": "CGU validées avocat", "current": 0, "target": 1, "unit": "done"}
            ]
        },
        {
            "objective": "Acquisition premiers clients",
            "key_results": [
                {"kr": "Démos réalisées", "current": 0, "target": 5, "unit": ""},
                {"kr": "Clients signés", "current": 0, "target": 2, "unit": ""},
                {"kr": "MRR", "current": 0, "target": 500, "unit": "€"}
            ]
        }
    ]

    # Sprint actuel
    current_sprint = {
        "name": "Sprint 1",
        "start_date": "2026-01-27",
        "end_date": "2026-02-09",
        "days_remaining": 13,
        "progress": 25,
        "velocity_target": 20,
        "velocity_current": 5,
        "burndown": [
            {"day": 1, "remaining": 20, "ideal": 20},
            {"day": 2, "remaining": 18, "ideal": 18.5},
            {"day": 3, "remaining": 15, "ideal": 17}
        ],
        "blockers": [
            {"issue": "Template promesse incomplet", "assigned": "Tom", "severity": "high"},
        ],
        "risks": [
            {"risk": "Délai structure juridique", "probability": "high", "impact": "Bloque facturation"}
        ]
    }

    # Ce qui reste à faire (priorité décroissante)
    remaining_work = {
        "critical": [
            {"task": "Compléter template promesse", "effort": "3j", "assigned": "Tom"},
            {"task": "Créer structure juridique", "effort": "2j", "assigned": None}
        ],
        "important": [
            {"task": "Intégrer validation dans agent", "effort": "2j", "assigned": "Payoss"},
            {"task": "Souscrire RC Pro", "effort": "1j", "assigned": None},
            {"task": "Formulaires web v1", "effort": "5j", "assigned": "Augustin"}
        ],
        "nice_to_have": [
            {"task": "Mode interactif agent", "effort": "3j", "assigned": "Payoss"},
            {"task": "Dashboard analytics", "effort": "3j", "assigned": "Augustin"},
            {"task": "Label ETIK", "effort": "60j", "assigned": None}
        ]
    }

    # Suggestions intelligentes basées sur l'état
    suggestions = []

    if avg_conformity < 80:
        suggestions.append({
            "type": "tech",
            "priority": "high",
            "message": f"Conformité moyenne à {avg_conformity:.1f}% - Prioriser template promesse",
            "action": "Exécuter: python execution/comparer_documents.py"
        })

    if legal_score < 70:
        suggestions.append({
            "type": "business",
            "priority": "high",
            "message": "Structure juridique manquante - Bloque la facturation",
            "action": "Créer SASU via Legalstart ou Infogreffe"
        })

    if business_score < 50:
        suggestions.append({
            "type": "growth",
            "priority": "medium",
            "message": "Aucun client actif - Démarrer les démos",
            "action": "Contacter 3 notaires pour démo cette semaine"
        })

    suggestions.append({
        "type": "quick_win",
        "priority": "low",
        "message": "Documentation à jour - Continuer sur cette lancée",
        "action": "Maintenir CLAUDE.md et CHANGELOG.md"
    })

    return {
        "overall_score": overall_score,
        "phase": phase,
        "scores": {
            "tech": {"score": tech_score, "label": "Technique", "icon": "⚙️"},
            "business": {"score": business_score, "label": "Business", "icon": "💼"},
            "legal": {"score": legal_score, "label": "Juridique", "icon": "⚖️"}
        },
        "milestones": milestones,
        "okrs": okrs,
        "current_sprint": current_sprint,
        "remaining_work": remaining_work,
        "suggestions": suggestions,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


def get_chef_projet_briefing() -> dict:
    """Génère le briefing chef de projet avec priorités par développeur."""

    # Priorités par développeur
    dev_priorities = {
        "Tom": {
            "role": "Lead Dev / Templates",
            "focus": "Template Promesse",
            "color": "#6366f1",
            "this_week": [
                {
                    "task": "Compléter template promesse → 85%",
                    "priority": "critical",
                    "subtasks": [
                        "Créer partie_developpee_promesse.md",
                        "Ajouter conditions suspensives",
                        "Ajouter indemnité d'immobilisation",
                        "Tester avec comparer_documents.py"
                    ],
                    "deadline": "Vendredi",
                    "progress": 60
                }
            ],
            "quick_wins": [
                "Lancer comparer_documents.py sur promesses anonymisées",
                "Identifier sections manquantes dans docs_originels/"
            ],
            "blocked_by": None
        },
        "Augustin": {
            "role": "Frontend / Formulaires",
            "focus": "Maquette Formulaires",
            "color": "#06b6d4",
            "this_week": [
                {
                    "task": "Maquette formulaire collecte notaire",
                    "priority": "important",
                    "subtasks": [
                        "Identifier 20 questions critiques",
                        "Créer wireframe Figma/Excalidraw",
                        "Proposer navigation conditionnelle",
                        "Valider avec Tom"
                    ],
                    "deadline": "Mercredi",
                    "progress": 20
                }
            ],
            "quick_wins": [
                "Lire schemas/questions_promesse_vente.json",
                "Commencer par formulaire promesse (plus simple)"
            ],
            "blocked_by": None
        },
        "Payoss": {
            "role": "Backend / Chat / Modal",
            "focus": "Déploiement Modal",
            "color": "#10b981",
            "this_week": [
                {
                    "task": "Chat fonctionnel sur Modal",
                    "priority": "critical",
                    "subtasks": [
                        "Endpoint /generate qui appelle l'agent",
                        "Streaming de réponses",
                        "Gestion d'erreurs avec fallback",
                        "URL de démo partageable"
                    ],
                    "deadline": "Vendredi",
                    "progress": 30
                },
                {
                    "task": "Intégrer validation dans l'agent",
                    "priority": "important",
                    "subtasks": [
                        "Ajouter _valider_donnees() avant génération",
                        "Retourner erreurs structurées"
                    ],
                    "deadline": "Sprint 1",
                    "progress": 0
                }
            ],
            "quick_wins": [
                "Tester modal deploy modal_app.py",
                "Vérifier que le setup fonctionne"
            ],
            "blocked_by": None
        }
    }

    # Actions business urgentes
    business_actions = [
        {
            "action": "Créer SASU sur Legalstart",
            "effort": "2h + 150€",
            "impact": "Débloquer facturation",
            "owner": "Fondateur",
            "status": "todo",
            "url": "https://www.legalstart.fr/creation-entreprise/sasu/"
        },
        {
            "action": "Souscrire RC Pro",
            "effort": "1h + ~1000€/an",
            "impact": "Couvrir risques",
            "owner": "Fondateur",
            "status": "blocked",
            "blocked_by": "SASU",
            "options": ["MACSF", "Hiscox", "AXA"]
        },
        {
            "action": "Contacter 3 notaires pour démo",
            "effort": "2h",
            "impact": "Pipeline prospects",
            "owner": "Tom",
            "status": "todo"
        }
    ]

    # Objectifs fin de sprint
    sprint_objectives = [
        {"objective": "Template promesse ≥85% conformité", "owner": "Tom", "status": "in_progress"},
        {"objective": "Chat fonctionnel sur Modal", "owner": "Payoss", "status": "in_progress"},
        {"objective": "Maquette formulaire validée", "owner": "Augustin", "status": "in_progress"},
        {"objective": "SASU créée", "owner": "Business", "status": "todo"},
        {"objective": "1-2 démos notaires programmées", "owner": "Tom", "status": "pending"}
    ]

    # Rituels recommandés
    rituals = [
        {"name": "Daily async", "frequency": "Quotidien 9h", "duration": "2min", "format": "Slack: Hier/Aujourd'hui/Bloqué"},
        {"name": "Démo vendredi", "frequency": "Vendredi 14h", "duration": "30min", "format": "Call + screen share"},
        {"name": "Sprint review", "frequency": "Bi-hebdo", "duration": "45min", "format": "Rétro + planning"}
    ]

    # Alerte principale
    main_alert = {
        "type": "warning",
        "message": "Sans structure juridique, impossible de facturer. C'est le vrai bloqueur.",
        "action": "Créer SASU cette semaine",
        "icon": "⚠️"
    }

    return {
        "dev_priorities": dev_priorities,
        "business_actions": business_actions,
        "sprint_objectives": sprint_objectives,
        "rituals": rituals,
        "main_alert": main_alert,
        "week": "27 Janvier - 2 Février 2026",
        "sprint": "Sprint 1",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


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
    activity = get_recent_activity()
    dev_stats = get_dev_stats()
    recommendations = get_recommendations()
    overview = get_project_overview()
    chef_projet = get_chef_projet_briefing()

    # Calculer les métriques
    prod_templates = sum(1 for t in templates if t["status"] == "prod")
    avg_conformity = sum(t["conformity"] for t in templates) / len(templates) if templates else 0

    # Enrichir l'équipe avec les stats
    team = [
        {"name": "Tom", "branch": "tom/dev", "role": "Lead Dev / Templates", "status": "active"},
        {"name": "Augustin", "branch": "augustin/dev", "role": "Frontend / Formulaires", "status": "active"},
        {"name": "Payoss", "branch": "payoss/dev", "role": "Backend / Scripts", "status": "active"}
    ]
    for member in team:
        stats = dev_stats.get(member["name"], {})
        member["commits_7d"] = stats.get("commits_7d", 0)

    data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": "1.3.0",
            "dashboard_version": "2.5"
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
        "team": team,
        "activity": activity[:20],  # 20 dernières actions
        "recommendations": recommendations,
        "overview": overview,
        "chef_projet": chef_projet
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
