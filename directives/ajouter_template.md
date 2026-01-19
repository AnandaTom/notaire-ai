# Directive : Ajouter un nouveau type d'acte

## Objectif

Documenter le processus d'ajout d'un nouveau type d'acte notarial au système (ex: donation, succession, bail commercial, etc.).

## Prérequis

1. **Document original** : Une trame DOCX de référence fournie par le notaire
2. **Approbation** : Validation du notaire sur la trame à utiliser
3. **Exemples** : Au moins 2-3 exemples d'actes complétés pour comprendre les variables

---

## Processus en 5 étapes

### Étape 1 : Analyse du document original

#### 1.1 Placer le document dans `docs_originels/`

```
docs_originels/
├── Trame vente lots de copropriété.docx      # Existant
├── Trame promesse vente.docx                  # Existant
└── [Nouveau] Trame donation.docx              # À ajouter
```

**IMPORTANT** : Ne jamais modifier les documents dans `docs_originels/`. Ce sont les références absolues.

#### 1.2 Analyser les variables (zones grisées/bookmarks)

```bash
python execution/extraire_bookmarks_contenu.py \
    --input "docs_originels/[nouveau_template].docx" \
    --output ".tmp/analyse_[type_acte].json"
```

**Résultat** : Liste de tous les bookmarks avec leur contexte.

#### 1.3 Analyser le formatage

Vérifier que les spécifications correspondent à celles de référence :

| Paramètre | Valeur attendue |
|-----------|-----------------|
| Police | Times New Roman 11pt |
| Marges | G=60mm, D=15mm, H/B=25mm |
| Retrait 1ère ligne | 12.51mm |
| Titres H1 | Bold, ALL CAPS, underline, centré |

Si différent, documenter les écarts dans `formatage_docx.md`.

---

### Étape 2 : Créer le schéma de variables

#### 2.1 Créer le fichier de schéma

Créer `schemas/variables_[type_acte].json` basé sur l'analyse :

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Variables pour acte de [type]",
  "type": "object",
  "required": ["acte", "parties", "objet"],
  "properties": {
    "acte": {
      "type": "object",
      "properties": {
        "date": { "$ref": "#/$defs/date_acte" },
        "reference": { "type": "string" }
      }
    },
    "parties": {
      "type": "object",
      "properties": {
        "partie1": { "$ref": "#/$defs/personne" },
        "partie2": { "$ref": "#/$defs/personne" }
      }
    }
    // ... autres propriétés
  }
}
```

#### 2.2 Créer le fichier de questions

Créer ou étendre `schemas/questions_[type_acte].json` :

```json
{
  "sections": {
    "1_acte": {
      "titre": "Informations sur l'acte",
      "questions": [
        {
          "id": "acte_date",
          "question": "Date prévue de l'acte ?",
          "type": "date",
          "obligatoire": true
        }
      ]
    }
  }
}
```

---

### Étape 3 : Créer le template Jinja2

#### 3.1 Créer le fichier template

Créer `templates/[type_acte].md` en utilisant la syntaxe Jinja2 :

```markdown
<div class="header-ref">{{ acte.reference }}</div>

# PARTIE NORMALISÉE

## IDENTIFICATION DES PARTIES

### {{ parties.partie1.qualite | upper }}

{{ parties.partie1.civilite }} {{ parties.partie1.prenoms }} {{ parties.partie1.nom }},
{{ parties.partie1.profession }}, demeurant à {{ parties.partie1.adresse.complete }}

Né{{ 'e' if parties.partie1.civilite == 'Madame' else '' }} à {{ parties.partie1.naissance.lieu }}
le {{ parties.partie1.naissance.date | format_date('lettres') }}

{% if parties.partie1.situation_matrimoniale == 'celibataire' %}
Célibataire.
{% elif parties.partie1.situation_matrimoniale == 'marie' %}
{{ parties.partie1.regime_matrimonial_texte }}
{% endif %}

// ... suite du template
```

#### 3.2 Conventions de formatage Markdown

| Élément | Syntaxe |
|---------|---------|
| Titre H1 | `# TITRE` |
| Titre H2 | `## Sous-titre` |
| Titre H3 | `### Sous-sous-titre` |
| Titre H4 | `#### Petit titre` |
| Gras | `**texte**` |
| Souligné | `__texte__` |
| Tableau | `| Col1 | Col2 |` |
| Div spécial | `<div class="personne">...</div>` |

#### 3.3 Filtres Jinja2 disponibles

| Filtre | Usage | Exemple |
|--------|-------|---------|
| `nombre_en_lettres` | Nombre → lettres | `{{ 14 | nombre_en_lettres }}` → "quatorze" |
| `montant_en_lettres` | Montant → lettres | `{{ 285000 | montant_en_lettres }}` → "deux cent quatre-vingt-cinq mille euros" |
| `format_nombre` | Séparateurs milliers | `{{ 285000 | format_nombre }}` → "285 000" |
| `format_date` | Formater date | `{{ "2025-03-15" | format_date('long') }}` → "15 mars 2025" |
| `date_en_lettres` | Date en lettres | `{{ "2025-03-15" | date_en_lettres }}` → "le quinze mars deux mille vingt-cinq" |

---

### Étape 4 : Mettre à jour les scripts

#### 4.1 Vérifier la compatibilité avec `assembler_acte.py`

Le script devrait fonctionner sans modification si :
- Le template suit les conventions Jinja2
- Les filtres existants sont suffisants

Si nouveaux filtres nécessaires, les ajouter dans `assembler_acte.py` :

```python
def nouveau_filtre(valeur):
    """Docstring du filtre."""
    # Implémentation
    return resultat

# Dans _creer_environnement_jinja():
env.filters['nouveau_filtre'] = nouveau_filtre
```

#### 4.2 Vérifier la compatibilité avec `exporter_docx.py`

Vérifier que :
- Les types de tableaux sont reconnus (ajouter si nécessaire)
- Les titres sont correctement détectés
- Les styles correspondent

#### 4.3 Mettre à jour `valider_acte.py`

Ajouter les règles de validation spécifiques au nouveau type d'acte.

---

### Étape 5 : Créer la directive

Créer `directives/creer_[type_acte].md` basé sur le modèle de `creer_acte.md` :

```markdown
# Directive : Création d'un acte de [type]

## Objectif
Guider la création d'un acte de [type] de A à Z.

## Flux de travail
1. Collecte des informations
2. Validation des données
3. Génération de l'acte
4. Export DOCX/PDF
// ...
```

---

## Checklist de validation

Avant de déclarer le nouveau type d'acte opérationnel :

- [ ] Document original placé dans `docs_originels/`
- [ ] Analyse des bookmarks effectuée
- [ ] Schéma de variables créé (`schemas/variables_[type].json`)
- [ ] Questions créées (`schemas/questions_[type].json`)
- [ ] Template Jinja2 créé (`templates/[type].md`)
- [ ] Tests avec données fictives réussis
- [ ] Export DOCX vérifié (formatage fidèle)
- [ ] Export PDF vérifié
- [ ] Directive créée (`directives/creer_[type].md`)
- [ ] CLAUDE.md mis à jour avec le nouveau type
- [ ] Documentation mise à jour

---

## Exemple : Ajouter un acte de donation

```bash
# 1. Analyser le document
python execution/extraire_bookmarks_contenu.py \
    -i "docs_originels/Trame donation.docx" \
    -o ".tmp/analyse_donation.json"

# 2. Créer le schéma (manuellement basé sur l'analyse)
# -> schemas/variables_donation.json

# 3. Créer le template (manuellement)
# -> templates/donation.md

# 4. Tester
python execution/assembler_acte.py \
    -t donation.md \
    -d .tmp/test_donation.json \
    -o .tmp/actes_generes/

# 5. Exporter et vérifier
python execution/exporter_docx.py \
    -i .tmp/actes_generes/*/acte.md \
    -o .tmp/test_donation.docx
```

---

## Mises à jour de cette directive

| Date | Modification | Auteur |
|------|--------------|--------|
| 2025-01-19 | Création initiale | Agent |

---

## Voir aussi

- [directives/creer_acte.md](creer_acte.md) - Exemple de directive de création
- [directives/formatage_docx.md](formatage_docx.md) - Spécifications formatage
- [execution/extraire_bookmarks_contenu.py](../execution/extraire_bookmarks_contenu.py) - Script d'analyse
- [templates/vente_lots_copropriete.md](../templates/vente_lots_copropriete.md) - Exemple de template
