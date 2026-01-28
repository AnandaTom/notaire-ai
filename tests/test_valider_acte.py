#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_valider_acte.py
--------------------
Tests unitaires pour valider_acte.py - Validation des données d'actes notariaux.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Ajouter le répertoire execution au path
PROJECT_ROOT = Path(__file__).parent.parent
EXECUTION_DIR = PROJECT_ROOT / "execution"
sys.path.insert(0, str(EXECUTION_DIR))

from execution.core.valider_acte import (
    ValidateurActe,
    NiveauErreur,
    ResultatValidation,
    RapportValidation,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def validateur():
    """Crée un validateur avec schéma vide."""
    return ValidateurActe({})


@pytest.fixture
def donnees_minimales():
    """Données minimales valides pour un acte."""
    return {
        "acte": {
            "date": {"jour": 15, "mois": 3, "annee": 2025},
            "reference": "TEST-001",
            "notaire": {
                "nom": "DUPONT",
                "prenom": "Jean",
                "ville": "Lyon",
                "adresse": "1 rue du Test, 69001 Lyon"
            }
        },
        "vendeurs": [{
            "nom": "VENDEUR",
            "prenoms": "Pierre",
            "adresse": "10 rue des Vendeurs, 69000 Lyon",
            "date_naissance": "15/06/1970",
            "lieu_naissance": "Lyon",
            "situation_matrimoniale": {
                "statut": "celibataire"
            }
        }],
        "acquereurs": [{
            "nom": "ACQUEREUR",
            "prenoms": "Marie",
            "adresse": "20 rue des Acheteurs, 69000 Lyon",
            "date_naissance": "20/08/1985",
            "lieu_naissance": "Paris",
            "situation_matrimoniale": {
                "statut": "celibataire"
            }
        }],
        "bien": {
            "adresse": {
                "numero": "15",
                "voie": "rue du Bien",
                "code_postal": "69001",
                "commune": "Lyon"
            },
            "lots": [{
                "numero": 1,
                "description": "Appartement T3"
            }]
        },
        "prix": {
            "montant": 250000
        }
    }


@pytest.fixture
def donnees_avec_quotites(donnees_minimales):
    """Données avec quotités définies."""
    donnees = donnees_minimales.copy()
    donnees["vendeurs"].append({
        "nom": "VENDEUR2",
        "prenoms": "Paul",
        "adresse": "10 rue des Vendeurs, 69000 Lyon",
        "date_naissance": "10/01/1965",
        "lieu_naissance": "Lyon",
        "situation_matrimoniale": {"statut": "celibataire"}
    })
    donnees["quotites_vendues"] = [
        {"nom": "VENDEUR Pierre", "pourcentage": 50},
        {"nom": "VENDEUR2 Paul", "pourcentage": 50}
    ]
    donnees["quotites_acquises"] = [
        {"nom": "ACQUEREUR Marie", "pourcentage": 100}
    ]
    return donnees


# =============================================================================
# TESTS RAPPORT VALIDATION
# =============================================================================

class TestRapportValidation:
    """Tests pour la classe RapportValidation."""

    def test_rapport_initial_valide(self):
        """Un rapport initial est valide."""
        rapport = RapportValidation()
        assert rapport.valide is True
        assert len(rapport.erreurs) == 0

    def test_ajout_erreur(self):
        """L'ajout d'une erreur invalide le rapport."""
        rapport = RapportValidation()
        erreur = ResultatValidation(
            niveau=NiveauErreur.ERREUR,
            code="TEST",
            message="Test erreur"
        )
        rapport.ajouter(erreur)

        assert rapport.valide is False
        assert len(rapport.erreurs) == 1

    def test_ajout_avertissement(self):
        """L'ajout d'un avertissement ne modifie pas la validité."""
        rapport = RapportValidation()
        avertissement = ResultatValidation(
            niveau=NiveauErreur.AVERTISSEMENT,
            code="TEST_WARN",
            message="Test avertissement"
        )
        rapport.ajouter(avertissement)

        assert rapport.valide is True
        assert len(rapport.avertissements) == 1


# =============================================================================
# TESTS VALIDATION DE BASE
# =============================================================================

class TestValidationBase:
    """Tests pour les validations de base."""

    def test_donnees_valides(self, validateur, donnees_minimales):
        """Données minimales valides."""
        rapport = validateur.valider(donnees_minimales)
        # Peut avoir des avertissements mais pas d'erreurs bloquantes
        # sur les champs obligatoires
        assert rapport.valide is True or len(rapport.erreurs) == 0

    def test_vendeurs_manquants(self, validateur):
        """Erreur si vendeurs manquants."""
        donnees = {
            "acte": {"date": "2025-01-01", "notaire": {}},
            "acquereurs": [{"nom": "TEST"}],
            "bien": {},
            "prix": {"montant": 100000}
        }
        rapport = validateur.valider(donnees)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "CHAMP_REQUIS_MANQUANT" in codes_erreurs or "LISTE_VIDE" in codes_erreurs

    def test_prix_zero(self, validateur, donnees_minimales):
        """Erreur si prix à zéro."""
        donnees_minimales["prix"]["montant"] = 0
        rapport = validateur.valider(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "PRIX_INVALIDE" in codes_erreurs

    def test_prix_negatif(self, validateur, donnees_minimales):
        """Erreur si prix négatif."""
        donnees_minimales["prix"]["montant"] = -50000
        rapport = validateur.valider(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "PRIX_INVALIDE" in codes_erreurs


# =============================================================================
# TESTS VALIDATION QUOTITÉS CROISÉES (v1.5.1)
# =============================================================================

class TestValidationQuotitesCroisees:
    """Tests pour la validation des quotités croisées."""

    def test_quotites_valides(self, validateur, donnees_avec_quotites):
        """Quotités valides (100% chaque côté)."""
        rapport = validateur.valider_complet(donnees_avec_quotites)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "QUOTITES_VENDUES_INVALIDES" not in codes_erreurs
        assert "QUOTITES_ACQUISES_INVALIDES" not in codes_erreurs

    def test_quotites_vendues_incomplet(self, validateur, donnees_avec_quotites):
        """Erreur si quotités vendues ne totalisent pas 100%."""
        donnees_avec_quotites["quotites_vendues"] = [
            {"nom": "VENDEUR Pierre", "pourcentage": 40},
            {"nom": "VENDEUR2 Paul", "pourcentage": 40}
        ]
        rapport = validateur.valider_complet(donnees_avec_quotites)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "QUOTITES_VENDUES_INVALIDES" in codes_erreurs

    def test_quotites_acquises_excess(self, validateur, donnees_avec_quotites):
        """Erreur si quotités acquises dépassent 100%."""
        donnees_avec_quotites["quotites_acquises"] = [
            {"nom": "ACQUEREUR Marie", "pourcentage": 110}
        ]
        rapport = validateur.valider_complet(donnees_avec_quotites)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "QUOTITES_ACQUISES_INVALIDES" in codes_erreurs

    def test_quotites_mismatch_vendeurs(self, validateur, donnees_avec_quotites):
        """Avertissement si nombre de quotités ≠ nombre de vendeurs."""
        # 2 vendeurs mais 3 quotités
        donnees_avec_quotites["quotites_vendues"].append(
            {"nom": "VENDEUR3", "pourcentage": 0}
        )
        rapport = validateur.valider_complet(donnees_avec_quotites)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "QUOTITES_VENDEURS_MISMATCH" in codes_warn

    def test_quotites_avec_fractions(self, validateur, donnees_minimales):
        """Test avec quotités en fractions."""
        donnees_minimales["vendeurs"].append({
            "nom": "VENDEUR2",
            "prenoms": "Paul",
            "adresse": "Test",
            "date_naissance": "10/01/1965",
            "lieu_naissance": "Lyon",
            "situation_matrimoniale": {"statut": "celibataire"}
        })
        donnees_minimales["quotites_vendues"] = [
            {"nom": "VENDEUR Pierre", "fraction": "1/2"},
            {"nom": "VENDEUR2 Paul", "fraction": "1/2"}
        ]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "QUOTITES_VENDUES_INVALIDES" not in codes_erreurs

    def test_multi_vendeurs_sans_quotites(self, validateur, donnees_minimales):
        """Avertissement si plusieurs vendeurs sans quotités."""
        donnees_minimales["vendeurs"].append({
            "nom": "VENDEUR2",
            "prenoms": "Paul",
            "adresse": "Test",
            "date_naissance": "10/01/1965",
            "lieu_naissance": "Lyon",
            "situation_matrimoniale": {"statut": "celibataire"}
        })
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "QUOTITES_VENDUES_MANQUANTES" in codes_warn


# =============================================================================
# TESTS VALIDATION CADASTRE (v1.5.1)
# =============================================================================

class TestValidationCadastre:
    """Tests pour la validation du cadastre."""

    def test_cadastre_valide(self, validateur, donnees_minimales):
        """Cadastre valide."""
        donnees_minimales["bien"]["cadastre"] = [{
            "section": "AB",
            "numero": "123",
            "commune": "Lyon"
        }]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "SECTION_CADASTRALE_MANQUANTE" not in codes_erreurs
        assert "NUMERO_PARCELLE_MANQUANT" not in codes_erreurs

    def test_section_manquante(self, validateur, donnees_minimales):
        """Erreur si section cadastrale manquante."""
        donnees_minimales["bien"]["cadastre"] = [{
            "numero": "123",
            "commune": "Lyon"
        }]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "SECTION_CADASTRALE_MANQUANTE" in codes_erreurs

    def test_numero_parcelle_manquant(self, validateur, donnees_minimales):
        """Erreur si numéro de parcelle manquant."""
        donnees_minimales["bien"]["cadastre"] = [{
            "section": "AB",
            "commune": "Lyon"
        }]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "NUMERO_PARCELLE_MANQUANT" in codes_erreurs

    def test_section_format_inhabituel(self, validateur, donnees_minimales):
        """Avertissement si format de section inhabituel."""
        donnees_minimales["bien"]["cadastre"] = [{
            "section": "ABC123",  # Format inhabituel
            "numero": "123",
            "commune": "Lyon"
        }]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "SECTION_FORMAT_INHABITUEL" in codes_warn

    def test_commune_differente(self, validateur, donnees_minimales):
        """Avertissement si commune cadastrale ≠ adresse."""
        donnees_minimales["bien"]["cadastre"] = [{
            "section": "AB",
            "numero": "123",
            "commune": "Villeurbanne"  # ≠ Lyon dans adresse
        }]
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "COMMUNE_CADASTRE_DIFFERENTE" in codes_warn

    def test_cadastre_absent(self, validateur, donnees_minimales):
        """Avertissement si cadastre absent."""
        donnees_minimales["bien"].pop("cadastre", None)
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "CADASTRE_MANQUANT" in codes_warn


# =============================================================================
# TESTS VALIDATION INTERVENTION CONJOINT (v1.5.0)
# =============================================================================

class TestValidationConjoint:
    """Tests pour la validation de l'intervention du conjoint."""

    def test_celibataire_ok(self, validateur, donnees_minimales):
        """Pas d'erreur pour un célibataire."""
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "CONJOINT_NON_INTERVENANT" not in codes_erreurs

    def test_marie_communaute_sans_conjoint(self, validateur, donnees_minimales):
        """Erreur si marié en communauté sans intervention conjoint."""
        donnees_minimales["vendeurs"][0]["situation_matrimoniale"] = {
            "statut": "marie",
            "regime_matrimonial": "communaute_legale",
            "conjoint": {
                "nom": "EPOUSE",
                "prenom": "Jeanne",
                "intervient": False
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "CONJOINT_NON_INTERVENANT" in codes_erreurs

    def test_marie_communaute_avec_conjoint(self, validateur, donnees_minimales):
        """Pas d'erreur si conjoint intervient."""
        donnees_minimales["vendeurs"][0]["situation_matrimoniale"] = {
            "statut": "marie",
            "regime_matrimonial": "communaute_legale",
            "conjoint": {
                "nom": "EPOUSE",
                "prenom": "Jeanne",
                "intervient": True
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "CONJOINT_NON_INTERVENANT" not in codes_erreurs

    def test_marie_separation_biens(self, validateur, donnees_minimales):
        """Pas d'erreur pour séparation de biens."""
        donnees_minimales["vendeurs"][0]["situation_matrimoniale"] = {
            "statut": "marie",
            "regime_matrimonial": "separation_biens",
            "conjoint": {
                "nom": "EPOUSE",
                "prenom": "Jeanne",
                "intervient": False
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "CONJOINT_NON_INTERVENANT" not in codes_erreurs


# =============================================================================
# TESTS VALIDATION DIAGNOSTICS (v1.5.0)
# =============================================================================

class TestValidationDiagnostics:
    """Tests pour la validation des diagnostics."""

    def test_dpe_valide(self, validateur, donnees_minimales):
        """DPE valide (moins de 10 ans)."""
        donnees_minimales["diagnostics"] = {
            "dpe": {
                "date": (datetime.now() - timedelta(days=365)).strftime("%d/%m/%Y"),
                "classe_energie": "D"
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "DIAGNOSTIC_EXPIRE_DPE" not in codes_erreurs

    def test_dpe_expire(self, validateur, donnees_minimales):
        """Erreur si DPE expiré (> 10 ans)."""
        donnees_minimales["diagnostics"] = {
            "dpe": {
                "date": "01/01/2010",  # > 10 ans
                "classe_energie": "D"
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "DIAGNOSTIC_EXPIRE_DPE" in codes_erreurs

    def test_passoire_energetique_sans_audit(self, validateur, donnees_minimales):
        """Erreur si DPE F/G sans audit énergétique."""
        donnees_minimales["diagnostics"] = {
            "dpe": {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "classe_energie": "G"
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "AUDIT_ENERGETIQUE_MANQUANT" in codes_erreurs

    def test_passoire_avec_audit(self, validateur, donnees_minimales):
        """Pas d'erreur si audit présent pour DPE F/G."""
        donnees_minimales["diagnostics"] = {
            "dpe": {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "classe_energie": "F"
            },
            "audit_energetique": {
                "date": datetime.now().strftime("%d/%m/%Y"),
                "diagnostiqueur": "Expert Test"
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        audit_erreurs = [c for c in codes_erreurs if "AUDIT" in c]
        assert len(audit_erreurs) == 0


# =============================================================================
# TESTS VALIDATION PRIX COHÉRENT (v1.5.0)
# =============================================================================

class TestValidationPrixCoherent:
    """Tests pour la validation de la cohérence du prix."""

    def test_prix_m2_normal(self, validateur, donnees_minimales):
        """Prix/m² dans la normale."""
        donnees_minimales["bien"]["superficie_carrez"] = {"superficie_m2": 50}
        donnees_minimales["prix"]["montant"] = 150000  # 3000€/m²
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "PRIX_M2_ANORMALEMENT_BAS" not in codes_warn
        assert "PRIX_M2_ANORMALEMENT_HAUT" not in codes_warn

    def test_prix_m2_bas(self, validateur, donnees_minimales):
        """Avertissement si prix/m² trop bas."""
        donnees_minimales["bien"]["superficie_carrez"] = {"superficie_m2": 100}
        donnees_minimales["prix"]["montant"] = 30000  # 300€/m² - trop bas
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "PRIX_M2_ANORMALEMENT_BAS" in codes_warn

    def test_prix_m2_haut(self, validateur, donnees_minimales):
        """Avertissement si prix/m² trop élevé."""
        donnees_minimales["bien"]["superficie_carrez"] = {"superficie_m2": 50}
        donnees_minimales["prix"]["montant"] = 1000000  # 20000€/m² - élevé hors Paris
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "PRIX_M2_ANORMALEMENT_HAUT" in codes_warn

    def test_prix_m2_paris(self, validateur, donnees_minimales):
        """Seuils différents pour Paris."""
        donnees_minimales["bien"]["adresse"]["code_postal"] = "75008"
        donnees_minimales["bien"]["superficie_carrez"] = {"superficie_m2": 50}
        donnees_minimales["prix"]["montant"] = 750000  # 15000€/m² - normal à Paris
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "PRIX_M2_ANORMALEMENT_HAUT" not in codes_warn


# =============================================================================
# TESTS VALIDATION PLUS-VALUE (v1.5.1)
# =============================================================================

class TestValidationPlusValue:
    """Tests pour la validation de la plus-value immobilière."""

    def test_exoneration_30_ans(self, validateur, donnees_minimales):
        """Info si bien détenu > 30 ans."""
        donnees_minimales["origine_propriete"] = {
            "date": {"jour": 1, "mois": 1, "annee": 1990}
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_info = [i.code for i in rapport.infos]
        assert "EXONERATION_30_ANS" in codes_info

    def test_plus_value_non_renseignee(self, validateur, donnees_minimales):
        """Avertissement si plus-value non renseignée pour bien récent."""
        donnees_minimales["origine_propriete"] = {
            "date": {"jour": 1, "mois": 1, "annee": 2020}
        }
        donnees_minimales["bien"]["usage"] = "investissement"
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "PLUS_VALUE_NON_RENSEIGNEE" in codes_warn

    def test_motif_exoneration_manquant(self, validateur, donnees_minimales):
        """Avertissement si exonération sans motif."""
        donnees_minimales["plus_value"] = {
            "exoneration": True
            # Pas de motif_exoneration
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "MOTIF_EXONERATION_MANQUANT" in codes_warn


# =============================================================================
# TESTS VALIDATION DATES PROMESSE (v1.5.0)
# =============================================================================

class TestValidationDatesPromesse:
    """Tests pour la validation des dates de promesse."""

    def test_delai_realisation_court(self, validateur, donnees_minimales):
        """Avertissement si délai de réalisation trop court."""
        date_acte = datetime.now()
        delai = date_acte + timedelta(days=20)

        donnees_minimales["acte"]["date"] = {
            "jour": date_acte.day,
            "mois": date_acte.month,
            "annee": date_acte.year
        }
        donnees_minimales["delai_realisation"] = delai.strftime("%d/%m/%Y")
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "DELAI_REALISATION_COURT" in codes_warn

    def test_date_pret_apres_realisation(self, validateur, donnees_minimales):
        """Avertissement si date prêt > délai réalisation."""
        date_acte = datetime.now()
        delai = date_acte + timedelta(days=90)
        date_pret = date_acte + timedelta(days=120)

        donnees_minimales["acte"]["date"] = {
            "jour": date_acte.day,
            "mois": date_acte.month,
            "annee": date_acte.year
        }
        donnees_minimales["delai_realisation"] = delai.strftime("%d/%m/%Y")
        donnees_minimales["conditions_suspensives"] = {
            "pret": {
                "date_limite_obtention": date_pret.strftime("%d/%m/%Y")
            }
        }
        rapport = validateur.valider_complet(donnees_minimales)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "DATE_PRET_APRES_REALISATION" in codes_warn


# =============================================================================
# TESTS VALIDATION PERSONNES
# =============================================================================

class TestValidationPersonnes:
    """Tests pour la validation des personnes."""

    def test_vendeur_mineur(self, validateur, donnees_minimales):
        """Erreur si vendeur mineur."""
        donnees_minimales["vendeurs"][0]["date_naissance"] = datetime.now().strftime("%d/%m/%Y")
        rapport = validateur.valider_complet(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "MINEUR" in codes_erreurs

    def test_nom_manquant(self, validateur, donnees_minimales):
        """Erreur si nom manquant."""
        donnees_minimales["vendeurs"][0]["nom"] = ""
        rapport = validateur.valider(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "NOM_MANQUANT" in codes_erreurs


# =============================================================================
# TESTS EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_donnees_vides(self, validateur):
        """Données complètement vides."""
        rapport = validateur.valider({})
        assert rapport.valide is False
        assert len(rapport.erreurs) > 0

    def test_donnees_none_values(self, validateur, donnees_minimales):
        """Données avec valeurs None."""
        donnees_minimales["vendeurs"][0]["nom"] = None
        rapport = validateur.valider(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "NOM_MANQUANT" in codes_erreurs

    def test_liste_vide_vendeurs(self, validateur, donnees_minimales):
        """Liste de vendeurs vide."""
        donnees_minimales["vendeurs"] = []
        rapport = validateur.valider(donnees_minimales)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "LISTE_VIDE" in codes_erreurs


# =============================================================================
# TESTS VALIDATION PERSONNES MORALES (v1.5.1)
# =============================================================================

class TestValidationPersonnesMorales:
    """Tests pour la validation des personnes morales."""

    @pytest.fixture
    def sci_valide(self):
        """SCI valide pour les tests."""
        return {
            "type_personne": "morale",
            "forme_juridique": "SCI",
            "denomination": "SCI LES OLIVIERS",
            "siege_social": {
                "adresse": "10 rue des Sociétés",
                "code_postal": "69001",
                "ville": "Lyon"
            },
            "siren": "123456789",
            "representant": {
                "qualite": "Gérant",
                "civilite": "Monsieur",
                "nom": "DUPONT",
                "prenoms": "Jean",
                "pouvoir": {
                    "source": "statuts"
                }
            }
        }

    @pytest.fixture
    def donnees_avec_sci(self, donnees_minimales, sci_valide):
        """Données avec une SCI comme vendeur."""
        donnees = donnees_minimales.copy()
        donnees["vendeurs"] = [sci_valide]
        return donnees

    def test_sci_valide(self, validateur, donnees_avec_sci):
        """SCI correctement remplie."""
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "DENOMINATION_MANQUANTE" not in codes_erreurs
        assert "SIREN_MANQUANT" not in codes_erreurs
        assert "REPRESENTANT_MANQUANT" not in codes_erreurs

    def test_denomination_manquante(self, validateur, donnees_avec_sci):
        """Erreur si dénomination manquante."""
        donnees_avec_sci["vendeurs"][0]["denomination"] = ""
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "DENOMINATION_MANQUANTE" in codes_erreurs

    def test_siren_manquant(self, validateur, donnees_avec_sci):
        """Erreur si SIREN manquant."""
        donnees_avec_sci["vendeurs"][0]["siren"] = ""
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "SIREN_MANQUANT" in codes_erreurs

    def test_siren_format_invalide(self, validateur, donnees_avec_sci):
        """Erreur si format SIREN invalide."""
        donnees_avec_sci["vendeurs"][0]["siren"] = "12345"  # Trop court
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "SIREN_INVALIDE" in codes_erreurs

    def test_representant_manquant(self, validateur, donnees_avec_sci):
        """Erreur si représentant manquant."""
        # Un dict vide est falsy en Python, donc REPRESENTANT_MANQUANT
        donnees_avec_sci["vendeurs"][0]["representant"] = {}
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "REPRESENTANT_MANQUANT" in codes_erreurs

    def test_sarl_sans_rcs(self, validateur, donnees_avec_sci):
        """Avertissement si SARL sans RCS."""
        donnees_avec_sci["vendeurs"][0]["forme_juridique"] = "SARL"
        donnees_avec_sci["vendeurs"][0].pop("rcs", None)
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "RCS_MANQUANT" in codes_warn

    def test_forme_juridique_inconnue(self, validateur, donnees_avec_sci):
        """Avertissement si forme juridique non reconnue."""
        donnees_avec_sci["vendeurs"][0]["forme_juridique"] = "FORME_INCONNUE"
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "FORME_JURIDIQUE_INCONNUE" in codes_warn

    def test_pouvoirs_non_specifies(self, validateur, donnees_avec_sci):
        """Avertissement si pouvoirs du représentant non spécifiés."""
        donnees_avec_sci["vendeurs"][0]["representant"]["pouvoir"] = {}
        rapport = validateur.valider_complet(donnees_avec_sci)

        codes_warn = [w.code for w in rapport.avertissements]
        assert "POUVOIRS_NON_SPECIFIES" in codes_warn

    def test_mixte_physique_morale(self, validateur, donnees_minimales, sci_valide):
        """Vente par personne physique et morale ensemble."""
        donnees = donnees_minimales.copy()
        # Ajouter une SCI comme co-vendeur
        donnees["vendeurs"].append(sci_valide)
        rapport = validateur.valider_complet(donnees)

        # Pas d'erreur spécifique au mixte
        codes_erreurs = [e.code for e in rapport.erreurs]
        assert "DENOMINATION_MANQUANTE" not in codes_erreurs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
