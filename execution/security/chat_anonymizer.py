# -*- coding: utf-8 -*-
"""
Service d'anonymisation pour le chat.

Anonymise les données sensibles avant envoi à Claude,
puis dé-anonymise la réponse.

Usage:
    anonymizer = ChatAnonymizer()
    texte_anonyme, mapping = anonymizer.anonymiser("Promesse Martin vers Dupont, 450000 euros")
    # texte_anonyme = "Promesse [VENDEUR_1] vers [ACQUEREUR_1], [PRIX_1] euros"

    reponse_finale = anonymizer.deanonymiser(reponse_claude, mapping)
"""

import re
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# Encodage UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


@dataclass
class AnonymizationMapping:
    """Mapping d'anonymisation réversible."""
    vendeurs: Dict[str, str] = field(default_factory=dict)  # nom_reel -> [VENDEUR_N]
    acquereurs: Dict[str, str] = field(default_factory=dict)
    adresses: Dict[str, str] = field(default_factory=dict)
    prix: Dict[str, str] = field(default_factory=dict)
    dates: Dict[str, str] = field(default_factory=dict)
    notaires: Dict[str, str] = field(default_factory=dict)

    def get_reverse_mapping(self) -> Dict[str, str]:
        """Retourne le mapping inversé pour la dé-anonymisation."""
        reverse = {}
        for category in [self.vendeurs, self.acquereurs, self.adresses,
                        self.prix, self.dates, self.notaires]:
            for original, anonyme in category.items():
                reverse[anonyme] = original
        return reverse


class ChatAnonymizer:
    """
    Anonymise les textes de chat pour envoi sécurisé à Claude.

    Détecte et remplace:
    - Noms de personnes (vendeurs, acquéreurs)
    - Adresses
    - Prix
    - Dates
    - Noms de notaires
    """

    # Patterns de détection
    PATTERNS = {
        # Noms après indicateurs de rôle
        'vendeur': re.compile(
            r'\b(?:vendeur|promettant|cédant|propriétaire)\s*[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
            re.IGNORECASE | re.UNICODE
        ),
        'acquereur': re.compile(
            r'\b(?:acquéreur|acheteur|bénéficiaire|cessionnaire)\s*[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
            re.IGNORECASE | re.UNICODE
        ),
        # Pattern "X → Y" ou "X vers Y" pour transactions
        'transaction': re.compile(
            r'([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+(?:et|&)\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)\s*(?:→|->|vers)\s*([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+(?:et|&)\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
            re.UNICODE
        ),
        # Prix en euros
        'prix': re.compile(
            r'\b(\d{1,3}(?:[\s.,]\d{3})*)\s*(?:€|euros?|EUR)\b',
            re.IGNORECASE
        ),
        # Adresses (numéro + rue + ville)
        'adresse': re.compile(
            r'\b(\d+(?:bis|ter)?)\s+(rue|avenue|boulevard|place|impasse|allée|chemin)\s+([A-ZÀ-Ÿa-zà-ÿ\s\-]+?)(?:\s+(?:à|,)\s+([A-ZÀ-Ÿ][a-zà-ÿ\-]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ\-]+)*))?',
            re.IGNORECASE | re.UNICODE
        ),
        # Codes postaux
        'code_postal': re.compile(r'\b(\d{5})\b'),
        # Dates (JJ/MM/AAAA ou JJ-MM-AAAA)
        'date': re.compile(r'\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b'),
        # Maître/Notaire
        'notaire': re.compile(
            r'\b(?:Ma[îi]tre|Me|Notaire)\s+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)?)',
            re.UNICODE
        ),
        # Civilités + Nom
        'civilite_nom': re.compile(
            r'\b(?:Monsieur|Madame|M\.|Mme|Mr\.?)\s+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
            re.UNICODE
        ),
    }

    # Mots à ne jamais anonymiser (termes juridiques, etc.)
    MOTS_EXCLUS = {
        # Termes juridiques
        'promesse', 'vente', 'acte', 'propriété', 'copropriété', 'lot', 'bien',
        'prix', 'euros', 'conditions', 'suspensives', 'prêt', 'financement',
        'notaire', 'signature', 'compromis', 'titre', 'cadastre',
        # Verbes
        'crée', 'créer', 'génère', 'générer', 'modifie', 'modifier', 'ajoute',
        'liste', 'affiche', 'recherche', 'trouve',
        # Types d'actes
        'standard', 'premium', 'mobilier',
        # Termes communs
        'appartement', 'maison', 'terrain', 'parking', 'cave', 'garage',
    }

    def __init__(self):
        self.compteurs = {
            'vendeur': 0,
            'acquereur': 0,
            'adresse': 0,
            'prix': 0,
            'date': 0,
            'notaire': 0,
        }

    def _est_mot_exclu(self, mot: str) -> bool:
        """Vérifie si le mot ne doit pas être anonymisé."""
        return mot.lower() in self.MOTS_EXCLUS or len(mot) < 3

    def anonymiser(self, texte: str) -> Tuple[str, AnonymizationMapping]:
        """
        Anonymise un texte et retourne le mapping.

        Args:
            texte: Texte original avec données sensibles

        Returns:
            Tuple (texte_anonymisé, mapping)
        """
        mapping = AnonymizationMapping()
        texte_anonyme = texte

        # 1. Détecter les transactions (X → Y)
        for match in self.PATTERNS['transaction'].finditer(texte):
            vendeurs = match.group(1)
            acquereurs = match.group(2)

            # Anonymiser les vendeurs
            for nom in re.split(r'\s+(?:et|&)\s+', vendeurs):
                nom = nom.strip()
                if nom and not self._est_mot_exclu(nom) and nom not in mapping.vendeurs:
                    self.compteurs['vendeur'] += 1
                    placeholder = f"[VENDEUR_{self.compteurs['vendeur']}]"
                    mapping.vendeurs[nom] = placeholder

            # Anonymiser les acquéreurs
            for nom in re.split(r'\s+(?:et|&)\s+', acquereurs):
                nom = nom.strip()
                if nom and not self._est_mot_exclu(nom) and nom not in mapping.acquereurs:
                    self.compteurs['acquereur'] += 1
                    placeholder = f"[ACQUEREUR_{self.compteurs['acquereur']}]"
                    mapping.acquereurs[nom] = placeholder

        # 2. Détecter les vendeurs explicites
        for match in self.PATTERNS['vendeur'].finditer(texte):
            nom = match.group(1).strip()
            if nom and not self._est_mot_exclu(nom) and nom not in mapping.vendeurs:
                self.compteurs['vendeur'] += 1
                mapping.vendeurs[nom] = f"[VENDEUR_{self.compteurs['vendeur']}]"

        # 3. Détecter les acquéreurs explicites
        for match in self.PATTERNS['acquereur'].finditer(texte):
            nom = match.group(1).strip()
            if nom and not self._est_mot_exclu(nom) and nom not in mapping.acquereurs:
                self.compteurs['acquereur'] += 1
                mapping.acquereurs[nom] = f"[ACQUEREUR_{self.compteurs['acquereur']}]"

        # 4. Détecter les prix
        for match in self.PATTERNS['prix'].finditer(texte):
            prix_str = match.group(0)
            if prix_str not in mapping.prix:
                self.compteurs['prix'] += 1
                mapping.prix[prix_str] = f"[PRIX_{self.compteurs['prix']}]"

        # 5. Détecter les adresses
        for match in self.PATTERNS['adresse'].finditer(texte):
            adresse = match.group(0)
            if adresse not in mapping.adresses:
                self.compteurs['adresse'] += 1
                mapping.adresses[adresse] = f"[ADRESSE_{self.compteurs['adresse']}]"

        # 6. Détecter les notaires
        for match in self.PATTERNS['notaire'].finditer(texte):
            nom = match.group(1).strip()
            if nom and not self._est_mot_exclu(nom) and nom not in mapping.notaires:
                self.compteurs['notaire'] += 1
                mapping.notaires[nom] = f"[NOTAIRE_{self.compteurs['notaire']}]"

        # 7. Détecter les dates
        for match in self.PATTERNS['date'].finditer(texte):
            date_str = match.group(1)
            if date_str not in mapping.dates:
                self.compteurs['date'] += 1
                mapping.dates[date_str] = f"[DATE_{self.compteurs['date']}]"

        # 8. Détecter les noms après civilités
        for match in self.PATTERNS['civilite_nom'].finditer(texte):
            nom = match.group(1).strip()
            # Vérifier si pas déjà mappé comme vendeur ou acquéreur
            if (nom and not self._est_mot_exclu(nom) and
                nom not in mapping.vendeurs and nom not in mapping.acquereurs):
                # On ne sait pas le rôle, on met en vendeur par défaut
                self.compteurs['vendeur'] += 1
                mapping.vendeurs[nom] = f"[PERSONNE_{self.compteurs['vendeur']}]"

        # Appliquer les remplacements (par longueur décroissante pour éviter les conflits)
        all_mappings = {}
        all_mappings.update(mapping.vendeurs)
        all_mappings.update(mapping.acquereurs)
        all_mappings.update(mapping.adresses)
        all_mappings.update(mapping.prix)
        all_mappings.update(mapping.dates)
        all_mappings.update(mapping.notaires)

        for original, anonyme in sorted(all_mappings.items(), key=lambda x: -len(x[0])):
            texte_anonyme = texte_anonyme.replace(original, anonyme)

        return texte_anonyme, mapping

    def deanonymiser(self, texte: str, mapping: AnonymizationMapping) -> str:
        """
        Restaure les données originales dans un texte anonymisé.

        Args:
            texte: Texte avec placeholders
            mapping: Mapping d'anonymisation

        Returns:
            Texte avec données réelles
        """
        reverse = mapping.get_reverse_mapping()

        texte_final = texte
        for anonyme, original in sorted(reverse.items(), key=lambda x: -len(x[0])):
            texte_final = texte_final.replace(anonyme, original)

        return texte_final

    def reset(self):
        """Réinitialise les compteurs pour une nouvelle session."""
        self.compteurs = {k: 0 for k in self.compteurs}


# Test simple
if __name__ == "__main__":
    anonymizer = ChatAnonymizer()

    # Test
    texte_test = """
    Crée une promesse de vente Martin vers Dupont pour un appartement
    45 rue de la Paix à Paris, prix 450000 euros.
    Le notaire Maître Leblanc sera en charge du dossier.
    Signature prévue le 15/03/2026.
    """

    print("=== TEXTE ORIGINAL ===")
    print(texte_test)

    texte_anonyme, mapping = anonymizer.anonymiser(texte_test)

    print("\n=== TEXTE ANONYMISÉ ===")
    print(texte_anonyme)

    print("\n=== MAPPING ===")
    print(f"Vendeurs: {mapping.vendeurs}")
    print(f"Acquéreurs: {mapping.acquereurs}")
    print(f"Prix: {mapping.prix}")
    print(f"Adresses: {mapping.adresses}")
    print(f"Notaires: {mapping.notaires}")
    print(f"Dates: {mapping.dates}")

    # Simuler une réponse Claude
    reponse_claude = """
    D'accord, je prépare une promesse de vente où [VENDEUR_1] vend à [ACQUEREUR_1]
    un appartement situé [ADRESSE_1] au prix de [PRIX_1].
    L'acte sera reçu par [NOTAIRE_1] avec signature prévue le [DATE_1].
    """

    print("\n=== RÉPONSE CLAUDE (anonyme) ===")
    print(reponse_claude)

    texte_final = anonymizer.deanonymiser(reponse_claude, mapping)

    print("\n=== RÉPONSE FINALE (dé-anonymisée) ===")
    print(texte_final)
