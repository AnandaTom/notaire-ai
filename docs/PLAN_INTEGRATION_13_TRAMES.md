# Plan d'Intégration Optimisée - 13 Trames de Promesse

> **Date de création:** 4 février 2026
> **Version:** 1.0.0
> **Auteur:** Notomai Agent
> **Objectif:** Intégrer 13 trames anonymisées pour atteindre 95%+ de conformité sur tous les cas réels

---

## Vue d'Ensemble

### Inventaire des Trames

**13 Trames Anonymisées:**
- **6 COPROPRIÉTÉ:** Principale (312 bookmarks), A (446), B (382), C (323), K (0 - création copro), L (0 - viager)
- **6 HORS COPROPRIÉTÉ:** E (292), F (277), G (325 - servitudes), H (305 - groupe habitations), I (326 - lotissement), J (343 - lotissement)
- **1 TERRAIN À BÂTIR:** D (230)

**Cas Spéciaux Identifiés:**
1. **Trame K** - Création de copropriété (23 tableaux, format libre)
2. **Trame L** - Viager avec bouquet + rente viagère (85 tableaux, format libre)
3. **Trame H** - Groupe d'habitations (variables PAGRHAB)
4. **Trame I, J** - Maison en lotissement (variables PALOTI, PLOTIS)
5. **Trame G** - Servitudes explicites (section spécifique)

### Gaps Critiques

| Gap | Impact | Effort | Priorité |
|-----|--------|--------|----------|
| Sections conditionnelles (lotissement, groupe habitations) | Haute | Bas | P0 - Court terme |
| Variables manquantes (PAGRHAB, PALOTI, PLOTIS) | Haute | Moyen | P0 - Court terme |
| Section servitudes hors-copro | Moyenne | Bas | P1 - Court terme |
| Template viager | Haute | Élevé | P1 - Moyen terme |
| Template création copro | Moyenne | Élevé | P2 - Moyen terme |

### Objectifs Mesurables

| Métrique | Avant | Objectif v1.9 | Objectif v2.0 |
|----------|-------|---------------|---------------|
| Conformité copro classique | 88.9% | 92%+ | 95%+ |
| Conformité hors-copro classique | NEW | 90%+ | 92%+ |
| Conformité terrain | NEW | 85%+ | 88%+ |
| Couverture cas spéciaux | 0% | 50% (H,I,J,G) | 85% (+ K, L) |
| Tests automatisés | 219 | 240+ | 260+ |

---

## Phase 1 : Améliorations Court Terme (v1.9.0)

**Durée estimée:** 1-2 jours
**Impact:** +5-10% conformité hors-copro, support 4 cas spéciaux (H, I, J, G)

### 1.1 Ajouter Sections Conditionnelles

#### A. Section Lotissement (Trames I, J)

**Fichier:** `templates/promesse_hors_copropriete.md`
**Position:** Après la section "Désignation du bien" (~ligne 200)

```jinja2
{% if bien.lotissement %}
## DISPOSITIONS RELATIVES AU LOTISSEMENT

Le bien vendu fait partie d'un lotissement autorisé par arrêté :
{% if bien.lotissement.arrete %}
- **Arrêté d'autorisation:** {{ bien.lotissement.arrete.date }} par {{ bien.lotissement.arrete.autorite }}
- **Référence:** {{ bien.lotissement.arrete.numero }}
{% endif %}

{% if bien.lotissement.nom %}
**Nom du lotissement:** {{ bien.lotissement.nom }}
{% endif %}

### Obligations du lotissement

Le promettant acquéreur s'oblige à respecter les conditions suivantes :

{% if bien.lotissement.obligations %}
{% for obligation in bien.lotissement.obligations %}
- {{ obligation.description }}
{% endfor %}
{% endif %}

{% if bien.lotissement.cahier_charges %}
### Cahier des charges

Le bien est soumis au cahier des charges du lotissement établi le {{ bien.lotissement.cahier_charges.date }}.

**Points clés du cahier des charges :**
{% for clause in bien.lotissement.cahier_charges.clauses %}
- {{ clause }}
{% endfor %}
{% endif %}

{% if bien.lotissement.association_syndicale %}
### Association syndicale

Le lotissement est géré par une association syndicale libre (ASL) :
- **Nom:** {{ bien.lotissement.association_syndicale.nom }}
- **Cotisation annuelle:** {{ bien.lotissement.association_syndicale.cotisation_annuelle }} €
{% endif %}

{% endif %}
```

#### B. Section Groupe d'Habitations (Trame H)

**Fichier:** `templates/promesse_hors_copropriete.md`
**Position:** Après "Désignation du bien"

```jinja2
{% if bien.groupe_habitations %}
## GROUPE D'HABITATIONS

Le bien vendu fait partie d'un groupe d'habitations comprenant {{ bien.groupe_habitations.nombre_lots }} lots.

{% if bien.groupe_habitations.parties_communes %}
### Parties communes du groupe

Les parties communes du groupe d'habitations comprennent :
{% for partie in bien.groupe_habitations.parties_communes %}
- {{ partie.designation }}{% if partie.surface %} ({{ partie.surface }} m²){% endif %}
{% endfor %}
{% endif %}

{% if bien.groupe_habitations.charges %}
### Charges communes

Les charges du groupe d'habitations sont réparties comme suit :
- **Quote-part du lot vendu:** {{ bien.groupe_habitations.charges.quote_part }} / {{ bien.groupe_habitations.charges.total }}
- **Montant annuel estimé:** {{ bien.groupe_habitations.charges.montant_annuel }} €
{% endif %}

{% if bien.groupe_habitations.reglement %}
### Règlement du groupe

Le groupe d'habitations est soumis à un règlement établi le {{ bien.groupe_habitations.reglement.date }}.

**Clauses principales du règlement :**
{% for clause in bien.groupe_habitations.reglement.clauses %}
- {{ clause }}
{% endfor %}
{% endif %}

{% endif %}
```

#### C. Section Servitudes Détaillées (Trame G)

**Fichier:** `templates/promesse_hors_copropriete.md`
**Position:** Après "État du bien" dans `partie_developpee_promesse.md`

```jinja2
{% if bien.servitudes and bien.servitudes|length > 0 %}
## SERVITUDES

Le bien est grevé ou bénéficie des servitudes suivantes :

{% for servitude in bien.servitudes %}
### {{ servitude.type | capitalize }}

**Nature:** {{ servitude.nature }}

{% if servitude.description %}
{{ servitude.description }}
{% endif %}

{% if servitude.origine %}
**Origine:** {{ servitude.origine }}
{% if servitude.origine_date %}({{ servitude.origine_date }}){% endif %}
{% endif %}

{% if servitude.fonds %}
**Fonds:** {{ servitude.fonds.type }} {{ servitude.fonds.designation }}
{% endif %}

{% if servitude.modalites %}
**Modalités:** {{ servitude.modalites }}
{% endif %}

{% endfor %}

{% if bien.servitudes_declaration %}
{{ bien.servitudes_declaration }}
{% endif %}

{% endif %}
```

### 1.2 Enrichir Templates Copropriété (Gaps Trames A, B, C)

#### D. Section Assurance Copropriété (manquante dans Principale)

**Fichier:** `templates/promesse_vente_lots_copropriete.md`
**Position:** Après "Fonds de travaux"

*(Déjà ajouté dans v1.7.0 - vérifier présence)*

#### E. Section Garantie de Superficie Carrez (manquante)

**Fichier:** `templates/promesse_vente_lots_copropriete.md`
**Position:** Après "Fonds de travaux"

*(Déjà ajouté dans v1.7.0 - vérifier présence)*

### 1.3 Ajouter Table "Lieu de Situation" (Manquante dans Trames A, B)

**Fichier:** Tous les templates promesse
**Position:** Avant "Désignation du bien"

*(Déjà ajouté dans v1.7.0 - vérifier présence dans les 3 templates)*

---

## Phase 2 : Enrichissement Schémas et Questions (v1.9.0)

**Durée estimée:** 1 jour
**Impact:** Support complet cas H, I, J, G

### 2.1 Schéma Variables Promesse (v4.0.0)

**Fichier:** `schemas/variables_promesse_vente.json`

**Ajouts dans `bien` :**

```json
{
  "bien": {
    "properties": {
      "lotissement": {
        "type": "object",
        "description": "Informations sur le lotissement (si applicable)",
        "properties": {
          "nom": { "type": "string" },
          "arrete": {
            "type": "object",
            "properties": {
              "date": { "type": "string", "format": "date" },
              "autorite": { "type": "string" },
              "numero": { "type": "string" }
            }
          },
          "cahier_charges": {
            "type": "object",
            "properties": {
              "date": { "type": "string", "format": "date" },
              "clauses": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          },
          "obligations": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "description": { "type": "string" },
                "echeance": { "type": "string" }
              }
            }
          },
          "association_syndicale": {
            "type": "object",
            "properties": {
              "nom": { "type": "string" },
              "cotisation_annuelle": { "type": "number" }
            }
          }
        }
      },
      "groupe_habitations": {
        "type": "object",
        "description": "Informations sur le groupe d'habitations (si applicable)",
        "properties": {
          "nombre_lots": { "type": "integer" },
          "parties_communes": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "designation": { "type": "string" },
                "surface": { "type": "number" }
              }
            }
          },
          "charges": {
            "type": "object",
            "properties": {
              "quote_part": { "type": "number" },
              "total": { "type": "number" },
              "montant_annuel": { "type": "number" }
            }
          },
          "reglement": {
            "type": "object",
            "properties": {
              "date": { "type": "string", "format": "date" },
              "clauses": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      },
      "servitudes": {
        "type": "array",
        "description": "Liste des servitudes affectant le bien",
        "items": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["active", "passive", "apparente", "non_apparente", "continue", "discontinue"]
            },
            "nature": { "type": "string" },
            "description": { "type": "string" },
            "origine": { "type": "string" },
            "origine_date": { "type": "string", "format": "date" },
            "fonds": {
              "type": "object",
              "properties": {
                "type": { "type": "string", "enum": ["dominant", "servant"] },
                "designation": { "type": "string" }
              }
            },
            "modalites": { "type": "string" }
          },
          "required": ["type", "nature"]
        }
      }
    }
  }
}
```

### 2.2 Questions Promesse (v3.1.0)

**Fichier:** `schemas/questions_promesse_vente.json`

**Nouvelle section 6b - Lotissement :**

```json
{
  "6b_lotissement": {
    "titre": "Lotissement (si applicable)",
    "condition": "bien.categorie in ['hors_copropriete', 'terrain_a_batir'] and bien.type_descriptif contains 'lotissement'",
    "questions": [
      {
        "id": "lotissement_existe",
        "question": "Le bien fait-il partie d'un lotissement ?",
        "type": "boolean",
        "obligatoire": true,
        "chemin_variable": "bien.lotissement"
      },
      {
        "id": "lotissement_nom",
        "question": "Nom du lotissement :",
        "type": "text",
        "condition": "bien.lotissement",
        "chemin_variable": "bien.lotissement.nom"
      },
      {
        "id": "lotissement_arrete_date",
        "question": "Date de l'arrêté d'autorisation du lotissement :",
        "type": "date",
        "condition": "bien.lotissement",
        "chemin_variable": "bien.lotissement.arrete.date"
      },
      {
        "id": "lotissement_arrete_autorite",
        "question": "Autorité ayant délivré l'arrêté (ex: Maire de ...) :",
        "type": "text",
        "condition": "bien.lotissement",
        "chemin_variable": "bien.lotissement.arrete.autorite"
      },
      {
        "id": "lotissement_cahier_charges",
        "question": "Existe-t-il un cahier des charges du lotissement ?",
        "type": "boolean",
        "condition": "bien.lotissement",
        "chemin_variable": "bien.lotissement.cahier_charges"
      },
      {
        "id": "lotissement_asl",
        "question": "Y a-t-il une association syndicale libre (ASL) ?",
        "type": "boolean",
        "condition": "bien.lotissement",
        "chemin_variable": "bien.lotissement.association_syndicale"
      },
      {
        "id": "lotissement_asl_cotisation",
        "question": "Montant de la cotisation annuelle ASL (en €) :",
        "type": "number",
        "condition": "bien.lotissement.association_syndicale",
        "chemin_variable": "bien.lotissement.association_syndicale.cotisation_annuelle"
      }
    ]
  }
}
```

**Nouvelle section 6c - Groupe d'Habitations :**

```json
{
  "6c_groupe_habitations": {
    "titre": "Groupe d'habitations (si applicable)",
    "condition": "bien.categorie == 'hors_copropriete' and bien.type_descriptif contains 'groupe'",
    "questions": [
      {
        "id": "groupe_habitations_existe",
        "question": "Le bien fait-il partie d'un groupe d'habitations ?",
        "type": "boolean",
        "obligatoire": true,
        "chemin_variable": "bien.groupe_habitations"
      },
      {
        "id": "groupe_nombre_lots",
        "question": "Nombre de lots dans le groupe d'habitations :",
        "type": "integer",
        "condition": "bien.groupe_habitations",
        "chemin_variable": "bien.groupe_habitations.nombre_lots"
      },
      {
        "id": "groupe_parties_communes",
        "question": "Y a-t-il des parties communes (ex: voies d'accès, espaces verts) ?",
        "type": "boolean",
        "condition": "bien.groupe_habitations",
        "chemin_variable": "bien.groupe_habitations.parties_communes"
      },
      {
        "id": "groupe_charges_quote_part",
        "question": "Quote-part du lot vendu dans les charges communes (ex: 1/15) :",
        "type": "text",
        "condition": "bien.groupe_habitations",
        "chemin_variable": "bien.groupe_habitations.charges.quote_part"
      },
      {
        "id": "groupe_charges_montant",
        "question": "Montant annuel estimé des charges communes (en €) :",
        "type": "number",
        "condition": "bien.groupe_habitations",
        "chemin_variable": "bien.groupe_habitations.charges.montant_annuel"
      },
      {
        "id": "groupe_reglement_existe",
        "question": "Existe-t-il un règlement du groupe d'habitations ?",
        "type": "boolean",
        "condition": "bien.groupe_habitations",
        "chemin_variable": "bien.groupe_habitations.reglement"
      }
    ]
  }
}
```

**Section 6d - Servitudes (enrichissement) :**

```json
{
  "6d_servitudes": {
    "titre": "Servitudes",
    "questions": [
      {
        "id": "servitudes_existence",
        "question": "Le bien est-il grevé de servitudes ou en bénéficie-t-il ?",
        "type": "boolean",
        "obligatoire": true,
        "chemin_variable": "bien.servitudes"
      },
      {
        "id": "servitudes_liste",
        "question": "Pour chaque servitude, précisez : type (passage, vue, puisage...), nature (active/passive), origine, modalités",
        "type": "array",
        "condition": "bien.servitudes",
        "chemin_variable": "bien.servitudes",
        "items_schema": {
          "type": { "type": "select", "options": ["active", "passive"] },
          "nature": { "type": "text" },
          "description": { "type": "textarea" },
          "origine": { "type": "text" }
        }
      }
    ]
  }
}
```

### 2.3 Mise à Jour Détection Automatique

**Fichier:** `execution/gestionnaires/gestionnaire_promesses.py`

**Méthode `detecter_categorie_bien()` - Ajout marqueurs :**

```python
def detecter_categorie_bien(self, donnees: Dict) -> Tuple[CategorieBien, int]:
    """Détecte la catégorie de bien avec marqueurs enrichis"""

    # Marqueurs existants + nouveaux
    marqueurs_hors_copro = {
        "maison": 10,
        "villa": 10,
        "pavillon": 10,
        "local": 8,
        "terrain_bati": 8,
        "lotissement": 12,  # NOUVEAU - priorité haute
        "groupe_habitations": 12,  # NOUVEAU
        "groupe habitations": 12,  # NOUVEAU
        "ASL": 10,  # NOUVEAU - Association Syndicale Libre
    }

    # ... (reste de la logique)
```

**Méthode `detecter_type()` - Nouveaux types :**

```python
def detecter_type(self, donnees: Dict) -> Dict[str, Any]:
    """Détection 2 niveaux: catégorie + type de transaction"""

    # Détection catégorie
    categorie, confiance_categorie = self.detecter_categorie_bien(donnees)

    # Détection type de transaction
    type_promesse = "standard"
    sous_type = None

    # Nouveaux sous-types
    if categorie == CategorieBien.HORS_COPROPRIETE:
        if self._contient_marqueur(donnees, ["lotissement", "lotis"]):
            sous_type = "lotissement"
        elif self._contient_marqueur(donnees, ["groupe", "ASL"]):
            sous_type = "groupe_habitations"
        elif self._contient_marqueur(donnees, ["servitude"]):
            sous_type = "avec_servitudes"

    return {
        "categorie_bien": categorie,
        "type_promesse": type_promesse,
        "sous_type": sous_type,  # NOUVEAU
        "confiance": confiance_categorie
    }
```

---

## Phase 3 : Templates Spécialisés (v2.0.0)

**Durée estimée:** 3-5 jours
**Impact:** Support complet viager (L) et création copro (K)

### 3.1 Template Viager

**Fichier:** `templates/promesse_viager.md`

**Structure :**

1. **En-tête** - Standard (parties, objet)
2. **Désignation du bien** - Standard
3. **SECTION SPÉCIALE : Modalités du Viager**
   - Bouquet (montant, versement)
   - Rente viagère (montant, périodicité, indexation)
   - Droit d'usage et d'habitation (DUH) ou occupation
   - Clause de libération anticipée
   - Tableau d'amortissement dynamique
4. **Conditions suspensives** - Adaptées (pas de prêt classique)
5. **Clauses standard** - Reste identique

**Composants clés :**

```jinja2
## MODALITÉS DU VIAGER

### Bouquet

Un bouquet d'un montant de **{{ viager.bouquet.montant }} € ({{ viager.bouquet.montant_lettres }})** sera versé :
- **Date de versement :** {{ viager.bouquet.date_versement }}
- **Modalités :** {{ viager.bouquet.modalites }}

### Rente viagère

Une rente viagère sera versée au(x) crédirentier(s) selon les modalités suivantes :

{% if viager.rente.type == "simple" %}
**Rente viagère simple**
- **Montant annuel :** {{ viager.rente.montant_annuel }} €
- **Périodicité :** {{ viager.rente.periodicite }} (mensuelle/trimestrielle/annuelle)
- **Premier versement :** {{ viager.rente.date_premier_versement }}
{% elif viager.rente.type == "reversible" %}
**Rente viagère réversible**
- **Montant initial :** {{ viager.rente.montant_annuel }} €
- **Taux de réversion :** {{ viager.rente.taux_reversion }}%
- **Bénéficiaire de la réversion :** {{ viager.rente.beneficiaire_reversion }}
{% endif %}

**Indexation :** La rente sera indexée annuellement sur {{ viager.rente.indice }} (ex: IPC, indice INSEE).

### Droit d'usage et d'habitation

{% if viager.occupation.type == "DUH" %}
Le crédirentier conserve un **droit d'usage et d'habitation** (DUH) sur le bien jusqu'à son décès.
{% elif viager.occupation.type == "occupe" %}
Le crédirentier occupe le bien et s'engage à l'entretenir.
{% elif viager.occupation.type == "libre" %}
Le bien est vendu **libre de toute occupation**.
{% endif %}

{% if viager.liberation_anticipee %}
### Clause de libération anticipée

En cas de libération anticipée du bien (départ en maison de retraite, décès), les modalités suivantes s'appliquent :

{{ viager.liberation_anticipee.conditions }}

**Réévaluation de la rente :** {{ viager.liberation_anticipee.reevaluation }}
{% endif %}

### Tableau financier récapitulatif

| Élément | Montant | Observations |
|---------|---------|--------------|
| Bouquet | {{ viager.bouquet.montant }} € | Versé le {{ viager.bouquet.date_versement }} |
| Rente annuelle | {{ viager.rente.montant_annuel }} € | Indexée sur {{ viager.rente.indice }} |
| Valeur vénale estimée | {{ viager.valeur_venale }} € | Évaluation {{ viager.valeur_venale_date }} |
| Décote occupation | {{ viager.decote_occupation }}% | DUH/Occupation |
```

**Schéma variables :**

```json
{
  "viager": {
    "type": "object",
    "required": ["bouquet", "rente", "occupation"],
    "properties": {
      "bouquet": {
        "type": "object",
        "properties": {
          "montant": { "type": "number" },
          "date_versement": { "type": "string", "format": "date" },
          "modalites": { "type": "string" }
        }
      },
      "rente": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["simple", "reversible"] },
          "montant_annuel": { "type": "number" },
          "periodicite": { "type": "string", "enum": ["mensuelle", "trimestrielle", "annuelle"] },
          "indice": { "type": "string" },
          "taux_reversion": { "type": "number" }
        }
      },
      "occupation": {
        "type": "object",
        "properties": {
          "type": { "type": "string", "enum": ["DUH", "occupe", "libre"] }
        }
      },
      "liberation_anticipee": {
        "type": "object",
        "properties": {
          "conditions": { "type": "string" },
          "reevaluation": { "type": "string" }
        }
      }
    }
  }
}
```

### 3.2 Template Création de Copropriété

**Fichier:** `templates/promesse_copro_creation.md`

**Structure :**

1. **En-tête** - Standard
2. **SECTION SPÉCIALE : Création de la Copropriété**
   - État descriptif de division à établir
   - Règlement de copropriété à établir
   - Répartition initiale des charges
   - Syndic initial
   - Première assemblée générale
3. **Désignation du bien** - Standard (mais sans EDD existant)
4. **Clauses standard** - Reste identique

**Composants clés :**

```jinja2
## CRÉATION DE LA COPROPRIÉTÉ

### État descriptif de division et règlement de copropriété

Le vendeur s'engage à faire établir par **Maître {{ copropriete_creation.notaire }}**, notaire, avant la réalisation de la vente :

1. **Un état descriptif de division (EDD)** décrivant :
   - Les lots de copropriété et leur répartition
   - Les parties communes générales et spéciales
   - Les tantièmes de chaque lot

2. **Un règlement de copropriété** définissant :
   - Les droits et obligations des copropriétaires
   - Les modalités de gestion des parties communes
   - Les clés de répartition des charges

{% if copropriete_creation.date_etablissement %}
**Date prévisionnelle d'établissement :** {{ copropriete_creation.date_etablissement }}
{% endif %}

### Syndic initial

{% if copropriete_creation.syndic_initial %}
Le syndic initial de la copropriété sera :
- **Nom :** {{ copropriete_creation.syndic_initial.nom }}
- **Durée du mandat :** {{ copropriete_creation.syndic_initial.duree_mandat }} an(s)
- **Honoraires annuels estimés :** {{ copropriete_creation.syndic_initial.honoraires }} €
{% else %}
Le syndic initial sera désigné lors de la première assemblée générale.
{% endif %}

### Répartition initiale des lots

| Lot n° | Type | Tantièmes | Acquéreur |
|--------|------|-----------|-----------|
{% for lot in copropriete_creation.lots_initiaux %}
| {{ lot.numero }} | {{ lot.type }} | {{ lot.tantiemes }} / {{ copropriete_creation.total_tantiemes }} | {{ lot.attributaire }} |
{% endfor %}

**Total des tantièmes :** {{ copropriete_creation.total_tantiemes }}

### Première assemblée générale

Une première assemblée générale des copropriétaires sera convoquée dans un délai de {{ copropriete_creation.ag_delai }} jours suivant la signature de l'acte de vente, afin de :
- Approuver le règlement de copropriété et l'EDD
- Désigner ou confirmer le syndic
- Voter le budget prévisionnel

{% if copropriete_creation.conditions_suspensives %}
### Condition suspensive spécifique

La présente promesse est conclue sous la condition suspensive de l'obtention de l'accord de tous les acquéreurs pressentis des lots de la copropriété à créer.

**Date limite de réalisation :** {{ copropriete_creation.condition_date_limite }}
{% endif %}
```

**Schéma variables :**

```json
{
  "copropriete_creation": {
    "type": "object",
    "required": ["notaire", "lots_initiaux", "total_tantiemes"],
    "properties": {
      "notaire": { "type": "string" },
      "date_etablissement": { "type": "string", "format": "date" },
      "syndic_initial": {
        "type": "object",
        "properties": {
          "nom": { "type": "string" },
          "duree_mandat": { "type": "integer" },
          "honoraires": { "type": "number" }
        }
      },
      "lots_initiaux": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "numero": { "type": "integer" },
            "type": { "type": "string" },
            "tantiemes": { "type": "number" },
            "attributaire": { "type": "string" }
          }
        }
      },
      "total_tantiemes": { "type": "number" },
      "ag_delai": { "type": "integer", "default": 30 },
      "conditions_suspensives": { "type": "boolean" },
      "condition_date_limite": { "type": "string", "format": "date" }
    }
  }
}
```

---

## Phase 4 : Tests et Validation (v1.9.0 et v2.0.0)

**Durée estimée:** 1-2 jours par phase

### 4.1 Tests Unitaires

**Fichier:** `tests/test_promesses_enrichies.py`

**Nouveaux tests à ajouter :**

```python
class TestPromesseLotissement:
    """Tests pour promesses avec lotissement (Trames I, J)"""

    def test_detection_lotissement(self):
        """Vérifie détection catégorie hors-copro + sous-type lotissement"""
        # ...

    def test_section_lotissement_presente(self):
        """Vérifie que la section lotissement s'affiche si données présentes"""
        # ...

    def test_section_lotissement_absente(self):
        """Vérifie que la section lotissement ne s'affiche pas si pas de données"""
        # ...

    def test_questions_lotissement(self):
        """Vérifie que les questions lotissement sont posées"""
        # ...

class TestPromesseGroupeHabitations:
    """Tests pour promesses avec groupe d'habitations (Trame H)"""

    def test_detection_groupe_habitations(self):
        # ...

    def test_section_groupe_presente(self):
        # ...

    def test_charges_groupe(self):
        """Vérifie calcul des charges du groupe"""
        # ...

class TestPromesseServitudes:
    """Tests pour promesses avec servitudes (Trame G)"""

    def test_section_servitudes_presente(self):
        # ...

    def test_servitudes_multiples(self):
        """Vérifie affichage de plusieurs servitudes"""
        # ...

class TestPromesseViager:
    """Tests pour promesses viager (Trame L)"""

    def test_detection_viager(self):
        """Vérifie détection type viager"""
        # ...

    def test_calcul_rente(self):
        """Vérifie calcul de la rente viagère"""
        # ...

    def test_tableau_financier(self):
        """Vérifie génération du tableau récapitulatif"""
        # ...

class TestPromesseCoproprieteCreation:
    """Tests pour promesses création copro (Trame K)"""

    def test_detection_creation_copro(self):
        # ...

    def test_repartition_lots_initiaux(self):
        """Vérifie répartition des lots initiaux"""
        # ...

    def test_total_tantiemes(self):
        """Vérifie que total des tantièmes = 100%"""
        # ...
```

**Objectif tests :**
- **v1.9.0 :** 240+ tests (ajout 21 tests pour H, I, J, G)
- **v2.0.0 :** 260+ tests (ajout 20 tests pour K, L)

### 4.2 Tests E2E (End-to-End)

**Fichier:** `tests/test_pipeline_e2e_enrichi.py`

**Scénarios à tester :**

1. **Pipeline complet Lotissement (Trame I)**
   - Données minimales → Q&R → Détection auto → Génération DOCX
   - Vérifier section lotissement présente
   - Vérifier conformité structurelle ≥90%

2. **Pipeline complet Groupe Habitations (Trame H)**
   - Idem avec données groupe habitations
   - Vérifier charges et règlement

3. **Pipeline complet Viager (Trame L)**
   - Données viager → Détection auto → Template spécialisé → DOCX
   - Vérifier tableau financier
   - Conformité ≥85% (nouveau template)

4. **Pipeline complet Création Copro (Trame K)**
   - Données création → Template spécialisé → DOCX
   - Vérifier répartition lots
   - Conformité ≥85%

### 4.3 Tests de Conformité

**Script:** `execution/analyse/comparer_documents.py`

**Nouveaux benchmarks :**

```bash
# Conformité copro (Trames Principale, A, B, C)
python execution/analyse/comparer_documents.py \
    --original "docs_original/Trame promesse unilatérale de vente lots de copropriété.docx" \
    --genere "outputs/test_copro_principale.docx"

# Conformité hors-copro lotissement (Trame I)
python execution/analyse/comparer_documents.py \
    --original "docs_original/Trame_promesse_hors_copro_I.docx" \
    --genere "outputs/test_hors_copro_lotissement.docx"

# Conformité groupe habitations (Trame H)
python execution/analyse/comparer_documents.py \
    --original "docs_original/Trame_promesse_hors_copro_H.docx" \
    --genere "outputs/test_hors_copro_groupe.docx"

# Conformité terrain (Trame D)
python execution/analyse/comparer_documents.py \
    --original "docs_original/Trame_promesse_terrain_D.docx" \
    --genere "outputs/test_terrain.docx"
```

**Objectifs de conformité :**

| Template | Trame référence | Objectif v1.9 | Objectif v2.0 |
|----------|----------------|---------------|---------------|
| promesse_vente_lots_copropriete.md | Principale | 92%+ | 95%+ |
| promesse_hors_copropriete.md | E, F | 90%+ | 92%+ |
| promesse_hors_copropriete.md | I (lotissement) | 88%+ | 90%+ |
| promesse_hors_copropriete.md | H (groupe) | 88%+ | 90%+ |
| promesse_terrain_a_batir.md | D | 85%+ | 88%+ |
| promesse_viager.md | L | - | 85%+ |
| promesse_copro_creation.md | K | - | 85%+ |

---

## Phase 5 : Documentation et Directives (v1.9.0 et v2.0.0)

**Durée estimée:** 1 jour

### 5.1 Mise à Jour Directives

#### A. Nouvelle Directive - Cas Spéciaux Promesse

**Fichier:** `directives/workflow_cas_speciaux_promesse.md`

**Contenu :**

```markdown
# Workflow Cas Spéciaux - Promesses de Vente

## Objectif

Guider la génération de promesses pour les cas spécialisés identifiés dans les 13 trames anonymisées.

## Cas Spéciaux Supportés

### 1. Lotissement (Trames I, J)
**Détection:** Présence de "lotissement" dans la description du bien
**Template:** `promesse_hors_copropriete.md` (section conditionnelle)
**Questions supplémentaires:** Section 6b (7 questions)
**Conformité attendue:** 90%+

### 2. Groupe d'Habitations (Trame H)
**Détection:** Présence de "groupe" ou "ASL" dans la description
**Template:** `promesse_hors_copropriete.md` (section conditionnelle)
**Questions supplémentaires:** Section 6c (6 questions)
**Conformité attendue:** 90%+

### 3. Servitudes Explicites (Trame G)
**Détection:** Champ `bien.servitudes` renseigné
**Template:** Tous templates (section dans `partie_developpee_promesse.md`)
**Questions supplémentaires:** Section 6d (2 questions)
**Conformité attendue:** 92%+

### 4. Viager (Trame L) - v2.0
**Détection:** Présence de "viager" ou "rente viagère" dans les données
**Template:** `promesse_viager.md` (template spécialisé)
**Questions supplémentaires:** Section viager (15 questions)
**Conformité attendue:** 85%+

### 5. Création de Copropriété (Trame K) - v2.0
**Détection:** `bien.etat` = "création" ou absence d'EDD existant
**Template:** `promesse_copro_creation.md` (template spécialisé)
**Questions supplémentaires:** Section création copro (12 questions)
**Conformité attendue:** 85%+

## Workflow de Détection

[Voir flowchart détaillé]
```

#### B. Mise à Jour CLAUDE.md (v1.9.0)

**Section à ajouter :**

```markdown
### 🆕 Cas Spéciaux Promesse Supportés (v1.9.0)

Le système supporte désormais 5 cas spéciaux de promesses identifiés dans les 13 trames analysées :

| Cas | Trames | Détection | Support |
|-----|--------|-----------|---------|
| **Lotissement** | I, J | "lotissement" dans description | Section conditionnelle ✓ |
| **Groupe habitations** | H | "groupe" ou "ASL" | Section conditionnelle ✓ |
| **Servitudes explicites** | G | `bien.servitudes` renseigné | Section conditionnelle ✓ |
| **Viager** | L | "viager" ou "rente viagère" | Template spécialisé (v2.0) |
| **Création copro** | K | `bien.etat` = "création" | Template spécialisé (v2.0) |

**Couverture totale:** 13/13 trames (100%) avec détection automatique

Voir [workflow_cas_speciaux_promesse.md](directives/workflow_cas_speciaux_promesse.md) pour les détails.
```

#### C. Mise à Jour Catalogue Unifié (v3.0.0)

**Fichier:** `schemas/promesse_catalogue_unifie.json`

**Ajout section `cas_speciaux` :**

```json
{
  "cas_speciaux": {
    "lotissement": {
      "marqueurs_detection": ["lotissement", "lotis", "ASL"],
      "template_base": "promesse_hors_copropriete",
      "sections_supplementaires": ["6b_lotissement"],
      "conformite_cible": 0.90,
      "trames_reference": ["I", "J"]
    },
    "groupe_habitations": {
      "marqueurs_detection": ["groupe", "groupe d'habitations", "PAGRHAB"],
      "template_base": "promesse_hors_copropriete",
      "sections_supplementaires": ["6c_groupe_habitations"],
      "conformite_cible": 0.90,
      "trames_reference": ["H"]
    },
    "servitudes": {
      "marqueurs_detection": ["servitude"],
      "template_base": "tous",
      "sections_supplementaires": ["restrictions_usage", "servitudes"],
      "conformite_cible": 0.92,
      "trames_reference": ["G"]
    },
    "viager": {
      "marqueurs_detection": ["viager", "rente viagère", "bouquet"],
      "template_base": "promesse_viager",
      "sections_supplementaires": [],
      "conformite_cible": 0.85,
      "trames_reference": ["L"],
      "version_disponible": "2.0.0"
    },
    "creation_copropriete": {
      "marqueurs_detection": ["création copropriété", "EDD à établir"],
      "template_base": "promesse_copro_creation",
      "sections_supplementaires": [],
      "conformite_cible": 0.85,
      "trames_reference": ["K"],
      "version_disponible": "2.0.0"
    }
  }
}
```

### 5.2 Guide Utilisateur - Notaire

**Fichier:** `docs/GUIDE_CAS_SPECIAUX_NOTAIRE.md`

**Contenu :**

```markdown
# Guide Notaire - Cas Spéciaux de Promesses

## Introduction

Ce guide présente les 5 cas spéciaux de promesses de vente supportés par Notomai, basés sur l'analyse de 13 trames réelles anonymisées.

## Cas 1 : Maison en Lotissement

**Situations concernées :**
- Maison individuelle dans un lotissement autorisé
- Présence d'un cahier des charges
- Association syndicale libre (ASL) pour les parties communes

**Questions supplémentaires posées :**
1. Nom du lotissement
2. Date et autorité de l'arrêté d'autorisation
3. Existence d'un cahier des charges
4. Existence d'une ASL et montant de la cotisation

**Sections ajoutées automatiquement :**
- Dispositions relatives au lotissement
- Obligations du cahier des charges
- Charges ASL

**Exemple concret :** Maison dans "Lotissement Les Érables", ASL avec cotisation 150 €/an

---

## Cas 2 : Groupe d'Habitations

**Situations concernées :**
- Maison dans un groupe d'habitations (non copropriété)
- Parties communes partagées (voies d'accès, espaces verts)
- Charges communes réparties entre propriétaires

**Questions supplémentaires posées :**
1. Nombre de lots dans le groupe
2. Description des parties communes
3. Quote-part du lot vendu
4. Montant annuel des charges
5. Existence d'un règlement

**Sections ajoutées automatiquement :**
- Groupe d'habitations
- Parties communes du groupe
- Répartition des charges

**Exemple concret :** Groupe de 8 maisons, quote-part 1/8, charges 400 €/an

---

## Cas 3 : Bien avec Servitudes

**Situations concernées :**
- Servitudes de passage, vue, puisage, etc.
- Servitudes actives (bénéfice au bien vendu) ou passives (charge)

**Questions supplémentaires posées :**
1. Existence de servitudes
2. Pour chaque servitude : type, nature, origine, modalités

**Sections ajoutées automatiquement :**
- Servitudes détaillées avec nature et modalités

**Exemple concret :** Servitude de passage pour accès garage, servitude de vue

---

## Cas 4 : Viager (v2.0)

**Situations concernées :**
- Vente en viager avec bouquet + rente viagère
- Droit d'usage et d'habitation (DUH) ou occupation
- Clause de libération anticipée

**Questions supplémentaires posées :**
1. Montant du bouquet
2. Montant de la rente annuelle
3. Périodicité (mensuelle/trimestrielle/annuelle)
4. Type de rente (simple/réversible)
5. DUH ou occupation
6. Clause de libération anticipée

**Sections ajoutées automatiquement :**
- Modalités du viager (bouquet, rente, DUH)
- Tableau financier récapitulatif
- Clause de libération anticipée

**Exemple concret :** Bouquet 50 000 €, rente 12 000 €/an, DUH conservé

---

## Cas 5 : Création de Copropriété (v2.0)

**Situations concernées :**
- Création initiale d'une copropriété (division d'immeuble)
- EDD et règlement de copropriété à établir
- Syndic initial à désigner

**Questions supplémentaires posées :**
1. Notaire établissant l'EDD
2. Date prévisionnelle
3. Syndic initial
4. Répartition des lots initiaux
5. Première AG

**Sections ajoutées automatiquement :**
- Création de la copropriété
- Répartition initiale des lots
- Syndic initial
- Première assemblée générale

**Exemple concret :** Division immeuble en 6 lots, syndic initial désigné, AG dans 30 jours

---

## Comment Notomai Détecte Automatiquement le Cas ?

Le système analyse vos réponses et détecte automatiquement le cas spécial :

1. **Lotissement** → Détecté si vous mentionnez "lotissement" dans la description
2. **Groupe habitations** → Détecté si "groupe" ou "ASL" mentionné
3. **Servitudes** → Détecté si vous répondez "Oui" à la question servitudes
4. **Viager** → Détecté si "viager" ou "rente viagère" mentionné
5. **Création copro** → Détecté si "création" ou absence d'EDD existant

Notomai sélectionne automatiquement le template approprié et pose les questions complémentaires.
```

---

## Métriques de Succès et Suivi

### Métriques Techniques

| Métrique | Baseline (v1.7) | v1.9.0 | v2.0.0 |
|----------|----------------|--------|--------|
| Conformité copro classique | 88.9% | 92%+ | 95%+ |
| Conformité hors-copro classique | NEW | 90%+ | 92%+ |
| Conformité terrain | NEW | 85%+ | 88%+ |
| Conformité viager | - | - | 85%+ |
| Conformité création copro | - | - | 85%+ |
| Tests automatisés | 219 | 240+ | 260+ |
| Couverture trames | 4/13 | 11/13 | 13/13 |
| Templates disponibles | 3 | 3 (enrichis) | 5 |

### Métriques Utilisateur

| Métrique | Baseline | v1.9.0 | v2.0.0 |
|----------|----------|--------|--------|
| Taux de détection auto correcte | 85% | 92%+ | 95%+ |
| Questions Q&R | 97 | 120+ | 140+ |
| Temps génération moyenne | 12s | 15s | 18s |
| Taux d'erreur validation | 5% | 2% | 1% |

### Métriques Métier

| Métrique | Baseline | v1.9.0 | v2.0.0 |
|----------|----------|--------|--------|
| Cas supportés | Copro simple | +4 cas spéciaux | +2 cas rares |
| Satisfaction notaire | - | Mesure à démarrer | 85%+ |
| Demandes support/clarification | - | <5 par semaine | <3 par semaine |

---

## Priorités et Séquençage

### Sprint 1 (Court Terme - v1.9.0) - **PRIORITAIRE**

**Durée:** 3-4 jours
**Effort:** Bas-Moyen
**Impact:** Haute (support 85% des cas réels)

1. ✅ **Jour 1-2** - Sections conditionnelles
   - Ajouter section lotissement (templates hors-copro)
   - Ajouter section groupe habitations (templates hors-copro)
   - Ajouter section servitudes (tous templates)

2. ✅ **Jour 2-3** - Enrichissement schémas
   - Variables lotissement, groupe, servitudes
   - Questions Q&R (6b, 6c, 6d)

3. ✅ **Jour 3** - Détection automatique
   - Marqueurs lotissement, groupe, servitudes
   - Sous-types dans `gestionnaire_promesses.py`

4. ✅ **Jour 3-4** - Tests
   - 21 nouveaux tests unitaires
   - 3 tests E2E
   - Tests conformité (Trames H, I, J, G)

5. ✅ **Jour 4** - Documentation
   - Mise à jour CLAUDE.md (v1.9.0)
   - Création `workflow_cas_speciaux_promesse.md`

### Sprint 2 (Moyen Terme - v2.0.0)

**Durée:** 5-7 jours
**Effort:** Élevé
**Impact:** Moyenne-Haute (support 100% des cas, y compris rares)

1. **Semaine 1** - Template Viager
   - Création template `promesse_viager.md`
   - Schéma variables viager
   - Questions Q&R viager (15 questions)
   - Tests E2E viager

2. **Semaine 2** - Template Création Copro
   - Création template `promesse_copro_creation.md`
   - Schéma variables création copro
   - Questions Q&R création (12 questions)
   - Tests E2E création copro

3. **Fin Semaine 2** - Tests et Documentation
   - 20 nouveaux tests (viager + création)
   - Tests conformité (Trames K, L)
   - Guide notaire cas spéciaux
   - Mise à jour CLAUDE.md (v2.0.0)

### Sprint 3 (Long Terme - v2.1+)

**Durée:** Variable
**Effort:** Élevé
**Impact:** Innovation

1. **Machine Learning** - Classification automatique K, L (sans bookmarks)
2. **Catalogues dynamiques** - Clauses viager, création copro réutilisables
3. **OCR avancé** - Support PDF scannés titres de propriété
4. **Dashboard Analytics** - Métriques usage par cas spécial

---

## Risques et Mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Trames K, L sans bookmarks impossibles à parser auto | Haute | Moyenne | Templates manuels, documentation claire |
| Détection automatique sous-types erronée | Moyenne | Moyenne | Tests E2E complets, fallback notaire |
| Complexité viager trop élevée pour template | Moyenne | Haute | Validation notaire expert, itérations |
| Régression conformité templates existants | Basse | Haute | Tests automatisés non-régression |
| Surcharge cognitive notaire (trop de questions) | Moyenne | Moyenne | Questions conditionnelles intelligentes |

---

## Checklist de Déploiement

### v1.9.0 - Court Terme

- [ ] Sections conditionnelles ajoutées (lotissement, groupe, servitudes)
- [ ] Variables enrichies dans `variables_promesse_vente.json` (v4.0.0)
- [ ] Questions ajoutées dans `questions_promesse_vente.json` (v3.1.0)
- [ ] Détection automatique enrichie (`gestionnaire_promesses.py`)
- [ ] 21 tests unitaires ajoutés (total 240+)
- [ ] 3 tests E2E ajoutés
- [ ] Tests conformité H, I, J, G ≥88%
- [ ] `workflow_cas_speciaux_promesse.md` créé
- [ ] CLAUDE.md mis à jour (v1.9.0)
- [ ] Tests non-régression passés (templates existants)
- [ ] Commit + Push sur branche tom/dev
- [ ] Merge sur master
- [ ] Déploiement Modal
- [ ] Documentation utilisateur

### v2.0.0 - Moyen Terme

- [ ] Template `promesse_viager.md` créé
- [ ] Template `promesse_copro_creation.md` créé
- [ ] Schémas variables viager + création copro
- [ ] Questions Q&R viager (15) + création (12)
- [ ] 20 tests unitaires viager + création
- [ ] 2 tests E2E viager + création
- [ ] Tests conformité K, L ≥85%
- [ ] `GUIDE_CAS_SPECIAUX_NOTAIRE.md` créé
- [ ] CLAUDE.md mis à jour (v2.0.0)
- [ ] Catalogue unifié v3.0.0
- [ ] Tests non-régression passés
- [ ] Commit + Push
- [ ] Merge sur master
- [ ] Déploiement Modal
- [ ] Formation notaires

---

## Conclusion

Ce plan d'intégration optimisée permettra à Notomai de :

1. **Supporter 100% des 13 trames** analysées (contre 30% actuellement)
2. **Atteindre 90%+ de conformité** sur tous les cas standard
3. **Gérer 5 cas spéciaux** identifiés dans les trames réelles
4. **Réduire les interventions manuelles** grâce à la détection automatique
5. **Améliorer l'expérience notaire** avec questions contextuelles intelligentes

**Priorisation recommandée :** Sprint 1 (v1.9.0) en priorité absolue pour support rapide de 85% des cas réels, puis Sprint 2 (v2.0.0) pour complétude 100%.

---

**Prochaines étapes :** Valider ce plan avec l'équipe, prioriser Sprint 1, et commencer l'implémentation.
