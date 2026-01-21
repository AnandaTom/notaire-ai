# Directive : Création d'une Donation-Partage

## Objectif

Générer un acte de **donation-partage** 100% conforme à la trame originale ([docs_originels/Donation partage (2).pdf](../docs_originels/Donation%20partage%20(2).pdf)), avec 28 pages de contenu structuré.

## Qu'est-ce qu'une Donation-Partage ?

Une donation-partage est un acte notarié par lequel les parents (donateurs) donnent et partagent tout ou partie de leurs biens entre leurs enfants (donataires) de leur vivant. Cet acte permet :

- **D'anticiper la succession** et d'éviter les conflits futurs
- **De figer la valeur des biens** au jour de la donation (art. 1078 Code civil)
- **De transmettre avec démembrement** (nue-propriété aux enfants, usufruit aux parents)
- **D'optimiser fiscalement** grâce aux abattements (100 000 € par parent et par enfant tous les 15 ans)

## Inputs

### Documents requis

1. **Pièces d'identité et d'état civil** :
   - Extraits d'acte de naissance (donateurs + donataires)
   - Cartes nationales d'identité
   - Extrait d'acte de mariage des donateurs
   - Contrat de mariage (si existant)

2. **Documents relatifs aux biens donnés** :
   - **Si parts sociales** : Statuts de la société, extraits Kbis, comptes sociaux, attestation de valorisation
   - **Si SCPI** : Attestations de propriété et de valeur
   - **Si immobilier** : Titres de propriété, diagnostics

3. **Documents fiscaux** :
   - Interrogations BODACC (vérification faillite)
   - Donations antérieures (<15 ans)

4. **Informations bancaires** (si comptes courants d'associés)

### Informations à collecter

Utiliser le fichier de questions : **`schemas/questions_donation_partage.json`** (150+ questions structurées)

**Sections principales** :

1. **Informations sur l'acte** (référence, date, lieu)
2. **Notaire rédacteur** (identité, office, CRPCEN)
3. **Donateurs** (identité complète, mariage, situation matrimoniale)
4. **Donataires** (identité, situation familiale, adresse)
5. **Donation antérieure** (si <15 ans → rappel fiscal)
6. **Société** (si donation de parts sociales : statuts, valorisation, comptes)
7. **Biens donnés** (description, valeur PP, calcul NP avec barème usufruit)
8. **Répartition** (égalitaire ou inégalitaire, quotités)
9. **Fiscalité** (abattements, calcul des droits)

## Scripts et Outils

| Étape | Script | Fonction |
|-------|--------|----------|
| **1. Validation** | `execution/valider_acte.py` | Valide la cohérence des données avec le schéma |
| **2. Assemblage** | `execution/assembler_acte.py` | Template + données → Markdown normalisé |
| **3. Export DOCX** | `execution/exporter_docx.py` | Markdown → DOCX fidèle à l'original |
| **4. Validation conformité** | `execution/comparer_documents.py` | Compare structure avec trame originale |

### Workflow complet

```bash
# 1. Validation des données
python execution/valider_acte.py \
    --donnees .tmp/dossiers/client_X/donnees.json \
    --schema schemas/variables_donation_partage.json

# 2. Assemblage de l'acte
python execution/assembler_acte.py \
    --template donation_partage.md \
    --donnees .tmp/dossiers/client_X/donnees.json \
    --output .tmp/actes_generes/

# 3. Export DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/{id}/acte.md \
    --output outputs/donation_partage_client_X.docx

# 4. Validation conformité
python execution/comparer_documents.py \
    --original "docs_originels/Donation partage (2).pdf" \
    --genere outputs/donation_partage_client_X.docx \
    --seuil 80
```

## Spécificités Techniques

### Formatage DOCX (CRITIQUE - NE PAS MODIFIER)

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| **Police** | Times New Roman 11pt | Trame originale |
| **Marges** | G=60mm, D=15mm, H/B=25mm | **Marges miroirs** |
| **Retrait 1ère ligne** | 12.51mm | Paragraphes normaux |
| **Interligne** | Simple | Tout le document |
| **Heading 1** | Bold, ALL CAPS, underline, centré | Titres principaux |
| **Heading 2** | Bold, small caps, underline, centré | Sous-titres |
| **Heading 3** | Bold, underline, centré | Sous-sections |
| **Heading 4** | Bold only, 6pt avant | Paragraphes importants |

### Sections obligatoires (28 pages)

1. **Page de garde** - Référence, date, titre, parties
2. **Identification des parties** - Donateurs + Donataires
3. **Éléments préalables** - Terminologie, déclarations, documents
4. **Exposé préalable** - Contexte, donations antérieures
5. **Constitution de société** (si applicable) - Statuts, capital, associés
6. **Donation-partage** - Structure en 4 parties :
   - PREMIERE PARTIE : Masse des biens donnés
   - DEUXIEME PARTIE : Valeurs des droits
   - TROISIEME PARTIE : Attributions aux donataires
   - QUATRIEME PARTIE : Conditions, clauses, fiscalité
7. **Conditions particulières** - 15+ clauses (exclusion communauté, droit de retour, etc.)
8. **Transfert de propriété** - Modalités usufruit/nue-propriété
9. **Décision d'agrément** (si société) - Intervention des associés
10. **Modifications statutaires** (si société) - Article 11 (droit de vote), article 21 (résultats)
11. **Déclarations fiscales** - Rappel fiscal, calcul des droits
12. **Mentions légales** - Médiation, RGPD, signatures

### Calcul de l'usufruit (Barème fiscal art. 669 CGI)

| Âge usufruitier | Taux usufruit | Taux nue-propriété |
|-----------------|---------------|---------------------|
| Moins de 21 ans | 90% | 10% |
| 21 à 30 ans | 80% | 20% |
| 31 à 40 ans | 70% | 30% |
| 41 à 50 ans | 60% | 40% |
| 51 à 60 ans | 50% | 50% |
| 61 à 70 ans | **40%** | **60%** |
| 71 à 80 ans | 30% | 70% |
| 81 à 90 ans | 20% | 80% |
| Plus de 90 ans | 10% | 90% |

**Exemple** : Donateur de 64 ans → Usufruit = 40%, Nue-propriété = 60%

### Clauses essentielles

1. **Clause d'exclusion de communauté** - Les biens restent propres aux donataires
2. **Clause d'exclusion PACS** - Idem pour l'indivision du PACS
3. **Réserve du droit de retour** - Art. 951 Code civil (prédécès sans postérité)
4. **Interdiction d'aliéner** - Pendant la vie du donateur (sauf accord exprès)
5. **Usufruit successif** - Au profit du conjoint survivant
6. **Rapport si renonciation** - Art. 845 Code civil
7. **Condition de non-attaque** - Pénalité si contestation du partage

## Outputs

### Fichiers générés

| Fichier | Emplacement | Description |
|---------|-------------|-------------|
| `acte.md` | `.tmp/actes_generes/{id}/` | Markdown assemblé et normalisé |
| `donation_partage_client.docx` | `outputs/` | **Acte final** 100% conforme |
| `rapport_conformite.json` | `.tmp/actes_generes/{id}/` | Résultat de comparaison structurelle |
| `donnees_normalisees.json` | `.tmp/actes_generes/{id}/` | Données avec deep copy et normalisation |

### Annexes (si applicables)

1. **Annexe n°1** : Attestations de propriété et de valeurs SCPI
2. **Annexe n°2** : Extrait bilan – Balance globale (comptes courants)
3. **Annexe n°3** : Attestation valorisation parts sociales

## Edge Cases et Validations

### 1. Vérifications obligatoires AVANT génération

```python
# Script de validation complet
python execution/valider_acte.py --donnees .tmp/donnees.json --schema schemas/variables_donation_partage.json
```

**Contrôles automatiques** :

- ✅ **Quotités = 100%** - La somme des parts attribuées doit totaliser 100%
- ✅ **Âge cohérent** - Donateurs > Donataires, usufruit calculable
- ✅ **Dates logiques** - Mariage < Naissance enfants < Date acte
- ✅ **SIREN valide** - 9 chiffres (si société)
- ✅ **Code postal** - 5 chiffres
- ✅ **Régime matrimonial compatible** - Avec clauses stipulées

### 2. Situation matrimoniale → Intervention du conjoint

| Régime | Biens personnels | Biens communs | Intervention conjoint |
|--------|------------------|---------------|-----------------------|
| **Séparation de biens** | Donation libre | N/A | Non requise |
| **Communauté réduite** | Donation libre | Accord obligatoire | Oui si biens communs |
| **Participation aux acquêts** | Donation libre | Accord obligatoire | Oui si biens communs |
| **Communauté universelle** | Quasi-inexistant | Accord obligatoire | **Toujours** |

### 3. Donation antérieure < 15 ans → Rappel fiscal

**Obligatoire** selon art. 784 CGI :

- Identifier toutes donations de même donateur à même donataire
- Calculer abattements déjà consommés
- Appliquer progressivité du barème (tranches les plus élevées)

**Exemple** :
```
Donation 2021 : 100 000 € (abattement 100 000 € → 0 droits)
Donation 2025 :     500 € (abattement 0 € → base taxable 500 €)
→ Droits à 5% = 10 €
```

### 4. Parts sociales → Agrément requis

**Si statuts prévoient agrément donation** (art. 13 statuts) :

1. Assemblée générale extraordinaire **OU**
2. Signature acte authentique par **tous les associés**

→ Intervention des associés **obligatoire** dans l'acte

### 5. Usufruit successif → Caducité si divorce

**Clause automatique** : Révocation de plein droit si :

- Introduction procédure divorce
- Jugement de divorce (même non définitif)
- Convention divorce amiable

**Sauf** volonté contraire constatée par juge → Irrévocable

## Points Critiques à NE PAS Oublier

### 📌 Avant de lancer la génération

- [ ] **Tous les donataires sont-ils enfants des donateurs ?** (présomptifs héritiers)
- [ ] **Y a-t-il d'autres enfants non donataires ?** (déséquilibre successoral ?)
- [ ] **Donation antérieure < 15 ans ?** → Rappel fiscal obligatoire
- [ ] **Biens personnels ou communs ?** → Intervention conjoint si communs
- [ ] **Parts sociales ?** → Vérifier clause d'agrément statuts
- [ ] **Usufruit réservé ?** → Calculer taux selon âge
- [ ] **Usufruit successif ?** → Accord du conjoint bénéficiaire
- [ ] **Comptes courants ?** → Valorisation + annexe bilan

### 📌 Après génération

- [ ] **Validation conformité ≥ 80%** (script `comparer_documents.py`)
- [ ] **Vérification manuelle** : Titres, numérotation articles, signatures
- [ ] **Export PDF** pour archivage (optionnel mais recommandé)
- [ ] **Enrichissement catalogues** si nouvelles clauses/situations

## Self-Anneal : Amélioration Continue

### Si erreur de génération

1. **Lire l'erreur complète** (stack trace)
2. **Identifier la cause** :
   - Variable manquante → Ajouter dans `questions_donation_partage.json`
   - Filtre Jinja2 absent → Créer dans `assembler_acte.py`
   - Formatage incorrect → Vérifier `exporter_docx.py`
3. **Corriger le code** (pas de workaround)
4. **Documenter** dans `directives/lecons_apprises.md`
5. **Tester à nouveau**

### Si conformité < 80%

1. **Analyser rapport** : `cat .tmp/actes_generes/{id}/rapport_conformite.json`
2. **Identifier sections manquantes** (comparaison titres)
3. **Enrichir template** :
   - Ajouter titres manquants dans `donation_partage.md`
   - Créer variables correspondantes dans `variables_donation_partage.json`
   - Ajouter questions dans `questions_donation_partage.json`
4. **Re-tester jusqu'à ≥ 80%**

## Ressources

### Fichiers du système

| Type | Chemin | Description |
|------|--------|-------------|
| **Template** | `templates/donation_partage.md` | Template Jinja2 (28 pages) |
| **Schéma** | `schemas/variables_donation_partage.json` | 150+ variables structurées |
| **Questions** | `schemas/questions_donation_partage.json` | 150+ questions collecte |
| **Directive** | `directives/creer_donation_partage.md` | Ce fichier |
| **Original** | `docs_originels/Donation partage (2).pdf` | Trame de référence (28 pages) |

### Documentation juridique

- **Code civil** : Art. 1075-1080 (Donation-partage)
- **Code civil** : Art. 738-2 (Droit de retour légal père/mère)
- **Code civil** : Art. 757-3 (Droit de retour frères/sœurs)
- **Code civil** : Art. 843-845 (Rapport des donations)
- **Code civil** : Art. 951 (Droit de retour conventionnel)
- **CGI** : Art. 669 (Barème usufruit)
- **CGI** : Art. 779 (Abattements)
- **CGI** : Art. 784 (Rappel fiscal donations antérieures)

## Exemple de Workflow Complet

```bash
# ÉTAPE 1 : Collecter les informations
python execution/collecter_informations.py \
    --type donation_partage \
    --output .tmp/dossiers/auvray_2025/donnees.json

# ÉTAPE 2 : Valider les données
python execution/valider_acte.py \
    --donnees .tmp/dossiers/auvray_2025/donnees.json \
    --schema schemas/variables_donation_partage.json

# ÉTAPE 3 : Assembler l'acte
python execution/assembler_acte.py \
    --template donation_partage.md \
    --donnees .tmp/dossiers/auvray_2025/donnees.json \
    --output .tmp/actes_generes/

# ÉTAPE 4 : Exporter en DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/dp_20250120_143022/acte.md \
    --output outputs/donation_partage_auvray.docx

# ÉTAPE 5 : Valider la conformité
python execution/comparer_documents.py \
    --original "docs_originels/Donation partage (2).pdf" \
    --genere outputs/donation_partage_auvray.docx \
    --seuil 80

# ÉTAPE 6 : Archiver dans Supabase
python execution/historique_supabase.py \
    --type donation_partage \
    --donnees .tmp/actes_generes/dp_20250120_143022/donnees_normalisees.json \
    --acte outputs/donation_partage_auvray.docx
```

## Garanties de Conformité

### Objectif : ≥ 80% de conformité structurelle

**Critères de validation** :

1. **Structure** : Tous les titres de niveau 1-4 présents
2. **Pagination** : 28 pages ±2
3. **Formatage** : Marges miroirs, police Times 11pt, retraits
4. **Sections** : 11 sections principales complètes
5. **Clauses** : 15+ conditions particulières
6. **Fiscalité** : Calcul droits conforme (abattements, barème)

### Si conformité < 80%

**Ne pas livrer au notaire**. Enrichir le template prioritairement (voir section Self-Anneal).

### Si conformité ≥ 80%

**Livrable PROD**. Le document peut être signé électroniquement et enregistré.

---

**Version** : 1.1.0
**Dernière mise à jour** : 2025-01-20
**Auteur** : NotaireAI
**Statut** : ✅ Directive production-ready
