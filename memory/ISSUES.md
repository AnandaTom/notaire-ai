# Issue Tracker - Notomai

> Problemes ouverts et fermes. Mis a jour a chaque session.
> Chaque issue a : ID, severite, statut, qui, date ouverture, date fermeture.

---

## Ouverts

### CRITIQUE

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| C-003 | Supabase anon key en dur | `frontend/lib/supabase.ts:6` | Paul | 18/02 | Fuite dans le bundle client si .env.local absent |

### IMPORTANT

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| I-004 | Pas de DPA signe avec Supabase | Legal | Paul | 18/02 | OBLIGATOIRE RGPD |
| I-007 | DOCX metadata non strippee | `core/exporter_docx.py` | Augustin | 18/02 | Risque RGPD (auteur, chemins) |
| I-008 | self_anneal.py n'existe pas | `modal_app.py:187` | - | 18/02 | Importe mais manquant, gere par try/except |
| I-009 | weekly_catalog_sync ecrit sur FS read-only | `modal_app.py:251` | - | 18/02 | Modal = read-only hors /outputs |
| I-010 | Endpoints /cadastre/* absents de api/main.py | `api/main.py` | - | 18/02 | Documentes dans CLAUDE.md mais pas integres |

### MOYEN

| ID | Probleme | Fichier | Qui | Ouvert le | Notes |
|----|----------|---------|-----|-----------|-------|
| M-001 | startWorkflow hardcode categorie='copropriete' | `frontend/lib/api/index.ts:95` | Paul | 18/02 | Ne supporte pas terrain/hors copro dynamiquement |
| M-002 | Pas de tests frontend | - | Tom (axe 8) | 18/02 | Ni Vitest, ni Jest, ni Playwright |
| M-003 | Pas de monitoring (Sentry) | - | Augustin (axe 6) | 18/02 | Aucun outil de monitoring |
| M-004 | Pas d'onboarding / tutoriel | - | Tom (axe 7) | 18/02 | Notaire perdu au premier lancement |
| M-005 | CLAUDE.md surdimensionne (500+ lignes) | `CLAUDE.md` | Paul (axe 10) | 18/02 | Melange doc, changelog, instructions |
| M-006 | Templates promesse sans {% include %} | `templates/` | Paul | 18/02 | Seul vente utilise les includes |
| M-007 | Protection mots de passe compromis desactivee | Supabase Auth | Paul | 18/02 | Setting Supabase a activer |

---

## Fermes

| ID | Probleme | Ferme le | Commit | Notes |
|----|----------|----------|--------|-------|
| C-001 | `frontend/lib/api.ts` n'existe pas | 18/02 | `3c6e009` | Cree frontend/lib/api/{client,index,promesse}.ts |
| C-004 | URLs hardcodees dans 6 fichiers frontend | 18/02 | `3c6e009` | Centralise dans frontend/lib/config.ts |
| C-005 | Bug URL Modal dans route.ts | 18/02 | `3c6e009` | notaire-ai → notomai |
| C-006 | Types incorrects ChatWithViager.tsx | 18/02 | `3c6e009` | .texte→.question, .help→.aide |
| C-007 | Typage ViagerBadge.tsx SousType index | 18/02 | `3c6e009` | BadgeColor union type |
| C-008 | .gitignore bloque frontend/lib/ | 18/02 | `3c6e009` | Ajout !frontend/lib/ |
| C-009 | SSE ne peut pas s'authentifier | 18/02 | `3c6e009` | API key en query param dans verify_api_key() |
| AUDIT-001 | Audit affirme endpoints /workflow/* absents | 18/02 | `9bacf0f` | ERREUR — existent L1891-2296, erratum ajoute |
| C-002 | UUIDs hardcodes dans chat_handler.py | 18/02 | `9e19166` | Augustin — suppression UUIDs, auth dynamique |
| I-001 | 13 vues SECURITY_DEFINER | 18/02 | `9e19166` | Augustin — toutes passees en SECURITY_INVOKER |
| I-002 | api_costs_tracking sans RLS | 18/02 | `9e19166` | Augustin — RLS activee + 25 policies |
| I-003 | 8 fonctions search_path mutable | 18/02 | `9e19166` | Augustin — SET search_path ajoute |
| I-005 | Pas de registre des traitements | 18/02 | `9e19166` | Augustin — registre mis a jour |
| I-006 | Cle dev par defaut signed_urls.py | 18/02 | `9e19166` | Augustin — cle par defaut supprimee |

---

## Conventions

- **C-xxx** : Critique (bloquant)
- **I-xxx** : Important (non-bloquant mais a corriger)
- **M-xxx** : Moyen (amelioration)
- **AUDIT-xxx** : Erreur d'audit
