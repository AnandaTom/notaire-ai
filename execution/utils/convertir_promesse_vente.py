#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convertir_promesse_vente.py
===========================

Convertit les données d'une promesse de vente en données pour un acte de vente définitif.
Conserve automatiquement toutes les informations déjà collectées (parties, bien, prix, diagnostics).

Usage:
    python execution/utils/convertir_promesse_vente.py \
        --promesse exemples/donnees_promesse_exemple.json \
        --output .tmp/donnees_vente_depuis_promesse.json

    python execution/utils/convertir_promesse_vente.py \
        --promesse exemples/donnees_promesse_exemple.json \
        --complement complement_vente.json \
        --output .tmp/donnees_vente.json

Le fichier --complement (optionnel) peut contenir des champs spécifiques à la vente
(paiement détaillé, jouissance, fiscalité) qui ne sont pas dans la promesse.
"""

import json
import argparse
import sys
import copy
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def convertir_promesse_vers_vente(
    promesse: Dict[str, Any],
    complement: Optional[Dict[str, Any]] = None,
    date_vente: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convertit les données d'une promesse en données de vente.

    Args:
        promesse: Données de la promesse signée
        complement: Données complémentaires pour la vente (optionnel)
        date_vente: Date de signature de la vente (optionnel)

    Returns:
        Données formatées pour un acte de vente
    """
    vente = {}

    # === 1. Acte ===
    acte_promesse = promesse.get('acte', {})
    if date_vente:
        vente['acte'] = {
            **acte_promesse,
            'date': date_vente,
            'numero_repertoire': ''  # Nouveau numéro à attribuer
        }
    else:
        vente['acte'] = {
            **acte_promesse,
            'date': {
                'jour': datetime.now().day,
                'mois': datetime.now().month,
                'annee': datetime.now().year
            },
            'numero_repertoire': ''
        }

    # Renommer notaire_beneficiaire → notaire_assistant
    if 'notaire_beneficiaire' in acte_promesse:
        vente['acte']['notaire_assistant'] = acte_promesse['notaire_beneficiaire']

    # === 2. Parties : promettants → vendeurs, beneficiaires → acquereurs ===
    vente['vendeurs'] = _convertir_parties(
        promesse.get('promettants', promesse.get('vendeurs', []))
    )
    vente['acquereurs'] = _convertir_parties(
        promesse.get('beneficiaires', promesse.get('acquereurs', []))
    )

    # === 3. Quotités ===
    if 'quotites_vendues' in promesse:
        vente['quotites_vendues'] = copy.deepcopy(promesse['quotites_vendues'])
    elif len(vente['vendeurs']) == 1:
        vente['quotites_vendues'] = [{
            'personne_index': 0,
            'quotite': 'la totalité',
            'pourcentage': 100,
            'type_propriete': 'pleine_propriete'
        }]

    if 'quotites_acquises' in promesse:
        vente['quotites_acquises'] = copy.deepcopy(promesse['quotites_acquises'])
    elif len(vente['acquereurs']) == 1:
        vente['quotites_acquises'] = [{
            'personne_index': 0,
            'quotite': 'la totalité',
            'pourcentage': 100,
            'type_propriete': 'pleine_propriete'
        }]

    # === 4. Bien (copie directe) ===
    if 'bien' in promesse:
        vente['bien'] = copy.deepcopy(promesse['bien'])
    elif 'biens' in promesse and promesse['biens']:
        # Multi-biens : prendre le premier comme bien principal
        vente['bien'] = copy.deepcopy(promesse['biens'][0])

    # === 5. Prix ===
    vente['prix'] = copy.deepcopy(promesse.get('prix', {}))

    # === 6. Copropriété ===
    if 'copropriete' in promesse:
        vente['copropriete'] = copy.deepcopy(promesse['copropriete'])

    # === 7. Diagnostics ===
    if 'diagnostics' in promesse:
        vente['diagnostics'] = copy.deepcopy(promesse['diagnostics'])

    # === 8. Origine de propriété ===
    if 'origine_propriete' in promesse:
        vente['origine_propriete'] = copy.deepcopy(promesse['origine_propriete'])

    # === 9. Avant-contrat (référence à la promesse) ===
    date_promesse = promesse.get('acte', {}).get('date', {})
    notaire_promesse = promesse.get('acte', {}).get('notaire', {})

    vente['avant_contrat'] = {
        'type': 'promesse_unilaterale',
        'date': _formater_date_texte(date_promesse),
        'notaire': f"Maître {notaire_promesse.get('prenom', '')} {notaire_promesse.get('nom', '')}".strip()
    }

    # === 10. Paiement (depuis financement promesse ou complément) ===
    financement = promesse.get('financement', {})
    condition_pret = promesse.get('condition_suspensive_pret', {})

    vente['paiement'] = {
        'mode': financement.get('mode', 'mixte'),
        'fonds_personnels': financement.get('fonds_personnels', 0),
        'prets': []
    }

    # Construire les prêts depuis les conditions suspensives
    if condition_pret.get('existe'):
        vente['paiement']['prets'] = [{
            'etablissement': {'nom': 'À préciser'},
            'montant': condition_pret.get('montant_maximal', financement.get('fonds_empruntes', 0)),
            'duree_mois': condition_pret.get('duree_maximale_annees', 20) * 12,
            'taux': condition_pret.get('taux_maximal', 0),
            'type_taux': 'fixe',
            'type_garantie': 'hypotheque_legale_preteur'
        }]
    elif financement.get('fonds_empruntes', 0) > 0:
        vente['paiement']['prets'] = [{
            'etablissement': {'nom': 'À préciser'},
            'montant': financement['fonds_empruntes'],
            'duree_mois': 240,
            'taux': 0,
            'type_taux': 'fixe'
        }]

    # === 11. Jouissance ===
    vente['jouissance'] = {
        'date_propriete': 'ce jour',
        'date_jouissance': 'ce jour',
        'jouissance_anticipee': False
    }

    # === 12. Fiscalité ===
    vente['fiscalite'] = copy.deepcopy(promesse.get('fiscalite', {}))
    if not vente['fiscalite']:
        vente['fiscalite'] = {
            'plus_value': {
                'exoneration': False
            }
        }

    # === 13. Urbanisme ===
    if 'urbanisme' in promesse:
        vente['urbanisme'] = copy.deepcopy(promesse['urbanisme'])

    # === 14. Meubles ===
    if 'meubles' in promesse:
        vente['meubles'] = copy.deepcopy(promesse['meubles'])
    if 'mobilier' in promesse and promesse['mobilier'].get('existe'):
        vente['meubles'] = {
            'inclus': True,
            'liste': [m.get('designation', '') for m in promesse['mobilier'].get('liste', [])],
            'valeur': promesse['mobilier'].get('prix_total')
        }

    # === 15. Publication ===
    vente['publication'] = copy.deepcopy(promesse.get('publication', {}))
    if not vente['publication']:
        vente['publication'] = {
            'service_publicite_fonciere': ''
        }

    # === 16. Travaux ===
    if 'travaux_recents' in promesse:
        vente['travaux'] = {
            'existence': promesse['travaux_recents'].get('existe', False),
            'recents': promesse['travaux_recents'].get('liste', []),
            'garantie_decennale': {
                'applicable': any(
                    t.get('assurance_decennale', False)
                    for t in promesse['travaux_recents'].get('liste', [])
                )
            }
        }

    # === 17. Négociation ===
    if 'negociation' in promesse:
        vente['negociation'] = copy.deepcopy(promesse['negociation'])

    # === 18. RGPD ===
    vente['rgpd'] = promesse.get('rgpd', {
        'consentement': True,
        'traitement_donnees': 'Notaire responsable de traitement',
        'duree_conservation': '10 ans'
    })

    # === 19. Appliquer compléments ===
    if complement:
        vente = _fusionner_profond(vente, complement)

    return vente


def _convertir_parties(parties: List[Dict]) -> List[Dict]:
    """Convertit les parties en supprimant les champs spécifiques promesse."""
    result = []
    for p in parties:
        partie = copy.deepcopy(p)
        # Supprimer les champs méta
        partie.pop('_comment', None)
        result.append(partie)
    return result


def _formater_date_texte(date_obj: Dict) -> str:
    """Formate un objet date {jour, mois, annee} en texte."""
    if not date_obj:
        return ''
    mois_noms = [
        '', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]
    jour = date_obj.get('jour', 1)
    mois = date_obj.get('mois', 1)
    annee = date_obj.get('annee', 2026)
    return f"{jour} {mois_noms[mois]} {annee}"


def _fusionner_profond(base: Dict, complement: Dict) -> Dict:
    """Fusionne deux dictionnaires en profondeur (le complément écrase la base)."""
    resultat = copy.deepcopy(base)
    for cle, valeur in complement.items():
        if cle in resultat and isinstance(resultat[cle], dict) and isinstance(valeur, dict):
            resultat[cle] = _fusionner_profond(resultat[cle], valeur)
        else:
            resultat[cle] = copy.deepcopy(valeur)
    return resultat


def analyser_conversion(promesse: Dict, vente: Dict) -> Dict[str, Any]:
    """
    Analyse la conversion et retourne un rapport de couverture.

    Returns:
        Dict avec les champs conservés, ajoutés, et à compléter
    """
    rapport = {
        'champs_conserves': [],
        'champs_ajoutes': [],
        'champs_a_completer': [],
        'completude': 0
    }

    # Champs attendus pour une vente
    champs_vente_requis = [
        'acte', 'vendeurs', 'acquereurs', 'bien', 'prix',
        'paiement', 'jouissance', 'fiscalite', 'publication'
    ]
    champs_vente_optionnels = [
        'copropriete', 'diagnostics', 'origine_propriete', 'avant_contrat',
        'urbanisme', 'meubles', 'travaux', 'negociation', 'quotites_vendues',
        'quotites_acquises', 'indivision'
    ]

    for champ in champs_vente_requis:
        if champ in vente and vente[champ]:
            if champ in promesse or champ in ['vendeurs', 'acquereurs', 'paiement', 'jouissance']:
                rapport['champs_conserves'].append(champ)
            else:
                rapport['champs_ajoutes'].append(champ)
        else:
            rapport['champs_a_completer'].append(champ)

    for champ in champs_vente_optionnels:
        if champ in vente and vente[champ]:
            rapport['champs_conserves'].append(champ)

    total_requis = len(champs_vente_requis)
    remplis = total_requis - len([c for c in rapport['champs_a_completer'] if c in champs_vente_requis])
    rapport['completude'] = round((remplis / total_requis) * 100) if total_requis > 0 else 0

    return rapport


def main():
    parser = argparse.ArgumentParser(
        description="Convertit une promesse de vente en données pour acte de vente définitif"
    )
    parser.add_argument(
        '--promesse', '-p',
        type=Path,
        required=True,
        help="Fichier JSON de la promesse"
    )
    parser.add_argument(
        '--complement', '-c',
        type=Path,
        default=None,
        help="Fichier JSON de complément (paiement détaillé, jouissance, etc.)"
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help="Fichier JSON de sortie pour la vente"
    )
    parser.add_argument(
        '--json-rapport',
        action='store_true',
        help="Afficher le rapport de conversion en JSON"
    )

    args = parser.parse_args()

    if not args.promesse.exists():
        print(f"Erreur: Fichier promesse introuvable: {args.promesse}")
        return 1

    # Charger la promesse
    with open(args.promesse, 'r', encoding='utf-8') as f:
        promesse = json.load(f)

    # Charger le complément si fourni
    complement = None
    if args.complement and args.complement.exists():
        with open(args.complement, 'r', encoding='utf-8') as f:
            complement = json.load(f)

    # Convertir
    print("=" * 60)
    print("CONVERSION PROMESSE -> VENTE")
    print("=" * 60)

    vente = convertir_promesse_vers_vente(promesse, complement)

    # Analyser
    rapport = analyser_conversion(promesse, vente)

    print(f"\n  Complétude: {rapport['completude']}%")
    print(f"  Champs conservés ({len(rapport['champs_conserves'])}): {', '.join(rapport['champs_conserves'])}")
    if rapport['champs_ajoutes']:
        print(f"  Champs ajoutés ({len(rapport['champs_ajoutes'])}): {', '.join(rapport['champs_ajoutes'])}")
    if rapport['champs_a_completer']:
        print(f"  A compléter ({len(rapport['champs_a_completer'])}): {', '.join(rapport['champs_a_completer'])}")

    # Vendeurs et acquéreurs
    nb_vendeurs = len(vente.get('vendeurs', []))
    nb_acquereurs = len(vente.get('acquereurs', []))
    prix = vente.get('prix', {}).get('montant', 0)
    print(f"\n  Vendeur(s): {nb_vendeurs}")
    print(f"  Acquéreur(s): {nb_acquereurs}")
    print(f"  Prix: {prix:,.0f} EUR")

    # Sauvegarder
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(vente, f, ensure_ascii=False, indent=2)

    print(f"\n  Fichier vente: {args.output}")

    if args.json_rapport:
        print(f"\n  Rapport JSON:")
        print(json.dumps(rapport, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("CONVERSION TERMINEE")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    try:
        exit(main())
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
