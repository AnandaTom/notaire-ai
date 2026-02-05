"""
Module d'enrichissement et validation des donnees pour la generation d'actes.

Transforme les donnees brutes collectees par le chat en structure compatible
avec les templates Jinja2 (assembler_acte).

Principe : donnees obligatoires manquantes -> erreur claire.
           sections optionnelles -> gerees par {% if %} dans les templates.
"""

import copy
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


# =========================================================================
# Fonctions publiques
# =========================================================================

def enrichir_donnees_pour_generation(
    donnees: dict,
    type_acte: str,
    etude_id: str = None
) -> dict:
    """
    Point d'entree principal. Enrichit + valide les donnees collectees
    pour les rendre compatibles avec les templates Jinja2.

    Args:
        donnees: Donnees brutes du chat (donnees_collectees)
        type_acte: "promesse_vente" ou "vente"
        etude_id: UUID de l'etude (pour auto-remplir acte.notaire)

    Returns:
        Donnees enrichies pretes pour AssembleurActe.assembler()

    Raises:
        ValueError: Si des champs obligatoires manquent
    """
    donnees = copy.deepcopy(donnees)
    donnees = _mapper_parties(donnees, type_acte)
    donnees = _restructurer_bien(donnees)
    donnees = _enrichir_notaire(donnees, etude_id)
    donnees = _ajouter_defaults_structurels(donnees, type_acte)
    valider_donnees_obligatoires(donnees, type_acte)
    return donnees


def valider_donnees_obligatoires(donnees: dict, type_acte: str) -> None:
    """
    Verifie que tous les champs obligatoires sont presents.
    Leve ValueError avec la liste des champs manquants.
    """
    manquants = get_champs_manquants(donnees, type_acte)
    if manquants:
        details = ", ".join(manquants)
        raise ValueError(f"Donnees manquantes pour la generation : {details}")


def get_champs_manquants(donnees: dict, type_acte: str) -> List[str]:
    """
    Retourne la liste lisible des champs manquants.
    Utile pour afficher la progression au notaire.
    """
    champs = _get_champs_obligatoires(type_acte)
    manquants = []

    for label, path in champs:
        if not _resolve_path(donnees, path):
            manquants.append(label)

    return manquants


# =========================================================================
# Fonctions internes - Mapping des parties
# =========================================================================

def _normaliser_personnes(personnes: list) -> list:
    """Assure que chaque personne a les sous-dicts optionnels attendus par les templates."""
    for p in personnes:
        if isinstance(p, dict):
            p.setdefault("coordonnees", {})
            p.setdefault("situation_matrimoniale", {"statut": "celibataire"})
    return personnes


def _mapper_parties(donnees: dict, type_acte: str) -> dict:
    """
    Mappe vendeurs->promettants et acquereurs->beneficiaires pour les promesses.
    """
    if type_acte == "promesse_vente":
        # vendeurs -> promettants
        if "vendeurs" in donnees and "promettants" not in donnees:
            donnees["promettants"] = donnees.pop("vendeurs")
        # acquereurs -> beneficiaires
        if "acquereurs" in donnees and "beneficiaires" not in donnees:
            donnees["beneficiaires"] = donnees.pop("acquereurs")

        # Quotites beneficiaires par defaut
        if "quotites_beneficiaires" not in donnees:
            nb = len(donnees.get("beneficiaires", []))
            if nb > 0:
                donnees["quotites_beneficiaires"] = [{
                    "personne_index": i,
                    "quotite": f"{100 // nb}%" if nb > 1 else "100%",
                    "type_propriete": "pleine_propriete",
                } for i in range(nb)]

    elif type_acte == "vente":
        # Quotites vendues/acquises par defaut
        if "quotites_vendues" not in donnees:
            nb = len(donnees.get("vendeurs", []))
            if nb > 0:
                donnees["quotites_vendues"] = [{
                    "personne_index": i,
                    "fraction": "la totalite" if nb == 1 else f"1/{nb}",
                    "type_propriete": "pleine_propriete",
                } for i in range(nb)]
        if "quotites_acquises" not in donnees:
            nb = len(donnees.get("acquereurs", []))
            if nb > 0:
                donnees["quotites_acquises"] = [{
                    "personne_index": i,
                    "fraction": "la totalite" if nb == 1 else f"1/{nb}",
                    "type_propriete": "pleine_propriete",
                } for i in range(nb)]

    # Normaliser les sous-dicts des personnes
    for key in ["promettants", "beneficiaires", "vendeurs", "acquereurs"]:
        if key in donnees and isinstance(donnees[key], list):
            _normaliser_personnes(donnees[key])

    return donnees


# =========================================================================
# Fonctions internes - Restructuration du bien
# =========================================================================

def _restructurer_bien(donnees: dict) -> dict:
    """
    Restructure bien.adresse_complete (string) en bien.adresse (dict).
    Enveloppe bien.lot_principal en bien.lots[] si necessaire.
    """
    bien = donnees.get("bien", {})
    if not bien:
        return donnees

    # Parser adresse_complete en dict structure
    if "adresse_complete" in bien and "adresse" not in bien:
        bien["adresse"] = _parser_adresse(bien["adresse_complete"])

    # Assurer que adresse est un dict
    if isinstance(bien.get("adresse"), str):
        bien["adresse"] = _parser_adresse(bien["adresse"])

    # Envelopper lot_principal en lots[] si necessaire
    if "lot_principal" in bien and "lots" not in bien:
        lot = bien["lot_principal"]
        if isinstance(lot, dict) and lot.get("numero"):
            bien["lots"] = [lot]
        elif isinstance(lot, str) and lot:
            bien["lots"] = [{"numero": lot, "type": "principal"}]

    # cadastre par defaut (liste vide, sera garde par {% if %} dans template)
    if "cadastre" not in bien:
        bien["cadastre"] = []

    # description_ensemble par defaut si absent
    if "description_ensemble" not in bien and "description" in bien:
        bien["description_ensemble"] = bien["description"]

    donnees["bien"] = bien
    return donnees


def _parser_adresse(adresse_str: str) -> dict:
    """
    Parse une adresse en string vers un dict structure.
    Exemples:
        "8 boulevard Haussmann, 75009 Paris" ->
        {"numero": "8", "voie": "boulevard Haussmann", "code_postal": "75009", "ville": "Paris"}

        "12 rue de la Paix, 75002 Paris" ->
        {"numero": "12", "voie": "rue de la Paix", "code_postal": "75002", "ville": "Paris"}
    """
    if not adresse_str or not isinstance(adresse_str, str):
        return {"numero": "", "voie": "", "code_postal": "", "ville": ""}

    result = {"numero": "", "voie": "", "code_postal": "", "ville": ""}

    # Pattern: "NUM VOIE, CODE_POSTAL VILLE"
    match = re.match(
        r'^(\d+[a-zA-Z]?(?:\s*(?:bis|ter))?)\s+(.+?),?\s+(\d{5})\s+(.+)$',
        adresse_str.strip()
    )
    if match:
        result["numero"] = match.group(1).strip()
        result["voie"] = match.group(2).strip().rstrip(",")
        result["code_postal"] = match.group(3).strip()
        result["ville"] = match.group(4).strip()
        # Deduire departement depuis code postal
        cp = result["code_postal"]
        if cp.startswith("75"):
            result["departement"] = "Paris"
        elif cp.startswith("69"):
            result["departement"] = "Rhone"
        elif cp.startswith("13"):
            result["departement"] = "Bouches-du-Rhone"
        elif cp.startswith("33"):
            result["departement"] = "Gironde"
        elif cp.startswith("31"):
            result["departement"] = "Haute-Garonne"
        else:
            result["departement"] = cp[:2]
        return result

    # Pattern sans numero: "VOIE, CODE_POSTAL VILLE"
    match2 = re.match(r'^(.+?),?\s+(\d{5})\s+(.+)$', adresse_str.strip())
    if match2:
        result["voie"] = match2.group(1).strip().rstrip(",")
        result["code_postal"] = match2.group(2).strip()
        result["ville"] = match2.group(3).strip()
        return result

    # Fallback: tout dans voie
    result["voie"] = adresse_str.strip()
    return result


# =========================================================================
# Fonctions internes - Enrichissement notaire
# =========================================================================

def _enrichir_notaire(donnees: dict, etude_id: str = None) -> dict:
    """
    Auto-remplit acte.notaire depuis la table Supabase etudes si possible.
    """
    acte = donnees.setdefault("acte", {})

    # Si notaire deja present avec un nom, ne pas ecraser
    if isinstance(acte.get("notaire"), dict) and acte["notaire"].get("nom"):
        return donnees

    if not etude_id:
        return donnees

    # Tenter de charger depuis Supabase
    try:
        from execution.database.supabase_client import get_client
        supabase = get_client()
        if not supabase:
            return donnees

        resp = supabase.table("etudes").select("*").eq("id", etude_id).execute()
        if not resp.data:
            return donnees

        etude = resp.data[0]
        notaire = acte.get("notaire", {})
        if not isinstance(notaire, dict):
            notaire = {}

        # Mapper les champs disponibles
        if etude.get("nom") and not notaire.get("societe"):
            notaire["societe"] = etude["nom"]
        if etude.get("adresse") and not notaire.get("adresse"):
            notaire["adresse"] = etude["adresse"]
        if etude.get("siret") and not notaire.get("siret"):
            notaire["siret"] = etude["siret"]

        # Extraire ville depuis adresse si possible
        if notaire.get("adresse") and not notaire.get("ville"):
            addr = _parser_adresse(notaire["adresse"])
            if addr.get("ville"):
                notaire["ville"] = addr["ville"]

        acte["notaire"] = notaire
        donnees["acte"] = acte

    except Exception:
        # Non bloquant - la validation attrapera les champs manquants
        pass

    return donnees


# =========================================================================
# Fonctions internes - Defaults structurels
# =========================================================================

def _ajouter_defaults_structurels(donnees: dict, type_acte: str) -> dict:
    """
    Ajoute les valeurs par defaut structurelles necessaires au template.
    """
    # acte.date par defaut = aujourd'hui
    acte = donnees.setdefault("acte", {})
    if "date" not in acte:
        now = datetime.now()
        acte["date"] = {"jour": now.day, "mois": now.month, "annee": now.year}

    # prix.devise par defaut
    prix = donnees.get("prix", {})
    if isinstance(prix, dict) and "devise" not in prix:
        prix["devise"] = "euros"
        donnees["prix"] = prix

    # Pour promesse de vente: delais et indemnite
    if type_acte == "promesse_vente":
        _defaults_promesse(donnees)

    # Fournir des dicts vides pour les variables optionnelles top-level
    # que le template reference dans des {% if var.sub %} ou {{ var.sub | default() }}
    # Cela evite les UndefinedError quand le template fait {% if parent.child %}
    OPTIONAL_TOPLEVEL = [
        "financement", "clause_penale", "negociation",
        "conditions_suspensives", "condition_suspensive_pret",
        "situation_environnementale", "beneficiaire_situation",
        "jouissance", "publication", "fiscalite",
        "conventions_particulieres", "visites",
        "diagnostics", "meubles", "urbanisme",
        "travaux_recents", "condition_survie",
        "annexe", "convention",
    ]
    for key in OPTIONAL_TOPLEVEL:
        donnees.setdefault(key, {})

    return donnees


def _defaults_promesse(donnees: dict) -> dict:
    """Defaults specifiques a la promesse de vente."""
    # delais.expiration_promesse
    delais = donnees.setdefault("delais", {})
    if "expiration_promesse" not in delais:
        # Calculer depuis delai_realisation si present
        delai_real = donnees.get("delai_realisation")
        if delai_real and isinstance(delai_real, str):
            delais["expiration_promesse"] = {
                "date": delai_real,
                "heure": "16h00",
            }
        else:
            # Default: +3 mois
            expiration = datetime.now() + timedelta(days=90)
            delais["expiration_promesse"] = {
                "date": expiration.strftime("%Y-%m-%d"),
                "heure": "16h00",
            }

    # indemnite_immobilisation: calculer 10% du prix si absent
    prix_montant = _safe_get_number(donnees, "prix.montant")
    if prix_montant and "indemnite_immobilisation" not in donnees:
        montant_indem = int(prix_montant * 0.10)
        donnees["indemnite_immobilisation"] = {
            "montant": montant_indem,
            "pourcentage": 10,
            "depot_garantie": montant_indem,
        }

    return donnees


# =========================================================================
# Fonctions internes - Validation
# =========================================================================

def _get_champs_obligatoires(type_acte: str) -> List[tuple]:
    """
    Retourne les champs obligatoires sous forme [(label, path), ...].
    """
    communs = [
        ("Adresse du bien (ville)", "bien.adresse.ville"),
        ("Prix de vente", "prix.montant"),
        ("Notaire (nom)", "acte.notaire.nom"),
    ]

    if type_acte == "promesse_vente":
        return [
            ("Promettant (nom)", "promettants.0.nom"),
            ("Beneficiaire (nom)", "beneficiaires.0.nom"),
        ] + communs
    elif type_acte == "vente":
        return [
            ("Vendeur (nom)", "vendeurs.0.nom"),
            ("Acquereur (nom)", "acquereurs.0.nom"),
        ] + communs
    else:
        return communs


def _resolve_path(data: dict, path: str) -> Any:
    """
    Resout un chemin pointe dans un dict/liste.
    Ex: "promettants.0.nom" -> data["promettants"][0]["nom"]
    """
    current = data
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, (list, tuple)):
            try:
                idx = int(part)
                current = current[idx] if idx < len(current) else None
            except (ValueError, IndexError):
                return None
        else:
            return None

    # Verifier que la valeur n'est pas vide
    if current is None or current == "" or current == 0:
        return None
    return current


def _safe_get_number(data: dict, path: str) -> Optional[float]:
    """Resout un chemin et retourne un nombre ou None."""
    val = _resolve_path(data, path)
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None
