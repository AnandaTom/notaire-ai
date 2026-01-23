# Workflow Notaire - Guide Complet

> Cette directive décrit le workflow complet pour qu'un notaire génère un acte avec NotaireAI.

---

## 🎯 Objectif

Générer des actes notariaux **100% identiques** aux trames originales en suivant un processus guidé, fiable et rapide.

---

## 📋 Prérequis

### Pour l'Agent NotaireAI

Avant toute génération d'acte, **TOUJOURS** vérifier:

1. ✅ Le template existe et est conforme (≥80%)
2. ✅ Les schémas JSON sont à jour
3. ✅ Les questions de collecte sont complètes
4. ✅ Les exemples de données existent

### Conformité des Templates

| Template | Conformité | Statut | Action |
|----------|-----------|--------|--------|
| `reglement_copropriete_edd.md` | **85.5%** | ✅ PROD | Utiliser directement |
| `modificatif_edd.md` | **91.7%** | ✅ PROD | Utiliser directement |
| `vente_lots_copropriete.md` | **85.1%** | ✅ PROD | 37 sections, données enrichies requises |
| `promesse_vente_lots_copropriete.md` | 60.9% | ⚠️ DEV | Utiliser `donnees_promesse_exemple.json` |

### ⚡ Performance Pipeline (v1.2.0)

| Étape | Durée | Description |
|-------|-------|-------------|
| Assemblage Jinja2 | **1.5s** | Template + données → Markdown |
| Export DOCX | **3.5s** | Markdown → Word avec formatage |
| Vérification conformité | **0.7s** | Comparaison structure originale |
| **TOTAL** | **5.7s** | ~8 pages/seconde |

**Si template <80%**: Utiliser les exemples fournis dans `exemples/` jusqu'à enrichissement complet.

---

## 🔄 Workflow en 5 Étapes

### Étape 1: Identification du Besoin

**Notaire dit**: "Je veux créer un acte de vente" / "Génère-moi une promesse" / etc.

**Agent fait**:
```python
# 1. Détecter le type d'acte
type_acte = detecter_depuis_description(description_notaire)

# 2. Vérifier conformité template
conformite = verifier_conformite_template(type_acte)

# 3. Informer le notaire
if conformite < 80:
    avertir_notaire(f"Template {type_acte} est à {conformite}%, je vais utiliser un exemple complet")
```

**Agent dit**:
> "Je vais créer un acte de vente. Le template actuel est en développement (46% de conformité avec l'original). Je vais utiliser les données d'exemple complètes pour garantir un document 100% conforme. Voulez-vous que je collecte vos données réelles ou utilise l'exemple?"

---

### Étape 2: Collecte des Informations

#### Option A: Collecte Interactive (RECOMMANDÉ pour PROD)

**Pour templates ≥80% uniquement**:

```bash
python execution/collecter_informations.py \
    --type reglement_copropriete \
    --output .tmp/dossier_client_001/donnees.json
```

L'agent pose les questions de `schemas/questions_reglement_copropriete.json` une par une avec validation.

#### Option B: Utiliser Exemple Complet

**Pour tous templates, surtout <80%**:

```bash
# Copier exemple → dossier client
cp exemples/donnees_vente_exemple.json .tmp/dossier_client_001/donnees.json
```

**Agent dit au notaire**:
> "J'utilise les données d'exemple. Vous pourrez les modifier après génération du DOCX ou me demander de personnaliser certains champs."

#### Option C: Données Fournies par Notaire

Si le notaire fournit un JSON ou des données structurées:

```bash
# Valider d'abord
python execution/valider_acte.py \
    --donnees donnees_notaire.json \
    --schema schemas/variables_vente.json
```

---

### Étape 3: Détection Automatique et Suggestion

Avant assemblage, utiliser l'intelligence du système:

```bash
# Détecter type (si pas évident)
python execution/detecter_type_acte.py \
    --donnees .tmp/dossier_client_001/donnees.json

# Suggérer clauses contextuelles
python execution/suggerer_clauses.py \
    --donnees .tmp/dossier_client_001/donnees.json \
    --output .tmp/dossier_client_001/suggestions.json
```

**Agent dit**:
> "J'ai détecté un acte de vente (100% de confiance). J'ai 11 suggestions de clauses selon votre contexte:
> - ⚠️ ALERTE: DPE classe G (passoire thermique) - Clause d'information obligatoire
> - Clause garantie d'éviction recommandée (plusieurs acquéreurs)
> - ..."

**Notaire peut**:
- Accepter toutes les suggestions
- Choisir manuellement
- Ignorer

---

### Étape 4: Génération de l'Acte

Pipeline automatique en 3 sous-étapes:

#### 4a. Assemblage (Jinja2)

```bash
python execution/assembler_acte.py \
    --template vente_lots_copropriete.md \
    --donnees .tmp/dossier_client_001/donnees.json \
    --output .tmp/dossier_client_001/acte_genere \
    --zones-grisees
```

**Génère**:
- `acte_genere/{id}/acte.md` - Markdown avec marqueurs zones grisées
- `acte_genere/{id}/donnees.json` - Données normalisées utilisées
- `acte_genere/{id}/metadata.json` - Historique, version, statut

#### 4b. Export DOCX

```bash
python execution/exporter_docx.py \
    --input .tmp/dossier_client_001/acte_genere/{id}/acte.md \
    --output outputs/acte_client_001.docx
```

**Formatage exact**:
- Times New Roman 11pt
- Marges: G=60mm, D=15mm, H/B=25mm
- Zones grisées pour variables
- Styles identiques à l'original

#### 4c. Validation Conformité

```bash
python execution/comparer_documents.py \
    --original "docs_originels/Trame vente lots de copropriété.docx" \
    --genere outputs/acte_client_001.docx \
    --rapport .tmp/dossier_client_001/conformite.json
```

**Si conformité ≥80%**: ✅ Document prêt pour le notaire
**Si conformité <80%**: ⚠️ Alerter et proposer corrections

---

### Étape 5: Archivage et Apprentissage

#### 5a. Sauvegarder dans Historique

```bash
python execution/historique_supabase.py \
    --action sauvegarder \
    --acte-id acte_client_001 \
    --donnees .tmp/dossier_client_001/donnees.json \
    --metadata .tmp/dossier_client_001/acte_genere/{id}/metadata.json
```

Mode offline si pas de connexion → sauvegarde locale en `historique/`.

#### 5b. Enrichissement Continu (CRITIQUE)

**TOUJOURS** après génération:

```python
# Si nouvelle clause utilisée → Ajouter au catalogue
if nouvelle_clause:
    enrichir_catalogue_clauses(clause, source="Dossier Client 001", date=today)

# Si nouvelle question posée → Ajouter au schéma
if nouvelle_question:
    enrichir_schema_questions(question, type_acte, section)

# Si nouvelle situation rencontrée → Documenter
if edge_case:
    documenter_lecons_apprises(cas, solution, fichier_impacte)
```

**Mettre à jour**:
- `schemas/clauses_catalogue.json`
- `schemas/questions_*.json`
- `directives/lecons_apprises.md`

---

## 🚀 Workflow Rapide (Templates PROD ≥80%)

Pour règlement copropriété et modificatif EDD:

```bash
# One-liner complet
python execution/collecter_informations.py --type reglement --output .tmp/client.json && \
python execution/assembler_acte.py -t reglement_copropriete_edd.md -d .tmp/client.json -o .tmp/out --zones-grisees && \
python execution/exporter_docx.py --input .tmp/out/*/acte.md --output outputs/acte_final.docx && \
python execution/comparer_documents.py --original "docs_originels/Trame reglement copropriete EDD.docx" --genere outputs/acte_final.docx
```

**Temps total**: ~30 secondes pour collecte + 2-3s pour génération = **<1 minute** pour acte complet validé.

---

## 🎯 Cas d'Usage Notaire

### Cas 1: "Génère-moi un EDD"

**Conformité template**: 85.5% ✅

**Agent fait**:
1. ✅ Vérifie conformité → PROD ready
2. 📋 Lance collecte interactive ou utilise exemple
3. 🔧 Assemble + exporte + valide
4. 📦 Livre DOCX conforme à 85.5%
5. 💾 Sauvegarde historique

**Notaire reçoit**: DOCX prêt à signer

---

### Cas 2: "Génère-moi un acte de vente"

**Conformité template**: 46% ⚠️

**Agent dit**:
> "Le template vente est en développement (46% de conformité). Pour garantir un document 100% conforme à la trame originale, je vais utiliser les données d'exemple complètes. Le document généré sera identique à la trame mais avec des données fictives que vous pourrez modifier."

**Agent fait**:
1. ⚠️ Détecte template <80%
2. 📄 Utilise `exemples/donnees_vente_exemple.json`
3. 🔧 Assemble + exporte (même pipeline)
4. 📦 Livre DOCX conforme aux sections présentes
5. 📝 **ENRICHIT le template** en analysant différences

**Notaire reçoit**:
- DOCX avec structure complète
- Liste des sections manquantes dans template
- Recommandation: "Utilisez ce DOCX comme base, je vais enrichir le template pour prochaine fois"

---

### Cas 3: "Modifie cette clause dans l'acte existant"

**Directive**: `directives/modifier_acte.md`

**Agent fait**:
1. 📖 Lit l'acte existant (DOCX ou JSON)
2. 🔍 Identifie la clause à modifier
3. ✏️ Applique modification
4. 🔧 Régénère avec données mises à jour
5. 📊 Compare ancien vs nouveau
6. 📦 Livre DOCX modifié

---

## 🛡️ Garanties de Conformité

### Pour Templates PROD (≥80%)

**GARANTIES**:
- ✅ Structure identique à la trame originale (≥80%)
- ✅ Formatage exact (marges, police, styles)
- ✅ Zones grisées pour variables
- ✅ Tableaux conformes
- ✅ Numérotation correcte

**NON GARANTI** (sections manquantes):
- ⚠️ Sections spécifiques absentes du template
- ⚠️ Styles personnalisés non standards

### Pour Templates DEV (<80%)

**GARANTIES**:
- ✅ Sections présentes sont 100% conformes
- ✅ Formatage exact
- ✅ Données structurées correctement

**NON GARANTI**:
- ⚠️ Sections manquantes (documentées dans rapport conformité)
- ⚠️ Template sera enrichi progressivement

---

## 📈 Amélioration Continue

### Après Chaque Acte

**Agent DOIT**:
1. Analyser différences conformité si <100%
2. Identifier sections manquantes
3. Proposer enrichissement template
4. Documenter edge cases dans `lecons_apprises.md`

### Enrichissement Template

**Process**:
```bash
# 1. Comparer structure
python execution/comparer_documents.py \
    --original docs_originels/trame.docx \
    --genere outputs/acte.docx \
    --rapport .tmp/diff.json

# 2. Analyser différences
jq '.differences[] | select(.type == "titre_manquant")' .tmp/diff.json

# 3. Extraire sections manquantes du DOCX original
python execution/extraire_bookmarks_contenu.py \
    --input docs_originels/trame.docx \
    --sections-manquantes .tmp/diff.json \
    --output .tmp/sections_a_ajouter.md

# 4. Ajouter au template avec Jinja2
# (Manuel ou semi-automatique)
```

### Métriques de Succès

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| Templates PROD (≥80%) | 4/4 | 2/4 |
| Conformité moyenne | ≥85% | 71% |
| Temps génération | <1 min | ~30s |
| Taux erreur | <5% | ~2% |

---

## ⚠️ Règles Critiques

### À FAIRE

1. ✅ **TOUJOURS** vérifier conformité template AVANT génération
2. ✅ **TOUJOURS** utiliser exemples complets si template <80%
3. ✅ **TOUJOURS** valider avec `comparer_documents.py`
4. ✅ **TOUJOURS** sauvegarder dans historique
5. ✅ **TOUJOURS** enrichir catalogues après génération

### À NE PAS FAIRE

1. ❌ **JAMAIS** générer avec données incomplètes
2. ❌ **JAMAIS** promettre conformité 100% si template <80%
3. ❌ **JAMAIS** modifier `docs_originels/` (référence absolue)
4. ❌ **JAMAIS** livrer DOCX sans validation conformité
5. ❌ **JAMAIS** oublier d'enrichir les catalogues

---

## 🎓 Formation Notaire

### Ce que le Notaire Doit Savoir

**Système mature** (≥80%):
- "Je génère ton acte en moins de 1 minute, 100% conforme"
- Collecte guidée question par question
- Validation automatique
- DOCX prêt à signer

**Système en développement** (<80%):
- "Je génère un acte avec les sections disponibles, puis j'enrichis le template pour la prochaine fois"
- Utilisation d'exemples complets
- Modification manuelle possible
- Amélioration progressive

### Ce que le Notaire Peut Demander

**Générations**:
- "Génère un acte de vente"
- "Crée une promesse unilatérale"
- "Fais-moi un EDD complet"
- "Modificatif pour division de lot"

**Modifications**:
- "Change le prix à 250 000€"
- "Ajoute un acquéreur"
- "Modifie la clause de garantie"

**Validations**:
- "Vérifie que c'est conforme"
- "Compare avec la trame originale"
- "Montre-moi ce qui manque"

**Apprentissage**:
- "Ajoute cette clause au catalogue"
- "Cette situation est nouvelle, documente-la"

---

## 📞 Support et Évolution

### Si Problème

1. Lire `directives/lecons_apprises.md`
2. Vérifier `CHANGELOG.md` pour version actuelle
3. Analyser rapport conformité `.tmp/conformite.json`
4. Documenter dans leçons apprises si nouveau cas

### Demandes d'Évolution

**Nouveau type d'acte**:
→ Suivre checklist dans `lecons_apprises.md`

**Nouvelle clause**:
→ Ajouter à `schemas/clauses_catalogue.json`

**Nouveau diagnostic**:
→ Ajouter à `schemas/annexes_catalogue.json`

---

**Version**: 1.1.0
**Dernière mise à jour**: 2026-01-20
**Prochaine révision**: Quand 4/4 templates ≥80%
