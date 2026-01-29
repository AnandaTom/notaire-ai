#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
valider_acte.py
===============

Script de validation des données d'un acte notarial avant génération.

Fonctionnalités:
- Vérifie la complétude des données requises
- Vérifie la cohérence des dates
- Vérifie la cohérence des montants
- Vérifie la validité des références
- Vérifie la logique juridique

Usage:
    python valider_acte.py --donnees <donnees.json> --schema <schema.json> [--strict]

Exemple:
    python valider_acte.py --donnees ../exemples/donnees_vente.json \\
                           --schema ../schemas/variables_vente.json
"""

import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class NiveauErreur(Enum):
    """Niveau de gravité des erreurs."""
    ERREUR = "ERREUR"      # Bloquant - empêche la génération
    AVERTISSEMENT = "AVERTISSEMENT"  # Non-bloquant - génération possible
    INFO = "INFO"          # Information


@dataclass
class ResultatValidation:
    """Résultat d'une validation."""
    niveau: NiveauErreur
    code: str
    message: str
    chemin: str = ""
    valeur: Any = None
    suggestion: str = ""


@dataclass
class RapportValidation:
    """Rapport complet de validation."""
    valide: bool = True
    erreurs: List[ResultatValidation] = field(default_factory=list)
    avertissements: List[ResultatValidation] = field(default_factory=list)
    infos: List[ResultatValidation] = field(default_factory=list)

    def ajouter(self, resultat: ResultatValidation):
        """Ajoute un résultat au rapport."""
        if resultat.niveau == NiveauErreur.ERREUR:
            self.erreurs.append(resultat)
            self.valide = False
        elif resultat.niveau == NiveauErreur.AVERTISSEMENT:
            self.avertissements.append(resultat)
        else:
            self.infos.append(resultat)


class ValidateurActe:
    """
    Validateur d'actes notariaux.
    """

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialise le validateur.

        Args:
            schema: Schéma JSON des variables
        """
        self.schema = schema
        self.rapport = RapportValidation()

    def valider(self, donnees: Dict[str, Any], strict: bool = True) -> RapportValidation:
        """
        Valide les données d'un acte.

        Args:
            donnees: Données à valider
            strict: Mode strict (erreurs bloquantes)

        Returns:
            Rapport de validation
        """
        self.rapport = RapportValidation()

        # 1. Validation de complétude
        self._valider_completude(donnees)

        # 2. Validation des dates
        self._valider_dates(donnees)

        # 3. Validation des montants
        self._valider_montants(donnees)

        # 4. Validation des références
        self._valider_references(donnees)

        # 5. Validation de la logique juridique
        self._valider_logique_juridique(donnees)

        # 6. Validation des personnes
        self._valider_personnes(donnees)

        return self.rapport

    def _get_valeur(self, donnees: Dict, chemin: str) -> Tuple[bool, Any]:
        """
        Récupère une valeur dans un dictionnaire imbriqué.

        Args:
            donnees: Dictionnaire source
            chemin: Chemin de la valeur (ex: "vendeur.nom")

        Returns:
            Tuple (trouvé, valeur)
        """
        parties = chemin.split('.')
        valeur = donnees
        for partie in parties:
            if isinstance(valeur, dict) and partie in valeur:
                valeur = valeur[partie]
            elif isinstance(valeur, list):
                try:
                    idx = int(partie)
                    valeur = valeur[idx]
                except (ValueError, IndexError):
                    return False, None
            else:
                return False, None
        return True, valeur

    def _valider_completude(self, donnees: Dict[str, Any]):
        """Vérifie que toutes les données requises sont présentes."""

        # Champs obligatoires de premier niveau
        champs_requis = {
            'acte': "Informations sur l'acte",
            'vendeurs': "Liste des vendeurs",
            'acquereurs': "Liste des acquéreurs",
            'bien': "Désignation du bien",
            'prix': "Prix de vente"
        }

        for champ, description in champs_requis.items():
            existe, valeur = self._get_valeur(donnees, champ)
            if not existe or valeur is None:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="CHAMP_REQUIS_MANQUANT",
                    message=f"Champ obligatoire manquant: {description}",
                    chemin=champ,
                    suggestion=f"Ajoutez le champ '{champ}' aux données"
                ))
            elif isinstance(valeur, list) and len(valeur) == 0:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="LISTE_VIDE",
                    message=f"Liste vide: {description}",
                    chemin=champ,
                    suggestion=f"Ajoutez au moins un élément à '{champ}'"
                ))

        # Vérifier les sous-champs obligatoires de l'acte
        if 'acte' in donnees:
            sous_champs_acte = ['date', 'notaire']
            for sous_champ in sous_champs_acte:
                chemin = f"acte.{sous_champ}"
                existe, _ = self._get_valeur(donnees, chemin)
                if not existe:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="CHAMP_REQUIS_MANQUANT",
                        message=f"Information de l'acte manquante: {sous_champ}",
                        chemin=chemin
                    ))

        # Vérifier les informations du notaire
        if 'acte' in donnees and 'notaire' in donnees['acte']:
            champs_notaire = ['nom', 'prenom', 'ville', 'adresse']
            for champ in champs_notaire:
                chemin = f"acte.notaire.{champ}"
                existe, valeur = self._get_valeur(donnees, chemin)
                if not existe or not valeur:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="NOTAIRE_INCOMPLET",
                        message=f"Information du notaire manquante: {champ}",
                        chemin=chemin
                    ))

        # Vérifier le prix
        if 'prix' in donnees:
            if 'montant' not in donnees['prix'] or donnees['prix']['montant'] is None:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="PRIX_MANQUANT",
                    message="Le montant du prix est manquant",
                    chemin="prix.montant"
                ))

        # Vérifier les lots
        if 'bien' in donnees and 'lots' in donnees['bien']:
            for i, lot in enumerate(donnees['bien']['lots']):
                champs_lot = ['numero', 'description']
                for champ in champs_lot:
                    if champ not in lot or not lot[champ]:
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="LOT_INCOMPLET",
                            message=f"Information du lot {i+1} manquante: {champ}",
                            chemin=f"bien.lots.{i}.{champ}"
                        ))

    def _valider_dates(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence des dates."""

        # Date de l'acte
        date_acte = None
        if 'acte' in donnees and 'date' in donnees['acte']:
            date_obj = donnees['acte']['date']
            if isinstance(date_obj, dict):
                try:
                    date_acte = datetime(
                        date_obj.get('annee', 2025),
                        date_obj.get('mois', 1),
                        date_obj.get('jour', 1)
                    )
                except ValueError as e:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="DATE_INVALIDE",
                        message=f"Date de l'acte invalide: {e}",
                        chemin="acte.date"
                    ))

        # Vérifier que la date de l'acte n'est pas dans le futur (avertissement)
        if date_acte and date_acte > datetime.now():
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="DATE_FUTURE",
                message="La date de l'acte est dans le futur",
                chemin="acte.date",
                valeur=date_acte.strftime("%d/%m/%Y")
            ))

        # Vérifier les dates de naissance des parties
        for type_partie, cle in [('vendeurs', 'vendeurs'), ('acquéreurs', 'acquereurs')]:
            if cle in donnees:
                for i, personne in enumerate(donnees[cle]):
                    if 'date_naissance' in personne:
                        try:
                            date_naissance = self._parser_date(personne['date_naissance'])
                            if date_naissance:
                                # Vérifier que la personne est majeure
                                if date_acte:
                                    age = (date_acte - date_naissance).days // 365
                                    if age < 18:
                                        self.rapport.ajouter(ResultatValidation(
                                            niveau=NiveauErreur.ERREUR,
                                            code="MINEUR",
                                            message=f"{type_partie.capitalize()} {i+1} est mineur ({age} ans)",
                                            chemin=f"{cle}.{i}.date_naissance",
                                            suggestion="Un mineur doit être représenté par son représentant légal"
                                        ))
                        except ValueError:
                            self.rapport.ajouter(ResultatValidation(
                                niveau=NiveauErreur.ERREUR,
                                code="DATE_NAISSANCE_INVALIDE",
                                message=f"Date de naissance invalide pour {type_partie} {i+1}",
                                chemin=f"{cle}.{i}.date_naissance"
                            ))

    def _parser_date(self, date_str: str) -> Optional[datetime]:
        """Parse une date au format DD/MM/YYYY ou YYYY-MM-DD."""
        if not date_str:
            return None
        try:
            if '-' in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                return datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            return None

    def _valider_montants(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence des montants."""

        # Prix
        prix = donnees.get('prix', {}).get('montant', 0)
        if prix <= 0:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="PRIX_INVALIDE",
                message="Le prix doit être supérieur à zéro",
                chemin="prix.montant",
                valeur=prix
            ))

        # Vérifier la cohérence des prêts
        if 'paiement' in donnees and 'prets' in donnees['paiement']:
            total_prets = sum(p.get('montant', 0) for p in donnees['paiement']['prets'])
            fonds_personnels = donnees.get('paiement', {}).get('fonds_personnels', 0)

            # Le total ne doit pas dépasser le prix + frais estimés
            marge_frais = prix * 0.15  # ~15% de frais estimés
            if total_prets > prix + marge_frais:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="PRETS_EXCESSIFS",
                    message=f"Le total des prêts ({total_prets}€) semble élevé par rapport au prix ({prix}€)",
                    chemin="paiement.prets",
                    valeur=total_prets
                ))

        # Vérifier les quotités
        for cle, description in [('quotites_vendues', 'vendues'), ('quotites_acquises', 'acquises')]:
            if cle in donnees:
                total_pourcentage = sum(q.get('pourcentage', 0) for q in donnees[cle])
                # Si les pourcentages sont spécifiés, ils doivent totaliser 100
                if total_pourcentage > 0 and abs(total_pourcentage - 100) > 0.01:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="QUOTITES_INVALIDES",
                        message=f"Les quotités {description} ne totalisent pas 100% ({total_pourcentage}%)",
                        chemin=cle,
                        valeur=total_pourcentage
                    ))

        # Vérifier l'emprunt collectif copropriété
        if 'copropriete' in donnees:
            emprunt = donnees['copropriete'].get('emprunt_collectif', {})
            if emprunt.get('existe') and emprunt.get('solde', 0) > prix:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="EMPRUNT_COLLECTIF_ELEVE",
                    message=f"Le solde de l'emprunt collectif ({emprunt['solde']}€) est supérieur au prix de vente",
                    chemin="copropriete.emprunt_collectif.solde"
                ))

    def _valider_references(self, donnees: Dict[str, Any]):
        """Vérifie le format des références cadastrales et publications."""

        # Références cadastrales
        if 'bien' in donnees and 'cadastre' in donnees['bien']:
            for i, parcelle in enumerate(donnees['bien']['cadastre']):
                section = parcelle.get('section', '')
                if section and not re.match(r'^[A-Z]{1,2}$', section):
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.AVERTISSEMENT,
                        code="SECTION_CADASTRALE_INVALIDE",
                        message=f"Format de section cadastrale inhabituel: {section}",
                        chemin=f"bien.cadastre.{i}.section",
                        suggestion="La section est généralement une ou deux lettres majuscules"
                    ))

        # Numéro ADEME du DPE
        if 'diagnostics' in donnees and 'dpe' in donnees['diagnostics']:
            numero_ademe = donnees['diagnostics']['dpe'].get('numero_ademe', '')
            if numero_ademe and not re.match(r'^[0-9A-Z]+$', numero_ademe):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="NUMERO_ADEME_SUSPECT",
                    message=f"Format du numéro ADEME inhabituel: {numero_ademe}",
                    chemin="diagnostics.dpe.numero_ademe"
                ))

    def _valider_logique_juridique(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence juridique des données."""

        # Si paiement par prêt, condition suspensive recommandée
        if 'paiement' in donnees and 'prets' in donnees['paiement']:
            prets = donnees['paiement']['prets']
            if prets and len(prets) > 0:
                # Pour une promesse, on devrait avoir une condition suspensive
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.INFO,
                    code="PRET_DETECTE",
                    message="Un prêt a été détecté - vérifiez la présence d'une condition suspensive dans l'avant-contrat",
                    chemin="paiement.prets"
                ))

        # Si copropriété, vérifier présence du syndic
        if 'copropriete' in donnees:
            if 'syndic' not in donnees['copropriete']:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="SYNDIC_MANQUANT",
                    message="Les informations du syndic sont manquantes pour une copropriété",
                    chemin="copropriete.syndic"
                ))

        # Vérifier cohérence régime matrimonial
        for cle in ['vendeurs', 'acquereurs']:
            if cle in donnees:
                for i, personne in enumerate(donnees[cle]):
                    sit_mat = personne.get('situation_matrimoniale', {})
                    if sit_mat.get('statut') == 'marie':
                        if sit_mat.get('regime_matrimonial') in ['separation_biens', 'communaute_universelle', 'participation_acquets']:
                            if 'contrat_mariage' not in sit_mat or not sit_mat['contrat_mariage'].get('notaire'):
                                self.rapport.ajouter(ResultatValidation(
                                    niveau=NiveauErreur.ERREUR,
                                    code="CONTRAT_MARIAGE_MANQUANT",
                                    message=f"Le régime matrimonial nécessite un contrat de mariage non spécifié",
                                    chemin=f"{cle}.{i}.situation_matrimoniale.contrat_mariage"
                                ))

    def _valider_personnes(self, donnees: Dict[str, Any]):
        """Vérifie la validité des informations des personnes (physiques et morales)."""

        for cle, type_partie in [('vendeurs', 'Vendeur'), ('acquereurs', 'Acquéreur')]:
            if cle in donnees:
                for i, personne in enumerate(donnees[cle]):
                    # Déterminer si personne morale ou physique
                    type_personne = personne.get('type_personne', 'physique')

                    if type_personne == 'morale':
                        self._valider_personne_morale(personne, cle, i, type_partie)
                    else:
                        self._valider_personne_physique(personne, cle, i, type_partie)

    def _valider_personne_physique(self, personne: Dict, cle: str, index: int, type_partie: str):
        """Valide une personne physique."""
        # Nom et prénom obligatoires
        if not personne.get('nom'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="NOM_MANQUANT",
                message=f"Nom manquant pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.nom"
            ))

        if not personne.get('prenoms'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="PRENOM_MANQUANT",
                message=f"Prénom(s) manquant(s) pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.prenoms"
            ))

        # Adresse obligatoire
        if not personne.get('adresse'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="ADRESSE_MANQUANTE",
                message=f"Adresse manquante pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.adresse"
            ))

        # Date et lieu de naissance
        if not personne.get('date_naissance'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="DATE_NAISSANCE_MANQUANTE",
                message=f"Date de naissance manquante pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.date_naissance"
            ))

        if not personne.get('lieu_naissance'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="LIEU_NAISSANCE_MANQUANT",
                message=f"Lieu de naissance manquant pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.lieu_naissance"
            ))

        # Valider situation PACS
        self._valider_pacs(personne, cle, index, type_partie)

    def _valider_personne_morale(self, personne: Dict, cle: str, index: int, type_partie: str):
        """Valide une personne morale (SCI, SARL, etc.)."""
        # Dénomination obligatoire
        if not personne.get('denomination'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="DENOMINATION_MANQUANTE",
                message=f"Dénomination sociale manquante pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.denomination"
            ))

        # Forme juridique obligatoire
        forme = personne.get('forme_juridique', '')
        if not forme:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="FORME_JURIDIQUE_MANQUANTE",
                message=f"Forme juridique manquante pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.forme_juridique"
            ))
        else:
            formes_valides = ['SCI', 'SARL', 'SAS', 'SA', 'SNC', 'EURL', 'SASU', 'SC',
                           'Association', 'Fondation', 'GIE', 'Syndicat', 'Autre']
            if forme not in formes_valides:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="FORME_JURIDIQUE_INCONNUE",
                    message=f"Forme juridique non reconnue: {forme}",
                    chemin=f"{cle}.{index}.forme_juridique",
                    suggestion=f"Formes connues: {', '.join(formes_valides)}"
                ))

        # Siège social obligatoire
        siege = personne.get('siege_social', {})
        if not siege or not siege.get('adresse'):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="SIEGE_SOCIAL_MANQUANT",
                message=f"Siège social manquant pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.siege_social"
            ))

        # SIREN obligatoire
        siren = personne.get('siren', '')
        if not siren:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="SIREN_MANQUANT",
                message=f"Numéro SIREN manquant pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.siren"
            ))
        elif not re.match(r'^\d{9}$', siren):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="SIREN_INVALIDE",
                message=f"Format SIREN invalide: {siren} (9 chiffres attendus)",
                chemin=f"{cle}.{index}.siren"
            ))

        # Représentant légal obligatoire
        representant = personne.get('representant', {})
        if not representant:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="REPRESENTANT_MANQUANT",
                message=f"Représentant légal manquant pour {type_partie} {index+1}",
                chemin=f"{cle}.{index}.representant"
            ))
        else:
            # Vérifier qualité du représentant
            qualite = representant.get('qualite', '')
            if not qualite:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="QUALITE_REPRESENTANT_MANQUANTE",
                    message=f"Qualité du représentant manquante pour {type_partie} {index+1}",
                    chemin=f"{cle}.{index}.representant.qualite"
                ))

            # Nom du représentant
            if not representant.get('nom'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="NOM_REPRESENTANT_MANQUANT",
                    message=f"Nom du représentant manquant pour {type_partie} {index+1}",
                    chemin=f"{cle}.{index}.representant.nom"
                ))

            # Pouvoirs du représentant
            pouvoir = representant.get('pouvoir', {})
            if not pouvoir.get('source'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="POUVOIRS_NON_SPECIFIES",
                    message=f"Source des pouvoirs du représentant non spécifiée pour {type_partie} {index+1}",
                    chemin=f"{cle}.{index}.representant.pouvoir",
                    suggestion="Préciser l'origine des pouvoirs (statuts, PV AG, délégation)"
                ))

        # RCS recommandé pour les sociétés commerciales
        formes_commerciales = ['SARL', 'SAS', 'SA', 'SNC', 'EURL', 'SASU']
        if forme in formes_commerciales:
            rcs = personne.get('rcs', {})
            if not rcs or not rcs.get('numero'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="RCS_MANQUANT",
                    message=f"Numéro RCS recommandé pour {forme} ({type_partie} {index+1})",
                    chemin=f"{cle}.{index}.rcs"
                ))

    def _valider_pacs(self, personne: Dict, cle: str, index: int, type_partie: str):
        """Valide la structure PACS."""
        sit_mat = personne.get('situation_matrimoniale', {})
        if sit_mat.get('statut') == 'pacse':
            # Vérifier que les infos PACS sont présentes
            if not sit_mat.get('pacs') and not sit_mat.get('date_pacs'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="PACS_INCOMPLET",
                    message=f"Informations PACS incomplètes pour {type_partie} {index+1}",
                    chemin=f"{cle}.{index}.situation_matrimoniale",
                    suggestion="Ajoutez date_pacs et lieu_pacs ou structure pacs:{date, regime_libelle}"
                ))

            # Vérifier partenaire vs conjoint
            if not sit_mat.get('conjoint') and not sit_mat.get('partenaire'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="PARTENAIRE_MANQUANT",
                    message=f"Informations du partenaire PACS manquantes pour {type_partie} {index+1}",
                    chemin=f"{cle}.{index}.situation_matrimoniale.partenaire"
                ))

    # =========================================================================
    # RÈGLES DE VALIDATION AVANCÉES (12+ règles)
    # =========================================================================

    def _valider_superficie_carrez(self, donnees: Dict[str, Any]):
        """Valide les superficies Carrez des lots."""
        if 'bien' not in donnees or 'lots' not in donnees['bien']:
            return

        for i, lot in enumerate(donnees['bien']['lots']):
            surface = lot.get('surface_carrez', lot.get('surface', 0))
            if surface:
                # Vérifier si < 8m² (Carrez non obligatoire)
                if 0 < surface < 8:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.INFO,
                        code="CARREZ_PETIT_LOT",
                        message=f"Lot {lot.get('numero', i+1)}: surface < 8m² - Carrez non obligatoire",
                        chemin=f"bien.lots.{i}.surface_carrez",
                        valeur=surface
                    ))

                # Vérifier si surface très grande (>300m² suspect)
                if surface > 300:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.AVERTISSEMENT,
                        code="CARREZ_GRANDE_SURFACE",
                        message=f"Lot {lot.get('numero', i+1)}: surface > 300m² - vérifier la valeur",
                        chemin=f"bien.lots.{i}.surface_carrez",
                        valeur=surface
                    ))

    def _valider_diagnostics_dpe(self, donnees: Dict[str, Any]):
        """Valide le DPE et alertes passoires énergétiques."""
        if 'diagnostics' not in donnees:
            return

        dpe = donnees['diagnostics'].get('dpe', {})
        classe_energie = dpe.get('classe_energie', dpe.get('classe', ''))

        if classe_energie:
            # Passoire énergétique (F ou G)
            if classe_energie.upper() in ['F', 'G']:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="PASSOIRE_ENERGETIQUE",
                    message=f"ATTENTION: DPE classe {classe_energie} - Passoire énergétique",
                    chemin="diagnostics.dpe.classe_energie",
                    valeur=classe_energie,
                    suggestion="Interdiction de location depuis 2025 (G) ou 2028 (F). Informer l'acquéreur."
                ))

            # Audit énergétique obligatoire pour F et G (depuis avril 2023)
            if classe_energie.upper() in ['F', 'G'] and not donnees['diagnostics'].get('audit_energetique'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="AUDIT_ENERGETIQUE_MANQUANT",
                    message=f"Audit énergétique obligatoire pour DPE classe {classe_energie}",
                    chemin="diagnostics.audit_energetique",
                    suggestion="L'audit énergétique est obligatoire depuis avril 2023 pour la vente"
                ))

    def _valider_diagnostics_obligatoires(self, donnees: Dict[str, Any]):
        """Vérifie la présence des diagnostics obligatoires selon l'année de construction."""
        if 'bien' not in donnees:
            return

        annee_construction = donnees['bien'].get('annee_construction', 0)
        diagnostics = donnees.get('diagnostics', {})

        # Plomb si avant 1949
        if annee_construction > 0 and annee_construction < 1949:
            if not diagnostics.get('plomb'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="PLOMB_OBLIGATOIRE",
                    message="Diagnostic plomb obligatoire (construction avant 1949)",
                    chemin="diagnostics.plomb",
                    suggestion="Le CREP (Constat de Risque d'Exposition au Plomb) est obligatoire"
                ))

        # Amiante si avant 1997
        if annee_construction > 0 and annee_construction < 1997:
            if not diagnostics.get('amiante'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="AMIANTE_OBLIGATOIRE",
                    message="Diagnostic amiante obligatoire (construction avant 1997)",
                    chemin="diagnostics.amiante"
                ))

        # Électricité et gaz si installation > 15 ans
        annee_installation = donnees['bien'].get('annee_installation_electrique', 0)
        if annee_installation > 0 and (datetime.now().year - annee_installation) > 15:
            if not diagnostics.get('electricite'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="ELECTRICITE_RECOMMANDE",
                    message="Diagnostic électricité recommandé (installation > 15 ans)",
                    chemin="diagnostics.electricite"
                ))

    def _valider_coherence_adresse(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence des adresses (code postal vs commune)."""
        if 'bien' not in donnees:
            return

        adresse = donnees['bien'].get('adresse', {})

        # Si adresse est une string, extraire code postal si possible
        if isinstance(adresse, str):
            # Essayer d'extraire un code postal français (5 chiffres)
            match = re.search(r'\b(\d{5})\b', adresse)
            code_postal = match.group(1) if match else ''
            commune = ''
        else:
            code_postal = str(adresse.get('code_postal', ''))
            commune = adresse.get('commune', '')

        # Vérifier format code postal français
        if code_postal and not re.match(r'^\d{5}$', code_postal):
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.ERREUR,
                code="CODE_POSTAL_INVALIDE",
                message=f"Format de code postal invalide: {code_postal}",
                chemin="bien.adresse.code_postal",
                suggestion="Le code postal doit comporter 5 chiffres"
            ))

        # Vérifier cohérence département (premiers 2 chiffres)
        if code_postal and len(code_postal) == 5:
            dept = code_postal[:2]
            # DOM-TOM: 97x, 98x
            if dept in ['97', '98'] and len(code_postal) == 5:
                dept = code_postal[:3]

    def _valider_coherence_financiere(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence financière globale."""
        prix = donnees.get('prix', {}).get('montant', 0)
        if prix <= 0:
            return

        # Calcul des frais de notaire estimés
        frais_estimes = prix * 0.08  # ~8% pour l'ancien

        # Vérifier le financement
        paiement = donnees.get('paiement', {})
        fonds_propres = paiement.get('fonds_personnels', 0)
        prets = paiement.get('prets', [])
        total_prets = sum(p.get('montant', 0) for p in prets)

        total_financement = fonds_propres + total_prets
        total_a_financer = prix + frais_estimes

        # Sous-financement
        if total_financement > 0 and total_financement < prix:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="SOUS_FINANCEMENT",
                message=f"Financement ({total_financement}€) inférieur au prix ({prix}€)",
                chemin="paiement",
                suggestion=f"Prévoir environ {total_a_financer:.0f}€ (prix + frais)"
            ))

        # PTZ: vérifier conditions
        for i, pret in enumerate(prets):
            if pret.get('type', '').lower() in ['ptz', 'pret_taux_zero']:
                # PTZ uniquement pour résidence principale
                usage = donnees.get('bien', {}).get('usage_futur', '')
                if usage and usage != 'habitation':
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="PTZ_USAGE_INVALIDE",
                        message="PTZ uniquement pour résidence principale",
                        chemin=f"paiement.prets.{i}",
                        suggestion="Le PTZ nécessite que le bien soit la résidence principale"
                    ))

    def _valider_tantièmes(self, donnees: Dict[str, Any]):
        """Vérifie la cohérence des tantièmes."""
        if 'bien' not in donnees or 'lots' not in donnees['bien']:
            return

        for i, lot in enumerate(donnees['bien']['lots']):
            tantiemes = lot.get('tantiemes', {})
            valeur = tantiemes.get('valeur', 0)
            base = tantiemes.get('base', 0)

            if valeur and base:
                # Vérifier que la valeur est inférieure à la base
                if valeur > base:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code="TANTIEMES_INVALIDES",
                        message=f"Lot {lot.get('numero', i+1)}: tantièmes ({valeur}) > base ({base})",
                        chemin=f"bien.lots.{i}.tantiemes",
                        suggestion="Les tantièmes ne peuvent pas dépasser la base totale"
                    ))

    # =========================================================================
    # NOUVELLES RÈGLES DE VALIDATION MÉTIER (v1.5.0)
    # =========================================================================

    def _valider_intervention_conjoint(self, donnees: Dict[str, Any]):
        """
        Vérifie que le conjoint intervient si le bien est commun.

        ERREUR si:
        - Vendeur marié en communauté (légale ou universelle)
        - ET bien acquis pendant le mariage (présumé commun)
        - ET conjoint n'intervient pas à l'acte
        """
        vendeurs = donnees.get('vendeurs', donnees.get('promettants', []))

        regimes_communaute = [
            'communaute_legale', 'communauté légale', 'communaute_universelle',
            'communauté universelle', 'communaute_reduite_aux_acquets',
            'communauté réduite aux acquêts', 'regime_legal', 'régime légal'
        ]

        for i, vendeur in enumerate(vendeurs):
            situation = vendeur.get('situation_matrimoniale', {})
            statut = situation.get('statut', '').lower()
            regime = situation.get('regime_matrimonial', situation.get('regime', '')).lower()

            # Vérifier si marié en communauté
            if statut in ['marie', 'marié', 'mariee', 'mariée']:
                est_communaute = any(r in regime for r in regimes_communaute) or not regime

                if est_communaute:
                    # Vérifier si le conjoint intervient
                    conjoint = situation.get('conjoint', {})
                    conjoint_intervient = conjoint.get('intervient', False)

                    # Chercher aussi dans la liste des co-vendeurs
                    nom_conjoint = conjoint.get('nom', '').upper()
                    conjoint_dans_vendeurs = any(
                        v.get('nom', '').upper() == nom_conjoint and v != vendeur
                        for v in vendeurs
                    ) if nom_conjoint else False

                    if not conjoint_intervient and not conjoint_dans_vendeurs:
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="CONJOINT_NON_INTERVENANT",
                            message=f"Le vendeur {vendeur.get('nom', '')} est marié en communauté mais le conjoint n'intervient pas",
                            chemin=f"vendeurs.{i}.situation_matrimoniale",
                            suggestion="Le conjoint doit intervenir à l'acte pour vendre un bien commun (art. 1424 Code civil)"
                        ))

    def _valider_diagnostics_validite(self, donnees: Dict[str, Any]):
        """
        Vérifie que les diagnostics ne sont pas expirés.

        Durées de validité:
        - DPE: 10 ans
        - Plomb (CREP): 1 an si présence, illimité si absence
        - Amiante: 3 ans si présence, illimité si absence
        - Termites: 6 mois
        - Électricité: 3 ans
        - Gaz: 3 ans
        - ERP: 6 mois
        """
        diagnostics = donnees.get('diagnostics', {})
        if not diagnostics:
            return

        date_acte = donnees.get('acte', {}).get('date', {})
        if isinstance(date_acte, dict):
            try:
                date_ref = datetime(
                    date_acte.get('annee', datetime.now().year),
                    date_acte.get('mois', 1),
                    date_acte.get('jour', 1)
                )
            except (ValueError, TypeError):
                date_ref = datetime.now()
        else:
            date_ref = datetime.now()

        # Configuration des durées de validité (en jours)
        validites = {
            'dpe': {'duree': 3650, 'nom': 'DPE'},  # 10 ans
            'electricite': {'duree': 1095, 'nom': 'Diagnostic électricité'},  # 3 ans
            'gaz': {'duree': 1095, 'nom': 'Diagnostic gaz'},  # 3 ans
            'termites': {'duree': 180, 'nom': 'État termites'},  # 6 mois
            'etat_risques': {'duree': 180, 'nom': 'ERP'},  # 6 mois
            'erp': {'duree': 180, 'nom': 'ERP'},  # 6 mois
            'plomb': {'duree': 365, 'nom': 'CREP (plomb)', 'si_positif': True},  # 1 an si positif
            'amiante': {'duree': 1095, 'nom': 'Amiante', 'si_positif': True},  # 3 ans si positif
        }

        for diag_key, config in validites.items():
            diag = diagnostics.get(diag_key, {})
            if not diag:
                continue

            date_diag = diag.get('date', '')
            if not date_diag:
                continue

            # Parser la date du diagnostic
            try:
                if isinstance(date_diag, str):
                    if '/' in date_diag:
                        date_diag_parsed = datetime.strptime(date_diag, '%d/%m/%Y')
                    elif '-' in date_diag:
                        date_diag_parsed = datetime.strptime(date_diag, '%Y-%m-%d')
                    else:
                        continue
                else:
                    continue

                # Calculer l'ancienneté
                jours_ecoules = (date_ref - date_diag_parsed).days

                # Vérifier si expiré
                if jours_ecoules > config['duree']:
                    # Pour plomb/amiante, vérifier si présence
                    if config.get('si_positif'):
                        presence = diag.get('presence', diag.get('positif', None))
                        if presence is False:
                            continue  # Illimité si absence

                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.ERREUR,
                        code=f"DIAGNOSTIC_EXPIRE_{diag_key.upper()}",
                        message=f"{config['nom']} expiré ({jours_ecoules} jours, max {config['duree']})",
                        chemin=f"diagnostics.{diag_key}.date",
                        suggestion=f"Renouveler le {config['nom']} avant la signature"
                    ))

            except (ValueError, TypeError):
                pass

    def _valider_coherence_dates_promesse(self, donnees: Dict[str, Any]):
        """
        Vérifie la cohérence des dates pour une promesse de vente.

        AVERTISSEMENT si:
        - date_obtention_pret > delai_realisation
        - delai_realisation < date_acte + 30 jours
        """
        # Délai de réalisation
        delai = donnees.get('delai_realisation', donnees.get('delais', {}).get('date_realisation', ''))
        if not delai:
            return

        # Date de l'acte
        date_acte = donnees.get('acte', {}).get('date', {})

        try:
            # Parser délai de réalisation
            if isinstance(delai, str):
                if '-' in delai:
                    date_delai = datetime.strptime(delai, '%Y-%m-%d')
                elif '/' in delai:
                    date_delai = datetime.strptime(delai, '%d/%m/%Y')
                else:
                    return
            else:
                return

            # Parser date acte
            if isinstance(date_acte, dict):
                date_acte_parsed = datetime(
                    date_acte.get('annee', datetime.now().year),
                    date_acte.get('mois', 1),
                    date_acte.get('jour', 1)
                )
            else:
                date_acte_parsed = datetime.now()

            # Vérifier délai minimum (30 jours)
            jours_delai = (date_delai - date_acte_parsed).days
            if jours_delai < 30:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="DELAI_REALISATION_COURT",
                    message=f"Délai de réalisation très court ({jours_delai} jours)",
                    chemin="delai_realisation",
                    suggestion="Prévoir au minimum 60-90 jours pour les formalités"
                ))

            # Vérifier cohérence avec date obtention prêt
            conditions = donnees.get('conditions_suspensives', {})
            pret = conditions.get('pret', {})
            date_pret = pret.get('date_limite_obtention', '')

            if date_pret:
                if isinstance(date_pret, str):
                    if '-' in date_pret:
                        date_pret_parsed = datetime.strptime(date_pret, '%Y-%m-%d')
                    elif '/' in date_pret:
                        date_pret_parsed = datetime.strptime(date_pret, '%d/%m/%Y')
                    else:
                        return

                    if date_pret_parsed > date_delai:
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.AVERTISSEMENT,
                            code="DATE_PRET_APRES_REALISATION",
                            message="Date limite d'obtention du prêt postérieure au délai de réalisation",
                            chemin="conditions_suspensives.pret.date_limite_obtention",
                            suggestion="La date d'obtention du prêt doit être antérieure au délai de réalisation"
                        ))

        except (ValueError, TypeError):
            pass

    def _valider_prix_coherent(self, donnees: Dict[str, Any]):
        """
        Vérifie que le prix au m² est cohérent.

        AVERTISSEMENT si prix/m² aberrant:
        - Hors Paris: < 500€/m² ou > 15000€/m²
        - Paris (75): < 5000€/m² ou > 25000€/m²
        """
        prix = donnees.get('prix', {}).get('montant', 0)
        if not prix or prix <= 0:
            return

        # Chercher la surface
        bien = donnees.get('bien', {})
        surface = bien.get('superficie_carrez', {})
        if isinstance(surface, dict):
            surface_m2 = surface.get('superficie_m2', surface.get('valeur', 0))
        else:
            surface_m2 = surface if isinstance(surface, (int, float)) else 0

        # Si pas de Carrez, chercher dans les lots
        if not surface_m2:
            lots = bien.get('lots', [])
            surface_m2 = sum(l.get('superficie_carrez', 0) for l in lots)

        if not surface_m2 or surface_m2 <= 0:
            return

        prix_m2 = prix / surface_m2

        # Déterminer si Paris
        adresse = bien.get('adresse', {})
        code_postal = str(adresse.get('code_postal', ''))
        est_paris = code_postal.startswith('75')

        # Seuils
        if est_paris:
            min_prix = 5000
            max_prix = 25000
            zone = "Paris"
        else:
            min_prix = 500
            max_prix = 15000
            zone = "hors Paris"

        if prix_m2 < min_prix:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="PRIX_M2_ANORMALEMENT_BAS",
                message=f"Prix/m² anormalement bas: {prix_m2:.0f}€/m² ({zone}, min attendu: {min_prix}€)",
                chemin="prix.montant",
                suggestion="Vérifier le prix ou la surface déclarée"
            ))
        elif prix_m2 > max_prix:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="PRIX_M2_ANORMALEMENT_HAUT",
                message=f"Prix/m² anormalement élevé: {prix_m2:.0f}€/m² ({zone}, max attendu: {max_prix}€)",
                chemin="prix.montant",
                suggestion="Vérifier le prix ou la surface déclarée"
            ))

    def _valider_dpe_energie(self, donnees: Dict[str, Any]):
        """
        Vérifie les obligations liées au DPE (passoires thermiques).

        ERREUR si:
        - DPE classe F ou G
        - ET pas d'audit énergétique
        (Obligatoire depuis avril 2023)
        """
        diagnostics = donnees.get('diagnostics', {})
        dpe = diagnostics.get('dpe', {})

        classe = dpe.get('classe_energie', dpe.get('classe', '')).upper()

        if classe in ['F', 'G']:
            audit = diagnostics.get('audit_energetique', {})
            if not audit or not audit.get('date'):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="AUDIT_ENERGETIQUE_MANQUANT",
                    message=f"Audit énergétique obligatoire pour DPE classe {classe} (passoire thermique)",
                    chemin="diagnostics.audit_energetique",
                    suggestion="Réaliser un audit énergétique avant la vente (obligation depuis avril 2023)"
                ))

    def _extraire_pourcentage_quotite(self, q) -> float:
        """
        Extrait le pourcentage d'une quotité (dict ou string).

        Supporte:
        - Dict: {"pourcentage": 50} ou {"fraction": "1/2"}
        - String: "50%" ou "1/2" ou "moitié"
        """
        if isinstance(q, dict):
            return q.get('pourcentage', 0) or self._fraction_to_pct(q.get('fraction', ''))
        elif isinstance(q, str):
            # String comme "50%", "100%", "1/2"
            q = q.strip()
            if q.endswith('%'):
                try:
                    return float(q[:-1])
                except ValueError:
                    return 0
            elif '/' in q:
                return self._fraction_to_pct(q)
            elif q.lower() in ('moitié', 'moitie'):
                return 50.0
            elif q.lower() == 'totalité':
                return 100.0
        return 0

    def _valider_quotites_croisees(self, donnees: Dict[str, Any]):
        """
        Vérifie la cohérence croisée des quotités vendeurs/acquéreurs.

        ERREUR si:
        - Total quotités vendues ≠ 100%
        - Total quotités acquises ≠ 100%
        - Nombre de vendeurs ≠ nombre de quotités vendues (si spécifié)
        """
        # Quotités vendues
        vendeurs = donnees.get('vendeurs', donnees.get('promettants', []))
        quotites_vendues = donnees.get('quotites_vendues', [])

        if quotites_vendues:
            # Calculer le total (supporte dict et string)
            total_vendues = sum(
                self._extraire_pourcentage_quotite(q)
                for q in quotites_vendues
            )

            if abs(total_vendues - 100) > 0.01 and total_vendues > 0:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="QUOTITES_VENDUES_INVALIDES",
                    message=f"Les quotités vendues ne totalisent pas 100% ({total_vendues:.2f}%)",
                    chemin="quotites_vendues",
                    suggestion="Ajuster les quotités pour qu'elles totalisent exactement 100%"
                ))

            # Vérifier correspondance avec nombre de vendeurs
            if len(quotites_vendues) != len(vendeurs) and len(vendeurs) > 0:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="QUOTITES_VENDEURS_MISMATCH",
                    message=f"Nombre de quotités ({len(quotites_vendues)}) ≠ nombre de vendeurs ({len(vendeurs)})",
                    chemin="quotites_vendues",
                    suggestion="Vérifier que chaque vendeur a une quotité associée"
                ))

        # Quotités acquises
        acquereurs = donnees.get('acquereurs', donnees.get('beneficiaires', []))
        quotites_acquises = donnees.get('quotites_acquises', [])

        if quotites_acquises:
            total_acquises = sum(
                self._extraire_pourcentage_quotite(q)
                for q in quotites_acquises
            )

            if abs(total_acquises - 100) > 0.01 and total_acquises > 0:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="QUOTITES_ACQUISES_INVALIDES",
                    message=f"Les quotités acquises ne totalisent pas 100% ({total_acquises:.2f}%)",
                    chemin="quotites_acquises",
                    suggestion="Ajuster les quotités pour qu'elles totalisent exactement 100%"
                ))

            if len(quotites_acquises) != len(acquereurs) and len(acquereurs) > 0:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="QUOTITES_ACQUEREURS_MISMATCH",
                    message=f"Nombre de quotités ({len(quotites_acquises)}) ≠ nombre d'acquéreurs ({len(acquereurs)})",
                    chemin="quotites_acquises",
                    suggestion="Vérifier que chaque acquéreur a une quotité associée"
                ))

        # Si plusieurs vendeurs sans quotités spécifiées
        if len(vendeurs) > 1 and not quotites_vendues:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="QUOTITES_VENDUES_MANQUANTES",
                message=f"Plusieurs vendeurs ({len(vendeurs)}) sans quotités définies",
                chemin="quotites_vendues",
                suggestion="Définir les quotités de propriété de chaque vendeur"
            ))

        if len(acquereurs) > 1 and not quotites_acquises:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="QUOTITES_ACQUISES_MANQUANTES",
                message=f"Plusieurs acquéreurs ({len(acquereurs)}) sans quotités définies",
                chemin="quotites_acquises",
                suggestion="Définir les quotités d'acquisition de chaque acquéreur"
            ))

    def _fraction_to_pct(self, fraction: str) -> float:
        """Convertit une fraction en pourcentage."""
        if not fraction:
            return 0.0
        try:
            if '/' in fraction:
                parts = fraction.split('/')
                return (float(parts[0]) / float(parts[1])) * 100
            return float(fraction)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _valider_cadastre_coherent(self, donnees: Dict[str, Any]):
        """
        Vérifie la cohérence des références cadastrales.

        ERREUR si:
        - Section cadastrale manquante
        - Numéro de parcelle manquant
        - Commune cadastrale différente de l'adresse

        AVERTISSEMENT si:
        - Format section inhabituel
        - Lieudit sans parcelle
        """
        bien = donnees.get('bien', {})
        cadastre = bien.get('cadastre', [])

        if not cadastre:
            self.rapport.ajouter(ResultatValidation(
                niveau=NiveauErreur.AVERTISSEMENT,
                code="CADASTRE_MANQUANT",
                message="Aucune référence cadastrale définie",
                chemin="bien.cadastre",
                suggestion="Ajouter les références cadastrales du bien"
            ))
            return

        adresse = bien.get('adresse', {})
        commune_adresse = adresse.get('commune', '').upper().strip()

        for i, parcelle in enumerate(cadastre):
            # Vérifier section
            section = parcelle.get('section', '')
            if not section:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="SECTION_CADASTRALE_MANQUANTE",
                    message=f"Section cadastrale manquante pour la parcelle {i+1}",
                    chemin=f"bien.cadastre.{i}.section"
                ))
            elif not re.match(r'^[A-Z]{1,2}$', section.upper()):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="SECTION_FORMAT_INHABITUEL",
                    message=f"Format de section cadastrale inhabituel: '{section}'",
                    chemin=f"bien.cadastre.{i}.section",
                    suggestion="La section est généralement 1 ou 2 lettres majuscules (ex: A, AB, ZC)"
                ))

            # Vérifier numéro de parcelle
            numero = parcelle.get('numero', parcelle.get('numero_parcelle', ''))
            if not numero:
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.ERREUR,
                    code="NUMERO_PARCELLE_MANQUANT",
                    message=f"Numéro de parcelle manquant pour la parcelle {i+1}",
                    chemin=f"bien.cadastre.{i}.numero"
                ))
            elif not re.match(r'^\d+[a-zA-Z]?$', str(numero)):
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.AVERTISSEMENT,
                    code="NUMERO_PARCELLE_FORMAT",
                    message=f"Format numéro de parcelle inhabituel: '{numero}'",
                    chemin=f"bien.cadastre.{i}.numero",
                    suggestion="Le numéro est généralement un nombre (ex: 123, 456b)"
                ))

            # Vérifier cohérence commune
            commune_cadastre = parcelle.get('commune', '').upper().strip()
            if commune_cadastre and commune_adresse:
                # Normaliser les communes (enlever articles, accents)
                norm_cad = self._normaliser_commune(commune_cadastre)
                norm_adr = self._normaliser_commune(commune_adresse)

                if norm_cad and norm_adr and norm_cad != norm_adr:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.AVERTISSEMENT,
                        code="COMMUNE_CADASTRE_DIFFERENTE",
                        message=f"Commune cadastrale '{commune_cadastre}' ≠ adresse '{commune_adresse}'",
                        chemin=f"bien.cadastre.{i}.commune",
                        suggestion="Vérifier que la commune cadastrale correspond à l'adresse du bien"
                    ))

            # Vérifier contenance si présente
            contenance = parcelle.get('contenance', parcelle.get('superficie', 0))
            if contenance and contenance > 100000:  # > 10 hectares
                self.rapport.ajouter(ResultatValidation(
                    niveau=NiveauErreur.INFO,
                    code="GRANDE_PARCELLE",
                    message=f"Parcelle de grande superficie: {contenance} m² ({contenance/10000:.2f} ha)",
                    chemin=f"bien.cadastre.{i}.contenance"
                ))

    def _normaliser_commune(self, commune: str) -> str:
        """Normalise le nom d'une commune pour comparaison."""
        if not commune:
            return ''
        # Supprimer les articles courants
        articles = ['LA ', 'LE ', 'LES ', 'L\'', 'SAINT-', 'SAINTE-', 'ST-', 'STE-']
        result = commune.upper().strip()
        for art in articles:
            if result.startswith(art):
                result = result[len(art):]
        # Supprimer accents basiques
        accents = {'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E', 'À': 'A', 'Â': 'A',
                   'Ù': 'U', 'Û': 'U', 'Î': 'I', 'Ï': 'I', 'Ô': 'O', 'Ç': 'C'}
        for acc, repl in accents.items():
            result = result.replace(acc, repl)
        return result.strip()

    def _valider_impots_plus_value(self, donnees: Dict[str, Any]):
        """
        Vérifie les déclarations relatives à la plus-value immobilière.

        AVERTISSEMENT si:
        - Bien non résidence principale et pas d'info plus-value
        - Durée de détention < 30 ans et pas de calcul plus-value

        INFO si:
        - Exonération applicable (résidence principale, > 30 ans)
        """
        plus_value = donnees.get('plus_value', {})
        bien = donnees.get('bien', {})
        vendeurs = donnees.get('vendeurs', donnees.get('promettants', []))

        # Vérifier si résidence principale (exonération)
        usage = bien.get('usage', bien.get('usage_actuel', '')).lower()
        est_residence_principale = 'principal' in usage or 'habitation' in usage

        # Vérifier durée de détention
        origine = donnees.get('origine_propriete', {})
        # origine_propriete peut être une liste ou un dict
        if isinstance(origine, list):
            origine = origine[0].get('origine_immediate', {}) if origine else {}
        date_acquisition = origine.get('date', {})

        if date_acquisition and isinstance(date_acquisition, dict):
            try:
                annee_acq = date_acquisition.get('annee', 0)
                if annee_acq:
                    duree_detention = datetime.now().year - annee_acq

                    if duree_detention >= 30:
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.INFO,
                            code="EXONERATION_30_ANS",
                            message=f"Bien détenu depuis {duree_detention} ans - Exonération plus-value totale",
                            chemin="origine_propriete.date"
                        ))
                    elif not est_residence_principale and not plus_value:
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.AVERTISSEMENT,
                            code="PLUS_VALUE_NON_RENSEIGNEE",
                            message=f"Plus-value potentiellement imposable (détention: {duree_detention} ans, non résidence principale)",
                            chemin="plus_value",
                            suggestion="Renseigner les informations de plus-value ou confirmer l'exonération"
                        ))
            except (ValueError, TypeError):
                pass

        # Si info plus-value présente, vérifier cohérence
        if plus_value:
            if plus_value.get('exoneration'):
                motif = plus_value.get('motif_exoneration', '')
                if not motif:
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.AVERTISSEMENT,
                        code="MOTIF_EXONERATION_MANQUANT",
                        message="Exonération déclarée mais motif non précisé",
                        chemin="plus_value.motif_exoneration",
                        suggestion="Préciser le motif d'exonération (résidence principale, > 30 ans, etc.)"
                    ))
            else:
                # Vérifier que le montant d'impôt est calculé
                if not plus_value.get('montant_impot') and plus_value.get('montant_brut'):
                    self.rapport.ajouter(ResultatValidation(
                        niveau=NiveauErreur.AVERTISSEMENT,
                        code="IMPOT_PLUS_VALUE_MANQUANT",
                        message="Plus-value brute déclarée mais montant d'impôt non calculé",
                        chemin="plus_value.montant_impot",
                        suggestion="Calculer l'impôt sur la plus-value (IR 19% + PS 17.2%)"
                    ))

    def valider_complet(self, donnees: Dict[str, Any], strict: bool = True) -> RapportValidation:
        """
        Validation complète avec toutes les règles avancées.

        Args:
            donnees: Données à valider
            strict: Mode strict

        Returns:
            Rapport de validation enrichi
        """
        # Validation de base
        self.valider(donnees, strict)

        # Règles avancées (existantes)
        self._valider_superficie_carrez(donnees)
        self._valider_diagnostics_dpe(donnees)
        self._valider_diagnostics_obligatoires(donnees)
        self._valider_coherence_adresse(donnees)
        self._valider_coherence_financiere(donnees)
        self._valider_tantièmes(donnees)

        # Règles métier v1.5.0
        self._valider_intervention_conjoint(donnees)
        self._valider_diagnostics_validite(donnees)
        self._valider_coherence_dates_promesse(donnees)
        self._valider_prix_coherent(donnees)
        self._valider_dpe_energie(donnees)

        # Règles métier v1.5.1
        self._valider_quotites_croisees(donnees)
        self._valider_cadastre_coherent(donnees)
        self._valider_impots_plus_value(donnees)

        return self.rapport


def afficher_rapport(rapport: RapportValidation):
    """Affiche le rapport de validation."""

    print("=" * 60)
    print("RAPPORT DE VALIDATION")
    print("=" * 60)

    if rapport.valide:
        print("\n[OK] VALIDATION REUSSIE - L'acte peut etre genere")
    else:
        print("\n[ERREUR] VALIDATION ECHOUEE - Corrections necessaires")

    if rapport.erreurs:
        print(f"\n[ERREURS] ({len(rapport.erreurs)}):")
        for err in rapport.erreurs:
            print(f"   [{err.code}] {err.message}")
            if err.chemin:
                print(f"      Chemin: {err.chemin}")
            if err.suggestion:
                print(f"      -> {err.suggestion}")

    if rapport.avertissements:
        print(f"\n[AVERTISSEMENTS] ({len(rapport.avertissements)}):")
        for warn in rapport.avertissements:
            print(f"   [{warn.code}] {warn.message}")
            if warn.chemin:
                print(f"      Chemin: {warn.chemin}")

    if rapport.infos:
        print(f"\n[INFO] ({len(rapport.infos)}):")
        for info in rapport.infos:
            print(f"   [{info.code}] {info.message}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Valide les données d'un acte notarial"
    )
    parser.add_argument(
        '--donnees', '-d',
        type=Path,
        required=True,
        help="Chemin vers le fichier de données JSON"
    )
    parser.add_argument(
        '--schema', '-s',
        type=Path,
        help="Chemin vers le schéma JSON"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help="Mode strict (toutes les erreurs sont bloquantes)"
    )
    parser.add_argument(
        '--complet',
        action='store_true',
        help="Validation complète avec règles avancées (conjoint, diagnostics, prix/m², cadastre)"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Sortie au format JSON"
    )

    args = parser.parse_args()

    if not args.donnees.exists():
        print(f"❌ Erreur: Fichier de données non trouvé: {args.donnees}")
        return 1

    # Charger les données
    with open(args.donnees, 'r', encoding='utf-8') as f:
        donnees = json.load(f)

    # Charger le schéma si fourni
    schema = {}
    if args.schema and args.schema.exists():
        with open(args.schema, 'r', encoding='utf-8') as f:
            schema = json.load(f)

    # Valider
    validateur = ValidateurActe(schema)
    if args.complet:
        rapport = validateur.valider_complet(donnees, strict=args.strict)
    else:
        rapport = validateur.valider(donnees, strict=args.strict)

    # Afficher
    if args.json:
        resultat = {
            'valide': rapport.valide,
            'erreurs': [
                {'code': e.code, 'message': e.message, 'chemin': e.chemin}
                for e in rapport.erreurs
            ],
            'avertissements': [
                {'code': w.code, 'message': w.message, 'chemin': w.chemin}
                for w in rapport.avertissements
            ],
            'infos': [
                {'code': i.code, 'message': i.message, 'chemin': i.chemin}
                for i in rapport.infos
            ]
        }
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
    else:
        afficher_rapport(rapport)

    return 0 if rapport.valide else 1


if __name__ == '__main__':
    exit(main())
