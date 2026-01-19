# Directive : Collecte d'informations auprès du notaire

## Objectif

Guider la collecte structurée de toutes les informations nécessaires à la génération d'un acte notarial complet et correct, en posant les questions dans l'ordre logique et en validant les réponses.

## Principe de fonctionnement

L'agent (via front-end) pose des questions au notaire de manière conversationnelle. Le schéma de questions se trouve dans `schemas/questions_notaire.json`.

---

## Flux de collecte

### Phase 1 : Initialisation

1. **Identifier le type d'acte**
   - Vente de lots de copropriété
   - Promesse de vente de lots de copropriété

2. **Créer le dossier temporaire**
   ```
   .tmp/dossiers/{reference}/
   ├── collecte.json      # Données collectées progressivement
   ├── validation.json    # Résultats de validation
   └── historique.json    # Historique des modifications
   ```

---

### Phase 2 : Questions par section

#### Section 1 : Informations sur l'acte
```
Questions:
- Date prévue de signature ?
- Numéro de répertoire / référence interne ?
- Y a-t-il un notaire assistant l'acquéreur ?
```

#### Section 2 : Vendeur(s)
```
Pour CHAQUE vendeur:

Questions d'identité:
- Civilité (Monsieur/Madame) ?
- Tous les prénoms (dans l'ordre de l'état civil) ?
- Nom de famille ?
- Nom de naissance (si différent) ?
- Profession ?
- Adresse complète (numéro, voie, CP, ville) ?
- Date de naissance ?
- Lieu de naissance (ville et département/pays) ?
- Nationalité ?

Question clé - Situation matrimoniale:
- Célibataire → Pas de questions supplémentaires
- Marié(e) → Questions régime matrimonial
- Pacsé(e) → Questions PACS
- Divorcé(e) → Questions divorce
- Veuf/Veuve → Question conjoint décédé

Si MARIÉ(E):
- Régime matrimonial ?
- Contrat de mariage ? (Si oui: notaire, date, lieu)
- Le conjoint intervient-il à l'acte ? (CRITIQUE si bien commun)

Si PACSÉ(E):
- Date du PACS ?
- Lieu d'enregistrement ?
- Régime (séparation ou indivision) ?

Si DIVORCÉ(E):
- Tribunal ayant prononcé le divorce ?
- Date du jugement ?

Si VEUF/VEUVE:
- Nom du conjoint décédé ?
```

#### Section 3 : Acquéreur(s)
Mêmes questions que vendeur + :
```
- L'acquéreur est-il primo-accédant ?
```

#### Section 4 : Quotités
```
- Comment se répartissent les quotités VENDUES ?
  (Exemple: Mme X = 1/2 pleine propriété, M. Y = 1/2 pleine propriété)

- Comment se répartissent les quotités ACQUISES ?
  (Exemple: M. et Mme Z = chacun 1/2 pleine propriété)

VALIDATION: Les quotités doivent totaliser 100% !
```

#### Section 5 : Désignation du bien
```
- Adresse complète du bien ?
- Nom de la résidence/copropriété ?
- Références cadastrales (section, numéro, lieudit, surface) ?
```

#### Section 6 : Lots de copropriété
```
Pour CHAQUE lot vendu:
- Numéro du lot ?
- Type (appartement, cave, parking...) ?
- Description détaillée ?
- Étage ?
- Escalier/Bâtiment ?
- Tantièmes des parties communes générales ?
- Total des tantièmes de la copropriété ?
- Superficie loi Carrez ? (OBLIGATOIRE si lot > 8m²)
```

#### Section 7 : Prix et paiement
```
- Prix de vente total ?
- Montant attribué au mobilier (si inclus) ?
- Mode de paiement (comptant / avec prêt / mixte) ?
- Si comptant: montant ?
```

#### Section 8 : Prêts (si applicable)
```
Pour CHAQUE prêt:
- Banque prêteuse ?
- Montant du prêt ?
- Durée (en mois) ?
- Taux d'intérêt nominal ?
- Type de prêt (classique, PTZ, Action Logement...) ?

VALIDATION: Total prêts cohérent avec prix + frais
```

#### Section 9 : Copropriété
```
- Nom du syndic ?
- Adresse du syndic ?
- Numéro d'immatriculation de la copropriété ?
- Montant quote-part fonds de travaux ?
- Emprunt collectif en cours ? (Si oui: solde restant)
```

#### Section 10 : Origine de propriété
```
- Comment le vendeur a-t-il acquis le bien ?
  (Acquisition, succession, donation, licitation, partage, adjudication)
- Date de l'acte précédent ?
- Notaire l'ayant reçu ?
- Lieu de réception ?
- Références de publication (SPF, volume, numéro) ?
```

#### Section 11 : État descriptif de division
```
- Date de l'EDD ?
- Notaire l'ayant reçu ?
- Y a-t-il eu des modificatifs ? (Si oui: détails)
```

#### Section 12 : Sections optionnelles
```
Proposer au notaire:
- Mobilier inclus ? → Liste et valeur
- Travaux récents (<10 ans) ? → Liste avec factures
- Agent immobilier ? → Nom, honoraires, à charge de qui
```

#### Section 13 : Usage du bien
```
- Usage actuel (habitation, commercial, mixte, professionnel) ?
- L'acquéreur conserve-t-il cet usage ?
```

---

### Phase 3 : Validation

Après collecte complète, exécuter:
```bash
python execution/valider_acte.py \
    --donnees .tmp/dossiers/{reference}/collecte.json \
    --schema schemas/variables_vente.json
```

**Gestion des erreurs:**
- **ERREUR** (bloquant): Informer le notaire, demander correction
- **AVERTISSEMENT** (non bloquant): Informer, laisser le choix
- **INFO** : Mentionner pour information

---

### Phase 4 : Génération

Une fois validé:
```bash
# 1. Assembler
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/dossiers/{reference}/collecte.json \
    --output .tmp/actes_generes/

# 2. Exporter DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/acte_{reference}.docx
```

---

## Exemples de dialogue

### Exemple 1 : Début de collecte

**Agent:** Bonjour ! Je vais vous aider à créer un acte de vente de lots de copropriété. Commençons par les informations générales.

Quelle est la **date prévue de signature** de l'acte ?

**Notaire:** 15 mars 2025

**Agent:** Parfait. Quel est le **numéro de répertoire** ou référence interne pour cet acte ?

---

### Exemple 2 : Situation matrimoniale

**Agent:** Quelle est la **situation matrimoniale** de Madame DUPONT ?

**Notaire:** Elle est mariée

**Agent:** D'accord. Pour une personne mariée, j'ai besoin de quelques précisions :
1. Quel est le **régime matrimonial** (communauté légale, séparation de biens...) ?
2. Y a-t-il eu un **contrat de mariage** ?
3. Le **conjoint** intervient-il à l'acte ?

---

### Exemple 3 : Validation avec avertissement

**Agent:** J'ai terminé la collecte. Voici le résultat de la validation :

✅ **Validé** : Identité des parties complète
✅ **Validé** : Désignation du bien conforme
⚠️ **Avertissement** : Le total des prêts (300 000 €) dépasse le prix de vente (285 000 €)

Cela peut s'expliquer par l'inclusion des frais de notaire dans le financement. Confirmez-vous vouloir continuer ?

---

## Variables et leur mapping

| Variable document | Question correspondante |
|-------------------|------------------------|
| `(tous les prénoms et nom)` | Prénoms + Nom |
| `(profession)` | Profession |
| `(adresse)` | Adresse complète |
| `Né à … le….` | Lieu + Date de naissance |
| `Célibataire.` | Situation matrimoniale |
| `le…, enregistré de … le….` | Date PACS, lieu, date enregistrement |
| `Section` / `N°` / `Lieudit` | Références cadastrales |
| `Lot numéro quatorze (14)` | Numéro du lot |
| `tantièmes` | Tantièmes du lot |

---

## Points de vigilance

1. **Régime matrimonial** : Toujours vérifier si le conjoint doit intervenir
2. **Quotités** : Vérifier qu'elles totalisent 100%
3. **Carrez** : Obligatoire pour lots > 8m²
4. **Prêts** : Vérifier cohérence avec le prix
5. **Syndic** : Ne pas oublier l'immatriculation
6. **Origine** : Vérifier les références de publication

---

## Mises à jour

| Date | Modification |
|------|--------------|
| 2025-01-19 | Création - Directive de collecte structurée basée sur l'analyse des 361 variables |

---

## Voir aussi

- [schemas/questions_notaire.json](../schemas/questions_notaire.json) - Schéma complet des questions
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma des données
- [directives/creer_acte.md](creer_acte.md) - Flux complet de création
