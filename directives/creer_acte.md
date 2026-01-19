# Directive : Création d'un Acte Notarial

## Objectif
Créer un acte notarial complet (vente ou promesse de vente de lots de copropriété) à partir des informations fournies par le notaire, en garantissant la conformité juridique et la fidélité au template.

## Prérequis
- Le notaire a demandé la création d'un acte
- Le type d'acte est identifié (vente ou promesse)
- Le notaire est disponible pour répondre aux questions

## Flux de travail

### Étape 1 : Identification du type d'acte

**Question au notaire :**
> Quel type d'acte souhaitez-vous créer ?
> - Acte de vente de lots de copropriété
> - Promesse unilatérale de vente de lots de copropriété

**Scripts utilisés :** Aucun (décision humaine)

**Sortie :** Type d'acte sélectionné

---

### Étape 2 : Collecte des informations essentielles

#### 2.1 Informations sur l'acte
**Questions obligatoires :**
- Date prévue de signature ?
- Numéro de répertoire / référence interne ?

#### 2.2 Identification du VENDEUR (ou PROMETTANT)
**Pour chaque vendeur, collecter :**
1. Civilité (Monsieur/Madame)
2. Nom et prénoms (tous les prénoms)
3. Profession
4. Adresse complète (numéro, voie, code postal, ville)
5. Date de naissance
6. Lieu de naissance
7. Nationalité
8. Situation matrimoniale :
   - Célibataire → pas de questions supplémentaires
   - Marié(e) → régime matrimonial, contrat de mariage (notaire, date, lieu)
   - Pacsé(e) → date, lieu d'enregistrement, régime
   - Divorcé(e) → tribunal, date du jugement
   - Veuf/Veuve → nom du défunt conjoint

**Astuce :** Si plusieurs vendeurs, demander s'ils vendent ensemble (indivision) et leurs quotités respectives.

#### 2.3 Identification de l'ACQUÉREUR (ou BÉNÉFICIAIRE)
Mêmes informations que pour le vendeur.

**Questions supplémentaires :**
- Primo-accédant ? (impact fiscal)
- Les acquéreurs achètent-ils en indivision ? Si oui, quelles quotités ?

#### 2.4 Désignation du bien
**Informations à collecter :**
1. Adresse complète de l'immeuble
2. Nom de la résidence/copropriété (si applicable)
3. Références cadastrales (section, numéro, lieudit, surface)
4. Pour chaque lot vendu :
   - Numéro de lot
   - Type (appartement, cave, parking, etc.)
   - Description détaillée
   - Étage, escalier
   - Tantièmes
5. Superficie loi Carrez (si applicable)

#### 2.5 Prix et financement
**Informations obligatoires :**
1. Prix de vente total
2. Mode de paiement :
   - Comptant intégral
   - Avec prêt(s) → détails de chaque prêt (banque, montant, durée, taux)

#### 2.6 Copropriété
**Informations à collecter :**
1. Nom et adresse du syndic
2. Numéro d'immatriculation
3. Existence d'un fonds de travaux (montant quote-part)
4. Emprunt collectif en cours ? (montant solde)

---

### Étape 3 : Sections optionnelles

**Proposer au notaire :**

| Section | Question | Condition |
|---------|----------|-----------|
| Meubles inclus | Des meubles sont-ils inclus dans la vente ? | Si oui, liste et valeur |
| Travaux récents | Le vendeur a-t-il réalisé des travaux depuis moins de 10 ans ? | Si oui, liste des travaux avec factures |
| Condition suspensive prêt | L'acquéreur a-t-il besoin d'un prêt ? (Promesse uniquement) | Si oui, caractéristiques du prêt |
| Négociation | Un agent immobilier est-il intervenu ? | Si oui, coordonnées et honoraires |
| Jouissance anticipée | Y a-t-il une entrée en jouissance avant la vente ? | Si oui, date et convention |

---

### Étape 4 : Validation des données

**Script à exécuter :**
```bash
python execution/valider_acte.py --donnees .tmp/donnees_collectees.json --schema schemas/variables_vente.json
```

**Gestion des erreurs :**
- **ERREUR** : Informer le notaire et demander les informations manquantes
- **AVERTISSEMENT** : Informer le notaire, lui laisser le choix de continuer
- **INFO** : Mentionner pour information

**Boucle :** Répéter jusqu'à validation réussie.

---

### Étape 5 : Génération de l'acte

**Question préalable au notaire :**
> Souhaitez-vous conserver les zones grisées sur les variables remplies dans le document final ?
> - **Oui** : Les zones de saisie resteront visibles (utile pour relecture)
> - **Non** : Les variables seront intégrées sans mise en forme spéciale

**Script à exécuter :**
```bash
# Sans zones grisées (par défaut)
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_collectees.json \
    --output .tmp/actes_generes/

# Avec zones grisées (si demandé par le notaire)
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_collectees.json \
    --output .tmp/actes_generes/ \
    --zones-grisees
```

**Sortie :**
- `acte.md` : Acte au format Markdown (avec marqueurs si zones grisées demandées)
- `donnees.json` : Données utilisées (pour traçabilité)
- `metadata.json` : Métadonnées (date, version)

---

### Étape 5bis : Choix du format d'export

**Question au notaire :**
> Dans quel format souhaitez-vous générer l'acte ?
> - **PDF** : Document figé, prêt pour signature
> - **Word (DOCX)** : Document modifiable, annotations possibles

**Note :** Ce choix peut être modifié à tout moment avant la validation finale.

**Sortie :** Format sélectionné (`pdf` ou `docx`)

---

### Étape 6 : Export et présentation

**Scripts à exécuter selon le format choisi :**

**Format PDF :**
```bash
python execution/exporter_pdf.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.pdf \
    --brouillon
```

**Format DOCX :**
```bash
# Sans zones grisées
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.docx \
    --brouillon

# Avec zones grisées (si le fichier contient les marqueurs)
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.docx \
    --brouillon \
    --zones-grisees
```

**Note :** L'option `--zones-grisees` doit être utilisée à la fois dans `assembler_acte.py` (pour insérer les marqueurs) ET dans `exporter_docx.py` (pour appliquer le fond gris).

**Présentation au notaire :**
> Voici le projet d'acte généré au format {FORMAT}.
>
> [Fichier {PDF/DOCX} joint]
>
> Points à vérifier particulièrement :
> - Identité des parties
> - Désignation du bien et tantièmes
> - Prix et conditions de paiement
> - Sections optionnelles incluses
>
> Souhaitez-vous apporter des modifications ou changer le format d'export ?

---

### Étape 7 : Modifications (si nécessaire)

**Si le notaire demande des modifications :**
1. Identifier la nature de la modification :
   - Correction de données → Mettre à jour `donnees.json`
   - Ajout/retrait de section → Mettre à jour les options
   - Reformulation → Modification manuelle du template si générique

2. Régénérer l'acte avec les scripts

3. Représenter au notaire

**Boucle :** Répéter jusqu'à validation finale.

---

### Étape 8 : Validation finale

**Lorsque le notaire valide :**
1. Régénérer le document final sans watermark "PROJET"
2. Mettre à jour le statut dans `metadata.json` : `"statut": "valide"`
3. Enregistrer le format choisi dans `metadata.json` : `"format": "pdf"` ou `"format": "docx"`
4. Archiver l'acte

**Format PDF :**
```bash
python execution/exporter_pdf.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte_final.pdf
```

**Format DOCX :**
```bash
# Sans zones grisées
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte_final.docx

# Avec zones grisées
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte_final.docx \
    --zones-grisees
```

**Note :** Si le notaire le souhaite, les deux formats peuvent être générés simultanément.

---

## Arbre de décision - Collecte d'informations

```
DÉBUT
│
├─ Type d'acte ?
│   ├─ Vente → Template: vente_lots_copropriete.md
│   └─ Promesse → Template: promesse_vente_lots_copropriete.md
│
├─ Nombre de vendeurs ?
│   ├─ 1 → Collecter infos vendeur unique
│   └─ >1 → Pour chaque vendeur + quotités
│
├─ Nombre d'acquéreurs ?
│   ├─ 1 → Collecter infos acquéreur unique
│   └─ >1 → Pour chaque acquéreur + quotités
│
├─ Financement ?
│   ├─ Comptant intégral → Prix uniquement
│   └─ Avec prêt(s) → Détails prêt + (si promesse) condition suspensive
│
├─ Meubles inclus ?
│   ├─ Non → Section omise
│   └─ Oui → Liste des meubles + valeur optionnelle
│
├─ Travaux récents (<10 ans) ?
│   ├─ Non → Mention standard
│   └─ Oui → Liste travaux + décennales
│
├─ Agent immobilier ?
│   ├─ Non → Section omise
│   └─ Oui → Coordonnées + honoraires + à charge de qui
│
└─ [Continuer avec diagnostics, copropriété, etc.]
```

---

## Exemples de dialogues

### Exemple 1 : Début de création

**Notaire :** "Je veux créer un acte de vente pour un appartement T3"

**Agent :** "Je vais créer un acte de vente de lots de copropriété. Commençons par les informations essentielles.

**VENDEUR :**
- Quel est le nom complet du vendeur (tous les prénoms) ?
- Sa profession ?
- Son adresse actuelle ?"

### Exemple 2 : Situation matrimoniale

**Notaire :** "M. Jean Dupont, marié"

**Agent :** "M. Dupont est marié. J'ai besoin de quelques précisions :
- Quel est le régime matrimonial (communauté légale, séparation de biens, etc.) ?
- Y a-t-il eu un contrat de mariage ? Si oui, chez quel notaire et à quelle date ?
- Nom de l'épouse (pour vérifier si elle doit intervenir à l'acte) ?"

### Exemple 3 : Validation avec avertissement

**Agent :** "La validation révèle un avertissement : le total des prêts (280 000 €) semble élevé par rapport au prix (245 000 €).

Cela peut s'expliquer par l'inclusion des frais de notaire et frais de prêt. Souhaitez-vous :
1. Confirmer et continuer
2. Corriger les montants ?"

---

## Points de vigilance

1. **Régime matrimonial** : Toujours vérifier si le conjoint doit intervenir à l'acte
2. **Quotités** : S'assurer qu'elles totalisent 100%
3. **Prêts** : Vérifier la cohérence montant prêt vs prix
4. **Copropriété** : Ne pas oublier le syndic et l'emprunt collectif éventuel
5. **Diagnostics** : Vérifier que tous sont à jour (dates de validité)
6. **Superficie Carrez** : Obligatoire pour les lots > 8m²

---

## Spécifications de formatage DOCX (CRITIQUE)

Le formatage DOCX doit être **100% fidèle** à la trame originale. Les paramètres suivants sont extraits de l'analyse de `docs_originels/Trame vente lots de copropriété.docx` et **ne doivent jamais être modifiés**.

### Police et taille
- **Police**: Times New Roman 11pt (partout, sans exception)
- **Interligne**: Simple

### Marges (A4)
| Marge | Valeur |
|-------|--------|
| Gauche | 60mm (6.0cm) |
| Droite | 15mm (1.5cm) |
| Haut | 25mm (2.5cm) |
| Bas | 25mm (2.5cm) |
| Marges miroir | **NON** |

### Retrait première ligne
- **Retrait**: 12.51mm (1.251cm) - appliqué à tous les paragraphes normaux

### Styles de titres (Headings)

| Style | Formatage | Alignement | Espacement |
|-------|-----------|------------|------------|
| Heading 1 | Bold, ALL CAPS, underline | Centré | 12pt après |
| Heading 2 | Bold, small caps, underline | Centré | 12pt après |
| Heading 3 | Bold, underline | Centré | 12pt après |
| Heading 4 | Bold only | Justifié | 6pt **avant** |

### Alignement texte
- **Paragraphes normaux**: Justifié
- **Titres (H1-H3)**: Centré
- **Listes à puces**: Justifié avec retrait 6mm

### Pagination
- Numéro de page en haut à droite (Times New Roman 9pt)
- En-tête différent sur première page

---

## Spécifications techniques du pipeline

### Étape 1: Assemblage (Markdown)
```bash
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_client.json \
    --output .tmp/actes_generes/
```

**Fonctionnalités auto-générées:**
- Montants en lettres (filtres Jinja2)
- Dates en lettres
- Numéros de lots en lettres
- Tantièmes en lettres

### Étape 2: Export DOCX
```bash
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.docx
```

**Détection automatique de 20+ types de tableaux:**
- Désignation cadastrale
- Répartition des charges
- État hypothécaire
- Frais d'acte / émoluments
- Diagnostics immobiliers
- Financement / prêts
- Lots de copropriété
- Et plus...

### Étape 3 (optionnel): Export PDF
```bash
python execution/exporter_pdf.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.pdf
```

---

## Points critiques pour la fidélité

1. **NE JAMAIS modifier les valeurs de formatage** - Elles proviennent de l'analyse du document original
2. **Utiliser le template Markdown avec balises HTML** pour le formatage spécifique (div class="personne", etc.)
3. **Tableaux**: Utiliser le format Markdown standard (`| Col1 | Col2 |`) - la détection est automatique
4. **Soulignement**: Utiliser `__texte__` en Markdown (pas de balises `<u>`)
5. **Gras**: Utiliser `**texte**` en Markdown

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-17 | Création initiale | Agent |
| 2025-01-19 | Ajout spécifications formatage DOCX fidèle à l'original | Agent |
| 2025-01-19 | Documentation pipeline complet et points critiques | Agent |

---

## Voir aussi

- [directives/modifier_acte.md](modifier_acte.md) - Modification d'un acte existant
- [directives/formatage_docx.md](formatage_docx.md) - Spécifications détaillées du formatage DOCX
- [directives/ajouter_template.md](ajouter_template.md) - Ajout d'un nouveau type d'acte
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma des variables
- [schemas/sections_catalogue.json](../schemas/sections_catalogue.json) - Catalogue des sections
