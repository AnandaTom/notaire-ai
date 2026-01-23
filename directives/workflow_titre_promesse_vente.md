# Directive : Workflow Complet Titre → Promesse → Vente

## Objectif

Ce document décrit le workflow complet pour générer des actes notariaux en partant du titre de propriété du vendeur.

---

## Vue d'ensemble

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   TITRE PROPRIÉTÉ   │────▶│  PROMESSE DE VENTE  │────▶│   ACTE DE VENTE     │
│   (Document source) │     │  (Étape 1)          │     │   (Étape finale)    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           │
         ▼                           ▼                           ▼
    Extraction auto            Génération auto             Génération auto
    + Stockage Supabase        depuis titre                depuis promesse
```

---

## Étape 1 : Obtenir le Titre de Propriété

### Option A : Rechercher dans Supabase (Recommandé)

```bash
# Recherche par nom du vendeur
python execution/gestionnaire_titres_propriete.py search -q "TARBOURIECH"

# Recherche par adresse
python execution/gestionnaire_titres_propriete.py search -q "Tassin"
```

Si trouvé → Passer à l'étape 2

### Option B : Demander au notaire de téléverser

Si le titre n'est pas dans la base :

1. **Front-end** : Le notaire téléverse le PDF/DOCX du titre
2. **Backend** : Réception et extraction automatique

```bash
# Upload et extraction automatique
python execution/gestionnaire_titres_propriete.py upload -f titre_propriete.pdf -v
```

**Résultat** :
```
✓ Titre créé: TITRE-20260123-143052
  Propriétaires: TARBOURIECH, KSOURI
  Adresse: 28 Chemin de la Raude 69160 Tassin-la-Demi-Lune
  Confiance: 85%
```

### Option C : Saisie manuelle

Si l'extraction automatique échoue (<50% de confiance) :
1. Afficher les champs extraits au notaire
2. Lui demander de compléter/corriger
3. Sauvegarder dans Supabase

---

## Étape 2 : Générer la Promesse de Vente

### 2.1 Convertir le titre vers données promesse

```bash
# Convertir automatiquement
python execution/gestionnaire_titres_propriete.py convert \
    -t TITRE-20260123-143052 \
    --type promesse \
    -o .tmp/donnees_promesse.json
```

**Ce qui est pré-rempli automatiquement** :
- ✅ Promettants (= propriétaires actuels du titre)
- ✅ Bien (adresse, cadastre, lots, tantièmes)
- ✅ Copropriété (règlement, syndic)
- ✅ Origine de propriété (= acte du titre)
- ✅ Prix initial (= prix d'acquisition du titre)

**À compléter par le notaire** :
- ⏳ Bénéficiaires (acquéreurs)
- ⏳ Prix de vente négocié
- ⏳ Indemnité d'immobilisation
- ⏳ Délais (expiration, dépôt garantie)
- ⏳ Conditions suspensives
- ⏳ Notaire du bénéficiaire (si différent)

### 2.2 Compléter les données manquantes

Via le questionnaire interactif :
```bash
python execution/collecter_informations.py \
    --type promesse_vente \
    --pre-rempli .tmp/donnees_promesse.json \
    --output .tmp/donnees_promesse_complete.json
```

### 2.3 Générer la promesse

```bash
python execution/workflow_rapide.py \
    --donnees .tmp/donnees_promesse_complete.json \
    --template promesse_vente_lots_copropriete.md \
    --output outputs/promesse_VENDEUR_ACQUEREUR.docx
```

### 2.4 Sauvegarder dans Supabase

```bash
python execution/historique_supabase.py \
    --action save \
    --reference PROM-2026-001 \
    --type promesse_vente \
    --data .tmp/donnees_promesse_complete.json
```

---

## Étape 3 : Générer l'Acte de Vente

Après signature de la promesse et réalisation des conditions suspensives :

### 3.1 Charger les données de la promesse

```bash
python execution/historique_supabase.py \
    --action get \
    --reference PROM-2026-001 \
    --json > .tmp/donnees_promesse_signee.json
```

### 3.2 Convertir vers acte de vente

```bash
# Ou directement depuis le titre
python execution/gestionnaire_titres_propriete.py convert \
    -t TITRE-20260123-143052 \
    --type vente \
    -o .tmp/donnees_vente.json
```

**Ce qui change par rapport à la promesse** :
- VENDEUR (au lieu de PROMETTANT)
- ACQUEREUR (au lieu de BENEFICIAIRE)
- Quotités vendues + acquises
- Paiement effectif
- Prêts détaillés
- Sections supplémentaires (garanties, plus-values, etc.)

### 3.3 Compléter et générer

```bash
# Compléter les données
python execution/collecter_informations.py \
    --type vente \
    --pre-rempli .tmp/donnees_vente.json \
    --output .tmp/donnees_vente_complete.json

# Générer l'acte
python execution/workflow_rapide.py \
    --donnees .tmp/donnees_vente_complete.json \
    --template vente_lots_copropriete.md \
    --output outputs/acte_VENDEUR_ACQUEREUR.docx
```

---

## Schéma des Données

### Mapping Titre → Promesse → Vente

| Données Titre | Données Promesse | Données Vente |
|--------------|------------------|---------------|
| `proprietaires_actuels` | `promettants` | `vendeurs` |
| `vendeurs_originaux` | `origine_propriete.auteur` | `origine_propriete.auteur` |
| `bien.adresse` | `bien.adresse` | `bien.adresse` |
| `bien.lots` | `bien.lots` | `bien.lots` |
| `copropriete` | `copropriete` | `copropriete` |
| `prix.montant_total` | `prix.montant` (modifiable) | `prix.montant` |
| `notaire` | `origine_propriete.notaire` | `origine_propriete.notaire` |
| `publication` | `origine_propriete.publication` | `origine_propriete.publication` |
| - | `beneficiaires` | `acquereurs` |
| - | `indemnite_immobilisation` | - |
| - | `conditions_suspensives` | `conditions_realisees` |
| - | - | `paiement` |
| - | - | `prets` |

---

## Scripts Disponibles

| Script | Description |
|--------|-------------|
| `extraire_titre_propriete.py` | Extraction automatique PDF/DOCX |
| `gestionnaire_titres_propriete.py` | CRUD + conversion Supabase |
| `historique_supabase.py` | Gestion des actes (promesses, ventes) |
| `collecter_informations.py` | Questionnaire interactif |
| `workflow_rapide.py` | Pipeline complet de génération |

---

## Intégration Supabase

### Tables

| Table | Description |
|-------|-------------|
| `titres_propriete` | Titres de propriété extraits |
| `actes` | Promesses et actes de vente |
| `dossiers_notariaux` | Liaison titre → promesse → vente |
| `historique_modifications` | Audit trail |

### Création des tables

```bash
# Afficher le schéma SQL
python execution/gestionnaire_titres_propriete.py schema

# Copier-coller dans l'éditeur SQL de Supabase
```

### Fonctions de recherche

```sql
-- Recherche par nom de propriétaire
SELECT * FROM find_titre_by_owner('TARBOURIECH');

-- Recherche par adresse
SELECT * FROM find_titre_by_address('Tassin', 'Raude');

-- Recherche full-text
SELECT * FROM search_titres('copropriété Tassin');
```

---

## Workflow Interactif (Agent AI)

### Quand un notaire demande une promesse de vente

```
1. Agent: "Avez-vous le titre de propriété du vendeur ?"

2a. Si OUI:
    → Agent: "Téléversez le document (PDF ou DOCX)"
    → Extraction automatique
    → Affichage des données extraites pour validation
    → "Les données sont correctes ?"

2b. Si NON:
    → Agent: "Quel est le nom du vendeur ?"
    → Recherche dans Supabase
    → Si trouvé: "J'ai trouvé ce titre. Est-ce le bon ?"
    → Si non trouvé: "Je n'ai pas ce titre. Pouvez-vous le téléverser ?"

3. Une fois le titre validé:
    → Agent: "Je génère la promesse de vente pré-remplie."
    → "Qui sont les bénéficiaires (acquéreurs) ?"
    → Collecte des informations manquantes
    → Génération du document

4. Après génération:
    → Affichage du score de conformité
    → Sauvegarde dans Supabase
    → "Voulez-vous que je prépare aussi l'acte de vente ?"
```

---

## Cas Particuliers

### Titre non trouvable / illisible

```
Si confiance < 50%:
    1. Notifier le notaire
    2. Afficher les champs extraits vs manquants
    3. Proposer saisie manuelle assistée
    4. Alternative: utiliser les données d'exemple
```

### Plusieurs vendeurs avec origines différentes

```
Si propriétaires ont acquis à des dates différentes:
    → Créer plusieurs entrées dans origine_propriete
    → Associer chaque lot à son origine
```

### Titre de succession ou donation

```
Si type_acquisition = succession ou donation:
    → Extraire les détails du défunt/donateur
    → Intégrer dans origine_propriete.details_succession
```

---

## Métriques et Qualité

### Score de confiance extraction

| Score | Interprétation | Action |
|-------|----------------|--------|
| ≥ 85% | Excellent | Utiliser directement |
| 70-84% | Bon | Vérification rapide |
| 50-69% | Moyen | Validation par notaire |
| < 50% | Faible | Saisie manuelle recommandée |

### Champs critiques (obligatoires)

- [ ] Propriétaires actuels (nom, prénom, adresse)
- [ ] Adresse du bien
- [ ] Lots de copropriété
- [ ] Origine de propriété (notaire, date, publication)
- [ ] Date de l'acte

### Champs importants (recommandés)

- [ ] Régime matrimonial des propriétaires
- [ ] Prix d'acquisition
- [ ] Superficie Carrez
- [ ] Règlement de copropriété
- [ ] Syndic

---

## Exemples de Commandes

### Workflow complet en une ligne

```bash
# 1. Upload titre + 2. Conversion promesse + 3. Génération
python execution/gestionnaire_titres_propriete.py upload -f titre.pdf && \
python execution/gestionnaire_titres_propriete.py convert -t $(ls -t .tmp/titres_propriete/*.json | head -1 | xargs basename .json) --type promesse -o .tmp/promesse.json && \
python execution/workflow_rapide.py --donnees .tmp/promesse.json --template promesse_vente_lots_copropriete.md --output outputs/promesse.docx
```

### Test avec le PDF exemple

```bash
# Extraire le titre de propriété analysé
python execution/extraire_titre_propriete.py \
    -i "docs_originels/ACTE_AUTHENTIQUE_PAGES_1-39.pdf" \
    -o .tmp/titre_diaz_extrait.json \
    -v
```

---

## Voir aussi

- [directives/creer_promesse_vente.md](creer_promesse_vente.md) - Détails promesse
- [directives/creer_acte.md](creer_acte.md) - Détails vente
- [directives/integration_titre_propriete.md](integration_titre_propriete.md) - Analyse initiale
- [schemas/variables_titre_propriete.json](../schemas/variables_titre_propriete.json) - Schéma titre
- [schemas/variables_promesse_vente.json](../schemas/variables_promesse_vente.json) - Schéma promesse
- [schemas/variables_vente.json](../schemas/variables_vente.json) - Schéma vente

---

## Historique

| Date | Modification | Auteur |
|------|--------------|--------|
| 2026-01-23 | Création du workflow complet | Agent |
