# Directive : Création d'une Promesse Unilatérale de Vente - Lots de Copropriété

**Version**: 2.0.0 | **Date**: 2026-01-28

---

## Objectif

Guider la création complète d'une **promesse unilatérale de vente** de lots de copropriété, avec support de **4 types de promesses** adaptés aux différents cas d'usage.

---

## 🆕 Système Multi-Templates (v1.4.0)

Le système détecte automatiquement le type de promesse approprié:

| Type | Template | Cas d'usage | Bookmarks |
|------|----------|-------------|-----------|
| **Standard** | `promesse_standard.md` | 1 bien simple, pas de mobilier | 298 |
| **Premium** | `promesse_premium.md` | Diagnostics exhaustifs, agences | 359 |
| **Avec mobilier** | `promesse_avec_mobilier.md` | Vente meublée | 312 |
| **Multi-biens** | `promesse_multi_biens.md` | Lot + parking + cave | 423 |

### Détection Automatique

```python
from execution.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()
detection = gestionnaire.detecter_type(donnees)

# Résultat:
# type_promesse: "avec_mobilier"
# confiance: 0.85
# sections_recommandees: ["entete", "mobilier_vendu", ...]
```

### Règles de Détection

| Priorité | Condition | Type |
|----------|-----------|------|
| 1 | `len(biens) > 1` | multi_biens |
| 2 | `mobilier.existe == True` | avec_mobilier |
| 3 | `diagnostics.exhaustifs == True` | premium |
| 4 | Par défaut | standard |

---

## Différences avec l'acte de vente définitif

| Élément | Promesse Unilatérale | Acte de Vente |
|---------|----------------------|---------------|
| **Parties** | Promettant / Bénéficiaire | Vendeur / Acquéreur |
| **Engagement** | Unilatéral (promettant seul) | Synallagmatique (réciproque) |
| **Indemnité d'immobilisation** | Obligatoire (généralement 10%) | Non applicable |
| **Option** | Le bénéficiaire a une option | Pas d'option |
| **Délai de réalisation** | Date limite pour réitérer | Transfert immédiat |
| **Conditions suspensives** | Fréquentes (prêt, préemption) | Rares |

---

## Ressources

| Ressource | Chemin |
|-----------|--------|
| **Gestionnaire principal** | `execution/gestionnaire_promesses.py` |
| **Catalogue unifié** | `schemas/promesse_catalogue_unifie.json` |
| Template DOCX original | `docs_originels/Trame promesse unilatérale de vente lots de copropriété.docx` |
| Templates spécialisés | `templates/promesse/*.md` |
| Schéma variables | `schemas/variables_promesse_vente.json` |
| Questions notaire | `schemas/questions_promesse_vente.json` |
| Script assemblage | `execution/assembler_acte.py` |
| Script export DOCX | `execution/exporter_docx.py` |

---

## Flux de Travail Principal

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CRÉATION PROMESSE UNILATÉRALE DE VENTE               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. COLLECTE DES INFORMATIONS                                          │
│     ├─► Via dialogue: schemas/questions_promesse_vente.json            │
│     ├─► Via titre: extraire_titre_propriete.py                         │
│     └─► Via API: POST /titres/{id}/vers-promesse                       │
│                                                                        │
│  2. DÉTECTION DU TYPE                                                  │
│     ├─► Exécuter gestionnaire_promesses.detecter_type()                │
│     └─► Résultat: standard | premium | avec_mobilier | multi_biens     │
│                                                                        │
│  3. VALIDATION DES DONNÉES                                             │
│     ├─► Exécuter gestionnaire_promesses.valider()                      │
│     ├─► Règles obligatoires (promettants, prix, délai)                 │
│     └─► Règles conditionnelles (prêt, mobilier, multi-biens)           │
│                                                                        │
│  4. GÉNÉRATION                                                         │
│     ├─► Exécuter gestionnaire_promesses.generer()                      │
│     ├─► Sélection automatique du template                              │
│     └─► Export DOCX fidèle à la trame                                  │
│                                                                        │
│  5. ARCHIVAGE (optionnel)                                              │
│     └─► Sauvegarde dans Supabase (titres_propriete, promesses_generees)│
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Méthode 1: Génération Rapide (CLI)

### Depuis des données complètes

```bash
python notaire.py promesse-avancee generer \
    --donnees donnees_promesse.json \
    --output promesse_client.docx
```

### Depuis un titre de propriété

```bash
# 1. Extraire le titre
python notaire.py extraire titre.pdf -o titre.json

# 2. Générer la promesse
python notaire.py promesse-avancee depuis-titre \
    --titre titre.json \
    --beneficiaires beneficiaires.json \
    --prix 250000 \
    --output promesse_client.docx
```

### Avec profil prédéfini

```bash
python notaire.py promesse-avancee generer \
    --donnees donnees.json \
    --profil agence_premium \
    --output promesse_premium.docx
```

---

## Méthode 2: Via API

### Générer une promesse

```bash
curl -X POST "https://notaire-ai--fastapi-app.modal.run/promesses/generer" \
    -H "X-API-Key: votre_cle" \
    -H "Content-Type: application/json" \
    -d '{
        "promettants": [...],
        "beneficiaires": [...],
        "bien": {...},
        "prix": {"montant": 250000},
        "delai_realisation": "2026-06-30"
    }'
```

### Depuis un titre existant

```bash
curl -X POST "https://notaire-ai--fastapi-app.modal.run/titres/{titre_id}/vers-promesse" \
    -H "X-API-Key: votre_cle" \
    -d '{
        "beneficiaires": [...],
        "prix": {"montant": 250000},
        "financement": {"pret": true, "montant": 200000}
    }'
```

---

## Méthode 3: Via Python

```python
from execution.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()

# Option A: Depuis des données
resultat = gestionnaire.generer(donnees)

# Option B: Depuis un titre
donnees, resultat = gestionnaire.generer_depuis_titre(
    titre_data=titre,
    beneficiaires=[{"nom": "DUPONT", "prenoms": "Jean", ...}],
    prix={"montant": 250000},
    financement={"pret": True, "montant": 200000, "taux_max": 4.5},
    options={
        "mobilier": {"existe": True, "liste": [...]},
        "indemnite": {"montant": 25000},
        "delai_realisation": "2026-06-30"
    }
)

print(f"Type: {resultat.type_promesse.value}")
print(f"DOCX: {resultat.fichier_docx}")
```

---

## Structure des Données par Type

### Type Standard (minimal)

```json
{
    "promettants": [{
        "nom": "MARTIN",
        "prenoms": "Pierre",
        "date_naissance": "1960-05-20",
        "adresse": "5 rue du Commerce, 69002 Lyon",
        "situation_matrimoniale": "marie"
    }],
    "beneficiaires": [{
        "nom": "DUPONT",
        "prenoms": "Jean",
        "date_naissance": "1985-03-15",
        "adresse": "10 rue des Lilas, 69001 Lyon"
    }],
    "bien": {
        "adresse": "25 avenue Jean Jaurès",
        "code_postal": "69007",
        "ville": "Lyon",
        "copropriete": true,
        "lots": [{
            "numero": 12,
            "nature": "Appartement",
            "tantiemes": 150,
            "carrez": 75.50
        }]
    },
    "prix": {"montant": 250000},
    "financement": {"pret": true, "montant": 200000},
    "delai_realisation": "2026-06-30"
}
```

### Type Avec Mobilier

Ajouter la section mobilier:

```json
{
    "mobilier": {
        "existe": true,
        "prix_total": 15000,
        "liste": [
            {"designation": "Cuisine équipée", "etat": "Bon", "valeur": 8000},
            {"designation": "Réfrigérateur Samsung", "etat": "Très bon", "valeur": 1200},
            {"designation": "Lave-vaisselle Bosch", "etat": "Bon", "valeur": 800}
        ]
    }
}
```

### Type Multi-Biens

Remplacer `bien` par `biens`:

```json
{
    "biens": [
        {
            "adresse": "25 avenue Jean Jaurès, Apt 12",
            "nature": "Appartement",
            "cadastre": {"section": "AB", "numero": "123"},
            "lots": [{"numero": 12, "tantiemes": 150}],
            "prix": 230000
        },
        {
            "adresse": "25 avenue Jean Jaurès, Parking 45",
            "nature": "Parking",
            "lots": [{"numero": 45, "tantiemes": 10}],
            "prix": 15000
        },
        {
            "adresse": "25 avenue Jean Jaurès, Cave 8",
            "nature": "Cave",
            "lots": [{"numero": 8, "tantiemes": 5}],
            "prix": 5000
        }
    ]
}
```

### Type Premium

Ajouter les sections exhaustives:

```json
{
    "bien": {
        "localisation_detaillee": true,
        "lieu_dit": "Les Brotteaux",
        "voie_acces": "Par la rue de la République",
        "coordonnees_gps": "45.7640° N, 4.8357° E"
    },
    "diagnostics": {
        "exhaustifs": true,
        "dpe": {"date": "2026-01-15", "classe": "C"},
        "amiante": {"date": "2026-01-15", "presence": false},
        "plomb": {"date": "2026-01-15"},
        "electricite": {"date": "2026-01-15"},
        "gaz": {"date": "2026-01-15"},
        "termites": {"date": "2026-01-15"},
        "erp": {"date": "2026-01-15"}
    }
}
```

---

## Profils Prédéfinis

| Profil | Type | Description |
|--------|------|-------------|
| `particulier_simple` | standard | 1 vendeur → 1 acquéreur |
| `particulier_meuble` | avec_mobilier | Avec liste de mobilier |
| `agence_premium` | premium | Documentation complète |
| `investisseur_multi` | multi_biens | Plusieurs biens, substitution |
| `sans_pret` | standard | Achat comptant |

```python
# Appliquer un profil
donnees = gestionnaire.appliquer_profil(donnees, "agence_premium")
resultat = gestionnaire.generer(donnees)
```

---

## Validation

### Règles Obligatoires

| Champ | Règle | Message |
|-------|-------|---------|
| `promettants` | Au moins 1 | "Au moins un promettant requis" |
| `beneficiaires` | Au moins 1 | "Au moins un bénéficiaire requis" |
| `bien.adresse` | Non vide | "Adresse du bien requise" |
| `prix.montant` | > 0 | "Prix de vente requis" |
| `delai_realisation` | Non vide | "Délai de réalisation requis" |

### Règles Conditionnelles

| Condition | Champs requis |
|-----------|---------------|
| `financement.pret == true` | montant, taux_max, duree |
| `mobilier.existe == true` | liste, prix_total |
| `len(biens) > 1` | adresse et cadastre pour chaque bien |

---

## Sections Conditionnelles

| Section | Condition | Types |
|---------|-----------|-------|
| Mobilier vendu | `mobilier.existe == true` | avec_mobilier |
| Localisation détaillée | `bien.localisation_detaillee == true` | premium |
| Multi-biens | `len(biens) > 1` | multi_biens |
| Condition prêt | `financement.pret == true` | tous |
| Condition vente préalable | `conditions_suspensives.vente_prealable == true` | tous |
| Diagnostics exhaustifs | `diagnostics.exhaustifs == true` | premium |
| Diagnostics tableau | `diagnostics.format_tableau == true` | avec_mobilier |
| Agent immobilier | `agent_immobilier.intervient == true` | premium |
| Faculté substitution | `substitution.autorisee == true` | multi_biens |

---

## Erreurs Fréquentes

| Erreur | Conséquence | Solution |
|--------|-------------|----------|
| Mobilier sans liste | Validation échoue | Remplir `mobilier.liste` |
| Multi-biens < 2 biens | Type incorrect | Vérifier `biens` array |
| Délai réalisation < date prêt | Incohérent | Ajuster les dates |
| Indemnité < 5% | Warning | Confirmer avec notaire |
| Carrez manquant | Non-conforme | Obligatoire si > 8m² |

---

## Intégration Frontend

### Workflow recommandé

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│  API /titres │────▶│  Supabase    │
│  Upload PDF  │     │  /extraire   │     │  stockage    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                                         │
       │    ┌──────────────────────────────────┘
       ▼    ▼
┌──────────────────────────────────────────────────────┐
│   Données pré-remplies (promettants, bien, cadastre) │
│   + Complétion par utilisateur (bénéficiaires, prix) │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│   POST /promesses/generer                            │
│   → Type détecté auto                                │
│   → DOCX généré + stocké                             │
└──────────────────────────────────────────────────────┘
```

---

## Voir aussi

- [directives/generation_promesses_avancee.md](generation_promesses_avancee.md) - Documentation complète v1.4
- [directives/analyse_trames_promesse.md](analyse_trames_promesse.md) - Analyse des 4 trames
- [directives/creer_acte.md](creer_acte.md) - Création acte de vente
- [schemas/promesse_catalogue_unifie.json](../schemas/promesse_catalogue_unifie.json) - Catalogue unifié
- [execution/gestionnaire_promesses.py](../execution/gestionnaire_promesses.py) - Gestionnaire principal

---

## Historique

| Date | Version | Modification |
|------|---------|--------------|
| 2025-01-19 | 1.0 | Création initiale |
| 2026-01-28 | 2.0 | Système multi-templates (4 types), détection auto, Supabase |
