#!/usr/bin/env python3
"""
Lecture des commits des autres developpeurs pour eviter les doublons.

Lit les commits recents de TOUTES les branches (sauf la branche courante)
et genere un resume parseable par les agents IA.

Usage:
    python read_team_commits.py                   # Commits des dernieres 24h
    python read_team_commits.py --days 3          # Commits des 3 derniers jours
    python read_team_commits.py --output resume   # Ecrit dans .tmp/team_commits.md
    python read_team_commits.py --branch tom/dev  # Exclut cette branche
"""

import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows UTF-8
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_PATH = Path(".tmp/team_commits.md")


def run_git(*args):
    """Execute une commande git et retourne stdout."""
    result = subprocess.run(
        ["git"] + list(args),
        capture_output=True, text=True
    )
    return result.stdout.strip()


def get_current_branch():
    return run_git("rev-parse", "--abbrev-ref", "HEAD")


def get_all_remote_branches():
    """Retourne toutes les branches remote."""
    output = run_git("branch", "-r", "--format=%(refname:short)")
    branches = []
    for line in output.split("\n"):
        line = line.strip()
        if line and "HEAD" not in line:
            branches.append(line)
    return branches


def get_commits_since(branch, since_date, current_branch):
    """Retourne les commits d'une branche depuis une date."""
    # Exclure la branche courante
    branch_short = branch.replace("origin/", "")
    if branch_short == current_branch:
        return []

    output = run_git(
        "log", branch,
        f"--since={since_date}",
        "--format=%H|%an|%ai|%s%n%b%n---COMMIT_END---",
        "--no-merges"
    )

    if not output.strip():
        return []

    commits = []
    for block in output.split("---COMMIT_END---"):
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        if not lines:
            continue

        header = lines[0]
        parts = header.split("|", 3)
        if len(parts) < 4:
            continue

        sha, author, date, subject = parts
        body = "\n".join(lines[1:]).strip()

        commits.append({
            "sha": sha[:8],
            "author": author,
            "date": date[:10],
            "subject": subject,
            "body": body,
            "branch": branch_short,
        })

    return commits


def extract_dev_name(commit):
    """Extrait le nom du dev depuis le sujet [Dev], l'auteur git, ou la branche."""
    # 1. Tag [Dev] dans le sujet du commit (format END_DAY v3)
    match = re.match(r"^\[(\w+)\]", commit["subject"])
    if match:
        return match.group(1)

    # 2. Branche dev personnelle (tom/dev, payoss/dev, augustin/dev)
    branch = commit["branch"]
    dev_match = re.match(r"^(?:origin/)?(\w+)/dev", branch)
    if dev_match:
        return dev_match.group(1).capitalize()

    # 3. Auteur git (prenom)
    if commit.get("author"):
        return commit["author"].split()[0]

    # 4. Fallback
    return branch.replace("origin/", "").split("/")[0].capitalize()


def extract_files_from_body(body):
    """Extrait les fichiers mentionnes dans le corps du commit."""
    files = []
    for line in body.split("\n"):
        line = line.strip()
        match = re.match(r"^- \[(\w+)\] (.+)$", line)
        if match:
            files.append((match.group(1), match.group(2)))
    return files


def extract_actions_from_body(body):
    """Extrait les actions depuis le corps du commit."""
    actions = []
    in_actions = False
    for line in body.split("\n"):
        line = line.strip()
        if line == "## Ce qui a ete fait":
            in_actions = True
            continue
        elif line.startswith("## "):
            in_actions = False
            continue
        if in_actions and line.startswith("- "):
            actions.append(line[2:])
    return actions


def generate_team_summary(days=1, current_branch_override=None):
    """Genere le resume des commits de l'equipe."""
    current = current_branch_override or get_current_branch()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    branches = get_all_remote_branches()

    all_commits = []
    for branch in branches:
        commits = get_commits_since(branch, since, current)
        all_commits.extend(commits)

    # Deduplication par SHA + filtrage auto-commits
    SKIP_PATTERNS = ["[skip ci]", "auto-update dashboard", "chore: auto-update"]
    seen = set()
    unique_commits = []
    for c in all_commits:
        if c["sha"] not in seen:
            seen.add(c["sha"])
            # Ignorer les commits auto-generes (dashboard, CI)
            if any(p.lower() in c["subject"].lower() for p in SKIP_PATTERNS):
                continue
            unique_commits.append(c)

    # Trier par date (plus recent d'abord)
    unique_commits.sort(key=lambda c: c["date"], reverse=True)

    # Grouper par dev
    by_dev = {}
    for c in unique_commits:
        dev = extract_dev_name(c)
        by_dev.setdefault(dev, []).append(c)

    # Generer le resume
    lines = [
        f"# Resume equipe - Commits des {days} dernier(s) jour(s)",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Branche courante: {current}",
        f"Commits trouves: {len(unique_commits)} (hors branche courante)",
        "",
    ]

    if not unique_commits:
        lines.append("Aucun commit des autres devs dans cette periode.")
        lines.append("")
        lines.append("Vous pouvez travailler librement sans risque de doublon.")
        return "\n".join(lines)

    for dev, commits in sorted(by_dev.items()):
        lines.append(f"## {dev} ({len(commits)} commit(s))")
        lines.append("")

        for c in commits:
            lines.append(f"### {c['sha']} - {c['subject']}")
            lines.append(f"Branche: {c['branch']} | Date: {c['date']}")

            # Extraire les actions si disponibles
            actions = extract_actions_from_body(c["body"])
            if actions:
                lines.append("Actions:")
                for a in actions[:10]:
                    lines.append(f"  - {a}")

            # Extraire les fichiers si disponibles
            files = extract_files_from_body(c["body"])
            if files:
                lines.append("Fichiers:")
                for status, path in files[:15]:
                    lines.append(f"  - [{status}] {path}")

            lines.append("")

    # Avertissements de chevauchement
    all_files_touched = set()
    files_by_dev = {}
    for dev, commits in by_dev.items():
        dev_files = set()
        for c in commits:
            for _, path in extract_files_from_body(c["body"]):
                dev_files.add(path)
                all_files_touched.add(path)
        files_by_dev[dev] = dev_files

    # Detecter les fichiers touches par plusieurs devs
    current_dev = current.split("/")[0].capitalize()
    conflicts = []
    for dev, dev_files in files_by_dev.items():
        if dev.lower() != current_dev.lower():
            for f in dev_files:
                conflicts.append((f, dev))

    if conflicts:
        lines.append("## ATTENTION - Fichiers touches par d'autres devs")
        lines.append("Verifier avant de modifier ces fichiers:")
        for f, dev in sorted(conflicts):
            lines.append(f"  - {f} (par {dev})")
        lines.append("")

    return "\n".join(lines)


def main():
    days = 1
    write_output = False
    branch_override = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == "--output":
            write_output = True
            i += 1
        elif args[i] == "--branch" and i + 1 < len(args):
            branch_override = args[i + 1]
            i += 2
        else:
            i += 1

    summary = generate_team_summary(days, branch_override)

    if write_output:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(summary, encoding="utf-8")
        print(f"Resume ecrit dans {OUTPUT_PATH}")
    else:
        print(summary)


if __name__ == "__main__":
    main()
