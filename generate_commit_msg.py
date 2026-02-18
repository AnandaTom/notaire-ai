#!/usr/bin/env python3
"""
Generateur de commit messages a partir du journal de bord.

Lit memory/JOURNAL.md (entree du jour), git diff --cached --stat,
et produit un commit message structure que les autres agents peuvent parser.

Usage:
    python generate_commit_msg.py              # Genere le message dans .tmp/commit_msg.txt
    python generate_commit_msg.py --preview    # Affiche sans ecrire
    python generate_commit_msg.py --dev "Tom"  # Force le nom du dev
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# Fix Windows UTF-8
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

JOURNAL_PATH = Path("memory/JOURNAL.md")
OUTPUT_PATH = Path(".tmp/commit_msg.txt")
ISSUES_PATH = Path("memory/ISSUES.md")


def get_branch():
    """Retourne le nom de la branche courante."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_dev_from_branch(branch):
    """Extrait le nom du dev depuis la branche (tom/dev -> Tom, payoss/dev -> Payoss)."""
    match = re.match(r"^([^/]+)/", branch)
    if match:
        return match.group(1).capitalize()
    return branch


def get_diff_stat():
    """Retourne le git diff --cached --stat."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_diff_files():
    """Retourne la liste des fichiers stages avec leur status."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status"],
        capture_output=True, text=True
    )
    files = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            status_label = {"A": "CREE", "M": "MODIFIE", "D": "SUPPRIME", "R": "RENOMME"}.get(status[0], status)
            files.append((status_label, path))
    return files


def extract_today_journal(date_str=None, dev_name=None):
    """Extrait les entrees du journal pour aujourd'hui et ce dev.

    Format attendu: ## YYYY-MM-DD (optionnel) — Dev (Prenom)
    Si dev_name fourni, ne retourne que les entrees de ce dev.
    """
    if not JOURNAL_PATH.exists():
        return None

    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    content = JOURNAL_PATH.read_text(encoding="utf-8")

    # Decouper en blocs par entete ## YYYY-MM-DD
    blocks = re.split(r"(?=\n## \d{4}-\d{2}-\d{2})", content)

    matching = []
    for block in blocks:
        block = block.strip()
        if not block.startswith("## " + date_str):
            continue

        if dev_name:
            header = block.split("\n")[0]
            # Extraire tout apres le tiret long: "Paul (Payoss)", "Tom", etc.
            dev_match = re.search(r"[—–-]\s*(.+)$", header)
            if dev_match:
                found_dev = dev_match.group(1).lower()
                if dev_name.lower() not in found_dev:
                    continue

        matching.append(block)

    return "\n\n---\n\n".join(matching) if matching else None


def extract_summary_from_journal(journal_entry):
    """Extrait un resume structure depuis l'entree du journal."""
    if not journal_entry:
        return {}

    result = {
        "contexte": "",
        "actions": [],
        "decouvertes": [],
        "erreurs": [],
        "build": "",
    }

    current_section = None
    for line in journal_entry.split("\n"):
        line_stripped = line.strip()

        if line_stripped.startswith("### Contexte"):
            current_section = "contexte"
            continue
        elif line_stripped.startswith("### Ce qui a ete fait"):
            current_section = "actions"
            continue
        elif line_stripped.startswith("### Decouvertes"):
            current_section = "decouvertes"
            continue
        elif line_stripped.startswith("### Erreurs"):
            current_section = "erreurs"
            continue
        elif line_stripped.startswith("### Build") or line_stripped.startswith("### Tests"):
            current_section = "build"
            continue
        elif line_stripped.startswith("### "):
            current_section = None
            continue

        if not line_stripped or line_stripped.startswith("|---"):
            continue

        if current_section == "contexte" and line_stripped and not line_stripped.startswith("|"):
            if line_stripped.startswith("- "):
                result["contexte"] += line_stripped[2:] + " "
            elif result["contexte"] and not line_stripped.startswith("#"):
                result["contexte"] += line_stripped + " "

        elif current_section == "actions" and line_stripped.startswith("|") and "Action" not in line_stripped:
            cols = [c.strip() for c in line_stripped.split("|") if c.strip()]
            if len(cols) >= 3:
                result["actions"].append({"action": cols[0], "fichier": cols[1], "detail": cols[2]})

        elif current_section == "decouvertes" and line_stripped:
            if line_stripped.startswith(("- ", "* ")) or re.match(r"^\d+\.", line_stripped):
                clean = re.sub(r"^[\d\.\-\*\s]+", "", line_stripped).strip()
                if clean:
                    result["decouvertes"].append(clean)

        elif current_section == "build" and line_stripped:
            if line_stripped.startswith("- "):
                result["build"] += line_stripped[2:] + " "

    result["contexte"] = result["contexte"].strip()
    result["build"] = result["build"].strip()
    return result


def count_open_issues():
    """Compte les issues ouvertes par severite."""
    if not ISSUES_PATH.exists():
        return {}

    content = ISSUES_PATH.read_text(encoding="utf-8")
    counts = {}
    current_severity = None

    for line in content.split("\n"):
        if line.startswith("### CRITIQUE"):
            current_severity = "CRITIQUE"
        elif line.startswith("### IMPORTANT"):
            current_severity = "IMPORTANT"
        elif line.startswith("### MOYEN"):
            current_severity = "MOYEN"
        elif line.startswith("## Fermes"):
            break
        elif current_severity and line.startswith("| ") and not line.startswith("| ID"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if cols and re.match(r"^[CIM]-\d+$", cols[0]):
                counts[current_severity] = counts.get(current_severity, 0) + 1

    return counts


def generate_commit_message(dev_name=None):
    """Genere le commit message complet."""
    branch = get_branch()
    dev = dev_name or get_dev_from_branch(branch)
    today = datetime.now().strftime("%Y-%m-%d")
    diff_files = get_diff_files()

    # Categoriser les fichiers
    created = [f for s, f in diff_files if s == "CREE"]
    modified = [f for s, f in diff_files if s == "MODIFIE"]
    deleted = [f for s, f in diff_files if s == "SUPPRIME"]

    # Lire le journal (filtre par dev pour eviter conflits multi-devs)
    journal_entry = extract_today_journal(today, dev_name=dev)
    summary = extract_summary_from_journal(journal_entry) if journal_entry else {}

    # --- Construire le message ---

    # Ligne 1: sujet (court, parseable)
    file_count = len(diff_files)
    if summary.get("contexte"):
        # Tronquer le contexte pour le sujet
        ctx = summary["contexte"]
        if len(ctx) > 60:
            ctx = ctx[:57] + "..."
        subject = f"[{dev}] {ctx}"
    else:
        subject = f"[{dev}] Travail du {today} ({file_count} fichiers)"

    lines = [subject, ""]

    # Section DEV (pour identification inter-agents)
    lines.append(f"Dev: {dev}")
    lines.append(f"Branche: {branch}")
    lines.append(f"Date: {today}")
    lines.append("")

    # Section FICHIERS
    if diff_files:
        lines.append("## Fichiers modifies")
        for status, path in diff_files:
            lines.append(f"- [{status}] {path}")
        lines.append("")

    # Section CE QUI A ETE FAIT (depuis le journal)
    if summary.get("actions"):
        lines.append("## Ce qui a ete fait")
        for action in summary["actions"]:
            lines.append(f"- {action['action']} {action['fichier']}: {action['detail']}")
        lines.append("")
    elif summary.get("contexte"):
        lines.append("## Ce qui a ete fait")
        lines.append(f"- {summary['contexte']}")
        lines.append("")

    # Section DECOUVERTES
    if summary.get("decouvertes"):
        lines.append("## Decouvertes")
        for d in summary["decouvertes"][:5]:  # Max 5
            lines.append(f"- {d}")
        lines.append("")

    # Section BUILD/TESTS
    if summary.get("build"):
        lines.append(f"## Build: {summary['build']}")
        lines.append("")

    # Section ISSUES
    issues = count_open_issues()
    if issues:
        issue_parts = [f"{count} {sev.lower()}" for sev, count in issues.items()]
        lines.append(f"## Issues ouvertes: {', '.join(issue_parts)}")
        lines.append("")

    # Si pas de journal du tout, au moins lister les fichiers modifies par domaine
    if not journal_entry and diff_files:
        domains = {}
        for _, path in diff_files:
            domain = path.split("/")[0] if "/" in path else "root"
            domains.setdefault(domain, []).append(path)

        lines.append("## Resume par domaine")
        for domain, files in sorted(domains.items()):
            lines.append(f"- {domain}/: {len(files)} fichier(s)")
        lines.append("")

    return "\n".join(lines).strip()


def main():
    preview = "--preview" in sys.argv
    dev_name = None
    if "--dev" in sys.argv:
        idx = sys.argv.index("--dev")
        if idx + 1 < len(sys.argv):
            dev_name = sys.argv[idx + 1]

    message = generate_commit_message(dev_name)

    if preview:
        print("=== COMMIT MESSAGE PREVIEW ===")
        print(message)
        print("=== FIN PREVIEW ===")
    else:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(message, encoding="utf-8")
        print(f"Commit message genere: {OUTPUT_PATH}")
        print(f"Sujet: {message.split(chr(10))[0]}")


if __name__ == "__main__":
    main()
