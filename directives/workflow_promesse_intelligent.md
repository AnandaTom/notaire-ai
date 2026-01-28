# Workflow Intelligent - Génération de Promesse de Vente

> **Version:** 1.0.0
> **Date:** 28 janvier 2026
> **Objectif:** Générer des promesses de vente flexibles, ultra-fiables, avec apprentissage continu

---

## Vue d'Ensemble

Ce workflow utilise un **système de clauses modulaires intelligent** qui:
1. **Sélectionne automatiquement** les sections en fonction des données du dossier
2. **S'adapte** aux demandes du notaire en temps réel
3. **Apprend** des retours pour s'améliorer continuellement
4. **Gère** des cas simples ou complexes avec le même template unifié

---

## Architecture du Système

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SYSTÈME DE GÉNÉRATION INTELLIGENT                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────┐     │
│  │   DONNÉES    │───▶│   GESTIONNAIRE   │───▶│    ASSEMBLEUR     │     │
│  │   DOSSIER    │    │    CLAUSES       │    │    TEMPLATE       │     │
│  └──────────────┘    └──────────────────┘    └───────────────────┘     │
│         │                    │                        │                 │
│         │           ┌───────┴───────┐                │                 │
│         │           │               │                │                 │
│         ▼           ▼               ▼                ▼                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    ┌───────────┐            │
│  │ Profils  │  │ Sections │  │ Sections │    │   DOCX    │            │
│  │ Pré-déf. │  │  Fixes   │  │ Variables│    │  Final    │            │
│  └──────────┘  │   (44)   │  │   (21)   │    └───────────┘            │
│                └──────────┘  └──────────┘                              │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    BOUCLE D'APPRENTISSAGE                         │   │
│  │  Feedback Notaire ──▶ Analyse ──▶ Enrichissement ──▶ Catalogue   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Étape 1: Collecte des Informations

### 1.1 Informations Obligatoires (Sections Fixes)

Ces informations sont **TOUJOURS** nécessaires:

| Catégorie | Données | Validation |
|-----------|---------|------------|
| **Promettant(s)** | Identité complète, situation matrimoniale, coordonnées | CNI, acte naissance |
| **Bénéficiaire(s)** | Identité complète, situation matrimoniale, coordonnées | CNI, acte naissance |
| **Bien** | Adresse, lots, tantièmes, superficie Carrez | EDD, cadastre |
| **Prix** | Montant, devise, ventilation éventuelle | - |
| **Délais** | Durée promesse, date butoir | - |
| **Copropriété** | Syndic, immatriculation, fonds travaux | - |
| **Origine propriété** | Titre, publication | - |
| **Diagnostics** | DDT complet | Rapports obligatoires |

### 1.2 Informations Conditionnelles (Sections Variables)

Ces informations déclenchent des sections spécifiques:

| Donnée | Section Déclenchée | Condition |
|--------|-------------------|-----------|
| `meubles.inclus == true` | LISTE DES MEUBLES | Si meubles inclus |
| `meubles.inclus == false` | ABSENCE DE MEUBLES | Si pas de meubles |
| `indemnite_immobilisation` | Indemnité d'immobilisation | Si montant défini |
| `clause_penale` | Clause pénale | Alternative à l'indemnité |
| `sequestre.actif == true` | SÉQUESTRE | Si mise sous séquestre |
| `conditions_suspensives.pret` | Condition suspensive prêt | Si financement bancaire |
| `conditions_suspensives.vente_prealable` | Condition vente préalable | Si bien à vendre |
| `faculte_substitution.autorisee == true` | FACULTÉ DE SUBSTITUTION | Si substitution possible |
| `copropriete.ascenseurs` | Règlementation Ascenseurs | Si immeuble avec ascenseur |

---

## Étape 2: Sélection Automatique des Sections

### 2.1 Utiliser le Gestionnaire de Clauses

```bash
# Analyser les données et générer la configuration
python execution/gestionnaire_clauses_intelligent.py analyser \
    --donnees .tmp/donnees_client.json \
    --output .tmp/config_sections.json
```

### 2.2 Utiliser un Profil Pré-configuré

```bash
# Avec un profil standard
python execution/gestionnaire_clauses_intelligent.py analyser \
    --donnees .tmp/donnees_client.json \
    --profil standard_couple \
    --output .tmp/config_sections.json
```

### 2.3 Profils Disponibles

| Profil | Description | Sections Incluses |
|--------|-------------|-------------------|
| `standard_simple` | 1 promettant → 1 bénéficiaire | Prêt, indemnité, sans meubles |
| `standard_couple` | 2 promettants → 2 bénéficiaires | Prêt, indemnité, meubles, substitution |
| `complexe_investisseur` | Avec vente préalable | Séquestre, mandats, clause pénale |
| `sans_pret` | Paiement comptant | Sans condition suspensive prêt |

---

## Étape 3: Modification Dynamique (Frontend)

### 3.1 Ajouter une Section

Le notaire peut demander d'ajouter une section via l'interface:

```json
{
  "action": "ajouter",
  "section_id": "clause_personnalisee_123",
  "titre": "Clause de non-concurrence",
  "niveau": "H2",
  "contenu": "Le PROMETTANT s'engage à ne pas vendre...",
  "apres": "conditions_declarations"
}
```

**Commande équivalente:**
```bash
python execution/gestionnaire_clauses_intelligent.py feedback \
    --action ajouter \
    --cible "clause_non_concurrence" \
    --contenu "Le PROMETTANT s'engage à ne pas vendre le bien à un concurrent du BÉNÉFICIAIRE pendant une durée de 6 mois." \
    --raison "Demandé par le notaire pour un cas spécifique" \
    --notaire "Me DUPONT"
```

### 3.2 Supprimer une Section

```json
{
  "action": "supprimer",
  "section_id": "provision_frais",
  "raison": "Le client ne souhaite pas de provision"
}
```

### 3.3 Modifier une Section

```json
{
  "action": "modifier",
  "section_id": "delai",
  "nouveau_contenu": "La présente promesse est consentie pour une durée de SIX MOIS..."
}
```

---

## Étape 4: Génération du Document

### 4.1 Pipeline Complet

```bash
# 1. Sélectionner les sections
python execution/gestionnaire_clauses_intelligent.py analyser \
    --donnees .tmp/donnees_client.json \
    --profil standard_couple \
    --output .tmp/config_sections.json

# 2. Assembler le template
python execution/assembler_acte.py \
    --template promesse_vente_lots_copropriete.md \
    --donnees .tmp/donnees_client.json \
    --config .tmp/config_sections.json \
    --output .tmp/actes_generes/

# 3. Exporter en DOCX
python execution/exporter_docx.py \
    --input .tmp/actes_generes/*/acte.md \
    --output outputs/promesse_client.docx

# 4. Valider la conformité
python execution/comparer_documents_v2.py \
    --original docs_original/Trame_promesse_C.docx \
    --genere outputs/promesse_client.docx
```

### 4.2 Commande Unifiée (Recommandé)

```bash
python notaire.py promesse \
    --donnees .tmp/donnees_client.json \
    --profil standard_couple \
    --output outputs/promesse_client.docx
```

---

## Étape 5: Apprentissage Continu

### 5.1 Enregistrer le Feedback du Notaire

Après chaque génération, collecter le feedback:

```python
from execution.gestionnaire_clauses_intelligent import (
    GestionnaireClausesIntelligent,
    FeedbackNotaire
)

gestionnaire = GestionnaireClausesIntelligent()

# Feedback pour amélioration
feedback = FeedbackNotaire(
    action="ajouter",
    cible="clause_bail_commercial",
    contenu="En cas de bail commercial en cours...",
    raison="Nécessaire pour les locaux commerciaux",
    source_notaire="Me MARTIN",
    dossier_reference="2026-001-MARTIN",
    approuve=True  # Si approuvé, appliqué au catalogue
)

gestionnaire.enregistrer_feedback(feedback)
```

### 5.2 Sources d'Enrichissement

| Source | Description | Action |
|--------|-------------|--------|
| **Feedback direct** | Le notaire demande un ajout/modification | Ajout au catalogue après validation |
| **Nouvelle trame** | Nouvelle trame fournie par un notaire | Extraction et comparaison automatique |
| **Correction manuelle** | Le notaire corrige le document final | Détection des patterns récurrents |

### 5.3 Processus de Validation

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Feedback   │────▶│   Analyse    │────▶│  Validation  │────▶│  Catalogue   │
│   Reçu       │     │   Impact     │     │   Admin      │     │   Mis à jour │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## Règles d'Or

### DO ✅

1. **Toujours** utiliser le gestionnaire de clauses pour sélectionner les sections
2. **Toujours** valider la conformité avec `comparer_documents_v2.py`
3. **Toujours** enregistrer les feedbacks pour amélioration continue
4. **Utiliser** les profils pré-configurés pour les cas standards
5. **Documenter** chaque nouvelle clause ajoutée

### DON'T ❌

1. **Ne jamais** supprimer une section OBLIGATOIRE (le système l'interdit)
2. **Ne pas** modifier le catalogue directement (utiliser le feedback)
3. **Ne pas** ignorer les retours des notaires
4. **Ne pas** générer sans validation de conformité

---

## Intégration Frontend

### API REST (Modal/FastAPI) - api/main.py

L'API est déployée sur Modal.com et intégrée avec Supabase pour le multi-tenant.

**Endpoints Clauses (nouveaux):**

```
GET /clauses/sections?type_sections=fixes|variables
→ Liste les 65 sections (44 fixes + 21 variables)

GET /clauses/profils
→ Liste les profils pré-configurés (standard_simple, standard_couple, etc.)

POST /clauses/analyser
{
  "donnees": {...},
  "profil": "standard_couple"
}
→ Analyse les données et sélectionne les sections appropriées

POST /clauses/feedback
{
  "action": "ajouter|modifier|supprimer",
  "cible": "section_id",
  "contenu": "...",
  "raison": "Justification"
}
→ Enregistre un feedback pour amélioration continue

GET /clauses/suggestions?contexte=vente+avec+pret
→ Propose des clauses pertinentes pour le contexte
```

**Endpoints Agent (existants - payoss):**

```
POST /agent/execute
{
  "texte": "Crée une promesse Martin→Dupont, 450000€"
}
→ Génère l'acte en langage naturel

POST /agent/feedback
{
  "dossier_id": "...",
  "type_feedback": "correction|validation|suggestion",
  "champ": "vendeur.nom",
  "valeur_corrigee": "..."
}
→ Feedback pour apprentissage continu
```

**Déploiement Modal:**
```bash
modal deploy api/modal_app.py
# Endpoint: https://notaire-ai--fastapi-app.modal.run/
```

---

## Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `schemas/clauses_promesse_catalogue.json` | Catalogue des 65 sections (44 fixes + 21 variables) |
| `execution/gestionnaire_clauses_intelligent.py` | Gestionnaire de sélection et modification |
| `api/main.py` | **API REST complète** (1000+ lignes, multi-tenant) |
| `api/modal_app.py` | **Déploiement Modal** (CRON learning, scaling) |
| `data/feedback_notaires.json` | Historique des feedbacks |
| `templates/promesse_vente_lots_copropriete.md` | Template unifié |
| `templates/sections/partie_developpee_promesse.md` | Sections spécifiques promesse |

---

## Métriques de Qualité

| Métrique | Seuil | Action si Non Atteint |
|----------|-------|----------------------|
| **Conformité structurelle** | ≥85% | Analyser sections manquantes |
| **Sections obligatoires** | 100% | Erreur bloquante |
| **Cohérence données** | 100% | Validation échoue |
| **Feedback traité** | <24h | Notification admin |

---

## Exemple Complet

```bash
# 1. Préparer les données
cp exemples/donnees_promesse_exemple.json .tmp/donnees_client.json

# 2. Analyser et sélectionner
python execution/gestionnaire_clauses_intelligent.py analyser \
    --donnees .tmp/donnees_client.json \
    --profil standard_couple

# 3. Générer
python notaire.py promesse \
    --donnees .tmp/donnees_client.json \
    --output outputs/promesse_client.docx

# 4. Le notaire demande d'ajouter une clause
python execution/gestionnaire_clauses_intelligent.py feedback \
    --action ajouter \
    --cible "clause_specifique_notaire" \
    --contenu "..." \
    --notaire "Me MARTIN" \
    --approuve

# 5. Régénérer avec la nouvelle clause
python notaire.py promesse \
    --donnees .tmp/donnees_client.json \
    --output outputs/promesse_client_v2.docx
```

---

## Roadmap

- [ ] **v1.1** - Interface graphique pour sélection des sections
- [ ] **v1.2** - Suggestions automatiques basées sur le type de bien
- [ ] **v1.3** - Détection automatique des incohérences
- [ ] **v2.0** - Apprentissage ML des patterns de modification

---

*Ce workflow garantit des promesses de vente fiables, flexibles et en amélioration continue.*
