#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
historique_supabase.py
----------------------
Module de gestion de l'historique des actes avec Supabase.

Fournit une interface CRUD pour sauvegarder, charger, lister
et rechercher les actes notariés dans une base Supabase.

Configuration requise dans .env:
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-anon-key

Usage en tant que module:
    from historique_supabase import HistoriqueActes
    historique = HistoriqueActes()
    historique.sauvegarder_acte("REF-001", "vente", donnees)

Usage en CLI:
    python historique_supabase.py --action list
    python historique_supabase.py --action get --reference REF-001
    python historique_supabase.py --action save --reference REF-001 --type vente --data donnees.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

try:
    from supabase import create_client, Client
except (ImportError, AttributeError, Exception) as e:
    # Python 3.14+ peut causer des erreurs dans httpcore/supabase
    print(f"Avertissement: supabase non disponible ({type(e).__name__}). Mode offline activé.")
    create_client = None
    Client = None

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

console = Console()

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Charge les variables d'environnement
load_dotenv(PROJECT_ROOT / ".env")


@dataclass
class Acte:
    """Représente un acte notarié dans la base de données."""
    id: Optional[str] = None
    reference: str = ""
    type_acte: str = ""
    date_creation: Optional[str] = None
    date_modification: Optional[str] = None
    statut: str = "brouillon"
    donnees: Dict = None
    metadata: Dict = None

    def __post_init__(self):
        if self.donnees is None:
            self.donnees = {}
        if self.metadata is None:
            self.metadata = {}


class HistoriqueActes:
    """
    Gestionnaire d'historique des actes avec Supabase.

    Permet de sauvegarder, charger, lister et rechercher les actes
    dans une base de données Supabase.
    """

    def __init__(self, url: str = None, key: str = None):
        """
        Initialise la connexion à Supabase.

        Args:
            url: URL Supabase (ou variable d'environnement SUPABASE_URL)
            key: Clé API Supabase (ou variable d'environnement SUPABASE_KEY)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        self.client: Optional[Client] = None

        if not self.url or not self.key:
            console.print("[yellow]Configuration Supabase manquante. Mode hors-ligne activé.[/yellow]")
            self._offline_mode = True
            self._offline_storage = {}
        else:
            self._offline_mode = False
            self._init_client()

    def _init_client(self) -> None:
        """Initialise le client Supabase."""
        if create_client is None:
            console.print("[yellow]Module supabase non disponible. Mode hors-ligne activé.[/yellow]")
            self._offline_mode = True
            self._offline_storage = {}
            return

        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            console.print(f"[red]Erreur connexion Supabase: {e}[/red]")
            self._offline_mode = True
            self._offline_storage = {}

    def sauvegarder_acte(
        self,
        reference: str,
        type_acte: str,
        donnees: Dict,
        metadata: Dict = None,
        statut: str = "brouillon"
    ) -> Optional[str]:
        """
        Sauvegarde ou met à jour un acte.

        Args:
            reference: Référence unique de l'acte
            type_acte: Type d'acte (vente, promesse, reglement, modificatif)
            donnees: Données de l'acte (JSON)
            metadata: Métadonnées additionnelles
            statut: Statut de l'acte (brouillon, en_cours, termine)

        Returns:
            ID de l'acte créé/mis à jour ou None si erreur
        """
        if metadata is None:
            metadata = {}

        metadata["derniere_sauvegarde"] = datetime.now().isoformat()

        if self._offline_mode:
            return self._sauvegarder_offline(reference, type_acte, donnees, metadata, statut)

        try:
            # Vérifie si l'acte existe déjà
            existing = self.client.table("actes").select("id").eq("reference", reference).execute()

            data = {
                "reference": reference,
                "type_acte": type_acte,
                "donnees": donnees,
                "metadata": metadata,
                "statut": statut,
                "date_modification": datetime.now().isoformat()
            }

            if existing.data:
                # Mise à jour
                acte_id = existing.data[0]["id"]
                result = self.client.table("actes").update(data).eq("id", acte_id).execute()

                # Enregistre dans l'historique
                self._enregistrer_modification(acte_id, "update", donnees)

            else:
                # Création
                data["date_creation"] = datetime.now().isoformat()
                result = self.client.table("actes").insert(data).execute()
                acte_id = result.data[0]["id"] if result.data else None

                # Enregistre dans l'historique
                if acte_id:
                    self._enregistrer_modification(acte_id, "create", donnees)

            return acte_id

        except Exception as e:
            console.print(f"[red]Erreur sauvegarde: {e}[/red]")
            return None

    def _sauvegarder_offline(
        self,
        reference: str,
        type_acte: str,
        donnees: Dict,
        metadata: Dict,
        statut: str
    ) -> str:
        """Sauvegarde en mode hors-ligne (mémoire)."""
        acte_id = f"offline_{reference}"
        self._offline_storage[reference] = {
            "id": acte_id,
            "reference": reference,
            "type_acte": type_acte,
            "donnees": donnees,
            "metadata": metadata,
            "statut": statut,
            "date_creation": datetime.now().isoformat(),
            "date_modification": datetime.now().isoformat()
        }
        return acte_id

    def charger_acte(self, reference: str) -> Optional[Acte]:
        """
        Charge un acte par sa référence.

        Args:
            reference: Référence de l'acte

        Returns:
            Objet Acte ou None si non trouvé
        """
        if self._offline_mode:
            data = self._offline_storage.get(reference)
            if data:
                return Acte(**data)
            return None

        try:
            result = self.client.table("actes").select("*").eq("reference", reference).execute()

            if result.data:
                row = result.data[0]
                return Acte(
                    id=row.get("id"),
                    reference=row.get("reference"),
                    type_acte=row.get("type_acte"),
                    date_creation=row.get("date_creation"),
                    date_modification=row.get("date_modification"),
                    statut=row.get("statut"),
                    donnees=row.get("donnees", {}),
                    metadata=row.get("metadata", {})
                )
            return None

        except Exception as e:
            console.print(f"[red]Erreur chargement: {e}[/red]")
            return None

    def lister_actes(
        self,
        type_acte: str = None,
        statut: str = None,
        limite: int = 50,
        offset: int = 0
    ) -> List[Acte]:
        """
        Liste les actes avec filtres optionnels.

        Args:
            type_acte: Filtre par type d'acte
            statut: Filtre par statut
            limite: Nombre maximum de résultats
            offset: Décalage pour pagination

        Returns:
            Liste d'objets Acte
        """
        if self._offline_mode:
            actes = list(self._offline_storage.values())
            if type_acte:
                actes = [a for a in actes if a["type_acte"] == type_acte]
            if statut:
                actes = [a for a in actes if a["statut"] == statut]
            return [Acte(**a) for a in actes[offset:offset + limite]]

        try:
            query = self.client.table("actes").select("*")

            if type_acte:
                query = query.eq("type_acte", type_acte)
            if statut:
                query = query.eq("statut", statut)

            query = query.order("date_creation", desc=True).limit(limite).offset(offset)
            result = query.execute()

            return [
                Acte(
                    id=row.get("id"),
                    reference=row.get("reference"),
                    type_acte=row.get("type_acte"),
                    date_creation=row.get("date_creation"),
                    date_modification=row.get("date_modification"),
                    statut=row.get("statut"),
                    donnees=row.get("donnees", {}),
                    metadata=row.get("metadata", {})
                )
                for row in result.data
            ]

        except Exception as e:
            console.print(f"[red]Erreur listage: {e}[/red]")
            return []

    def rechercher(self, query: str, champs: List[str] = None) -> List[Acte]:
        """
        Recherche dans les actes.

        Args:
            query: Terme de recherche
            champs: Champs à rechercher (défaut: reference, donnees)

        Returns:
            Liste d'actes correspondants
        """
        if champs is None:
            champs = ["reference"]

        if self._offline_mode:
            resultats = []
            query_lower = query.lower()
            for ref, acte in self._offline_storage.items():
                if query_lower in ref.lower():
                    resultats.append(Acte(**acte))
                elif query_lower in json.dumps(acte.get("donnees", {})).lower():
                    resultats.append(Acte(**acte))
            return resultats

        try:
            # Recherche basique par référence
            result = self.client.table("actes").select("*").ilike("reference", f"%{query}%").execute()

            return [
                Acte(
                    id=row.get("id"),
                    reference=row.get("reference"),
                    type_acte=row.get("type_acte"),
                    date_creation=row.get("date_creation"),
                    date_modification=row.get("date_modification"),
                    statut=row.get("statut"),
                    donnees=row.get("donnees", {}),
                    metadata=row.get("metadata", {})
                )
                for row in result.data
            ]

        except Exception as e:
            console.print(f"[red]Erreur recherche: {e}[/red]")
            return []

    def supprimer_acte(self, reference: str) -> bool:
        """
        Supprime un acte par sa référence.

        Args:
            reference: Référence de l'acte à supprimer

        Returns:
            True si supprimé, False sinon
        """
        if self._offline_mode:
            if reference in self._offline_storage:
                del self._offline_storage[reference]
                return True
            return False

        try:
            # Récupère l'ID
            existing = self.client.table("actes").select("id").eq("reference", reference).execute()

            if existing.data:
                acte_id = existing.data[0]["id"]

                # Supprime l'historique d'abord
                self.client.table("historique_modifications").delete().eq("acte_id", acte_id).execute()

                # Supprime l'acte
                self.client.table("actes").delete().eq("id", acte_id).execute()
                return True

            return False

        except Exception as e:
            console.print(f"[red]Erreur suppression: {e}[/red]")
            return False

    def changer_statut(self, reference: str, nouveau_statut: str) -> bool:
        """
        Change le statut d'un acte.

        Args:
            reference: Référence de l'acte
            nouveau_statut: Nouveau statut

        Returns:
            True si mis à jour, False sinon
        """
        if self._offline_mode:
            if reference in self._offline_storage:
                self._offline_storage[reference]["statut"] = nouveau_statut
                self._offline_storage[reference]["date_modification"] = datetime.now().isoformat()
                return True
            return False

        try:
            result = self.client.table("actes").update({
                "statut": nouveau_statut,
                "date_modification": datetime.now().isoformat()
            }).eq("reference", reference).execute()

            return bool(result.data)

        except Exception as e:
            console.print(f"[red]Erreur changement statut: {e}[/red]")
            return False

    def obtenir_historique(self, reference: str) -> List[Dict]:
        """
        Récupère l'historique des modifications d'un acte.

        Args:
            reference: Référence de l'acte

        Returns:
            Liste des modifications
        """
        if self._offline_mode:
            return []

        try:
            # Récupère l'ID de l'acte
            acte = self.client.table("actes").select("id").eq("reference", reference).execute()

            if not acte.data:
                return []

            acte_id = acte.data[0]["id"]

            result = self.client.table("historique_modifications").select("*").eq(
                "acte_id", acte_id
            ).order("date_modification", desc=True).execute()

            return result.data

        except Exception as e:
            console.print(f"[red]Erreur historique: {e}[/red]")
            return []

    def _enregistrer_modification(self, acte_id: str, action: str, donnees: Dict) -> None:
        """Enregistre une modification dans l'historique."""
        if self._offline_mode:
            return

        try:
            self.client.table("historique_modifications").insert({
                "acte_id": acte_id,
                "action": action,
                "donnees_apres": donnees,
                "date_modification": datetime.now().isoformat()
            }).execute()
        except Exception:
            pass  # Erreur non bloquante

    def exporter_json(self, reference: str, output_path: Path) -> bool:
        """
        Exporte un acte vers un fichier JSON.

        Args:
            reference: Référence de l'acte
            output_path: Chemin du fichier de sortie

        Returns:
            True si exporté, False sinon
        """
        acte = self.charger_acte(reference)
        if not acte:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(acte.donnees, f, ensure_ascii=False, indent=2)

        return True

    def importer_json(
        self,
        reference: str,
        type_acte: str,
        input_path: Path,
        metadata: Dict = None
    ) -> Optional[str]:
        """
        Importe un acte depuis un fichier JSON.

        Args:
            reference: Référence à attribuer
            type_acte: Type d'acte
            input_path: Chemin du fichier JSON
            metadata: Métadonnées additionnelles

        Returns:
            ID de l'acte importé ou None
        """
        if not input_path.exists():
            console.print(f"[red]Fichier non trouvé: {input_path}[/red]")
            return None

        with open(input_path, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        if metadata is None:
            metadata = {}
        metadata["source_import"] = str(input_path)

        return self.sauvegarder_acte(reference, type_acte, donnees, metadata)


def afficher_actes(actes: List[Acte]) -> None:
    """Affiche une liste d'actes sous forme de tableau."""
    if not actes:
        console.print("[dim]Aucun acte trouvé.[/dim]")
        return

    table = Table(title="Actes", show_header=True)
    table.add_column("Référence", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Statut")
    table.add_column("Date création")
    table.add_column("Dernière modif.")

    for acte in actes:
        statut_style = {
            "brouillon": "yellow",
            "en_cours": "blue",
            "termine": "green"
        }.get(acte.statut, "white")

        table.add_row(
            acte.reference,
            acte.type_acte,
            f"[{statut_style}]{acte.statut}[/{statut_style}]",
            acte.date_creation[:10] if acte.date_creation else "-",
            acte.date_modification[:10] if acte.date_modification else "-"
        )

    console.print(table)


def main():
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description="Gestion de l'historique des actes avec Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions disponibles:
  list      - Liste les actes
  get       - Récupère un acte par référence
  save      - Sauvegarde un acte depuis un fichier JSON
  delete    - Supprime un acte
  search    - Recherche dans les actes
  export    - Exporte un acte vers JSON
  history   - Affiche l'historique des modifications

Exemples:
  python historique_supabase.py --action list
  python historique_supabase.py --action list --type vente
  python historique_supabase.py --action get --reference VTE-2024-001
  python historique_supabase.py --action save --reference VTE-2024-002 --type vente --data donnees.json
  python historique_supabase.py --action search --query "Dupont"
        """
    )

    parser.add_argument(
        "--action", "-a",
        required=True,
        choices=["list", "get", "save", "delete", "search", "export", "history"],
        help="Action à effectuer"
    )

    parser.add_argument(
        "--reference", "-r",
        type=str,
        help="Référence de l'acte"
    )

    parser.add_argument(
        "--type", "-t",
        type=str,
        help="Type d'acte (pour list et save)"
    )

    parser.add_argument(
        "--statut", "-s",
        type=str,
        help="Statut de l'acte (pour list)"
    )

    parser.add_argument(
        "--data", "-d",
        type=str,
        help="Fichier JSON de données (pour save)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Fichier de sortie (pour export)"
    )

    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Terme de recherche (pour search)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie en format JSON"
    )

    args = parser.parse_args()

    # Initialise l'historique
    historique = HistoriqueActes()

    if historique._offline_mode:
        console.print(Panel(
            "[yellow]Mode hors-ligne activé[/yellow]\n\n"
            "Les données seront stockées en mémoire uniquement.\n"
            "Configurez SUPABASE_URL et SUPABASE_KEY dans .env pour la persistance.",
            border_style="yellow"
        ))

    # Exécute l'action
    if args.action == "list":
        actes = historique.lister_actes(type_acte=args.type, statut=args.statut)
        if args.json:
            print(json.dumps([asdict(a) for a in actes], ensure_ascii=False, indent=2))
        else:
            afficher_actes(actes)

    elif args.action == "get":
        if not args.reference:
            console.print("[red]--reference requis pour l'action get[/red]")
            sys.exit(1)

        acte = historique.charger_acte(args.reference)
        if acte:
            if args.json:
                print(json.dumps(asdict(acte), ensure_ascii=False, indent=2))
            else:
                console.print(Panel(
                    f"[bold]Référence:[/bold] {acte.reference}\n"
                    f"[bold]Type:[/bold] {acte.type_acte}\n"
                    f"[bold]Statut:[/bold] {acte.statut}\n"
                    f"[bold]Créé le:[/bold] {acte.date_creation}\n"
                    f"[bold]Modifié le:[/bold] {acte.date_modification}",
                    title=f"Acte {acte.reference}"
                ))
                console.print("\n[dim]Données:[/dim]")
                console.print(json.dumps(acte.donnees, ensure_ascii=False, indent=2)[:1000])
        else:
            console.print(f"[yellow]Acte non trouvé: {args.reference}[/yellow]")

    elif args.action == "save":
        if not args.reference or not args.type or not args.data:
            console.print("[red]--reference, --type et --data requis pour l'action save[/red]")
            sys.exit(1)

        data_path = Path(args.data)
        if not data_path.exists():
            console.print(f"[red]Fichier non trouvé: {data_path}[/red]")
            sys.exit(1)

        with open(data_path, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        acte_id = historique.sauvegarder_acte(args.reference, args.type, donnees)
        if acte_id:
            console.print(f"[green]✓ Acte sauvegardé: {args.reference} (ID: {acte_id})[/green]")
        else:
            console.print("[red]Erreur lors de la sauvegarde[/red]")

    elif args.action == "delete":
        if not args.reference:
            console.print("[red]--reference requis pour l'action delete[/red]")
            sys.exit(1)

        if historique.supprimer_acte(args.reference):
            console.print(f"[green]✓ Acte supprimé: {args.reference}[/green]")
        else:
            console.print(f"[yellow]Acte non trouvé: {args.reference}[/yellow]")

    elif args.action == "search":
        if not args.query:
            console.print("[red]--query requis pour l'action search[/red]")
            sys.exit(1)

        actes = historique.rechercher(args.query)
        if args.json:
            print(json.dumps([asdict(a) for a in actes], ensure_ascii=False, indent=2))
        else:
            console.print(f"\n[dim]Résultats pour '{args.query}':[/dim]\n")
            afficher_actes(actes)

    elif args.action == "export":
        if not args.reference or not args.output:
            console.print("[red]--reference et --output requis pour l'action export[/red]")
            sys.exit(1)

        if historique.exporter_json(args.reference, Path(args.output)):
            console.print(f"[green]✓ Acte exporté: {args.output}[/green]")
        else:
            console.print(f"[red]Erreur lors de l'export[/red]")

    elif args.action == "history":
        if not args.reference:
            console.print("[red]--reference requis pour l'action history[/red]")
            sys.exit(1)

        historique_modifs = historique.obtenir_historique(args.reference)
        if historique_modifs:
            table = Table(title=f"Historique de {args.reference}")
            table.add_column("Date")
            table.add_column("Action")

            for modif in historique_modifs:
                table.add_row(
                    modif.get("date_modification", "-")[:19],
                    modif.get("action", "-")
                )

            console.print(table)
        else:
            console.print("[dim]Aucun historique disponible[/dim]")


# Schéma SQL pour Supabase
SCHEMA_SQL = """
-- Exécuter ce SQL dans l'éditeur SQL de Supabase

-- Table principale des actes
CREATE TABLE IF NOT EXISTS actes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference TEXT UNIQUE NOT NULL,
    type_acte TEXT NOT NULL,
    date_creation TIMESTAMPTZ DEFAULT NOW(),
    date_modification TIMESTAMPTZ DEFAULT NOW(),
    statut TEXT DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'en_cours', 'termine', 'archive')),
    donnees JSONB NOT NULL DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_actes_reference ON actes(reference);
CREATE INDEX IF NOT EXISTS idx_actes_type ON actes(type_acte);
CREATE INDEX IF NOT EXISTS idx_actes_statut ON actes(statut);
CREATE INDEX IF NOT EXISTS idx_actes_date_creation ON actes(date_creation DESC);

-- Table d'historique des modifications
CREATE TABLE IF NOT EXISTS historique_modifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    acte_id UUID REFERENCES actes(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    donnees_avant JSONB,
    donnees_apres JSONB,
    date_modification TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour l'historique
CREATE INDEX IF NOT EXISTS idx_historique_acte ON historique_modifications(acte_id);
CREATE INDEX IF NOT EXISTS idx_historique_date ON historique_modifications(date_modification DESC);

-- Fonction de recherche full-text dans les données JSON
CREATE OR REPLACE FUNCTION search_actes(search_term TEXT)
RETURNS SETOF actes AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM actes
    WHERE
        reference ILIKE '%' || search_term || '%'
        OR donnees::TEXT ILIKE '%' || search_term || '%';
END;
$$ LANGUAGE plpgsql;

-- Activer Row Level Security (optionnel)
-- ALTER TABLE actes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE historique_modifications ENABLE ROW LEVEL SECURITY;
"""


if __name__ == "__main__":
    main()
