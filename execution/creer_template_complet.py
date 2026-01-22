#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
creer_template_complet.py
==========================

Crée un template Markdown complet à partir du DOCX original
en remplaçant toutes les valeurs spécifiques par des variables Jinja2.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from pathlib import Path

def remplacer_valeurs_par_variables(texte):
    """Remplace les valeurs spécifiques par des variables Jinja2"""

    # Mapping des remplacements
    remplacements = {
        # Noms et prénoms
        r'\bDominique\b': '{{ donateur_1.prenom }}',
        r'\bChristian\b': '{{ donateur_1.deuxieme_prenom }}',
        r'\bAUVRAY\b': '{{ donateur_1.nom|upper }}',
        r'\bAuvray\b': '{{ donateur_1.nom }}',
        r'\bViviane\b': '{{ donateur_2.prenom }}',
        r'\bBlanche\b': '{{ donateur_2.deuxieme_prenom }}',
        r'\bCélie\b': '{{ donateur_2.troisieme_prenom }}',
        r'\bROBIN\b': '{{ donateur_2.nom_naissance|upper }}',
        r'\bRobin\b': '{{ donateur_2.nom_naissance }}',
        r'\bAntoine\b': '{{ donataires[0].prenom }}',
        r'\bEdmond\b': '{{ donataires[0].troisieme_prenom }}',
        r'\bMathilde\b': '{{ donataires[1].prenom }}',
        r'\bYvonne\b': '{{ donataires[1].deuxieme_prenom }}',
        r'\bNicole\b': '{{ donataires[1].troisieme_prenom }}',

        # Lieux
        r'\bDARDILLY\b': '{{ donateur_1.adresse.ville|upper }}',
        r'\bDardilly\b': '{{ donateur_1.adresse.ville }}',
        r'\b69570\b': '{{ donateur_1.adresse.code_postal }}',
        r'29 chemin du [Pp]anorama': '{{ donateur_1.adresse.numero }} {{ donateur_1.adresse.voie }}',
        r'\bLYON 3ÈME ARRONDISSEMENT\b': '{{ donataires[0].adresse.ville|upper }}',
        r'\b69003\b': '{{ donataires[0].adresse.code_postal }}',
        r'16 cours Lafayette': '{{ donataires[0].adresse.numero }} {{ donataires[0].adresse.voie }}',
        r'\bPARIS 9ÈME ARRONDISSEMENT\b': '{{ donataires[1].adresse.ville|upper }}',
        r'\b75009\b': '{{ donataires[1].adresse.code_postal }}',
        r'18 rue Milton': '{{ donataires[1].adresse.numero }} {{ donataires[1].adresse.voie }}',

        # Dates
        r'23 décembre 2025': '{{ date_acte.day }} {{ date_acte.month|mois_en_lettres }} {{ date_acte.year }}',
        r'DEUX MILLE VINGT CINQ': '{{ date_acte.year|nombre_en_lettres|upper }}',
        r'VINGT TROIS DÉCEMBRE': '{{ date_acte.day|jour_en_lettres|upper }} {{ date_acte.month|mois_en_lettres|upper }}',
        r'20 février 1961': '{{ donateur_1.naissance.date.day }} {{ donateur_1.naissance.date.month|mois_en_lettres }} {{ donateur_1.naissance.date.year }}',
        r'16 avril 1961': '{{ donateur_2.naissance.date.day }} {{ donateur_2.naissance.date.month|mois_en_lettres }} {{ donateur_2.naissance.date.year }}',
        r'19 février 1991': '{{ donataires[0].naissance.date.day }} {{ donataires[0].naissance.date.month|mois_en_lettres }} {{ donataires[0].naissance.date.year }}',
        r'9 août 1993': '{{ donataires[1].naissance.date.day }} {{ donataires[1].naissance.date.month|mois_en_lettres }} {{ donataires[1].naissance.date.year }}',

        # Références
        r'\b100583001\b': '{{ reference_acte }}',
        r'\bCDI/ALG\b': '{{ initiales_notaire }}',

        # Notaire
        r'\bCharlotte\b': '{{ notaire.prenom }}',
        r'\bDIAZ\b': '{{ notaire.nom|upper }}',
        r'\bDiaz\b': '{{ notaire.nom }}',
        r'des Cèdres': '{{ notaire.nom_societe }}',
        r'\bTASSIN-LA-DEMI-LUNE\b': '{{ notaire.office.ville|upper }}',
        r'93 avenue du 11 Novembre 1918': '{{ notaire.office.adresse }}',
        r'\b69182\b': '{{ notaire.crpcen }}',

        # Société
        r'\bBLOUGE\b': '{{ societe.nom }}',
        r'\b985 331 354\b': '{{ societe.siren }}',

        # Montants (euros)
        r'QUATRE CENT MILLE EUROS': '{{ montant_donation_anterieure|nombre_en_lettres|upper }} EUROS',
        r'400 000,00 EUR': '{{ montant_donation_anterieure|format_montant }} EUR',
        r'MILLE EUROS': '{{ societe.capital|nombre_en_lettres|upper }} EUROS',
        r'1 000,00 EUR': '{{ societe.capital|format_montant }} EUR',
    }

    # Appliquer les remplacements
    for pattern, replacement in remplacements.items():
        texte = re.sub(pattern, replacement, texte)

    return texte

def creer_template_complet():
    """Crée le template complet"""

    # Lire le fichier texte extrait
    content_path = Path('.tmp/donation_partage_original_complet.txt')
    content = content_path.read_text(encoding='utf-8')

    lines = []
    for line in content.split('\n'):
        if '.' in line:
            parts = line.split('.', 1)
            if len(parts) == 2:
                lines.append(parts[1].strip())

    print(f"✅ {len(lines)} lignes extraites")

    # Construire le template
    template_lines = []

    # Header page 1
    template_lines.append('{FIRST_PAGE_HEADER_START}')
    template_lines.append('{{ reference_acte }}')
    template_lines.append('{{ initiales_notaire }}/')
    template_lines.append('')
    template_lines.append('Le {{ date_acte.day }} {{ date_acte.month|mois_en_lettres }} {{ date_acte.year }}')
    template_lines.append('{FIRST_PAGE_HEADER_END}')
    template_lines.append('')
    template_lines.append('**DONATION-PARTAGE**')
    template_lines.append('**Par {{ donateur_1.civilite }} {{ donateur_1.prenom }} {{ donateur_1.nom|upper }}**')
    template_lines.append('**Et {{ donateur_2.civilite }} {{ donateur_2.prenom }} {{ donateur_2.nom_naissance|upper }} née {{ donateur_2.nom_naissance|upper }}**')
    template_lines.append('**Au profit de leurs {{ nombre_enfants_lettres }} enfants**')
    template_lines.append('***************************************************************')
    template_lines.append('')

    # Remplacer les valeurs spécifiques par des variables
    for i, line in enumerate(lines[3:]):  # Skip les 3 premières lignes déjà traitées
        line_template = remplacer_valeurs_par_variables(line)
        template_lines.append(line_template)

    # Écrire le template
    output_path = Path('templates/donation_partage_complet_v2.md')
    output_path.write_text('\n'.join(template_lines), encoding='utf-8')

    print(f"✅ Template créé: {output_path}")
    print(f"   Lignes: {len(template_lines)}")

if __name__ == '__main__':
    creer_template_complet()
