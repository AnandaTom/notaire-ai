# Directive: Génération Avancée de Promesses de Vente

**Version**: 1.0.0 | **Date**: 2026-01-28

---

## Vue d'ensemble

Le système supporte désormais **4 types de promesses de vente**, chacun adapté à un cas d'usage spécifique:

| Type | Template | Cas d'usage | Bookmarks |
|------|----------|-------------|-----------|
| **standard** | `promesse_standard.md` | 1 bien simple, pas de mobilier | 298 |
| **premium** | `promesse_premium.md` | Diagnostics exhaustifs, localisation détaillée | 359 |
| **avec_mobilier** | `promesse_avec_mobilier.md` | Vente meublée, équipements inclus | 312 |
| **multi_biens** | `promesse_multi_biens.md` | Plusieurs propriétés vendues ensemble | 423 |

---

## Détection Automatique du Type

Le système détecte automatiquement le type approprié:

```python
from execution.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()

# Détection automatique
detection = gestionnaire.detecter_type(donnees)
print(f"Type: {detection.type_promesse.value}")
print(f"Confiance: {detection.confiance:.0%}")
print(f"Sections: {len(detection.sections_recommandees)}")
```

### Règles de Détection

1. **Multi-biens** (priorité 1): Si `len(biens) > 1`
2. **Avec mobilier** (priorité 2): Si `mobilier.existe == True`
3. **Premium** (priorité 3): Si diagnostics exhaustifs ou localisation détaillée
4. **Standard** (priorité 4): Par défaut

---

## Génération depuis un Titre de Propriété

### Workflow complet

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   TITRE PROPRIÉTÉ   │────▶│  EXTRACTION AUTO    │────▶│  PROMESSE GÉNÉRÉE   │
│   (PDF/DOCX/URL)    │     │  (données mappées)  │     │   (DOCX prêt)       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

### Via CLI

```bash
# 1. Extraire un titre
python execution/extraire_titre_propriete.py --input titre.pdf --output titre.json

# 2. Générer la promesse
python execution/gestionnaire_promesses.py depuis-titre \
    --titre titre.json \
    --beneficiaires beneficiaires.json \
    --prix 250000 \
    --output outputs/
```

### Via API

```python
# POST /titres/{titre_id}/vers-promesse
{
    "beneficiaires": [
        {
            "nom": "DUPONT",
            "prenoms": "Jean",
            "date_naissance": "1985-03-15",
            "adresse": "10 rue des Lilas, 69001 Lyon"
        }
    ],
    "prix": {
        "montant": 250000,
        "frais_notaire_estimes": 18000
    },
    "financement": {
        "pret": true,
        "montant": 200000,
        "taux_max": 4.5,
        "duree": 240
    },
    "options": {
        "indemnite": {"montant": 25000},
        "delai_realisation": "2026-04-30"
    }
}
```

### Via Frontend

Le frontend peut:
1. Uploader un titre de propriété (PDF/DOCX)
2. Appeler `POST /titres/extraire` pour extraire les données
3. Afficher les données pré-remplies (promettants, bien, cadastre)
4. Permettre à l'utilisateur de compléter (bénéficiaires, prix, etc.)
5. Appeler `POST /titres/{id}/vers-promesse` pour générer

---

## Profils Prédéfinis

Utiliser un profil pour pré-configurer les sections:

```python
# Appliquer un profil
donnees = gestionnaire.appliquer_profil(donnees, "agence_premium")

# Profils disponibles
profils = gestionnaire.get_profils_disponibles()
```

### Profils disponibles

| Profil | Type | Description |
|--------|------|-------------|
| `particulier_simple` | standard | 1 vendeur → 1 acquéreur |
| `particulier_meuble` | avec_mobilier | Avec liste de mobilier |
| `agence_premium` | premium | Documentation complète |
| `investisseur_multi` | multi_biens | Plusieurs biens, substitution |
| `sans_pret` | standard | Achat comptant |

---

## Structure des Données

### Données minimales requises

```json
{
    "promettants": [
        {
            "nom": "MARTIN",
            "prenoms": "Pierre",
            "date_naissance": "1960-05-20",
            "lieu_naissance": "Lyon",
            "adresse": "5 rue du Commerce, 69002 Lyon",
            "situation_matrimoniale": "marie",
            "conjoint": {
                "nom": "MARTIN",
                "prenoms": "Marie",
                "nom_naissance": "DURAND"
            }
        }
    ],
    "beneficiaires": [
        {
            "nom": "DUPONT",
            "prenoms": "Jean",
            "date_naissance": "1985-03-15",
            "adresse": "10 rue des Lilas, 69001 Lyon"
        }
    ],
    "bien": {
        "adresse": "25 avenue Jean Jaurès",
        "code_postal": "69007",
        "ville": "Lyon",
        "copropriete": true,
        "lots": [
            {
                "numero": 12,
                "nature": "Appartement",
                "etage": 3,
                "tantiemes": 150,
                "carrez": 75.50
            }
        ],
        "cadastre": {
            "section": "AB",
            "numero": "123"
        }
    },
    "prix": {
        "montant": 250000
    },
    "delai_realisation": "2026-04-30"
}
```

### Données spécifiques par type

#### Type `avec_mobilier`

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

#### Type `multi_biens`

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
            "cadastre": {"section": "AB", "numero": "123"},
            "lots": [{"numero": 45, "tantiemes": 10}],
            "prix": 15000
        },
        {
            "adresse": "25 avenue Jean Jaurès, Cave 8",
            "nature": "Cave",
            "cadastre": {"section": "AB", "numero": "123"},
            "lots": [{"numero": 8, "tantiemes": 5}],
            "prix": 5000
        }
    ]
}
```

#### Type `premium`

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
        "plomb": {"date": "2026-01-15", "presence": false},
        "electricite": {"date": "2026-01-15", "conforme": true},
        "gaz": {"date": "2026-01-15", "conforme": true},
        "termites": {"date": "2026-01-15", "presence": false},
        "erp": {"date": "2026-01-15"}
    }
}
```

---

## Intégration Supabase

### Tables créées

| Table | Description |
|-------|-------------|
| `titres_propriete` | Titres extraits (source pour génération) |
| `promesses_generees` | Promesses générées |
| `feedbacks_promesse` | Retours notaires |

### Recherche de titres

```python
# Par adresse
resultats = gestionnaire.rechercher_titre_par_adresse("25 avenue Jean Jaurès Lyon")

# Par propriétaire
resultats = gestionnaire.rechercher_titre_par_proprietaire("MARTIN")
```

### Requêtes SQL utiles

```sql
-- Titres d'une étude
SELECT * FROM titres_propriete WHERE etude_id = '...' ORDER BY created_at DESC;

-- Promesses générées depuis titres
SELECT * FROM v_promesses_avec_titre WHERE etude_id = '...';

-- Stats par étude
SELECT * FROM v_stats_promesses_etude WHERE etude_id = '...';

-- Recherche floue par adresse
SELECT * FROM rechercher_titre_adresse('etude_id', 'avenue Jean Jaurès');
```

---

## Validation

Le gestionnaire valide automatiquement:

### Règles obligatoires
- Au moins 1 promettant
- Au moins 1 bénéficiaire
- Adresse du bien
- Prix de vente > 0
- Délai de réalisation

### Règles conditionnelles
- Si prêt: montant, taux max, durée requis
- Si mobilier: liste et prix total requis
- Si multi-biens: adresse et cadastre pour chaque bien

```python
validation = gestionnaire.valider(donnees)

if not validation.valide:
    print("Erreurs:", validation.erreurs)
    print("Champs manquants:", validation.champs_manquants)
else:
    print("Suggestions:", validation.suggestions)
```

---

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/promesses/generer` | POST | Générer une promesse |
| `/promesses/detecter-type` | POST | Détecter le type approprié |
| `/promesses/valider` | POST | Valider les données |
| `/promesses/profils` | GET | Lister les profils |
| `/promesses/types` | GET | Lister les types |
| `/titres` | GET | Lister les titres |
| `/titres/{id}` | GET | Récupérer un titre |
| `/titres/recherche/adresse` | GET | Rechercher par adresse |
| `/titres/recherche/proprietaire` | GET | Rechercher par nom |
| `/titres/{id}/vers-promesse` | POST | Convertir titre → promesse |

---

## Fichiers du système

```
schemas/
├── promesse_catalogue_unifie.json   # Catalogue des 4 trames

templates/promesse/
├── promesse_base.md                 # Template de base
├── promesse_standard.md             # Type standard
├── promesse_premium.md              # Type premium
├── promesse_avec_mobilier.md        # Type avec mobilier
└── promesse_multi_biens.md          # Type multi-biens

execution/
├── gestionnaire_promesses.py        # Gestionnaire intelligent

supabase/migrations/
└── 20260128_promesses_titres.sql    # Tables Supabase

api/
└── main.py                          # Endpoints REST
```

---

## Ajout de nouvelles trames

Quand tu reçois une nouvelle trame de promesse:

1. **Analyser** avec `extraire_bookmarks_contenu.py`
2. **Comparer** avec les trames existantes (bookmarks communs/spécifiques)
3. **Déterminer** si c'est:
   - Une variante d'un type existant → Enrichir le type
   - Un nouveau cas d'usage → Créer un nouveau type
4. **Mettre à jour** `promesse_catalogue_unifie.json`
5. **Créer/modifier** le template approprié
6. **Tester** avec des données réelles

---

*Document créé le 2026-01-28 pour Notomai v1.4.0*
