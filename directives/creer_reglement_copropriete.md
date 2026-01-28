# Directive : Créer un État Descriptif de Division et Règlement de Copropriété

## Objectif

Générer un acte d'état descriptif de division (EDD) et règlement de copropriété pour la mise en copropriété d'un immeuble, 100% fidèle à la trame originale.

---

## Quand utiliser cette directive

- Mise en copropriété d'un immeuble existant
- Création d'une copropriété sur un immeuble neuf
- Division d'un immeuble en plusieurs lots

---

## Fichiers de référence

| Fichier | Description |
|---------|-------------|
| `templates/reglement_copropriete_edd.md` | Template Markdown avec variables Jinja2 |
| `schemas/variables_reglement_copropriete.json` | Structure des données attendues |
| `schemas/questions_reglement_copropriete.json` | Questions à poser au notaire |
| `docs_original/Trame reglement copropriete EDD.docx` | Trame originale - NE JAMAIS MODIFIER |

---

## Structure de l'acte (43 sections)

### Première partie : Désignation et division

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| Préambule | Objet de l'acte, article 7 décret 55-22, loi 65-557 | Oui |
| Chapitre I - Désignation générale | Désignation de l'immeuble | Oui |
| - Désignation | Adresse, cadastre | Oui |
| - Propriétaire | Identification du requérant | Oui |
| - Désignation ensemble immobilier | Description détaillée | Oui |
| - Plans | Liste des plans annexés | Oui |
| - Précisions diverses | Urbanisme, alignement, voirie | Oui |
| Chapitre II - Division | État descriptif de division | Oui |
| - Désignation des lots | Description lot par lot | Oui |
| - Tableau récapitulatif | Numéro, étage, désignation, tantièmes | Oui |
| Chapitre III - Distinction | Parties communes vs privatives | Oui |

### Deuxième partie : Droits et obligations

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| Chapitre IV | Conditions d'usage | Oui |
| Chapitre V | Charges de l'immeuble | Oui |
| Chapitre VI | Mutations, modifications, hypothèques | Oui |

### Troisième partie : Administration

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| Syndicat | Organisation du syndicat | Oui |
| Syndic | Désignation et pouvoirs | Oui |
| Conseil syndical | Composition et rôle | Oui |
| Petite copropriété | Si applicable (<5 lots) | Conditionnel |

### Quatrième partie : Dispositions diverses

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| Chapitre X | Améliorations, surélévations | Oui |
| Chapitre XI | Assurances | Oui |
| Chapitre XII | Litiges | Oui |

### Cinquième partie : Formalités

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| Domicile | Élection de domicile | Oui |
| Frais | Répartition des frais | Oui |
| Immatriculation | Registre national des copropriétés | Oui |
| Enregistrement - Publicité foncière | Formalités SPF | Oui |
| Certification d'identité | Certification notaire | Oui |
| Formalisme annexes | Mention des annexes | Oui |

---

## Diagnostics obligatoires

### DTG (Diagnostic Technique Global)

**Obligatoire si immeuble > 10 ans** (article L731-4 CCH)

Contenu :
- Analyse parties communes et équipements
- État au regard des obligations légales
- Analyse améliorations possibles
- DPE ou audit énergétique
- Évaluation travaux nécessaires sur 10 ans

### Mesurages loi Carrez

- Obligatoire pour tous lots > 8 m²
- Par géomètre-expert

---

## Processus de génération

### Étape 1 : Collecter les informations

```bash
# Utiliser le questionnaire
python execution/collecter_informations.py --schema schemas/questions_reglement_copropriete.json
```

**Informations critiques à collecter :**

1. **Requérant**
   - Identité complète
   - Situation matrimoniale
   - Origine de propriété

2. **Immeuble**
   - Adresse précise
   - Références cadastrales
   - Description par bâtiment et niveau

3. **Lots**
   - Numéro, étage, désignation
   - Superficie Carrez
   - Tantièmes de copropriété
   - Usage et occupation actuelle

4. **Parties communes**
   - Générales
   - Spéciales (si applicable)
   - À jouissance privative

5. **Diagnostics**
   - DTG (si immeuble > 10 ans)
   - Certificats Carrez
   - Urbanisme

### Étape 2 : Valider les données

```bash
python execution/valider_acte.py --schema schemas/variables_reglement_copropriete.json --data donnees.json
```

**Règles de validation critiques :**

| Règle | Vérification |
|-------|--------------|
| Tantièmes | Somme = base totale (1000 ou 10000) |
| Carrez | Obligatoire si lot > 8 m² |
| DTG | Obligatoire si immeuble > 10 ans |
| Cadastre | Références valides |
| Lots | Numérotation continue sans doublon |

### Étape 3 : Assembler l'acte

```bash
# Sans zones grisées (par défaut)
python execution/assembler_acte.py --template templates/reglement_copropriete_edd.md --data donnees.json --output .tmp/acte_edd.md

# Avec zones grisées (si demandé par le notaire)
python execution/assembler_acte.py --template templates/reglement_copropriete_edd.md --data donnees.json --output .tmp/acte_edd.md --zones-grisees
```

### Étape 4 : Générer le DOCX

```bash
# Sans zones grisées
python execution/exporter_docx.py --input .tmp/acte_edd.md --output outputs/EDD_RC_[COMMUNE]_[DATE].docx

# Avec zones grisées
python execution/exporter_docx.py --input .tmp/acte_edd.md --output outputs/EDD_RC_[COMMUNE]_[DATE].docx --zones-grisees
```

**Note :** L'option `--zones-grisees` conserve le fond gris sur les variables remplies, utile pour la relecture.

---

## Particularités de cet acte

### Différences avec une vente

| Élément | Vente | EDD/RC |
|---------|-------|--------|
| Parties | Vendeur/Acquéreur | Requérant (propriétaire) |
| Objet | Transfert propriété | Division en lots |
| Prix | Oui | Non |
| Diagnostics | Vente (DPE, amiante...) | DTG + Carrez |

### Points critiques

1. **Respect de l'article 7 décret 55-22** : L'EDD doit identifier chaque lot de manière unique

2. **Méthode de calcul des tantièmes** : Doit être explicitée (article 10 loi 65-557 modifié)

3. **Immatriculation obligatoire** :
   - > 200 lots : depuis 31/12/2016
   - > 50 lots : depuis 31/12/2017
   - Autres : depuis 31/12/2018

4. **Mise en conformité loi ELAN** : Vérifier si règlement nécessite mise à jour

---

## Annexes à prévoir

| N° | Document | Obligatoire |
|----|----------|-------------|
| 1 | État descriptif de division (géomètre) | Oui |
| 2 | Certificats Carrez | Oui (lots > 8m²) |
| 3 | DTG | Oui (si > 10 ans) |
| 4 | Plans d'accès | Oui |
| 5 | Plans des niveaux | Oui |
| 6 | Certificat d'urbanisme | Oui |
| 7 | Note renseignements urbanisme | Recommandé |
| 8 | Arrêté d'alignement | Si applicable |
| 9-21 | Diagnostics techniques | Selon situation |

---

## Commandes rapides

```bash
# Pipeline complet (SANS zones grisées)
cd "c:\Users\tomra\...\Agent AI Création & Modification d'actes notariaux"

# 1. Collecter
python execution/collecter_informations.py --schema schemas/questions_reglement_copropriete.json --output .tmp/donnees_edd.json

# 2. Valider
python execution/valider_acte.py --schema schemas/variables_reglement_copropriete.json --data .tmp/donnees_edd.json

# 3. Assembler
python execution/assembler_acte.py --template templates/reglement_copropriete_edd.md --data .tmp/donnees_edd.json --output .tmp/acte_edd.md

# 4. Exporter
python execution/exporter_docx.py --input .tmp/acte_edd.md --output outputs/EDD_RC.docx
```

```bash
# Pipeline complet (AVEC zones grisées - demandé par notaire)
cd "c:\Users\tomra\...\Agent AI Création & Modification d'actes notariaux"

# 1. Collecter
python execution/collecter_informations.py --schema schemas/questions_reglement_copropriete.json --output .tmp/donnees_edd.json

# 2. Valider
python execution/valider_acte.py --schema schemas/variables_reglement_copropriete.json --data .tmp/donnees_edd.json

# 3. Assembler (avec marqueurs zones grisées)
python execution/assembler_acte.py --template templates/reglement_copropriete_edd.md --data .tmp/donnees_edd.json --output .tmp/acte_edd.md --zones-grisees

# 4. Exporter (avec fond gris appliqué)
python execution/exporter_docx.py --input .tmp/acte_edd.md --output outputs/EDD_RC.docx --zones-grisees
```

---

## Cas particuliers

### Petite copropriété (≤ 5 lots)

- Syndic non obligatoire
- Conseil syndical facultatif
- Comptabilité simplifiée possible

### Copropriété à deux

- Dispositions spéciales (article 42-1 loi 65-557)
- Pas de conseil syndical
- Majorité adaptée

### Immeuble neuf (VEFA)

- Pas de DTG requis
- Règlement établi par le promoteur
- Fonctionnement copropriété à la livraison du 1er lot

---

## Mises à jour de cette directive

| Date | Modification |
|------|--------------|
| 2025-01-19 | Création initiale |

---

## Voir aussi

- [creer_acte.md](creer_acte.md) - Acte de vente
- [creer_promesse_vente.md](creer_promesse_vente.md) - Promesse de vente
- [creer_modificatif_edd.md](creer_modificatif_edd.md) - Modificatif EDD
- [schemas/clauses_catalogue.json](../schemas/clauses_catalogue.json) - Catalogue des clauses
