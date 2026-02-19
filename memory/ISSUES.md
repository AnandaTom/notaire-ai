# Issue Tracker - Notomai

> Problemes ouverts et fermes. Mis a jour a chaque session.
> Chaque issue a : ID, severite, statut, qui, date ouverture, date fermeture.

---

## Ouverts

### CRITIQUE

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| C-011b | Cles anon Supabase REGRESSEES par merge | 6 fichiers legacy | Paul | 19/02 | Merge `c4be78d` "keep both sides" a restaure les fichiers supprimes dans `b4d4129`. Fichiers: `frontend/assets/js/app.js`, `frontend/public/assets/js/app.js`, `frontend/pages/login.html`, `frontend/index.html`, `web/supabase-client.js`, `web/questionnaires/questionnaire-common.js` |

### IMPORTANT

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| I-004 | Pas de DPA signe avec Supabase | Legal | Paul | 18/02 | OBLIGATOIRE RGPD |
| I-008 | self_anneal.py n'existe pas | `modal_app.py` | - | 18/02 | Manquant; daily_learning_job gere l'erreur |
| I-010 | ~~Endpoints /cadastre/* absents de api/main.py~~ | `api/main.py` | Paul | 18/02 | **FERME 19/02** — routers montes |

### MOYEN

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| M-003 | Pas de monitoring (Sentry) | - | Augustin (axe 6) | 18/02 | Aucun outil |
| M-004 | Pas d'onboarding / tutoriel | - | Tom (axe 7) | 18/02 | Notaire perdu au 1er lancement |
| M-005 | CLAUDE.md surdimensionne (500+ lignes) | `CLAUDE.md` | Paul (axe 10) | 18/02 | Melange doc, changelog, instructions |
| M-006 | Templates promesse sans {% include %} | `templates/` | Paul | 18/02 | Seul vente utilise les includes |
| M-007 | Protection mots de passe compromis desactivee | Supabase Auth | - | 18/02 | Requiert plan Pro Supabase — pas dispo en Free |
| M-008 | ~65 index Supabase inutilises | Supabase | Paul | 19/02 | Confirme par advisor perf 19/02 nuit (65 index) |
| M-009 | Accessibilite frontend = ZERO | `frontend/components/` | Tom | 19/02 | 0 attributs aria/role/tabIndex (audit 19/02 soir) |
| M-010 | POST /ventes/generer absent de CODE_MAP | `api/main.py:1601` | - | 19/02 | 40 endpoints (pas 39) |
| M-011 | Multiple permissive policies feedbacks | Supabase | Augustin | 19/02 | 2 policies SELECT meme role, perf |
| M-013 | CODE_MAP desynchronise | `memory/CODE_MAP.md` | Paul | 19/02 | LOC obsoletes: api/main.py 2940→2994, anthropic_agent.py 1030→1101, workflowStore.ts 318→436 |
| M-014 | Ajouter message "mot de passe robuste" sur page inscription | Frontend (a creer) | Tom | 19/02 | Page inscription n'existe pas encore |
| M-015 | 53 fichiers morts dans execution/ | `execution/` | Tom | 19/02 | Fichiers Python jamais importes — dead code |
| M-016 | 7 tests backend en echec (pre-existants) | `tests/` | Tom | 19/02 | test_chat_generation (6) + test_tier1_optimizations (1) |
| M-017 | Responsive minimal | `frontend/components/` | Tom | 19/02 | 14 classes md: seulement sur ~25 composants |

---

## Fermes

| ID | Probleme | Ferme le | Commit | Notes |
|----|----------|----------|--------|-------|
| I-009 | weekly_catalog_sync ecrit sur FS read-only | 18/02 | tom/dev | Corrige: persistence via Supabase |
| C-001 | `frontend/lib/api.ts` n'existe pas | 18/02 | `3c6e009` | Cree frontend/lib/api/{client,index,promesse}.ts |
| C-004 | URLs hardcodees dans 6 fichiers frontend | 18/02 | `3c6e009` | Centralise dans frontend/lib/config.ts |
| C-005 | Bug URL Modal dans route.ts | 18/02 | `3c6e009` | notaire-ai → notomai |
| C-006 | Types incorrects ChatWithViager.tsx | 18/02 | `3c6e009` | .texte→.question, .help→.aide |
| C-007 | Typage ViagerBadge.tsx SousType index | 18/02 | `3c6e009` | BadgeColor union type |
| C-008 | .gitignore bloque frontend/lib/ | 18/02 | `3c6e009` | Ajout !frontend/lib/ |
| C-009 | SSE ne peut pas s'authentifier | 18/02 | `3c6e009` | API key en query param |
| AUDIT-001 | Audit affirme endpoints /workflow/* absents | 18/02 | `9bacf0f` | ERREUR — existent L1891-2296 |
| C-002 | UUIDs hardcodes dans chat_handler.py | 18/02 | `9e19166` | Augustin — auth dynamique |
| I-001 | 13 vues SECURITY_DEFINER | 18/02 | `9e19166` | Augustin — SECURITY_INVOKER |
| I-002 | api_costs_tracking sans RLS | 18/02 | `9e19166` | Augustin — RLS + 25 policies |
| I-003 | 8 fonctions search_path mutable | 18/02 | `9e19166` | Augustin — SET search_path |
| I-005 | Pas de registre des traitements | 18/02 | `9e19166` | Augustin — registre MAJ |
| I-006 | Cle dev par defaut signed_urls.py | 18/02 | `9e19166` | Augustin — cle supprimee |
| C-003 | Supabase anon key en dur | 19/02 | tom/dev | Tom — Proxy lazy init, env vars only |
| M-002 | Pas de tests frontend | 19/02 | tom/dev | Tom — 30 tests Vitest + Testing Library (AXE 8) |
| C-010 | `next build` CASSE — vitest.config.ts | 19/02 | tom/dev + `1eecf9b` | Tom + Paul — exclu dans tsconfig.json |
| I-010 | Endpoints /cadastre/* absents api/main.py | 19/02 | payoss/dev | Paul — include_router cadastre + validation |
| I-011 | ChatAnonymizer non branche | 19/02 | payoss/dev | Paul — anonymiser/deanonymiser dans anthropic_agent.py |
| I-012 | data_enrichment.py non appele | 19/02 | payoss/dev | Paul — insere avant validation dans generate + generate-stream |
| I-013 | promesse.ts zero imports | 19/02 | payoss/dev | Paul — re-export dans api/index.ts + VALIDATING step |
| I-014 | Pile securite non branchee | 19/02 | payoss/dev | Paul — AgentClientAccess dans anthropic_tools.py |
| M-001 | startWorkflow hardcode copropriete | 19/02 | `b0845b9` | Paul — categorie_bien + sous_type dynamiques |
| I-011 | 18 FK non-indexees Supabase | 19/02 | migration | Paul — CREATE INDEX 18 FK |
| I-012 | RLS initplan notaire_users | 19/02 | migration | Paul — (select current_setting(...)) |
| C-011 | Anon key dans legacy files + web/ | 19/02 | payoss/dev | Paul — legacy supprime, web/ externalise via env.js |
| I-007 | DOCX metadata non strippee | 19/02 | payoss/dev | Paul — core_properties nettoyees avant save |
| I-013 | Zero retry + silent catches | 19/02 | payoss/dev + tom/dev | Paul — retries. Tom — showToast() |
| I-014 | Zero timeout backend | 19/02 | payoss/dev | Paul — timeout=120s Anthropic, 30s Supabase |
| I-015 | RLS initplan notaire_users | 19/02 | migration MCP | Paul — auth_user_id = (SELECT auth.uid()) |
| M-012 | Pas de sauvegarde workflow | 19/02 | payoss/dev | Paul — Zustand persist + beforeunload + recovery UI |
| I-016 | Secret github-credentials manquant Modal | 19/02 | TODO **Tom** | Tom (Paul dit que c'est un ptit coquin) — Creer fine-grained token GitHub (repo AnandaTom/notaire-ai only, Contents read-only) puis ajouter sur modal.com/secrets/notomai secret_name=github-credentials cle=GITHUB_TOKEN. Decommenter deployment_modal/modal_app.py L65 apres |

---

## Conventions

- **C-xxx** : Critique (bloquant)
- **I-xxx** : Important (non-bloquant mais a corriger)
- **M-xxx** : Moyen (amelioration)
- **AUDIT-xxx** : Erreur d'audit
