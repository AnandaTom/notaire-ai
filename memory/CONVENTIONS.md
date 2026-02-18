# Conventions - Notomai

> Regles de code, naming, workflow Git, et patterns a suivre.
> Mis a jour quand on decouvre un nouveau pattern ou qu'on en abandonne un.

---

## Git

- **Branches** : `payoss/dev`, `tom/dev`, `augustin/dev` → merge sur `master`
- **Commits** : `feat:`, `fix:`, `chore:`, `docs:` — message en anglais, body en francais OK
- **Push** : toujours push dev PUIS merge fast-forward sur master
- **Jamais** : force push sur master, amend de commits publies, --no-verify

## Frontend (Next.js 14 + TypeScript)

- **Imports** : `@/lib/config` pour API_URL, jamais de hardcode
- **Store** : Zustand, selectors individuels (`useWorkflowStore((s) => s.step)`)
- **API calls** : toujours via `frontend/lib/api/`, jamais de `fetch()` direct dans les composants
- **Types** : `frontend/types/workflow.ts` pour les types workflow, `frontend/types/index.ts` pour les types generaux
- **Composants** : `'use client'` en tete si interactif, pas de logique metier dans les composants
- **Erreurs** : `ApiError` class dans `api/client.ts`, messages en francais user-friendly
- **SSE** : via `apiSSE()` dans `api/client.ts`, API key en query param (EventSource limitation)

## Backend (Python FastAPI)

- **Fichier principal** : `api/main.py` (2887 lignes, 39 endpoints) — TOUJOURS grep avant d'affirmer
- **Auth** : `verify_api_key` dependency, 3 niveaux (read, write, delete)
- **Routers** : chat dans `chat_handler.py`, agents dans `api/agents.py`
- **Imports conditionnels** : les gestionnaires sont importes DANS les endpoints (pas au top-level) pour eviter les erreurs d'import Modal
- **Erreurs** : toujours HTTPException avec detail en francais

## Templates Jinja2

- **Variables** : toujours guardees avec `{% if var %}...{% endif %}`
- **Sections** : dans `templates/sections/`, incluses via `{% include %}`
- **Formatage DOCX** : NE JAMAIS modifier les valeurs dans `exporter_docx.py` (Times New Roman 11pt, marges G=60mm D=15mm)
- **Conformite** : minimum 80% pour passer en PROD

## Naming

- **Fichiers Python** : snake_case (`gestionnaire_promesses.py`)
- **Fichiers TS/TSX** : PascalCase pour composants (`WorkflowPage.tsx`), camelCase pour utils (`workflowStore.ts`)
- **Endpoints** : kebab-case en francais (`/promesses/detecter-type`)
- **Variables JSON** : snake_case (`categorie_bien`, `type_promesse`)

## Securite

- **Secrets** : JAMAIS dans le code, toujours via `.env` / `process.env`
- **Supabase** : RLS sur chaque table, vues en SECURITY_INVOKER
- **PII** : chiffrees via `encryption_service.py`, anonymisees avant envoi aux LLMs
- **URLs signees** : pour les telechargements DOCX, TTL court

## Equipe (3 devs)

| Dev | Focus | Branches |
|-----|-------|----------|
| Paul (Payoss) | Architecture, front-back, revue | `payoss/dev` |
| Tom | Frontend, UX, tests FE | `tom/dev` |
| Augustin | Backend, securite, infra, RGPD | `augustin/dev` |
