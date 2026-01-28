# Directive : Créer un Modificatif de l'État Descriptif de Division et Règlement de Copropriété

## Objectif

Générer un acte modificatif de l'EDD/RC pour modifier la composition d'une copropriété existante (création/suppression/réunion de lots, création de parties communes spéciales, modification du règlement, etc.).

---

## Quand utiliser cette directive

- Création de nouveaux lots (division, prélèvement sur PC)
- Suppression de lots
- Réunion de plusieurs lots en un seul
- Division d'un lot en plusieurs
- Création de parties communes spéciales (par bâtiment)
- Modification des tantièmes
- Modification du règlement de copropriété
- Mise en conformité avec une nouvelle loi

---

## Fichiers de référence

| Fichier | Description |
|---------|-------------|
| `templates/modificatif_edd.md` | Template Markdown avec variables Jinja2 |
| `schemas/variables_modificatif_edd.json` | Structure des données attendues |
| `schemas/questions_modificatif_edd.json` | Questions à poser au notaire |
| `docs_original/trame modificatif.docx` | Trame originale - NE JAMAIS MODIFIER |

---

## Structure de l'acte (12 sections)

| Section | Contenu | Obligatoire |
|---------|---------|-------------|
| En-tête | Date, référence, notaire | Oui |
| Requérant | Syndicat des copropriétaires + syndic | Oui |
| Objet | Type de modificatif | Oui |
| Exposé préalable | Désignation immeuble, historique EDD | Oui |
| EDD actuel | État avant modification | Oui |
| Autorisation AG | Résolution, vote, non-recours | Oui |
| Modifications | Détail des changements | Oui |
| Nouvel EDD | Tableau récapitulatif après modification | Oui |
| Méthode de calcul | Explication des tantièmes | Conditionnel |
| Immatriculation syndicat | Numéro registre national | Oui |
| Formalités | Domicile, frais, publicité foncière | Oui |
| Annexes | Documents joints | Oui |

---

## Différences avec l'EDD initial

| Élément | EDD initial | Modificatif |
|---------|-------------|-------------|
| Requérant | Propriétaire | Syndicat des copropriétaires |
| Représentation | Directe | Par le syndic (pouvoir AG) |
| Autorisation | Aucune | Assemblée générale |
| Majorité | N/A | Article 24, 25 ou 26 selon nature |
| Certificat | N/A | Non-recours obligatoire |
| Historique | Origine propriété | Historique tous modificatifs antérieurs |

---

## Majorités requises selon le type de modification

| Type de modification | Majorité |
|---------------------|----------|
| Division d'un lot privatif | Art. 25 (ou 24 si pas d'impact sur RC) |
| Réunion de lots | Art. 25 |
| Création lot par prélèvement PC | Art. 26 |
| Création parties communes spéciales | Art. 26 |
| Modification tantièmes | Art. 26 |
| Modification droits de jouissance | Unanimité |
| Modification règlement (clauses diverses) | Art. 26 |
| Mise en conformité loi ELAN | Art. 24 |

---

## Processus de génération

### Étape 1 : Collecter les informations

```bash
python execution/collecter_informations.py --schema schemas/questions_modificatif_edd.json
```

**Informations critiques à collecter :**

1. **Syndicat des copropriétaires**
   - Dénomination exacte
   - Numéro d'immatriculation
   - Adresse de l'immeuble

2. **Syndic**
   - Professionnel ou bénévole
   - Coordonnées complètes
   - Représentant à l'acte
   - Délégation de pouvoirs si applicable
   - Dates du mandat

3. **Assemblée générale**
   - Date de l'AG autorisant
   - Majorité requise et obtenue
   - Texte de la résolution
   - Résultat du vote (pour/contre/abstention)
   - Certificat de non-recours

4. **EDD d'origine et historique**
   - Date et notaire de l'acte initial
   - Publication SPF
   - Nombre de lots à l'origine
   - TOUS les modificatifs antérieurs avec leurs références

5. **État actuel**
   - Nombre de lots
   - Tableau récapitulatif complet
   - Total tantièmes

6. **Modifications apportées**
   - Type de modification
   - Détail lot par lot
   - Nouvelles clauses si modification RC

7. **Nouvel état**
   - Nouveau tableau récapitulatif
   - Méthode de calcul si tantièmes modifiés

### Étape 2 : Valider les données

```bash
python execution/valider_acte.py --schema schemas/variables_modificatif_edd.json --data donnees.json
```

**Règles de validation critiques :**

| Règle | Vérification |
|-------|--------------|
| Numéro immatriculation | Format AA9-999-999 |
| AG autorisant | Date < date acte |
| Certificat non-recours | Présent et daté |
| Tantièmes | Somme identique avant/après (sauf prélèvement PC) |
| Historique | Tous modificatifs listés |
| Majorité | Cohérente avec type modification |

### Étape 3 : Assembler l'acte

```bash
# Sans zones grisées (par défaut)
python execution/assembler_acte.py --template templates/modificatif_edd.md --data donnees.json --output .tmp/acte_modificatif.md

# Avec zones grisées (si demandé par le notaire)
python execution/assembler_acte.py --template templates/modificatif_edd.md --data donnees.json --output .tmp/acte_modificatif.md --zones-grisees
```

### Étape 4 : Générer le DOCX

```bash
# Sans zones grisées
python execution/exporter_docx.py --input .tmp/acte_modificatif.md --output outputs/MODIFICATIF_EDD_[COMMUNE]_[DATE].docx

# Avec zones grisées
python execution/exporter_docx.py --input .tmp/acte_modificatif.md --output outputs/MODIFICATIF_EDD_[COMMUNE]_[DATE].docx --zones-grisees
```

**Note :** L'option `--zones-grisees` conserve le fond gris sur les variables remplies, utile pour la relecture.

---

## Cas particuliers

### Création de parties communes spéciales

**Cas typique** : Copropriété multi-bâtiments souhaitant isoler les charges par bâtiment.

**Points clés :**
- Définir précisément les éléments inclus dans chaque PCS
- Créer une clé de répartition par PCS
- Tantièmes PCS répartis entre lots concernés uniquement
- Les charges générales restent engagées

**Exemple de texte :**
```
Les parties communes spéciales « Bâtiment A » comprennent :
- les fondations et gros œuvre
- les éléments de clos et couvert
- les façades et revêtements
- les conduites générales
- le hall d'entrée et circulations
- l'éclairage des parties communes spéciales
```

### Réunion de lots

**Processus :**
1. Identifier les lots à réunir (ex: 12, 15, 17)
2. Supprimer ces lots de l'EDD
3. Créer un nouveau lot avec numéro suivant (ex: 18)
4. Additionner les tantièmes des lots réunis
5. Mettre à jour le tableau récapitulatif

### Division d'un lot

**Processus :**
1. Identifier le lot à diviser (ex: lot 14)
2. Supprimer ce lot de l'EDD
3. Créer les nouveaux lots (ex: 15 et 16)
4. Répartir les tantièmes du lot divisé
5. Faire établir nouveaux mesurages Carrez

### Mise en conformité loi ELAN

**Délai** : 3 ans à compter de la loi pour mise en conformité article 6-4 loi 65-557.

**Points à vérifier :**
- Définition des parties communes (générales, spéciales, à jouissance privative)
- Détermination des lots transitoires
- Mention des éléments d'équipement

---

## Annexes obligatoires

| N° | Document | Obligatoire |
|----|----------|-------------|
| 1 | Pouvoir du syndic / Délégation | Oui |
| 2 | PV de l'assemblée générale | Oui |
| 3 | Certificat de non-recours | Oui |
| 4 | Plan cadastral | Oui |
| 5 | Projet modificatif EDD (géomètre) | Si applicable |
| 6 | Attestation mise à jour immatriculation | Oui |

---

## Commandes rapides

```bash
# Pipeline complet (SANS zones grisées)
cd "c:\Users\tomra\...\Agent AI Création & Modification d'actes notariaux"

# 1. Collecter
python execution/collecter_informations.py --schema schemas/questions_modificatif_edd.json --output .tmp/donnees_modificatif.json

# 2. Valider
python execution/valider_acte.py --schema schemas/variables_modificatif_edd.json --data .tmp/donnees_modificatif.json

# 3. Assembler
python execution/assembler_acte.py --template templates/modificatif_edd.md --data .tmp/donnees_modificatif.json --output .tmp/acte_modificatif.md

# 4. Exporter
python execution/exporter_docx.py --input .tmp/acte_modificatif.md --output outputs/MODIFICATIF_EDD.docx
```

```bash
# Pipeline complet (AVEC zones grisées - demandé par notaire)
cd "c:\Users\tomra\...\Agent AI Création & Modification d'actes notariaux"

# 1. Collecter
python execution/collecter_informations.py --schema schemas/questions_modificatif_edd.json --output .tmp/donnees_modificatif.json

# 2. Valider
python execution/valider_acte.py --schema schemas/variables_modificatif_edd.json --data .tmp/donnees_modificatif.json

# 3. Assembler (avec marqueurs zones grisées)
python execution/assembler_acte.py --template templates/modificatif_edd.md --data .tmp/donnees_modificatif.json --output .tmp/acte_modificatif.md --zones-grisees

# 4. Exporter (avec fond gris appliqué)
python execution/exporter_docx.py --input .tmp/acte_modificatif.md --output outputs/MODIFICATIF_EDD.docx --zones-grisees
```

---

## Points critiques

### Historique des modificatifs

**OBLIGATOIRE** : Lister TOUS les modificatifs antérieurs avec :
- Date de l'acte
- Notaire
- Objet (division, réunion, création...)
- Publication SPF (date, volume, numéro)
- Attestations rectificatives si existantes

### Contribution de sécurité immobilière

- Modificatif EDD : 125 EUR (droit fixe)
- + 15 EUR (formalité de publicité)

### Observations loi ELAN

À mentionner si le règlement de copropriété n'est pas conforme :
- Calcul des tantièmes non conforme à l'origine
- Extensions non régularisées
- Caves/greniers non identifiés

---

## Mises à jour de cette directive

| Date | Modification |
|------|--------------|
| 2025-01-19 | Création initiale |

---

## Voir aussi

- [creer_reglement_copropriete.md](creer_reglement_copropriete.md) - EDD/RC initial
- [creer_acte.md](creer_acte.md) - Acte de vente
- [modifier_acte.md](modifier_acte.md) - Modification d'actes existants
- [schemas/clauses_catalogue.json](../schemas/clauses_catalogue.json) - Catalogue des clauses
