#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assembler_acte.py
=================

Script d'assemblage d'actes notariaux à partir de templates Jinja2 et données JSON.

Fonctionnalités:
- Charge un template et des données
- Substitue les variables
- Gère les sections conditionnelles
- Génère automatiquement certaines valeurs (montants en lettres, dates)
- Sauvegarde l'acte généré avec métadonnées

Usage:
    python assembler_acte.py --template <template> --donnees <donnees.json> --output <sortie.md>
    python assembler_acte.py --template <template> --donnees <donnees.json> --output <sortie.md> --zones-grisees

Options:
    --zones-grisees : Marquer les variables pour affichage avec fond gris dans le DOCX final

Exemple:
    python assembler_acte.py --template ../templates/vente_lots_copropriete.md \\
                             --donnees ../exemples/donnees_vente.json \\
                             --output ../.tmp/actes_generes/acte_001.md
"""

import json
import argparse
import uuid
import os
from pathlib import Path
from datetime import datetime
from copy import deepcopy
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, UndefinedError


# ==============================================================================
# MARQUEURS ZONES GRISEES
# ==============================================================================

# Ces marqueurs sont reconnus par exporter_docx.py pour appliquer un fond gris
MARQUEUR_VAR_START = "<<<VAR_START>>>"
MARQUEUR_VAR_END = "<<<VAR_END>>>"


# ==============================================================================
# FILTRES PERSONNALISÉS JINJA2
# ==============================================================================

UNITES = ['', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf',
          'dix', 'onze', 'douze', 'treize', 'quatorze', 'quinze', 'seize',
          'dix-sept', 'dix-huit', 'dix-neuf']
DIZAINES = ['', '', 'vingt', 'trente', 'quarante', 'cinquante',
            'soixante', 'soixante', 'quatre-vingt', 'quatre-vingt']


def nombre_en_lettres(n: int) -> str:
    """
    Convertit un nombre entier en lettres (français).

    Args:
        n: Nombre entier

    Returns:
        Nombre en toutes lettres
    """
    if n < 0:
        return 'moins ' + nombre_en_lettres(-n)
    if n == 0:
        return 'zéro'
    if n < 20:
        return UNITES[n]
    if n < 100:
        dizaine = n // 10
        unite = n % 10
        if dizaine == 7 or dizaine == 9:
            # 70-79 et 90-99
            return DIZAINES[dizaine] + ('-' if unite != 1 else ' et ') + UNITES[10 + unite]
        elif dizaine == 8 and unite == 0:
            return 'quatre-vingts'
        elif unite == 1 and dizaine != 8:
            return DIZAINES[dizaine] + ' et un'
        elif unite == 0:
            return DIZAINES[dizaine]
        else:
            return DIZAINES[dizaine] + '-' + UNITES[unite]
    if n < 1000:
        centaine = n // 100
        reste = n % 100
        if centaine == 1:
            prefix = 'cent'
        else:
            prefix = UNITES[centaine] + ' cent'
            if reste == 0:
                prefix += 's'
        if reste == 0:
            return prefix
        return prefix + ' ' + nombre_en_lettres(reste)
    if n < 1000000:
        millier = n // 1000
        reste = n % 1000
        if millier == 1:
            prefix = 'mille'
        else:
            prefix = nombre_en_lettres(millier) + ' mille'
        if reste == 0:
            return prefix
        return prefix + ' ' + nombre_en_lettres(reste)
    if n < 1000000000:
        million = n // 1000000
        reste = n % 1000000
        if million == 1:
            prefix = 'un million'
        else:
            prefix = nombre_en_lettres(million) + ' millions'
        if reste == 0:
            return prefix
        return prefix + ' ' + nombre_en_lettres(reste)

    return str(n)  # Fallback pour les très grands nombres


def montant_en_lettres(montant: float, devise: str = 'EUR') -> str:
    """
    Convertit un montant en lettres avec devise.

    Args:
        montant: Montant numérique
        devise: Code devise (EUR par défaut)

    Returns:
        Montant en toutes lettres
    """
    partie_entiere = int(montant)
    partie_decimale = round((montant - partie_entiere) * 100)

    devise_libelle = {
        'EUR': ('euro', 'euros', 'centime', 'centimes'),
    }.get(devise, (devise, devise, 'centime', 'centimes'))

    texte = nombre_en_lettres(partie_entiere)
    if partie_entiere <= 1:
        texte += ' ' + devise_libelle[0]
    else:
        texte += ' ' + devise_libelle[1]

    if partie_decimale > 0:
        texte += ' et ' + nombre_en_lettres(partie_decimale)
        if partie_decimale <= 1:
            texte += ' ' + devise_libelle[2]
        else:
            texte += ' ' + devise_libelle[3]

    return texte


def format_nombre(n: float) -> str:
    """
    Formate un nombre avec séparateurs de milliers.

    Args:
        n: Nombre

    Returns:
        Nombre formaté (ex: 245 000,00)
    """
    if n is None:
        return ''
    if isinstance(n, int):
        return f"{n:,}".replace(',', ' ')
    return f"{n:,.2f}".replace(',', ' ').replace('.', ',')


def date_en_lettres(date_str: str) -> str:
    """
    Convertit une date en toutes lettres.

    Args:
        date_str: Date au format YYYY-MM-DD ou DD/MM/YYYY

    Returns:
        Date en toutes lettres
    """
    mois_noms = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

    try:
        if '-' in date_str:
            annee, mois, jour = date_str.split('-')
        else:
            jour, mois, annee = date_str.split('/')

        jour = int(jour)
        mois = int(mois)
        annee = int(annee)

        jour_lettres = nombre_en_lettres(jour) if jour != 1 else 'premier'

        return f"le {jour_lettres} {mois_noms[mois]} {nombre_en_lettres(annee)}"
    except (ValueError, IndexError):
        return date_str


def annee_en_lettres(annee: int) -> str:
    """
    Convertit une année en lettres majuscules.

    Args:
        annee: Année (ex: 2025)

    Returns:
        Année en lettres majuscules (ex: DEUX MILLE VINGT-CINQ)
    """
    return nombre_en_lettres(annee).upper()


def numero_lot_en_lettres(numero: int) -> str:
    """
    Convertit un numéro de lot en lettres.

    Args:
        numero: Numéro

    Returns:
        Numéro en lettres (ex: quatorze)
    """
    return nombre_en_lettres(numero)


def mois_en_lettres(mois: int) -> str:
    """
    Convertit un numéro de mois en nom de mois.

    Args:
        mois: Numéro du mois (1-12)

    Returns:
        Nom du mois (ex: janvier)
    """
    mois_noms = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
    if 1 <= mois <= 12:
        return mois_noms[mois]
    return str(mois)


def jour_en_lettres(jour: int) -> str:
    """
    Convertit un numéro de jour en lettres.

    Args:
        jour: Numéro du jour (1-31)

    Returns:
        Jour en lettres (ex: quinze, premier pour 1)
    """
    if jour == 1:
        return 'premier'
    return nombre_en_lettres(jour)


def format_date(date_str: str, format: str = "long") -> str:
    """
    Formate une date au format francais lisible.

    Args:
        date_str: Date au format YYYY-MM-DD ou DD/MM/YYYY
        format: "long" (15 mars 1965), "court" (15/03/1965), "lettres" (le quinze mars...)

    Returns:
        Date formatee
    """
    mois_noms = ['', 'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
                 'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']

    if not date_str:
        return ''

    try:
        if '-' in str(date_str):
            annee, mois, jour = str(date_str).split('-')
        else:
            jour, mois, annee = str(date_str).split('/')

        jour = int(jour)
        mois = int(mois)
        annee = int(annee)

        if format == "court":
            return f"{jour:02d}/{mois:02d}/{annee}"
        elif format == "lettres":
            jour_lettres = nombre_en_lettres(jour) if jour != 1 else 'premier'
            return f"le {jour_lettres} {mois_noms[mois]} {nombre_en_lettres(annee)}"
        else:  # long
            return f"{jour} {mois_noms[mois]} {annee}"
    except (ValueError, IndexError, AttributeError):
        return str(date_str)


# ==============================================================================
# CLASSE PRINCIPALE
# ==============================================================================

class AssembleurActe:
    """
    Classe principale pour l'assemblage d'actes notariaux.
    """

    def __init__(self, dossier_templates: Path, zones_grisees: bool = False):
        """
        Initialise l'assembleur.

        Args:
            dossier_templates: Chemin vers le dossier des templates
            zones_grisees: Si True, encadre les variables avec des marqueurs pour fond gris
        """
        self.dossier_templates = dossier_templates
        self.zones_grisees = zones_grisees
        self.env = self._creer_environnement_jinja()

    def _finalize_avec_marqueurs(self, valeur):
        """
        Fonction finalize pour Jinja2 qui encadre les valeurs avec les marqueurs de zone grisee.

        Args:
            valeur: Valeur rendue par Jinja2

        Returns:
            Valeur encadree avec marqueurs si zones_grisees est actif
        """
        if valeur is None:
            return ''
        str_valeur = str(valeur)
        if not str_valeur.strip():
            return str_valeur
        # Ne pas encadrer les valeurs qui sont deja des marqueurs ou du Markdown structurel
        if str_valeur.startswith('<<<') or str_valeur.startswith('#') or str_valeur.startswith('|'):
            return str_valeur
        return f"{MARQUEUR_VAR_START}{str_valeur}{MARQUEUR_VAR_END}"

    def _finalize_standard(self, valeur):
        """
        Fonction finalize standard (sans marqueurs).

        Args:
            valeur: Valeur rendue par Jinja2

        Returns:
            Valeur en string
        """
        if valeur is None:
            return ''
        return str(valeur)

    def _creer_environnement_jinja(self) -> Environment:
        """
        Crée l'environnement Jinja2 avec les filtres personnalisés.

        Returns:
            Environnement Jinja2 configuré
        """
        # Choisir la fonction finalize selon l'option zones_grisees
        finalize_func = self._finalize_avec_marqueurs if self.zones_grisees else self._finalize_standard

        env = Environment(
            loader=FileSystemLoader([
                str(self.dossier_templates),
                str(self.dossier_templates / 'sections'),
                str(self.dossier_templates.parent / 'clauses')
            ]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            finalize=finalize_func
        )

        # Ajouter les filtres personnalisés
        env.filters['nombre_en_lettres'] = nombre_en_lettres
        env.filters['montant_en_lettres'] = montant_en_lettres
        env.filters['format_nombre'] = format_nombre
        env.filters['format_date'] = format_date
        env.filters['date_en_lettres'] = date_en_lettres
        env.filters['annee_en_lettres'] = annee_en_lettres
        env.filters['numero_lot_en_lettres'] = numero_lot_en_lettres
        env.filters['mois_en_lettres'] = mois_en_lettres
        env.filters['jour_en_lettres'] = jour_en_lettres

        return env

    def enrichir_donnees(self, donnees: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit les données avec des valeurs auto-générées.

        Args:
            donnees: Données brutes

        Returns:
            Données enrichies
        """
        donnees_enrichies = deepcopy(donnees)

        # Aplatir la structure personne_physique/personne_morale pour vendeurs et acquéreurs
        for cle in ['vendeurs', 'acquereurs']:
            if cle in donnees_enrichies:
                for i, personne in enumerate(donnees_enrichies[cle]):
                    # Aplatir personne_physique
                    if 'personne_physique' in personne:
                        donnees_enrichies[cle][i] = {**personne, **personne['personne_physique']}
                        del donnees_enrichies[cle][i]['personne_physique']

                    # Aplatir personne_morale
                    elif 'personne_morale' in personne:
                        donnees_enrichies[cle][i] = {**personne, **personne['personne_morale']}
                        del donnees_enrichies[cle][i]['personne_morale']

                # Normaliser après l'aplatissement
                for i in range(len(donnees_enrichies[cle])):
                    # Normaliser 'partenaire' en 'conjoint' pour PACS (uniquement personnes physiques)
                    if 'situation_matrimoniale' in donnees_enrichies[cle][i]:
                        sitmat = donnees_enrichies[cle][i]['situation_matrimoniale']
                        if 'partenaire' in sitmat and 'conjoint' not in sitmat:
                            sitmat['conjoint'] = sitmat['partenaire']

                        # Restructurer les données PACS pour le template
                        if sitmat.get('statut') == 'pacse' and 'pacs' not in sitmat:
                            sitmat['pacs'] = {
                                'date': sitmat.get('date_pacs', ''),
                                'regime_libelle': sitmat.get('regime_pacs', 'séparation de biens'),
                                'lieu_enregistrement': sitmat.get('lieu_pacs', 'au greffe du tribunal')
                            }

        # Générer les montants en lettres
        if 'prix' in donnees_enrichies and 'montant' in donnees_enrichies['prix']:
            montant = donnees_enrichies['prix']['montant']
            donnees_enrichies['prix']['montant_lettres'] = montant_en_lettres(montant)

        # Générer les dates en lettres
        if 'acte' in donnees_enrichies and 'date' in donnees_enrichies['acte']:
            date_obj = donnees_enrichies['acte']['date']
            if isinstance(date_obj, dict):
                jour = date_obj.get('jour', 1)
                mois = date_obj.get('mois', 1)
                annee = date_obj.get('annee', 2025)

                mois_noms = ['', 'JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN',
                            'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE']

                date_obj['en_lettres'] = f"le {nombre_en_lettres(jour) if jour != 1 else 'premier'} {mois_noms[mois].lower()} {nombre_en_lettres(annee)}"
                date_obj['jour_mois_lettres'] = f"{nombre_en_lettres(jour) if jour != 1 else 'premier'} {mois_noms[mois]}"
                date_obj['annee_lettres'] = annee_en_lettres(annee)

        # Générer les numéros de lots en lettres
        if 'bien' in donnees_enrichies and 'lots' in donnees_enrichies['bien']:
            for lot in donnees_enrichies['bien']['lots']:
                if 'numero' in lot:
                    lot['numero_lettres'] = numero_lot_en_lettres(lot['numero'])
                if 'tantiemes' in lot and 'valeur' in lot['tantiemes']:
                    lot['tantiemes']['valeur_lettres'] = nombre_en_lettres(lot['tantiemes']['valeur'])

        # Générer les montants de prêts en lettres
        if 'paiement' in donnees_enrichies and 'prets' in donnees_enrichies['paiement']:
            for pret in donnees_enrichies['paiement']['prets']:
                if 'montant' in pret:
                    pret['montant_lettres'] = montant_en_lettres(pret['montant'])

            # Total emprunté
            total_emprunte = sum(p.get('montant', 0) for p in donnees_enrichies['paiement']['prets'])
            donnees_enrichies['paiement']['fonds_empruntes'] = total_emprunte
            donnees_enrichies['paiement']['fonds_empruntes_lettres'] = montant_en_lettres(total_emprunte)

        # Libellés des types de propriété
        types_libelles = {
            'pleine_propriete': 'la pleine propriété indivise',
            'nue_propriete': 'la nue-propriété',
            'usufruit': "l'usufruit"
        }

        for cle in ['quotites_vendues', 'quotites_acquises']:
            if cle in donnees_enrichies:
                for quotite in donnees_enrichies[cle]:
                    if 'type_propriete' in quotite:
                        quotite['type_propriete_libelle'] = types_libelles.get(
                            quotite['type_propriete'], quotite['type_propriete']
                        )

        # Libellés des usages
        usages_libelles = {
            'habitation': "d'habitation",
            'commercial': 'commercial',
            'mixte': 'mixte',
            'professionnel': 'professionnel'
        }

        if 'bien' in donnees_enrichies:
            if 'usage_actuel' in donnees_enrichies['bien']:
                donnees_enrichies['bien']['usage_actuel_libelle'] = usages_libelles.get(
                    donnees_enrichies['bien']['usage_actuel'],
                    donnees_enrichies['bien']['usage_actuel']
                )
            if 'usage_futur' in donnees_enrichies['bien']:
                donnees_enrichies['bien']['usage_futur_libelle'] = usages_libelles.get(
                    donnees_enrichies['bien']['usage_futur'],
                    donnees_enrichies['bien']['usage_futur']
                )

        # Libellés origine de propriété
        origines_libelles = {
            'acquisition': 'Acquisition',
            'succession': 'Succession',
            'donation': 'Donation',
            'licitation': 'Licitation',
            'partage': 'Partage',
            'adjudication': 'Adjudication'
        }

        if 'origine_propriete' in donnees_enrichies:
            for origine in donnees_enrichies['origine_propriete']:
                if 'origine_immediate' in origine and 'type' in origine['origine_immediate']:
                    origine['origine_immediate']['type_libelle'] = origines_libelles.get(
                        origine['origine_immediate']['type'],
                        origine['origine_immediate']['type']
                    )

        return donnees_enrichies

    def assembler(self, nom_template: str, donnees: Dict[str, Any],
                  sections_actives: Optional[Dict[str, bool]] = None) -> str:
        """
        Assemble un acte à partir d'un template et de données.

        Args:
            nom_template: Nom du fichier template
            donnees: Données à injecter
            sections_actives: Dictionnaire des sections à activer/désactiver

        Returns:
            Contenu de l'acte généré
        """
        # Charger le template
        try:
            template = self.env.get_template(nom_template)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template non trouvé: {nom_template}")

        # Enrichir les données
        donnees_enrichies = self.enrichir_donnees(donnees)

        # Ajouter les sections actives au contexte
        if sections_actives:
            donnees_enrichies['sections'] = sections_actives

        # Générer l'acte
        try:
            acte = template.render(**donnees_enrichies)
        except UndefinedError as e:
            # Extraire la variable manquante pour un message plus clair
            import re
            match = re.search(r"'(\w+)' is undefined|has no attribute '(\w+)'", str(e))
            if match:
                var_name = match.group(1) or match.group(2)
                suggestion = "{% if " + var_name + " %}"
                raise ValueError(f"Variable manquante dans le template: '{var_name}' - {e}\n"
                               f"Vérifier que cette variable existe dans les données ou ajouter {suggestion}")
            else:
                raise ValueError(f"Variable manquante dans le template: {e}")

        return acte

    def sauvegarder(self, acte: str, donnees: Dict[str, Any],
                    dossier_sortie: Path, id_acte: Optional[str] = None) -> Dict[str, Path]:
        """
        Sauvegarde l'acte généré avec ses métadonnées.

        Args:
            acte: Contenu de l'acte
            donnees: Données utilisées
            dossier_sortie: Dossier de destination
            id_acte: Identifiant optionnel

        Returns:
            Dictionnaire des chemins créés
        """
        if not id_acte:
            id_acte = str(uuid.uuid4())[:8]

        dossier_acte = dossier_sortie / id_acte
        dossier_acte.mkdir(parents=True, exist_ok=True)

        chemins = {}

        # Sauvegarder l'acte
        chemin_acte = dossier_acte / 'acte.md'
        with open(chemin_acte, 'w', encoding='utf-8') as f:
            f.write(acte)
        chemins['acte'] = chemin_acte

        # Sauvegarder les données
        chemin_donnees = dossier_acte / 'donnees.json'
        with open(chemin_donnees, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        chemins['donnees'] = chemin_donnees

        # Créer les métadonnées
        metadata = {
            'id': id_acte,
            'date_generation': datetime.now().isoformat(),
            'statut': 'brouillon',
            'version': 1,
            'historique': [
                {
                    'date': datetime.now().isoformat(),
                    'action': 'creation',
                    'description': 'Génération initiale'
                }
            ]
        }
        chemin_metadata = dossier_acte / 'metadata.json'
        with open(chemin_metadata, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        chemins['metadata'] = chemin_metadata

        return chemins


def main():
    parser = argparse.ArgumentParser(
        description="Assemble un acte notarial à partir d'un template et de données"
    )
    parser.add_argument(
        '--template', '-t',
        type=str,
        required=True,
        help="Nom du fichier template (ex: vente_lots_copropriete.md)"
    )
    parser.add_argument(
        '--donnees', '-d',
        type=Path,
        required=True,
        help="Chemin vers le fichier de données JSON"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help="Dossier de sortie (défaut: .tmp/actes_generes)"
    )
    parser.add_argument(
        '--id',
        type=str,
        help="Identifiant de l'acte (auto-généré si non fourni)"
    )
    parser.add_argument(
        '--dossier-templates',
        type=Path,
        default=Path(__file__).parent.parent / 'templates',
        help="Dossier des templates"
    )
    parser.add_argument(
        '--zones-grisees', '-z',
        action='store_true',
        help="Marquer les variables pour affichage avec fond gris dans le DOCX final"
    )

    args = parser.parse_args()

    # Vérifications
    if not args.donnees.exists():
        print(f"[ERREUR] Fichier de donnees non trouve: {args.donnees}")
        return 1

    # Charger les données
    with open(args.donnees, 'r', encoding='utf-8') as f:
        donnees = json.load(f)

    # Créer l'assembleur avec option zones grisees
    assembleur = AssembleurActe(args.dossier_templates, zones_grisees=args.zones_grisees)

    # Assembler l'acte
    try:
        acte = assembleur.assembler(args.template, donnees)
    except FileNotFoundError as e:
        print(f"[ERREUR] {e}")
        return 1
    except ValueError as e:
        print(f"[ERREUR] Donnees: {e}")
        return 1

    # Sauvegarder
    dossier_sortie = args.output or (Path(__file__).parent.parent / '.tmp' / 'actes_generes')
    chemins = assembleur.sauvegarder(acte, donnees, dossier_sortie, args.id)

    option_gris = " (avec marqueurs zones grisees)" if args.zones_grisees else ""
    print(f"[OK] Acte genere avec succes!{option_gris}")
    print(f"   - Acte: {chemins['acte']}")
    print(f"   - Donnees: {chemins['donnees']}")
    print(f"   - Metadonnees: {chemins['metadata']}")

    return 0


if __name__ == '__main__':
    exit(main())
