# Journal de Bord - Notomai

> Ce fichier est tenu par Claude. Chaque session est loguee avec : date, ce qui a ete fait,
> fichiers modifies, decouvertes, erreurs commises, lecons tirees.
> BUT : ne jamais perdre le fil d'un jour a l'autre.

---

## 2026-02-19 (nuit, suite) — Paul (Payoss)

### Contexte
- Audit post-branchement des 5 phases. Paul s'occupe du chatbot ce soir.

### Audit /audit — Score 7.2/10 (↑ depuis 6.7)

| Dimension | Score | Tendance |
|-----------|-------|----------|
| Architecture | 6.5 | → |
| Optimisation | 6.0 | → |
| Securite | **8.5** | **↑** |
| Fiabilite | **8.0** | **↑** |
| Fluidite | 6.0 | ↑ |

### Decouvertes audit
1. **C-011 REGRESSION** — Le merge `c4be78d` ("keep both sides") a restaure 6 fichiers legacy supprimes dans `b4d4129`. Cles anon Supabase de retour dans `frontend/assets/`, `frontend/pages/`, `frontend/index.html`, `web/supabase-client.js`.
2. **65 index Supabase inutilises** (vs 68 precedemment — 3 ont ete utilises)
3. **api/main.py passe a 2994 lignes** (+54 depuis CODE_MAP)
4. **anthropic_agent.py passe a 1101 lignes** (+71 — anonymisation)
5. **workflowStore.ts passe a 436 lignes** (+118 — VALIDATING + persist)

### Tests verifies
- Python : 348 passed, 7 failed (pre-existants), 4 skipped — **0 regression**
- Frontend : `npm run build` — 11/11 pages OK
- Modules individuels : data_enrichment OK, ChatAnonymizer roundtrip OK, EncryptionService roundtrip OK

### Prochaine etape
- Paul travaille sur le chatbot ce soir

---

## 2026-02-19 (nuit) — Paul (Payoss)

### Contexte
- Audit complet : 50 fichiers backend + 19 elements frontend deconnectes identifies
- Plan d'attaque 5 phases pour brancher les composants critiques

### Ce qui a ete fait (5 phases)

| Phase | Action | Fichiers modifies |
|-------|--------|-------------------|
| 1 | Monte api_cadastre + api_validation routers | `api/main.py` L509-520 |
| 2 | Insere data_enrichment dans pipeline generation (POST + SSE) | `api/main.py` L2148, L2270 |
| 3a | Re-export promesse.ts dans api/index.ts | `frontend/lib/api/index.ts` L324 |
| 3b | VALIDATING step + validation semantique backend | `frontend/stores/workflowStore.ts` L168-196 |
| 3c | Filtrage condition_categorie sur questions | `frontend/components/workflow/DynamicQuestion.tsx` L18-23 |
| 3d | Auto-start via initialType URL param | `frontend/components/workflow/WorkflowPage.tsx` L100 |
| 3e | Ecran VALIDATING (spinner) | `frontend/components/workflow/WorkflowPage.tsx` L246 |
| 4 | ChatAnonymizer branche dans process_message + stream | `execution/anthropic_agent.py` L47, L800, L835, L940, L960, L993 |
| 5 | AgentClientAccess dans ToolExecutor (submit + generate) | `execution/anthropic_tools.py` L17, L247, L393, L489 |

### Impact
- PII anonymises avant envoi a Claude (RGPD)
- Documents enrichis (mapping parties, restructuration adresses, defaults)
- 8 nouveaux endpoints API actifs (/cadastre/*, /validation/*)
- Workflow frontend complete : auto-start + VALIDATING + filtrage categories
- PII chiffres au repos via pile securite

---

## 2026-02-19 — Tom (session 2)

### Contexte
- Audit /audit score 6.2/10 (5 dimensions). Tom prend dimensions 1 (architecture) et 2 (optimisation frontend).
- Objectif: renforcer la couche API frontend, corriger les erreurs silencieuses et les stale closures.

### Ce qui a ete fait

| Action | Fichier | Detail |
|--------|---------|--------|
| MODIFIE | `frontend/lib/api/index.ts` | +4 fonctions exportees : loadConversations(), loadConversation(), sendChatFeedback(), loadDocumentSections() — toutes via apiFetch() |
| MODIFIE | `frontend/app/app/page.tsx` | +toastError state + showToast() helper (auto-dismiss 5s, useRef pour eviter timer leak) |
| MODIFIE | `frontend/app/app/page.tsx` | loadConversation et loadConversations → useCallback (fix stale closure) |
| MODIFIE | `frontend/app/app/page.tsx` | 4 silent catch {} → showToast() avec message contextuel |
| MODIFIE | `frontend/app/app/page.tsx` | 4 appels fetch() directs → fonctions API du module @/lib/api |
| MODIFIE | `frontend/app/app/page.tsx` | sendFeedback : revert optimiste si echec backend |
| MODIFIE | `frontend/app/app/page.tsx` | SSE sendMessage : ajout header X-API-Key |

### Nouvelles interfaces (lib/api/index.ts)

```typescript
ConversationListResponse    // { conversations: ConversationSummary[] }
ConversationDetailResponse  // { messages: [...], context?: { progress_pct? } }
```

### Review (/review — 2 passes)

- 2 CRITICAL trouves et corriges
- 3 MODERATE trouves et corriges
- 2 MINOR trouves et corriges

### Build / Tests

- `next build` — 11/11 pages OK
- `vitest run` — 30/30 tests OK
- Backend 257 tests inchanges (0 fichiers Python modifies)

### Decouvertes

1. **C-010 FIXEE** — vitest.config.ts exclu dans tsconfig.json. Build passe a nouveau.
2. **Dimension 3 & 4** : prises par Payoss.
3. **Dimension 5** : prise par Augustin.

### Branches

- `tom/dev` — changements locaux, pas encore commites

---

## 2026-02-19 — Tom

### Contexte
- Mise en place du systeme de commits intelligents multi-devs
- Merge master pour recuperer le systeme memoire de Payoss
- Partage des agents reviewer/documenter pour toute l'equipe

### Ce qui a ete fait

| Action | Fichier | Detail |
|--------|---------|--------|
| CREE | `generate_commit_msg.py` | Genere commit msg depuis JOURNAL.md + auto-summary git diff |
| CREE | `read_team_commits.py` | Lecture commits autres devs (anti-doublon, filtre auto-commits) |
| MODIFIE | `END_DAY.bat` | v3.0→v3.1: journal check, locale-independent date, error handling |
| MODIFIE | `START_DAY_AUGUSTIN.bat` | v2.0: ajout step team commits |
| MODIFIE | `START_DAY_PAYOSS.bat` | v2.0: ajout step team commits |
| CREE | `.claude/agents/reviewer.md` | Copie depuis ~/.claude/ → repo (partage equipe) |
| CREE | `.claude/agents/documenter.md` | Copie depuis ~/.claude/ → repo (partage equipe) |
| MODIFIE | `.claude/skills/document/SKILL.md` | Format journal anti-conflit multi-devs |
| MODIFIE | `.claude/commands/audit.md` | +read_team_commits.py dans Phase 0 |
| MODIFIE | `memory/CONVENTIONS.md` | Conventions journal + commit end-of-day |
| MODIFIE | `CLAUDE.md` | Scripts BAT table, agent paths → repo-level |
| MODIFIE | `memory/CODE_MAP.md` | +scripts racine table |

### Decouvertes

1. **Agents reviewer/documenter etaient locaux** — dans `~/.claude/agents/` (machine Tom uniquement). Payoss et Augustin n'y avaient pas acces. Deplaces dans `.claude/agents/` (repo).
2. **`%date%` Windows est locale-dependent** — format different selon langue OS. Fix: PowerShell `Get-Date -Format yyyy-MM-dd`.
3. **`git push --force-with-lease` apres rebase silencieux** pouvait corrompre la branche remote. Fix: check ERRORLEVEL apres chaque etape.
4. **Dev name substring collision** — `"tom" in "thomas"` est vrai. Fix: word-boundary regex.
5. **`--branch` arg dans read_team_commits.py** etait parse mais jamais passe a la fonction. Fix: ajoute `current_branch_override` param.

### Review (2 passes)
- 2 CRITICAL: force-with-lease apres rebase silencieux (CORRIGE), --branch arg ignore (CORRIGE)
- 6 MODERATE: substring collision (CORRIGE), dev name normalization (CORRIGE), Python errors silenced (CORRIGE), missing commit check (CORRIGE), rename tab handling (CORRIGE), locale-dependent date (CORRIGE)
- 3 MINOR: double get_current_branch (CORRIGE), work_type threshold (CORRIGE), temp files cleanup (CORRIGE)

### Build / Tests
- Backend 257 tests inchanges (pas de modif execution/)
- Scripts utilitaires: pas de tests dedies (CLI tools)

### Branches
- `tom/dev` — changements locaux, pas encore commite

---

## 2026-02-19 (soir) — Paul (Payoss)

### Contexte
- Plan securite + fiabilite (6 issues, score audit 6.6→cible 7.5+)
- Attribution : Paul=securite+fiabilite, Augustin=fluidite, Tom=archi+optim

### Ce qui a ete fait (plan 6 etapes)

| # | Issue | Action | Fichiers modifies |
|---|-------|--------|-------------------|
| 1 | I-015 | Migration RLS: `auth_user_id = (SELECT auth.uid())` | Supabase migration MCP |
| 2 | I-007 | DOCX metadata strippee (author=Notomai, title/subject vides) | `execution/core/exporter_docx.py` L1835-1838 |
| 3 | C-011 | Legacy files supprimes + web/ externalise via env.js | Supprime: `frontend/assets/`, `frontend/public/assets/`, `frontend/pages/`, `frontend/index.html`, `dashboard/app/index.html`. Modifie: `web/supabase-client.js`, `web/questionnaires/questionnaire-common.js`, 6 HTML. Cree: `web/env.js.example`. Ajoute `web/env.js` a `.gitignore` |
| 4 | I-013+I-014 | Timeout+retry: Anthropic 120s/2 retries, Supabase 30s | `execution/anthropic_agent.py`, `execution/agent_llm.py`, `execution/database/supabase_client.py` |
| 5 | M-012 | Zustand persist middleware + beforeunload + recovery UI | `frontend/stores/workflowStore.ts`, `frontend/components/workflow/WorkflowPage.tsx` |
| 6 | M-007 | A faire manuellement dans Supabase Dashboard | (toggle Auth settings) |

### /document — mise a jour memory/
- `memory/CODE_MAP.md` — workflowStore LOC 283→318, WorkflowPage LOC 226→323, ajout Zustand persist pattern, tests frontend corrige
- `memory/JOURNAL.md` — ajout table /review fixes

### /audit (soir) — Score 6.7/10 (↑ depuis 6.6)
| Dimension | Score | Tendance |
|-----------|-------|----------|
| Architecture | 6.5 | → |
| Optimisation | 6.0 | → |
| Securite | **8.0** | **↑** |
| Fiabilite | **7.5** | **↑** |
| Fluidite | 5.5 | → |

Amelioration securite (+1) et fiabilite (+1) grace aux 6 issues fermees + review fixes.
Aucun nouveau probleme trouve. 12 issues restent ouvertes (3 important, 9 moyen).

### /review — 1 CRITICAL + 3 MODERATE fixes

| Severite | Fichier | Probleme | Fix |
|----------|---------|----------|-----|
| CRITICAL | `WorkflowPage.tsx` | Recovery dialog jamais affiche (Zustand persist hydrate async, step=IDLE au mount) | `onFinishHydration` + flag `hasHydrated` |
| MODERATE | `workflowStore.ts` | Step GENERATING sur rehydration = ecran casse | `onRehydrateStorage` fallback → REVIEW |
| MODERATE | `workflowStore.ts` | Pas de version persist = hydration errors futures | Ajoute `version: 1` |
| MODERATE | `supabase_client.py` | Import `ClientOptions` dans try/except masque la vraie erreur | Import top-level avec fallback gracieux |

### Verification finale
- `next build` — **OK** (11/11 pages) post-review fixes
- `get_advisors(security)` — 1 WARN restant (leaked password, toggle manuel M-007)
- `get_advisors(performance)` — **initplan WARN disparue**, reste unused indexes (INFO) + feedbacks policies (WARN)
- `grep eyJhbG` — **0 vrai cle**, reste uniquement docstring exemples dans agent_database.py
- 6 issues fermees : C-011, I-007, I-013, I-014, I-015, M-012

### Issues fermees : 6
C-011, I-007, I-013, I-014, I-015, M-012

---

## 2026-02-19 (matin) — Augustin

### Contexte
- START_DAY.bat avait un conflit de merge avec master
- Rebase augustin/dev sur origin/master (17 commits Tom/Paul importes)
- Audit complet /audit lance

### Ce qui a ete fait

| Action | Fichier | Detail |
|--------|---------|--------|
| REBASE | augustin/dev | Rebase sur origin/master, 17 commits importes (Tom: agent intelligence, AXE 2, AXE 7-8; Paul: AXE 1) |
| AUDIT | /audit | Audit 5 dimensions, score 5.8/10 |
| MODIFIE | START_DAY.bat | v2.0 par Augustin (ajout lecture commits equipe) |

### Decouvertes

1. **60+ index Supabase inutilises** — tous les index crees preventifs ne sont jamais utilises
2. **RLS policy `authenticated_update_own_notaire`** reevalue `auth.*()` par ligne (perf issue Supabase)
3. **2 policies permissive SELECT sur feedbacks** pour `authenticated` — sous-optimal
4. **api/main.py est passe a 2940 lignes** (+53 depuis dernier audit)

### Build / Tests
- Build frontend non verifie (skip pour rapidite)
- Backend : pas de changement de code

### Branches
- `augustin/dev` rebase sur `origin/master` (a jour)

---

## 2026-02-19 (matin) — Paul (Payoss)

### Contexte
- Finalisation integration prompt comportemental
- Deux audits via commande /audit (matin + soir)

### Ce qui a ete fait

| Action | Fichier | Detail |
|--------|---------|--------|
| CREE | `memory/PROJECT_STATE.md` | Features done/en cours/a faire + plan 10 axes |
| ENRICHI | `memory/CODE_MAP.md` | +stack tech, patterns cles, dependances |
| MIS A JOUR | `memory/ISSUES.md` | Ferme C-003 + M-002, ajoute 7 nouvelles issues |
| MIS A JOUR | `memory/JOURNAL.md` | Entree 18/02 (suite) + 19/02 |
| MIS A JOUR | `CLAUDE.md` | PROJECT_STATE.md dans routine pre-reponse + table |
| FIX | `frontend/tsconfig.json` | Exclude vitest.config.ts du build Next.js (C-010) |
| FIX | `frontend/stores/workflowStore.ts` + `frontend/lib/api/index.ts` | Workflow dynamique categorie_bien + sous_type (M-001) |
| MIGRATION | Supabase | 18 FK indexees + RLS initplan fix partiel (I-011, I-012) |
| AUDIT #1 | `/audit full` | Score 6/10 — 5 dimensions analysees |
| AUDIT #2 | `/audit full` | Score 6.6/10 — post-fixes, build green |

### Decouvertes (audit 19/02 soir)

1. **BUILD GREEN** — C-010 fixee, `next build` 11/11 pages OK.
2. **Supabase anon key dans 4 legacy JS** — `frontend/assets/js/app.js`, `frontend/public/assets/js/app.js`, `web/supabase-client.js`, `web/questionnaires/questionnaire-common.js`. supabase.ts est clean (Proxy env vars) mais ces fichiers trainent. **C-011 NOUVEAU**.
3. **68 index Supabase inutilises** (pas 55) — confirme par advisor performance.
4. **Zero retry logic** dans tout le projet — grep confirme 0 occurrences. **I-013 NOUVEAU**.
5. **Zero timeout backend** — seul timeout commente L2931. **I-014 NOUVEAU**.
6. **RLS initplan incomplet** — `authenticated_update_own_notaire` sur notaire_users encore flagge. **I-015 NOUVEAU**.
7. **Zero attributs accessibilite** — grep confirme 0 aria-*/role/tabIndex dans components/. M-009 aggrave.
8. **Tendance** : amelioration vs audit matin (+0.6), 6 issues fermees, 5 nouvelles.

### Build / Tests
- `next build` — **OK** (11/11 pages)
- Backend 257 tests + 30 frontend = 287

### Branches
- `payoss/dev` — commit `b0845b9` (workflow dynamique + index FK + RLS)

---

## 2026-02-18 (soir) — Paul (Payoss)

### Contexte
- Paul a demande un audit complet du projet (10 axes)
- Puis implementation de l'AXE 1 (connexion frontend <-> backend)
- Augustin a confirme qu'il prend les axes 4, 5, 6, 9

### Ce qui a ete fait

**AXE 1 complet — commit `3c6e009` puis `9bacf0f` (erratum audit)**

| Action | Fichier | Detail |
|--------|---------|--------|
| CREE | `frontend/lib/config.ts` | Config centralisee (API_URL, API_KEY, timeouts) |
| CREE | `frontend/lib/api/client.ts` | Client HTTP securise (auth, timeout, erreurs typees, SSE) |
| CREE | `frontend/lib/api/index.ts` | 5 fonctions workflow — LE fichier manquant |
| CREE | `frontend/lib/api/promesse.ts` | 3 fonctions API promesse |
| CREE | `frontend/lib/constants.ts` | Labels UI, couleurs, etapes |
| MODIFIE | `frontend/app/app/page.tsx` | URL hardcodee → import config |
| MODIFIE | `frontend/app/app/dossiers/page.tsx` | idem |
| MODIFIE | `frontend/app/api/chat/route.ts` | Fix URL Modal incorrecte |
| MODIFIE | `frontend/components/ChatArea.tsx` | URL → config |
| MODIFIE | `frontend/components/workflow/WorkflowPage.tsx` | URL → config |
| MODIFIE | `frontend/components/workflow/GenerationProgress.tsx` | URL → config |
| MODIFIE | `frontend/components/ChatWithViager.tsx` | Fix types .texte→.question |
| MODIFIE | `frontend/components/ViagerBadge.tsx` | Fix typage SousType index |
| MODIFIE | `api/main.py` | API key query param pour SSE |
| MODIFIE | `.gitignore` | Exception `!frontend/lib/` |
| CREE | `PLAN_10_AXES.md` | Plan complet 10 axes |
| CREE | `docs/AUDIT_COMPLET_18_FEVRIER_2026.md` | Audit (puis corrige) |
| CREE | `docs/PROMPTS_EQUIPE.md` | Prompts equipe |

### Decouvertes

1. **api/main.py fait 2887 lignes avec 39 endpoints** — l'audit initial disait que les endpoints workflow n'existaient pas, c'etait FAUX. Ils sont a partir de la ligne 1891.
2. **Format mismatches** entre frontend et backend :
   - `type_acte` (frontend) vs `categorie_bien` (backend)
   - `{id, titre}` (frontend) vs `{key, title}` (backend)
   - `sectionId` inutile cote backend
3. **.gitignore bloque `frontend/lib/`** — la regle Python `lib/` capturait aussi le dossier frontend
4. **EventSource ne supporte pas les headers custom** — API key doit passer en query param

### Erreurs commises

| Erreur | Gravite | Lecon |
|--------|---------|-------|
| Affirme que les endpoints `/workflow/*` n'existaient pas | **CRITIQUE** | TOUJOURS grep les patterns dans un fichier > 500 lignes. Ne JAMAIS lire sequentiellement et conclure. |
| Audit partiel de api/main.py (lu ~500 lignes sur 2887) | **CRITIQUE** | Utiliser `grep -n "@app\." api/main.py` AVANT toute affirmation sur les endpoints |

### Build
- `next build` passe ✅ (compilation + type-checking + generation statique)

### Branches
- `payoss/dev` et `master` synchronises
- Commits: `3c6e009` (AXE 1) + `9bacf0f` (erratum audit)

---

## 2026-02-18 (soir, suite) — Paul (Payoss)

### Contexte
- Suite session : creation systeme memoire, conventions, commande /audit
- Integration des regles comportementales dans CLAUDE.md
- Decouverte du commit d'Augustin en parallele

### Ce qui a ete fait

| Action | Fichier | Detail |
|--------|---------|--------|
| CREE | `memory/JOURNAL.md` | Journal quotidien |
| CREE | `memory/CODE_MAP.md` | Cartographie exhaustive (39 endpoints, LOC) |
| CREE | `memory/CHECKLIST.md` | Regles verification avant affirmation |
| CREE | `memory/ISSUES.md` | Tracker 17 issues ouvertes, 8 fermees |
| CREE | `memory/CONVENTIONS.md` | Regles code, naming, Git, securite |
| CREE | `memory/README.md` | Index des fichiers memoire |
| CREE | `.claude/commands/audit.md` | Commande /audit 5 phases |
| MODIFIE | `CLAUDE.md` | +74 lignes regles comportementales en tete |
| MIS A JOUR | `memory/ISSUES.md` | Ferme 6 issues corrigees par Augustin |

### Decouvertes

1. **Augustin a commite `9e19166`** pendant la session — fixes axes 4, 5, 6, 9 :
   - 13 vues SECURITY_DEFINER → INVOKER
   - RLS sur api_costs_tracking + 25 policies
   - 9 fonctions avec SET search_path
   - UUIDs hardcodes supprimes de chat_handler.py
   - Cle dev supprimee de signed_urls.py
   - CI/CD fix (main→master, chemins Modal)
   - Procedure incident RGPD ajoutee
2. **Augustin a aussi commite `d017da2`** — politique de confidentialite HTML (637 lignes)
3. **PR #23 mergee** pour les fixes Augustin

### Branches
- `payoss/dev` et `master` synchronises
- Commits: `17be6ff` (memoire) + `f7e8b22` (conventions) + merge `606e43d`
- Augustin: `9e19166` (securite) + `d017da2` (politique confidentialite) via PR #23

---

## 2026-02-18 (nuit, suite) — Tom

### Contexte
- Rendre le chatbot Modal aussi intelligent que l'agent Claude Code local
- 3 gaps identifies: system prompt maigre, orchestration mock, pas de self-annealing

### Ce qui a ete fait

**Chantier 1-3: Agent intelligence upgrade (3 fichiers, ~400 lignes modifiees)**

| Action | Fichier | Detail |
|--------|---------|--------|
| MODIFIE | `execution/anthropic_agent.py` | SYSTEM_PROMPT 73→175 lignes (detection 3 niveaux, 8 outils, workflow, regles) |
| MODIFIE | `execution/anthropic_agent.py` | `_load_full_directive()` remplace `_load_directive_summary()` (32K chars vs 3KB tronque) |
| MODIFIE | `execution/anthropic_agent.py` | `_build_cached_system()` restructure en 3 tiers (cache prompt Anthropic) |
| MODIFIE | `execution/anthropic_agent.py` | `_build_session_context()` : resume donnees collectees dans le prompt |
| MODIFIE | `execution/anthropic_agent.py` | Constantes: MAX_TOOL_ITERATIONS 8→15, MAX_OUTPUT_TOKENS 2048→4096, MAX_HISTORY_MESSAGES 20→30 |
| MODIFIE | `api/agents.py` | `execute_clause_suggester()` : mock → reel (suggerer_clauses.py) |
| MODIFIE | `api/agents.py` | `execute_post_generation_reviewer()` : mock (qa_score=94) → QA 7 dimensions reel |
| MODIFIE | `api/agents.py` | `orchestrate_generation()` phases 4-7 : connecte au vrai pipeline (GestionnairePromesses + OrchestratorNotaire) |
| MODIFIE | `api/agents.py` | Sequential strategy implementee (etait `pass` no-op) |
| MODIFIE | `api/agents.py` | `asyncio.to_thread()` pour les appels blocking (cadastre, Q&R) |
| MODIFIE | `deployment_modal/modal_app.py` | Ajout mount `docs_original/`, secret `github-credentials` |
| MODIFIE | `deployment_modal/modal_app.py` | weekly_catalog_sync : suppression ecriture FS ephemere |
| MODIFIE | `deployment_modal/modal_app.py` | daily_learning_job : seuil 5+ corrections pour self-anneal |

### Review (2 passes)

**Pass 1** — 5 CRITICAL, 4 MODERATE trouves :
- C1: index/label mismatch dans resultats paralleles (CORRIGE)
- C2+C3: cles `enriched_data` et `donnees_collectees` mal alignees (CORRIGE)
- C4+C5: event loop bloque par appels sync dans async (CORRIGE avec asyncio.to_thread)
- M2: sequential strategy = `pass` no-op (CORRIGE, implementation complete)
- M4: ecriture FS ephemere Modal (CORRIGE)
- E2: clause-suggester erreur silencieuse (CORRIGE)
- E3: formule speedup inversee (CORRIGE)

**Pass 2 (re-review)** — 2 nouveaux issues trouves et corriges :
- NEW-1: speedup comptait tous les agents au lieu des seuls paralleles
- NEW-2: clause-suggester error status pas propage dans agents_executed

### Decouvertes

1. **`asyncio.gather` sur des fonctions `async` qui font du blocking I/O** ne parallelise PAS — les coroutines se serialisent sur l'event loop. Toujours `asyncio.to_thread()` pour le code sync.
2. **Les cles de retour des fonctions async** doivent matcher les cles lues par l'appelant — sinon les donnees sont silencieusement ignorees (pas de KeyError car `.get()` retourne None).

### Build / Tests
- `python -m pytest tests/ -v` — 348 passed, 7 failed (pre-existants), 4 skipped
- Les 7 failures sont dans test_chat_generation.py (6) et test_tier1_optimizations.py (1) — pas liees a nos changements

### Branches
- `tom/dev` — changements locaux, pas encore commite

---

## 2026-02-18 (nuit) — Tom

### Contexte
- Suite de l'audit 10 axes. AXE 1 fait par Paul, AXE 2 assigne a Tom (frontend cleanup)
- Merge `origin/master` → `tom/dev` pour recuperer le travail de Paul (commit `3c6e009`)

### Ce qui a ete fait

**AXE 2 complet — Nettoyage & Optimisation Frontend (~900 lignes nettoyees)**

| Action | Fichier | Detail |
|--------|---------|--------|
| SUPPRIME | `components/ChatWithViager.tsx` | 302 lignes orphelines |
| SUPPRIME | `components/ViagerBadge.tsx` | 130 lignes orphelines |
| SUPPRIME | `hooks/useViagerDetection.ts` | 208 lignes orphelines |
| CREE | `lib/auth.ts` | `getUserEtudeId()` extrait de 2 pages |
| CREE | `lib/format.ts` | `formatDate()` extrait de 2 composants |
| CREE | `components/MessageBubble.tsx` | 207 lignes extraites de ChatArea |
| CREE | `components/TypingIndicator.tsx` | 27 lignes extraites de ChatArea |
| CREE | `app/app/clients/[id]/page.tsx` | Page placeholder (lien mort fixe) |
| CREE | `app/app/dossiers/[id]/page.tsx` | Page placeholder (lien mort fixe) |
| MODIFIE | `app/app/dossiers/page.tsx` | import auth.ts, `useMemo`, supprime `console.error` |
| MODIFIE | `app/app/clients/page.tsx` | import auth.ts, 3x `useMemo`, supprime `console.error` |
| MODIFIE | `components/ClientCard.tsx` | import format.ts au lieu de formatDate inline |
| MODIFIE | `components/DossierCard.tsx` | idem |
| MODIFIE | `components/ChatArea.tsx` | 373 → 130 lignes (extraction composants) |
| MODIFIE | `components/Header.tsx` | Boutons Brouillons/Exporter marques `disabled` |
| MODIFIE | `components/Sidebar.tsx` | NavItem avec prop `disabled` + tooltip |
| MODIFIE | `components/ParagraphReview.tsx` | supprime `console.error` client-side |
| MODIFIE | `app/app/page.tsx` | supprime 2x `console.error` client-side |
| MODIFIE | `app/login/page.tsx` | 361 → 168 lignes (style jsx → Tailwind) |
| MODIFIE | `app/page.tsx` (landing) | 278 → 108 lignes (style jsx → Tailwind) |

### Decouvertes

1. **Paul a deja fixe les types `any`** dans `promesse.ts` — plus besoin de le faire
2. **`lib/supabase.ts` n'existe toujours pas** dans le repo — importe par 6 fichiers, c'est dans le scope de Paul (AXE 1)
3. **`api/chat/route.ts` console.error** est server-side (Next.js API route) — conserve car utile pour debug serveur
4. **Les emojis dans landing page** ne peuvent pas etre directement en JSX Tailwind — utilise HTML entities

### Erreurs commises

| Erreur | Gravite | Lecon |
|--------|---------|-------|
| Edit tool "File has not been read" apres interruption user | BASSE | Toujours re-lire un fichier avant de l'editer si le contexte a ete coupe |

### Review & Documentation (subagents)

**`/review` (feature-dev:code-reviewer)** — 17 fichiers, 2 passes :
- 2 CRITICAL : props mortes `metadata`/`suggestions` dans MessageBubble (CORRIGE), loadDossiers deps (OK en pratique)
- 3 MODERATE : formatDate null safety (CORRIGE), dossier count filtre (CORRIGE), includes('format') heuristique (pre-existant)
- 2 MINOR : `|| null` → `?? null` dans auth.ts (CORRIGE), landing responsive (OK)

**`/document`** — CODE_MAP.md mis a jour (composants, pages, LOC, stats)

### Build / Tests
- `next build` — PASSE ✅ (10/10 pages, compilation + types OK)
- `lib/supabase.ts` cree avec lazy init (Proxy) pour eviter crash prerendering sans env vars
- Backend 257 tests inchanges (pas de modif Python)

### Branches
- `tom/dev` — AXE 2 commite en `af1ad93`

---

## 2026-02-18 (nuit, suite 2) — Tom

### Contexte
- Suite de l'audit 10 axes. AXE 2 commite. Attaque AXE 7 (UX) + AXE 8 (Tests)

### Ce qui a ete fait

**AXE 7 — UX & Experience Notaire**

| Action | Fichier | Detail |
|--------|---------|--------|
| CREE | `app/app/documents/page.tsx` | Page "Mes Documents" (~213 lignes), liste `actes_generes` Supabase |
| CREE | `components/DocumentCard.tsx` | Card document (131 lignes) — type, status, completion, download DOCX/PDF |
| MODIFIE | `components/Sidebar.tsx` | +2 NavLinks : "Mes Documents" (/app/documents), "Workflow guide" (/app/workflow) |
| MODIFIE | `components/ChatArea.tsx` | +lien "Mode guide" au-dessus de l'input → /app/workflow |
| MODIFIE | `app/app/workflow/page.tsx` | +bouton flottant "Retour au chat" (fixed bottom-right) |
| MODIFIE | `types/index.ts` | +ActeGenere interface (14 champs), nom rendu optionnel |

**AXE 8 — Tests Frontend (de 0 a 30)**

| Action | Fichier | Detail |
|--------|---------|--------|
| INSTALLE | `package.json` | +vitest, @testing-library/react, @testing-library/jest-dom, @vitejs/plugin-react, jsdom |
| CREE | `vitest.config.ts` | Config Vitest — React plugin, jsdom, path alias @/, css:false |
| CREE | `vitest.setup.ts` | Setup jest-dom/vitest matchers |
| CREE | `__tests__/format.test.ts` | 6 tests : null, undefined, vide, invalide, ISO, date-only |
| CREE | `__tests__/auth.test.ts` | 4 tests : happy path, no user, no etude_id, erreur reseau |
| CREE | `__tests__/MessageBubble.test.tsx` | 11 tests : user/assistant, feedback +/-, download, section, quickActions, welcome, legal ref |
| CREE | `__tests__/ChatArea.test.tsx` | 9 tests : submit, empty submit, typing dots, mode guide link, disabled btn, streaming placeholder |

### Review

**1 passe (feature-dev:code-reviewer)** — 6 issues :
- CRITIQUE : API key in query string (pre-existant, EventSource limitation)
- CRITIQUE : Supabase errors (deja corrige dans le code reel)
- IMPORTANT : `nom` type required vs optional (CORRIGE)
- IMPORTANT : etude_id guard (deja present dans le code reel)
- IMPORTANT : fragile CSS class test (note pour futur)
- IMPORTANT : download sans feedback erreur (pre-existant)

### Build / Tests
- `vitest run` — 30 passed, 0 failed ✅
- `next build` — a verifier (en cours)

### Branches
- `tom/dev` — changements locaux, pas encore commite

---

## Template entree journal

```
## YYYY-MM-DD — Qui (Prenom)

### Contexte
[Pourquoi cette session]

### Ce qui a ete fait
| Action | Fichier | Detail |
|--------|---------|--------|

### Decouvertes
[Choses apprises sur le code]

### Erreurs commises
| Erreur | Gravite | Lecon |

### Build / Tests
[Status build, tests passes/echoues]

### Branches
[Etat des branches, commits]
```
