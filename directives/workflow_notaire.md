# Workflow Notaire - Guide Complet

> Cette directive décrit le workflow complet pour qu'un notaire génère un acte avec NotaireAI.

**Version**: 2.3.0 | **Date**: 2026-01-29

---

## 🎯 Objectif

Générer des actes notariaux **100% identiques** aux trames originales en suivant un processus guidé, fiable et rapide.

---

## ⚡ Raccourcis Claude Code (Skills)

Les workflows les plus courants sont accessibles via des commandes `/slash` dans Claude Code:

| Besoin | Commande | Ce qui se passe |
|--------|----------|----------------|
| Générer un acte | `/generer-acte vente` | Pipeline complet: validation → assemblage → DOCX |
| Générer une promesse | `/generer-promesse standard` | Détection auto du type + génération |
| Tester le pipeline | `/test-pipeline` | pytest + conformité templates |
| Auditer un template | `/valider-template all` | Comparaison vs trames originales |
| Déployer en prod | `/deploy-modal prod` | Tests → deploy Modal |
| Voir le status | `/status` | Dashboard complet du projet |

Ces skills appellent les mêmes scripts Python que le workflow ci-dessous, mais automatisent l'enchainement.

---

## 📋 Prérequis

### Pour l'Agent NotaireAI

Avant toute génération d'acte, **TOUJOURS** vérifier:

1. ✅ Le template existe et est conforme (≥80%)
2. ✅ Les schémas JSON sont à jour
3. ✅ Les questions de collecte sont complètes
4. ✅ Les exemples de données existent

### Conformité des Templates

#### Actes de Vente et Copropriété

| Template | Conformité | Statut | Action |
|----------|-----------|--------|--------|
| `reglement_copropriete_edd.md` | **85.5%** | ✅ PROD | Utiliser directement |
| `modificatif_edd.md` | **91.7%** | ✅ PROD | Utiliser directement |
| `vente_lots_copropriete.md` | **80.2%** | ✅ PROD | 37 sections, données enrichies requises |

#### 🆕 Promesses de Vente (Système Multi-Templates v1.4.0)

| Type | Template | Conformité | Cas d'usage |
|------|----------|-----------|-------------|
| **Standard** | `promesse/promesse_standard.md` | **88.9%** | ✅ PROD | 1 bien simple |
| **Premium** | `promesse/promesse_premium.md` | **85.2%** | ✅ PROD | Diagnostics exhaustifs |
| **Avec mobilier** | `promesse/promesse_avec_mobilier.md` | **87.1%** | ✅ PROD | Vente meublée |
| **Multi-biens** | `promesse/promesse_multi_biens.md` | **82.4%** | ✅ PROD | Lot + parking + cave |

**Détection automatique**: Le système choisit le bon template selon les données fournies.

### ⚡ Performance Pipeline (v1.4.0)

| Étape | Durée | Description |
|-------|-------|-------------|
| Assemblage Jinja2 | **1.5s** | Template + données → Markdown |
| Export DOCX | **3.5s** | Markdown → Word avec formatage |
| Vérification conformité | **0.7s** | Comparaison structure originale |
| **TOTAL** | **5.7s** | ~8 pages/seconde |

**Workflow Titre → Promesse** (v1.4.0):

| Étape | Durée | Description |
|-------|-------|-------------|
| Extraction titre (PDF/DOCX) | **2.0s** | OCR + patterns avancés |
| Détection type promesse | **0.2s** | Analyse automatique |
| Génération promesse | **5.7s** | Pipeline complet |
| **TOTAL** | **~8s** | Titre → DOCX en une commande |

**Si template <80%**: Utiliser les exemples fournis dans `exemples/` jusqu'à enrichissement complet.

### 🆕 Collecte Interactive Q&R Sprint 3 (v1.6.0)

Le `CollecteurInteractif` dans `agent_autonome.py` permet une collecte schema-driven:

| Mode | Description | Pré-remplissage |
|------|-------------|-----------------|
| `cli` | Questions interactives terminal | 64% depuis données existantes |
| `prefill_only` | Automatique, pas de questions | 100% (données + défauts) |

```bash
# Mode interactif (pose les questions manquantes)
python execution/agent_autonome.py interactif-qr --type promesse_vente

# Mode automatique (pré-remplit tout)
python execution/agent_autonome.py interactif-qr --type promesse_vente --auto

# Demo complète: titre → Q&R → promesse → DOCX
python execution/demo_titre_promesse.py --auto
python execution/demo_titre_promesse.py --titre titre.json --prix 500000
```

**Pipeline démo complet**: ~26s pour titre → collecte → validation → assemblage → DOCX.

### 🆕 Intégration Backend Sprint 2 (v1.5.1)

| Fonctionnalité | Endpoint | Statut |
|----------------|----------|--------|
| Streaming SSE | `POST /agent/execute-stream` | ✅ Déployé |
| Téléchargement DOCX | `GET /files/{filename}` | ✅ Déployé |
| Persistance conversations | `POST /chat` + Supabase | ✅ Déployé |
| Validation pré-génération | `POST /promesses/valider` | ✅ Déployé |

**Flux complet :**
```
Dashboard/Chat → POST /promesses/generer → DOCX → GET /files/{name} → Download
                 ↑                                        ↑
        X-API-Key header                          X-API-Key header
```

**Donnée de démo complète** : `exemples/donnees_demo_complete.json` (vendeur + acquéreur + bien complet)

---

## 🔄 Workflow en 5 Étapes

### Étape 1: Identification du Besoin

**Notaire dit**: "Je veux créer un acte de vente" / "Génère-moi une promesse" / etc.

**Agent fait**:
```python
# 1. Détecter le type d'acte
type_acte = detecter_depuis_description(description_notaire)

# 2. Pour promesse: détecter le sous-type automatiquement
if type_acte == "promesse":
    from execution.gestionnaire_promesses import GestionnairePromesses
    gestionnaire = GestionnairePromesses()
    detection = gestionnaire.detecter_type(donnees)
    # detection.type_promesse: standard | premium | avec_mobilier | multi_biens

# 3. Vérifier conformité template
conformite = verifier_conformite_template(type_acte)

# 4. Informer le notaire
if conformite < 80:
    avertir_notaire(f"Template {type_acte} est à {conformite}%, je vais utiliser un exemple complet")
```

**Agent dit** (pour promesse):
> "Je vais créer une promesse de vente. D'après les données, je détecte une vente **avec mobilier** (confiance 85%). Le template correspondant est prêt à 87.1%. Je génère le document."

**Agent dit** (pour vente):
> "Je vais créer un acte de vente. Le template est prêt à 80.2%. Voulez-vous que je collecte vos données ou utilise un exemple?"

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
    --original "docs_original/Trame vente lots de copropriété.docx" \
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

### Règlement copropriété et modificatif EDD

```bash
# One-liner complet
python execution/collecter_informations.py --type reglement --output .tmp/client.json && \
python execution/assembler_acte.py -t reglement_copropriete_edd.md -d .tmp/client.json -o .tmp/out --zones-grisees && \
python execution/exporter_docx.py --input .tmp/out/*/acte.md --output outputs/acte_final.docx && \
python execution/comparer_documents.py --original "docs_original/Trame reglement copropriete EDD.docx" --genere outputs/acte_final.docx
```

**Temps total**: ~30 secondes pour collecte + 2-3s pour génération = **<1 minute** pour acte complet validé.

---

### 🆕 Promesses de Vente (v1.4.0)

#### Génération depuis données

```bash
# Avec détection automatique du type
python notaire.py promesse-avancee generer \
    --donnees donnees_promesse.json \
    --output promesse_client.docx

# Avec profil prédéfini
python notaire.py promesse-avancee generer \
    --donnees donnees.json \
    --profil agence_premium \
    --output promesse_premium.docx
```

#### Génération depuis titre de propriété

```bash
# 1. Extraire le titre (optionnel si déjà en JSON)
python notaire.py extraire titre.pdf -o titre.json

# 2. Générer la promesse depuis le titre
python notaire.py promesse-avancee depuis-titre \
    --titre titre.json \
    --beneficiaires beneficiaires.json \
    --prix 250000 \
    --output promesse_client.docx
```

#### Utilitaires

```bash
# Détecter le type de promesse
python notaire.py promesse-avancee detecter --donnees donnees.json

# Valider les données
python notaire.py promesse-avancee valider --donnees donnees.json

# Lister les profils disponibles
python notaire.py promesse-avancee profils

# Lister les types de promesse
python notaire.py promesse-avancee types
```

**Temps total promesse**: ~8 secondes pour génération complète avec détection automatique.

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

### Cas 2: "Génère-moi une promesse de vente"

**Conformité template**: 82-89% ✅ (selon type détecté)

**Agent dit**:
> "Je détecte une promesse de type **avec mobilier** (confiance 92%). Le template correspondant est prêt à 87.1%. Je génère le document."

**Agent fait**:
1. 🔍 Détection automatique du type (standard/premium/avec_mobilier/multi_biens)
2. ✅ Validation des données obligatoires
3. 📋 Suggestions de sections conditionnelles
4. 🔧 Génération avec template spécialisé
5. 📦 Export DOCX fidèle à la trame

**Notaire reçoit**:
- DOCX prêt avec toutes les sections du type détecté
- Rapport de conformité avec confiance de détection

---

### Cas 2b: "Génère une promesse depuis ce titre de propriété"

**Workflow titre → promesse** (v1.4.0):

**Agent fait**:
```bash
python notaire.py promesse-avancee depuis-titre \
    --titre titre_propriete.pdf \
    --beneficiaires beneficiaires.json \
    --prix 250000 \
    --output promesse_client.docx
```

**Étapes automatisées**:
1. 📄 Extraction du titre (OCR + patterns avancés)
2. 🔄 Conversion vers données promesse (promettants = propriétaires)
3. 🔍 Détection automatique du type
4. ✅ Validation + enrichissement données
5. 🔧 Génération DOCX
6. 💾 Archivage Supabase (optionnel)

**Notaire reçoit**:
- DOCX avec promettants pré-remplis depuis le titre
- Données enrichies automatiquement (cadastre, copropriété, etc.)
- Champs bénéficiaires à compléter si non fournis

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
    --original docs_original/trame.docx \
    --genere outputs/acte.docx \
    --rapport .tmp/diff.json

# 2. Analyser différences
jq '.differences[] | select(.type == "titre_manquant")' .tmp/diff.json

# 3. Extraire sections manquantes du DOCX original
python execution/extraire_bookmarks_contenu.py \
    --input docs_original/trame.docx \
    --sections-manquantes .tmp/diff.json \
    --output .tmp/sections_a_ajouter.md

# 4. Ajouter au template avec Jinja2
# (Manuel ou semi-automatique)
```

### Métriques de Succès

| Métrique | Objectif | Actuel (v1.6.0) |
|----------|----------|-----------------|
| Templates PROD (≥80%) | 8/8 | **7/8** ✅ |
| Conformité moyenne | ≥85% | **86.2%** ✅ |
| Temps génération | <1 min | ~8s |
| Taux erreur | <5% | ~1.5% |
| Promesses avec détection auto | 100% | **100%** ✅ |
| Tests automatisés | 100% pass | **194/194** ✅ |
| Pipeline E2E promesse→DOCX | OK | **92.8 Ko** ✅ |
| Pipeline E2E vente→DOCX | OK | **72 Ko** ✅ |
| Collecte Q&R pré-remplissage | ≥60% | **64%** ✅ |

#### Détail par type d'acte

| Type | Templates | Conformité | Statut |
|------|-----------|-----------|--------|
| Vente | 1 | 80.2% | ✅ PROD |
| Promesse Standard | 1 | 88.9% | ✅ PROD |
| Promesse Premium | 1 | 85.2% | ✅ PROD |
| Promesse Mobilier | 1 | 87.1% | ✅ PROD |
| Promesse Multi-biens | 1 | 82.4% | ✅ PROD |
| Règlement Copro | 1 | 85.5% | ✅ PROD |
| Modificatif EDD | 1 | 91.7% | ✅ PROD |

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
3. ❌ **JAMAIS** modifier `docs_original/` (référence absolue)
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

## 🆕 Intégration Supabase (v1.4.0)

### Stockage des Titres de Propriété

```sql
-- Recherche par adresse
SELECT * FROM titres_propriete
WHERE adresse_bien ILIKE '%jean jaurès%';

-- Historique des promesses générées
SELECT * FROM promesses_generees
WHERE etude_id = 'mon_etude'
ORDER BY created_at DESC;
```

### Workflow avec Supabase

```python
from execution.gestionnaire_promesses import GestionnairePromesses

gestionnaire = GestionnairePromesses()

# Rechercher un titre existant
titres = gestionnaire.rechercher_titre_par_adresse("25 avenue Jean Jaurès")

# Générer depuis titre stocké
if titres:
    donnees, resultat = gestionnaire.generer_depuis_titre(
        titre_data=titres[0],
        beneficiaires=[{"nom": "DUPONT", "prenoms": "Jean"}],
        prix={"montant": 250000}
    )
```

---

---

## 🔄 Workflow Promesse → Vente (v1.5.1)

Lorsqu'une promesse a été signée, le notaire peut convertir les données de la promesse pour générer l'acte de vente définitif. Ce workflow conserve automatiquement les données déjà collectées.

```
Données Promesse                     Données Vente
┌─────────────────┐                  ┌─────────────────┐
│ promettants[] ──────────────────►  │ vendeurs[]       │
│ beneficiaires[] ────────────────►  │ acquereurs[]     │
│ bien {}  ───────────────────────►  │ bien {}          │
│ prix {}  ───────────────────────►  │ prix {}          │
│ copropriete {} ─────────────────►  │ copropriete {}   │
│ diagnostics {} ─────────────────►  │ diagnostics {}   │
│ origine_propriete {} ───────────►  │ origine {} + ref │
│ conditions_suspensives ─────────►  │ avant_contrat {} │
└─────────────────┘                  └─────────────────┘
                                     + paiement{}
                                     + jouissance{}
                                     + fiscalite{}
                                     + publication{}
```

### Utilisation

```bash
# Convertir une promesse en données de vente
python execution/utils/convertir_promesse_vente.py \
    --promesse exemples/donnees_promesse_exemple.json \
    --output .tmp/donnees_vente_depuis_promesse.json

# Compléter les données spécifiques à la vente puis générer
python execution/workflow_rapide.py --type vente \
    --donnees .tmp/donnees_vente_depuis_promesse.json
```

### Champs ajoutés automatiquement

| Champ vente | Source |
|-------------|--------|
| `avant_contrat.type` | `"promesse_unilaterale"` |
| `avant_contrat.date` | date de la promesse |
| `paiement.mode` | déduit de `financement` |
| `jouissance.date_propriete` | `"ce jour"` (par défaut) |
| `fiscalite.plus_value` | conservé de la promesse |
| `publication` | service de publicité foncière |

---

## Voir aussi

- [directives/creer_promesse_vente.md](creer_promesse_vente.md) - Création promesses (4 types)
- [directives/generation_promesses_avancee.md](generation_promesses_avancee.md) - Documentation complète v1.4
- [directives/workflow_titre_promesse_vente.md](workflow_titre_promesse_vente.md) - Workflow titre → promesse → vente
- [execution/gestionnaire_promesses.py](../execution/gestionnaire_promesses.py) - Gestionnaire principal
- [execution/utils/convertir_promesse_vente.py](../execution/utils/convertir_promesse_vente.py) - Conversion promesse → vente
- [schemas/promesse_catalogue_unifie.json](../schemas/promesse_catalogue_unifie.json) - Catalogue unifié

---

**Version**: 2.3.0
**Dernière mise à jour**: 2026-01-29
**Sprint 3 (P3+P4)**: Collecte Q&R interactive, démo titre→promesse→DOCX, conversion promesse→vente, 194 tests
**Prochaine révision**: Quand support autres types d'actes (donation, succession)
