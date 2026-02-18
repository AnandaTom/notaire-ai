# PLAN COMPLET - 10 AXES DE TRAVAIL NOTOMAI

> Analyse exhaustive du code par Claude Opus 4.6 — 18 fevrier 2026
> A distribuer a Tom et Augustin pour choix de leurs axes.

---

## VUE D'ENSEMBLE

| Axe | Titre | Effort | Urgence | Qui (CONFIRME) |
|-----|-------|--------|---------|----------------|
| **1** | **Connexion Frontend <-> Backend** | **3-5 jours** | **CRITIQUE** | **Paul** |
| 2 | Nettoyage Frontend | 2-3 jours | MOYEN | Tom (a confirmer) |
| 3 | Nettoyage Backend | 2-3 jours | MOYEN | (a attribuer) |
| **4** | **Securite Base de Donnees** | **1-2 jours** | **IMPORTANT** | **Augustin** ✅ |
| **5** | **Securite Code (Secrets)** | **1 jour** | **IMPORTANT** | **Augustin** ✅ |
| **6** | **Infrastructure & DevOps** | **2-3 jours** | **IMPORTANT** | **Augustin** ✅ |
| 7 | UX & Experience Notaire | 5-7 jours | MOYEN | Tom (a confirmer) |
| 8 | Tests & Qualite | 3-5 jours | IMPORTANT | Tom (a confirmer) |
| **9** | **RGPD & Conformite** | **3-5 jours** | **OBLIGATOIRE** | **Augustin** ✅ |
| 10 | Architecture & Documentation | 2-3 jours | FAIBLE | Paul |

---

## AXE 1 — CONNEXION FRONTEND <-> BACKEND (DEEP DIVE)

### Diagnostic exact

**Decouverte majeure** : les endpoints backend EXISTENT dans `api/main.py` (lignes 1884-2290). Le probleme est uniquement cote frontend : **2 fichiers client API n'ont jamais ete crees**.

### Fichiers a CREER

#### 1. `frontend/lib/api.ts` — Client API principal

Importe par :
- `frontend/stores/workflowStore.ts` (ligne 12) : `import * as api from '@/lib/api'`
- `frontend/components/workflow/FeedbackPanel.tsx` (ligne 5) : `import * as api from '@/lib/api'`

**5 fonctions attendues** (deduites du code appelant) :

```typescript
// === startWorkflow ===
// Appele par: workflowStore.ts ligne 99
// Backend: POST /workflow/promesse/start (api/main.py:1884)
//
// Frontend envoie:
//   { type_acte: TypeActe, etude_id?: string, source: 'workflow_frontend' }
//
// Backend attend (WorkflowStartRequest):
//   { categorie_bien: string, sous_type?: string, titre_id?: string, prefill?: Dict }
//
// ⚠️ MISMATCH: le store envoie "type_acte" mais le backend attend "categorie_bien"
//    → Il faut mapper type_acte vers categorie_bien dans api.ts
//
// Backend retourne:
//   { workflow_id, categorie_bien, sous_type, status, sections[],
//     current_section, questions[], progress, viager_questions_active }
//
// Le store attend:
//   { workflow_id, dossier_id, detection, sections[{id, titre, description, questions}] }
//
// ⚠️ MISMATCH: le store attend "dossier_id" et "detection" mais le backend ne les retourne pas
//    → Il faut adapter le store OU enrichir la reponse backend
export async function startWorkflow(request: {
  type_acte: string;
  etude_id?: string;
  source?: string;
}): Promise<StartWorkflowResponse>

// === submitAnswers ===
// Appele par: workflowStore.ts ligne 161
// Backend: POST /workflow/promesse/{workflow_id}/submit (api/main.py:1968)
//
// Frontend envoie: (workflowId, sectionId, donnees)
// Backend attend (WorkflowSubmitRequest): { answers: Dict }
//
// ⚠️ Le store passe sectionId mais le backend ne l'attend pas
//    → Ignorer sectionId ou l'ajouter au backend
//
// Backend retourne:
//   { status, next_section, questions, progress, validation }
//
// Le store attend:
//   { progression: { sections_completes, pourcentage },
//     validation: { messages: [{niveau, message}] } }
export async function submitAnswers(
  workflowId: string,
  sectionId: string,
  donnees: Record<string, unknown>
): Promise<SubmitAnswersResponse>

// === validateField ===
// Appele par: workflowStore.ts ligne 194
// Backend: AUCUN endpoint exact
//
// Le store envoie: { type_acte, chemin, valeur }
// Backend possibles:
//   POST /promesses/valider (api/main.py:1499) — valide donnees completes
//   Pas d'endpoint pour validation champ par champ
//
// ⚠️ ENDPOINT MANQUANT: il faut soit creer POST /workflow/validate-field
//    soit faire la validation cote frontend uniquement
export async function validateField(request: {
  type_acte: string;
  chemin: string;
  valeur: unknown;
}): Promise<ValidateFieldResponse>

// === streamGeneration ===
// Appele par: workflowStore.ts ligne 217
// Backend: GET /workflow/promesse/{workflow_id}/generate-stream (api/main.py:2134)
//
// C'est un EventSource (SSE), pas un fetch classique
// Retourne des events: { etape, statut, detail, fichier?, conformite? }
export function streamGeneration(
  workflowId: string,
  onEvent: (event: GenerationEvent) => void,
  onError: (error: string) => void
): () => void  // retourne cleanup function

// === sendFeedback ===
// Appele par: FeedbackPanel.tsx ligne 23
// Backend: POST /agent/feedback (api/main.py:677) — format different
//         POST /chat/feedback — format different
//         POST /feedback/paragraphe (api/main.py:2582) — format different
//
// Frontend envoie: { workflow_id?, section, type, contenu }
// Aucun backend ne matche exactement
//
// ⚠️ ENDPOINT MANQUANT ou ADAPTATION NECESSAIRE
//    → Creer POST /workflow/feedback ou adapter FeedbackPanel
export async function sendFeedback(request: {
  workflow_id?: string;
  section: string;
  type: 'erreur' | 'suggestion' | 'question';
  contenu: string;
}): Promise<void>
```

#### 2. `frontend/lib/api/promesse.ts` — Client API promesse

Importe par :
- `frontend/hooks/useViagerDetection.ts` (ligne 7) : `import { detecterType, getQuestions, validerPromesse, DetectionResult, Section } from '@/lib/api/promesse'`
- `frontend/components/ViagerBadge.tsx` (ligne 6) : `import { DetectionResult } from '@/lib/api/promesse'`

**3 fonctions + 2 types a exporter** :

```typescript
// === DetectionResult ===
// Utilise par: ViagerBadge.tsx (ligne 14), useViagerDetection.ts (ligne 20)
export interface DetectionResult {
  categorie_bien: string;
  type_promesse: string;
  sous_type?: string;       // 'viager' | 'creation' | 'lotissement' | etc.
  confiance: number;        // 0-100
  marqueurs_detectes: string[];
  avertissement?: string;
}

// === Section === (re-export ou alias du type workflow)
export interface Section {
  id: string;
  titre: string;
  questions: any[];
}

// === detecterType ===
// Appele par: useViagerDetection.ts ligne 48
// Backend: POST /promesses/detecter-type (api/main.py:1462)
export async function detecterType(donnees: Record<string, any>): Promise<DetectionResult>

// === getQuestions ===
// Appele par: useViagerDetection.ts ligne 69
// Backend: GET /questions/promesse?categorie=X&sous_type=Y&section=Z (api/main.py:1641)
export async function getQuestions(
  categorie: string,
  sousType: string,
  section: string
): Promise<{ sections: Section[] }>

// === validerPromesse ===
// Appele par: useViagerDetection.ts ligne 86
// Backend: POST /promesses/valider (api/main.py:1499)
export async function validerPromesse(donnees: Record<string, any>): Promise<any>
```

### Fichiers a MODIFIER

#### 3. Centraliser l'URL API — `frontend/lib/config.ts` (a creer)

L'URL Modal est hardcodee dans **6 fichiers** :
- `frontend/app/app/page.tsx` (ligne 11)
- `frontend/components/ChatArea.tsx` (ligne 9)
- `frontend/components/workflow/WorkflowPage.tsx` (ligne 13)
- `frontend/components/workflow/GenerationProgress.tsx` (ligne 8)
- `frontend/app/app/dossiers/page.tsx` (ligne 11)
- `frontend/app/api/chat/route.ts` (ligne 11)

De plus, l'ancienne app legacy utilise une URL DIFFERENTE :
- `frontend/assets/js/app.js` (ligne 14) : `paulannes-pro--notaire-ai-fastapi-app.modal.run`
- Fichiers Next.js : `notomai--notaire-ai-fastapi-app.modal.run`

```typescript
// frontend/lib/config.ts
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notomai--notaire-ai-fastapi-app.modal.run'
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ''
```

Puis remplacer dans les 6 fichiers : `const API_URL = ...` → `import { API_URL } from '@/lib/config'`

#### 4. Adapter le store — `frontend/stores/workflowStore.ts`

Mismatches identifies entre ce que le store envoie et ce que le backend attend :

| Store (frontend) | Backend (api/main.py) | Action |
|---|---|---|
| `type_acte: TypeActe` | `categorie_bien: string` | Mapper dans api.ts |
| Attend `dossier_id` en retour | Backend ne retourne pas `dossier_id` | Utiliser `workflow_id` comme dossier_id |
| Attend `detection` en retour | Backend retourne `categorie_bien + sous_type` | Construire Detection dans api.ts |
| Envoie `sectionId` a submitAnswers | Backend n'attend pas sectionId | Ignorer dans api.ts |

#### 5. Endpoint manquant : validation champ par champ

Le store appelle `api.validateField({type_acte, chemin, valeur})` mais aucun endpoint backend ne fait de la validation champ par champ.

**Options** :
- A) Creer `POST /workflow/validate-field` dans api/main.py (5-10 lignes)
- B) Faire la validation cote frontend dans api.ts (sans appel reseau)
- **Recommandation** : Option B pour l'instant (validation locale), option A en sprint 2

#### 6. Endpoint manquant : feedback workflow

FeedbackPanel envoie `{workflow_id, section, type, contenu}` mais aucun endpoint ne matche.

**Options** :
- A) Creer `POST /workflow/feedback` (10 lignes)
- B) Adapter FeedbackPanel pour utiliser `POST /agent/feedback`
- **Recommandation** : Option A, creer un endpoint simple qui insert dans `feedbacks_promesse`

### Ordre d'execution AXE 1

| # | Tache | Fichier | Effort |
|---|-------|---------|--------|
| 1 | Creer `frontend/lib/config.ts` (URL centralisee) | Nouveau | 15 min |
| 2 | Remplacer les 6 URL hardcodees par import config | 6 fichiers | 30 min |
| 3 | Creer `frontend/lib/api/promesse.ts` (types + 3 fonctions) | Nouveau | 1h |
| 4 | Creer `frontend/lib/api.ts` (5 fonctions) | Nouveau | 2-3h |
| 5 | Adapter le mapping dans api.ts (type_acte → categorie_bien, etc.) | api.ts | 30 min |
| 6 | Creer `POST /workflow/feedback` dans backend | api/main.py | 30 min |
| 7 | Validation champ par champ cote frontend | api.ts | 30 min |
| 8 | Tester le workflow complet E2E | — | 1-2h |
| **Total** | | | **~5-8h** |

### Schema de connexion final

```
                          FRONTEND                                    BACKEND

WorkflowPage.tsx ──→ workflowStore.ts ──→ lib/api.ts ─── fetch ──→ api/main.py
    |                     |                   |                        |
    |  TYPE_SELECT        | startWorkflow()   | POST /workflow/        | WorkflowStartRequest
    |  COLLECTING         | submitAnswers()   |   promesse/start       | WorkflowSubmitRequest
    |  REVIEW             | validateField()   | POST /workflow/        | (local validation)
    |  GENERATING         | streamGeneration()│   promesse/{id}/submit │
    |  DONE               |                   | GET /workflow/         |
    |                     |                   |   promesse/{id}/       |
FeedbackPanel.tsx ────────────────────→ api.ts |   generate-stream     |
    |                                    |     | POST /workflow/        |
    | sendFeedback()                     |     |   feedback (A CREER)   |
                                               |                        |
ViagerBadge.tsx ──→ useViagerDetection ──→ lib/api/promesse.ts ──→     |
    |                     |                   |                        |
    | DetectionResult     | detecterType()    | POST /promesses/       |
    |                     | getQuestions()    |   detecter-type         |
    |                     | validerPromesse() | GET /questions/promesse |
    |                     |                   | POST /promesses/valider |
```

---

## AXE 2 — NETTOYAGE FRONTEND

### Fichiers concernes et taches

| # | Tache | Fichier(s) | Detail |
|---|-------|-----------|--------|
| 1 | Archiver composant mort | `components/ChatWithViager.tsx` (302 lignes) | Importe nulle part en production — seulement dans README_VIAGER.md comme exemple. Deplacer vers `frontend/examples/` |
| 2 | Verifier DynamicQuestion.tsx import | `components/workflow/DynamicQuestion.tsx` | Aucun grep ne l'importe directement — verifier s'il est utilise via DynamicForm.tsx |
| 3 | Supprimer fichiers legacy | `frontend/assets/js/app.js`, `frontend/public/assets/js/app.js`, `frontend/index.html`, `frontend/pages/login.html` | Ancienne app pre-Next.js avec URL differente (`paulannes-pro--...`). Confirmer qu'elle n'est plus utilisee |
| 4 | Extraire MessageBubble | `components/ChatArea.tsx` (374 lignes) | `MessageBubble()` (lignes ~145-352) est defini inline dans ChatArea — extraire en composant separe pour lisibilite |
| 5 | console.log en production | Aucun trouve en `.tsx/.ts` | CLEAN — rien a faire (un point positif !) |
| 6 | Imports inutilises | Aucun trouve sauf les 2 fichiers manquants (api.ts) | Sera resolu par AXE 1 |
| 7 | Code duplique | Pas de duplication significative trouvee | Architecture proprement separee (composants, store, types) |
| 8 | Types dupliques | `types/index.ts` (97 lignes) + `types/workflow.ts` (127 lignes) | Pas de doublon — separation propre (domain vs workflow) |
| 9 | useEffect | 2 useEffect trouves (ChatArea.tsx:36, GenerationProgress.tsx:17) | Les 2 sont corrects avec bonnes dependances |
| 10 | Verifier re-renders | `WorkflowPage.tsx` (227 lignes) | Pas de useMemo/useCallback mais Zustand selectors sont deja optimises — impact minimal |

**Verdict** : Le frontend est plus propre qu'attendu. Pas de gros nettoyage necessaire sauf le composant mort ChatWithViager et les fichiers legacy.

---

## AXE 3 — NETTOYAGE BACKEND

### Doublons analyses

| Doublon suspecte | Verdict | Detail |
|---|---|---|
| `exporter_acte.py` vs `core/exporter_docx.py` | PAS UN DOUBLON | exporter_acte.py est un orchestrateur (appelle exporter_docx + exporter_pdf) |
| `generer_acte_complet.py` vs `gestionnaires/orchestrateur.py` | PAS UN DOUBLON | generer_acte_complet = pipeline full, orchestrateur = workflow management |
| `extraire_variables.py` vs `extraction/extracteur_v2.py` | PAS UN DOUBLON | Directions opposees — extraire_variables = template→vars, extracteur = document→data |
| `preparer_donnees_test.py` vs `generation/generer_donnees_test.py` | PAS UN DOUBLON | preparer = enrichir existant, generer = creer synthetique avec Faker |

### Taches reelles

| # | Tache | Fichier(s) | Detail |
|---|-------|-----------|--------|
| 1 | Auditer script obsolete | `execution/generer_depuis_template_docx.py` | Ancienne methode (avant Jinja2). Probablement obsolete — verifier s'il est importe quelque part |
| 2 | Clarifier scripts statuts | `execution/generer_statuts.py`, `execution/mettre_a_jour_statuts.py`, `execution/copier_statuts_generique.py` | 3 scripts lies aux statuts sans relation claire — documenter ou fusionner |
| 3 | Auditer overlap agents | `execution/agent_autonome.py`, `execution/agent_llm.py`, `execution/anthropic_agent.py`, `execution/anthropic_tools.py` | 4 fichiers LLM/agent — verifier qui appelle quoi et s'il y a du dead code |
| 4 | Migrer schema SQL | `execution/database/historique.py` (lignes 746-798) | Schema SQL defini en string Python mais jamais applique en migration Supabase. Soit le migrer, soit le supprimer |
| 5 | Chat handler dead code | `execution/chat_handler.py` (1072+ lignes) | `SimpleParseur` (fallback) utilise uniquement si ParseurDemandeNL echoue — acceptable mais verifier les fonctions vraiment mortes |
| 6 | Enrichir __init__.py | `execution/*/\__init__.py` (10 fichiers) | Tous vides — acceptable pour Python 3.3+ mais ajouter des re-exports pour les modules publics ameliorerait la DX |

---

## AXE 4 — SECURITE BASE DE DONNEES

### Taches exactes

| # | Tache | Gravite | Effort | Detail |
|---|-------|---------|--------|--------|
| 1 | Corriger 13 vues SECURITY_DEFINER → SECURITY_INVOKER | CRITIQUE | 1h | `v_cost_alerts`, `v_kpis_etude`, `v_dossiers_dashboard`, `v_daily_costs`, `v_agent_costs`, `v_model_distribution`, `v_tier1_savings`, `v_recent_activity`, `v_activite_recente`, `v_statistiques_etude`, `v_stats_promesses_etude`, `v_rappels_proches`, `v_clients_etude`, `v_documents_dossier`, `v_conversions_promesse_vente`, `v_performance_agents`. Migration : `ALTER VIEW ... SET (security_invoker = true)` |
| 2 | Activer RLS sur api_costs_tracking | CRITIQUE | 30 min | Table creee dans `20260211_cost_optimization.sql` sans RLS. Ajouter : `ALTER TABLE api_costs_tracking ENABLE ROW LEVEL SECURITY; CREATE POLICY ...` |
| 3 | Fixer 8 fonctions search_path mutable | IMPORTANT | 1h | Fonctions concernees : `get_max_tokens()`, `insert_cost_tracking()`, `sync_context_columns()`, `update_conversation_timestamp()`, `update_qr_sessions_updated_at()` + 3 autres. Ajouter `SET search_path = public` dans chaque fonction |
| 4 | Activer protection mots de passe compromis | IMPORTANT | 5 min | Dashboard Supabase → Authentication → Providers → Enable Leaked Password Protection |

---

## AXE 5 — SECURITE CODE (SECRETS)

### Taches exactes

| # | Tache | Gravite | Fichier | Detail |
|---|-------|---------|---------|--------|
| 1 | Supprimer UUIDs hardcodes | CRITIQUE | `execution/chat_handler.py` lignes 755-756 | `REAL_USER_ID = "3138517c-..."` et `REAL_ETUDE_ID = "a2cb1402-..."`. Extraire du JWT Authorization header. Le TODO est la depuis des semaines |
| 2 | Supprimer anon key hardcodee | CRITIQUE | `frontend/lib/supabase.ts` ligne 6 | Supprimer le fallback `\|\| 'eyJhbGci...'`. Si env var manquante, throw Error au lieu de fallback |
| 3 | Crash si cle manquante | IMPORTANT | `execution/security/signed_urls.py` lignes 28-34 | Cle dev `"dev_only_key_change_in_production_immediately"` — remplacer par `raise ValueError()` en prod |
| 4 | Stripper metadata DOCX | IMPORTANT | `execution/core/exporter_docx.py` | Ajouter apres creation du document : `doc.core_properties.author = "Notomai"`, `doc.core_properties.last_modified_by = ""`, clear timestamps |
| 5 | Scan complet secrets | MOYEN | 87 scripts Python + composants React | Aucun autre secret trouve dans le scan — mais installer un pre-commit hook (detect-secrets ou gitleaks) pour eviter les regressions |

---

## AXE 6 — INFRASTRUCTURE & DEVOPS

### Taches exactes

| # | Tache | Gravite | Fichier | Detail |
|---|-------|---------|---------|--------|
| 1 | Fix weekly_catalog_sync | CRITIQUE | `deployment_modal/modal_app.py` ~ligne 251 | Ecrit sur filesystem read-only de Modal. Migrer vers Supabase Storage ou Volume `/outputs` |
| 2 | Fix deploy.yml | CRITIQUE | `.github/workflows/deploy.yml` | 2 erreurs : ecoute `main` au lieu de `master`, chemin `modal deploy modal_app.py` au lieu de `deployment_modal/modal_app.py` |
| 3 | Fix test.yml `\|\| true` | IMPORTANT | `.github/workflows/test.yml` ligne 29 | `pytest ... \|\| true` ignore les echecs de test — supprimer le `\|\| true` |
| 4 | Evaluer min_containers=0 | MOYEN | `deployment_modal/modal_app.py` ligne ~70 | `min_containers=1` coute ~$30-50/mois. Cold start Modal est <100ms — passer a 0 en dev |
| 5 | Ajouter monitoring | IMPORTANT | Nouveau | Installer Sentry (SDK Python + Next.js). ~1-2h de setup |
| 6 | Verifier self_anneal.py | FAIBLE | `execution/self_anneal.py` | Le fichier EXISTE (contrairement a l'audit). Verifier qu'il est correctement importe dans modal_app.py |
| 7 | Health check endpoint | EXISTE | `api/main.py` ligne 958 | `/health` existe et verifie Supabase — pas d'action necessaire |

---

## AXE 7 — UX & EXPERIENCE NOTAIRE

### Taches exactes

| # | Tache | Gravite | Detail |
|---|-------|---------|--------|
| 1 | Creer page "Mes documents" | IMPORTANT | Route `frontend/app/app/documents/page.tsx`. Query Supabase `promesses_generees` + `actes`. Afficher liste avec statut, date, type, bouton download |
| 2 | Creer onboarding | IMPORTANT | Composant modal au premier login. 3-4 etapes : bienvenue, choisir type d'acte, explication workflow, lancer |
| 3 | Lier chat et workflow | MOYEN | Ajouter bouton "Passer au formulaire guide" dans la page chat (page.tsx). Ajouter bouton "Passer au chat libre" dans WorkflowPage |
| 4 | Erreurs user-friendly | MOYEN | FeedbackPanel.tsx ligne 33 : `catch { // Silently fail }` — ajouter message d'erreur visible. workflowStore : traduire les erreurs backend en francais comprehensible |
| 5 | Skeleton screens | FAIBLE | Ajouter skeleton UI pendant le chargement initial du workflow (sections, questions). Actuellement : seulement des spinners Loader2 |
| 6 | Dashboard notaire | MOYEN | Route `frontend/app/app/dashboard/page.tsx`. KPIs : actes generes ce mois, en cours, rappels proches |
| 7 | Champs de formulaire | OK | Les 7 types existent dans `workflow/fields/` — coherence confirmee |

---

## AXE 8 — TESTS & QUALITE

### Taches exactes

| # | Tache | Gravite | Detail |
|---|-------|---------|--------|
| 1 | Setup Vitest pour frontend | IMPORTANT | `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom`. Creer `vitest.config.ts` |
| 2 | Tests prioritaires frontend | IMPORTANT | Par ordre : (a) workflowStore.ts — toutes les transitions d'etat, (b) DynamicForm.tsx — rendu des questions, (c) FeedbackPanel.tsx — soumission |
| 3 | Supprimer `\|\| true` dans CI | IMPORTANT | `.github/workflows/test.yml` ligne 29 : les tests passent meme en echec |
| 4 | Tests endpoint API | MOYEN | Verifier que `tests/test_chat_handler.py` couvre les endpoints. Ajouter tests pour `/workflow/*` endpoints (11 routes non testees) |
| 5 | Coverage config | MOYEN | Ajouter `--cov` dans pytest, `coverage` dans vitest.config |
| 6 | Setup Playwright E2E | FAIBLE (sprint 4+) | Test complet : login → choisir type → remplir questions → generer → download |

**Tests backend existants (13 fichiers) :**
```
tests/conftest.py
tests/test_assembler_acte.py
tests/test_cadastre.py
tests/test_chat_handler.py
tests/test_collecter_informations.py
tests/test_exporter_docx.py
tests/test_integration.py
tests/test_security.py
tests/test_valider_acte.py
tests/test_tier1_optimizations.py
tests/test_gestionnaire_promesses.py
tests/test_logger.py
tests/test_orchestrateur.py
```

---

## AXE 9 — RGPD & CONFORMITE

### Taches exactes

| # | Tache | Gravite | Detail |
|---|-------|---------|--------|
| 1 | Signer DPA Supabase | CRITIQUE | Dashboard Supabase → Settings → Legal → DPA. Document standard fourni par Supabase |
| 2 | Registre des traitements | OBLIGATOIRE | Document interne listant : finalites, categories de donnees, destinataires, durees de conservation, base legale. Format : Google Sheet ou Notion |
| 3 | Politique de confidentialite | OBLIGATOIRE | Page frontend `frontend/app/privacy/page.tsx`. Lister : donnees collectees, finalites, droits, contact DPO |
| 4 | Procedure notification breach | OBLIGATOIRE | Document interne : qui contacter, delai 72h CNIL, template de notification |
| 5 | Liste sous-traitants | OBLIGATOIRE | Modal (infra), Supabase (BDD), Anthropic (LLM). Pour chaque : localisation, DPA, finalite |
| 6 | Workflow effacement | IMPORTANT | Table `rgpd_requests` existe dans le schema Supabase. Implementer : endpoint API pour demande d'effacement, cascade delete sur toutes les tables liees, confirmation notaire |
| 7 | Verifier chiffrement PII | IMPORTANT | `encryption_service.py` chiffre 10 champs (nom, prenom, email, etc.). Verifier que TOUS les inserts Supabase passent par ce service — audit a faire sur `supabase_client.py` et `agent_database.py` |
| 8 | Tables rgpd_requests et audit_logs | IMPORTANT | Mentionnees dans la doc mais PAS TROUVEES dans les migrations Supabase. Soit elles existent via autre moyen, soit a creer |

---

## AXE 10 — ARCHITECTURE & DOCUMENTATION

### Taches exactes

| # | Tache | Gravite | Detail |
|---|-------|---------|--------|
| 1 | Scinder CLAUDE.md | MOYEN | 1200+ lignes melangeant instructions, changelog, versioning. Separer en : CLAUDE.md (instructions agent, <200 lignes), CHANGELOG.md (historique), ARCHITECTURE.md (schemas) |
| 2 | Auditer docs/ (33 fichiers) | FAIBLE | Potentiels obsoletes : `DIAGNOSTIC_WORKFLOW.md`, `ETAT_SPRINT_JOUR1.md`, `NEXT_STEPS.md`. A archiver ou supprimer |
| 3 | web/demo-workflow.html | FAIBLE | Demo standalone 1038 lignes. Probablement obsolete depuis le frontend Next.js. Confirmer et archiver |
| 4 | Evaluer docxtpl | PLANIFIE | Jinja2 directement dans DOCX au lieu du pipeline Markdown→DOCX. Avantage : fidelite 100% garantie. POC sur modificatif_edd (le plus simple) |
| 5 | Modulariser templates promesse | PLANIFIE | Les 4 templates promesse n'utilisent PAS `{% include %}` (contrairement a la doc CLAUDE.md). Les sections existent (39 fichiers dans `templates/sections/`) mais ne sont jamais incluses. Decider : les inclure ou garder inline |
| 6 | userId dans localStorage | CONFIRME | `frontend/app/app/page.tsx` ligne 14-20 : `localStorage.getItem('notaire_user_id')` avec `crypto.randomUUID()` si absent. Migrer vers Supabase Auth user.id |
| 7 | Coherence schemas/ | MOYEN | 17 fichiers JSON. Verifier que les variables dans les schemas matchent les variables dans les templates Jinja2 |

---

## PRIORITES RECOMMANDEES

### Sprint immediat (cette semaine)
1. **AXE 1** — Connexion Frontend <-> Backend (Paul)
2. **AXE 5 taches 1-3** — Supprimer secrets hardcodes (rapide, critique)
3. **AXE 4 taches 1-2** — Fixer vues SECURITY_DEFINER + RLS (Augustin)

### Sprint suivant (semaine prochaine)
4. **AXE 6 taches 1-3** — Fix deploy.yml + catalog_sync + CI
5. **AXE 8 tache 1-3** — Setup Vitest + premiers tests frontend (Tom)
6. **AXE 9 taches 1-5** — RGPD obligatoire (Paul)

### Sprint 3
7. **AXE 7 taches 1-3** — Mes documents + onboarding + lien chat/workflow (Tom)
8. **AXE 3** — Nettoyage backend (Augustin)
9. **AXE 2** — Nettoyage frontend (Tom)

### Backlog
10. **AXE 10** — Architecture + documentation
