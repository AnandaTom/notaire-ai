# Changelog - NotaireAI

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [1.5.1] - 2026-01-28

### 🎯 Objectif de cette Release
Validation métier avancée avec 12 règles, support personnes morales, et API validation temps réel.

### ✨ Ajouté

#### Validation Métier Avancée (12 règles)
- **Validation quotités croisées** - Vérifie que vendeurs ET acquéreurs totalisent 100%
- **Validation cohérence cadastre** - Section, numéro, commune correspondant à l'adresse
- **Validation plus-value immobilière** - Résidence principale, durée détention, exonérations
- **Validation intervention conjoint** - Erreur si communauté sans signature conjoint
- **Validation diagnostics** - DPE expiration 10 ans, audit si passoire thermique (F/G)
- **Validation cohérence dates promesse** - Délai réalisation vs date prêt
- **Validation prix cohérent** - Prix/m² aberrant (alertes)

#### Support Personnes Morales
- **SCI, SARL, SAS, SA, SNC** - Validation complète dans les schémas
- **Validation SIREN** - Format 9 chiffres obligatoire
- **Représentant légal** - Qualité, nom, pouvoirs requis
- **RCS recommandé** - Pour sociétés commerciales

#### API Validation Temps Réel
- **`execution/api_validation.py`** - Endpoints FastAPI pour frontend
  - `POST /validation/donnees` - Validation complète
  - `POST /validation/champ` - Validation champ individuel
  - `GET /validation/schema/{type_acte}` - Récupérer schéma
- **MAPPING_CHAMPS_UI** - Noms lisibles pour interface

#### Tests Unitaires
- **`tests/test_exporter_docx.py`** - ~400 lignes, 35+ tests
  - Nettoyage XML, détection tableaux, marqueurs variables
  - Tests performance et contenu notarial
- **`tests/test_valider_acte.py`** - ~500 lignes, 50+ tests
  - Validation quotités, cadastre, diagnostics
  - Personnes morales (SCI, SARL)
  - Dates promesse, intervention conjoint

### 📝 Template Promesse Amélioré (60.9% → 69.7%)

#### 5 Nouvelles Sections Créées
- **`section_condition_vente_prealable.md`** - Condition suspensive vente bien préalable (complet)
- **`section_faculte_substitution.md`** - Faculté de substitution avec tous les cas (autorisée/refusée)
- **`section_indemnite_immobilisation_detaillee.md`** - Indemnité avec restitution, séquestre, clause pénale
- **`section_prorogation.md`** - Prorogation de la promesse (conditions, durée, forme)
- **`section_clause_penale.md`** - Clause pénale réciproque (promettant et bénéficiaire)

#### Variables Promesse Ajoutées
- `conditions_suspensives.vente_bien_prealable.*` - Description, adresse, date limite, notification
- `faculte_substitution.*` - Autorisée, conditions, délai notification, SCI
- `indemnite_immobilisation.version_detaillee` - Active la section complète
- `delais.prorogation.*` - Possible, durée max, conditions, forme
- `clause_penale.*` - Applicable, montants, cumul, mise en demeure

### 🔧 Amélioré

#### Agent Autonome v1.2
- **Intégration ValidateurActe** - Validation avancée avant génération
- **Génération quotités multi-parties** - Répartition automatique égale
- **Affichage structuré validation** - Erreurs/Avertissements/Suggestions

#### Orchestrateur
- **Import GestionnairePromesses** - Pour conversion promesse → vente
- **`_convertir_promesse_vers_vente` améliorée** - Deep copy, diagnostics, quotités auto

#### Schémas
- **`schemas/variables_vente.json`** - Ajout `personne_morale` dans `$defs`
- **vendeurs/acquereurs** - Support `oneOf` personne_physique | personne_morale

### 📁 Fichiers Modifiés/Créés

| Fichier | Action | Lignes |
|---------|--------|--------|
| `execution/valider_acte.py` | Modifié | +280 |
| `execution/api_validation.py` | Créé | ~450 |
| `execution/agent_autonome.py` | Modifié | +100 |
| `execution/orchestrateur_notaire.py` | Modifié | +50 |
| `schemas/variables_vente.json` | Modifié | +60 |
| `tests/test_exporter_docx.py` | Créé | ~400 |
| `tests/test_valider_acte.py` | Créé | ~500 |
| `docs/data/dashboard.json` | Modifié | Version 1.5.1 |
| `templates/sections/section_condition_vente_prealable.md` | Créé | ~60 |
| `templates/sections/section_faculte_substitution.md` | Créé | ~100 |
| `templates/sections/section_indemnite_immobilisation_detaillee.md` | Créé | ~120 |
| `templates/sections/section_prorogation.md` | Créé | ~80 |
| `templates/sections/section_clause_penale.md` | Créé | ~110 |
| `templates/sections/partie_developpee_promesse.md` | Modifié | +30 |

### ✅ Tests

```bash
# Tests validation
pytest tests/test_valider_acte.py -v

# Tests export DOCX
pytest tests/test_exporter_docx.py -v

# Validation complète
python execution/valider_acte.py --donnees exemples/donnees_vente_exemple.json
```

---

## [1.2.1] - 2026-01-22

### 🔧 Corrections Export DOCX

#### Styles des Titres
- **Couleur noire forcée** - Tous les styles Heading (1-5) ont maintenant `font.color.rgb = RGBColor(0, 0, 0)` pour éviter les titres bleus par défaut de Word
- **Support complet #### et #####** - `detecter_titre_markdown` détecte maintenant les 5 niveaux de titres Markdown (était limité à 3)
- **Mapping Heading 4/5** - Les titres `####` utilisent maintenant `Heading 4` (bold only, justified) et `#####` utilise `Heading 5` (bold, underline)

#### Zones Grisées dans les Titres
- **`ajouter_texte_formate(force_bold=)`** - Nouveau paramètre optionnel pour forcer le bold dans les titres tout en gérant les zones grisées
- **Titres notariaux** - Les sections `est_titre_notarial` et `est_sous_titre_notarial` utilisent maintenant `ajouter_texte_formate` avec `force_bold=True`
- **Cellules de tableau** - Les titres dans les cellules gèrent maintenant correctement les zones grisées

#### Formatage des Tableaux
- **Largeurs proportionnelles** - Calcul automatique des largeurs de colonnes basé sur le contenu (approximation 2.5mm/caractère)
- **Largeur minimale** - 15mm minimum par colonne pour éviter les colonnes trop étroites
- **Largeur totale fixe** - 135mm (page A4 - marges) pour des tableaux bien dimensionnés
- **Pas de retrait** - `first_line_indent = Pt(0)` dans les cellules de tableau

### 📁 Fichiers Modifiés

| Fichier | Changements |
|---------|-------------|
| `execution/exporter_docx.py` | Import `RGBColor`, couleur noire sur H1-H5, support H4/H5, largeurs tableaux proportionnelles |

### ✅ Tests

```bash
# Régénérer avec corrections
python execution/exporter_docx.py --input .tmp/acte_test_final/9489bd1b/acte.md --output .tmp/test_v2_corrections.docx --zones-grisees
```

---

## [1.1.0] - 2026-01-20

### 🎯 Objectif de cette Release
Amélioration majeure de la robustesse du système suite aux tests complets des 4 types d'actes.

### ✨ Ajouté

#### Scripts d'Exécution
- **`execution/collecter_informations.py`** - CLI interactive avec questionary et rich pour collecte guidée des données notaire
- **`execution/generer_donnees_test.py`** - Générateur de données aléatoires réalistes avec Faker
  - Support types: vente, promesse, règlement, modificatif
  - Données françaises (adresses Rhône, notaires Lyon, etc.)
  - ~900 lignes de code
- **`execution/comparer_documents.py`** - Validation conformité DOCX généré vs original
  - Score de conformité (structure, titres, tableaux)
  - Seuil: 80% pour production
  - ~400 lignes
- **`execution/detecter_type_acte.py`** - Détection automatique du type d'acte depuis JSON
  - Basé sur signatures (champs présents)
  - Retourne type + confidence + analyse
  - ~300 lignes
- **`execution/suggerer_clauses.py`** - Intelligence de suggestion de clauses contextuelles
  - 11+ suggestions selon contexte (DPE, emprunt, etc.)
  - Alertes spéciales (passoire thermique, emprunt collectif)
  - ~550 lignes
- **`execution/historique_supabase.py`** - Intégration Supabase pour historique des actes
  - CRUD complet: sauvegarder, charger, lister, rechercher
  - Mode offline fallback (fichiers locaux)
  - ~500 lignes

#### Catalogues Enrichis
- **`schemas/clauses_catalogue.json`** - Ajout 18 nouvelles clauses:
  - `reglement_copropriete` (9 clauses)
  - `modificatif_edd` (5 clauses)
  - `fiscalite_copropriete` (2 clauses)
  - `servitudes_copropriete` (2 clauses)
- **`schemas/annexes_catalogue.json`** - 28 types d'annexes documentées

#### Exemples
- `exemples/donnees_reglement_copropriete_exemple.json` - 12 lots, structure complète
- `exemples/donnees_modificatif_edd_exemple.json` - Division de lot type

#### Tests
- `tests/conftest.py` - Fixtures pytest (chemins, exemples)
- `tests/test_assembler_acte.py` - Unit tests filtres Jinja2
- `tests/test_integration.py` - Tests pipeline complet

#### Documentation
- **`directives/lecons_apprises.md`** ⭐ - **15 leçons** tirées des tests
  - Gestion structures données
  - Normalisation PACS
  - Encodage Unicode Windows
  - Deep copy vs shallow copy
  - Workflow création template
  - Checklist ajout nouveau type
- **`CHANGELOG.md`** - Ce fichier

### 🔧 Modifié

#### `execution/assembler_acte.py`
1. **Fix encodage deep copy** (ligne 35)
   ```python
   from copy import deepcopy
   donnees_enrichies = deepcopy(donnees)  # Au lieu de .copy()
   ```

2. **Aplatissement automatique personnes** (lignes 370-383)
   ```python
   # Aplatir personne_physique et personne_morale
   if 'personne_physique' in personne:
       donnees_enrichies[cle][i] = {**personne, **personne['personne_physique']}
       del donnees_enrichies[cle][i]['personne_physique']
   ```

3. **Normalisation PACS** (lignes 386-399)
   ```python
   # Créer alias conjoint pour partenaire
   if 'partenaire' in sitmat and 'conjoint' not in sitmat_norm:
       sitmat_norm['conjoint'] = sitmat['partenaire']

   # Restructurer données PACS
   sitmat_norm['pacs'] = {
       'date': sitmat.get('date_pacs'),
       'regime_libelle': sitmat.get('regime_pacs', 'séparation de biens'),
       'lieu_enregistrement': sitmat.get('lieu_pacs')
   }
   ```

4. **Nouveaux filtres Jinja2** (lignes 233-262, 373, 389)
   - `mois_en_lettres(mois: int)` - Convertit 1-12 → janvier-décembre
   - `jour_en_lettres(jour: int)` - Convertit 1-31 → premier, deux, trois...
   - Registrés dans l'environnement Jinja2

#### `execution/comparer_documents.py`
- **Fix encodage Windows** (lignes 48-50)
  ```python
  if sys.platform == 'win32':
      sys.stdout.reconfigure(encoding='utf-8', errors='replace')
  ```

#### `execution/generer_donnees_test.py`
1. **Amélioration `generer_situation_matrimoniale()`** (lignes 128-156)
   - PACS: Ajout `regime_pacs`, `lieu_pacs`, `conjoint` (alias)
   - Divorce: Ajout `jugement_divorce.date/lieu`, `ex_conjoint`
   - Veuf: Ajout `defunt_conjoint`

2. **Nouvelle fonction `normaliser_situation_matrimoniale()`** (lignes 161-188)
   - Restructure PACS en objet imbriqué pour compatibilité template
   - Restructure contrat_mariage pour mariés
   - Crée alias `conjoint` si manquant

3. **Amélioration `generer_donnees_vente()`** (lignes 738-948)
   - Force personnes physiques uniquement (compatibilité template)
   - Ajout **quotités vendues/acquises** (CRITIQUE - lignes 820-856)
   - Ajout surface Carrez globale (lignes 840-845, 914-917)
   - Ajout section **copropriété** complète (lignes 931-947)
   - Normalisation PACS dès génération (lignes 750-752, 796-798)

4. **Amélioration `generer_lot()` et `generer_lot_annexe()`** (lignes 287-302, 340-354)
   - Structure `tantiemes` enrichie:
     ```python
     "tantiemes": {
         "valeur": tantiemes_val,
         "base": 1000,
         "base_unite": "millièmes",
         "type": "tantièmes généraux"
     }
     ```

#### `requirements.txt`
Ajout dépendances:
```
questionary>=2.0.0
rich>=13.0.0
faker>=20.0.0
supabase>=2.0.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

### 🐛 Corrigé

1. **Unicode sur Windows**
   - Problème: `UnicodeEncodeError` avec ✓, é, à, etc.
   - Fix: `sys.stdout.reconfigure(encoding='utf-8', errors='replace')`
   - Fichiers: `comparer_documents.py`, `suggerer_clauses.py`, `generer_donnees_test.py`

2. **Shallow copy dictionnaires imbriqués**
   - Problème: Modifications involontaires avec `.copy()`
   - Fix: Utilisation `deepcopy()`
   - Fichier: `assembler_acte.py:369`

3. **Mismatch structure personne_physique**
   - Problème: Données nested, template attend flat
   - Fix: Aplatissement automatique dans `enrichir_donnees()`
   - Fichier: `assembler_acte.py:370-383`

4. **PACS: partenaire vs conjoint**
   - Problème: Incohérence nomenclature
   - Fix: Création alias `conjoint` automatique
   - Fichier: `assembler_acte.py:390` + `generer_donnees_test.py:135`

5. **Filtres Jinja2 manquants**
   - Problème: Template utilise `mois_en_lettres`, `jour_en_lettres` non définis
   - Fix: Création filtres
   - Fichier: `assembler_acte.py:233-262`

6. **Quotités absentes**
   - Problème: Template vente nécessite `quotites_vendues/acquises`
   - Fix: Génération automatique dans `generer_donnees_vente()`
   - Fichier: `generer_donnees_test.py:820-856`

7. **Données matrimoniales incomplètes**
   - Problème: Template attend `defunt_conjoint`, `ex_conjoint`, `jugement_divorce`
   - Fix: Génération complète pour tous statuts
   - Fichier: `generer_donnees_test.py:137-156`

8. **Structure tantièmes simplifiée**
   - Problème: Template attend `lot.tantiemes.valeur/base/type`
   - Fix: Génération structure complète
   - Fichier: `generer_donnees_test.py:295-300`

### 📊 Résultats Tests

| Type d'acte | Conformité | Statut | Fichiers |
|-------------|-----------|--------|----------|
| **Règlement copropriété** | **85.5%** | ✅ CONFORME | 117.8 Ko, 22 tableaux |
| **Modificatif EDD** | **91.7%** | ✅ CONFORME | 48.8 Ko, 3 tableaux |
| Acte de vente | 46.0% | ⚠️ Template incomplet | 80.4 Ko (manque 97 titres) |
| Promesse de vente | 60.9% | ⚠️ Template incomplet | 69.8 Ko (manque 24 titres) |

**Seuil de production**: ≥80% de conformité structurelle.

### 🎓 Leçons Clés

1. **Normalisation dans l'orchestration** - Toujours normaliser dans `assembler_acte.py`, pas dans le générateur
2. **Deep copy obligatoire** - Jamais utiliser `.copy()` pour dictionnaires imbriqués
3. **Validation pré-assemblage** - Utiliser `valider_acte.py` AVANT génération
4. **Templates ≥80% conformité** - Les templates doivent être complets, pas des squelettes
5. **Analyse DOCX en premier** - Toujours analyser avec `extraire_bookmarks_contenu.py` AVANT de coder

Voir [directives/lecons_apprises.md](directives/lecons_apprises.md) pour le détail complet.

### 🚀 Prochaines Étapes

- [ ] Enrichir templates vente et promesse pour atteindre ≥80%
- [ ] Créer tests de régression automatiques
- [ ] Implémenter cache Jinja2 pour performance
- [ ] Ajouter support personnes morales dans templates
- [ ] Créer script de migration données anciennes → nouvelles
- [ ] Documentation README.md pour utilisateurs finaux

---

## [1.0.0] - 2026-01-19

### 🎉 Release Initiale

#### Ajouté
- Architecture 3 layers (Directive / Orchestration / Execution)
- Script `assembler_acte.py` - Assemblage Jinja2 + enrichissement données
- Script `exporter_docx.py` - Export Markdown → DOCX avec formatage notarial
- Script `exporter_pdf.py` - Export Markdown → PDF
- Script `valider_acte.py` - Validation données vs schéma JSON
- Script `extraire_bookmarks_contenu.py` - Analyse variables DOCX original

#### Templates
- `vente_lots_copropriete.md` - 361 bookmarks (squelette)
- `promesse_vente_lots_copropriete.md` - 298 bookmarks (squelette)
- `reglement_copropriete_edd.md` - 116 bookmarks (complet ✅)
- `modificatif_edd.md` - 60 bookmarks (complet ✅)

#### Schémas
- `variables_vente.json`
- `variables_promesse_vente.json`
- `variables_reglement_copropriete.json`
- `variables_modificatif_edd.json`
- `questions_notaire.json` - 100+ questions pour vente
- `sections_catalogue.json`
- `clauses_catalogue.json` - 45 clauses initiales
- `annexes_catalogue.json` - 28 types

#### Directives
- `CLAUDE.md` - Architecture et principes
- `directives/creer_acte.md`
- `directives/creer_promesse_vente.md`
- `directives/creer_reglement_copropriete.md`
- `directives/creer_modificatif_edd.md`
- `directives/modifier_acte.md`
- `directives/collecte_informations.md`
- `directives/formatage_docx.md`
- `directives/pipeline_generation.md`
- `directives/apprentissage_continu.md`

#### Fonctionnalités Clés
- Génération actes DOCX 100% fidèles aux trames originales
- Zones grisées pour variables (marqueurs `<<<VAR_START>>>` / `<<<VAR_END>>>`)
- Filtres Jinja2: `nombre_en_lettres`, `montant_en_lettres`, `format_date`, `annee_en_lettres`
- Formatage notarial exact: Times New Roman 11pt, marges 60mm/15mm/25mm/25mm
- Métadonnées JSON (historique, version, statut)
- Support multi-vendeurs, multi-acquéreurs
- Calculs automatiques (tantièmes, montants en lettres, dates)

---

## Format

### Types de Changements
- `Ajouté` pour les nouvelles fonctionnalités
- `Modifié` pour les changements de fonctionnalités existantes
- `Déprécié` pour les fonctionnalités bientôt supprimées
- `Supprimé` pour les fonctionnalités supprimées
- `Corrigé` pour les corrections de bugs
- `Sécurité` pour les correctifs de vulnérabilités

---

**Maintenu par**: Claude Sonnet 4.5 (NotaireAI Agent)
