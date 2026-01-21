# Bonnes Pratiques - Templates Jinja2

> **Objectif** : Créer des templates robustes, maintenables et sans erreurs

---

## 🎯 Règle d'Or

**TOUTE variable utilisée DOIT être protégée par une condition `{% if %}`**

```jinja2
# ❌ MAUVAIS - Crash si variable absente
{{ fiscalite.plus_value.exoneration }}

# ✅ BON - Robuste
{% if fiscalite and fiscalite.plus_value and fiscalite.plus_value.exoneration %}
{{ fiscalite.plus_value.exoneration }}
{% endif %}
```

---

## ✅ Checklist Avant Commit

Avant toute modification de template:

- [ ] Toutes les variables ont une condition `{% if %}`
- [ ] Les boucles `{% for %}` sont fermées par `{% endfor %}`
- [ ] Les conditions `{% if %}` sont fermées par `{% endif %}`
- [ ] Les noms de variables correspondent EXACTEMENT aux données JSON
- [ ] Test assemblage avec données minimales ET maximales
- [ ] Zones grisées `<<<VAR_START>>>` présentes sur toutes variables

**Script validation** :
```bash
# Windows
.\execution\valider_rapide.ps1 vente

# Linux/Mac
./execution/valider_rapide.sh vente
```

---

## 📐 Patterns Recommandés

### 1. Accès Attribut Imbriqué (3+ niveaux)

```jinja2
# ❌ MAUVAIS
{{ fiscalite.droits_mutation.taux_departemental }}

# ✅ BON
{% if fiscalite and fiscalite.droits_mutation and fiscalite.droits_mutation.taux_departemental %}
{{ fiscalite.droits_mutation.taux_departemental }}
{% endif %}
```

### 2. Boucle avec Accès Attributs

```jinja2
# ✅ BON
{% if paiement and paiement.prets and paiement.prets|length > 0 %}
{% for pret in paiement.prets %}
  {% if pret.mensualite %}
  Mensualité: {{ pret.mensualite | format_nombre }} EUR
  {% endif %}
{% endfor %}
{% endif %}
```

### 3. Inclusion de Section

```jinja2
# ✅ BON - Condition AVANT include
{% if garanties %}
{% include 'sections/section_garanties.md' %}
{% endif %}

# ❌ MAUVAIS - Include sans condition
{% include 'sections/section_garanties.md' %}
```

### 4. Filtre sur Variable Potentiellement Undefined

```jinja2
# ❌ MAUVAIS - Crash si undefined
{{ prix.montant | format_nombre }}

# ✅ BON
{% if prix and prix.montant %}
<<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>>
{% endif %}
```

---

## 🐛 Erreurs Fréquentes et Solutions

### Erreur 1: `'dict object' has no attribute 'X'`

**Cause** : Variable utilisée sans vérification d'existence

**Solution** :
```jinja2
# Avant
{{ fiscalite.centre_impots_vendeur.nom }}

# Après
{% if fiscalite and fiscalite.centre_impots_vendeur %}
{{ fiscalite.centre_impots_vendeur.nom }}
{% endif %}
```

### Erreur 2: `TypeError: unsupported format string passed to Undefined.__format__`

**Cause** : Filtre appliqué sur variable undefined

**Solution** :
```jinja2
# Avant
{{ pret.mensualite | format_nombre }}

# Après
{% if pret.mensualite %}
{{ pret.mensualite | format_nombre }}
{% endif %}
```

### Erreur 3: `jinja2.exceptions.TemplateNotFound`

**Cause** : Fichier include dans mauvais dossier

**Search paths** : `templates/`, `templates/sections/`, `clauses/`

**Solution** :
```bash
# Déplacer fichier dans bon dossier
mv .tmp/section_X.md templates/sections/

# Ou utiliser chemin relatif correct
{% include 'sections/section_X.md' %}
```

### Erreur 4: Boucle non fermée

**Cause** : `{% for %}` sans `{% endfor %}` → contexte corrompu

**Détection** :
```python
# Script validation
python -c "
with open('template.md') as f:
    lines = f.readlines()
depth = 0
for i, line in enumerate(lines, 1):
    if '{% for' in line: depth += 1
    elif '{% endfor %}' in line: depth -= 1
    if depth < 0: print(f'Ligne {i}: endfor en trop')
print(f'Depth finale: {depth} (devrait être 0)')
"
```

---

## 🔄 Workflow Intégration Nouvelle Section

### Étape 1: Créer Fichier Section

**Fichier** : `templates/sections/section_nom_section.md`

**Template** :
```jinja2
## Titre Section

{% if variable_racine %}

### Sous-section

{% if variable_racine.champ %}
**Champ** : <<<VAR_START>>>{{ variable_racine.champ }}<<<VAR_END>>>
{% endif %}

{% endif %}
```

### Étape 2: Intégrer à la FIN de `partie_developpee.md`

**TOUJOURS à la fin**, jamais inline :

```jinja2
# Avant dernière section "Formalisme lié aux annexes"

{% if variable_racine %}
{% include 'sections/section_nom_section.md' %}
{% endif %}

# Formalisme lié aux annexes
...
```

### Étape 3: Test Progressif

```bash
# 1. Assemblage
python execution/assembler_acte.py \
  --template vente_lots_copropriete.md \
  --donnees .tmp/donnees_test_vague5_enrichi.json \
  --output .tmp/test_section/ \
  --zones-grisees

# 2. Si ❌ → Commenter section et analyser erreur
# 3. Si ✅ → Ajouter section suivante
```

**Règle** : 1 section → test → 1 section → test

**Jamais** : 4 sections → test (= 60 min debug)

### Étape 4: Enrichir Données

Si variables manquantes:

```python
# Script .tmp/enrichir_donnees_vaguX.py
data['variable_racine'] = {
    'champ': 'valeur'
}
```

---

## 📏 Alignement Noms Variables

### Problème Fréquent

Template attend `assiette`, script crée `base` → TypeError

### Solution

**1. Lire template AVANT créer script**

```bash
grep -n "fiscalite.droits_mutation" templates/vente_lots_copropriete.md
```

**2. Utiliser EXACTEMENT le même nom**

```python
# ✅ BON
data['fiscalite']['droits_mutation']['assiette'] = 245000

# ❌ MAUVAIS
data['fiscalite']['droits_mutation']['base'] = 245000
```

**3. Replace-all si besoin d'alignement global**

```python
# Modifier template (si alignement avec original)
# Ou modifier données (si template vient de document original)
```

---

## 🎨 Zones Grisées - Règles

### Obligatoire Sur

- ✅ Toutes variables dynamiques (noms, montants, dates)
- ✅ Variables calculées (pourcentages, totaux)
- ✅ Variables optionnelles présentes

### Interdit Sur

- ❌ Texte fixe légal (Code civil)
- ❌ Titres de sections
- ❌ Labels fixes

### Format

```jinja2
**Prix** : <<<VAR_START>>>{{ prix.montant | format_nombre }}<<<VAR_END>>> EUR
```

**Pas d'espace** entre marqueurs et `{{}}` :
```jinja2
# ✅ BON
<<<VAR_START>>>{{ var }}<<<VAR_END>>>

# ❌ MAUVAIS
<<<VAR_START>>> {{ var }} <<<VAR_END>>>
```

---

## 🚀 Optimisations Performances

### 1. Conditions Courtes en Début

```jinja2
# ✅ BON - Évaluation rapide
{% if prix and prix.montant %}
...section longue...
{% endif %}

# ❌ MAUVAIS - Évaluation à la fin
...section longue...
{% if prix and prix.montant %}
...
{% endif %}
```

### 2. Éviter Recalculs dans Boucles

```jinja2
# ❌ MAUVAIS - Calcul à chaque itération
{% for lot in bien.lots %}
{{ (lot.surface / bien.surface_totale * 100) | round(2) }}%
{% endfor %}

# ✅ BON - Calcul une fois
{% set surface_totale = bien.surface_totale %}
{% for lot in bien.lots %}
{{ (lot.surface / surface_totale * 100) | round(2) }}%
{% endfor %}
```

### 3. Filtres Jinja2 Optimisés

**Préférer** :
- `format_nombre` (filtre custom rapide)
- `format_date` (filtre custom)

**Éviter** :
- Calculs Python complexes inline
- Filtres chainés excessifs

---

## 🧪 Tests Automatisés

### Script `test_fiabilite.py`

```bash
python execution/test_fiabilite.py --verbose
```

**Vérifie** :
- ✅ Assemblage données minimales
- ✅ Assemblage données maximales
- ✅ Zones grisées présentes
- ✅ Sections obligatoires
- ✅ Conformité ≥ seuil

**Seuils** :
- Données minimales : 60%
- Données maximales : 70%+

### Test Rapide Manuel

```bash
# 1 commande = 4 tests
python execution/workflow_rapide.py \
  --type vente \
  --donnees .tmp/donnees_test_vague5_enrichi.json \
  --sections all \
  --output .tmp/test/
```

---

## 📚 Ressources

### Documentation Jinja2

- Conditions : https://jinja.palletsprojects.com/templates/#if
- Boucles : https://jinja.palletsprojects.com/templates/#for
- Includes : https://jinja.palletsprojects.com/templates/#include
- Filtres : https://jinja.palletsprojects.com/templates/#list-of-builtin-filters

### Fichiers Clés

| Fichier | Description |
|---------|-------------|
| `execution/assembler_acte.py` | Moteur assemblage (lignes 558-568: messages erreur améliorés) |
| `execution/valider_rapide.ps1` | Script validation Windows |
| `execution/workflow_rapide.py` | Génération 1 commande |
| `execution/test_fiabilite.py` | Tests automatisés |
| `directives/pipeline_generation.md` | Pipeline 3 étapes |

---

## ✨ Résumé

**3 Règles d'Or** :

1. **Toujours** protéger variables par `{% if %}`
2. **Toujours** ajouter sections à la FIN
3. **Toujours** tester après CHAQUE ajout

**Gain de temps** :
- Sans bonnes pratiques : 60 min debug / section
- Avec bonnes pratiques : 5 min / section

**→ 12x plus rapide** 🚀

---

**Dernière mise à jour** : 2026-01-21 (Vague 5 complète - 76.7%)
