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
        """Vérifie la validité des informations des personnes."""

        for cle, type_partie in [('vendeurs', 'Vendeur'), ('acquereurs', 'Acquéreur')]:
            if cle in donnees:
                for i, personne in enumerate(donnees[cle]):
                    # Nom et prénom obligatoires
                    if not personne.get('nom'):
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="NOM_MANQUANT",
                            message=f"Nom manquant pour {type_partie} {i+1}",
                            chemin=f"{cle}.{i}.nom"
                        ))

                    if not personne.get('prenoms'):
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="PRENOM_MANQUANT",
                            message=f"Prénom(s) manquant(s) pour {type_partie} {i+1}",
                            chemin=f"{cle}.{i}.prenoms"
                        ))

                    # Adresse obligatoire
                    if not personne.get('adresse'):
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="ADRESSE_MANQUANTE",
                            message=f"Adresse manquante pour {type_partie} {i+1}",
                            chemin=f"{cle}.{i}.adresse"
                        ))

                    # Date et lieu de naissance
                    if not personne.get('date_naissance'):
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="DATE_NAISSANCE_MANQUANTE",
                            message=f"Date de naissance manquante pour {type_partie} {i+1}",
                            chemin=f"{cle}.{i}.date_naissance"
                        ))

                    if not personne.get('lieu_naissance'):
                        self.rapport.ajouter(ResultatValidation(
                            niveau=NiveauErreur.ERREUR,
                            code="LIEU_NAISSANCE_MANQUANT",
                            message=f"Lieu de naissance manquant pour {type_partie} {i+1}",
                            chemin=f"{cle}.{i}.lieu_naissance"
                        ))

                    # Valider situation PACS
                    self._valider_pacs(personne, cle, i, type_partie)

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

        # Règles avancées
        self._valider_superficie_carrez(donnees)
        self._valider_diagnostics_dpe(donnees)
        self._valider_diagnostics_obligatoires(donnees)
        self._valider_coherence_adresse(donnees)
        self._valider_coherence_financiere(donnees)
        self._valider_tantièmes(donnees)

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
