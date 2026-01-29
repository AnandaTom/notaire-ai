# Diagnostic Workflow Promesse de Vente

> Audit complet du 29/01/2026 - Version 1.5.0

## Verdict

Le moteur de generation fonctionne (template 94.3%, pipeline teste, DOCX conforme). Ce qui manque c'est la **plomberie entre les composants** : le frontend ne parle pas a l'API de generation, l'API ne sert pas les fichiers, et le collecteur a un bug de chemin.

```
Frontend Notaire       Collecte Q&R          Generation DOCX
+-----------------+    +-----------------+    +-----------------+
| Dashboard       | -X-| Questions       | -X-| Assemblage      |
| Questionnaires  |    | Agent NL        |    | Export DOCX     |
| Chiffrement E2E |    | Schemas 100+    |    | Workflow rapide  |
|                 |    |                 |    |                 |
| EXISTE          |    | BUG chemin      |    | FONCTIONNE      |
| PAS CONNECTE    |    | PAS CONNECTE    |    | TESTE E2E       |
+-----------------+    +-----------------+    +-----------------+
```

---

## Bloc 1 : Frontend Notaire

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Dashboard notaire | Fonctionne | `web/dashboard-notaire.html` |
| Questionnaire acquereur | Fonctionne | `web/fill.html` |
| Questionnaire vente appart | Fonctionne | `web/questionnaires/vente-appartement.html` |
| Questionnaire vente maison | Fonctionne | `web/questionnaires/vente-maison.html` |
| Questionnaire achat bien | Fonctionne | `web/questionnaires/achat-bien.html` |
| Chiffrement E2E client | Fonctionne | Supabase + AES-GCM |
| **Bouton "Generer promesse"** | **MANQUE** | A ajouter dans dashboard |
| **Telechargement DOCX** | **MANQUE** | Pas d'endpoint `/files/` |

Le dashboard collecte des donnees client chiffrees via Supabase mais n'a aucun bouton pour declencher la generation d'un acte.

---

## Bloc 2 : Collecte Questions-Reponses

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Schema questions promesse | 100+ questions, 21 sections | `schemas/questions_promesse_vente.json` |
| Schema variables promesse | Complet, multi-template | `schemas/variables_promesse_vente.json` |
| Catalogue unifie 4 types | Mapping complet | `schemas/promesse_catalogue_unifie.json` |
| **Script collecte interactive** | **BUG ligne 57** | `execution/utils/collecter_informations.py` |
| Agent NL (langage naturel) | Parse et genere | `execution/agent_autonome.py` |
| **Agent interactif Q&R** | **N'EXISTE PAS** | L'agent ne pose pas les questions une par une |

### Bug critique

`collecter_informations.py` ligne 57 pointe vers `questions_promesse.json` (n'existe pas) au lieu de `questions_promesse_vente.json`. Le script crashe immediatement pour les promesses.

### Agent autonome

L'agent fonctionne en mode "bulk" : il parse une phrase complete (`"Martin -> Dupont, appart 67m2, 450k"`), pas en mode interactif question par question. Il ne lit pas `questions_promesse_vente.json`.

---

## Bloc 3 : Generation DOCX

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Assemblage Jinja2 | Fonctionne | `execution/core/assembler_acte.py` |
| Export DOCX formate | Fonctionne | `execution/core/exporter_docx.py` |
| Workflow rapide | **Teste et fonctionnel** | `execution/workflow_rapide.py` |
| Gestionnaire promesses 4 types | Existe | `execution/gestionnaires/gestionnaire_promesses.py` |
| API endpoint `/promesses/generer` | Code | `api/main.py` ligne 1134 |
| **Endpoint telechargement fichier** | **MANQUE** | Pas de `GET /files/{name}` |

### Test e2e reussi

```bash
python execution/workflow_rapide.py --type promesse_vente \
    --donnees exemples/donnees_promesse_exemple.json \
    --output .tmp/test_e2e_promesse.docx
# -> DOCX genere en ~5 secondes
```

Note : les chemins dans `workflow_rapide.py` (lignes 116, 146, 171) ont ete corriges pour la structure v1.5.0 (`execution/core/` au lieu de `execution/`).

---

## Les 5 coupures dans la chaine

| # | Coupure | Impact | Qui |
|---|---------|--------|-----|
| 1 | Dashboard sans bouton "Generer" | Le notaire ne peut pas lancer la generation depuis le web | Augustin |
| 2 | API sans endpoint `/files/` | Impossible de telecharger le DOCX genere | Payoss |
| 3 | `collecter_informations.py` bug chemin | La collecte interactive CLI ne marche pas pour promesse | Tom (1 ligne) |
| 4 | Agent sans mode interactif Q&R | L'agent parse du texte brut au lieu de poser les questions une par une | Payoss |
| 5 | Questionnaires web non relies a la generation | Les formulaires HTML envoient vers Supabase mais ne declenchent pas la generation | Augustin + Payoss |

---

## Plan d'action par priorite

### P0 - Pour que ca fonctionne de bout en bout

1. **Endpoint `GET /files/{filename}`** dans `api/main.py`
   - `FileResponse` pour servir les DOCX generes
   - ~5 lignes de code

2. **Bouton "Generer Promesse"** dans `dashboard-notaire.html`
   - Appelle `POST /promesses/generer` avec les donnees decryptees
   - Puis download le DOCX via `/files/`

3. **Fix `collecter_informations.py` ligne 57**
   - `"questions_promesse.json"` -> `"questions_promesse_vente.json"`

### P1 - Pour une bonne experience notaire

4. **Mode interactif dans l'agent**
   - Pose les questions de `questions_promesse_vente.json` une par une
   - Au lieu de parser du texte brut

5. **Relier les questionnaires web a `/promesses/generer`**
   - `fill.html`, `vente-appartement.html` -> API generation
   - Au lieu de juste sauvegarder dans Supabase

6. **Validation metier avancee**
   - Conjoint doit signer si communaute
   - Diagnostics non expires
   - Coherence des dates

### P2 - Ameliorations

7. Template vente de 80.2% -> 85%+ (agent immobilier, plus-value)
8. Workflow automatique Promesse -> Vente (conservation donnees)
9. Template donation-partage

---

## API existante (api/main.py)

### Endpoints fonctionnels

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/agent/execute` | POST | Execute requete langage naturel |
| `/promesses/generer` | POST | Genere une promesse (detection auto type) |
| `/promesses/detecter-type` | POST | Detecte le type de promesse |
| `/promesses/valider` | POST | Valide les donnees avant generation |
| `/promesses/profils` | GET | Liste les profils predefinies |
| `/promesses/types` | GET | Liste les 4 types de promesse |
| `/titres/{id}/vers-promesse` | POST | Convertit titre -> promesse |
| `/dossiers` | CRUD | Gestion des dossiers clients |
| `/clauses/sections` | GET | Sections disponibles |
| `/clauses/analyser` | POST | Analyse et selection de clauses |
| `/health` | GET | Health check |

### Endpoints manquants

| Endpoint | Besoin |
|----------|--------|
| `GET /files/{filename}` | Telecharger les DOCX generes |
| `POST /validation/donnees` | Validation temps reel (existe dans `api_validation.py` mais pas monte) |

---

## Commandes CLI fonctionnelles

```bash
# Generation directe depuis JSON
python execution/workflow_rapide.py --type promesse_vente \
    --donnees data.json --output promesse.docx

# Via CLI unifie
python notaire.py generer --type promesse_vente --donnees data.json -o promesse.docx

# Systeme avance (4 types)
python notaire.py promesse-avancee generer --donnees data.json -o promesse.docx
python notaire.py promesse-avancee detecter --donnees data.json
python notaire.py promesse-avancee valider --donnees data.json

# Depuis titre de propriete
python notaire.py promesse --titre titre.pdf --beneficiaires acq.json --prix 250000

# Dashboard
python notaire.py dashboard
```

---

## Metriques actuelles

| Metrique | Valeur |
|----------|--------|
| Conformite promesse | **94.3%** (titres 97.2%, tableaux 86%, sections critiques 100%) |
| Conformite vente | 80.2% |
| Templates en production | 4/4 |
| Trames analysees (promesse) | 7 (Principale + A-F) |
| Sections promesse | 165 |
| Questions promesse | 100+ (21 sections) |
| Temps generation | ~5 secondes |
| Endpoints API | 30+ |
