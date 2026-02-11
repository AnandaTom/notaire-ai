# Directive : Création d'une Promesse Unilatérale de Vente

**Version**: 3.2.0 | **Date**: 2026-02-10

---

## Objectif

Guider la création complète d'une **promesse unilatérale de vente** pour les 3 catégories de biens immobiliers, avec détection automatique à **3 niveaux** (v1.9.0).

---

## Architecture 3 niveaux (v1.9.0)

Le système utilise une détection à **3 niveaux** pour adapter le template et les sections:

### Niveau 1 : Catégorie de bien (détermine le template de base)

| Catégorie | Template | Cas d'usage |
|-----------|----------|-------------|
| **Copropriété** | `promesse_vente_lots_copropriete.md` | Appartement, lot de copro |
| **Hors copropriété** | `promesse_hors_copropriete.md` | Maison individuelle, local commercial |
| **Terrain à bâtir** | `promesse_terrain_a_batir.md` | Terrain, lotissement |

### Niveau 2 : Type de transaction (sections conditionnelles)

| Type | Sections supplémentaires |
|------|--------------------------|
| **Standard** | Sections de base |
| **Premium** | Diagnostics exhaustifs, localisation détaillée |
| **Avec mobilier** | Liste mobilier, ventilation prix |
| **Multi-biens** | Multi-désignation, multi-cadastre |

### Niveau 3 : Sous-types spécifiques (v2.0.0) ✨

Sections activées selon le contexte du bien:

| Catégorie | Sous-type | Marqueur | Section activée |
|-----------|-----------|----------|-----------------|
| **Toutes** | `viager` | Multi-marqueurs (>=2 parmi 6) | **Template dédié** `promesse_viager.md` + 4 sections |
| **Hors copro** | `lotissement` | `bien.lotissement` | DISPOSITIONS RELATIVES AU LOTISSEMENT |
| **Hors copro** | `groupe_habitations` | `bien.groupe_habitations` | GROUPE D'HABITATIONS |
| **Hors copro / Toutes** | `avec_servitudes` | `bien.servitudes[]` | SERVITUDES (actives/passives) |
| **Copro** | `creation` | Pas de `syndic`/`reglement` | Sections création copropriété |

**Exemple lotissement**:
```json
{
  "bien": {
    "lotissement": {
      "nom": "Les Jardins de Marcy",
      "arrete": {"date": "12/06/2018", "autorite": "Préfecture du Rhône"},
      "association_syndicale": {"nom": "ASL Les Jardins", "cotisation_annuelle": 350}
    }
  }
}
```

→ Active automatiquement la section "DISPOSITIONS RELATIVES AU LOTISSEMENT" dans le template

### Détection Automatique (3 niveaux)

```python
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()
detection = gestionnaire.detecter_type(donnees)

# Résultat v1.9.0 (3 niveaux):
# categorie_bien: CategorieBien.HORS_COPROPRIETE
# type_promesse: TypePromesse.STANDARD
# sous_type: "lotissement"  # ✨ NOUVEAU
# confiance: 0.90
# raison: "Détecté bien.lotissement + usage_actuel=Habitation"
```

Le champ `sous_type` est utilisé pour activer les sections conditionnelles spécifiques dans le template.

### Règles de Détection Catégorie (Niveau 1)

| Priorité | Condition | Catégorie |
|----------|-----------|-----------|
| 1 | `usage_actuel == "terrain"` ou `type_bien == "terrain"` | TERRAIN_A_BATIR |
| 2 | `bien.copropriete` ou `syndic` ou `lots` | COPROPRIETE |
| 3 | `usage_actuel == "Habitation"` ou `copropriete == False` | HORS_COPROPRIETE |
| 4 | `bien.lotissement` ou `bien.groupe_habitations` | HORS_COPROPRIETE |
| 5 | Par défaut | COPROPRIETE |

**Note v1.9.0**: `bien.lotissement` seul NE détermine PLUS la catégorie TERRAIN. Une maison dans un lotissement = HORS_COPROPRIETE avec sous-type "lotissement".

### Règles de Détection Type (Niveau 2)

| Priorité | Condition | Type |
|----------|-----------|------|
| 1 | `len(biens) > 1` | multi_biens |
| 2 | `mobilier.existe == True` | avec_mobilier |
| 3 | `diagnostics.exhaustifs == True` | premium |
| 4 | Par défaut | standard |

### Règles de Détection Sous-Type (Niveau 3) ✨

**Pour HORS_COPROPRIETE**:

| Priorité | Condition | Sous-type | Confiance |
|----------|-----------|-----------|-----------|
| 1 | `bien.lotissement` existe | `lotissement` | 95% |
| 2 | `bien.groupe_habitations` existe | `groupe_habitations` | 95% |
| 3 | `bien.servitudes[]` non vide | `avec_servitudes` | 90% |
| 4 | Aucun marqueur | `None` | - |

**Pour TOUTES CATÉGORIES (priorité absolue)**:

| Priorité | Condition | Sous-type | Confiance |
|----------|-----------|-----------|-----------|
| 0 | Multi-marqueurs viager >= 2 (type_vente=2pts, rente=1pt, bouquet=1pt, DUH=1pt, modalités=1pt) | `viager` | 95% |

**Pour COPROPRIETE**:

| Priorité | Condition | Sous-type | Confiance |
|----------|-----------|-----------|-----------|
| 1 | Pas de `syndic` ni `reglement` | `creation` | 85% |
| 2 | Aucun marqueur | `None` | - |

**Cas de priorité combinée**: Si lotissement + servitudes → `lotissement` (priorité haute). Si viager + lotissement → `viager` (priorité absolue).

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
| **Gestionnaire principal** | `execution/gestionnaires/gestionnaire_promesses.py` |
| **Catalogue unifié** | `schemas/promesse_catalogue_unifie.json` |
| Template copropriété | `templates/promesse_vente_lots_copropriete.md` |
| Template hors copropriété | `templates/promesse_hors_copropriete.md` |
| Template terrain à bâtir | `templates/promesse_terrain_a_batir.md` |
| Sections réutilisables | `templates/sections/section_*.md` |
| Schéma variables | `schemas/variables_promesse_vente.json` |
| Questions notaire | `schemas/questions_promesse_vente.json` |
| Script assemblage | `execution/core/assembler_acte.py` |
| Script export DOCX | `execution/core/exporter_docx.py` |

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
│  2. DÉTECTION (2 niveaux)                                              │
│     ├─► Niveau 1: categorie_bien (copro | hors_copro | terrain)        │
│     ├─► Niveau 2: type_promesse (standard | premium | mobilier | multi)│
│     └─► Sélection automatique du template par catégorie                │
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
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()

# Détection catégorie + type
detection = gestionnaire.detecter_type(donnees)
print(f"Catégorie: {detection.categorie_bien.value}")  # copropriete / hors_copropriete / terrain_a_batir
print(f"Type: {detection.type_promesse.value}")  # standard / premium / avec_mobilier / multi_biens

# Option A: Depuis des données (sélection template automatique par catégorie)
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

print(f"Catégorie: {resultat.categorie_bien.value}")
print(f"DOCX: {resultat.fichier_docx}")
```

---

## Structure des Données par Catégorie

### Copropriété (standard)

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

### Hors copropriété (maison)

```json
{
    "promettants": [{"nom": "MARTIN", "prenoms": "Pierre"}],
    "beneficiaires": [{"nom": "DUPONT", "prenoms": "Jean"}],
    "bien": {
        "adresse": "15 chemin des Vignes",
        "code_postal": "69380",
        "ville": "Lissieu",
        "copropriete": false,
        "type_bien": "maison",
        "surface_habitable": 120.50,
        "surface_terrain": 850,
        "dependances": [
            {"type": "garage", "surface": 25},
            {"type": "abri_jardin", "surface": 12}
        ],
        "construction": {"date": "1985", "materiaux": "Parpaings"},
        "assainissement": {"type": "collectif"}
    },
    "prix": {"montant": 380000},
    "delai_realisation": "2026-06-30"
}
```

### Terrain à bâtir (lotissement)

```json
{
    "promettants": [{"nom": "SCI LES ORMES"}],
    "beneficiaires": [{"nom": "LAMBERT", "prenoms": "Sophie"}],
    "bien": {
        "adresse": "Rue du Lotissement",
        "code_postal": "69380",
        "ville": "Lissieu",
        "type_bien": "terrain",
        "lotissement": {
            "nom": "LE PRE DES LYS",
            "numero_permis": "PA 069 380 26 V0001",
            "lotisseur": "SCI LES ORMES",
            "cahier_charges": {"auteur": "Me NOTAIRE"}
        },
        "nature_terrain": "Terrain à bâtir",
        "surface_terrain": 450
    },
    "viabilisation": {
        "viabilise": true,
        "raccordements": [
            {"reseau": "Eau potable", "statut": "Raccordé"},
            {"reseau": "Électricité", "statut": "En limite"},
            {"reseau": "Assainissement", "statut": "Raccordé"}
        ]
    },
    "constructibilite": {
        "zone_plu": "1AU",
        "cu_reference": "CU 069 380 26 A0012"
    },
    "prix": {"montant": 150000},
    "delai_realisation": "2026-09-30"
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
| 2026-01-30 | 3.0 | Architecture 2 niveaux (3 catégories + 4 types), templates hors-copro et terrain |
| 2026-02-04 | 3.1 | Sections conditionnelles (lotissement, groupe, servitudes), sous-types copro (création, viager) |
| 2026-02-10 | 3.2 | Template viager dédié, détection multi-marqueurs cross-catégorie, schéma v4.1.0, 19 questions viager |
