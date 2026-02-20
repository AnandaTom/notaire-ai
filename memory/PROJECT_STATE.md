# Etat du Projet - Notomai

> Fonctionnalites : done / en cours / a faire.
> Mis a jour a chaque session. Derniere MAJ : 2026-02-20 (soir).

---

## Vue d'ensemble

| Categorie | Done | En cours | A faire | Score |
|-----------|------|----------|---------|-------|
| Backend API | 41 endpoints (+/dashboard/stats) | - | - | 95% |
| Frontend | UX Redesign + AI Panel deploye (Vercel) | - | Onboarding | 80% |
| Templates | 7/7 PROD | - | - | 100% |
| Chat + Generation | **E2E FONCTIONNE** (20/02) | - | - | 90% |
| AI Side Panel | **FAIT** (20/02 soir) — 380px copilot panel SSE | - | Connecter contexte workflow | 80% |
| Securite | Axes 4,5 (fait) | DPA Supabase | password leak | 80% |
| RGPD | Registre, procedure, politique | DPA Supabase | Audit CNIL complet | 60% |
| Tests | 339 backend + 53 frontend | - | Coverage, E2E | 75% |
| CI/CD | Fix deploy.yml + test.yml | - | Monitoring (Sentry) | 60% |

---

## Fonctionnalites — DONE

| Feature | Composants | Commit/Version |
|---------|-----------|----------------|
| API Backend complete | 41 endpoints, `api/main.py` (~2994 LOC) | v2.0.0 + `6470690` |
| Chat SSE | `chat_handler.py`, streaming temps reel | v1.5.0 |
| Workflow backend | 5 endpoints `/workflow/*` (L1891-2296) | v1.7.0 |
| Workflow frontend | 20 composants React, store Zustand | `98ebb0e` |
| Connexion FE <-> BE | `frontend/lib/api/`, config centralisee | `3c6e009` (AXE 1) |
| Templates 7 PROD | vente, 4 promesses, reglement copro, modificatif EDD | v2.0.0 |
| Viager complet | Template dedie, 4 sections, 19 questions, validation | v2.0.0 |
| Detection 3 niveaux | categorie + type + sous-type | v1.9.0 |
| Sections conditionnelles | lotissement, groupe habitations, servitudes | v1.9.0 |
| Creation copropriete | 6 guards, detection, schema, questions | v2.0.0 |
| Agent autonome | NL parsing, multi-parties, Q&R interactif | v1.3.1 |
| Agent Teams (Opus 4.6) | orchestrator, cadastre, collector, clause, reviewer | 11/02/2026 |
| Collecte Q&R | 97 questions, 21 sections, 64% prefill | v1.6.0 |
| Conversion promesse→vente | Conservation donnees, champs complementaires | v1.6.0 |
| Cadastre service | geocoding BAN + parcelle IGN, cache 24h | v1.8.0 |
| Extraction titre | OCR + ML, 50+ patterns regex | v1.3.0 |
| Securite Supabase | 13 vues INVOKER, RLS, search_path, policies | `9e19166` (Augustin) |
| Secrets code | UUIDs supprimes, cle dev supprimee | `9e19166` (Augustin) |
| CI/CD fixes | deploy.yml main→master, chemins Modal, test.yml | `9e19166` (Augustin) |
| RGPD procedure | Procedure incident, registre MAJ, politique confidentialite | `9e19166` + `d017da2` |
| Systeme memoire | 6 fichiers memory/, commande /audit | `17be6ff` |
| Regles comportementales | Regle #0, self-annealing, multi-dev | `f7e8b22` |
| UX Redesign (Phases 0-4) | Shared layout, dashboard, sidebar, header, toast, command palette | `1e31541` |
| AI Side Panel (Copilot) | 380px panel SSE, toggle, context hints, responsive | `6470690` |
| Dashboard API endpoint | `/dashboard/stats` — single call replaces 4 Supabase queries | `6470690` |
| Accessibility (ChatArea) | role=log, aria-live, aria-labels sur textarea + boutons | `6470690` |
| Cleanup ancien code | Supprime Header.tsx + Sidebar.tsx inutilises | `6470690` |
| Tests frontend (53) | Toast(6), CommandPalette(10), Dashboard(7) + anciens(30) | `6470690` |

---

## Fonctionnalites — EN COURS

| Feature | Responsable | Bloqueur | Notes |
|---------|------------|----------|-------|
| DPA Supabase (I-004) | Paul (legal) | Signature requise | Obligatoire RGPD |
| Connecter contexte workflow au AI panel | Paul | - | `setAiPanelContext()` dans workflow/dossier pages |

---

## Fonctionnalites — A FAIRE

### Priorite haute

| Feature | Responsable | Dependance | Estimation |
|---------|------------|------------|------------|
| AI Panel: contexte workflow/dossiers | Paul | uiStore.setAiPanelContext | 0.5 jour |
| UX onboarding (M-004, AXE 7) | Tom | - | 2-3 jours |

### Priorite moyenne

| Feature | Responsable | Dependance | Estimation |
|---------|------------|------------|------------|
| Nettoyage frontend (AXE 2) | Tom | - | 2-3 jours |
| Monitoring Sentry (M-003) | Augustin | - | 1 jour |

### Priorite basse / futur

| Feature | Responsable | Notes |
|---------|------------|-------|
| Architecture cleanup (AXE 10) | Paul | CLAUDE.md trop long |
| Migration Modal → GCP Cloud Run | Augustin | Pour RGPD (donnees en France) |
| RAG pour suggestion clauses | - | Phase 2+, LlamaIndex |
| Fix self_anneal.py manquant (I-008) | - | Import dans modal_app.py, gere par try/except |

---

## Plan 10 Axes — Avancement

| Axe | Description | Qui | Status |
|-----|-------------|-----|--------|
| 1 | Connexion Frontend <-> Backend | Paul | **FAIT** (`3c6e009`) |
| 2 | Nettoyage frontend | Tom | A faire |
| 3 | Optimisation backend | - | A faire |
| 4 | Securite BDD (Supabase) | Augustin | **FAIT** (`9e19166`) |
| 5 | Secrets dans le code | Augustin | **90%** — reste C-003 |
| 6 | Infrastructure / DevOps | Augustin | **FAIT** (`9e19166`) |
| 7 | UX / Onboarding | Tom | En cours (AI panel fait, reste onboarding) |
| 8 | Tests frontend | Tom/Paul | **En cours** — 53 tests (30 anciens + 23 nouveaux) |
| 9 | RGPD / Conformite | Augustin | **80%** — reste DPA |
| 10 | Architecture / Doc | Paul | En cours (memory/ fait) |
