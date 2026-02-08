"""
Self-Anneal: analyse des feedbacks confirmes et creation automatique de PRs GitHub.

Workflow:
1. Query feedbacks confirmes (approuve=True, processed=False) avec min_occurrences
2. Grouper par (section_id, action, contenu)
3. Classifier chaque groupe -> fichier cible
4. Creer branche GitHub auto-anneal/YYYY-MM-DD
5. Appliquer les corrections comme commits
6. Creer PR avec resume
7. Marquer feedbacks comme processed
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional
from collections import defaultdict

import requests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# A. Mapping correction -> fichier cible
# ---------------------------------------------------------------------------

FEEDBACK_FILE_MAP = {
    # Section du template -> fichier template a modifier
    "designation_bien": "templates/promesse_vente_lots_copropriete.md",
    "conditions_suspensives": "templates/sections/section_conditions_suspensives.md",
    "prix_paiement": "templates/promesse_vente_lots_copropriete.md",
    "sequestre": "templates/sections/section_sequestre.md",
    "declarations_parties": "templates/sections/section_declarations_parties.md",
    "propriete_jouissance": "templates/sections/section_propriete_jouissance.md",
    "lotissement": "templates/sections/section_lotissement_dispositions.md",

    # Actions specifiques -> fichiers cibles
    "ajouter_clause": "schemas/clauses_catalogue.json",
    "modifier_schema": "schemas/variables_promesse_vente.json",
    "modifier_question": "schemas/questions_promesse_vente.json",
    "directive": "directives/lecons_apprises.md",
}

# Corrections "simples" = texte direct a appliquer
SIMPLE_ACTIONS = {"modifier", "corriger", "remplacer"}
# Corrections "complexes" = necessitent review humain
COMPLEX_ACTIONS = {"ajouter", "supprimer", "restructurer"}


# ---------------------------------------------------------------------------
# B. Query des feedbacks confirmes
# ---------------------------------------------------------------------------

def query_confirmed_feedbacks(supabase, min_occurrences: int = 3) -> list[dict]:
    """
    Recupere les feedbacks approuves non traites, groupes par
    (section_id, action, contenu) avec count >= min_occurrences.
    """
    try:
        result = supabase.table("feedbacks_promesse").select(
            "id, section_id, action, contenu, raison, metadata, created_at"
        ).eq("approuve", True).eq("processed", False).execute()

        if not result.data:
            return []

        # Grouper par (section_id, action, contenu)
        groups = defaultdict(list)
        for fb in result.data:
            key = (
                fb.get("section_id", ""),
                fb.get("action", ""),
                (fb.get("contenu") or "").strip()[:200],  # Tronquer pour grouper
            )
            groups[key].append(fb)

        # Filtrer les groupes avec assez d'occurrences
        confirmed = []
        for (section_id, action, contenu), feedbacks in groups.items():
            if len(feedbacks) >= min_occurrences:
                confirmed.append({
                    "section_id": section_id,
                    "action": action,
                    "contenu": contenu,
                    "count": len(feedbacks),
                    "feedback_ids": [fb["id"] for fb in feedbacks],
                    "raisons": list({fb.get("raison", "") for fb in feedbacks if fb.get("raison")}),
                    "first_seen": min(fb["created_at"] for fb in feedbacks),
                })

        logger.info("Feedbacks confirmes: %d groupes (seuil=%d)", len(confirmed), min_occurrences)
        return confirmed

    except Exception as e:
        logger.error("Erreur query feedbacks: %s", e)
        return []


def classify_feedback(feedback_group: dict) -> dict:
    """
    Determine le fichier cible et le type de correction pour un groupe de feedbacks.
    """
    section_id = feedback_group["section_id"]
    action = feedback_group["action"]

    # Determiner le fichier cible
    target_file = FEEDBACK_FILE_MAP.get(section_id)
    if not target_file:
        # Fallback: si l'action indique un type specifique
        if "clause" in (feedback_group.get("contenu") or "").lower():
            target_file = FEEDBACK_FILE_MAP["ajouter_clause"]
        elif "question" in (feedback_group.get("contenu") or "").lower():
            target_file = FEEDBACK_FILE_MAP["modifier_question"]
        else:
            target_file = FEEDBACK_FILE_MAP["directive"]

    # Determiner la complexite
    is_simple = action in SIMPLE_ACTIONS
    requires_human_review = action in COMPLEX_ACTIONS or feedback_group["count"] < 5

    return {
        **feedback_group,
        "target_file": target_file,
        "is_simple": is_simple,
        "requires_human_review": requires_human_review,
        "correction_type": "template" if target_file.startswith("templates/")
            else "schema" if target_file.startswith("schemas/")
            else "directive",
    }


# ---------------------------------------------------------------------------
# C. GitHub Integration (REST API v3)
# ---------------------------------------------------------------------------

class GitHubIntegration:
    """Client GitHub REST API pour creer branches, commits et PRs."""

    def __init__(
        self,
        token: Optional[str] = None,
        repo: Optional[str] = None,
        default_branch: Optional[str] = None,
    ):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.repo = repo or os.getenv("GITHUB_REPO", "AnandaTom/notaire-ai")
        self.default_branch = default_branch or os.getenv("GITHUB_DEFAULT_BRANCH", "master")
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get(self, path: str) -> dict:
        resp = requests.get(f"{self.api_base}{path}", headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, data: dict) -> dict:
        resp = requests.post(
            f"{self.api_base}{path}", headers=self.headers, json=data, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def _put(self, path: str, data: dict) -> dict:
        resp = requests.put(
            f"{self.api_base}{path}", headers=self.headers, json=data, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def get_default_branch_sha(self) -> str:
        """Recupere le SHA du HEAD de la branche par defaut."""
        data = self._get(f"/repos/{self.repo}/git/ref/heads/{self.default_branch}")
        return data["object"]["sha"]

    def create_branch(self, branch_name: str) -> str:
        """Cree une branche a partir du HEAD de master. Retourne le SHA."""
        sha = self.get_default_branch_sha()
        self._post(f"/repos/{self.repo}/git/refs", {
            "ref": f"refs/heads/{branch_name}",
            "sha": sha,
        })
        logger.info("Branche creee: %s (base: %s)", branch_name, sha[:8])
        return sha

    def get_file_content(self, branch: str, path: str) -> tuple[str, str]:
        """Recupere le contenu et le SHA d'un fichier. Retourne (content, sha)."""
        import base64
        data = self._get(f"/repos/{self.repo}/contents/{path}?ref={branch}")
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content, data["sha"]

    def update_file(self, branch: str, path: str, content: str, message: str) -> dict:
        """Met a jour un fichier sur une branche. Cree le fichier s'il n'existe pas."""
        import base64
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        data = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }

        # Recuperer le SHA existant si le fichier existe
        try:
            _, sha = self.get_file_content(branch, path)
            data["sha"] = sha
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise
            # Fichier n'existe pas, on le cree

        result = self._put(f"/repos/{self.repo}/contents/{path}", data)
        logger.info("Fichier mis a jour: %s sur %s", path, branch)
        return result

    def create_pr(self, branch: str, title: str, body: str) -> dict:
        """Cree une Pull Request."""
        result = self._post(f"/repos/{self.repo}/pulls", {
            "title": title,
            "body": body,
            "head": branch,
            "base": self.default_branch,
        })
        logger.info("PR creee: %s -> %s", branch, result.get("html_url"))
        return result


# ---------------------------------------------------------------------------
# D. Orchestrateur self-anneal
# ---------------------------------------------------------------------------

def _build_pr_body(classified_feedbacks: list[dict]) -> str:
    """Construit le body Markdown de la PR."""
    lines = [
        "## Self-Anneal automatique",
        "",
        f"Ce PR applique **{len(classified_feedbacks)} corrections** identifiees automatiquement",
        "a partir des feedbacks notaires confirmes (3+ occurrences identiques).",
        "",
        "### Corrections appliquees",
        "",
        "| Section | Action | Occurrences | Fichier | Review |",
        "|---------|--------|-------------|---------|--------|",
    ]

    for fb in classified_feedbacks:
        review = "Manuel" if fb["requires_human_review"] else "Auto"
        lines.append(
            f"| {fb['section_id']} | {fb['action']} | {fb['count']}x "
            f"| `{fb['target_file']}` | {review} |"
        )

    lines.extend([
        "",
        "### Details des corrections",
        "",
    ])

    for i, fb in enumerate(classified_feedbacks, 1):
        lines.append(f"#### {i}. {fb['section_id']} ({fb['action']})")
        lines.append(f"- **Contenu:** {fb['contenu'][:300]}")
        if fb["raisons"]:
            lines.append(f"- **Raisons:** {', '.join(fb['raisons'][:3])}")
        lines.append(f"- **Premiere occurrence:** {fb['first_seen']}")
        lines.append(f"- **Nombre:** {fb['count']} feedbacks identiques")
        lines.append("")

    needs_review = [fb for fb in classified_feedbacks if fb["requires_human_review"]]
    if needs_review:
        lines.extend([
            "### Sections necessitant une revue manuelle",
            "",
            "Les corrections suivantes sont complexes et doivent etre verifiees:",
            "",
        ])
        for fb in needs_review:
            lines.append(f"- **{fb['section_id']}**: {fb['action']} — {fb['contenu'][:100]}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "Genere automatiquement par `execution/self_anneal.py`",
    ])

    return "\n".join(lines)


def _apply_directive_feedback(github: GitHubIntegration, branch: str, fb: dict) -> bool:
    """Ajoute une lecon apprise dans directives/lecons_apprises.md."""
    try:
        path = fb["target_file"]
        content, _ = github.get_file_content(branch, path)

        new_entry = (
            f"\n\n### Lecon auto-anneal ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            f"**Section:** {fb['section_id']}\n"
            f"**Action:** {fb['action']}\n"
            f"**Correction:** {fb['contenu']}\n"
            f"**Occurrences:** {fb['count']} feedbacks confirmes\n"
            f"**Raisons:** {', '.join(fb['raisons'][:3]) if fb['raisons'] else 'N/A'}\n"
        )

        updated_content = content.rstrip() + new_entry

        github.update_file(
            branch, path, updated_content,
            f"auto-anneal: lecon apprise — {fb['section_id']} ({fb['action']})"
        )
        return True
    except Exception as e:
        logger.error("Erreur apply directive %s: %s", fb["section_id"], e)
        return False


def mark_feedbacks_processed(supabase, feedback_ids: list[str], pr_url: str, correction_type: str):
    """Marque les feedbacks comme traites dans Supabase."""
    try:
        supabase.table("feedbacks_promesse").update({
            "processed": True,
            "processed_at": datetime.now().isoformat(),
            "pr_url": pr_url,
            "correction_type": correction_type,
        }).in_("id", feedback_ids).execute()

        logger.info("Marque %d feedbacks comme processed", len(feedback_ids))
    except Exception as e:
        logger.error("Erreur marking feedbacks: %s", e)


def run_self_anneal(supabase, min_occurrences: int = 3) -> dict:
    """
    Orchestrateur principal du self-anneal.

    1. Query feedbacks confirmes (3+ occurrences identiques)
    2. Classifie chaque groupe (fichier cible, complexite)
    3. Cree branche GitHub auto-anneal/YYYY-MM-DD
    4. Applique les corrections simples (directives, lecons)
    5. Cree PR avec resume complet
    6. Marque feedbacks comme processed

    Retourne un rapport d'execution.
    """
    rapport = {
        "date": datetime.now().isoformat(),
        "feedbacks_found": 0,
        "corrections_applied": 0,
        "pr_url": None,
        "errors": [],
    }

    # 1. Query feedbacks confirmes
    confirmed = query_confirmed_feedbacks(supabase, min_occurrences)
    rapport["feedbacks_found"] = len(confirmed)

    if not confirmed:
        logger.info("Aucun feedback confirme a traiter")
        rapport["status"] = "no_feedbacks"
        return rapport

    # 2. Classifier
    classified = [classify_feedback(fb) for fb in confirmed]

    # 3. Verifier credentials GitHub
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning("GITHUB_TOKEN manquant — rapport sans PR")
        rapport["status"] = "no_github_token"
        rapport["classified_feedbacks"] = [
            {k: v for k, v in fb.items() if k != "feedback_ids"}
            for fb in classified
        ]
        return rapport

    github = GitHubIntegration(token=github_token)

    # 4. Creer branche
    branch_name = f"auto-anneal/{datetime.now().strftime('%Y-%m-%d')}"
    try:
        github.create_branch(branch_name)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            # Branche existe deja (job relance le meme jour)
            branch_name = f"auto-anneal/{datetime.now().strftime('%Y-%m-%d-%H%M')}"
            github.create_branch(branch_name)
        else:
            raise

    # 5. Appliquer corrections
    applied_count = 0
    all_feedback_ids = []

    for fb in classified:
        try:
            if fb["correction_type"] == "directive":
                success = _apply_directive_feedback(github, branch_name, fb)
            else:
                # Templates et schemas: flag pour review humain
                # On ajoute quand meme la lecon dans les directives
                fb_directive = {**fb, "target_file": "directives/lecons_apprises.md"}
                success = _apply_directive_feedback(github, branch_name, fb_directive)
                fb["requires_human_review"] = True

            if success:
                applied_count += 1
                all_feedback_ids.extend(fb["feedback_ids"])
        except Exception as e:
            error_msg = f"Erreur correction {fb['section_id']}: {e}"
            logger.error(error_msg)
            rapport["errors"].append(error_msg)

    rapport["corrections_applied"] = applied_count

    if applied_count == 0:
        rapport["status"] = "no_corrections_applied"
        return rapport

    # 6. Creer PR
    try:
        pr_title = f"auto-anneal: {applied_count} corrections ({datetime.now().strftime('%d/%m/%Y')})"
        pr_body = _build_pr_body(classified)
        pr_result = github.create_pr(branch_name, pr_title, pr_body)
        pr_url = pr_result.get("html_url", "")
        rapport["pr_url"] = pr_url
    except Exception as e:
        logger.error("Erreur creation PR: %s", e)
        rapport["errors"].append(f"PR creation failed: {e}")
        pr_url = ""

    # 7. Marquer feedbacks comme processed
    if all_feedback_ids:
        mark_feedbacks_processed(supabase, all_feedback_ids, pr_url, "auto-anneal")

    rapport["status"] = "success"
    logger.info(
        "Self-anneal termine: %d corrections, PR: %s",
        applied_count, pr_url
    )
    return rapport
