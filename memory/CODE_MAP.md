# Code Map - Notomai

> Cartographie exhaustive du code. Mis a jour a chaque session.
> BUT : ne jamais sous-estimer la taille d'un fichier ou rater des endpoints.
> REGLE : avant d'affirmer qu'un truc n'existe pas, consulter cette carte.

**Derniere mise a jour : 2026-02-20**

---

## Stack technique

### Backend
- **Runtime** : Python 3.10-3.13 (3.14 incompatible — httpcore)
- **Framework** : FastAPI >= 0.104 + Uvicorn + SSE-Starlette
- **Deploy** : Modal (Docker, volumes, CRON) — migration GCP Cloud Run prevue
- **ORM/DB** : supabase-py >= 2.3, httpx >= 0.27
- **Docs** : Jinja2 >= 3.1, python-docx >= 1.1, markdown >= 3.5
- **Securite** : cryptography >= 46.0
- **Validation** : jsonschema >= 4.20, pydantic >= 2.5
- **Tests** : pytest >= 7.4, pytest-asyncio

### Frontend
- **Framework** : Next.js 14.2.35 (App Router)
- **UI** : React 18.3 + TailwindCSS 3.4 + Lucide React
- **State** : Zustand 5.0.11 — `workflowStore` (persist) + `uiStore` (sidebar/toasts/palette/aiPanel)
- **Auth/DB** : @supabase/supabase-js 2.95.3
- **Markdown** : react-markdown 9.0
- **TypeScript** : 5.x strict mode
- **Tests** : Vitest 4.0 + Testing Library + jsdom (53 tests)
- **Layout** : `app/app/layout.tsx` partage (AppSidebar + AppHeader + AISidePanel + Toast + CommandPalette)
- **Routes** : `/app` (dashboard), `/app/chat` (SSE), `/app/dossiers`, `/app/documents`, `/app/clients`, `/app/workflow`

### Infrastructure
- **DB** : Supabase (wcklvjckzktijtgakdrk) — Frankfurt EU, 17 tables
- **Auth** : API keys 3 niveaux (read/write/delete) + Supabase Auth
- **CI/CD** : GitHub Actions (deploy.yml + test.yml)
- **Monitoring** : AUCUN (Sentry prevu)

### Patterns cles
- **API calls frontend** : toujours via `frontend/lib/api/`, jamais fetch() direct
- **Config** : `frontend/lib/config.ts` centralise API_URL, API_KEY, timeouts
- **SSE** : EventSource ne supporte pas les headers → API key en query param
- **Zustand persist** : `workflowStore` sauvegarde dans localStorage (cle `notomai-workflow`, version 1), hydratation async via `onFinishHydration`
- **Imports backend** : conditionnels DANS les endpoints (pas top-level, evite crash Modal)
- **Templates** : Jinja2 avec guards `{% if var %}`, sections via `{% include %}` (vente only)
- **DOCX** : formatage hardcode dans `exporter_docx.py` — NE JAMAIS MODIFIER

---

## Stats globales

| Categorie | Quantite | LOC approx |
|-----------|----------|------------|
| Endpoints API (api/main.py) | 40 (+8 routers) | 2994 |
| Endpoints Agents (api/agents.py) | 4 | 973 |
| Chat router (chat_handler.py) | 4+ | 1242 |
| Composants React | 30 (+6 UX redesign, -2 supprimes) | ~4500 |
| Scripts Python (execution/) | 60+ | ~20000 |
| Templates Jinja2 | 9 + 60 sections | - |
| Schemas JSON | 17 | - |
| Tests backend | 257 | - |
| Tests frontend | 53 | Vitest + Testing Library |

---

## api/main.py — 2940 lignes, 40 endpoints

**ATTENTION : ce fichier est ENORME. Toujours grep avant d'affirmer quoi que ce soit.**

### Endpoints par categorie

| # | Route | Methode | Ligne | Fonction |
|---|-------|---------|-------|----------|
| **Agent** | | | | |
| 1 | `/agent/execute` | POST | 514 | execute_agent() |
| 2 | `/agent/execute-stream` | POST | 602 | execute_streaming() |
| 3 | `/agent/feedback` | POST | 684 | submit_feedback() |
| **Dossiers** | | | | |
| 4 | `/dossiers` | GET | 735 | list_dossiers() |
| 5 | `/dossiers/{id}` | GET | 789 | get_dossier() |
| 6 | `/dossiers` | POST | 833 | create_dossier() |
| 7 | `/dossiers/{id}` | PATCH | 886 | update_dossier() |
| 8 | `/dossiers/{id}` | DELETE | 932 | delete_dossier() |
| **Systeme** | | | | |
| 9 | `/health` | GET | 965 | health_check() |
| 10 | `/files/{filename}` | GET | 991 | download_file() |
| 11 | `/download/{filename}` | GET | 1023 | download_file_secure() |
| 12 | `/stats` | GET | 1086 | get_stats() |
| 13 | `/me` | GET | 1134 | get_current_etude() |
| 13b | `/dashboard/stats` | GET | ~1148 | get_dashboard_stats() |
| **Clauses** | | | | |
| 14 | `/clauses/sections` | GET | 1149 | lister_sections_clauses() |
| 15 | `/clauses/profils` | GET | 1207 | lister_profils_clauses() |
| 16 | `/clauses/analyser` | POST | 1234 | analyser_donnees_clauses() |
| 17 | `/clauses/feedback` | POST | 1267 | soumettre_feedback_clause() |
| 18 | `/clauses/suggestions` | GET | 1330 | obtenir_suggestions_clauses() |
| **Promesses** | | | | |
| 19 | `/promesses/generer` | POST | 1418 | generer_promesse() |
| 20 | `/promesses/detecter-type` | POST | 1469 | detecter_type_promesse() |
| 21 | `/promesses/valider` | POST | 1506 | valider_donnees_promesse() |
| 22 | `/promesses/profils` | GET | 1538 | lister_profils_promesse() |
| 23 | `/promesses/types` | GET | 1567 | lister_types_promesse() |
| **Ventes** | | | | |
| 24 | `/ventes/generer` | POST | 1601 | generer_vente() |
| **Questions Q&R** | | | | |
| 25 | `/questions/promesse` | GET | 1702 | get_questions() |
| 25 | `/questions/promesse/answer` | POST | 1708 | submit_answers() |
| 26 | `/questions/promesse/progress/{id}` | GET | 1759 | get_progress() |
| 27 | `/questions/promesse/prefill` | POST | 1795 | prefill_questions() |
| **Workflow (L1891-2296)** | | | | |
| 28 | `/workflow/promesse/start` | POST | 1891 | workflow_start() |
| 29 | `/workflow/promesse/{id}/submit` | POST | 1975 | workflow_submit() |
| 30 | `/workflow/promesse/{id}/generate` | POST | 2046 | workflow_generate() |
| 31 | `/workflow/promesse/{id}/generate-stream` | GET | 2141 | workflow_generate_stream() |
| 32 | `/workflow/promesse/{id}/status` | GET | 2246 | workflow_status() |
| **Titres** | | | | |
| 33 | `/titres` | GET | 2303 | lister_titres() |
| 34 | `/titres/{id}` | GET | 2334 | get_titre() |
| 35 | `/titres/recherche/adresse` | GET | 2364 | rechercher_titre_adresse() |
| 36 | `/titres/recherche/proprietaire` | GET | 2391 | rechercher_titre_proprietaire() |
| 37 | `/titres/{id}/vers-promesse` | POST | 2418 | convertir_titre_en_promesse() |
| **Document** | | | | |
| 38 | `/document/{id}/sections` | GET | 2524 | get_document_sections() |
| 39 | `/feedback/paragraphe` | POST | 2589 | submit_paragraph_feedback() |

### Routers inclus (pas dans la table ci-dessus)
- L498 : `chat_router` (from execution.chat_handler) — `/chat/stream`, `/chat/conversations`, etc.
- L505 : `agents_router` (from api.agents) — `/agents`, `/agents/orchestrate`, etc.
- L513 : `cadastre_router` (from execution.api.api_cadastre) — `/cadastre/geocoder`, `/cadastre/parcelle`, etc.
- L521 : `validation_router` (from execution.api.api_validation) — `/validation/champ`, `/validation/schema`, etc.

### Middleware / Auth
- L200-350 : `verify_api_key()`, `require_write_permission`, `RateLimiter`
- L303 : API key acceptee en query param `?api_key=` (pour SSE/EventSource)

---

## api/agents.py — ~960 lignes, 4 endpoints

| Route | Methode | Ligne | Description |
|-------|---------|-------|-------------|
| `/agents` | GET | 525 | Liste agents disponibles |
| `/agents/{name}/execute` | POST | 602 | Executer un agent |
| `/agents/orchestrate` | POST | 677 | Generation parallele (3-5x) |
| `/agents/status` | GET | 945 | Status & monitoring |

---

## Frontend — Fichiers cles

### frontend/lib/ (cree le 18/02, enrichi AXE 2)

| Fichier | LOC | Role | Exporte |
|---------|-----|------|---------|
| `auth.ts` | 23 | Auth helper (AXE 2) | getUserEtudeId() |
| `format.ts` | 14 | Formatage dates (AXE 2) | formatDate() |
| `config.ts` | 19 | Config centralisee | API_URL, API_KEY, FETCH_TIMEOUT, WORKFLOW_SUPPORTED_TYPES |
| `constants.ts` | 63 | Labels UI | TYPE_ACTE_LABELS, CATEGORIE_LABELS, STEP_LABELS, SECTION_STATUS_COLORS, GENERATION_STEPS |
| `supabase.ts` | 18 | Client Supabase (Proxy lazy init) | supabase |
| `api/client.ts` | 188 | Client HTTP | ApiError, apiFetch<T>(), apiSSE<T>() |
| `api/index.ts` | ~358 | Pont frontend↔backend | startWorkflow(), submitAnswers(), validateField(), streamGeneration(), sendFeedback(), loadConversations(), loadConversation(), sendChatFeedback(), loadDocumentSections() |
| `api/promesse.ts` | 111 | API promesse | detecterType(), getQuestions(), validerPromesse() |

### frontend/stores/

| Fichier | LOC | Role |
|---------|-----|------|
| `workflowStore.ts` | 436 | Store Zustand — persist middleware (localStorage), VALIDATING step, importe `@/lib/api` + `@/lib/api/promesse` |
| `uiStore.ts` | 62 | Store Zustand — sidebar, mobileSidebar, commandPalette, **aiPanelOpen**, **aiPanelContext**, toasts |

### frontend/types/

| Fichier | LOC | Types cles |
|---------|-----|------------|
| `index.ts` | 115 | Message, ConversationSummary, DocumentSection, Dossier, Partie, ActeGenere, Client |
| `workflow.ts` | 126 | WorkflowStep, TypeActe, CategorieBien, SousType, Section, Question |

### frontend/components/workflow/ (20 composants)

| Fichier | LOC | Role |
|---------|-----|------|
| `WorkflowPage.tsx` | 341 | Orchestrateur principal (6 ecrans: IDLE, COLLECTING, VALIDATING, REVIEW, GENERATING, DONE + recovery UI + beforeunload + auto-start) |
| `WorkflowHeader.tsx` | ~80 | En-tete avec progression |
| `WorkflowSidebar.tsx` | ~100 | Navigation sections |
| `DynamicForm.tsx` | ~200 | Construction formulaire depuis schema |
| `DynamicQuestion.tsx` | ~150 | Rendu d'une question |
| `DocumentReview.tsx` | ~180 | Relecture document |
| `FeedbackPanel.tsx` | ~200 | Feedback notaire |
| `GenerationProgress.tsx` | ~150 | Progression generation |
| `fields/*.tsx` | 7 fichiers | TextField, NumberField, DateField, BooleanField, SelectField, ContactField, ArrayField |

### frontend/components/ (extraits AXE 2)

| Fichier | LOC | Role |
|---------|-----|------|
| `MessageBubble.tsx` | 213 | Bulle message chat (extrait de ChatArea) |
| `TypingIndicator.tsx` | 29 | Indicateur de saisie (extrait de ChatArea) |
| `DocumentCard.tsx` | 131 | Card document genere (AXE 7) |
| `ChatArea.tsx` | 148 | Zone de chat + lien Mode guide (AXE 7) + aria role=log |
| `ParagraphReview.tsx` | 252 | Relecture paragraphe par paragraphe |
| `AISidePanel.tsx` | 289 | **Panneau IA Copilot 380px** — SSE, context hints, toggle, responsive |
| `ClientCard.tsx` | ~80 | Card client (import format.ts) |
| `DossierCard.tsx` | ~90 | Card dossier (import format.ts) |

### frontend/app/ (pages)

| Route | Fichier | LOC |
|-------|---------|-----|
| `/` | `page.tsx` | 110 |
| `/login` | `login/page.tsx` | 191 |
| `/app` | `app/page.tsx` | ~410 |
| `/app/clients` | `app/clients/page.tsx` | ~180 |
| `/app/clients/[id]` | `app/clients/[id]/page.tsx` | ~40 |
| `/app/documents` | `app/documents/page.tsx` | 213 |
| `/app/workflow` | `app/workflow/page.tsx` | ~45 |
| `/app/dossiers` | `app/dossiers/page.tsx` | ~160 |
| `/app/dossiers/[id]` | `app/dossiers/[id]/page.tsx` | ~40 |
| API proxy | `api/chat/route.ts` | ~150 |

### frontend/__tests__/ (AXE 8 — cree le 18/02, enrichi 20/02)

| Fichier | Tests | Cible |
|---------|-------|-------|
| `format.test.ts` | 6 | formatDate() — null, undefined, vide, invalide, ISO, date-only |
| `auth.test.ts` | 4 | getUserEtudeId() — happy path, no user, no etude, erreur |
| `MessageBubble.test.tsx` | 11 | Rendu user/assistant, feedback, download, section, quick actions, welcome |
| `ChatArea.test.tsx` | 9 | Submit, empty submit, typing indicator, mode guide, streaming |
| `Toast.test.tsx` | 6 | Rendu success/error/multiple, close button, aria attributes |
| `CommandPalette.test.tsx` | 10 | Rendu open/closed, navigation/actions/conversations, filter, Enter nav, backdrop |
| `Dashboard.test.tsx` | 7 | Greeting, quick actions, stats API, recent dossiers, empty state, error |
| **Total** | **53** | Vitest 4.0 + Testing Library + jsdom |

---

## Execution — Fichiers principaux

| Fichier | LOC | Role |
|---------|-----|------|
| `agent_autonome.py` | 3142 | Agent intelligent NL + Q&R |
| `chat_handler.py` | 1237 | Chat SSE + contexte |
| `anthropic_agent.py` | 1101 | Wrapper Claude API (3-tier prompt caching, directive loading, ChatAnonymizer) |
| `core/assembler_acte.py` | 792 | Assemblage Jinja2 |
| `gestionnaires/gestionnaire_promesses.py` | 1695 | Orchestration promesses |
| `services/cadastre_service.py` | 673 | APIs cadastre gouv.fr |
| `core/exporter_docx.py` | ~600 | Export DOCX |
| `database/supabase_client.py` | 406 | Client Supabase Python |
| `test_fiabilite.py` | 335 | 257 tests |

### Sous-dossiers execution/

| Dossier | Nb fichiers | Role |
|---------|-------------|------|
| `core/` | 5 | Assemblage, export, validation |
| `gestionnaires/` | 6 | Orchestration metier |
| `utils/` | 9 | Utilitaires divers |
| `database/` | 4 | Acces Supabase |
| `analyse/` | 6 | Analyse documents |
| `generation/` | 4 | Generation donnees test |
| `extraction/` | 7 | ML/OCR extraction |
| `services/` | 2 | APIs externes (cadastre) |
| `api/` | 4 | Endpoints internes |
| `security/` | 8 | Chiffrement, RGPD |

---

## Scripts racine (workflow multi-devs)

| Fichier | LOC | Role |
|---------|-----|------|
| `notaire.py` | ~200 | CLI simplifie — point d'entree racine |
| `generate_commit_msg.py` | 406 | Commit message depuis JOURNAL.md ou git diff (auto) |
| `read_team_commits.py` | 279 | Lecture commits autres devs (anti-doublon) |
| `END_DAY.bat` | 194 | Fin de journee: stage + journal check + commit + push + PR (v3.1) |
| `START_DAY_AUGUSTIN.bat` | ~30 | Debut journee: fetch + team commits + pull |
| `START_DAY_PAYOSS.bat` | ~30 | idem pour Payoss |

---

## Deployment

| Fichier | LOC | Role |
|---------|-----|------|
| `deployment_modal/modal_app.py` | 397 | Config Modal (Docker, volumes, CRON, docs_original mount, github-credentials) |

---

## Endpoints via routers (non dans la table principale mais actifs)

| Endpoint | Router | Monte a |
|----------|--------|---------|
| `/cadastre/geocoder` | `api_cadastre.py` | L513 |
| `/cadastre/parcelle` | `api_cadastre.py` | L513 |
| `/cadastre/sections` | `api_cadastre.py` | L513 |
| `/cadastre/enrichir` | `api_cadastre.py` | L513 |
| `/cadastre/surface` | `api_cadastre.py` | L513 |
| `/validation/champ` | `api_validation.py` | L521 |
| `/validation/schema/{type}` | `api_validation.py` | L521 |
| `/validation/donnees` | `api_validation.py` | L521 |
