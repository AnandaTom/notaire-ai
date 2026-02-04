#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraire_titre_propriete.py
---------------------------
Script d'extraction automatique des données d'un titre de propriété.

Supporte les formats:
- PDF (via pdfplumber ou PyMuPDF)
- DOCX (via python-docx)

Usage:
    python extraire_titre_propriete.py --input titre.pdf --output donnees_titre.json
    python extraire_titre_propriete.py --input titre.docx --output donnees_titre.json --verbose
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Imports conditionnels
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            text = str(args[0]) if args else ""
            # Enlever les tags rich
            text = re.sub(r'\[.*?\]', '', text)
            print(text)
    console = Console()


# =============================================================================
# PATTERNS D'EXTRACTION (REGEX)
# =============================================================================

PATTERNS = {
    # Dates
    "date_acte": [
        r"[Ll]e\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})",
        r"[Ee]n\s+date\s+du\s+(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})",
        r"(\d{1,2})/(\d{1,2})/(\d{4})",
    ],

    # Notaire
    "notaire": [
        r"[Mm]aître\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*[Nn]otaire\s+(?:associé\s+)?(?:de la société\s+)?(?:à|situé à)\s+([A-Za-zÉÈÀÇéèàç\s\-]+)",
        r"[Mm]e\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*[Nn]otaire\s+à\s+([A-Za-zÉÈÀÇéèàç\s\-]+)",
        r"CRPCEN\s*[:\s]*(\d+)",
    ],

    # Publication
    "publication": [
        r"[Pp]ublié\s+au\s+[Ss]ervice\s+de\s+la\s+[Pp]ublicité\s+[Ff]oncière\s+de\s+([A-ZÉÈÀÇéèàça-z\s\dème]+?)[\s,]+le\s+(\d{1,2}\s+\w+\s+\d{4})[\s,]+[Vv]olume\s+(\w+)[\s,]+[Nn]°?\s*(\d+)",
        r"[Pp]ublicité\s+[Ff]oncière\s+de\s+([A-ZÉÈÀÇéèàça-z\s\dème]+)",
    ],

    # Personnes physiques
    "personne_physique": [
        r"(Monsieur|Madame|M\.|Mme)\s+([A-ZÉÈÀÇa-zéèàç\-]+)\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*([a-zéèàçA-ZÉÈÀÇ\s\-]+),\s*demeurant\s+(?:à\s+)?([^\.]+)",
        r"(Monsieur|Madame)\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*né(?:e)?\s+(?:le\s+)?(\d{1,2}[/\s]\w+[/\s]\d{4})\s+à\s+([A-Za-zÉÈÀÇéèàç\s\-]+)",
    ],

    # Quotités
    "quotite": [
        r"(?:à\s+concurrence\s+de\s+)?(?:la\s+)?(moitié|totalité|un\s+tiers|deux\s+tiers|un\s+quart|trois\s+quarts)",
        r"(?:à\s+hauteur\s+de\s+)?(\d+[,\.]\d+)\s*%",
        r"(\d+)/(\d+)(?:ème)?s?",
    ],

    # Régime matrimonial
    "regime_matrimonial": [
        r"[Mm]arié(?:e)?s?\s+sous\s+le\s+régime\s+(?:de\s+)?(la\s+communauté\s+(?:légale|réduite\s+aux\s+acquêts|universelle)|la\s+séparation\s+de\s+biens|la\s+participation\s+aux\s+acquêts)",
        r"[Cc]élibataire",
        r"[Pp]acte\s+[Cc]ivil\s+de\s+[Ss]olidarité",
        r"[Vv]euf|[Vv]euve",
        r"[Dd]ivorcé(?:e)?",
    ],

    # Adresse du bien
    "adresse_bien": [
        r"situé\s+(?:à\s+)?([A-ZÉÈÀÇa-zéèàç\s\-]+)\s*\(([A-Za-z\-]+)\)\s*,?\s*(\d{5})?\s*,?\s*(\d+)?\s*,?\s*([^\.]+)",
        r"(\d+)[\s,]+(?:rue|avenue|chemin|boulevard|place|impasse|allée)\s+([A-Za-zÉÈÀÇéèàç\s\d\-']+)[\s,]+(\d{5})\s+([A-Za-zÉÈÀÇéèàç\s\-]+)",
    ],

    # Cadastre
    "cadastre": [
        r"[Ss]ection\s+([A-Z]{1,2})\s*,?\s*[Nn]°?\s*(\d+)",
        r"cadastré(?:e)?s?\s+[Ss]ection\s+([A-Z]{1,2})\s*[Nn]°?\s*(\d+)",
        r"lieudit\s+[\"«]?([A-Za-zÉÈÀÇéèàç\s\-]+)[\"»]?",
    ],

    # Lots de copropriété
    "lots": [
        r"[Ll]ot\s+(?:numéro\s+)?(?:[A-Z\-]+\s+)?(?:\()?(\d+)(?:\))?",
        r"(\d+)/(\d+)(?:ème)?s?\s+des\s+(?:parties\s+communes|tantièmes)",
        r"[Tt]antièmes?\s*[:\s]*(\d+)\s*/\s*(\d+)",
    ],

    # Prix
    "prix": [
        r"[Mm]oyennant\s+(?:le\s+)?[Pp]rix\s+(?:principal\s+)?(?:de\s+)?([A-ZÉÈÀÇ\s\-]+)\s*(?:EUROS?|€|EUR)\s*\((\d[\d\s]*)\s*(?:EUROS?|€|EUR)?\)",
        r"(\d[\d\s,\.]+)\s*(?:EUROS?|€|EUR)",
        r"[Pp]rix\s+total\s*[:\s]*(\d[\d\s,\.]+)",
    ],

    # Origine de propriété
    "origine": [
        r"ORIGINE\s+DE\s+PROPRI[ÉE]T[ÉE]",
        r"[Aa]cquisition\s+(?:par\s+)?(?:suivant\s+)?(?:acte\s+)?(?:reçu\s+par\s+)?([^,]+),\s*(?:le\s+)?(\d{1,2}\s+\w+\s+\d{4}|\d{1,2}/\d{1,2}/\d{4})",
        r"[Ss]uccession\s+de\s+([A-ZÉÈÀÇa-zéèàç\s\-]+)",
        r"[Dd]onation\s+(?:par|de)\s+([A-ZÉÈÀÇa-zéèàç\s\-]+)",
        r"[Vv]ente\s+en\s+l'[ÉEée]tat\s+[Ff]utur\s+d'[Aa]chèvement|VEFA",
    ],

    # Copropriété
    "copropriete": [
        r"[ÉEé]tat\s+[Dd]escriptif\s+de\s+[Dd]ivision",
        r"[Rr]èglement\s+de\s+[Cc]opropriété",
        r"[Ii]mmatriculation\s*[:\s]*(\d[\d\s\-]+)",
    ],

    # Carrez
    "carrez": [
        r"[Ss]uperficie\s+(?:Carrez\s+)?(?:de\s+)?(\d+[,\.]\d+)\s*m[²2]",
        r"(\d+[,\.]\d+)\s*m(?:ètres?\s+)?[²2]\s+(?:Carrez|de\s+partie\s+privative)",
    ],
}


# =============================================================================
# FONCTIONS D'EXTRACTION
# =============================================================================

def calculer_hash_fichier(filepath: Path) -> str:
    """Calcule le hash SHA256 d'un fichier."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def extraire_texte_pdf(filepath: Path) -> str:
    """Extrait le texte d'un fichier PDF."""
    if not HAS_PDFPLUMBER:
        raise ImportError("pdfplumber n'est pas installé. Exécutez: pip install pdfplumber")

    texte = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texte += page_text + "\n"
    return texte


def extraire_texte_docx(filepath: Path) -> str:
    """Extrait le texte d'un fichier DOCX."""
    if not HAS_DOCX:
        raise ImportError("python-docx n'est pas installé. Exécutez: pip install python-docx")

    doc = Document(filepath)
    texte = ""
    for para in doc.paragraphs:
        texte += para.text + "\n"
    return texte


def extraire_texte(filepath: Path) -> str:
    """Extrait le texte d'un fichier (PDF ou DOCX)."""
    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return extraire_texte_pdf(filepath)
    elif suffix in [".docx", ".doc"]:
        return extraire_texte_docx(filepath)
    else:
        raise ValueError(f"Format non supporté: {suffix}")


def trouver_pattern(texte: str, patterns: List[str], flags=re.IGNORECASE | re.MULTILINE) -> List[Tuple]:
    """Trouve tous les matchs pour une liste de patterns."""
    resultats = []
    for pattern in patterns:
        matches = re.findall(pattern, texte, flags)
        resultats.extend(matches)
    return resultats


def extraire_date(texte: str) -> Optional[str]:
    """Extrait la date de l'acte."""
    matches = trouver_pattern(texte, PATTERNS["date_acte"])
    if matches:
        match = matches[0]
        if isinstance(match, tuple):
            if len(match) == 3:
                # Format "27 juin 2017"
                return f"{match[0]} {match[1]} {match[2]}"
        return str(match)
    return None


def extraire_notaire(texte: str) -> Dict:
    """Extrait les informations du notaire."""
    notaire = {}

    # Nom et ville
    pattern = r"[Mm]aître\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*[Nn]otaire\s+(?:associé\s+)?(?:de la société\s+)?(?:à|situé à)\s+([A-Za-zÉÈÀÇéèàç\s\-]+)"
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        notaire["civilite"] = "Maître"
        nom_complet = match.group(1).strip()
        # Séparer prénom et nom si possible
        parts = nom_complet.split()
        if len(parts) >= 2:
            notaire["prenom"] = parts[0]
            notaire["nom"] = " ".join(parts[1:])
        else:
            notaire["nom"] = nom_complet
        notaire["ville"] = match.group(2).strip()

    # CRPCEN
    match_crpcen = re.search(r"CRPCEN\s*[:\s]*(\d+)", texte)
    if match_crpcen:
        notaire["crpcen"] = match_crpcen.group(1)

    return notaire


def extraire_publication(texte: str) -> Dict:
    """Extrait les références de publication."""
    publication = {}

    pattern = r"[Pp]ublié\s+au\s+[Ss]ervice\s+de\s+la\s+[Pp]ublicité\s+[Ff]oncière\s+de\s+([A-ZÉÈÀÇéèàça-z\s\dème]+?)[\s,]+le\s+(\d{1,2}\s+\w+\s+\d{4})[\s,]+[Vv]olume\s+(\w+)[\s,]+[Nn]°?\s*(\d+)"
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        publication["service"] = match.group(1).strip()
        publication["date"] = match.group(2).strip()
        publication["volume"] = match.group(3).strip()
        publication["numero"] = match.group(4).strip()

    return publication


def extraire_personnes(texte: str, section: str = "VENDEUR") -> List[Dict]:
    """Extrait les informations des personnes (vendeurs ou acquéreurs)."""
    personnes = []

    # Trouver la section appropriée
    if section == "VENDEUR":
        section_pattern = r"VENDEUR[S]?\s*(.*?)(?=ACQU[ÉE]REUR|$)"
    else:
        section_pattern = r"ACQU[ÉE]REUR[S]?\s*(.*?)(?=Quotités|Désignation|$)"

    section_match = re.search(section_pattern, texte, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return personnes

    section_text = section_match.group(1)

    # Pattern pour personne physique
    pattern = r"(Monsieur|Madame|M\.|Mme)\s+([A-ZÉÈÀÇa-zéèàç\s\-]+),\s*([a-zéèàçA-ZÉÈÀÇ\s\-/]+),\s*demeurant\s+(?:à\s+)?([^\.]+)"
    matches = re.findall(pattern, section_text, re.IGNORECASE)

    for match in matches:
        personne = {
            "type": "physique",
            "civilite": match[0].strip(),
            "nom": match[1].strip().split()[-1] if match[1].strip() else "",
            "prenoms": " ".join(match[1].strip().split()[:-1]) if len(match[1].strip().split()) > 1 else "",
            "profession": match[2].strip(),
            "adresse": match[3].strip()
        }

        # Extraire naissance
        naissance_pattern = r"[Nn]é(?:e)?\s+(?:le\s+)?(\d{1,2}[/\s]\w+[/\s]\d{4})\s+à\s+([A-Za-zÉÈÀÇéèàç\s\-]+)"
        naissance_match = re.search(naissance_pattern, section_text)
        if naissance_match:
            personne["date_naissance"] = naissance_match.group(1)
            personne["lieu_naissance"] = naissance_match.group(2).strip()

        # Extraire régime matrimonial
        for regime_pattern in PATTERNS["regime_matrimonial"]:
            regime_match = re.search(regime_pattern, section_text, re.IGNORECASE)
            if regime_match:
                personne["situation_matrimoniale"] = {
                    "statut": "marie" if "marié" in regime_match.group(0).lower() else
                             "celibataire" if "célibataire" in regime_match.group(0).lower() else
                             "pacse" if "pacte" in regime_match.group(0).lower() else
                             "veuf" if "veuf" in regime_match.group(0).lower() else
                             "divorce" if "divorc" in regime_match.group(0).lower() else "inconnu",
                    "regime": regime_match.group(1) if regime_match.lastindex else regime_match.group(0)
                }
                break

        personnes.append(personne)

    return personnes


def extraire_bien(texte: str) -> Dict:
    """Extrait les informations du bien immobilier."""
    bien = {
        "adresse": {},
        "cadastre": [],
        "lots": []
    }

    # Adresse
    adresse_pattern = r"situé\s+(?:à\s+)?([A-ZÉÈÀÇa-zéèàç\s\-]+)\s*\(([A-Za-z\-]+)\)"
    adresse_match = re.search(adresse_pattern, texte, re.IGNORECASE)
    if adresse_match:
        bien["adresse"]["ville"] = adresse_match.group(1).strip()
        bien["adresse"]["departement"] = adresse_match.group(2).strip()

    # Numéro et voie
    voie_pattern = r"(\d+)[\s,]+(?:rue|avenue|chemin|boulevard|place|impasse|allée)\s+([A-Za-zÉÈÀÇéèàç\s\d\-']+)"
    voie_match = re.search(voie_pattern, texte, re.IGNORECASE)
    if voie_match:
        bien["adresse"]["numero"] = voie_match.group(1)
        bien["adresse"]["voie"] = voie_match.group(2).strip()

    # Code postal
    cp_pattern = r"(\d{5})\s+[A-ZÉÈÀÇa-zéèàç\s\-]+"
    cp_match = re.search(cp_pattern, texte)
    if cp_match:
        bien["adresse"]["code_postal"] = cp_match.group(1)

    # Cadastre
    cadastre_pattern = r"[Ss]ection\s+([A-Z]{1,2})\s*,?\s*[Nn]°?\s*(\d+)"
    cadastre_matches = re.findall(cadastre_pattern, texte)
    for match in cadastre_matches:
        bien["cadastre"].append({
            "section": match[0],
            "numero": match[1]
        })

    # Lots de copropriété
    lot_pattern = r"[Ll]ot\s+(?:numéro\s+)?(?:[A-Z\-]+\s+)?\((\d+)\)|[Ll]ot\s+(\d+)"
    lot_matches = re.findall(lot_pattern, texte)
    tantiemes_pattern = r"(\d+)\s*/\s*(\d+)\s*(?:ème)?s?\s+(?:des\s+)?(?:parties\s+communes|tantièmes)"
    tantiemes_matches = re.findall(tantiemes_pattern, texte)

    for i, match in enumerate(lot_matches):
        lot_num = match[0] or match[1]
        lot = {"numero": int(lot_num)}

        if i < len(tantiemes_matches):
            lot["tantiemes"] = {
                "valeur": int(tantiemes_matches[i][0]),
                "base": int(tantiemes_matches[i][1])
            }

        bien["lots"].append(lot)

    # Carrez
    carrez_pattern = r"[Ss]uperficie\s+(?:Carrez\s+)?(?:de\s+)?(\d+[,\.]\d+)\s*m[²2]"
    carrez_match = re.search(carrez_pattern, texte)
    if carrez_match:
        bien["superficie_carrez"] = float(carrez_match.group(1).replace(",", "."))

    return bien


def extraire_prix(texte: str) -> Dict:
    """Extrait le prix de la vente."""
    prix = {}

    # Prix en lettres et chiffres
    pattern = r"[Mm]oyennant\s+(?:le\s+)?[Pp]rix\s+(?:principal\s+)?(?:de\s+)?[A-ZÉÈÀÇ\s\-]+\s*(?:EUROS?|€|EUR)\s*\((\d[\d\s]*)\s*(?:EUROS?|€|EUR)?\)"
    match = re.search(pattern, texte, re.IGNORECASE)
    if match:
        montant_str = match.group(1).replace(" ", "").replace("\u00a0", "")
        prix["montant_total"] = int(montant_str)
    else:
        # Fallback: chercher un montant en euros
        pattern2 = r"[Pp]rix\s+(?:total|principal)?\s*[:\s]*(\d[\d\s,\.]+)\s*(?:EUROS?|€|EUR)"
        match2 = re.search(pattern2, texte, re.IGNORECASE)
        if match2:
            montant_str = match2.group(1).replace(" ", "").replace("\u00a0", "").replace(",", "")
            try:
                prix["montant_total"] = int(float(montant_str))
            except ValueError:
                pass

    prix["devise"] = "EUR"
    return prix


def extraire_origine_propriete(texte: str) -> List[Dict]:
    """Extrait la chaîne d'origine de propriété."""
    origines = []

    # Trouver la section ORIGINE DE PROPRIETE
    origine_section = re.search(r"ORIGINE\s+DE\s+PROPRI[ÉE]T[ÉE](.*?)(?=SITUATION\s+HYPOTH|CHARGES|URBANISME|$)",
                                texte, re.DOTALL | re.IGNORECASE)
    if not origine_section:
        return origines

    section_text = origine_section.group(1)

    # Niveau 1: Acquisition directe
    acquisition_pattern = r"[Aa]cquisition\s+(?:par\s+)?(?:suivant\s+)?(?:acte\s+)?(?:reçu\s+par\s+)?[Mm]aître\s+([^,]+),\s*(?:notaire\s+à\s+)?([^,]+),\s*(?:le\s+)?(\d{1,2}\s+\w+\s+\d{4})"
    acq_match = re.search(acquisition_pattern, section_text, re.IGNORECASE)
    if acq_match:
        origines.append({
            "niveau": 1,
            "type": "acquisition",
            "notaire": f"Maître {acq_match.group(1).strip()}, notaire à {acq_match.group(2).strip()}",
            "date": acq_match.group(3).strip()
        })

    # Succession
    succession_pattern = r"[Ss]uccession\s+de\s+([A-ZÉÈÀÇa-zéèàç\s\-]+).*?(?:décédé(?:e)?\s+le\s+)?(\d{1,2}\s+\w+\s+\d{4}|\d{1,2}/\d{1,2}/\d{4})?"
    succ_match = re.search(succession_pattern, section_text, re.IGNORECASE)
    if succ_match:
        origine = {
            "niveau": len(origines) + 1,
            "type": "succession",
            "auteur": succ_match.group(1).strip()
        }
        if succ_match.group(2):
            origine["details_succession"] = {"date_deces": succ_match.group(2)}
        origines.append(origine)

    # VEFA
    if re.search(r"[Vv]ente\s+en\s+l'[ÉEée]tat\s+[Ff]utur\s+d'[Aa]chèvement|VEFA", section_text, re.IGNORECASE):
        origines.append({
            "niveau": len(origines) + 1,
            "type": "vefa"
        })

    # Donation
    donation_pattern = r"[Dd]onation\s+(?:par|de)\s+([A-ZÉÈÀÇa-zéèàç\s\-]+)"
    don_match = re.search(donation_pattern, section_text, re.IGNORECASE)
    if don_match:
        origines.append({
            "niveau": len(origines) + 1,
            "type": "donation",
            "auteur": don_match.group(1).strip()
        })

    return origines


def extraire_copropriete(texte: str) -> Dict:
    """Extrait les informations de copropriété."""
    copro = {}

    # Règlement
    reglement_pattern = r"[ÉEé]tat\s+[Dd]escriptif\s+de\s+[Dd]ivision.*?(?:reçu\s+par\s+)?[Mm]aître\s+([^,]+),\s*(?:notaire\s+à\s+)?([^,]+),\s*(?:le\s+)?(\d{1,2}\s+\w+\s+\d{4})"
    reg_match = re.search(reglement_pattern, texte, re.IGNORECASE | re.DOTALL)
    if reg_match:
        copro["reglement"] = {
            "notaire_origine": f"Maître {reg_match.group(1).strip()}",
            "date_origine": reg_match.group(3).strip()
        }

    # Immatriculation
    immat_pattern = r"[Ii]mmatriculation\s*[:\s]*(\d[\d\s\-]+)"
    immat_match = re.search(immat_pattern, texte)
    if immat_match:
        copro["immatriculation"] = {
            "numero": immat_match.group(1).strip()
        }

    return copro


def extraire_donnees_titre(filepath: Path, verbose: bool = False) -> Dict:
    """
    Extrait toutes les données d'un titre de propriété.

    Args:
        filepath: Chemin vers le fichier (PDF ou DOCX)
        verbose: Afficher les détails de l'extraction

    Returns:
        Dictionnaire des données extraites
    """
    if verbose:
        console.print(f"[blue]Lecture de {filepath.name}...[/blue]")

    # Extraire le texte
    texte = extraire_texte(filepath)

    if verbose:
        console.print(f"[dim]Texte extrait: {len(texte)} caractères[/dim]")

    # Calculer le hash
    hash_fichier = calculer_hash_fichier(filepath)

    # Extraire les données
    donnees = {
        "reference": f"TITRE-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "source": {
            "type_fichier": filepath.suffix.lower().replace(".", ""),
            "nom_fichier": filepath.name,
            "date_upload": datetime.now().isoformat(),
            "hash_fichier": hash_fichier
        }
    }

    # Date de l'acte
    date = extraire_date(texte)
    if date:
        donnees["date_acte"] = date
        if verbose:
            console.print(f"[green]✓[/green] Date de l'acte: {date}")

    # Notaire
    notaire = extraire_notaire(texte)
    if notaire:
        donnees["notaire"] = notaire
        if verbose:
            console.print(f"[green]✓[/green] Notaire: {notaire.get('nom', 'N/A')}")

    # Publication
    publication = extraire_publication(texte)
    if publication:
        donnees["publication"] = publication
        if verbose:
            console.print(f"[green]✓[/green] Publication: {publication.get('service', 'N/A')}")

    # Vendeurs (propriétaires précédents)
    vendeurs = extraire_personnes(texte, "VENDEUR")
    if vendeurs:
        donnees["vendeurs_originaux"] = vendeurs
        if verbose:
            console.print(f"[green]✓[/green] Vendeurs originaux: {len(vendeurs)}")

    # Acquéreurs (propriétaires actuels)
    acquereurs = extraire_personnes(texte, "ACQUEREUR")
    if acquereurs:
        donnees["proprietaires_actuels"] = acquereurs
        if verbose:
            console.print(f"[green]✓[/green] Propriétaires actuels: {len(acquereurs)}")

    # Bien
    bien = extraire_bien(texte)
    if bien:
        donnees["bien"] = bien
        if verbose:
            lots_count = len(bien.get("lots", []))
            console.print(f"[green]✓[/green] Bien: {lots_count} lot(s)")

    # Prix
    prix = extraire_prix(texte)
    if prix:
        donnees["prix"] = prix
        if verbose:
            console.print(f"[green]✓[/green] Prix: {prix.get('montant_total', 'N/A')} EUR")

    # Origine de propriété
    origines = extraire_origine_propriete(texte)
    if origines:
        donnees["origine_propriete"] = origines
        if verbose:
            console.print(f"[green]✓[/green] Origine: {len(origines)} niveau(x)")

    # Copropriété
    copro = extraire_copropriete(texte)
    if copro:
        donnees["copropriete"] = copro
        if verbose:
            console.print(f"[green]✓[/green] Copropriété: règlement trouvé")

    # ── Enrichissement cadastre via API gouvernementale ──
    try:
        from execution.services.cadastre_service import CadastreService
        cadastre_svc = CadastreService()
        resultat_cadastre = cadastre_svc.enrichir_cadastre(donnees)
        donnees = resultat_cadastre["donnees"]
        rapport_cadastre = resultat_cadastre["rapport"]
        if verbose:
            if rapport_cadastre["cadastre_enrichi"]:
                console.print(
                    f"[green]✓[/green] Cadastre enrichi: "
                    f"{rapport_cadastre['parcelles_validees']} parcelle(s) validée(s), "
                    f"code INSEE {rapport_cadastre['code_insee']}"
                )
            elif rapport_cadastre["code_insee"]:
                console.print(
                    f"[yellow]⚠[/yellow] Code INSEE {rapport_cadastre['code_insee']} trouvé "
                    f"mais parcelle(s) non validée(s)"
                )
            for w in rapport_cadastre.get("warnings", []):
                console.print(f"[yellow]  → {w}[/yellow]")
    except ImportError:
        rapport_cadastre = None
        if verbose:
            console.print("[dim]Module cadastre non disponible, enrichissement ignoré[/dim]")
    except Exception as e:
        rapport_cadastre = None
        if verbose:
            console.print(f"[yellow]⚠ Enrichissement cadastre échoué: {e}[/yellow]")

    # Métadonnées
    champs_extraits = [k for k, v in donnees.items() if v and k not in ["reference", "source", "metadata"]]
    champs_attendus = ["date_acte", "notaire", "publication", "proprietaires_actuels", "bien", "prix", "origine_propriete"]
    champs_manquants = [c for c in champs_attendus if c not in champs_extraits]

    donnees["metadata"] = {
        "date_extraction": datetime.now().isoformat(),
        "methode_extraction": "automatique",
        "confiance": round(len(champs_extraits) / len(champs_attendus), 2),
        "champs_manquants": champs_manquants
    }
    if rapport_cadastre:
        donnees["metadata"]["cadastre"] = {
            "enrichi": rapport_cadastre["cadastre_enrichi"],
            "code_insee": rapport_cadastre["code_insee"],
            "parcelles_validees": rapport_cadastre["parcelles_validees"],
        }

    if verbose:
        console.print(f"\n[bold]Score de confiance:[/bold] {donnees['metadata']['confiance'] * 100:.0f}%")
        if champs_manquants:
            console.print(f"[yellow]Champs manquants:[/yellow] {', '.join(champs_manquants)}")

    return donnees


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extraction automatique des données d'un titre de propriété",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python extraire_titre_propriete.py -i titre.pdf -o donnees.json
  python extraire_titre_propriete.py -i titre.docx -o donnees.json --verbose
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        type=str,
        help="Fichier d'entrée (PDF ou DOCX)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier JSON de sortie (défaut: <input>_extrait.json)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mode verbeux"
    )

    args = parser.parse_args()

    # Vérifier le fichier d'entrée
    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"[red]Erreur: fichier non trouvé: {input_path}[/red]")
        sys.exit(1)

    # Déterminer le fichier de sortie
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(f"{input_path.stem}_extrait.json")

    # Extraire les données
    console.print(Panel(
        f"[bold]Extraction du titre de propriété[/bold]\n\n"
        f"Entrée: {input_path.name}\n"
        f"Sortie: {output_path.name}",
        border_style="blue"
    ))

    try:
        donnees = extraire_donnees_titre(input_path, verbose=args.verbose)

        # Sauvegarder
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)

        console.print(f"\n[green]✓ Données extraites et sauvegardées dans {output_path}[/green]")
        console.print(f"[dim]Score de confiance: {donnees['metadata']['confiance'] * 100:.0f}%[/dim]")

    except Exception as e:
        console.print(f"[red]Erreur lors de l'extraction: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
