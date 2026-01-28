# 🚀 Guide Démarrage Rapide - Notomai

**Objectif** : Générer un acte notarial en 30 secondes

---

## ⚡ Méthode Ultra-Rapide (1 commande)

### Génération Complète

```bash
python execution/workflow_rapide.py \
  --type vente \
  --donnees .tmp/donnees_test_vague5_enrichi.json \
  --sections all
```

**Résultat** : Acte DOCX avec zones grisées dans `outputs/`

**Temps** : 30 secondes

---

## 📋 Méthode Pas-à-Pas (3 étapes)

### Étape 1: Préparer les Données (si besoin)

```bash
python execution/preparer_donnees_test.py \
  --input exemples/donnees_vente_exemple.json \
  --output .tmp/mes_donnees.json \
  --vague 5
```

**Ajoute automatiquement** :
- 16 variables obligatoires (urbanisme, indivision, etc.)
- Mensualités prêts calculées
- Garanties, fiscalité détaillée, lots (Vague 5)

### Étape 2: Générer l'Acte

```bash
python execution/assembler_acte.py \
  --template vente_lots_copropriete.md \
  --donnees .tmp/mes_donnees.json \
  --output .tmp/mon_acte/ \
  --zones-grisees
```

**Résultat** : Markdown dans `.tmp/mon_acte/{id}/acte.md`

### Étape 3: Exporter en DOCX

```bash
python execution/exporter_docx.py \
  --input .tmp/mon_acte/{id}/acte.md \
  --output outputs/mon_acte.docx \
  --zones-grisees
```

**Résultat** : DOCX fidèle avec zones grisées

---

## ✅ Validation Rapide (10 secondes)

### Avant Commit

```powershell
# Windows
.\execution\valider_rapide.ps1 vente

# Linux/Mac
./execution/valider_rapide.sh vente
```

**Teste** :
1. ✅ Assemblage données minimales
2. ✅ Assemblage données enrichies
3. ✅ Zones grisées présentes
4. ✅ Export DOCX

---

## 🧪 Tests Automatisés

```bash
python execution/test_fiabilite.py
```

**Vérifie** :
- Assemblage min + max
- Zones grisées
- Sections obligatoires
- Conformité ≥ 60% (min) / 70% (max)

**Objectif** : ≥ 75% de tests réussis (système fiable)

---

## 📊 Score de Conformité

```bash
python execution/comparer_documents_v2.py \
  --original "docs_original/Trame vente lots de copropriété.docx" \
  --genere outputs/mon_acte.docx
```

**Score actuel** : **76.7%** (Vague 5 complète)
**Objectif** : 90%

---

## 🎯 Fichiers Clés

### Données Exemples

| Fichier | Niveau | Sections |
|---------|--------|----------|
| `exemples/donnees_vente_exemple.json` | Enrichi | 16 vars + prêts |
| `.tmp/donnees_test_vague3_enrichi.json` | Vague 3 | 22 H1 |
| `.tmp/donnees_test_vague5_enrichi.json` | Vague 5 | 22 H1 + 4 H2 |

### Templates

| Fichier | Type | Bookmarks |
|---------|------|-----------|
| `templates/vente_lots_copropriete.md` | Vente définitif | 361 |
| `templates/promesse_vente_lots_copropriete.md` | Promesse | 298 |

### Scripts Utiles

| Script | Usage |
|--------|-------|
| `workflow_rapide.py` | 🚀 Génération 1 commande |
| `preparer_donnees_test.py` | 🔧 Enrichissement auto |
| `valider_rapide.ps1/.sh` | ⚡ Validation pré-commit |
| `test_fiabilite.py` | ✅ Tests automatisés |

---

## 🛠️ Cas d'Usage Fréquents

### 1. Générer Acte avec Données Client

```bash
# 1. Créer fichier JSON avec données client
# 2. Préparer
python execution/preparer_donnees_test.py \
  --input client_data.json \
  --output .tmp/client_prepared.json

# 3. Générer
python execution/workflow_rapide.py \
  --type vente \
  --donnees .tmp/client_prepared.json \
  --sections all \
  --output outputs/
```

### 2. Tester Nouveau Template

```bash
# 1. Valider rapidement
.\execution\valider_rapide.ps1 vente

# 2. Tests complets
python execution/test_fiabilite.py --verbose

# 3. Score conformité
python execution/workflow_rapide.py \
  --type vente \
  --donnees .tmp/donnees_test_vague5_enrichi.json \
  --sections all \
  --validate
```

### 3. Développer Nouvelle Section

```markdown
# 1. Créer fichier section
templates/sections/section_ma_section.md

# 2. Intégrer dans partie_developpee.md (à la fin)
{% if ma_variable %}
{% include 'sections/section_ma_section.md' %}
{% endif %}

# 3. Enrichir données
python execution/preparer_donnees_test.py ...

# 4. Tester
.\execution\valider_rapide.ps1 vente

# 5. Si erreur, consulter
directives/bonnes_pratiques_templates.md
```

---

## 📚 Ressources

### Directives Essentielles

| Directive | Quand l'utiliser |
|-----------|------------------|
| [bonnes_pratiques_templates.md](directives/bonnes_pratiques_templates.md) | Créer/modifier templates Jinja2 |
| [pipeline_generation.md](directives/pipeline_generation.md) | Workflow génération standard |
| [workflow_notaire.md](directives/workflow_notaire.md) | Dialogue avec notaire |

### Aide Débogage

**Erreur `'X' is undefined`** :
- Consulter : [bonnes_pratiques_templates.md](directives/bonnes_pratiques_templates.md) section "Erreurs Fréquentes"
- Solution : Ajouter `{% if X %}` avant utilisation

**Erreur `TemplateNotFound`** :
- Vérifier dossier : `templates/sections/` (pas `.tmp/`)

**Score conformité bas** :
- Vérifier sections manquantes : `python execution/comparer_documents_v2.py ...`
- Consulter : `.tmp/SYNTHESE_SESSION_2026-01-21.md` section "Sections Manquantes"

---

## 🎓 Niveaux d'Utilisation

### Débutant
- ✅ Utiliser `workflow_rapide.py` uniquement
- ✅ Données : `.tmp/donnees_test_vague5_enrichi.json`
- ✅ Ne PAS modifier templates

### Intermédiaire
- ✅ Créer données client JSON
- ✅ Utiliser `preparer_donnees_test.py`
- ✅ Modifier variables dans templates (avec `{% if %}`)

### Avancé
- ✅ Créer nouvelles sections
- ✅ Enrichir scripts Vague 6/7
- ✅ Optimiser patterns Jinja2
- ✅ Contribuer à `bonnes_pratiques_templates.md`

---

## ⚡ Raccourcis

```bash
# Génération express
alias generer='python execution/workflow_rapide.py --type vente --donnees .tmp/donnees_test_vague5_enrichi.json --sections all'

# Validation express
alias valider='python execution/valider_rapide.ps1 vente'

# Tests express
alias tester='python execution/test_fiabilite.py'

# Usage
generer
valider
tester
```

---

## 📞 Support

**Problème** ? Consulter dans l'ordre :

1. 📖 [bonnes_pratiques_templates.md](directives/bonnes_pratiques_templates.md) - Patterns & erreurs
2. 📊 `.tmp/SYNTHESE_SESSION_2026-01-21.md` - Bugs résolus cette session
3. 🎯 `CLAUDE.md` - Documentation complète

**Amélioration** ? Ajouter à :
- `directives/bonnes_pratiques_templates.md` (nouveau pattern)
- `schemas/clauses_catalogue.json` (nouvelle clause)

---

## 🎯 Objectifs Actuels

| Vague | Score | Statut |
|-------|-------|--------|
| Vague 3 | 71.6% | ✅ Validé |
| Vague 4 | 74.3% | ✅ Validé |
| **Vague 5** | **76.7%** | ✅ **COMPLET** |
| Vague 6 | ~85% | ⏳ Prochaine étape |
| Vague 7 | ~90% | 🎯 Objectif final |

**Tests fiabilité** : **75%** (système fiable) ✅

**Temps restant vers 90%** : ~60 minutes

---

**Dernière mise à jour** : 2026-01-21 (Vague 5 complète)
