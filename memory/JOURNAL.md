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
