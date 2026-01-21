#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générer des données minimales valides pour les tests
Ajoute automatiquement les sections obligatoires manquantes
"""
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def ajouter_sections_minimales(data: dict) -> dict:
    """Ajoute les sections minimales requises par le template Vague 3"""

    # Urbanisme (section ajoutée en Vague 3)
    if 'urbanisme' not in data:
        data['urbanisme'] = {
            'plan_local_urbanisme': {
                'zonage': 'UAa',
                'autorise_usage': True
            },
            'droit_preemption': {
                'applicable': False
            }
        }

    # Indivision (section ajoutée en Vague 3)
    if 'indivision' not in data:
        data['indivision'] = {
            'regime': 'indivision_simple',
            'acquereurs': []
        }
        # Créer acquereurs d'indivision basés sur acquereurs principaux
        for idx, acq in enumerate(data.get('acquereurs', [])):
            data['indivision']['acquereurs'].append({
                'civilite': acq['civilite'],
                'nom': acq['nom'],
                'prenom': acq.get('prenoms', '').split()[0] if acq.get('prenoms') else acq.get('prenom', ''),
                'quotite': data.get('quotites_acquises', [{}])[idx].get('quotite', 'la moitié'),
                'pourcentage': data.get('quotites_acquises', [{}])[idx].get('pourcentage', 50),
                'financement': {
                    'apport_personnel': data.get('paiement', {}).get('fonds_personnels', 0),
                    'emprunt': {
                        'montant': sum(p.get('montant', 0) for p in data.get('paiement', {}).get('prets', [])) / len(data.get('acquereurs', [1])),
                        'taux': data.get('paiement', {}).get('prets', [{}])[0].get('taux', 0) if data.get('paiement', {}).get('prets') else 0,
                        'duree': data.get('paiement', {}).get('prets', [{}])[0].get('duree_mois', 0) if data.get('paiement', {}).get('prets') else 0
                    }
                }
            })

        # Conditions générales de l'indivision
        data['indivision']['conditions_generales'] = {
            'gestion': {
                'mode': 'unanimite',
                'designation_gerant': False
            },
            'jouissance': {
                'mode': 'occupation_exclusive',
                'indemnite_occupation': False
            },
            'charges': {
                'repartition': 'proportionnelle',
                'proportionnelles_quotite': True
            },
            'alienation': {
                'droit_preemption': True,
                'notification_obligatoire': True
            },
            'revente': {
                'droit_preference': True,
                'delai_reponse': 60
            }
        }

    # Modalités de délivrance
    if 'modalites_delivrance' not in data:
        data['modalites_delivrance'] = {
            'remise_cles': {
                'date': data.get('jouissance', {}).get('date_jouissance', 'à la signature'),
                'modalites': 'Remise physique au notaire'
            },
            'libre_occupation': True
        }

    # Négociation
    if 'negociation' not in data:
        data['negociation'] = {
            'agent_immobilier': None,
            'conditions_suspensives': []
        }

    # Conclusion du contrat
    if 'conclusion_contrat' not in data:
        data['conclusion_contrat'] = {
            'lieu': data.get('acte', {}).get('notaire', {}).get('ville', 'LYON'),
            'lieu_signature': 'Étude notariale'
        }

    # Devoir d'information
    if 'devoir_information' not in data:
        data['devoir_information'] = {
            'conseil_notaire': True,
            'delai_reflexion': True
        }

    # Imprévision
    if 'imprevision' not in data:
        data['imprevision'] = {
            'clause_applicable': True,
            'seuil_variation': 10
        }

    # Conventions antérieures
    if 'conventions_anterieures' not in data:
        data['conventions_anterieures'] = {
            'existe': False,
            'liste': []
        }

    # Médiation
    if 'mediation' not in data:
        data['mediation'] = {
            'clause_applicable': True,
            'organisme': 'Chambre des Notaires'
        }

    # Élection de domicile
    if 'election_domicile' not in data:
        data['election_domicile'] = {
            'vendeur': {
                'lieu': data.get('vendeurs', [{}])[0].get('adresse', ''),
                'ville': data.get('vendeurs', [{}])[0].get('ville', '')
            },
            'acquereur': {
                'lieu': data.get('acquereurs', [{}])[0].get('adresse', ''),
                'ville': data.get('acquereurs', [{}])[0].get('ville', '')
            }
        }

    # Titres
    if 'titres' not in data:
        data['titres'] = {
            'conservation': 'Acquéreur',
            'remise_copies': True
        }

    # Pouvoirs
    if 'pouvoirs' not in data:
        data['pouvoirs'] = {
            'vendeur': {'procuration': False},
            'acquereur': {'procuration': False}
        }

    # Affirmation de sincérité
    if 'affirmation' not in data:
        data['affirmation'] = {
            'sincere': True,
            'complete': True
        }

    # Restitution
    if 'restitution' not in data:
        data['restitution'] = {
            'garantie_bancaire': False,
            'sequestre': False
        }

    # RGPD
    if 'rgpd' not in data:
        data['rgpd'] = {
            'consentement': True,
            'traitement_donnees': 'Notaire responsable de traitement',
            'duree_conservation': '10 ans'
        }

    # Certification d'identité
    if 'certification_identite' not in data:
        data['certification_identite'] = {
            'vendeur': {
                'documents': ['CNI', 'Justificatif de domicile'],
                'certifie': True
            },
            'acquereur': {
                'documents': ['CNI', 'Justificatif de domicile'],
                'certifie': True
            }
        }

    return data

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Ajouter sections minimales aux données')
    parser.add_argument('--input', '-i', required=True, help='Fichier données source')
    parser.add_argument('--output', '-o', required=True, help='Fichier données enrichies')

    args = parser.parse_args()

    # Charger données
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Enrichir
    data_enrichie = ajouter_sections_minimales(data)

    # Sauvegarder
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data_enrichie, f, ensure_ascii=False, indent=2)

    print(f'✅ Données enrichies sauvegardées: {args.output}')
    print(f'   Sections ajoutées: urbanisme, indivision, modalites_delivrance, negociation, conclusion_contrat,')
    print(f'                      devoir_information, imprevision, conventions_anterieures, mediation,')
    print(f'                      election_domicile, titres, pouvoirs, affirmation, restitution, rgpd,')
    print(f'                      certification_identite')

if __name__ == '__main__':
    main()
