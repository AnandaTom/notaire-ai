# Flexibilité du Système - Guide Complet

> **Principe fondamental** : Le système DOIT être 100% flexible pour s'adapter à chaque cas client tout en garantissant la conformité légale.

---

## 🎯 Objectifs de Flexibilité

1. **Sections optionnelles** : Inclure/exclure selon le cas
2. **Variables toujours grisées** : Même quand remplies (traçabilité)
3. **Clauses modulaires** : Ajouter/retirer facilement
4. **Annexes dynamiques** : S'adaptent au contexte
5. **Conditions intelligentes** : Sections n'apparaissent que si pertinentes

---

## ✅ Ce qui EST Déjà Flexible

### 1. Sections Conditionnelles (100% des sections)

**Toutes** les sections utilisent `{% if %}` pour n'apparaître que si nécessaire :

```jinja2
{# Section n'apparaît QUE si indivision existe #}
{% if indivision %}
# Fixation de la proportion de propriété indivise
...
{% endif %}

{# Section n'apparaît QUE si urbanisme.plu existe #}
{% if urbanisme and urbanisme.plu %}
## Plan Local d'Urbanisme
...
{% endif %}

{# Section n'apparaît QUE si plusieurs acquéreurs #}
{% if quotites_acquises|length > 1 %}
### FIXATION DE LA PROPORTION DE PROPRIÉTÉ INDIVISE
...
{% endif %}
```

**Résultat** :
- Client avec 1 acquéreur → Pas de section indivision ✅
- Client sans agent immobilier → Pas de section négociation ✅
- Client sans prêt → Pas de section financement emprunt ✅

### 2. Variables TOUJOURS Grisées

**Garantie absolue** : Les zones `<<<VAR_START>>>...<<<VAR_END>>>` sont **TOUJOURS** présentes.

```jinja2
{# MAUVAIS - Variable non grisée #}
{{ vendeur.nom | upper }}

{# BON - Variable grisée (même si remplie) #}
<<<VAR_START>>>{{ vendeur.nom | upper }}<<<VAR_END>>>
```

**Dans le DOCX final** :
```
Vendeur: DUPONT  ← "DUPONT" apparaît avec fond gris
         ^^^^^^
         Zone modifiable identifiable
```

**Pourquoi c'est critique** :
1. **Traçabilité** : Le notaire voit quelles données proviennent du système
2. **Modification facile** : Zones clairement identifiables
3. **Conformité** : Respect des pratiques notariales

### 3. Clauses Modulaires (48 clauses disponibles)

**Catalogue** : `schemas/clauses_catalogue.json`

**16 catégories** :
- Conditions suspensives (8 clauses)
- Paiement (6 clauses)
- Garanties (5 clauses)
- Fiscalité (4 clauses)
- Urbanisme (3 clauses)
- etc.

**Insertion dynamique** :

```python
# Méthode 1: Via script
python execution/inserer_clauses.py \
    --template vente_lots_copropriete.md \
    --clauses condition_pret_standard,garantie_eviction_totale \
    --output templates/vente_custom.md

# Méthode 2: Via include Jinja2
{% if paiement.condition_suspensive %}
{% include 'clauses/conditions_suspensives/condition_suspensive_pret_standard.md' %}
{% endif %}
```

**Résultat** : Le notaire peut activer/désactiver des clauses selon le dossier.

### 4. Annexes Dynamiques

**Liste automatique** selon données :

```jinja2
{% if annexes %}
# ANNEXES

{% for annexe in annexes %}
**Annexe n°{{ loop.index }}** : {{ annexe.titre }}
{% if annexe.description %}
{{ annexe.description }}
{% endif %}
{% endfor %}
{% endif %}
```

**Exemples d'annexes variables** :
- Diagnostics techniques (nombre variable)
- Plans de lots (selon nombre de lots)
- PV assemblées générales (si copropriété)
- Certificats (selon type de bien)

### 5. Logique Métier Intelligente

**Exemples de conditions intelligentes** :

```jinja2
{# Syndic obligatoire SEULEMENT si copropriété #}
{% if bien.copropriete %}
## COPROPRIÉTÉ
### Syndic
...
{% endif %}

{# Prêt SEULEMENT si financement #}
{% if paiement.fonds_empruntes > 0 %}
## FINANCEMENT PAR EMPRUNT
...
{% endif %}

{# Intervention conjoint SEULEMENT si marié sans séparation de biens #}
{% if vendeur.situation_matrimoniale.statut == 'marie' %}
{% if vendeur.situation_matrimoniale.regime_matrimonial != 'separation_biens' %}
## INTERVENTION DU CONJOINT
...
{% endif %}
{% endif %}
```

---

## 🔧 Configuration par Cas Client

### Cas 1 : Vente Simple (Célibataire, Sans Prêt, Sans Agent)

**Données minimales** :
```json
{
  "vendeurs": [{"civilite": "Monsieur", "nom": "DUPONT", "situation_matrimoniale": {"statut": "celibataire"}}],
  "acquereurs": [{"civilite": "Madame", "nom": "MARTIN"}],
  "bien": {"adresse": "...", "lots": [...]},
  "prix": {"montant": 250000},
  "paiement": {"mode": "comptant", "fonds_personnels": 250000}
}
```

**Sections générées** :
- ✅ Comparution
- ✅ Désignation
- ✅ Prix
- ✅ Paiement (sans section prêt)
- ❌ Indivision (1 seul acquéreur)
- ❌ Négociation (pas d'agent)
- ❌ Financement emprunt (pas de prêt)

### Cas 2 : Vente Complexe (Couple, Prêt, Agent, Indivision)

**Données complètes** :
```json
{
  "vendeurs": [{
    "situation_matrimoniale": {
      "statut": "marie",
      "regime_matrimonial": "communaute_reduite_acquets",
      "conjoint": {...}
    }
  }],
  "acquereurs": [{"nom": "MARTIN"}, {"nom": "BERNARD"}],
  "quotites_acquises": [{"personne_index": 0, "pourcentage": 60}, {"personne_index": 1, "pourcentage": 40}],
  "indivision": {...},
  "paiement": {
    "fonds_empruntes": 200000,
    "prets": [{...}]
  },
  "negociation": {
    "agent_immobilier": {...}
  }
}
```

**Sections générées** :
- ✅ Comparution (avec intervention conjoint vendeur)
- ✅ Indivision (proportions, financement)
- ✅ Négociation (commission agent)
- ✅ Financement emprunt (détails prêt)
- ✅ Garanties hypothécaires
- ✅ TOUTES les sections pertinentes

---

## 🎨 Personnalisation Avancée

### 1. Sections Personnalisées par Notaire

**Créer une section custom** :

```bash
# 1. Créer fichier Markdown
cat > templates/sections/ma_section_custom.md <<'EOF'
## MA SECTION PERSONNALISÉE

{% if mon_critere %}
Texte personnalisé avec <<<VAR_START>>>{{ ma_variable }}<<<VAR_END>>>
{% endif %}
EOF

# 2. Inclure dans template
echo "{% include 'sections/ma_section_custom.md' %}" >> templates/vente_lots_copropriete.md
```

### 2. Variantes de Templates

**Créer des variantes** pour différents cas :

```
templates/
├── vente_lots_copropriete.md           # Standard
├── vente_lots_copropriete_viager.md    # Variante viager
├── vente_lots_copropriete_sci.md       # Variante SCI
└── vente_lots_copropriete_etranger.md  # Variante acquéreur étranger
```

**Différences** :
- Viager → Sections rente viagère, DUH
- SCI → Sections associés, parts sociales
- Étranger → Sections fiscalité non-résident, certificat résidence

### 3. Clauses Spécifiques Notaire

**Ajouter au catalogue** :

```json
{
  "categories": {
    "mon_notaire_clauses": {
      "nom": "Clauses Notaire XYZ",
      "clauses": [
        {
          "id": "clause_specifique_1",
          "nom": "Ma clause personnalisée",
          "texte": "Texte avec {{ variables }}",
          "variables_requises": ["var1", "var2"],
          "source": "Notaire XYZ - Cas ABC",
          "date_ajout": "2026-01-21"
        }
      ]
    }
  }
}
```

**Utilisation** :
```jinja2
{% if conditions_specifiques %}
{% include 'clauses/mon_notaire_clauses/clause_specifique_1.md' %}
{% endif %}
```

---

## 🔍 Détection Automatique du Contexte

### Variables de Contexte Automatiques

Le système enrichit automatiquement les données avec du contexte :

```python
# Dans assembler_acte.py
donnees_enrichies = {
    **donnees,
    'contexte': {
        'nb_vendeurs': len(donnees.get('vendeurs', [])),
        'nb_acquereurs': len(donnees.get('acquereurs', [])),
        'indivision': len(donnees.get('acquereurs', [])) > 1,
        'avec_pret': donnees.get('paiement', {}).get('fonds_empruntes', 0) > 0,
        'avec_agent': 'negociation' in donnees and 'agent_immobilier' in donnees['negociation'],
        'copropriete': 'copropriete' in donnees.get('bien', {}),
        'vendeur_marie': any(v.get('situation_matrimoniale', {}).get('statut') == 'marie' for v in donnees.get('vendeurs', []))
    }
}
```

**Utilisation dans templates** :
```jinja2
{% if contexte.indivision %}
# Section Indivision
{% endif %}

{% if contexte.avec_agent %}
# Section Négociation
{% endif %}

{% if contexte.vendeur_marie %}
## INTERVENTION DU CONJOINT
{% endif %}
```

---

## 📊 Tableau de Flexibilité

| Élément | Flexible ? | Méthode | Exemple |
|---------|------------|---------|---------|
| **Sections** | ✅ 100% | Conditions `{% if %}` | Indivision n'apparaît que si >1 acquéreur |
| **Variables** | ✅ Toujours grisées | `<<<VAR_START>>>` | Modification facile post-génération |
| **Clauses** | ✅ Modulaires | Include ou script | 48 clauses réutilisables |
| **Annexes** | ✅ Dynamiques | Boucle `{% for %}` | Nombre variable selon dossier |
| **Template** | ✅ Variantes | Fichiers séparés | vente_standard.md vs vente_viager.md |
| **Données** | ✅ Optionnelles | Conditions robustes | Section n'apparaît que si donnée existe |

---

## 💡 Workflow Notaire - Cas d'Usage Réels

### Scénario A : "J'ai un cas standard"

```bash
# 1. Copier données exemple
cp exemples/donnees_vente_exemple.json dossiers/client_A/donnees.json

# 2. Remplir les champs (via formulaire ou manuellement)
nano dossiers/client_A/donnees.json

# 3. Générer en 1 commande
python execution/workflow_rapide.py \
    --type vente \
    --donnees dossiers/client_A/donnees.json \
    --sections all

# 4. Ouvrir DOCX généré avec zones grisées
# 5. Ajuster manuellement si besoin (zones grisées identifiables)
```

### Scénario B : "J'ai besoin d'ajouter une clause spécifique"

```bash
# 1. Lister clauses disponibles
cat schemas/clauses_catalogue.json | jq '.categories | keys'

# 2. Ajouter clause dans données JSON
{
  "clauses_additionnelles": ["condition_suspensive_vente_bien_vendeur"]
}

# 3. Ou insérer directement dans template
python execution/inserer_clauses.py \
    --template vente_lots_copropriete.md \
    --clauses condition_suspensive_vente_bien_vendeur \
    --position avant_prix
```

### Scénario C : "J'ai un cas particulier (viager, SCI, etc.)"

```bash
# 1. Créer template variante (1 fois)
cp templates/vente_lots_copropriete.md templates/vente_viager.md

# 2. Ajouter sections spécifiques viager
cat >> templates/vente_viager.md <<'EOF'
{% if viager %}
# RENTE VIAGÈRE
Bouquet : {{ viager.bouquet }} EUR
Rente mensuelle : {{ viager.rente_mensuelle }} EUR
{% endif %}
EOF

# 3. Utiliser template viager
python workflow_rapide.py --type vente --template vente_viager.md ...
```

---

## 🚀 Recommandations pour Maximiser Flexibilité

### 1. Pour Chaque Nouveau Cas

- ✅ Créer données JSON dans `dossiers/client_X/`
- ✅ Inclure UNIQUEMENT variables nécessaires
- ✅ Laisser le template gérer les sections conditionnelles
- ❌ NE PAS modifier le template pour chaque client

### 2. Pour Enrichir le Système

- ✅ Ajouter nouvelles clauses à `clauses_catalogue.json`
- ✅ Créer sections réutilisables dans `templates/sections/`
- ✅ Documenter dans `schemas/variables_*.json`
- ✅ Tester avec `workflow_rapide.py --validate`

### 3. Pour Garantir Qualité

- ✅ Toujours utiliser zones grisées `<<<VAR_START>>>`
- ✅ Toujours entourer sections de `{% if %}`
- ✅ Toujours tester avec données minimales ET complètes
- ✅ Toujours valider conformité avec document original

---

## 📝 Checklist Flexibilité

Avant de livrer un template, vérifier :

- [ ] Toutes sections ont conditions `{% if %}`
- [ ] Toutes variables ont zones grisées
- [ ] Template fonctionne avec données minimales
- [ ] Template fonctionne avec données complètes
- [ ] Sections inutiles n'apparaissent PAS
- [ ] Variables manquantes ne cassent PAS le template
- [ ] DOCX généré a zones grisées visibles
- [ ] Conformité ≥ 80% avec document original

---

**Résumé** : Le système est **100% flexible** grâce aux conditions Jinja2, zones grisées systématiques, et architecture modulaire. Chaque cas client peut avoir son propre ensemble de sections sans modifier le template de base.
