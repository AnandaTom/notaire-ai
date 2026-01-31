# Directive: Génération Avancée de Promesses de Vente

**Version**: 1.0.0 | **Date**: 2026-01-28

---

## Vue d'ensemble

Le système supporte désormais **3 catégories de promesses de vente**, chacune adaptée à un cas d'usage spécifique:

| Type | Template | Cas d'usage | Bookmarks |
|------|----------|-------------|-----------|
| **copropriete** | `promesse_vente_lots_copropriete.md` | Appartement, lots de copro | 298 |
| **hors_copropriete** | `promesse_hors_copropriete.md` | Maison, villa, local commercial | - |
| **terrain_a_batir** | `promesse_terrain_a_batir.md` | Terrain, lotissement | - |

---

## Détection Automatique du Type

Le système détecte automatiquement le type approprié:

```python
from execution.gestionnaires.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()

# Détection automatique
detection = gestionnaire.detecter_type(donnees)
print(f"Type: {detection.type_promesse.value}")
print(f"Confiance: {detection.confiance:.0%}")
print(f"Sections: {len(detection.sections_recommandees)}")
```

### Règles de Détection

1. **Copropriété** (priorité 1): Si `bien.copropriete == True`
2. **Terrain à bâtir** (priorité 2): Si `bien.nature == "Terrain"` et `bien.nb_lots_cadastraux == 1`
3. **Hors copropriété** (priorité 3): Par défaut (maison, villa, local commercial)

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
python execution/extraction/extraire_titre_propriete.py --input titre.pdf --output titre.json

# 2. Générer la promesse
python execution/gestionnaires/gestionnaire_promesses.py depuis-titre \
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
| `particulier_copropriete` | copropriete | Appartement, 1 bien |
| `particulier_maison` | hors_copropriete | Maison, achat simple |
| `investisseur_terrain` | terrain_a_batir | Terrain à bâtir, développement |
| `agence_standard` | copropriete | Vente classique avec agence |
| `sans_pret` | copropriete | Achat comptant |

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

#### Type `hors_copropriete`

```json
{
    "bien": {
        "nature": "Maison d'habitation",
        "surface_habitable": 120.5,
        "surface_terrain": 850,
        "localisation_detaillee": true,
        "lieu_dit": "Les Brotteaux",
        "voie_acces": "Par la rue de la République"
    },
    "diagnostics": {
        "dpe": {"date": "2026-01-15", "classe": "C"},
        "amiante": {"date": "2026-01-15", "presence": false},
        "plomb": {"date": "2026-01-15", "presence": false},
        "electricite": {"date": "2026-01-15", "conforme": true},
        "gaz": {"date": "2026-01-15", "conforme": true}
    }
}
```

#### Type `terrain_a_batir`

```json
{
    "bien": {
        "nature": "Terrain à bâtir",
        "surface": 500,
        "zone_urbaine": true,
        "plu_conforme": true,
        "acces_direct_route": true,
        "viabilisation_etat": "Partiellement viabilisé"
    },
    "lotissement": {
        "existe": false
    },
    "urbanisme": {
        "permis_construire_possible": true,
        "zone_classement": "Zone AU - Aménagement à moyen terme"
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
├── promesse_catalogue_unifie.json   # Catalogue des 3 catégories

templates/
├── promesse_vente_lots_copropriete.md  # Catégorie copropriété
├── promesse_hors_copropriete.md        # Catégorie hors copropriété
├── promesse_terrain_a_batir.md         # Catégorie terrain à bâtir
└── sections/                            # Sections réutilisables
    ├── section_sequestre.md
    ├── section_declarations_parties.md
    ├── section_propriete_jouissance.md
    ├── section_lotissement_dispositions.md
    └── section_evenement_sanitaire.md

execution/gestionnaires/
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
