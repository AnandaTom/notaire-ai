# Directive : Apprentissage Continu et Enrichissement de la Base de Données

## Objectif

Enrichir continuellement la base de données NotaireAI à chaque interaction avec les notaires. Stocker les nouvelles clauses, templates, questions, et situations rencontrées pour construire une base de connaissances exhaustive.

---

## Principe fondamental

> **À chaque acte généré, à chaque clause rencontrée, à chaque nouvelle situation : ENRICHIR LA BASE.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CYCLE D'APPRENTISSAGE CONTINU                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │  INTERACTION │────▶│   ANALYSE    │────▶│ ENRICHISSEMENT│           │
│   │  (Notaire)   │     │  (Nouveautés)│     │  (Base)      │           │
│   └──────────────┘     └──────────────┘     └──────────────┘           │
│          │                                         │                    │
│          │         ┌──────────────────┐           │                    │
│          └────────▶│  ACTE GÉNÉRÉ     │◀──────────┘                    │
│                    │  (Plus intelligent)│                               │
│                    └──────────────────┘                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Ce qui doit être capturé

### 1. Nouvelles clauses

| Situation | Action |
|-----------|--------|
| Clause jamais vue | Ajouter à `schemas/clauses_catalogue.json` |
| Variante d'une clause existante | Créer nouvelle entrée avec référence à l'originale |
| Clause spécifique à un notaire | Marquer comme "personnalisée" avec ID notaire |

**Format d'ajout :**
```json
{
  "id": "categorie_description",
  "nom": "Nom lisible de la clause",
  "type_acte": ["promesse_vente", "vente"],
  "obligatoire": false,
  "condition_application": "expression_jinja2",
  "texte": "Texte complet avec {{ variables }}",
  "variables_requises": ["var1", "var2"],
  "source": "Notaire X - Dossier Y",
  "date_ajout": "2025-01-19"
}
```

### 2. Nouveaux templates

| Situation | Action |
|-----------|--------|
| Nouveau type d'acte | Suivre `directives/ajouter_template.md` |
| Variante de template | Créer nouveau fichier, documenter différences |
| Template spécifique région | Préfixer avec code région (ex: `69_vente_lots.md`) |

### 3. Nouvelles questions

| Situation | Action |
|-----------|--------|
| Information manquante découverte | Ajouter question dans le schéma approprié |
| Question contextuelle | Ajouter avec `condition_affichage` |
| Question fréquemment posée | Promouvoir en question principale |

### 4. Nouvelles règles de validation

| Situation | Action |
|-----------|--------|
| Erreur de cohérence détectée | Ajouter règle dans `valider_acte.py` |
| Règle métier apprise | Documenter dans `validation_donnees.md` |
| Exception à une règle | Ajouter condition d'exception |

### 5. Nouvelles situations matrimoniales/fiscales

| Situation | Action |
|-----------|--------|
| Régime matrimonial rare | Ajouter dans les options + texte type |
| Situation fiscale complexe | Documenter le traitement |
| Cas de représentation | Ajouter les formulations |

---

## Fichiers à enrichir

### Catalogues principaux

| Fichier | Contenu | Enrichir quand |
|---------|---------|----------------|
| `schemas/clauses_catalogue.json` | Clauses réutilisables | Nouvelle clause rencontrée |
| `schemas/questions_notaire.json` | Questions acte vente | Nouvelle info nécessaire |
| `schemas/questions_promesse_vente.json` | Questions promesse | Nouvelle info nécessaire |
| `schemas/sections_catalogue.json` | Sections optionnelles | Nouvelle section identifiée |
| `schemas/annexes_catalogue.json` | Types d'annexes | Nouveau type d'annexe |

### Templates

| Fichier | Enrichir quand |
|---------|----------------|
| `templates/vente_lots_copropriete.md` | Nouvelle formulation standard |
| `templates/promesse_vente_lots_copropriete.md` | Nouvelle formulation |
| `templates/clauses/*.md` | Clauses modulaires réutilisables |

### Scripts

| Fichier | Enrichir quand |
|---------|----------------|
| `execution/valider_acte.py` | Nouvelle règle de validation |
| `execution/assembler_acte.py` | Nouveau filtre Jinja2 |

---

## Processus d'enrichissement

### Étape 1 : Détecter la nouveauté

Lors de chaque interaction, vérifier :

```
□ Clause jamais vue dans clauses_catalogue.json ?
□ Question posée non présente dans les schémas ?
□ Situation matrimoniale/fiscale non documentée ?
□ Type d'annexe non répertorié ?
□ Formulation différente de l'existante ?
□ Règle de validation manquante ?
```

### Étape 2 : Capturer l'information

**Pour une clause :**
```bash
# 1. Lire le catalogue actuel
# 2. Vérifier que la clause n'existe pas
# 3. Identifier la catégorie appropriée
# 4. Extraire les variables Jinja2
# 5. Ajouter au catalogue
```

**Pour une question :**
```bash
# 1. Identifier la section appropriée
# 2. Créer l'entrée avec tous les champs
# 3. Définir les sous-questions si nécessaire
# 4. Lier à la variable du schéma
```

### Étape 3 : Valider l'ajout

- Tester que la clause s'intègre bien au template
- Vérifier que la question produit la bonne variable
- S'assurer que le formatage est cohérent

### Étape 4 : Documenter

Mettre à jour :
- Les directives concernées
- L'index `directives/README.md`
- Les statistiques du catalogue

---

## Exemples concrets

### Exemple 1 : Nouvelle clause de condition suspensive

**Situation :** Le notaire mentionne une condition suspensive d'obtention d'un prêt relais.

**Action :**
```json
// Ajouter à schemas/clauses_catalogue.json > conditions_suspensives
{
  "id": "cs_pret_relais",
  "nom": "Condition suspensive de prêt relais",
  "type_acte": ["promesse_vente", "compromis"],
  "obligatoire": false,
  "texte": "La présente promesse est consentie sous la condition suspensive de l'obtention par le BENEFICIAIRE d'un prêt relais d'un montant de {{ pret_relais.montant | montant_en_lettres }} ({{ pret_relais.montant | format_nombre }} EUR), garanti par une hypothèque sur le bien situé {{ pret_relais.bien_garanti }}.\n\nCe prêt sera remboursé par anticipation lors de la vente du bien servant de garantie, laquelle devra intervenir au plus tard le {{ pret_relais.date_vente_garantie | format_date }}.",
  "variables_requises": ["pret_relais.montant", "pret_relais.bien_garanti", "pret_relais.date_vente_garantie"],
  "source": "Notaire DIAZ - Dossier MARTIN/DURAND - 2025-01-19",
  "date_ajout": "2025-01-19"
}
```

### Exemple 2 : Nouvelle question découverte

**Situation :** On découvre qu'il faut demander si le bien est en zone ANRU pour les frais réduits.

**Action :**
```json
// Ajouter à schemas/questions_notaire.json > section fiscalite
{
  "id": "zone_anru",
  "question": "Le bien est-il situé en zone ANRU (Agence Nationale pour la Rénovation Urbaine) ?",
  "type": "booleen",
  "obligatoire": true,
  "variable": "fiscalite.zone_anru",
  "note": "Si oui, droits de mutation réduits à 0.715%",
  "sous_questions": {
    "si_oui": [
      {
        "id": "zone_anru_reference",
        "question": "Référence du quartier prioritaire ?",
        "variable": "fiscalite.zone_anru.reference"
      }
    ]
  }
}
```

### Exemple 3 : Nouvelle règle de validation

**Situation :** Erreur détectée - un prêt relais ne peut excéder 80% de la valeur du bien en garantie.

**Action :**
```python
# Ajouter à execution/valider_acte.py
def valider_pret_relais(donnees):
    """Vérifie que le prêt relais n'excède pas 80% de la valeur du bien garanti."""
    if donnees.get('pret_relais'):
        montant = donnees['pret_relais'].get('montant', 0)
        valeur_bien = donnees['pret_relais'].get('valeur_bien_garanti', 0)
        if valeur_bien > 0 and montant > valeur_bien * 0.8:
            return Resultat(
                niveau=Niveau.AVERTISSEMENT,
                code="PRET_RELAIS_EXCESSIF",
                message=f"Prêt relais ({montant}€) > 80% valeur bien ({valeur_bien * 0.8}€)",
                champs=["pret_relais.montant"]
            )
    return None
```

---

## Catalogue des annexes

Créer et maintenir un catalogue des types d'annexes :

```json
// schemas/annexes_catalogue.json
{
  "annexes": [
    {
      "id": "plans_cadastral_geoportail",
      "nom": "Plans cadastral et géoportail",
      "obligatoire": true,
      "type_acte": ["promesse_vente", "vente"],
      "description": "Extrait cadastral + vue aérienne Géoportail"
    },
    {
      "id": "diagnostic_carrez",
      "nom": "Diagnostic Carrez",
      "obligatoire": true,
      "condition": "lot.superficie > 8",
      "type_acte": ["promesse_vente", "vente"]
    }
    // ... enrichir au fur et à mesure
  ]
}
```

---

## Statistiques à maintenir

À chaque enrichissement, mettre à jour :

```json
// Dans chaque catalogue
"statistiques": {
  "total_clauses": 45,
  "categories": 12,
  "derniere_mise_a_jour": "2025-01-19",
  "sources": {
    "trames_originales": 30,
    "ajouts_notaires": 15
  }
}
```

---

## Comportement automatique

### À chaque création d'acte

1. **Analyser** les données fournies pour détecter des éléments nouveaux
2. **Comparer** avec les catalogues existants
3. **Enrichir** si nouveau élément détecté
4. **Documenter** la source (notaire, dossier, date)

### À chaque modification d'acte

1. **Identifier** les modifications demandées
2. **Vérifier** si elles révèlent un pattern nouveau
3. **Généraliser** si applicable à d'autres actes
4. **Stocker** comme variante ou nouvelle entrée

### À chaque erreur

1. **Analyser** la cause de l'erreur
2. **Ajouter** une règle de validation si manquante
3. **Améliorer** les questions si information insuffisante
4. **Documenter** dans la directive concernée

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création initiale | Agent |

---

## Voir aussi

- [schemas/clauses_catalogue.json](../schemas/clauses_catalogue.json) - Catalogue des clauses
- [directives/ajouter_template.md](ajouter_template.md) - Ajout de nouveaux templates
- [directives/validation_donnees.md](validation_donnees.md) - Règles de validation
- [execution/valider_acte.py](../execution/valider_acte.py) - Script de validation
