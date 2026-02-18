# Journal de Bord - Notomai

> Ce fichier est tenu par Claude. Chaque session est loguee avec : date, ce qui a ete fait,
> fichiers modifies, decouvertes, erreurs commises, lecons tirees.
> BUT : ne jamais perdre le fil d'un jour a l'autre.

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
