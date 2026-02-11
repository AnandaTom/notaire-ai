# Intégration Viager v2.0.0 dans le Chat Existant (Payos)

> **Date**: 11/02/2026
> **Public**: Payos (front-end chat), Tom/Augustin (backend)
> **Objectif**: Intégrer les nouvelles fonctionnalités viager + création copro dans le chat existant connecté à Modal

---

## 🎯 Situation Actuelle

### Architecture Existante (CORRECTE)

```
Chat de Payos (Front-end)
    ↓ HTTP/WebSocket
Modal API (api/main.py)
    ↓
Backend v2.0.0 (7 templates PROD, 257 tests)
    ↓
Export DOCX
```

**Endpoints déjà en production** :
- `POST /promesses/generer` - Génération complète
- `POST /promesses/detecter-type` - Détection automatique (nouveau: viager)
- `POST /promesses/valider` - Validation sémantique
- `GET /questions/promesse` - Questions dynamiques (nouveau: section viager)
- `POST /workflow/promesse/start` - Workflow complet
- `GET /workflow/promesse/{id}/generate-stream` - SSE pour progression

---

## 🆕 Nouveautés v2.0.0 à Intégrer

### 1. Support Viager Complet

**Backend prêt** :
- Template dédié `promesse_viager.md` avec 4 sections spécifiques
- Détection cross-catégorie (maison viager, appart viager, terrain viager)
- 19 nouvelles questions (section `15_viager`)
- Validation sémantique (bouquet obligatoire, rente obligatoire)

**Ce qui change pour le chat** :

#### A. Détection Viager Automatique

**Endpoint existant** : `POST /promesses/detecter-type`

**Requête** (inchangée) :
```json
{
  "donnees": {
    "prix": {
      "type_vente": "viager",
      "montant": 150000,
      "bouquet": {"montant": 50000},
      "rente_viagere": {"montant": 1200, "periodicite": "mensuelle"}
    },
    "bien": {"nature": "appartement", "adresse": {...}}
  }
}
```

**Réponse** (enrichie avec v2.0.0) :
```json
{
  "type_promesse": "promesse_vente",
  "categorie_bien": "COPROPRIETE",
  "sous_type": "viager",
  "confiance": 95,
  "marqueurs_detectes": ["type_vente_viager", "bouquet", "rente_viagere", "duh_reserve"],
  "template_recommande": "promesse_viager.md",
  "sections_conditionnelles": [
    "section_sante_promettant",
    "section_droit_usage_habitation",
    "section_rente_viagere",
    "section_garanties_viager"
  ]
}
```

**Action Payos** :
- Si `sous_type == "viager"` → Afficher badge "Viager" dans l'UI
- Activer section de questions viager (voir B)

#### B. Questions Viager Dynamiques

**Endpoint existant** : `GET /questions/promesse`

**Requête** (nouvelle syntaxe v2.0.0) :
```
GET /questions/promesse?sous_type=viager&section=15_viager
```

**Réponse** (nouvelles questions activées) :
```json
{
  "sections": [
    {
      "id": "15_viager",
      "titre": "Modalités du Viager",
      "ordre": 15,
      "questions": [
        {
          "id": "viager_type_vente",
          "texte": "Type de vente en viager ?",
          "type": "select",
          "variable": "prix.type_vente",
          "options": ["Viager occupé", "Viager libre"],
          "obligatoire": true
        },
        {
          "id": "viager_bouquet",
          "texte": "Montant du bouquet (capital initial) ?",
          "type": "number",
          "variable": "prix.bouquet.montant",
          "unite": "EUR",
          "obligatoire": true
        },
        {
          "id": "viager_rente_montant",
          "texte": "Montant de la rente viagère ?",
          "type": "number",
          "variable": "prix.rente_viagere.montant",
          "unite": "EUR",
          "obligatoire": true
        },
        {
          "id": "viager_rente_periodicite",
          "texte": "Périodicité de la rente ?",
          "type": "select",
          "variable": "prix.rente_viagere.periodicite",
          "options": ["mensuelle", "trimestrielle", "annuelle"],
          "obligatoire": true
        },
        {
          "id": "viager_indexation",
          "texte": "Indexation de la rente ?",
          "type": "select",
          "variable": "prix.rente_viagere.indexation.indice",
          "options": ["IRL", "IPC", "ICC", "Aucune"],
          "par_defaut": "IRL"
        },
        {
          "id": "viager_duh_reserve",
          "texte": "Le vendeur se réserve-t-il un droit d'usage et d'habitation (DUH) ?",
          "type": "boolean",
          "variable": "bien.droit_usage_habitation.reserve",
          "help": "Le DUH permet au vendeur de continuer à occuper le bien",
          "par_defaut": true
        },
        {
          "id": "viager_age_creancier",
          "texte": "Âge du crédirentier (vendeur) ?",
          "type": "number",
          "variable": "promettants[0].age",
          "unite": "ans",
          "obligatoire": false,
          "help": "Recommandé pour le calcul actuariel"
        },
        {
          "id": "viager_certificat_medical",
          "texte": "Un certificat médical attestant de la santé du vendeur a-t-il été fourni ?",
          "type": "boolean",
          "variable": "promettants[0].sante.certificat_medical.fourni",
          "help": "Recommandé (art. 1975 C. civ.) pour éviter les contestations",
          "par_defaut": false
        },
        {
          "id": "viager_privilege_vendeur",
          "texte": "Le vendeur souhaite-t-il bénéficier du privilège du vendeur ?",
          "type": "boolean",
          "variable": "garanties.privilege_vendeur",
          "help": "Garantie supplémentaire en cas de non-paiement de la rente",
          "par_defaut": true
        },
        {
          "id": "viager_rachat_possible",
          "texte": "Possibilité de rachat de la rente par l'acquéreur ?",
          "type": "boolean",
          "variable": "prix.rente_viagere.rachat.possible",
          "par_defaut": false
        }
      ]
    }
  ]
}
```

**Action Payos** :
- Afficher ces questions uniquement si `sous_type == "viager"` détecté
- Validation inline : bouquet + rente obligatoires si viager
- Badge warning si pas de certificat médical fourni

#### C. Génération avec Viager

**Endpoint existant** : `POST /workflow/promesse/{id}/generate`

**Requête** (inchangée, données enrichies) :
```json
{
  "donnees": {
    "prix": {
      "type_vente": "viager",
      "bouquet": {"montant": 50000},
      "rente_viagere": {
        "montant": 1200,
        "periodicite": "mensuelle",
        "indexation": {"indice": "IRL", "reference": "2026-Q1"}
      },
      "valeur_venale": 350000,
      "valeur_economique": 150000
    },
    "bien": {
      "droit_usage_habitation": {
        "reserve": true,
        "obligations": "Entretien courant à la charge du crédirentier",
        "restrictions": "Interdiction de sous-louer"
      }
    },
    "promettants": [{
      "age": 78,
      "sante": {
        "certificat_medical": {
          "fourni": true,
          "date": "2026-02-01",
          "medecin": "Dr. Martin LEFEBVRE"
        }
      }
    }],
    "garanties": {
      "privilege_vendeur": true,
      "solidarite_acquereurs": true
    }
  }
}
```

**Réponse** (inchangée) :
```json
{
  "workflow_id": "wf_abc123",
  "fichier_genere": "/outputs/etude_123/promesse_viager_20260211.docx",
  "template_utilise": "promesse_viager.md",
  "sections_incluses": [
    "section_sante_promettant",
    "section_droit_usage_habitation",
    "section_rente_viagere",
    "section_garanties_viager"
  ],
  "score_conformite": 92.5,
  "duree_ms": 5800
}
```

**Action Payos** :
- Rien à changer côté requête, le backend détecte automatiquement le viager
- Afficher les sections incluses dans le résumé

---

### 2. Support Création Copropriété

**Backend prêt** :
- 6 guards ajoutés dans `promesse_vente_lots_copropriete.md`
- Détection implicite (pas de syndic + pas de règlement + lots)
- 6 nouvelles questions (section `8f_creation_copropriete`)

**Ce qui change pour le chat** :

#### A. Détection Création Copro

**Endpoint existant** : `POST /promesses/detecter-type`

**Requête** :
```json
{
  "donnees": {
    "bien": {
      "nature": "appartement",
      "copropriete": {
        "lots": [{"numero": 12, "nature": "appartement"}],
        "syndic": null,
        "reglement": null,
        "en_creation": true
      }
    }
  }
}
```

**Réponse** :
```json
{
  "categorie_bien": "COPROPRIETE",
  "sous_type": "creation",
  "confiance": 85,
  "marqueurs_detectes": ["lots_presents", "pas_syndic", "pas_reglement", "en_creation_true"],
  "template_recommande": "promesse_vente_lots_copropriete.md",
  "avertissement": "Copropriété en cours de création - sections syndic/règlement masquées"
}
```

**Action Payos** :
- Badge "Création copro" si `sous_type == "creation"`
- Griser les questions syndic/règlement/exercice

#### B. Questions Création Copro

**Endpoint** : `GET /questions/promesse?categorie=copropriete&sous_type=creation`

**Réponse** :
```json
{
  "sections": [
    {
      "id": "8f_creation_copropriete",
      "titre": "Création de la Copropriété",
      "ordre": 8.5,
      "questions": [
        {
          "id": "creation_futur_reglement_notaire",
          "texte": "Notaire chargé du règlement de copropriété ?",
          "type": "text",
          "variable": "copropriete.futur_reglement.notaire"
        },
        {
          "id": "creation_futur_reglement_date",
          "texte": "Date prévue de signature du règlement ?",
          "type": "date",
          "variable": "copropriete.futur_reglement.date_prevue"
        },
        {
          "id": "creation_promoteur",
          "texte": "Nom du promoteur ?",
          "type": "text",
          "variable": "copropriete.promoteur.nom"
        }
      ]
    }
  ]
}
```

---

## 🚀 Checklist d'Intégration pour Payos

### Phase 1 : Détection Viager (1 jour)

- [ ] **Appeler `/promesses/detecter-type` dès le début du workflow**
  - Déclencher après les 3 premières questions (parties, bien, prix)
  - Afficher badge "Viager" si `sous_type == "viager"`

- [ ] **Gérer les réponses enrichies**
  ```typescript
  interface DetectionResponse {
    type_promesse: string;
    categorie_bien: "COPROPRIETE" | "HORS_COPROPRIETE" | "TERRAIN_A_BATIR";
    sous_type?: "viager" | "creation" | "lotissement" | "groupe_habitations";
    confiance: number;
    marqueurs_detectes: string[];
    template_recommande: string;
    sections_conditionnelles?: string[];
  }
  ```

- [ ] **Afficher les informations de détection**
  - Badge de statut : "Détecté : Viager" avec confiance (%)
  - Tooltip : Marqueurs détectés (type_vente, bouquet, rente, DUH)

### Phase 2 : Questions Viager (2 jours)

- [ ] **Activer section viager si `sous_type == "viager"`**
  ```typescript
  const questionsSections = await fetch(
    `/questions/promesse?sous_type=${detectionResult.sous_type}`
  ).then(r => r.json());

  // Filtrer section 15_viager
  const questionViager = questionsSections.sections.find(
    s => s.id === "15_viager"
  );
  ```

- [ ] **Ajouter validation inline spécifique viager**
  - `bouquet.montant` obligatoire si viager
  - `rente_viagere.montant` obligatoire si viager
  - Warning si `certificat_medical.fourni == false`
  - Warning si `age` non renseigné

- [ ] **Enrichir l'UI des questions viager**
  - Icône 🏡 pour DUH (droit d'usage et d'habitation)
  - Icône 💰 pour rente/bouquet
  - Icône 📋 pour certificat médical
  - Tooltip explicatif pour chaque concept

### Phase 3 : Génération Viager (1 jour)

- [ ] **Aucun changement côté requête** (backend détecte automatiquement)

- [ ] **Afficher les sections incluses dans le résumé**
  ```typescript
  if (result.sections_incluses?.includes("section_rente_viagere")) {
    afficherSection("✅ Rente viagère configurée");
  }
  if (result.sections_incluses?.includes("section_droit_usage_habitation")) {
    afficherSection("✅ Droit d'usage et d'habitation réservé");
  }
  ```

- [ ] **Téléchargement DOCX** (inchangé)
  ```typescript
  const docxUrl = `/files/${result.fichier_genere}`;
  window.open(docxUrl, '_blank');
  ```

### Phase 4 : Création Copro (1 jour)

- [ ] **Détecter `sous_type == "creation"`**
  - Badge "Copropriété en création"
  - Griser questions syndic/règlement/exercice

- [ ] **Activer section `8f_creation_copropriete`**
  - Questions : futur_reglement, promoteur, date_prevue

- [ ] **Afficher message contextuel**
  > "La copropriété est en cours de constitution. Le règlement et le syndic seront désignés ultérieurement."

### Phase 5 : Tests E2E (1 jour)

- [ ] **Test viager complet**
  - Maison viager avec DUH
  - Rente + bouquet + indexation
  - Certificat médical fourni
  - Privilège vendeur activé

- [ ] **Test viager cross-catégories**
  - Appartement copro viager
  - Terrain viager (rare mais supporté)
  - Maison hors copro viager

- [ ] **Test création copro**
  - Appartement neuf, pas de syndic
  - Futur règlement renseigné
  - Promoteur identifié

- [ ] **Test non-régression**
  - Promesse standard copro (pas viager)
  - Promesse hors copro (pas viager)
  - Promesse terrain (pas viager)

---

## 📊 Métriques de Succès

| Métrique | Avant v2.0.0 | Après v2.0.0 |
|----------|--------------|--------------|
| **Types supportés** | 3 catégories | 3 catégories + 6 sous-types |
| **Questions totales** | 97 | 122 (+25 viager/création) |
| **Détection viager** | ❌ | ✅ 95% confiance |
| **Validation sémantique** | Basique | Règles métier viager |
| **Templates PROD** | 6 | 7 (+ viager) |

---

## 🐛 Points d'Attention

### 1. Validation API Viager

**Bug corrigé dans v2.0.0** : `ResultatValidationPromesse` est un dataclass, pas un dict.

❌ **Ancien code (ne pas utiliser)** :
```python
validation = gestionnaire.valider(donnees)
if validation.get('erreurs'):  # ❌ ERREUR
    ...
```

✅ **Nouveau code** :
```python
validation = gestionnaire.valider(donnees)
if validation.erreurs:  # ✅ Attribut dataclass
    ...
```

**Action Payos** : Si vous appelez `/promesses/valider` via API, la réponse JSON est correcte (pas de changement).

### 2. Migration Supabase

La migration `20260210_viager_support.sql` ajoute :
- Colonne `sous_type VARCHAR(50)`
- Colonnes analytics : `viager_bouquet`, `viager_rente_mensuelle`, `viager_valeur_venale`

**Action Payos** : Aucun changement côté chat, mais les stats admin afficheront les données viager.

### 3. Coût API

**Viager = +4 sections conditionnelles** → Légère augmentation tokens (~15%).

**Avant** : ~8,000 tokens (promesse standard)
**Après** : ~9,200 tokens (promesse viager)

**Action** : Coût négligeable avec Opus 4.6 ($0.015/1k input tokens → +$0.02 par génération viager).

---

## 📝 Exemple Complet : Flow Viager dans le Chat

### 1. User : "Je veux créer une promesse de vente en viager"

**Chat détecte "viager" dans l'input** → Appelle `/promesses/detecter-type` avec données partielles.

### 2. Système : Détection automatique

```json
{
  "sous_type": "viager",
  "confiance": 40,
  "marqueurs_detectes": ["viager_in_text"],
  "message": "Viager détecté. Collecte des informations spécifiques en cours..."
}
```

### 3. Chat pose les questions standard (parties, bien, prix)

```
Q1: Nom du vendeur ? → "Jean Dupont"
Q2: Adresse du bien ? → "12 rue de la Paix, Lyon"
Q3: Nature du bien ? → "Maison"
Q4: Prix de vente ? → "150 000 €"
```

### 4. Système réanalyse avec plus de contexte

```json
{
  "sous_type": "viager",
  "confiance": 75,
  "marqueurs_detectes": ["viager_in_text", "maison_detected"],
  "message": "Viager sur maison. Activation section viager..."
}
```

### 5. Chat active questions viager (section 15)

```
Q5: Montant du bouquet ? → "50 000 €"
Q6: Montant de la rente mensuelle ? → "1 200 €"
Q7: Le vendeur se réserve le droit d'usage ? → "Oui"
Q8: Âge du vendeur ? → "78 ans"
Q9: Certificat médical fourni ? → "Oui"
```

### 6. Système valide les données

```json
{
  "valide": true,
  "confiance": 95,
  "marqueurs_detectes": ["type_vente_viager", "bouquet", "rente_viagere", "duh_reserve", "age_renseigne"],
  "warnings": [
    "Pensez à joindre le certificat médical au dossier"
  ]
}
```

### 7. Génération

```
POST /workflow/promesse/{id}/generate
→ Template: promesse_viager.md
→ Sections: sante + DUH + rente + garanties
→ Export: promesse_viager_20260211_Jean_DUPONT.docx
```

### 8. Téléchargement

```
Chat affiche:
✅ Promesse de vente en viager générée avec succès !
📄 Télécharger le document (92 Ko)

Sections incluses:
✅ Santé du promettant (art. 1974-1975)
✅ Droit d'usage et d'habitation réservé
✅ Rente viagère indexée sur IRL
✅ Privilège du vendeur activé
```

---

## 🎯 Résumé : Ce Que Payos Doit Faire

| Tâche | Effort | Priorité | Dépendance |
|-------|--------|----------|------------|
| Appeler `/promesses/detecter-type` | 2h | 🔴 CRITIQUE | Aucune |
| Gérer `sous_type` dans réponses | 1h | 🔴 CRITIQUE | Détection |
| Activer section `15_viager` | 4h | 🔴 HAUTE | Détection |
| Validation inline viager | 3h | 🟡 MOYENNE | Questions |
| UI badges/tooltips viager | 2h | 🟡 MOYENNE | Questions |
| Afficher sections incluses | 1h | 🟢 BASSE | Génération |
| Support création copro | 4h | 🟡 MOYENNE | Détection |
| Tests E2E complets | 8h | 🔴 HAUTE | Tout |

**Total : ~3 jours** (1 dev)

---

## 📚 Ressources

- [API Documentation](../api/main.py) - Tous les endpoints
- [Schéma Viager v4.1.0](../schemas/variables_promesse_vente.json) - Structure données
- [Questions Viager v3.2.0](../schemas/questions_promesse_vente.json) - Section 15
- [Template Viager](../templates/promesse_viager.md) - Structure document
- [Tests Viager](../tests/test_gestionnaire_promesses.py) - 19 tests unitaires + E2E

---

**Dernière mise à jour** : 11/02/2026
**Version backend** : v2.0.0
**Version API** : Inchangée (endpoints rétrocompatibles)
