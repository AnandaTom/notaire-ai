#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_donnees_test.py
-----------------------
Génère des données de test réalistes pour les différents types d'actes notariés.
Utilise Faker pour générer des données françaises cohérentes.

Usage:
    python generer_donnees_test.py --type vente --output .tmp/test_vente.json
    python generer_donnees_test.py --type reglement --output .tmp/test_edd.json
    python generer_donnees_test.py --type modificatif --output .tmp/test_modificatif.json
    python generer_donnees_test.py --type reglement --lots 15 --output .tmp/test_edd_15lots.json
"""

import argparse
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from faker import Faker
except ImportError:
    print("Erreur: faker n'est pas installé. Exécutez: pip install faker")
    sys.exit(1)

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TMP_DIR = PROJECT_ROOT / ".tmp"

# Initialisation de Faker avec locale française
fake = Faker('fr_FR')
Faker.seed(42)  # Pour reproductibilité pendant les tests

# Données de référence pour la génération
PRENOMS_HOMMES = ["Jean", "Pierre", "Michel", "Philippe", "Alain", "Bernard", "Jacques", "Daniel", "Thierry", "Patrick"]
PRENOMS_FEMMES = ["Marie", "Françoise", "Monique", "Catherine", "Nicole", "Isabelle", "Sophie", "Nathalie", "Anne", "Sylvie"]
PROFESSIONS = ["Retraité", "Cadre", "Enseignant", "Médecin", "Avocat", "Ingénieur", "Commerçant", "Artisan", "Chef d'entreprise", "Fonctionnaire"]
FORMES_SOCIETES = ["SCI", "SARL", "SAS", "SA", "SASU", "EURL"]
VILLES_RHONE = ["Lyon", "Villeurbanne", "Vénissieux", "Caluire-et-Cuire", "Saint-Priest", "Vaulx-en-Velin", "Bron", "Villefranche-sur-Saône", "Meyzieu", "Oullins"]
CODES_POSTAUX_RHONE = ["69001", "69002", "69003", "69004", "69005", "69006", "69007", "69008", "69009", "69100", "69200", "69300"]

TYPES_VOIE = ["rue", "avenue", "boulevard", "place", "impasse", "chemin", "allée"]
NOMS_VOIE = ["Victor Hugo", "Jean Jaurès", "Gambetta", "Pasteur", "de la République", "de la Liberté", "des Lilas", "du Parc", "de la Gare", "des Écoles"]

ETAGES = ["rez-de-chaussée", "premier étage", "deuxième étage", "troisième étage", "quatrième étage", "cinquième étage"]
ORIENTATIONS = ["côté rue", "côté cour", "sur jardin", "côté parc"]

DESIGNATIONS_LOTS = ["Appartement", "Studio", "Local commercial", "Cave", "Parking", "Box", "Grenier", "Cellier"]

NOTAIRES = [
    {"nom": "MARTIN", "prenom": "François", "office": "SCP MARTIN & Associés", "ville": "Lyon 2ème"},
    {"nom": "DURAND", "prenom": "Sophie", "office": "Office Notarial du Parc", "ville": "Lyon 6ème"},
    {"nom": "BERNARD", "prenom": "Jacques", "office": "Étude BERNARD", "ville": "Villeurbanne"},
    {"nom": "DUPONT", "prenom": "Marie", "office": "SCP DUPONT-LEFEBVRE", "ville": "Lyon 3ème"},
]

GEOMETRES = [
    {"nom": "GEOMETRA", "societe": "GEOMETRA Lyon", "adresse": "15 rue de la Géométrie, 69002 Lyon"},
    {"nom": "TOPEXPERT", "societe": "TOPEXPERT SARL", "adresse": "8 avenue des Arpenteurs, 69006 Lyon"},
    {"nom": "CADASTRA", "societe": "CADASTRA & Associés", "adresse": "42 boulevard Vivier-Merle, 69003 Lyon"},
]

SYNDICS = [
    {"nom": "FONCIA Lyon", "adresse": "25 rue de la Part-Dieu, 69003 Lyon"},
    {"nom": "NEXITY Lamy", "adresse": "10 place Bellecour, 69002 Lyon"},
    {"nom": "Citya Immobilier", "adresse": "5 rue Édouard Herriot, 69001 Lyon"},
    {"nom": "Sergic", "adresse": "30 avenue Jean Jaurès, 69007 Lyon"},
]


def generer_personne_physique(genre: str = None) -> Dict:
    """Génère une personne physique fictive."""
    if genre is None:
        genre = random.choice(["homme", "femme"])

    if genre == "homme":
        civilite = "Monsieur"
        prenom = random.choice(PRENOMS_HOMMES)
    else:
        civilite = "Madame"
        prenom = random.choice(PRENOMS_FEMMES)

    nom = fake.last_name().upper()
    date_naissance = fake.date_of_birth(minimum_age=25, maximum_age=80)
    ville_naissance = random.choice(VILLES_RHONE)

    return {
        "civilite": civilite,
        "prenom": prenom,
        "nom": nom,
        "date_naissance": date_naissance.isoformat(),
        "lieu_naissance": f"{ville_naissance} (Rhône)",
        "nationalite": "française",
        "profession": random.choice(PROFESSIONS),
        "adresse": generer_adresse_complete(),
        "resident_fiscal": True
    }


def generer_situation_matrimoniale() -> Dict:
    """Génère une situation matrimoniale fictive."""
    statut = random.choice(["celibataire", "marie", "pacse", "divorce", "veuf"])

    result = {"statut": statut}

    if statut == "marie":
        result["regime_matrimonial"] = random.choice([
            "communauté légale réduite aux acquêts",
            "séparation de biens",
            "communauté universelle"
        ])
        result["contrat_mariage"] = random.random() > 0.6
        if result["contrat_mariage"]:
            date_mariage = fake.date_between(start_date="-30y", end_date="-1y")
            result["date_mariage"] = date_mariage.isoformat()
            notaire = random.choice(NOTAIRES)
            result["notaire_contrat"] = f"Maître {notaire['prenom']} {notaire['nom']}, Notaire à {notaire['ville']}"

        # Conjoint
        genre_conjoint = random.choice(["homme", "femme"])
        result["conjoint"] = generer_personne_physique(genre_conjoint)

    elif statut == "pacse":
        date_pacs = fake.date_between(start_date="-10y", end_date="-1y")
        result["date_pacs"] = date_pacs.isoformat()
        result["regime_pacs"] = random.choice(["séparation de biens", "indivision"])
        result["lieu_pacs"] = f"au greffe du tribunal judiciaire de {random.choice(['Lyon', 'Villeurbanne', 'Vénissieux'])}"
        genre_partenaire = random.choice(["homme", "femme"])
        result["partenaire"] = generer_personne_physique(genre_partenaire)
        result["conjoint"] = result["partenaire"]  # Alias pour compatibilité template

    elif statut == "divorce":
        date_jugement = fake.date_between(start_date="-15y", end_date="-1y")
        result["jugement_divorce"] = {
            "date": date_jugement.isoformat(),
            "lieu": random.choice(["Lyon", "Villeurbanne", "Vénissieux"])
        }
        genre_ex = random.choice(["homme", "femme"])
        ex_conjoint = generer_personne_physique(genre_ex)
        result["ex_conjoint"] = {
            "civilite": ex_conjoint["civilite"],
            "nom": ex_conjoint["nom"]
        }

    elif statut == "veuf":
        genre_defunt = random.choice(["homme", "femme"])
        defunt = generer_personne_physique(genre_defunt)
        result["defunt_conjoint"] = {
            "civilite": defunt["civilite"],
            "nom": defunt["nom"]
        }

    return result


def normaliser_situation_matrimoniale(sitmat: Dict) -> Dict:
    """
    Normalise la structure de situation matrimoniale pour compatibilité template.
    Transforme la structure flat en structure nested attendue par les templates.
    """
    sitmat_norm = sitmat.copy()

    # Pour PACS: restructurer en objet imbriqué
    if sitmat.get("statut") == "pacse" and "pacs" not in sitmat:
        sitmat_norm["pacs"] = {
            "date": sitmat.get("date_pacs", ""),
            "regime_libelle": sitmat.get("regime_pacs", "séparation de biens"),
            "lieu_enregistrement": sitmat.get("lieu_pacs", "au greffe du tribunal")
        }
        # Assurer que conjoint existe (alias de partenaire)
        if "partenaire" in sitmat and "conjoint" not in sitmat_norm:
            sitmat_norm["conjoint"] = sitmat["partenaire"]

    # Pour mariage: restructurer contrat_mariage
    elif sitmat.get("statut") == "marie" and sitmat.get("contrat_mariage"):
        if "contrat_mariage" not in sitmat or not isinstance(sitmat.get("contrat_mariage"), dict):
            sitmat_norm["regime_matrimonial_libelle"] = sitmat.get("regime_matrimonial", "communauté légale")
            sitmat_norm["contrat_mariage"] = {
                "date": sitmat.get("date_mariage", ""),
                "notaire": sitmat.get("notaire_contrat", ""),
                "lieu": "Lyon"
            }

    return sitmat_norm


def generer_personne_morale() -> Dict:
    """Génère une personne morale fictive."""
    forme = random.choice(FORMES_SOCIETES)
    denomination = f"{forme} {fake.last_name().upper()}"

    ville = random.choice(VILLES_RHONE)
    code_postal = random.choice([cp for cp in CODES_POSTAUX_RHONE if ville.upper() in cp or "69" in cp])

    return {
        "denomination": denomination,
        "forme_juridique": forme,
        "siege_social": generer_adresse_complete(),
        "rcs": f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)} RCS Lyon",
        "capital": random.choice([1000, 5000, 10000, 50000, 100000]),
        "representant": {
            "nom": fake.last_name().upper(),
            "prenom": random.choice(PRENOMS_HOMMES + PRENOMS_FEMMES),
            "qualite": random.choice(["Gérant", "Président", "Directeur Général"])
        }
    }


def generer_adresse_complete() -> str:
    """Génère une adresse complète."""
    numero = random.randint(1, 150)
    type_voie = random.choice(TYPES_VOIE)
    nom_voie = random.choice(NOMS_VOIE)
    ville = random.choice(VILLES_RHONE)
    code_postal = random.choice([cp for cp in CODES_POSTAUX_RHONE])

    return f"{numero} {type_voie} {nom_voie}, {code_postal} {ville}"


def generer_adresse_structuree() -> Dict:
    """Génère une adresse structurée."""
    numero = str(random.randint(1, 150))
    type_voie = random.choice(TYPES_VOIE)
    nom_voie = random.choice(NOMS_VOIE)
    ville = random.choice(VILLES_RHONE)
    code_postal = random.choice([cp for cp in CODES_POSTAUX_RHONE])

    return {
        "numero": numero,
        "voie": f"{type_voie} {nom_voie}",
        "code_postal": code_postal,
        "commune": ville,
        "departement": "Rhône"
    }


def generer_cadastre(nb_parcelles: int = 1) -> List[Dict]:
    """Génère des références cadastrales."""
    parcelles = []
    sections = ["A", "B", "C", "AB", "AC", "AD", "AE"]

    for _ in range(nb_parcelles):
        parcelles.append({
            "section": random.choice(sections),
            "numero": str(random.randint(1, 500)),
            "lieudit": "",
            "surface": f"{random.randint(100, 5000)} m²"
        })

    return parcelles


def generer_lot(numero: int, batiment: str = None) -> Dict:
    """Génère un lot de copropriété."""
    designation = random.choice(DESIGNATIONS_LOTS[:3])  # Appartement, Studio, Local commercial

    if designation in ["Appartement", "Studio"]:
        etage = random.choice(ETAGES)
        nb_pieces = random.randint(1, 5) if designation == "Appartement" else 1
        superficie = random.randint(20, 120) if designation == "Appartement" else random.randint(15, 35)

        description = f"Un {designation.lower()} de {nb_pieces} pièce{'s' if nb_pieces > 1 else ''}"
        description += f" au {etage}, comprenant: entrée, "

        if nb_pieces == 1:
            description += "séjour avec coin cuisine, salle d'eau avec WC"
        elif nb_pieces == 2:
            description += "séjour, une chambre, cuisine, salle de bains, WC"
        else:
            description += f"séjour, {nb_pieces - 1} chambres, cuisine, salle de bains, WC"

        description += f", {random.choice(ORIENTATIONS)}"

    elif designation == "Local commercial":
        superficie = random.randint(30, 200)
        description = f"Un local commercial au rez-de-chaussée, à usage de {random.choice(['commerce', 'bureau', 'activité'])}"

    else:
        superficie = random.randint(5, 20)
        description = f"Un {designation.lower()}"

    tantiemes_val = random.randint(50, 300)
    lot = {
        "numero": numero,
        "etage": etage if designation in ["Appartement", "Studio"] else "rez-de-chaussée",
        "designation": designation,
        "description_detaillee": description,
        "superficie_carrez": round(superficie + random.uniform(-2, 2), 2),
        "tantiemes_generaux": tantiemes_val,
        "tantiemes": {
            "valeur": tantiemes_val,
            "base": 1000,
            "base_unite": "millièmes",
            "type": "tantièmes généraux"
        },
        "usage": "habitation" if designation in ["Appartement", "Studio"] else "commercial"
    }

    if batiment:
        lot["batiment"] = batiment

    return lot


def generer_lot_annexe(numero: int, type_lot: str, batiment: str = None) -> Dict:
    """Génère un lot annexe (cave, parking, etc.)."""
    if type_lot == "cave":
        designation = "Cave"
        description = f"Une cave au sous-sol, numérotée {numero}"
        superficie = round(random.uniform(3, 15), 2)
        tantiemes = random.randint(5, 30)
        usage = "cave"

    elif type_lot == "parking":
        designation = "Parking"
        description = f"Un emplacement de stationnement numéroté {numero}"
        superficie = round(random.uniform(10, 15), 2)
        tantiemes = random.randint(10, 50)
        usage = "stationnement"

    elif type_lot == "box":
        designation = "Box fermé"
        description = f"Un box fermé numéroté {numero}"
        superficie = round(random.uniform(12, 20), 2)
        tantiemes = random.randint(15, 60)
        usage = "stationnement"

    else:
        designation = "Grenier"
        description = f"Un grenier sous combles"
        superficie = round(random.uniform(8, 25), 2)
        tantiemes = random.randint(10, 40)
        usage = "grenier"

    lot = {
        "numero": numero,
        "etage": "sous-sol" if type_lot in ["cave", "parking", "box"] else "combles",
        "designation": designation,
        "description_detaillee": description,
        "superficie_carrez": superficie if type_lot not in ["parking"] else None,
        "tantiemes_generaux": tantiemes,
        "tantiemes": {
            "valeur": tantiemes,
            "base": 1000,
            "base_unite": "millièmes",
            "type": "tantièmes généraux"
        },
        "usage": usage
    }

    if batiment:
        lot["batiment"] = batiment

    return lot


def generer_notaire() -> Dict:
    """Génère un notaire fictif."""
    notaire = random.choice(NOTAIRES)
    return {
        "nom": notaire["nom"],
        "prenom": notaire["prenom"],
        "office": notaire["office"],
        "adresse": f"123 rue des Notaires, 69002 {notaire['ville']}",
        "crpcen": f"{random.randint(1000, 9999)}"
    }


def generer_publication_spf() -> Dict:
    """Génère des références de publication au service de publicité foncière."""
    date = fake.date_between(start_date="-5y", end_date="-1m")
    return {
        "service": f"SPF de Lyon {random.randint(1, 5)}",
        "date": date.isoformat(),
        "volume": f"{random.randint(2020, 2024)}P{random.randint(1, 12):02d}",
        "numero": str(random.randint(1000, 9999))
    }


def generer_donnees_reglement(nb_lots: int = 10) -> Dict:
    """
    Génère un jeu de données complet pour un EDD/Règlement de copropriété.
    """
    date_acte = fake.date_between(start_date="today", end_date="+30d")

    # Requerant
    type_requerant = random.choice(["personne_physique", "personne_morale"])

    requerant = {"type": type_requerant}
    if type_requerant == "personne_physique":
        requerant["personne_physique"] = generer_personne_physique()
        requerant["personne_physique"]["situation_matrimoniale"] = generer_situation_matrimoniale()
    else:
        requerant["personne_morale"] = generer_personne_morale()

    # Immeuble
    adresse = generer_adresse_structuree()
    nb_batiments = random.randint(1, 3) if nb_lots > 10 else 1
    annee_construction = random.randint(1950, 2020)

    batiments = []
    for i in range(nb_batiments):
        nom_bat = f"Bâtiment {chr(65 + i)}" if nb_batiments > 1 else "Bâtiment unique"
        nb_niveaux = random.randint(3, 7)
        niveaux = [{"niveau": "Sous-sol", "description": "Caves et parkings"}]
        niveaux.append({"niveau": "Rez-de-chaussée", "description": "Hall d'entrée, local poubelles, locaux commerciaux"})
        for n in range(1, nb_niveaux):
            niveaux.append({"niveau": f"{n}{'er' if n == 1 else 'ème'} étage", "description": f"Appartements"})

        batiments.append({
            "nom": nom_bat,
            "usage": random.choice(["Habitation", "Mixte"]),
            "niveaux": niveaux
        })

    # Lots
    lots = []
    lot_numero = 1

    # Répartition des lots entre bâtiments
    lots_principaux = nb_lots - (nb_lots // 4)  # 75% lots principaux
    lots_annexes = nb_lots - lots_principaux

    for i in range(lots_principaux):
        batiment = batiments[i % nb_batiments]["nom"] if nb_batiments > 1 else None
        lots.append(generer_lot(lot_numero, batiment))
        lot_numero += 1

    # Lots annexes
    types_annexes = ["cave", "parking", "box"]
    for i in range(lots_annexes):
        type_annexe = random.choice(types_annexes)
        batiment = batiments[i % nb_batiments]["nom"] if nb_batiments > 1 else None
        lots.append(generer_lot_annexe(lot_numero, type_annexe, batiment))
        lot_numero += 1

    # Ajuste les tantièmes pour qu'ils totalisent 1000
    total_tantiemes = sum(lot["tantiemes_generaux"] for lot in lots)
    base_tantiemes = 1000
    facteur = base_tantiemes / total_tantiemes

    for lot in lots:
        lot["tantiemes_generaux"] = round(lot["tantiemes_generaux"] * facteur)

    # Ajuste pour atteindre exactement 1000
    diff = base_tantiemes - sum(lot["tantiemes_generaux"] for lot in lots)
    if diff != 0:
        lots[0]["tantiemes_generaux"] += diff

    # Parties communes
    parties_communes = {
        "generales": [
            "Le sol",
            "Les cours et jardins",
            "Le gros œuvre des bâtiments (fondations, murs porteurs, toiture)",
            "Les façades et revêtements extérieurs",
            "Les halls d'entrée et circulations communes",
            "Les escaliers et leurs cages",
            "Les canalisations communes",
            "Les locaux communs (local poubelles, local vélos)"
        ],
        "speciales": [],
        "jouissance_privative": []
    }

    # Parties communes spéciales si plusieurs bâtiments
    if nb_batiments > 1:
        for bat in batiments:
            parties_communes["speciales"].append({
                "nom": f"PCS {bat['nom']}",
                "description": f"Parties communes propres au {bat['nom']}: escalier, hall, façades",
                "lots_concernes": [lot["numero"] for lot in lots if lot.get("batiment") == bat["nom"]]
            })

    # Parties privatives
    parties_privatives = {
        "elements": [
            "Les locaux privatifs et leurs aménagements intérieurs",
            "Les revêtements intérieurs (sols, murs, plafonds)",
            "Les portes palières et fenêtres",
            "Les équipements sanitaires privatifs",
            "Les installations électriques privatives"
        ]
    }

    # Origine de propriété
    date_acquisition = fake.date_between(start_date="-20y", end_date="-2y")
    notaire_acquisition = random.choice(NOTAIRES)

    origine_propriete = {
        "immediate": {
            "mode_acquisition": random.choice(["achat", "donation", "succession"]),
            "date": date_acquisition.isoformat(),
            "notaire": f"Maître {notaire_acquisition['prenom']} {notaire_acquisition['nom']}, Notaire à {notaire_acquisition['ville']}",
            "publication_spf": generer_publication_spf()
        }
    }

    # Charges
    charges = {
        "cles_repartition": [
            {
                "nom": "Charges générales",
                "base_repartition": "tantiemes_generaux",
                "total_tantiemes": base_tantiemes
            }
        ],
        "total_tantiemes": base_tantiemes
    }

    # Syndic
    syndic_info = random.choice(SYNDICS)
    syndic = {
        "type": "provisoire_requerant",
        "designation": {
            "nom": syndic_info["nom"],
            "adresse": syndic_info["adresse"]
        },
        "duree_mandat": "jusqu'à la première assemblée générale"
    }

    # Diagnostics
    diagnostics = {}
    if annee_construction < datetime.now().year - 10:
        date_dtg = fake.date_between(start_date="-6m", end_date="today")
        diagnostics["dtg"] = {
            "date": date_dtg.isoformat(),
            "diagnostiqueur": f"Cabinet {fake.company()}",
            "conclusions": "L'immeuble est en bon état général. Travaux de ravalement à prévoir dans les 5 ans."
        }
        diagnostics["dtg_requis"] = True
    else:
        diagnostics["dtg_requis"] = False

    diagnostics["dpe"] = {
        "date": fake.date_between(start_date="-1y", end_date="today").isoformat(),
        "classe_energie": random.choice(["A", "B", "C", "D", "E"]),
        "classe_ges": random.choice(["A", "B", "C", "D", "E"])
    }

    # Géomètre
    geometre = random.choice(GEOMETRES)

    # Urbanisme
    urbanisme = {
        "plu_applicable": True,
        "zone_plu": random.choice(["UA", "UB", "UC", "UD"]),
        "droit_preemption": {
            "applicable": random.random() > 0.5,
            "type": "dpu_simple",
            "beneficiaire": adresse["commune"]
        }
    }

    # Annexes
    annexes = [
        {"numero": 1, "titre": "État descriptif de division", "description": "Établi par le géomètre-expert"},
        {"numero": 2, "titre": "Certificats de superficie loi Carrez", "description": "Pour chaque lot"},
        {"numero": 3, "titre": "Plans d'accès", "description": "Plan de situation"},
        {"numero": 4, "titre": "Plans des niveaux", "description": "Plans de chaque niveau"},
        {"numero": 5, "titre": "Plan cadastral", "description": "Extrait cadastral"}
    ]

    if diagnostics.get("dtg_requis"):
        annexes.append({"numero": 6, "titre": "Diagnostic Technique Global", "description": "DTG de l'immeuble"})

    # Assemblage final
    return {
        "acte": {
            "date": date_acte.isoformat(),
            "reference": f"EDD-{date_acte.year}-{random.randint(1000, 9999)}",
            "type": "edd_reglement_initial",
            "notaire": generer_notaire()
        },
        "requerant": requerant,
        "immeuble": {
            "adresse": adresse,
            "cadastre": generer_cadastre(random.randint(1, 2)),
            "description_generale": f"Un ensemble immobilier comprenant {nb_batiments} bâtiment{'s' if nb_batiments > 1 else ''} à usage d'habitation et éventuellement de commerce",
            "batiments": batiments,
            "annee_construction": annee_construction
        },
        "origine_propriete": origine_propriete,
        "lots": lots,
        "parties_communes": parties_communes,
        "parties_privatives": parties_privatives,
        "charges": charges,
        "syndic": syndic,
        "conseil_syndical": {
            "composition": "Trois membres titulaires et un suppléant",
            "membres_nombre": 3
        },
        "diagnostics": diagnostics,
        "urbanisme": urbanisme,
        "geomètre": {
            "nom": geometre["nom"],
            "societe": geometre["societe"],
            "adresse": geometre["adresse"],
            "date_edd": fake.date_between(start_date="-3m", end_date="today").isoformat()
        },
        "annexes": annexes
    }


def generer_donnees_modificatif(nb_modifications: int = 2) -> Dict:
    """
    Génère un jeu de données pour un modificatif de l'EDD.
    """
    date_acte = fake.date_between(start_date="today", end_date="+30d")

    # Syndicat des copropriétaires
    adresse = generer_adresse_structuree()
    syndicat = {
        "denomination": f"Syndicat des copropriétaires du {adresse['numero']} {adresse['voie']}, {adresse['commune']}",
        "immatriculation": f"AA{random.randint(1, 9)}-{random.randint(100, 999)}-{random.randint(100, 999)}",
        "adresse": f"{adresse['numero']} {adresse['voie']}, {adresse['code_postal']} {adresse['commune']}"
    }

    # Syndic
    syndic_info = random.choice(SYNDICS)
    representant = generer_personne_physique()

    syndic = {
        "type": "professionnel",
        "denomination": syndic_info["nom"],
        "adresse": syndic_info["adresse"],
        "representant": {
            "civilite": representant["civilite"],
            "nom": representant["nom"],
            "prenom": representant["prenom"],
            "qualite": "Directeur d'agence"
        },
        "mandat": {
            "date_debut": fake.date_between(start_date="-2y", end_date="-6m").isoformat(),
            "date_fin": fake.date_between(start_date="+6m", end_date="+2y").isoformat()
        }
    }

    # Assemblée générale autorisant
    date_ag = fake.date_between(start_date="-6m", end_date="-2m")
    type_modification = random.choice(["division_lot", "reunion_lots", "creation_pcs"])

    if type_modification == "division_lot":
        majorite = "article 25"
        objet = "Division du lot n°5 en deux lots distincts"
    elif type_modification == "reunion_lots":
        majorite = "article 25"
        objet = "Réunion des lots n°12 et n°13 en un seul lot"
    else:
        majorite = "article 26"
        objet = "Création de parties communes spéciales par bâtiment"

    assemblee_generale = {
        "date": date_ag.isoformat(),
        "resolution_numero": random.randint(5, 15),
        "objet": objet,
        "majorite_requise": majorite,
        "vote": {
            "pour": random.randint(600, 900),
            "contre": random.randint(50, 200),
            "abstention": random.randint(0, 100)
        },
        "certificat_non_recours": {
            "date": (date_ag + timedelta(days=random.randint(65, 90))).isoformat(),
            "delivre_par": syndic_info["nom"]
        }
    }

    # EDD d'origine et historique
    date_edd_origine = fake.date_between(start_date="-30y", end_date="-5y")
    notaire_origine = random.choice(NOTAIRES)

    edd_origine = {
        "date": date_edd_origine.isoformat(),
        "notaire": f"Maître {notaire_origine['prenom']} {notaire_origine['nom']}, Notaire à {notaire_origine['ville']}",
        "publication_spf": generer_publication_spf(),
        "nombre_lots_origine": random.randint(10, 30)
    }

    # Historique des modificatifs antérieurs
    historique_modificatifs = []
    nb_modifs_anterieurs = random.randint(0, 3)

    for i in range(nb_modifs_anterieurs):
        date_modif = fake.date_between(
            start_date=date_edd_origine,
            end_date="-1y"
        )
        notaire_modif = random.choice(NOTAIRES)
        historique_modificatifs.append({
            "date": date_modif.isoformat(),
            "notaire": f"Maître {notaire_modif['prenom']} {notaire_modif['nom']}",
            "objet": random.choice([
                "Division du lot n°3",
                "Réunion des lots n°7 et n°8",
                "Création d'un lot de parking",
                "Mise en conformité loi ALUR"
            ]),
            "publication_spf": generer_publication_spf()
        })

    # État actuel
    nb_lots_actuels = edd_origine["nombre_lots_origine"] + len(historique_modificatifs)
    etat_actuel = {
        "nombre_lots": nb_lots_actuels,
        "total_tantiemes": 1000
    }

    # Modifications apportées
    modifications = []

    if type_modification == "division_lot":
        lot_divise = random.randint(1, nb_lots_actuels)
        nouveau_lot_1 = nb_lots_actuels + 1
        nouveau_lot_2 = nb_lots_actuels + 2

        modifications.append({
            "type": "suppression_lot",
            "lot_numero": lot_divise,
            "description": f"Suppression du lot n°{lot_divise} (appartement de 4 pièces)"
        })
        modifications.append({
            "type": "creation_lot",
            "lot_numero": nouveau_lot_1,
            "description": f"Appartement de 2 pièces issu de la division",
            "tantiemes": random.randint(80, 120)
        })
        modifications.append({
            "type": "creation_lot",
            "lot_numero": nouveau_lot_2,
            "description": f"Appartement de 2 pièces issu de la division",
            "tantiemes": random.randint(80, 120)
        })

    elif type_modification == "reunion_lots":
        lot_1 = random.randint(1, nb_lots_actuels - 1)
        lot_2 = lot_1 + 1
        nouveau_lot = nb_lots_actuels + 1

        modifications.append({
            "type": "suppression_lot",
            "lot_numero": lot_1,
            "description": f"Suppression du lot n°{lot_1}"
        })
        modifications.append({
            "type": "suppression_lot",
            "lot_numero": lot_2,
            "description": f"Suppression du lot n°{lot_2}"
        })
        modifications.append({
            "type": "creation_lot",
            "lot_numero": nouveau_lot,
            "description": f"Appartement résultant de la réunion des lots n°{lot_1} et n°{lot_2}",
            "tantiemes": random.randint(150, 250)
        })

    else:  # creation_pcs
        modifications.append({
            "type": "creation_pcs",
            "nom": "Parties communes spéciales Bâtiment A",
            "description": "Comprenant: escalier, hall, façades du bâtiment A",
            "lots_concernes": list(range(1, nb_lots_actuels // 2 + 1))
        })
        modifications.append({
            "type": "creation_pcs",
            "nom": "Parties communes spéciales Bâtiment B",
            "description": "Comprenant: escalier, hall, façades du bâtiment B",
            "lots_concernes": list(range(nb_lots_actuels // 2 + 1, nb_lots_actuels + 1))
        })

    # Annexes
    annexes = [
        {"numero": 1, "titre": "Pouvoir du syndic", "description": "Délégation de l'assemblée générale"},
        {"numero": 2, "titre": "Procès-verbal de l'assemblée générale", "description": f"AG du {date_ag.strftime('%d/%m/%Y')}"},
        {"numero": 3, "titre": "Certificat de non-recours", "description": "Attestant l'absence de contestation"},
        {"numero": 4, "titre": "Plan cadastral", "description": "Extrait cadastral"},
        {"numero": 5, "titre": "Projet modificatif EDD", "description": "Établi par le géomètre-expert"}
    ]

    return {
        "acte": {
            "date": date_acte.isoformat(),
            "reference": f"MOD-{date_acte.year}-{random.randint(1000, 9999)}",
            "type": "modificatif_edd",
            "notaire": generer_notaire()
        },
        "syndicat_demandeur": syndicat,
        "syndic": syndic,
        "assemblee_generale": assemblee_generale,
        "immeuble": {
            "adresse": adresse,
            "cadastre": generer_cadastre(1)
        },
        "edd_origine": edd_origine,
        "historique_modificatifs": historique_modificatifs,
        "etat_actuel": etat_actuel,
        "modifications": modifications,
        "annexes": annexes
    }


def generer_donnees_vente(nb_lots: int = 1) -> Dict:
    """
    Génère un jeu de données pour une vente de lots de copropriété.
    """
    date_acte = fake.date_between(start_date="today", end_date="+30d")

    # Vendeurs (TOUJOURS personnes physiques pour compatibilité template)
    nb_vendeurs = random.randint(1, 2)
    vendeurs = []
    for _ in range(nb_vendeurs):
        vendeur = {"type": "personne_physique"}
        vendeur["personne_physique"] = generer_personne_physique()
        vendeur["personne_physique"]["situation_matrimoniale"] = normaliser_situation_matrimoniale(
            generer_situation_matrimoniale()
        )
        vendeurs.append(vendeur)

    # Acquéreurs (TOUJOURS personnes physiques pour compatibilité template)
    nb_acquereurs = random.randint(1, 2)
    acquereurs = []
    for _ in range(nb_acquereurs):
        acquereur = {"type": "personne_physique"}
        acquereur["personne_physique"] = generer_personne_physique()
        acquereur["personne_physique"]["situation_matrimoniale"] = normaliser_situation_matrimoniale(
            generer_situation_matrimoniale()
        )
        acquereurs.append(acquereur)

    # Lots
    lots = []
    for i in range(nb_lots):
        lots.append(generer_lot(i + 1))

    # Surface Carrez totale (somme des lots principaux seulement)
    superficie_totale = sum(
        lot.get("superficie_carrez", 0)
        for lot in lots
        if lot.get("superficie_carrez") is not None
    )

    # Prix
    prix_total = sum(lot.get("superficie_carrez", 50) * random.randint(2000, 6000) for lot in lots if lot.get("superficie_carrez"))
    prix_total = round(prix_total, -2)  # Arrondi à la centaine

    # Financement
    financement = {
        "type": random.choice(["comptant", "pret"]),
    }
    if financement["type"] == "pret":
        financement["montant_pret"] = round(prix_total * random.uniform(0.7, 0.95), -2)
        financement["banque"] = random.choice(["Crédit Agricole", "BNP Paribas", "Société Générale", "Caisse d'Épargne", "LCL"])
        financement["duree_mois"] = random.choice([180, 240, 300])
        financement["taux"] = round(random.uniform(2.5, 4.5), 2)

    # Quotités vendues (OBLIGATOIRE pour template)
    quotites_vendues = []
    if nb_vendeurs == 1:
        quotites_vendues.append({
            "personne_index": 0,
            "quotite": "100%",
            "type_propriete": "pleine_propriete",
            "type_propriete_libelle": "la pleine propriété"
        })
    else:
        # Répartition 50/50 par défaut
        for i in range(nb_vendeurs):
            quotites_vendues.append({
                "personne_index": i,
                "quotite": "50%",
                "type_propriete": "pleine_propriete",
                "type_propriete_libelle": "la pleine propriété indivise"
            })

    # Quotités acquises (OBLIGATOIRE pour template)
    quotites_acquises = []
    if nb_acquereurs == 1:
        quotites_acquises.append({
            "personne_index": 0,
            "quotite": "100%",
            "type_propriete": "pleine_propriete",
            "type_propriete_libelle": "la pleine propriété"
        })
    else:
        # Répartition 50/50 par défaut
        for i in range(nb_acquereurs):
            quotites_acquises.append({
                "personne_index": i,
                "quotite": "50%",
                "type_propriete": "pleine_propriete",
                "type_propriete_libelle": "la pleine propriété indivise"
            })

    return {
        "acte": {
            "date": date_acte.isoformat(),
            "reference": f"VTE-{date_acte.year}-{random.randint(1000, 9999)}",
            "type": "vente_lots_copropriete",
            "notaire": generer_notaire()
        },
        "vendeurs": vendeurs,
        "acquereurs": acquereurs,
        "quotites_vendues": quotites_vendues,
        "quotites_acquises": quotites_acquises,
        "bien": {
            "adresse": generer_adresse_structuree(),
            "cadastre": generer_cadastre(1),
            "lots": lots,
            "superficie_carrez": {
                "superficie_m2": round(superficie_totale, 2),
                "lot_concerne": lots[0]["numero"] if lots else 1
            }
        },
        "prix": {
            "montant": prix_total,
            "modalites_paiement": "comptant" if financement["type"] == "comptant" else "partie comptant, partie à crédit"
        },
        "financement": financement,
        "meubles": {
            "inclus": random.choice([True, False]),
            "valeur": random.choice([None, random.randint(1000, 5000)]) if random.choice([True, False]) else None,
            "liste": [
                "Cuisine équipée avec plaques de cuisson, four encastrable et hotte",
                "Salle de bain avec meuble vasque",
                "Rangements sur mesure dans la chambre"
            ] if random.choice([True, False]) else []
        },
        "jouissance": {
            "jouissance_anticipee": random.choice([True, False]),
            "date_jouissance": fake.date_between(start_date="-3m", end_date="today").isoformat() if random.choice([True, False]) else None,
            "convention_occupation": {
                "date": fake.date_between(start_date="-3m", end_date="today").isoformat()
            } if random.choice([True, False]) else None
        },
        "diagnostics": {
            "dpe": {
                "date": fake.date_between(start_date="-6m", end_date="today").isoformat(),
                "classe_energie": random.choice(["A", "B", "C", "D", "E", "F", "G"]),
                "classe_ges": random.choice(["A", "B", "C", "D", "E", "F", "G"])
            }
        },
        "copropriete": {
            "syndic": {
                "nom": random.choice(["Cabinet FONCIA", "ORPI Gestion", "Nexity", "Citya Immobilier", "SERGIC"]),
                "adresse": generer_adresse_complete(),
                "telephone": f"0{random.randint(1, 9)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
            },
            "reglement": {
                "notaire_origine": f"Maître {random.choice(NOTAIRES)['nom']}",
                "date_origine": fake.date_between(start_date="-30y", end_date="-5y").isoformat(),
                "publication": "Lyon 3ème",
                "modificatifs": []
            },
            "immatriculation": {
                "numero": f"{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(100, 999)}",
                "date": fake.date_between(start_date="-10y", end_date="-1y").isoformat()
            }
        }
    }


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description="Génère des données de test réalistes pour actes notariés",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python generer_donnees_test.py --type reglement --output .tmp/test_edd.json
  python generer_donnees_test.py --type reglement --lots 20 --output .tmp/test_edd_20lots.json
  python generer_donnees_test.py --type modificatif --output .tmp/test_modificatif.json
  python generer_donnees_test.py --type vente --output .tmp/test_vente.json
        """
    )

    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["vente", "promesse", "reglement", "modificatif"],
        help="Type d'acte pour lequel générer les données"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier de sortie JSON (défaut: .tmp/test_{type}.json)"
    )

    parser.add_argument(
        "--lots",
        type=int,
        default=10,
        help="Nombre de lots à générer (pour reglement et vente)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="Seed pour la génération aléatoire (pour reproductibilité)"
    )

    args = parser.parse_args()

    # Initialise le seed si fourni
    if args.seed:
        Faker.seed(args.seed)
        random.seed(args.seed)

    # Détermine le fichier de sortie
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = TMP_DIR / f"test_{args.type}.json"

    # Génère les données selon le type
    if args.type == "reglement":
        donnees = generer_donnees_reglement(nb_lots=args.lots)
    elif args.type == "modificatif":
        donnees = generer_donnees_modificatif()
    elif args.type == "vente":
        donnees = generer_donnees_vente(nb_lots=args.lots)
    elif args.type == "promesse":
        # Pour l'instant, utilise les mêmes données que vente
        donnees = generer_donnees_vente(nb_lots=args.lots)
        donnees["acte"]["type"] = "promesse_vente"
    else:
        print(f"Type d'acte non supporté: {args.type}")
        sys.exit(1)

    # Crée le répertoire de sortie si nécessaire
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Écrit le fichier JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    print(f"[OK] Donnees generees: {output_path}")
    print(f"  Type: {args.type}")
    if args.type in ["reglement", "vente"]:
        print(f"  Lots: {len(donnees.get('lots', donnees.get('bien', {}).get('lots', [])))}")


if __name__ == "__main__":
    main()
