# Stratégie Génération d'Actes - Axes d'Amélioration

## Notre Avantage Compétitif Unique

**Génération d'actes notariaux complets en < 1 minute, 100% fidèles aux trames.**

Aucun concurrent ne fait ça. C'est notre moat.

---

## Axes Prioritaires pour Booster l'Efficacité

### 1. Pipeline Données → Acte (Optimiser le flux)

**Problème actuel :** Les données arrivent des questionnaires, mais le mapping vers les templates peut être amélioré.

**Actions :**
- [ ] Créer un mapping unifié `questionnaire → variables_acte` pour chaque type
- [ ] Valider automatiquement la complétude des données avant génération
- [ ] Pré-remplir intelligemment les champs manquants (valeurs par défaut juridiques)

**Impact :** Réduire les erreurs et les allers-retours

---

### 2. Templates Intelligents (Améliorer la qualité)

**Problème actuel :** Les templates sont statiques, certains cas limites ne sont pas couverts.

**Actions :**
- [ ] Enrichir `promesse_catalogue_unifie.json` avec plus de clauses conditionnelles
- [ ] Créer des profils de génération (standard, premium, simplifié)
- [ ] Ajouter détection automatique du type de promesse (standard/multi-biens/mobilier)

**Impact :** Couvrir 95%+ des cas réels sans intervention manuelle

---

### 3. Extraction de Titres de Propriété (Game Changer)

**Problème actuel :** Le notaire doit souvent re-saisir des infos déjà présentes dans le titre.

**Actions :**
- [ ] Améliorer `extraire_titre.py` avec plus de patterns regex
- [ ] Ajouter OCR pour les titres scannés (pytesseract)
- [ ] Créer workflow : Titre PDF → JSON → Promesse/Vente pré-remplie

**Impact :** Économiser 30-45min par dossier (extraction manuelle)

---

### 4. Validation Juridique Automatique

**Problème actuel :** L'IA génère, mais le notaire doit tout vérifier.

**Actions :**
- [ ] Implémenter validations automatiques :
  - Quotités = 100%
  - Régime matrimonial → conjoint requis ?
  - Surface Carrez obligatoire si lot > 8m²
  - Cohérence prix/financement
- [ ] Alerter sur les incohérences AVANT génération
- [ ] Suggérer des corrections

**Impact :** Réduire les corrections post-génération de 50%

---

### 5. Feedback Loop (Amélioration Continue)

**Problème actuel :** On ne sait pas où les actes générés nécessitent des corrections.

**Actions :**
- [ ] Tracker les modifications manuelles post-génération
- [ ] Identifier les patterns récurrents de correction
- [ ] Enrichir automatiquement les templates/règles

**Impact :** L'IA s'améliore avec chaque acte généré

---

## Métriques à Suivre

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| Temps génération | < 30s | ~15s |
| Taux acceptation 1er jet | > 90% | À mesurer |
| Corrections manuelles/acte | < 3 | À mesurer |
| Types d'actes couverts | 10+ | 4 |
| Conformité structurelle | > 95% | 80-91% |

---

## Types d'Actes à Ajouter (Par priorité)

### Priorité 1 (Demande forte)
1. **Compromis de vente** - Variante de la promesse
2. **Acte de vente définitif** - ✅ Fait (80.2%)
3. **Promesse unilatérale** - ✅ Fait (88.9%)

### Priorité 2 (Demande moyenne)
4. **Donation simple** - Transmission patrimoine
5. **Donation-partage** - Anticipation succession
6. **Attestation de propriété** - Post-succession

### Priorité 3 (Niches lucratives)
7. **Bail commercial** - Haute valeur ajoutée
8. **Statuts SCI** - Création sociétés
9. **Cession parts sociales** - M&A simplifié

---

## Architecture Technique Recommandée

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRÉES DONNÉES                          │
├─────────────────────────────────────────────────────────────┤
│  Questionnaire   │   Titre PDF   │   Données manuelles      │
│  (chiffré)       │   (OCR/ML)    │   (notaire)              │
└────────┬─────────┴───────┬───────┴───────────┬──────────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│              NORMALISATION & VALIDATION                      │
│  - Mapping vers schéma unifié                               │
│  - Validation juridique auto                                │
│  - Détection incohérences                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              MOTEUR DE GÉNÉRATION                           │
│  - Sélection template (détection auto)                      │
│  - Injection variables Jinja2                               │
│  - Gestion clauses conditionnelles                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              EXPORT & POST-TRAITEMENT                        │
│  - Markdown → DOCX (formatage notarial)                     │
│  - Validation conformité (comparaison trame)                │
│  - Génération PDF si demandé                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              FEEDBACK & AMÉLIORATION                         │
│  - Tracking corrections notaire                             │
│  - Enrichissement catalogues                                │
│  - Self-anneal sur erreurs récurrentes                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Wins Immédiats

### 1. Améliorer le mapping questionnaire (1-2 jours)
Fichier : `web/mapping-formulaire.js`

Les données du questionnaire doivent mapper 1:1 vers `schemas/variables_*.json`.

### 2. Ajouter validation pré-génération (1 jour)
Dans `execution/valider_acte.py`, ajouter :
```python
def valider_avant_generation(donnees):
    erreurs = []
    # Vérifier quotités
    if sum(q['valeur'] for q in donnees.get('quotites_vendues', [])) != 100:
        erreurs.append("Quotités vendues != 100%")
    # Vérifier régime matrimonial
    # etc.
    return erreurs
```

### 3. Créer endpoint API unifié (1 jour)
```
POST /api/generer-acte
{
  "type": "promesse_vente",
  "donnees": {...},
  "options": {
    "format": "docx",
    "valider": true
  }
}
```

### 4. Dashboard KPI génération (déjà fait ✅)
- Temps moyen génération
- Taux acceptation
- Types les plus générés

---

## Ressources Existantes à Exploiter

| Fichier | Usage |
|---------|-------|
| `schemas/variables_vente.json` | Structure données vente |
| `schemas/promesse_catalogue_unifie.json` | 4 trames promesse |
| `templates/vente_lots_copropriete.md` | Template vente (80.2%) |
| `execution/assembler_acte.py` | Moteur génération |
| `execution/valider_acte.py` | Validation données |
| `execution/gestionnaire_promesses.py` | Orchestration promesses |

---

## Prochaines Étapes Concrètes

1. **Cette semaine :** Finaliser dashboard + tester relances clients
2. **Semaine prochaine :** Améliorer mapping questionnaire → génération
3. **Mois prochain :** Ajouter extraction titre de propriété améliorée
4. **Trimestre :** Ajouter 2 nouveaux types d'actes (donation, compromis)

---

*Document stratégique - Février 2026*
