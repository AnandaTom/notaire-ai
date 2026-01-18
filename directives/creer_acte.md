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

**Script à exécuter :**
```bash
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/donnees_collectees.json \
    --output .tmp/actes_generes/
```

**Sortie :**
- `acte.md` : Acte au format Markdown
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
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte.docx \
    --brouillon
```

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
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output .tmp/actes_generes/{id}/acte_final.docx
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

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-17 | Création initiale | Agent |

---

## Voir aussi

- [directives/modifier_acte.md](modifier_acte.md) - Modification d'un acte existant
- [directives/ajouter_template.md](ajouter_template.md) - Ajout d'un nouveau type d'acte
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma des variables
- [schemas/sections_catalogue.json](../schemas/sections_catalogue.json) - Catalogue des sections
