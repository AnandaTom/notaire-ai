#!/usr/bin/env python3
"""
Générateur de données pour le dashboard Notomai.
Analyse le codebase et génère des fichiers JSON pour le dashboard dynamique.

Lit la configuration depuis docs/data/project_config.json pour les valeurs
manuelles (conformité, tâches, OKRs) et calcule dynamiquement les métriques
automatiques (git, scripts, schémas).

Usage:
    python execution/generer_dashboard_data.py

Output:
    docs/data/dashboard.json - Données complètes du dashboard

Config source:
    docs/data/project_config.json - Valeurs configurables (conformité, tâches, etc.)
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
CONFIG_FILE = DOCS_DATA_DIR / "project_config.json"


def load_config() -> dict:
    """Charge la configuration depuis project_config.json."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)
    return {}


# Charger la config au démarrage
CONFIG = load_config()


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
    """Analyse les templates et leur conformité.

    Lit les valeurs de conformité depuis CONFIG['templates'] (project_config.json).
    Les métriques dynamiques (lignes, date de modification) sont calculées en live.
    """
    templates_dir = PROJECT_ROOT / "templates"
    templates = []

    # Fallback hardcodé si pas de config
    default_info = {
        "vente_lots_copropriete.md": {
            "name": "Vente lots copropriété",
            "conformity": 80.2,
            "status": "prod",
            "bookmarks": 361,
            "sections": 37
        },
        "promesse_vente_lots_copropriete.md": {
            "name": "Promesse de vente",
            "conformity": 94.3,
            "status": "prod",
            "bookmarks": 298,
            "sections": 165
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

    # Utiliser la config si disponible, sinon les valeurs par défaut
    config_templates = CONFIG.get("templates", {})

    for template_file, fallback in default_info.items():
        template_path = templates_dir / template_file

        # Lire depuis config ou utiliser fallback
        cfg = config_templates.get(template_file, fallback)
        info = {
            "name": cfg.get("name", fallback["name"]),
            "conformity": cfg.get("conformity", fallback["conformity"]),
            "status": cfg.get("status", fallback["status"]),
            "bookmarks": cfg.get("bookmarks", fallback["bookmarks"]),
            "sections": cfg.get("sections", fallback["sections"]),
        }

        if template_path.exists():
            # Métriques dynamiques
            with open(template_path, "r", encoding="utf-8") as f:
                lines = len(f.readlines())
            mtime = datetime.fromtimestamp(template_path.stat().st_mtime)

            templates.append({
                "file": template_file,
                **info,
                "trames_source": cfg.get("trames_source", 1),
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
    """Récupère les tâches du projet depuis la config.

    Source: CONFIG['tasks'] dans project_config.json.
    Pour mettre à jour les tâches, éditer docs/data/project_config.json.
    """
    config_tasks = CONFIG.get("tasks", {})

    if config_tasks:
        return {
            "todo": config_tasks.get("todo", []),
            "in_progress": config_tasks.get("in_progress", []),
            "done": config_tasks.get("done", [])
        }

    # Fallback si pas de config
    return {
        "todo": [
            {"task": "Créer structure juridique (SAS/SASU)", "priority": "high", "assignee": None},
            {"task": "Souscrire RC Pro", "priority": "high", "assignee": None},
        ],
        "in_progress": [],
        "done": []
    }


def get_capabilities() -> list:
    """Liste les capacités du système depuis la config."""
    config_caps = CONFIG.get("capabilities", None)
    if config_caps:
        return config_caps

    return [
        {"icon": "📄", "name": "Générer actes", "description": "4 types: vente, promesse, EDD, modificatif", "active": True},
        {"icon": "💬", "name": "Dialogue notaire", "description": "Collecte interactive 100+ questions", "active": True},
        {"icon": "✅", "name": "Validation", "description": "Cohérence et complétude", "active": True},
        {"icon": "🔍", "name": "Détection auto", "description": "Type d'acte + type promesse", "active": True},
        {"icon": "💡", "name": "Suggestions", "description": "Clauses contextuelles intelligentes", "active": True},
        {"icon": "📊", "name": "Conformité", "description": "Score automatique vs 7 trames", "active": True},
        {"icon": "🗄️", "name": "Historique", "description": "Supabase + chiffrement E2E", "active": True},
        {"icon": "⚡", "name": "Pipeline rapide", "description": "~6 secondes / acte", "active": True},
        {"icon": "📑", "name": "Extraction titre", "description": "PDF/DOCX vers JSON (OCR+ML)", "active": True},
        {"icon": "🔄", "name": "Workflow chaîné", "description": "Titre vers Promesse vers Vente", "active": True},
        {"icon": "🔐", "name": "Sécurité RGPD", "description": "Anonymisation + chiffrement AES-256", "active": True},
    ]


def get_recommendations() -> dict:
    """Récupère les recommandations stratégiques.

    Lit les scores système et faiblesses depuis CONFIG.
    Les priorités sont calculées dynamiquement selon l'état du projet.
    """
    # Scores depuis config
    system_scores = CONFIG.get("system_scores", {
        "architecture": {"score": 9.5, "max": 10, "label": "Architecture 3 couches"},
        "documentation": {"score": 9, "max": 10, "label": "Documentation"},
        "templates_promesse": {"score": 9.4, "max": 10, "label": "Templates Promesse"},
        "templates_vente": {"score": 8, "max": 10, "label": "Templates Vente"},
        "agent": {"score": 8, "max": 10, "label": "Agent Autonome"},
        "pipeline": {"score": 8.5, "max": 10, "label": "Pipeline Performance"},
        "securite": {"score": 9.5, "max": 10, "label": "Sécurité & RGPD"}
    })

    # Faiblesses depuis config
    weaknesses = CONFIG.get("weaknesses", [
        {"problem": "Pas de validation conjoint/diagnostics", "impact": "Erreurs possibles", "priority": "P1"},
        {"problem": "Template vente conformité 80.2%", "impact": "Marge d'amélioration", "priority": "P2"}
    ])

    # Priorités calculées dynamiquement
    config_templates = CONFIG.get("templates", {})
    promesse_cfg = config_templates.get("promesse_vente_lots_copropriete.md", {})
    promesse_conformity = promesse_cfg.get("conformity", 94.3)
    vente_cfg = config_templates.get("vente_lots_copropriete.md", {})
    vente_conformity = vente_cfg.get("conformity", 80.2)

    priorities = {
        "P0": {"label": "CRITIQUE", "color": "#ef4444", "items": []},
        "P1": {"label": "IMPORTANT", "color": "#f59e0b", "items": []},
        "P2": {"label": "NICE TO HAVE", "color": "#10b981", "items": []}
    }

    # P0 - Auto-détection des problèmes critiques
    if promesse_conformity < 80:
        priorities["P0"]["items"].append({
            "task": f"Template promesse à {promesse_conformity}% - Enrichir",
            "dev": "Tom", "impact": 5
        })
    if vente_conformity < 80:
        priorities["P0"]["items"].append({
            "task": f"Template vente à {vente_conformity}% - Enrichir",
            "dev": "Tom", "impact": 5
        })

    # P1 - Prochaines priorités
    priorities["P1"]["items"].extend([
        {"task": "Validation métier avancée (conjoint, diagnostics)", "dev": "Tom", "impact": 4},
        {"task": "API backend + Chat Modal", "dev": "Payoss", "impact": 4},
        {"task": "Formulaires web v2", "dev": "Augustin", "impact": 4}
    ])

    if vente_conformity < 85:
        priorities["P1"]["items"].append({
            "task": f"Améliorer vente ({vente_conformity}% → 85%+)", "dev": "Tom", "impact": 4
        })

    # P2
    priorities["P2"]["items"].extend([
        {"task": "Template donation-partage", "dev": "Tom", "impact": 3},
        {"task": "Dashboard analytics temps réel", "dev": "Augustin", "impact": 3},
        {"task": "Optimisation performance (<3s)", "dev": "Payoss", "impact": 3}
    ])

    # Sprint depuis config
    config_sprint = CONFIG.get("sprint", {})
    sprints = [
        {
            "name": "Sprint 1",
            "weeks": "Semaine 1-2",
            "objective": "Template promesse ≥85%",
            "status": "done",
            "tasks": [
                {"task": "Template promesse 94.3%", "dev": "Tom", "status": "done"},
                {"task": "Enrichissement 7 trames", "dev": "Tom", "status": "done"},
                {"task": "Validation intégrée agent", "dev": "Tom", "status": "done"},
                {"task": "Support multi-parties", "dev": "Tom", "status": "done"}
            ]
        },
        {
            "name": config_sprint.get("name", "Sprint 2"),
            "weeks": "Semaine 3-4",
            "objective": config_sprint.get("objective", "API + Formulaires + Validation métier"),
            "status": config_sprint.get("status", "in_progress"),
            "tasks": config_sprint.get("tasks", [
                {"task": "Validation métier avancée", "dev": "Tom", "status": "pending"},
                {"task": "API backend", "dev": "Payoss", "status": "in_progress"},
                {"task": "Chat Modal", "dev": "Payoss", "status": "in_progress"},
                {"task": "Formulaires web v2", "dev": "Augustin", "status": "in_progress"}
            ])
        },
        {
            "name": "Sprint 3",
            "weeks": "Semaine 5-6",
            "objective": "UX excellente, donation-partage",
            "status": "pending",
            "tasks": [
                {"task": "Template donation-partage", "dev": "Tom", "status": "pending"},
                {"task": "Dashboard analytics", "dev": "Augustin", "status": "pending"},
                {"task": "Optimisations perf", "dev": "Payoss", "status": "pending"}
            ]
        }
    ]

    return {
        "priorities": priorities,
        "sprints": sprints,
        "system_scores": system_scores,
        "weaknesses": weaknesses,
        "source_file": "docs/data/project_config.json",
        "last_updated": datetime.now().strftime("%Y-%m-%d")
    }


def get_project_overview() -> dict:
    """Génère une vue d'ensemble complète du projet.

    Calcule dynamiquement le score de santé, lit les OKRs depuis CONFIG.
    """
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

    # Milestones dynamiques
    milestones = [
        {
            "name": "Architecture 3 couches",
            "status": "done",
            "date": "2025-12",
            "description": "Directives + Orchestration + Exécution"
        },
        {
            "name": "Templates Production",
            "status": "done" if prod_templates == 4 else "in_progress",
            "progress": int(prod_templates / 4 * 100),
            "description": f"{prod_templates}/4 templates >=80% conformite"
        },
        {
            "name": "Enrichissement 7 trames promesse",
            "status": "done",
            "date": "2026-01",
            "description": f"Promesse a {avg_conformity:.1f}% conformite (v3.0.0)"
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

    # OKRs depuis config
    okrs = CONFIG.get("okrs", [
        {
            "objective": "Tous les templates en production",
            "key_results": [
                {"kr": "Template promesse >=85%", "current": 94.3, "target": 85, "unit": "%"},
                {"kr": "Template vente >=85%", "current": 80.2, "target": 85, "unit": "%"},
                {"kr": "Tests e2e couvrant 90% des cas", "current": 75, "target": 90, "unit": "%"},
                {"kr": "Temps generation <3s", "current": 5.7, "target": 3, "unit": "s", "lower_is_better": True}
            ]
        }
    ])

    # Sprint depuis config
    config_sprint = CONFIG.get("sprint", {})
    current_sprint = {
        "name": config_sprint.get("name", "Sprint 2"),
        "start_date": config_sprint.get("start_date", "2026-01-27"),
        "end_date": config_sprint.get("end_date", "2026-02-09"),
        "objective": config_sprint.get("objective", "API + Formulaires + Validation metier"),
        "status": config_sprint.get("status", "in_progress"),
        "blockers": [
            {"issue": "Structure juridique manquante", "assigned": "Fondateur", "severity": "high"},
        ],
        "risks": [
            {"risk": "Delai structure juridique", "probability": "high", "impact": "Bloque facturation"}
        ]
    }

    # Ce qui reste a faire
    remaining_work = {
        "critical": [
            {"task": "Creer structure juridique", "assigned": None},
            {"task": "Souscrire RC Pro", "assigned": None},
            {"task": "Validation metier avancee (conjoint, diagnostics)", "assigned": "Tom"}
        ],
        "important": [
            {"task": "Ameliorer template vente (80.2% -> 85%+)", "assigned": "Tom"},
            {"task": "API backend + Chat Modal", "assigned": "Payoss"},
            {"task": "Formulaires web v2", "assigned": "Augustin"},
            {"task": "Documentation API frontend", "assigned": "Tom"}
        ],
        "nice_to_have": [
            {"task": "Template donation-partage", "assigned": "Tom"},
            {"task": "Dashboard analytics", "assigned": "Augustin"},
            {"task": "Label ETIK", "assigned": None}
        ]
    }

    # Suggestions intelligentes basees sur l'etat
    suggestions = []

    if avg_conformity >= 85:
        suggestions.append({
            "type": "tech",
            "priority": "low",
            "message": f"Conformite moyenne a {avg_conformity:.1f}% - Excellent! 4/4 templates en prod.",
            "action": "Focus sur validation metier et optimisations"
        })
    elif avg_conformity < 80:
        suggestions.append({
            "type": "tech",
            "priority": "high",
            "message": f"Conformite moyenne a {avg_conformity:.1f}% - Enrichir les templates",
            "action": "Executer: python execution/analyse/comparer_documents.py"
        })

    if legal_score < 70:
        suggestions.append({
            "type": "business",
            "priority": "high",
            "message": "Structure juridique manquante - Bloque la facturation",
            "action": "Creer SASU via Legalstart ou Infogreffe"
        })

    if business_score < 50:
        suggestions.append({
            "type": "growth",
            "priority": "medium",
            "message": "Aucun client actif - Demarrer les demos",
            "action": "Contacter 3 notaires pour demo cette semaine"
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
    """Génère le briefing chef de projet.

    Utilise les données dynamiques (conformité templates) et la config.
    """
    # Lire conformité actuelle pour contexte
    config_templates = CONFIG.get("templates", {})
    promesse_conf = config_templates.get("promesse_vente_lots_copropriete.md", {}).get("conformity", 94.3)
    vente_conf = config_templates.get("vente_lots_copropriete.md", {}).get("conformity", 80.2)

    dev_priorities = {
        "Tom": {
            "role": "Lead Dev / Templates",
            "focus": "Validation metier + Vente",
            "color": "#6366f1",
            "this_week": [
                {
                    "task": "Validation metier avancee",
                    "priority": "critical",
                    "subtasks": [
                        "Validation conjoint (communaute)",
                        "Validation diagnostics expires",
                        "Validation coherence dates",
                        "Tests unitaires"
                    ],
                    "progress": 0
                },
                {
                    "task": f"Ameliorer template vente ({vente_conf}% -> 85%+)",
                    "priority": "important",
                    "subtasks": [
                        "Analyser sections manquantes vs trame originale",
                        "Ajouter sections agent immobilier, plus-value",
                        "Tester conformite"
                    ],
                    "progress": 0
                }
            ],
            "achievements": [
                f"Template promesse a {promesse_conf}% (objectif 85% depasse!)",
                "Enrichissement depuis 7 trames originales",
                "40+ nouvelles sections ajoutees (v3.0.0)",
                "7 bugs templates corriges"
            ],
            "blocked_by": None
        },
        "Augustin": {
            "role": "Frontend / Formulaires",
            "focus": "Formulaires web v2",
            "color": "#06b6d4",
            "this_week": [
                {
                    "task": "Formulaires web collecte notaire v2",
                    "priority": "important",
                    "subtasks": [
                        "Composants React/Vue questionnaire",
                        "Navigation conditionnelle",
                        "Integration API backend",
                        "Validation cote client"
                    ],
                    "progress": 50
                }
            ],
            "achievements": [
                "Systeme formulaires clients securises",
                "Dashboard notaire HTML"
            ],
            "blocked_by": None
        },
        "Payoss": {
            "role": "Backend / Chat / Modal",
            "focus": "API + Chat Modal",
            "color": "#10b981",
            "this_week": [
                {
                    "task": "Chat fonctionnel sur Modal",
                    "priority": "critical",
                    "subtasks": [
                        "Endpoint /generate qui appelle l'agent",
                        "Streaming de reponses",
                        "Gestion d'erreurs avec fallback",
                        "URL de demo partageable"
                    ],
                    "progress": 30
                },
                {
                    "task": "API backend generation",
                    "priority": "important",
                    "subtasks": [
                        "Endpoints promesse/vente",
                        "Validation donnees API",
                        "Documentation OpenAPI"
                    ],
                    "progress": 40
                }
            ],
            "achievements": [
                "Historique Supabase",
                "Tests automatises"
            ],
            "blocked_by": None
        }
    }

    business_actions = [
        {
            "action": "Creer SASU sur Legalstart",
            "impact": "Debloquer facturation",
            "owner": "Fondateur",
            "status": "todo"
        },
        {
            "action": "Souscrire RC Pro",
            "impact": "Couvrir risques",
            "owner": "Fondateur",
            "status": "blocked",
            "blocked_by": "SASU"
        },
        {
            "action": "Contacter 3 notaires pour demo",
            "impact": "Pipeline prospects",
            "owner": "Tom",
            "status": "todo"
        }
    ]

    sprint_objectives = [
        {"objective": f"Template promesse >=85% conformite", "owner": "Tom", "status": "done",
         "result": f"{promesse_conf}%"},
        {"objective": "Chat fonctionnel sur Modal", "owner": "Payoss", "status": "in_progress"},
        {"objective": "Formulaires web v2", "owner": "Augustin", "status": "in_progress"},
        {"objective": "Validation metier avancee", "owner": "Tom", "status": "pending"},
        {"objective": "SASU creee", "owner": "Business", "status": "todo"}
    ]

    main_alert = {
        "type": "success",
        "message": f"Template promesse a {promesse_conf}% - Objectif Sprint 1 depasse! 4/4 templates en PROD.",
        "action": "Focus: structure juridique + API + validation metier",
        "icon": "🎉"
    }

    return {
        "dev_priorities": dev_priorities,
        "business_actions": business_actions,
        "sprint_objectives": sprint_objectives,
        "main_alert": main_alert,
        "sprint": CONFIG.get("sprint", {}).get("name", "Sprint 2"),
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

    config_version = CONFIG.get("version", "1.5.0")
    dashboard_version = CONFIG.get("dashboard_version", "3.0")

    data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": config_version,
            "dashboard_version": dashboard_version,
            "config_source": "docs/data/project_config.json"
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
        "chef_projet": chef_projet,
        "conformity_details": CONFIG.get("conformity_details", {})
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
