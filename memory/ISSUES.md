# Issue Tracker - Notomai

> Problemes ouverts et fermes. Mis a jour a chaque session.
> Chaque issue a : ID, severite, statut, qui, date ouverture, date fermeture.

---

## Ouverts

### CRITIQUE

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| C-010 | `next build` CASSE — vitest.config.ts | `frontend/vitest.config.ts:1` | Tom/Paul | 19/02 | `/// <reference types="vitest" />` inclus dans compil TS Next.js. Fix: exclure dans tsconfig.json |

### IMPORTANT

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| I-004 | Pas de DPA signe avec Supabase | Legal | Paul | 18/02 | OBLIGATOIRE RGPD |
| I-007 | DOCX metadata non strippee | `core/exporter_docx.py` | Augustin | 18/02 | Risque RGPD (auteur, chemins) |
| I-008 | self_anneal.py n'existe pas | `modal_app.py` | - | 18/02 | Manquant; daily_learning_job gere l'erreur |
| I-010 | Endpoints /cadastre/* absents de api/main.py | `api/main.py` | - | 18/02 | Documentes dans CLAUDE.md mais pas integres |
| I-011 | 18 FK non-indexees Supabase | Supabase | Augustin | 19/02 | actes_generes, clients, dossiers, feedbacks, etc. Perf JOIN/DELETE |
| I-012 | RLS initplan notaire_users | Supabase | Augustin | 19/02 | `auth.uid()` re-evalue par ligne → `(select auth.uid())` |

### MOYEN

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| M-001 | startWorkflow hardcode categorie='copropriete' | `frontend/lib/api/index.ts:95` | Paul | 18/02 | Ne supporte pas terrain/hors copro |
| M-003 | Pas de monitoring (Sentry) | - | Augustin (axe 6) | 18/02 | Aucun outil |
| M-004 | Pas d'onboarding / tutoriel | - | Tom (axe 7) | 18/02 | Notaire perdu au 1er lancement |
| M-005 | CLAUDE.md surdimensionne (500+ lignes) | `CLAUDE.md` | Paul (axe 10) | 18/02 | Melange doc, changelog, instructions |
| M-006 | Templates promesse sans {% include %} | `templates/` | Paul | 18/02 | Seul vente utilise les includes |
| M-007 | Protection mots de passe compromis desactivee | Supabase Auth | Paul | 18/02 | Confirme par Supabase advisor 19/02 |
| M-008 | ~55 index Supabase inutilises | Supabase | Augustin | 19/02 | Dead weight, overhead INSERT/UPDATE |
| M-009 | Accessibilite frontend minimale | `frontend/components/` | Tom | 19/02 | 19 aria/role/tabIndex sur ~25 composants |
| M-010 | POST /ventes/generer absent de CODE_MAP | `api/main.py:1601` | - | 19/02 | 40 endpoints (pas 39) |
| M-011 | Multiple permissive policies feedbacks | Supabase | Augustin | 19/02 | 2 policies SELECT meme role, perf |

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

---

## Conventions

- **C-xxx** : Critique (bloquant)
- **I-xxx** : Important (non-bloquant mais a corriger)
- **M-xxx** : Moyen (amelioration)
- **AUDIT-xxx** : Erreur d'audit
