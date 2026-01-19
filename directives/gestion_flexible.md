# Directive : Gestion flexible des templates, annexes et clauses

## Objectif

Permettre une adaptation dynamique des actes notariaux selon les besoins spécifiques de chaque dossier, tout en maintenant la fidélité aux trames originales.

---

## Principes de flexibilité

### 1. Un template, plusieurs variantes

Chaque template peut générer différentes variantes selon les données :

```
vente_lots_copropriete.md
├── Avec agent immobilier (si agent_immobilier = true)
├── Sans agent immobilier (si agent_immobilier = false)
├── Avec prêt(s) (si paiement.mode != 'comptant')
├── Sans prêt (si paiement.mode == 'comptant')
├── Avec mobilier (si mobilier.inclus = true)
├── Sans mobilier (si mobilier.inclus = false)
└── etc.
```

### 2. Sections conditionnelles

Les templates utilisent des conditions Jinja2 :

```jinja2
{% if mobilier.inclus %}
## MOBILIER INCLUS DANS LA VENTE

Le prix comprend les meubles suivants :
| Désignation | Valeur |
|-------------|--------|
{% for meuble in mobilier.liste %}
| {{ meuble.designation }} | {{ meuble.valeur | format_nombre }} € |
{% endfor %}
{% endif %}
```

---

## Gestion des nouveaux templates

### Quand un notaire fournit un nouveau template

1. **Placer dans `docs_originels/`** (ne jamais modifier l'original)

2. **Analyser les variables** :
   ```bash
   python execution/extraire_bookmarks_contenu.py \
       -i "docs_originels/[nouveau].docx" \
       -o ".tmp/analyse_[nouveau].json"
   ```

3. **Comparer avec les templates existants** :
   - Variables communes → Réutiliser le schéma existant
   - Nouvelles variables → Étendre le schéma

4. **Créer ou adapter le template Jinja2** :
   - Si similaire à un existant → Copier et adapter
   - Si très différent → Créer nouveau template

5. **Tester avant utilisation en production**

---

## Gestion des annexes

### Annexes standard (toujours incluses)

| Annexe | Contenu |
|--------|---------|
| Plan cadastral | Extrait Géoportail |
| Plan des lots | Plans de l'appartement/local |
| Diagnostics | DDT complet |

### Annexes conditionnelles

| Annexe | Condition |
|--------|-----------|
| PV AG | Si travaux votés ou en cours |
| Attestation Carrez | Si lots > 8m² |
| Relevé de charges | Toujours pour copropriété |
| Certificat d'urbanisme | Si demandé |
| Servitudes | Si servitudes actives |

### Comment ajouter une annexe dynamiquement

1. **Le notaire demande une annexe spécifique**

2. **Vérifier si elle existe dans le catalogue** (`schemas/sections_catalogue.json`)

3. **Si elle existe** → L'activer dans les données :
   ```json
   {
     "annexes": {
       "plan_cadastral": true,
       "pv_ag": true,
       "certificat_urbanisme": true
     }
   }
   ```

4. **Si elle n'existe pas** → L'ajouter au catalogue puis activer

---

## Gestion des clauses

### Clauses standard (toujours présentes)

- Charges et conditions générales
- Garanties légales
- Déclarations fiscales
- RGPD

### Clauses optionnelles

| Clause | Quand l'inclure |
|--------|-----------------|
| Condition suspensive de prêt | Si financement par prêt |
| Condition suspensive de vente | Si l'acquéreur doit vendre un bien |
| Travaux réalisés par le vendeur | Si travaux récents |
| Servitudes | Si servitudes existantes |
| Droit de préemption | Si zone concernée |
| Plus-value | Si résidence secondaire |

### Comment ajouter une clause personnalisée

1. **Le notaire décrit la clause**

2. **Vérifier `schemas/sections_catalogue.json`** pour une clause similaire

3. **Si clause standard** → Activer dans les données

4. **Si clause personnalisée** :

   a. Créer dans `templates/clauses/` :
   ```markdown
   {# templates/clauses/clause_personnalisee.md #}

   ### Clause spécifique

   {{ clause_personnalisee.texte }}
   ```

   b. Inclure dans le template principal :
   ```jinja2
   {% if clause_personnalisee %}
   {% include 'clauses/clause_personnalisee.md' %}
   {% endif %}
   ```

---

## Workflow de flexibilité

```
DEMANDE DU NOTAIRE
       │
       ├── Nouveau template ?
       │   └── Analyser → Créer schéma → Créer template
       │
       ├── Annexes spécifiques ?
       │   └── Vérifier catalogue → Activer/Créer
       │
       └── Clauses spécifiques ?
           └── Vérifier catalogue → Activer/Créer
       │
       ▼
GÉNÉRATION PERSONNALISÉE
```

---

## Exemples concrets

### Exemple 1 : Vente avec agent immobilier

**Notaire :** "Cette vente inclut un agent immobilier, Orpi Lyon, honoraires 8 000 € à charge vendeur"

**Action :**
```json
{
  "agent_immobilier": {
    "intervient": true,
    "agence": {
      "nom": "ORPI LYON",
      "adresse": "...",
      "carte_pro": "..."
    },
    "honoraires": 8000,
    "charge_de": "vendeur"
  }
}
```

Le template génère automatiquement la section agent.

---

### Exemple 2 : Clause suspensive personnalisée

**Notaire :** "L'acquéreur conditionne l'achat à l'obtention d'un permis de construire pour extension"

**Action :**
1. Vérifier si clause existe → Non, c'est personnalisé
2. Créer la clause :
   ```json
   {
     "conditions_suspensives": [
       {
         "type": "permis_construire",
         "description": "Obtention d'un permis de construire pour extension",
         "delai_jours": 90,
         "beneficiaire": "acquereur"
       }
     ]
   }
   ```
3. Le template génère :
   > La présente vente est conclue sous la condition suspensive de l'obtention par l'ACQUÉREUR d'un permis de construire pour extension, dans un délai de 90 jours.

---

### Exemple 3 : Nouveau type d'acte (bail commercial)

**Notaire :** "J'ai besoin de générer des baux commerciaux, voici ma trame"

**Action :**
1. Recevoir `docs_originels/Trame bail commercial.docx`
2. Analyser les variables
3. Créer `schemas/variables_bail_commercial.json`
4. Créer `schemas/questions_bail_commercial.json`
5. Créer `templates/bail_commercial.md`
6. Créer `directives/creer_bail_commercial.md`
7. Mettre à jour CLAUDE.md

---

## Catalogue des sections (extrait)

Le fichier `schemas/sections_catalogue.json` contient :

```json
{
  "sections": {
    "agent_immobilier": {
      "id": "agent",
      "titre": "Intervention d'un agent immobilier",
      "obligatoire": false,
      "questions_declencheur": ["agent_immobilier"]
    },
    "mobilier": {
      "id": "mobilier",
      "titre": "Mobilier inclus dans la vente",
      "obligatoire": false,
      "questions_declencheur": ["mobilier_inclus"]
    },
    "condition_suspensive_pret": {
      "id": "cond_pret",
      "titre": "Condition suspensive d'obtention de prêt",
      "obligatoire": false,
      "auto_active_si": "paiement.mode == 'pret'"
    },
    "travaux_recents": {
      "id": "travaux",
      "titre": "Travaux réalisés par le vendeur",
      "obligatoire": false,
      "questions_declencheur": ["travaux_recents"]
    }
  }
}
```

---

## Points de vigilance

1. **Toujours partir de la trame originale** - Ne pas improviser le formatage
2. **Tester les nouvelles clauses** - Vérifier le rendu DOCX
3. **Documenter les ajouts** - Mettre à jour le catalogue
4. **Valider avec le notaire** - Avant utilisation en production

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création initiale | Agent |

---

## Voir aussi

- [directives/ajouter_template.md](ajouter_template.md) - Ajouter un nouveau type d'acte
- [directives/creer_acte.md](creer_acte.md) - Création d'acte standard
- [schemas/sections_catalogue.json](../schemas/sections_catalogue.json) - Catalogue des sections
- [templates/](../templates/) - Templates Jinja2 existants
