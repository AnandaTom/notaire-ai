#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gestionnaire_titres_propriete.py
--------------------------------
Gestionnaire complet des titres de propriété avec intégration Supabase.

Fonctionnalités:
- Upload et extraction automatique de titres de propriété
- Stockage et recherche dans Supabase
- Conversion vers promesse de vente et acte de vente
- Workflow complet: Titre → Promesse → Vente

Usage:
    # Upload et extraction
    python gestionnaire_titres_propriete.py upload --file titre.pdf

    # Recherche par adresse ou nom
    python gestionnaire_titres_propriete.py search --query "Tassin"

    # Convertir vers promesse de vente
    python gestionnaire_titres_propriete.py convert --titre TITRE-001 --type promesse

    # Lister tous les titres
    python gestionnaire_titres_propriete.py list
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict, field

# Configuration encodage Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Imports projet
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))

from extraire_titre_propriete import extraire_donnees_titre

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    Client = None

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            text = str(args[0]) if args else ""
            import re
            text = re.sub(r'\[.*?\]', '', text)
            print(text)
    console = Console()


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class TitrePropriete:
    """Représente un titre de propriété dans la base."""
    id: Optional[str] = None
    reference: str = ""
    date_creation: Optional[str] = None
    date_modification: Optional[str] = None
    statut: str = "actif"
    donnees: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    fichier_source: Optional[str] = None

    @property
    def adresse_complete(self) -> str:
        """Retourne l'adresse complète du bien."""
        bien = self.donnees.get("bien", {})
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
        return " ".join(parts) if parts else "Adresse non renseignée"

    @property
    def proprietaires_noms(self) -> str:
        """Retourne les noms des propriétaires."""
        props = self.donnees.get("proprietaires_actuels", [])
        noms = [p.get("nom", "") for p in props if p.get("nom")]
        return ", ".join(noms) if noms else "Inconnu"


@dataclass
class DossierNotarial:
    """Représente un dossier notarial complet (titre + promesse + vente)."""
    id: Optional[str] = None
    reference: str = ""
    statut: str = "en_cours"
    titre_id: Optional[str] = None
    promesse_id: Optional[str] = None
    vente_id: Optional[str] = None
    date_creation: Optional[str] = None
    date_modification: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


# =============================================================================
# GESTIONNAIRE
# =============================================================================

class GestionnaireTitres:
    """
    Gestionnaire des titres de propriété avec intégration Supabase.

    Gère le workflow complet:
    1. Upload et extraction automatique du titre
    2. Stockage et recherche dans Supabase
    3. Conversion vers promesse de vente
    4. Conversion vers acte de vente
    """

    def __init__(self):
        """Initialise le gestionnaire."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None
        self._offline_mode = False
        self._offline_storage: Dict[str, Dict] = {}

        # Dossiers de stockage local
        self.titres_dir = PROJECT_ROOT / ".tmp" / "titres_propriete"
        self.titres_dir.mkdir(parents=True, exist_ok=True)

        self._init_client()

    def _init_client(self) -> None:
        """Initialise le client Supabase."""
        if not HAS_SUPABASE:
            console.print("[yellow]Module supabase non installé. Mode hors-ligne activé.[/yellow]")
            self._offline_mode = True
            return

        if not self.supabase_url or not self.supabase_key:
            console.print("[yellow]Configuration Supabase manquante. Mode hors-ligne activé.[/yellow]")
            self._offline_mode = True
            return

        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            console.print(f"[red]Erreur connexion Supabase: {e}[/red]")
            self._offline_mode = True

    # -------------------------------------------------------------------------
    # UPLOAD ET EXTRACTION
    # -------------------------------------------------------------------------

    def upload_titre(
        self,
        filepath: Path,
        reference: Optional[str] = None,
        verbose: bool = False
    ) -> Optional[TitrePropriete]:
        """
        Upload un titre de propriété et extrait automatiquement les données.

        Args:
            filepath: Chemin vers le fichier (PDF ou DOCX)
            reference: Référence personnalisée (auto-générée si None)
            verbose: Mode verbeux

        Returns:
            TitrePropriete créé ou None si erreur
        """
        if not filepath.exists():
            console.print(f"[red]Fichier non trouvé: {filepath}[/red]")
            return None

        if verbose:
            console.print(f"[blue]Upload de {filepath.name}...[/blue]")

        # Extraire les données
        try:
            donnees = extraire_donnees_titre(filepath, verbose=verbose)
        except Exception as e:
            console.print(f"[red]Erreur extraction: {e}[/red]")
            return None

        # Vérifier si le fichier existe déjà (déduplication par hash)
        hash_fichier = donnees.get("source", {}).get("hash_fichier", "")
        existing = self._trouver_par_hash(hash_fichier)
        if existing:
            console.print(f"[yellow]⚠ Ce fichier existe déjà: {existing.reference}[/yellow]")
            return existing

        # Générer la référence
        if not reference:
            reference = donnees.get("reference", f"TITRE-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

        # Copier le fichier dans le dossier de stockage
        dest_path = self.titres_dir / f"{reference}{filepath.suffix}"
        shutil.copy2(filepath, dest_path)

        # Créer le titre
        titre = TitrePropriete(
            reference=reference,
            date_creation=datetime.now().isoformat(),
            date_modification=datetime.now().isoformat(),
            statut="actif",
            donnees=donnees,
            fichier_source=str(dest_path),
            metadata={
                "source_originale": str(filepath),
                "confiance": donnees.get("metadata", {}).get("confiance", 0)
            }
        )

        # Sauvegarder
        titre_id = self._sauvegarder_titre(titre)
        if titre_id:
            titre.id = titre_id
            console.print(f"[green]✓ Titre créé: {reference}[/green]")
            return titre

        return None

    def _trouver_par_hash(self, hash_fichier: str) -> Optional[TitrePropriete]:
        """Trouve un titre par le hash de son fichier source."""
        if not hash_fichier:
            return None

        if self._offline_mode:
            for ref, data in self._offline_storage.items():
                if data.get("donnees", {}).get("source", {}).get("hash_fichier") == hash_fichier:
                    return TitrePropriete(**data)
            return None

        try:
            # Recherche dans JSONB
            result = self.client.table("titres_propriete").select("*").execute()
            for row in result.data:
                donnees = row.get("donnees", {})
                if donnees.get("source", {}).get("hash_fichier") == hash_fichier:
                    return self._row_to_titre(row)
        except Exception:
            pass

        return None

    # -------------------------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------------------------

    def _sauvegarder_titre(self, titre: TitrePropriete) -> Optional[str]:
        """Sauvegarde un titre dans Supabase ou en local."""
        if self._offline_mode:
            titre_id = f"offline_{titre.reference}"
            self._offline_storage[titre.reference] = {
                "id": titre_id,
                "reference": titre.reference,
                "date_creation": titre.date_creation,
                "date_modification": titre.date_modification,
                "statut": titre.statut,
                "donnees": titre.donnees,
                "metadata": titre.metadata,
                "fichier_source": titre.fichier_source
            }

            # Sauvegarder aussi en fichier JSON
            json_path = self.titres_dir / f"{titre.reference}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self._offline_storage[titre.reference], f, ensure_ascii=False, indent=2)

            return titre_id

        try:
            # Vérifie si existe
            existing = self.client.table("titres_propriete").select("id").eq("reference", titre.reference).execute()

            data = {
                "reference": titre.reference,
                "donnees": titre.donnees,
                "metadata": titre.metadata,
                "statut": titre.statut,
                "fichier_source": titre.fichier_source,
                "date_modification": datetime.now().isoformat()
            }

            if existing.data:
                # Update
                result = self.client.table("titres_propriete").update(data).eq("reference", titre.reference).execute()
                return existing.data[0]["id"]
            else:
                # Insert
                data["date_creation"] = datetime.now().isoformat()
                result = self.client.table("titres_propriete").insert(data).execute()
                return result.data[0]["id"] if result.data else None

        except Exception as e:
            console.print(f"[red]Erreur sauvegarde: {e}[/red]")
            return None

    def charger_titre(self, reference: str) -> Optional[TitrePropriete]:
        """Charge un titre par sa référence."""
        if self._offline_mode:
            # Essayer le storage en mémoire
            if reference in self._offline_storage:
                return TitrePropriete(**self._offline_storage[reference])

            # Essayer de charger depuis le fichier
            json_path = self.titres_dir / f"{reference}.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._offline_storage[reference] = data
                    return TitrePropriete(**data)

            return None

        try:
            result = self.client.table("titres_propriete").select("*").eq("reference", reference).execute()
            if result.data:
                return self._row_to_titre(result.data[0])
            return None
        except Exception as e:
            console.print(f"[red]Erreur chargement: {e}[/red]")
            return None

    def lister_titres(
        self,
        statut: Optional[str] = None,
        limite: int = 50
    ) -> List[TitrePropriete]:
        """Liste tous les titres."""
        if self._offline_mode:
            # Charger tous les fichiers JSON
            for json_file in self.titres_dir.glob("TITRE-*.json"):
                ref = json_file.stem
                if ref not in self._offline_storage:
                    with open(json_file, "r", encoding="utf-8") as f:
                        self._offline_storage[ref] = json.load(f)

            titres = [TitrePropriete(**data) for data in self._offline_storage.values()]
            if statut:
                titres = [t for t in titres if t.statut == statut]
            return titres[:limite]

        try:
            query = self.client.table("titres_propriete").select("*")
            if statut:
                query = query.eq("statut", statut)
            query = query.order("date_creation", desc=True).limit(limite)
            result = query.execute()
            return [self._row_to_titre(row) for row in result.data]
        except Exception as e:
            console.print(f"[red]Erreur listage: {e}[/red]")
            return []

    def rechercher_titres(self, query: str) -> List[TitrePropriete]:
        """Recherche dans les titres (nom, adresse, référence)."""
        if self._offline_mode:
            # Recherche simple en mémoire
            resultats = []
            query_lower = query.lower()
            for ref, data in self._offline_storage.items():
                # Recherche dans la référence
                if query_lower in ref.lower():
                    resultats.append(TitrePropriete(**data))
                    continue
                # Recherche dans les données JSON
                if query_lower in json.dumps(data.get("donnees", {}), ensure_ascii=False).lower():
                    resultats.append(TitrePropriete(**data))
            return resultats

        try:
            # Recherche par référence
            result = self.client.table("titres_propriete").select("*").ilike("reference", f"%{query}%").execute()
            titres = [self._row_to_titre(row) for row in result.data]

            # TODO: Ajouter recherche full-text dans donnees JSONB

            return titres
        except Exception as e:
            console.print(f"[red]Erreur recherche: {e}[/red]")
            return []

    def _row_to_titre(self, row: Dict) -> TitrePropriete:
        """Convertit une ligne Supabase en TitrePropriete."""
        return TitrePropriete(
            id=row.get("id"),
            reference=row.get("reference", ""),
            date_creation=row.get("date_creation"),
            date_modification=row.get("date_modification"),
            statut=row.get("statut", "actif"),
            donnees=row.get("donnees", {}),
            metadata=row.get("metadata", {}),
            fichier_source=row.get("fichier_source")
        )

    # -------------------------------------------------------------------------
    # CONVERSION VERS PROMESSE / VENTE
    # -------------------------------------------------------------------------

    def convertir_vers_promesse(
        self,
        titre_reference: str,
        beneficiaires: List[Dict] = None,
        prix: int = None
    ) -> Dict:
        """
        Convertit un titre de propriété en données pour promesse de vente.

        Args:
            titre_reference: Référence du titre source
            beneficiaires: Liste des bénéficiaires (acquéreurs potentiels)
            prix: Prix de vente proposé

        Returns:
            Données JSON pour générer une promesse de vente
        """
        titre = self.charger_titre(titre_reference)
        if not titre:
            raise ValueError(f"Titre non trouvé: {titre_reference}")

        donnees_titre = titre.donnees

        # Construire les données de la promesse
        promesse = {
            "acte": {
                "numero_repertoire": "",
                "reference_interne": f"PROM-{datetime.now().strftime('%Y-%m-%d')}",
                "date": {
                    "jour": datetime.now().day,
                    "mois": datetime.now().strftime("%B").lower(),
                    "annee": datetime.now().year
                },
                "notaire": {}  # À remplir par le notaire
            },
            "promettants": self._convertir_proprietaires_vers_promettants(
                donnees_titre.get("proprietaires_actuels", [])
            ),
            "beneficiaires": beneficiaires or [],
            "bien": self._convertir_bien(donnees_titre.get("bien", {})),
            "copropriete": donnees_titre.get("copropriete", {}),
            "origine_propriete": self._convertir_origine(
                donnees_titre,
                titre_reference
            ),
            "prix": {
                "montant": prix or donnees_titre.get("prix", {}).get("montant_total", 0),
                "devise": "EUR"
            },
            "_source_titre": {
                "reference": titre_reference,
                "date_extraction": donnees_titre.get("metadata", {}).get("date_extraction"),
                "confiance": donnees_titre.get("metadata", {}).get("confiance", 0)
            }
        }

        return promesse

    def convertir_vers_vente(
        self,
        titre_reference: str,
        promesse_reference: Optional[str] = None,
        acquereurs: List[Dict] = None,
        prix: int = None
    ) -> Dict:
        """
        Convertit un titre de propriété en données pour acte de vente.

        Args:
            titre_reference: Référence du titre source
            promesse_reference: Référence de la promesse (optionnel)
            acquereurs: Liste des acquéreurs
            prix: Prix de vente définitif

        Returns:
            Données JSON pour générer un acte de vente
        """
        titre = self.charger_titre(titre_reference)
        if not titre:
            raise ValueError(f"Titre non trouvé: {titre_reference}")

        donnees_titre = titre.donnees

        # Construire les données de la vente
        vente = {
            "acte": {
                "numero_repertoire": "",
                "reference_interne": f"VTE-{datetime.now().strftime('%Y-%m-%d')}",
                "date": {
                    "jour": datetime.now().day,
                    "mois": datetime.now().strftime("%B").lower(),
                    "annee": datetime.now().year
                },
                "notaire": {}  # À remplir par le notaire
            },
            "vendeurs": self._convertir_proprietaires_vers_vendeurs(
                donnees_titre.get("proprietaires_actuels", [])
            ),
            "acquereurs": acquereurs or [],
            "bien": self._convertir_bien(donnees_titre.get("bien", {})),
            "copropriete": donnees_titre.get("copropriete", {}),
            "origine_propriete": self._convertir_origine(
                donnees_titre,
                titre_reference
            ),
            "prix": {
                "montant": prix or donnees_titre.get("prix", {}).get("montant_total", 0),
                "devise": "EUR"
            },
            "_source": {
                "titre_reference": titre_reference,
                "promesse_reference": promesse_reference
            }
        }

        return vente

    def _convertir_proprietaires_vers_promettants(self, proprietaires: List[Dict]) -> List[Dict]:
        """Convertit les propriétaires actuels en promettants."""
        promettants = []
        for prop in proprietaires:
            promettant = {
                "civilite": prop.get("civilite", ""),
                "nom": prop.get("nom", ""),
                "prenoms": prop.get("prenoms", ""),
                "profession": prop.get("profession", ""),
                "adresse": prop.get("adresse", ""),
                "code_postal": prop.get("code_postal", ""),
                "ville": prop.get("ville", ""),
                "lieu_naissance": prop.get("lieu_naissance", ""),
                "date_naissance": prop.get("date_naissance", ""),
                "nationalite": prop.get("nationalite", "française"),
                "resident_fiscal": True,
                "situation_matrimoniale": prop.get("situation_matrimoniale", {})
            }
            promettants.append(promettant)
        return promettants

    def _convertir_proprietaires_vers_vendeurs(self, proprietaires: List[Dict]) -> List[Dict]:
        """Convertit les propriétaires actuels en vendeurs."""
        # Même structure que promettants
        return self._convertir_proprietaires_vers_promettants(proprietaires)

    def _convertir_bien(self, bien_titre: Dict) -> Dict:
        """Convertit les données du bien."""
        return {
            "adresse": bien_titre.get("adresse", {}),
            "cadastre": bien_titre.get("cadastre", []),
            "lots": bien_titre.get("lots", []),
            "superficie_carrez": {
                "superficie_m2": str(bien_titre.get("superficie_carrez", "")),
                "date_mesurage": "",
                "diagnostiqueur": ""
            },
            "usage_actuel": "d'habitation",
            "usage_futur": "residence_principale"
        }

    def _convertir_origine(self, donnees_titre: Dict, titre_reference: str) -> List[Dict]:
        """Convertit l'origine de propriété."""
        # L'acquisition actuelle devient l'origine immédiate
        return [{
            "lots_concernes": [lot.get("numero") for lot in donnees_titre.get("bien", {}).get("lots", [])],
            "origine_immediate": {
                "type": "acquisition",
                "vendeur_precedent": ", ".join([
                    v.get("nom", "") for v in donnees_titre.get("vendeurs_originaux", [])
                ]),
                "notaire": f"{donnees_titre.get('notaire', {}).get('civilite', 'Maître')} {donnees_titre.get('notaire', {}).get('nom', '')}, notaire à {donnees_titre.get('notaire', {}).get('ville', '')}",
                "date": donnees_titre.get("date_acte", ""),
                "publication": donnees_titre.get("publication", {})
            }
        }]


# =============================================================================
# SCHEMA SQL POUR SUPABASE
# =============================================================================

SCHEMA_SQL_TITRES = """
-- ==========================================================================
-- SCHEMA SQL POUR WORKFLOW NOTARIAL COMPLET
-- Tables: titres_propriete, dossiers_notariaux, actes
-- ==========================================================================

-- Table des titres de propriété
CREATE TABLE IF NOT EXISTS titres_propriete (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference TEXT UNIQUE NOT NULL,
    date_creation TIMESTAMPTZ DEFAULT NOW(),
    date_modification TIMESTAMPTZ DEFAULT NOW(),
    statut TEXT DEFAULT 'actif' CHECK (statut IN ('actif', 'archive', 'obsolete')),
    donnees JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    fichier_source TEXT
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_titres_reference ON titres_propriete(reference);
CREATE INDEX IF NOT EXISTS idx_titres_statut ON titres_propriete(statut);
CREATE INDEX IF NOT EXISTS idx_titres_date ON titres_propriete(date_creation DESC);

-- Index GIN pour recherche full-text dans JSONB
CREATE INDEX IF NOT EXISTS idx_titres_donnees ON titres_propriete USING GIN (donnees);

-- Table des dossiers notariaux (liaison titre → promesse → vente)
CREATE TABLE IF NOT EXISTS dossiers_notariaux (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference TEXT UNIQUE NOT NULL,
    statut TEXT DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'promesse_signee', 'vente_signee', 'annule', 'archive')),
    titre_id UUID REFERENCES titres_propriete(id),
    promesse_id UUID REFERENCES actes(id),
    vente_id UUID REFERENCES actes(id),
    date_creation TIMESTAMPTZ DEFAULT NOW(),
    date_modification TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Index dossiers
CREATE INDEX IF NOT EXISTS idx_dossiers_reference ON dossiers_notariaux(reference);
CREATE INDEX IF NOT EXISTS idx_dossiers_statut ON dossiers_notariaux(statut);
CREATE INDEX IF NOT EXISTS idx_dossiers_titre ON dossiers_notariaux(titre_id);

-- Fonction de recherche dans les titres
CREATE OR REPLACE FUNCTION search_titres(search_term TEXT)
RETURNS SETOF titres_propriete AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM titres_propriete
    WHERE
        reference ILIKE '%' || search_term || '%'
        OR donnees::TEXT ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;

-- Fonction pour trouver un titre par adresse
CREATE OR REPLACE FUNCTION find_titre_by_address(ville TEXT, voie TEXT DEFAULT NULL)
RETURNS SETOF titres_propriete AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM titres_propriete
    WHERE
        donnees->'bien'->'adresse'->>'ville' ILIKE '%' || ville || '%'
        AND (voie IS NULL OR donnees->'bien'->'adresse'->>'voie' ILIKE '%' || voie || '%');
END;
$$ LANGUAGE plpgsql;

-- Fonction pour trouver un titre par propriétaire
CREATE OR REPLACE FUNCTION find_titre_by_owner(nom TEXT)
RETURNS SETOF titres_propriete AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM titres_propriete
    WHERE
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(donnees->'proprietaires_actuels') AS prop
            WHERE prop->>'nom' ILIKE '%' || nom || '%'
        );
END;
$$ LANGUAGE plpgsql;

-- Vue pour statistiques
CREATE OR REPLACE VIEW stats_titres AS
SELECT
    COUNT(*) AS total_titres,
    COUNT(*) FILTER (WHERE statut = 'actif') AS titres_actifs,
    COUNT(*) FILTER (WHERE statut = 'archive') AS titres_archives,
    AVG((metadata->>'confiance')::NUMERIC) AS confiance_moyenne,
    MIN(date_creation) AS premier_titre,
    MAX(date_creation) AS dernier_titre
FROM titres_propriete;

-- Trigger pour mise à jour automatique de date_modification
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_titres_modtime
    BEFORE UPDATE ON titres_propriete
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_dossiers_modtime
    BEFORE UPDATE ON dossiers_notariaux
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
"""


# =============================================================================
# CLI
# =============================================================================

def afficher_titres(titres: List[TitrePropriete]) -> None:
    """Affiche une liste de titres sous forme de tableau."""
    if not titres:
        console.print("[dim]Aucun titre trouvé.[/dim]")
        return

    table = Table(title="Titres de propriété", show_header=True)
    table.add_column("Référence", style="cyan")
    table.add_column("Propriétaires", style="green")
    table.add_column("Adresse")
    table.add_column("Statut")
    table.add_column("Confiance")
    table.add_column("Date")

    for titre in titres:
        confiance = titre.donnees.get("metadata", {}).get("confiance", 0)
        confiance_style = "green" if confiance >= 0.7 else "yellow" if confiance >= 0.5 else "red"

        table.add_row(
            titre.reference,
            titre.proprietaires_noms[:30],
            titre.adresse_complete[:40],
            titre.statut,
            f"[{confiance_style}]{confiance * 100:.0f}%[/{confiance_style}]",
            titre.date_creation[:10] if titre.date_creation else "-"
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Gestionnaire des titres de propriété",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions disponibles:
  upload    - Upload et extrait un titre de propriété
  list      - Liste tous les titres
  get       - Récupère un titre par référence
  search    - Recherche dans les titres
  convert   - Convertit un titre vers promesse ou vente
  schema    - Affiche le schéma SQL pour Supabase

Exemples:
  python gestionnaire_titres_propriete.py upload -f titre.pdf
  python gestionnaire_titres_propriete.py list
  python gestionnaire_titres_propriete.py search -q "Tassin"
  python gestionnaire_titres_propriete.py convert -t TITRE-001 --type promesse -o promesse.json
        """
    )

    parser.add_argument(
        "action",
        choices=["upload", "list", "get", "search", "convert", "schema"],
        help="Action à effectuer"
    )

    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Fichier d'entrée (pour upload)"
    )

    parser.add_argument(
        "--titre", "-t",
        type=str,
        help="Référence du titre"
    )

    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Terme de recherche"
    )

    parser.add_argument(
        "--type",
        choices=["promesse", "vente"],
        help="Type de conversion"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier de sortie"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mode verbeux"
    )

    args = parser.parse_args()

    # Initialise le gestionnaire
    gestionnaire = GestionnaireTitres()

    if gestionnaire._offline_mode:
        console.print(Panel(
            "[yellow]Mode hors-ligne activé[/yellow]\n\n"
            "Les données sont stockées localement dans .tmp/titres_propriete/\n"
            "Configurez SUPABASE_URL et SUPABASE_KEY dans .env pour la synchronisation cloud.",
            border_style="yellow"
        ))

    # Exécute l'action
    if args.action == "upload":
        if not args.file:
            console.print("[red]--file requis pour upload[/red]")
            sys.exit(1)

        filepath = Path(args.file)
        titre = gestionnaire.upload_titre(filepath, verbose=args.verbose)
        if titre:
            console.print(f"\n[green]✓ Titre créé avec succès![/green]")
            console.print(f"  Référence: {titre.reference}")
            console.print(f"  Propriétaires: {titre.proprietaires_noms}")
            console.print(f"  Adresse: {titre.adresse_complete}")

    elif args.action == "list":
        titres = gestionnaire.lister_titres()
        afficher_titres(titres)

    elif args.action == "get":
        if not args.titre:
            console.print("[red]--titre requis pour get[/red]")
            sys.exit(1)

        titre = gestionnaire.charger_titre(args.titre)
        if titre:
            console.print(Panel(
                f"[bold]Référence:[/bold] {titre.reference}\n"
                f"[bold]Propriétaires:[/bold] {titre.proprietaires_noms}\n"
                f"[bold]Adresse:[/bold] {titre.adresse_complete}\n"
                f"[bold]Statut:[/bold] {titre.statut}\n"
                f"[bold]Date création:[/bold] {titre.date_creation}",
                title=f"Titre {titre.reference}"
            ))
            if args.verbose:
                console.print("\n[dim]Données complètes:[/dim]")
                console.print(json.dumps(titre.donnees, ensure_ascii=False, indent=2)[:2000])
        else:
            console.print(f"[yellow]Titre non trouvé: {args.titre}[/yellow]")

    elif args.action == "search":
        if not args.query:
            console.print("[red]--query requis pour search[/red]")
            sys.exit(1)

        titres = gestionnaire.rechercher_titres(args.query)
        console.print(f"\n[dim]Résultats pour '{args.query}':[/dim]\n")
        afficher_titres(titres)

    elif args.action == "convert":
        if not args.titre or not args.type:
            console.print("[red]--titre et --type requis pour convert[/red]")
            sys.exit(1)

        try:
            if args.type == "promesse":
                donnees = gestionnaire.convertir_vers_promesse(args.titre)
            else:
                donnees = gestionnaire.convertir_vers_vente(args.titre)

            if args.output:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(donnees, f, ensure_ascii=False, indent=2)
                console.print(f"[green]✓ Données exportées vers {output_path}[/green]")
            else:
                console.print(json.dumps(donnees, ensure_ascii=False, indent=2))

        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            sys.exit(1)

    elif args.action == "schema":
        console.print(Panel(
            SCHEMA_SQL_TITRES,
            title="Schéma SQL pour Supabase",
            border_style="blue"
        ))


if __name__ == "__main__":
    main()
