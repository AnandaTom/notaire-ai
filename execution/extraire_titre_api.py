#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraire_titre_api.py
---------------------
Module d'extraction de titres de propriété pour intégration API/Frontend.

Ce module fournit:
- Fonctions asynchrones pour l'extraction
- Support des uploads de fichiers (bytes)
- Intégration Supabase automatique
- Modèles de réponse standardisés

Usage:
    # Depuis FastAPI endpoint
    from execution.extraire_titre_api import ExtractionTitreAPI

    api = ExtractionTitreAPI()
    result = await api.extraire_depuis_upload(file_content, filename)

    # Avec stockage Supabase
    result = await api.extraire_et_stocker(file_content, filename, etude_id)
"""

import asyncio
import hashlib
import io
import json
import os
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import du module d'extraction existant
try:
    from execution.utils.extraire_titre import (
        extraire_donnees_titre,
        extraire_texte,
        calculer_hash_fichier
    )
except ImportError:
    from extraire_titre_propriete import (
        extraire_donnees_titre,
        extraire_texte,
        calculer_hash_fichier
    )

# Supabase (optionnel)
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False


# =============================================================================
# MODÈLES DE DONNÉES
# =============================================================================

class StatutExtraction(Enum):
    """Statut de l'extraction."""
    SUCCES = "succes"
    PARTIEL = "partiel"
    ECHEC = "echec"


@dataclass
class ResultatExtraction:
    """Résultat d'une extraction de titre."""
    statut: StatutExtraction
    titre_id: Optional[str] = None
    donnees: Optional[Dict[str, Any]] = None
    confiance: float = 0.0
    champs_manquants: List[str] = field(default_factory=list)
    erreur: Optional[str] = None
    temps_extraction_ms: int = 0
    stocke_supabase: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON."""
        return {
            "statut": self.statut.value,
            "titre_id": self.titre_id,
            "donnees": self.donnees,
            "confiance": self.confiance,
            "champs_manquants": self.champs_manquants,
            "erreur": self.erreur,
            "temps_extraction_ms": self.temps_extraction_ms,
            "stocke_supabase": self.stocke_supabase
        }


@dataclass
class TitreStocke:
    """Titre stocké dans Supabase."""
    id: str
    reference: str
    etude_id: str
    nom_fichier: str
    hash_fichier: str
    date_upload: str
    donnees: Dict[str, Any]
    confiance: float
    created_at: str


# =============================================================================
# CLASSE PRINCIPALE
# =============================================================================

class ExtractionTitreAPI:
    """
    API d'extraction de titres de propriété.

    Fournit des méthodes asynchrones pour:
    - Extraire depuis un fichier uploadé (bytes)
    - Extraire depuis un chemin de fichier
    - Stocker automatiquement dans Supabase
    - Rechercher des titres existants
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialise l'API d'extraction.

        Args:
            supabase_url: URL Supabase (ou depuis SUPABASE_URL env var)
            supabase_key: Clé Supabase (ou depuis SUPABASE_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        self._supabase: Optional[Client] = None

        # Charger le mapping titre → promesse si disponible
        self._mapping_promesse: Optional[Dict] = None
        try:
            mapping_path = Path(__file__).parent.parent / "schemas" / "promesse_catalogue_unifie.json"
            if mapping_path.exists():
                with open(mapping_path, "r", encoding="utf-8") as f:
                    catalogue = json.load(f)
                    self._mapping_promesse = catalogue.get("mapping_titre_propriete", {})
        except Exception:
            pass

    @property
    def supabase(self) -> Optional[Client]:
        """Client Supabase (lazy loading)."""
        if not self._supabase and HAS_SUPABASE and self.supabase_url and self.supabase_key:
            self._supabase = create_client(self.supabase_url, self.supabase_key)
        return self._supabase

    # =========================================================================
    # MÉTHODES D'EXTRACTION
    # =========================================================================

    async def extraire_depuis_upload(
        self,
        file_content: bytes,
        filename: str,
        verbose: bool = False
    ) -> ResultatExtraction:
        """
        Extrait les données d'un titre depuis un fichier uploadé.

        Args:
            file_content: Contenu du fichier en bytes
            filename: Nom du fichier original
            verbose: Mode verbeux

        Returns:
            ResultatExtraction avec les données extraites
        """
        start_time = datetime.now()

        # Déterminer l'extension
        suffix = Path(filename).suffix.lower()
        if suffix not in [".pdf", ".docx", ".doc"]:
            return ResultatExtraction(
                statut=StatutExtraction.ECHEC,
                erreur=f"Format non supporté: {suffix}. Formats acceptés: PDF, DOCX"
            )

        # Sauvegarder temporairement
        try:
            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False,
                prefix="titre_"
            ) as tmp_file:
                tmp_file.write(file_content)
                tmp_path = Path(tmp_file.name)

            # Extraire (en async via thread pool)
            loop = asyncio.get_event_loop()
            donnees = await loop.run_in_executor(
                None,
                lambda: extraire_donnees_titre(tmp_path, verbose=verbose)
            )

            # Calculer le hash
            hash_fichier = hashlib.sha256(file_content).hexdigest()

            # Enrichir les métadonnées
            donnees["source"]["hash_fichier"] = hash_fichier
            donnees["source"]["nom_fichier"] = filename

            # Générer un ID unique
            titre_id = f"TITRE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash_fichier[:8]}"
            donnees["reference"] = titre_id

            # Calculer le temps
            temps_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Déterminer le statut
            confiance = donnees.get("metadata", {}).get("confiance", 0)
            champs_manquants = donnees.get("metadata", {}).get("champs_manquants", [])

            if confiance >= 0.7:
                statut = StatutExtraction.SUCCES
            elif confiance >= 0.4:
                statut = StatutExtraction.PARTIEL
            else:
                statut = StatutExtraction.ECHEC

            return ResultatExtraction(
                statut=statut,
                titre_id=titre_id,
                donnees=donnees,
                confiance=confiance,
                champs_manquants=champs_manquants,
                temps_extraction_ms=temps_ms
            )

        except Exception as e:
            return ResultatExtraction(
                statut=StatutExtraction.ECHEC,
                erreur=str(e),
                temps_extraction_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )

        finally:
            # Nettoyer le fichier temporaire
            if 'tmp_path' in locals() and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass

    async def extraire_depuis_fichier(
        self,
        filepath: Union[str, Path],
        verbose: bool = False
    ) -> ResultatExtraction:
        """
        Extrait les données d'un titre depuis un chemin de fichier.

        Args:
            filepath: Chemin vers le fichier
            verbose: Mode verbeux

        Returns:
            ResultatExtraction avec les données extraites
        """
        filepath = Path(filepath)

        if not filepath.exists():
            return ResultatExtraction(
                statut=StatutExtraction.ECHEC,
                erreur=f"Fichier non trouvé: {filepath}"
            )

        # Lire le contenu
        with open(filepath, "rb") as f:
            content = f.read()

        return await self.extraire_depuis_upload(content, filepath.name, verbose)

    # =========================================================================
    # INTÉGRATION SUPABASE
    # =========================================================================

    async def extraire_et_stocker(
        self,
        file_content: bytes,
        filename: str,
        etude_id: str,
        verbose: bool = False
    ) -> ResultatExtraction:
        """
        Extrait un titre et le stocke dans Supabase.

        Args:
            file_content: Contenu du fichier
            filename: Nom du fichier
            etude_id: ID de l'étude notariale
            verbose: Mode verbeux

        Returns:
            ResultatExtraction avec le titre stocké
        """
        # D'abord extraire
        result = await self.extraire_depuis_upload(file_content, filename, verbose)

        if result.statut == StatutExtraction.ECHEC:
            return result

        # Puis stocker si Supabase disponible
        if self.supabase and result.donnees:
            try:
                # Préparer les données pour Supabase
                titre_data = {
                    "reference": result.titre_id,
                    "etude_id": etude_id,
                    "nom_fichier": filename,
                    "hash_fichier": result.donnees.get("source", {}).get("hash_fichier"),
                    "date_acte": result.donnees.get("date_acte"),
                    "adresse_bien": self._extraire_adresse_complete(result.donnees),
                    "proprietaires": result.donnees.get("proprietaires_actuels", []),
                    "bien": result.donnees.get("bien", {}),
                    "prix": result.donnees.get("prix", {}),
                    "copropriete": result.donnees.get("copropriete", {}),
                    "origine_propriete": result.donnees.get("origine_propriete", []),
                    "donnees_completes": result.donnees,
                    "confiance_extraction": result.confiance,
                    "methode_extraction": "api_upload"
                }

                # Insérer dans Supabase (async via thread)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.supabase.table("titres_propriete").insert(titre_data).execute()
                )

                if response.data:
                    result.stocke_supabase = True
                    result.titre_id = response.data[0].get("id", result.titre_id)

            except Exception as e:
                # Ne pas échouer si Supabase échoue, juste logger
                if verbose:
                    print(f"Warning: Stockage Supabase échoué: {e}")

        return result

    async def rechercher_titre(
        self,
        adresse: Optional[str] = None,
        proprietaire: Optional[str] = None,
        etude_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recherche des titres dans Supabase.

        Args:
            adresse: Recherche par adresse (partielle)
            proprietaire: Recherche par nom de propriétaire
            etude_id: Filtrer par étude
            limit: Nombre maximum de résultats

        Returns:
            Liste des titres correspondants
        """
        if not self.supabase:
            return []

        try:
            query = self.supabase.table("titres_propriete").select("*")

            if adresse:
                query = query.ilike("adresse_bien", f"%{adresse}%")

            if etude_id:
                query = query.eq("etude_id", etude_id)

            query = query.limit(limit).order("created_at", desc=True)

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: query.execute())

            return response.data or []

        except Exception:
            return []

    async def obtenir_titre(self, titre_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un titre par son ID.

        Args:
            titre_id: ID du titre

        Returns:
            Données du titre ou None
        """
        if not self.supabase:
            return None

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.supabase.table("titres_propriete").select("*").eq("id", titre_id).single().execute()
            )
            return response.data

        except Exception:
            return None

    # =========================================================================
    # CONVERSION VERS PROMESSE
    # =========================================================================

    def titre_vers_donnees_promesse(
        self,
        titre_data: Dict[str, Any],
        beneficiaires: List[Dict[str, Any]],
        prix: Dict[str, Any],
        financement: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convertit un titre de propriété en données pour une promesse de vente.

        Args:
            titre_data: Données du titre extrait
            beneficiaires: Liste des bénéficiaires (futurs acquéreurs)
            prix: Informations sur le prix {"montant": int}
            financement: Informations de financement (optionnel)
            options: Options supplémentaires (mobilier, délai, etc.)

        Returns:
            Dictionnaire de données pour génération de promesse
        """
        options = options or {}

        # Récupérer les données extraites
        donnees_completes = titre_data.get("donnees_completes", titre_data)

        # Construire les promettants depuis les propriétaires actuels
        proprietaires = donnees_completes.get("proprietaires_actuels", [])
        promettants = []

        for prop in proprietaires:
            promettant = {
                "civilite": prop.get("civilite", "Monsieur"),
                "nom": prop.get("nom", ""),
                "prenoms": prop.get("prenoms", ""),
                "date_naissance": prop.get("date_naissance", ""),
                "lieu_naissance": prop.get("lieu_naissance", ""),
                "adresse": prop.get("adresse", ""),
                "profession": prop.get("profession", "")
            }

            # Ajouter situation matrimoniale si présente
            if "situation_matrimoniale" in prop:
                promettant["situation_matrimoniale"] = prop["situation_matrimoniale"]

            promettants.append(promettant)

        # Construire le bien depuis les données extraites
        bien_source = donnees_completes.get("bien", {})
        adresse_source = bien_source.get("adresse", {})

        bien = {
            "adresse": adresse_source.get("voie", ""),
            "numero": adresse_source.get("numero", ""),
            "code_postal": adresse_source.get("code_postal", ""),
            "ville": adresse_source.get("ville", ""),
            "copropriete": bool(bien_source.get("lots") or donnees_completes.get("copropriete")),
            "lots": bien_source.get("lots", []),
            "cadastre": {
                "parcelles": bien_source.get("cadastre", [])
            }
        }

        # Ajouter Carrez si disponible
        if "superficie_carrez" in bien_source:
            bien["carrez"] = bien_source["superficie_carrez"]

        # Construire la structure complète
        donnees_promesse = {
            "reference": f"PROMESSE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "date_promesse": datetime.now().strftime("%Y-%m-%d"),
            "promettants": promettants,
            "beneficiaires": beneficiaires,
            "bien": bien,
            "prix": prix,
            "source_titre": {
                "titre_id": titre_data.get("id") or titre_data.get("reference"),
                "date_titre": donnees_completes.get("date_acte"),
                "hash_fichier": donnees_completes.get("source", {}).get("hash_fichier")
            }
        }

        # Ajouter copropriété si présente
        if donnees_completes.get("copropriete"):
            donnees_promesse["copropriete"] = donnees_completes["copropriete"]

        # Ajouter origine de propriété
        if donnees_completes.get("origine_propriete"):
            donnees_promesse["origine_propriete"] = donnees_completes["origine_propriete"]

        # Ajouter financement si présent
        if financement:
            donnees_promesse["financement"] = financement

        # Ajouter options
        if options.get("mobilier"):
            donnees_promesse["mobilier"] = options["mobilier"]

        if options.get("delai_realisation"):
            donnees_promesse["delai_realisation"] = options["delai_realisation"]

        if options.get("indemnite"):
            donnees_promesse["indemnite"] = options["indemnite"]
        else:
            # Calculer indemnité par défaut (10%)
            montant_prix = prix.get("montant", 0)
            donnees_promesse["indemnite"] = {
                "montant": int(montant_prix * 0.10),
                "pourcentage": 10
            }

        return donnees_promesse

    # =========================================================================
    # MÉTHODES UTILITAIRES
    # =========================================================================

    def _extraire_adresse_complete(self, donnees: Dict[str, Any]) -> str:
        """Extrait l'adresse complète formatée."""
        bien = donnees.get("bien", {})
        adresse = bien.get("adresse", {})

        parts = []
        if adresse.get("numero"):
            parts.append(adresse["numero"])
        if adresse.get("voie"):
            parts.append(adresse["voie"])
        if adresse.get("code_postal"):
            parts.append(adresse["code_postal"])
        if adresse.get("ville"):
            parts.append(adresse["ville"])

        return " ".join(parts) if parts else ""

    def get_formats_supportes(self) -> List[str]:
        """Retourne la liste des formats de fichiers supportés."""
        return [".pdf", ".docx", ".doc"]

    def get_champs_attendus(self) -> List[str]:
        """Retourne la liste des champs attendus dans un titre."""
        return [
            "date_acte",
            "notaire",
            "publication",
            "proprietaires_actuels",
            "bien",
            "prix",
            "origine_propriete",
            "copropriete"
        ]


# =============================================================================
# FONCTIONS UTILITAIRES STANDALONE
# =============================================================================

async def extraire_titre_upload(
    file_content: bytes,
    filename: str,
    etude_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour extraction rapide.

    Args:
        file_content: Contenu du fichier
        filename: Nom du fichier
        etude_id: ID étude (optionnel, pour stockage)

    Returns:
        Dictionnaire avec résultat
    """
    api = ExtractionTitreAPI()

    if etude_id:
        result = await api.extraire_et_stocker(file_content, filename, etude_id)
    else:
        result = await api.extraire_depuis_upload(file_content, filename)

    return result.to_dict()


# =============================================================================
# CLI (pour tests)
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="API d'extraction de titres")
    parser.add_argument("--file", "-f", required=True, help="Fichier à extraire")
    parser.add_argument("--etude", "-e", help="ID de l'étude (pour stockage Supabase)")
    parser.add_argument("--output", "-o", help="Fichier JSON de sortie")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    async def run():
        api = ExtractionTitreAPI()

        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Erreur: fichier non trouvé: {filepath}")
            return

        with open(filepath, "rb") as f:
            content = f.read()

        if args.etude:
            result = await api.extraire_et_stocker(content, filepath.name, args.etude, args.verbose)
        else:
            result = await api.extraire_depuis_upload(content, filepath.name, args.verbose)

        output = result.to_dict()

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"Résultat sauvegardé dans {args.output}")
        else:
            print(json.dumps(output, ensure_ascii=False, indent=2))

    asyncio.run(run())


if __name__ == "__main__":
    main()
