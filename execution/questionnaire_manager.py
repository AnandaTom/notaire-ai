# -*- coding: utf-8 -*-
"""
Questionnaire Manager - Collecte intelligente des donnees pour actes notariaux.

Collecte les informations necessaires via extraction naturelle du langage.
Le notaire envoie ses infos librement, le systeme extrait tout ce qu'il peut
et ne demande que ce qui manque.

Deux modes d'extraction:
1. Regex (gratuit, instantane) - detecte dates, prix, noms, etc.
2. Claude (fallback) - extraction structuree via LLM

Usage:
    qm = QuestionnaireManager("promesse_vente")
    extracted = qm.extract_from_text("Le vendeur est M. Bernard Jean-Pierre, marie, ne le 15/03/1962 a Lyon")
    qm.record_multiple(extracted)  # -> enregistre tout d'un coup
    missing = qm.get_missing_fields_message()  # -> "Il me manque: adresse, profession"
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict

PROJECT_ROOT = Path(__file__).parent.parent

# Sections essentielles pour une promesse de vente
SECTIONS_ESSENTIELLES = [
    {
        "id": "vendeur",
        "titre": "Vendeur",
        "questions": [
            {"id": "vendeur_civilite", "question": "Civilite du vendeur", "type": "choix", "options": ["M.", "Mme"], "obligatoire": True, "variable": "vendeurs[0].civilite"},
            {"id": "vendeur_nom", "question": "Nom du vendeur", "type": "texte", "obligatoire": True, "variable": "vendeurs[0].nom"},
            {"id": "vendeur_prenoms", "question": "Prenoms du vendeur", "type": "texte", "obligatoire": True, "variable": "vendeurs[0].prenoms"},
            {"id": "vendeur_date_naissance", "question": "Date de naissance du vendeur", "type": "texte", "obligatoire": True, "variable": "vendeurs[0].date_naissance"},
            {"id": "vendeur_lieu_naissance", "question": "Lieu de naissance du vendeur", "type": "texte", "obligatoire": True, "variable": "vendeurs[0].lieu_naissance"},
            {"id": "vendeur_adresse", "question": "Adresse du vendeur", "type": "texte", "obligatoire": True, "variable": "vendeurs[0].adresse"},
            {"id": "vendeur_situation", "question": "Situation matrimoniale du vendeur", "type": "choix", "options": ["celibataire", "marie", "pacse", "divorce", "veuf"], "obligatoire": True, "variable": "vendeurs[0].situation_matrimoniale"},
            {"id": "vendeur_profession", "question": "Profession du vendeur", "type": "texte", "obligatoire": False, "variable": "vendeurs[0].profession"},
        ]
    },
    {
        "id": "acquereur",
        "titre": "Acquereur",
        "questions": [
            {"id": "acquereur_civilite", "question": "Civilite de l'acquereur", "type": "choix", "options": ["M.", "Mme"], "obligatoire": True, "variable": "acquereurs[0].civilite"},
            {"id": "acquereur_nom", "question": "Nom de l'acquereur", "type": "texte", "obligatoire": True, "variable": "acquereurs[0].nom"},
            {"id": "acquereur_prenoms", "question": "Prenoms de l'acquereur", "type": "texte", "obligatoire": True, "variable": "acquereurs[0].prenoms"},
            {"id": "acquereur_date_naissance", "question": "Date de naissance de l'acquereur", "type": "texte", "obligatoire": True, "variable": "acquereurs[0].date_naissance"},
            {"id": "acquereur_lieu_naissance", "question": "Lieu de naissance de l'acquereur", "type": "texte", "obligatoire": True, "variable": "acquereurs[0].lieu_naissance"},
            {"id": "acquereur_adresse", "question": "Adresse de l'acquereur", "type": "texte", "obligatoire": True, "variable": "acquereurs[0].adresse"},
            {"id": "acquereur_situation", "question": "Situation matrimoniale de l'acquereur", "type": "choix", "options": ["celibataire", "marie", "pacse", "divorce", "veuf"], "obligatoire": True, "variable": "acquereurs[0].situation_matrimoniale"},
            {"id": "acquereur_profession", "question": "Profession de l'acquereur", "type": "texte", "obligatoire": False, "variable": "acquereurs[0].profession"},
        ]
    },
    {
        "id": "bien",
        "titre": "Bien immobilier",
        "questions": [
            {"id": "bien_type", "question": "Type de bien", "type": "choix", "options": ["appartement", "maison", "studio", "terrain", "local commercial"], "obligatoire": True, "variable": "bien.type"},
            {"id": "bien_adresse", "question": "Adresse complete du bien", "type": "texte", "obligatoire": True, "variable": "bien.adresse_complete"},
            {"id": "bien_surface", "question": "Surface Carrez (m2)", "type": "nombre", "obligatoire": True, "variable": "bien.surface_carrez"},
            {"id": "bien_lot", "question": "Numero de lot principal", "type": "texte", "obligatoire": False, "variable": "bien.lot_principal.numero"},
            {"id": "bien_description", "question": "Description du bien", "type": "texte", "obligatoire": False, "variable": "bien.description"},
        ]
    },
    {
        "id": "prix",
        "titre": "Prix et financement",
        "questions": [
            {"id": "prix_vente", "question": "Prix de vente (euros)", "type": "nombre", "obligatoire": True, "variable": "prix.vente"},
            {"id": "financement_type", "question": "Mode de financement", "type": "choix", "options": ["pret", "comptant", "mixte"], "obligatoire": True, "variable": "financement.type"},
            {"id": "pret_montant", "question": "Montant du pret (euros)", "type": "nombre", "obligatoire": False, "condition": "financement_type != comptant", "variable": "financement.prets[0].montant"},
            {"id": "pret_duree", "question": "Duree du pret (mois)", "type": "nombre", "obligatoire": False, "condition": "financement_type != comptant", "variable": "financement.prets[0].duree_mois"},
        ]
    },
    {
        "id": "conditions",
        "titre": "Conditions et delais",
        "questions": [
            {"id": "condition_pret", "question": "Condition suspensive de pret", "type": "choix", "options": ["oui", "non"], "obligatoire": True, "variable": "conditions_suspensives.pret"},
            {"id": "delai_promesse", "question": "Duree de validite (mois)", "type": "nombre", "obligatoire": True, "variable": "delais.validite_promesse_mois"},
            {"id": "indemnite_pourcent", "question": "Indemnite d'immobilisation (%)", "type": "nombre", "obligatoire": True, "variable": "delais.indemnite_immobilisation_pourcent"},
        ]
    },
]


# =============================================================================
# Patterns regex pour extraction naturelle
# =============================================================================

# Dates: 15/03/1962, 15-03-1962, 15 mars 1962
RE_DATE = re.compile(
    r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b'
    r'|'
    r'\b(\d{1,2}\s+(?:janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)\s+\d{4})\b',
    re.IGNORECASE
)

# Prix: 450000€, 450 000 €, 450k€, 1.2M€, 450000 euros
RE_PRIX = re.compile(
    r'(\d[\d\s]*[\d])\s*(?:€|euros?)\b'
    r'|'
    r'(\d+(?:[.,]\d+)?)\s*[kK]\s*(?:€|euros?)\b'
    r'|'
    r'(\d+(?:[.,]\d+)?)\s*[mM]\s*(?:€|euros?)\b',
    re.IGNORECASE
)

# Surface: 67m², 67 m2, 67m2
RE_SURFACE = re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:m[²2]|metres?\s*carr)', re.IGNORECASE)

# Situation matrimoniale
RE_SITUATION = re.compile(
    r'\b(celibataire|marie[e]?|pacse[e]?|divorce[e]?|veuf|veuve|'
    r'célibataire|marié[e]?|pacsé[e]?|divorcé[e]?)\b',
    re.IGNORECASE
)

# Civilite (pas de \b apres M. car le point casse word boundary)
RE_CIVILITE = re.compile(r'(?:^|\s)(M\.|Mme|Monsieur|Madame)(?:\s|$|,)', re.IGNORECASE)

# Type de bien
RE_BIEN_TYPE = re.compile(
    r'\b(appartement|maison|studio|terrain|local\s+commercial|t[1-5]|f[1-5])\b',
    re.IGNORECASE
)

# "ne(e) le ... a ..."  ou "ne(e) a ..."
RE_NE_A = re.compile(
    r'n[eéè]+e?\s+(?:le\s+)?(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\s+[aà]\s+([\w\u00C0-\u017F][\w\u00C0-\u017F\s\-]*)',
    re.IGNORECASE
)

# Financement
RE_FINANCEMENT = re.compile(
    r'\b(pret|prêt|emprunt|credit|crédit|comptant|fonds\s+propres)\b',
    re.IGNORECASE
)

# Pourcentage
RE_POURCENTAGE = re.compile(r'(\d+(?:[.,]\d+)?)\s*%')

# Duree en mois
RE_DUREE_MOIS = re.compile(r'(\d+)\s*mois', re.IGNORECASE)

# Noms: mots en majuscules (au moins 2 lettres)
RE_NOM_MAJ = re.compile(r'\b([A-Z\u00C0-\u017F]{2,}(?:\s*-\s*[A-Z\u00C0-\u017F]{2,})?)\b')

# Prenoms: mot capitalise apres un nom en majuscules
RE_PRENOM = re.compile(r'\b([A-Z][a-z\u00C0-\u017F]+(?:\s*-\s*[A-Z][a-z\u00C0-\u017F]+)*)\b')

# Adresse: numero + rue/avenue/boulevard + suite (stop at period/comma/exclamation)
RE_ADRESSE = re.compile(
    r'(\d+\s*,?\s*(?:rue|avenue|boulevard|av\.|bd\.|place|impasse|chemin|allee|allée|cours|passage|square|quai)\s+[^,.!?\n]+(?:,\s*\d{5}\s*[^,.!?\n]*)?)',
    re.IGNORECASE
)

# Profession courante
RE_PROFESSION = re.compile(
    r'\b(?:profession\s*:?\s*|de\s+profession\s+)([\w\s\-éèêëàâùûîïôö]+)',
    re.IGNORECASE
)


@dataclass
class QuestionnaireState:
    """Etat persistable du questionnaire."""
    type_acte: str = "promesse_vente"
    current_section_idx: int = 0
    current_question_idx: int = 0
    answers: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False

    def serialize(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "QuestionnaireState":
        return cls(**data)


class QuestionnaireManager:
    """Gestionnaire de questionnaire intelligent pour actes notariaux.

    Contrairement a un questionnaire rigide question-par-question,
    ce gestionnaire accepte du texte libre, extrait tous les champs possibles,
    et ne demande que les informations manquantes.
    """

    def __init__(self, type_acte: str = "promesse_vente", state: Optional[Dict] = None):
        self.sections = SECTIONS_ESSENTIELLES
        self.state = QuestionnaireState.deserialize(state) if state else QuestionnaireState(type_acte=type_acte)

    # =========================================================================
    # Proprietes
    # =========================================================================

    @property
    def total_obligatoires(self) -> int:
        count = 0
        for section in self.sections:
            for q in section["questions"]:
                if q.get("obligatoire", False) and self._question_applicable(q):
                    count += 1
        return count

    @property
    def reponses_obligatoires(self) -> int:
        count = 0
        for section in self.sections:
            for q in section["questions"]:
                if q.get("obligatoire", False) and q["id"] in self.state.answers and self._question_applicable(q):
                    count += 1
        return count

    @property
    def progress_percent(self) -> int:
        total = self.total_obligatoires
        if total == 0:
            return 100
        return int((self.reponses_obligatoires / total) * 100)

    # =========================================================================
    # Conditions
    # =========================================================================

    def _question_applicable(self, question: Dict) -> bool:
        condition = question.get("condition")
        if not condition:
            return True
        if "!=" in condition:
            field_id, value = condition.split("!=")
            return self.state.answers.get(field_id.strip()) != value.strip()
        return True

    # =========================================================================
    # Extraction intelligente depuis texte libre
    # =========================================================================

    def extract_from_text(self, text: str, context_section: str = None, allow_overwrite: bool = False) -> Dict[str, Any]:
        """Extrait tous les champs possibles depuis un message en langage naturel.

        Args:
            text: Le message brut de l'utilisateur
            context_section: Section en cours (vendeur/acquereur) pour desambiguer
            allow_overwrite: Si True, ecrase les champs deja remplis (pour corrections)

        Returns:
            Dict {question_id: valeur_extraite} pour tous les champs detectes
        """
        extracted = {}
        text_lower = text.lower()

        # Helper: verifier si on peut ecrire un champ (nouveau ou correction)
        def can_set(key):
            return allow_overwrite or key not in self.state.answers

        # Determiner le contexte: est-on en train de parler du vendeur ou de l'acquereur?
        if context_section is None:
            context_section = self._detect_context_section(text_lower)

        # Si les deux parties sont mentionnees, diviser et extraire separement
        if context_section == "both":
            acquereur_kw = ["acquereur", "acquéreur", "beneficiaire", "bénéficiaire", "acheteur"]
            split_idx = -1
            for kw in acquereur_kw:
                idx = text_lower.find(kw)
                if idx > 0:
                    split_idx = idx
                    break
            if split_idx > 0:
                part_vendeur = text[:split_idx]
                part_acquereur = text[split_idx:]
                ext_v = self.extract_from_text(part_vendeur, context_section="vendeur", allow_overwrite=allow_overwrite)
                ext_a = self.extract_from_text(part_acquereur, context_section="acquereur", allow_overwrite=allow_overwrite)
                extracted.update(ext_v)
                extracted.update(ext_a)
                return extracted
            context_section = "vendeur"  # fallback

        # --- Civilite ---
        civ_match = RE_CIVILITE.search(text)
        if civ_match:
            civ = civ_match.group(1).strip()
            civ_norm = "M." if civ.lower() in ("m.", "monsieur") else "Mme"
            if context_section == "vendeur" and can_set("vendeur_civilite"):
                extracted["vendeur_civilite"] = civ_norm
            elif context_section == "acquereur" and can_set("acquereur_civilite"):
                extracted["acquereur_civilite"] = civ_norm

        # --- "ne(e) le DD/MM/YYYY a Ville" ---
        ne_match = RE_NE_A.search(text)
        if ne_match:
            date_val = ne_match.group(1)
            # Extraire le lieu: premier(s) mot(s) capitalise(s) apres "a"
            lieu_raw = ne_match.group(2).strip()
            # Couper au premier mot-cle qui n'est pas le lieu
            for stop in [",", " marie", " celibataire", " pacse", " divorce", " veuf",
                        " de profession", " demeurant", " habitant", " domicilie"]:
                idx = lieu_raw.lower().find(stop)
                if idx > 0:
                    lieu_raw = lieu_raw[:idx]
                    break
            lieu_val = lieu_raw.strip()
            prefix = context_section
            if prefix and can_set(f"{prefix}_date_naissance"):
                extracted[f"{prefix}_date_naissance"] = date_val
            if prefix and can_set(f"{prefix}_lieu_naissance"):
                extracted[f"{prefix}_lieu_naissance"] = lieu_val
        else:
            # Date seule
            date_match = RE_DATE.search(text)
            if date_match:
                date_val = date_match.group(1) or date_match.group(2)
                if date_val and context_section:
                    key = f"{context_section}_date_naissance"
                    if can_set(key):
                        extracted[key] = date_val

        # --- Situation matrimoniale ---
        sit_match = RE_SITUATION.search(text)
        if sit_match:
            sit = sit_match.group(1).lower()
            # Normaliser
            sit_map = {
                "célibataire": "celibataire", "celibataire": "celibataire",
                "marié": "marie", "mariée": "marie", "marie": "marie", "mariee": "marie",
                "pacsé": "pacse", "pacsée": "pacse", "pacse": "pacse", "pacsee": "pacse",
                "divorcé": "divorce", "divorcée": "divorce", "divorce": "divorce", "divorcee": "divorce",
                "veuf": "veuf", "veuve": "veuf",
            }
            sit_norm = sit_map.get(sit, sit)
            if context_section:
                key = f"{context_section}_situation"
                if can_set(key):
                    extracted[key] = sit_norm

        # --- Noms (mots en MAJUSCULES) ---
        noms = RE_NOM_MAJ.findall(text)
        # Filtrer les mots-cles courants
        noise = {"LE", "LA", "DE", "DU", "ET", "AU", "EN", "SCI", "SARL", "SAS",
                 "NEE", "NE", "MM", "MME"}
        noms = [n for n in noms if n not in noise and len(n) >= 2]
        if noms and context_section:
            key = f"{context_section}_nom"
            if can_set(key):
                extracted[key] = noms[0]

        # --- Prenoms (mots Capitalises, pas en majuscules) ---
        # Extraire les prenoms AVANT les marqueurs d'adresse pour eviter la pollution
        text_for_prenoms = text
        for addr_marker in ["demeurant", "habitant", "domicilie", "résidant", "residant",
                           "situe", "situé", "sis "]:
            idx = text_for_prenoms.lower().find(addr_marker)
            if idx > 0:
                text_for_prenoms = text_for_prenoms[:idx]
                break
        prenoms_found = RE_PRENOM.findall(text_for_prenoms)
        # Filtrer: pas un nom deja extrait, pas un mot-cle
        noise_prenoms = {"Le", "La", "De", "Du", "Et", "Au", "En", "Rue", "Avenue",
                        "Boulevard", "Place", "Monsieur", "Madame", "Mme", "Paris", "Lyon",
                        "Marseille", "Toulouse", "Bordeaux", "Nantes", "Strasbourg",
                        "Vendeur", "Acquereur", "Acquéreur", "Promesse", "Vente",
                        "Section", "Profession", "Celibataire", "Civilite",
                        "Republique", "République"}
        nom_extrait = extracted.get(f"{context_section}_nom", "").title() if context_section else ""
        prenoms_filtered = [p for p in prenoms_found
                          if p not in noise_prenoms
                          and p != nom_extrait
                          and not p.isupper()]
        if prenoms_filtered and context_section:
            key = f"{context_section}_prenoms"
            if can_set(key):
                extracted[key] = " ".join(prenoms_filtered[:2])  # max 2 prenoms

        # --- Profession ---
        prof_match = RE_PROFESSION.search(text)
        if prof_match and context_section:
            key = f"{context_section}_profession"
            if can_set(key):
                extracted[key] = prof_match.group(1).strip()

        # --- Type de bien ---
        bien_match = RE_BIEN_TYPE.search(text)
        if bien_match and can_set("bien_type"):
            bien_val = bien_match.group(1).lower()
            # Normaliser T2/F3 -> appartement
            if bien_val.startswith(("t", "f")) and len(bien_val) == 2:
                bien_val = "appartement"
            extracted["bien_type"] = bien_val

        # --- Surface ---
        surf_match = RE_SURFACE.search(text)
        if surf_match and can_set("bien_surface"):
            extracted["bien_surface"] = float(surf_match.group(1).replace(",", "."))

        # --- Adresse (personne ou bien) ---
        addr_match = RE_ADRESSE.search(text)
        if addr_match:
            addr = addr_match.group(1).strip().rstrip(",.- ")
            # Determiner: adresse de la personne ou du bien ?
            is_person_addr = any(kw in text_lower for kw in ["demeurant", "habitant", "domicilie", "résidant", "residant"])
            is_bien_addr = any(kw in text_lower for kw in ["bien situe", "immeuble", "sis ", "situe a", "situé"])

            if is_person_addr and context_section and can_set(f"{context_section}_adresse"):
                extracted[f"{context_section}_adresse"] = addr
            elif is_bien_addr and can_set("bien_adresse"):
                extracted["bien_adresse"] = addr
            elif context_section and can_set(f"{context_section}_adresse"):
                extracted[f"{context_section}_adresse"] = addr
            elif can_set("bien_adresse"):
                extracted["bien_adresse"] = addr

        # --- Prix ---
        prix_match = RE_PRIX.search(text)
        if prix_match and can_set("prix_vente"):
            if prix_match.group(1):  # 450000€
                extracted["prix_vente"] = float(prix_match.group(1).replace(" ", ""))
            elif prix_match.group(2):  # 450k€
                extracted["prix_vente"] = float(prix_match.group(2).replace(",", ".")) * 1000
            elif prix_match.group(3):  # 1.2M€
                extracted["prix_vente"] = float(prix_match.group(3).replace(",", ".")) * 1000000

        # --- Financement ---
        fin_match = RE_FINANCEMENT.search(text)
        if fin_match and can_set("financement_type"):
            fin = fin_match.group(1).lower()
            if fin in ("comptant", "fonds propres"):
                extracted["financement_type"] = "comptant"
            else:
                extracted["financement_type"] = "pret"

        # --- Condition suspensive de pret ---
        if can_set("condition_pret"):
            if any(kw in text_lower for kw in ["condition suspensive", "clause suspensive"]):
                if any(kw in text_lower for kw in ["oui", "avec", "incluse", "prevue"]):
                    extracted["condition_pret"] = "oui"
                elif any(kw in text_lower for kw in ["non", "sans", "pas de", "aucune"]):
                    extracted["condition_pret"] = "non"
                else:
                    extracted["condition_pret"] = "oui"  # default: oui si mentionne

        # --- Pourcentage (indemnite) ---
        pct_matches = RE_POURCENTAGE.findall(text)
        if pct_matches and can_set("indemnite_pourcent"):
            for pct in pct_matches:
                val = float(pct.replace(",", "."))
                if 1 <= val <= 20:  # vraisemblable pour une indemnite
                    extracted["indemnite_pourcent"] = val
                    break

        # --- Duree en mois ---
        duree_match = RE_DUREE_MOIS.search(text)
        if duree_match:
            mois = int(duree_match.group(1))
            if can_set("delai_promesse") and 1 <= mois <= 12:
                extracted["delai_promesse"] = mois
            elif can_set("pret_duree") and mois > 12:
                extracted["pret_duree"] = mois

        return extracted

    def _detect_context_section(self, text_lower: str) -> Optional[str]:
        """Detecte si le texte parle du vendeur ou de l'acquereur."""
        vendeur_kw = ["vendeur", "promettant", "cédant", "cedant", "propriétaire", "proprietaire"]
        acquereur_kw = ["acquereur", "acquéreur", "beneficiaire", "bénéficiaire", "acheteur"]

        has_vendeur = any(kw in text_lower for kw in vendeur_kw)
        has_acquereur = any(kw in text_lower for kw in acquereur_kw)

        if has_vendeur and not has_acquereur:
            return "vendeur"
        if has_acquereur and not has_vendeur:
            return "acquereur"
        if has_vendeur and has_acquereur:
            return "both"  # Signal pour extraction multi-parties

        # Si pas de mot-cle explicite, deviner par les champs manquants
        vendeur_missing = sum(1 for q in self.sections[0]["questions"]
                            if q["id"] not in self.state.answers and q.get("obligatoire"))
        acquereur_missing = sum(1 for q in self.sections[1]["questions"]
                               if q["id"] not in self.state.answers and q.get("obligatoire"))

        if vendeur_missing > 0 and acquereur_missing == 0:
            return "vendeur"
        if acquereur_missing > 0 and vendeur_missing == 0:
            return "acquereur"
        if vendeur_missing > acquereur_missing:
            return "vendeur"

        return "vendeur"  # default

    # =========================================================================
    # Extraction via Claude (fallback)
    # =========================================================================

    def build_extraction_prompt(self) -> str:
        """Construit le prompt Claude pour extraction structuree."""
        pending = self.get_pending_fields()
        if not pending:
            return ""

        fields_desc = []
        for section_title, questions in pending:
            for q in questions:
                desc = f'- "{q["id"]}": {q["question"]}'
                if q.get("options"):
                    desc += f' (valeurs: {", ".join(q["options"])})'
                if q.get("type") == "nombre":
                    desc += " (nombre)"
                fields_desc.append(desc)

        return f"""Extrait les informations suivantes du message de l'utilisateur.
Retourne UNIQUEMENT un JSON valide avec les champs trouves (ignore ceux absents du message).

Champs a extraire:
{chr(10).join(fields_desc)}

IMPORTANT:
- Retourne seulement les champs presents dans le message
- Les nombres doivent etre des nombres (pas de texte)
- Les choix doivent correspondre aux valeurs indiquees
- Retourne {{}} si rien n'est trouvable
- PAS de texte autour du JSON, juste le JSON"""

    def parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse la reponse JSON de Claude."""
        try:
            # Trouver le JSON dans la reponse
            text = response_text.strip()
            # Chercher un bloc JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            # Trouver les accolades
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except (json.JSONDecodeError, IndexError):
            pass
        return {}

    # =========================================================================
    # Enregistrement et requetes
    # =========================================================================

    def record_answer(self, question_id: str, value: Any) -> bool:
        """Enregistre une reponse. Retourne True si valide."""
        question = self._find_question(question_id)
        if not question:
            return False

        if question.get("obligatoire") and not value and value != 0:
            return False

        if question.get("type") == "nombre":
            try:
                value = float(str(value).replace(" ", "").replace(",", "."))
            except (ValueError, TypeError):
                return False

        if question.get("type") == "choix":
            options = question.get("options", [])
            if options and value not in options:
                lower_options = [o.lower() for o in options]
                if str(value).lower() in lower_options:
                    value = options[lower_options.index(str(value).lower())]

        self.state.answers[question_id] = value
        return True

    def record_multiple(self, answers: Dict[str, Any]) -> Dict[str, bool]:
        """Enregistre plusieurs reponses d'un coup. Retourne le statut par champ."""
        results = {}
        for qid, value in answers.items():
            results[qid] = self.record_answer(qid, value)
        return results

    def _find_question(self, question_id: str) -> Optional[Dict]:
        for section in self.sections:
            for q in section["questions"]:
                if q["id"] == question_id:
                    return q
        return None

    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """Retourne la prochaine question non repondue."""
        for s_idx, section in enumerate(self.sections):
            for q_idx, question in enumerate(section["questions"]):
                if question["id"] not in self.state.answers:
                    if not self._question_applicable(question):
                        continue
                    self.state.current_section_idx = s_idx
                    self.state.current_question_idx = q_idx
                    return {
                        **question,
                        "section_titre": section["titre"],
                        "section_id": section["id"],
                        "progress": self.progress_percent
                    }
        self.state.completed = True
        return None

    def get_pending_fields(self) -> List[Tuple[str, List[Dict]]]:
        """Retourne toutes les questions non repondues, groupees par section."""
        result = []
        for section in self.sections:
            pending = []
            for q in section["questions"]:
                if q["id"] not in self.state.answers and self._question_applicable(q):
                    pending.append(q)
            if pending:
                result.append((section["titre"], pending))
        return result

    def is_complete(self) -> bool:
        for section in self.sections:
            for q in section["questions"]:
                if q.get("obligatoire") and q["id"] not in self.state.answers and self._question_applicable(q):
                    return False
        self.state.completed = True
        return True

    # =========================================================================
    # Formatage des messages
    # =========================================================================

    def format_welcome_message(self, type_lisible: str) -> str:
        """Message d'accueil montrant les infos necessaires."""
        article = "une" if self.state.type_acte == "promesse_vente" else "un"
        lines = [f"Je vais vous aider a preparer {article} {type_lisible}."]
        lines.append("Envoyez-moi les informations dont vous disposez, je completerai au fur et a mesure.\n")
        lines.append("**Informations necessaires :**")

        for section in self.sections:
            obligatoires = [q for q in section["questions"] if q.get("obligatoire")]
            if obligatoires:
                fields = [q["question"] for q in obligatoires]
                lines.append(f"- **{section['titre']}** : {', '.join(fields)}")

        lines.append("\nVous pouvez tout envoyer d'un coup ou en plusieurs messages.")
        return "\n".join(lines)

    def format_extraction_result(self, extracted: Dict[str, Any]) -> str:
        """Formate le resultat d'extraction: ce qui a ete compris + ce qui manque."""
        lines = []
        progress = self.progress_percent

        # Ce qui a ete compris
        if extracted:
            lines.append(f"[{progress}%] **Compris** :")
            for qid, val in extracted.items():
                q = self._find_question(qid)
                if q:
                    lines.append(f"  - {q['question']} : **{val}**")

        # Ce qui manque (obligatoire uniquement)
        pending = self.get_pending_fields()
        mandatory_missing = []
        for section_title, questions in pending:
            for q in questions:
                if q.get("obligatoire"):
                    mandatory_missing.append((section_title, q["question"]))

        if not mandatory_missing:
            # Tout est rempli !
            return self._format_complete_message()

        # Grouper par section
        lines.append(f"\n**Il me manque** ({len(mandatory_missing)} champs) :")
        current_section = None
        for section_title, question_text in mandatory_missing:
            if section_title != current_section:
                current_section = section_title
                lines.append(f"  *{section_title}* :")
            lines.append(f"    - {question_text}")

        return "\n".join(lines)

    def _format_complete_message(self) -> str:
        """Message quand toutes les infos sont collectees."""
        resume = self.get_summary()
        return f"[100%] Toutes les informations sont collectees !\n\n{resume}\n\nSouhaitez-vous generer le document ?"

    def get_summary(self) -> str:
        """Resume des donnees collectees."""
        lines = []
        for section in self.sections:
            section_data = []
            for q in section["questions"]:
                if q["id"] in self.state.answers:
                    val = self.state.answers[q["id"]]
                    section_data.append(f"  - {q['question']}: **{val}**")
            if section_data:
                lines.append(f"\n**{section['titre']}**")
                lines.extend(section_data)
        return "\n".join(lines)

    def get_missing_suggestions(self) -> List[str]:
        """Suggestions basees sur ce qui manque."""
        pending = self.get_pending_fields()
        if not pending:
            return ["Generer le document", "Modifier une reponse"]

        # Suggerer la prochaine section a remplir
        suggestions = []
        for section_title, questions in pending[:2]:
            suggestions.append(f"Renseigner {section_title.lower()}")
        suggestions.append("Annuler")
        return suggestions

    # =========================================================================
    # Export
    # =========================================================================

    def to_acte_data(self) -> Dict[str, Any]:
        """Convertit les reponses en structure donnees_metier compatible assembler_acte."""
        a = self.state.answers

        def _build_situation(statut: str) -> Dict[str, Any]:
            """Construit l'objet situation_matrimoniale attendu par assembler_acte."""
            sit = {"statut": statut}
            if statut == "marie":
                sit["regime_matrimonial"] = "communaute_legale"
            elif statut == "pacse":
                sit["pacs"] = {"regime_libelle": "separation de biens"}
            return sit

        prix_val = a.get("prix_vente", 0)

        data = {
            "type_acte": self.state.type_acte,
            "vendeurs": [{
                "civilite": a.get("vendeur_civilite", ""),
                "nom": a.get("vendeur_nom", ""),
                "prenoms": a.get("vendeur_prenoms", ""),
                "date_naissance": a.get("vendeur_date_naissance", ""),
                "lieu_naissance": a.get("vendeur_lieu_naissance", ""),
                "adresse": a.get("vendeur_adresse", ""),
                "situation_matrimoniale": _build_situation(a.get("vendeur_situation", "celibataire")),
                "profession": a.get("vendeur_profession", ""),
                "nationalite": "Francaise",
            }],
            "acquereurs": [{
                "civilite": a.get("acquereur_civilite", ""),
                "nom": a.get("acquereur_nom", ""),
                "prenoms": a.get("acquereur_prenoms", ""),
                "date_naissance": a.get("acquereur_date_naissance", ""),
                "lieu_naissance": a.get("acquereur_lieu_naissance", ""),
                "adresse": a.get("acquereur_adresse", ""),
                "situation_matrimoniale": _build_situation(a.get("acquereur_situation", "celibataire")),
                "profession": a.get("acquereur_profession", ""),
                "nationalite": "Francaise",
            }],
            "bien": {
                "type": a.get("bien_type", ""),
                "adresse_complete": a.get("bien_adresse", ""),
                "surface_carrez": a.get("bien_surface", 0),
                "lot_principal": {"numero": a.get("bien_lot", "")},
                "description": a.get("bien_description", ""),
            },
            "prix": {
                "vente": prix_val,
                "montant": prix_val,  # alias attendu par assembler_acte
            },
            "financement": {
                "type": a.get("financement_type", "pret"),
            },
            "conditions_suspensives": {
                "pret": a.get("condition_pret", "oui") == "oui",
            },
            "delais": {
                "validite_promesse_mois": int(a.get("delai_promesse", 3)),
                "indemnite_immobilisation_pourcent": int(a.get("indemnite_pourcent", 10)),
            },
            # Defaults pour assembler_acte
            "acte": {
                "date": {
                    "jour": datetime.now().day,
                    "mois": datetime.now().month,
                    "annee": datetime.now().year,
                },
                "lieu": a.get("bien_adresse", "").split(",")[-1].strip() if a.get("bien_adresse") else "",
            },
            "quotites_vendues": [{
                "personne_index": 0,
                "fraction": "la totalite",
                "type_propriete": "pleine_propriete",
            }],
            "quotites_acquises": [{
                "personne_index": 0,
                "fraction": "la totalite",
                "type_propriete": "pleine_propriete",
            }],
        }

        if a.get("financement_type") != "comptant" and a.get("pret_montant"):
            data["financement"]["prets"] = [{
                "montant": a.get("pret_montant", 0),
                "duree_mois": int(a.get("pret_duree", 240)),
            }]
        elif a.get("financement_type") == "pret":
            # Pret sans montant specifie: utiliser le prix total
            data["paiement"] = {
                "prets": [{"montant": prix_val, "duree_mois": 240}],
                "fonds_empruntes": prix_val,
            }

        pourcent = a.get("indemnite_pourcent", 10)
        if prix_val and pourcent:
            data["delais"]["indemnite_immobilisation"] = int(prix_val * pourcent / 100)

        return data

    def serialize(self) -> Dict[str, Any]:
        return self.state.serialize()
