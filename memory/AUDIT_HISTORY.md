# Audit History - Notomai

> Historique structuré de chaque audit. Permet de mesurer la progression, d'identifier les patterns récurrents et d'améliorer le skill d'audit.
> Mis à jour automatiquement à la fin de chaque /audit.

---

## Format

| DATE | SCORE | DELTA | ARCHI | OPTIM | SECU | FIAB | UX | TOP CRITIQUE | FERMEES | MISSED |
|------|-------|-------|-------|-------|------|------|----|-------------|---------|--------|

---

## Historique

| DATE | SCORE | DELTA | ARCHI | OPTIM | SECU | FIAB | UX | TOP CRITIQUE | FERMEES | MISSED |
|------|-------|-------|-------|-------|------|------|----|-------------|---------|--------|
| 2026-02-19 (nuit, v3) | 7.3 | +0.1 | 7.5 | 6.5 | 7.0 | 7.5 | 6.5 | C-011b (legacy keys ressuscitées) | I-010, M-010, I-008, I-017 | I-017 (déjà corrigé par Payoss dans merge — l'audit l'avait ouvert par erreur) |
| 2026-02-19 (nuit, v2) | 7.2 | +0.5 | 6.5 | 6.0 | 8.5 | 8.0 | 6.0 | C-011 (regression keys) | I-001..I-016 (branching) | C-011b non identifié comme regression merge |
| 2026-02-19 (v1) | 6.7 | base | 6.0 | 6.0 | 6.5 | 7.0 | 5.5 | 4 silent catches page.tsx | - | fetch() sans timeout, lib/api.ts shadow bug |

---

## Leçons apprises (améliorations audit)

### Pattern détecté : Shadow bug lib/api.ts
- **Découvert** : 19/02 v1 — `frontend/lib/api.ts` shadowe `frontend/lib/api/index.ts`
- **Fix** : Supprimer `lib/api.ts` si présent
- **Check ajouté en Phase 1** : `ls frontend/lib/api.ts 2>/dev/null && echo "SHADOW BUG"`

### Pattern détecté : Régression legacy files par merge "keep both sides"
- **Découvert** : 19/02 v2 — merge `c4be78d` a ressuscité 6 fichiers avec clés Supabase
- **Symptôme** : fichiers dans `web/`, `frontend/assets/`, `frontend/pages/` qui ne devraient pas exister
- **Check ajouté en Phase 1** : `ls frontend/assets/ frontend/public/assets/ frontend/pages/ web/`

### Pattern détecté : Zustand persist middleware incomplet
- **Découvert** : 19/02 v3 post-merge — Payoss a ajouté config persist en dehors du wrapper `persist()`
- **Symptôme** : orphaned `{name: 'notomai-workflow', ...}` après `}),`
- **Check à ajouter** : grep `persist.onFinishHydration` dans workflowStore si persist pas dans create()

### Pattern détecté : Issue ouverte par erreur (déjà corrigée)
- **Découvert** : 19/02 v3 — I-017 ouverte par l'audit mais Payoss l'avait déjà corrigée dans le même merge
- **Leçon** : TOUJOURS vérifier le renderer avec grep avant d'ouvrir une issue frontend
- **Check ajouté** : grep `step === 'VALIDATING'` dans WorkflowPage avant d'ouvrir I-017

---

## Retrospective par audit

### 2026-02-19 (nuit, v3) — Tom

**Ce que j'ai trouvé que les audits précédents avaient raté :**
- lib/api.ts shadow bug (découvert en Phase 0 build failure)
- Zustand persist config orpheline dans workflowStore.ts

**Ce que cet audit a raté (découvert ensuite) :**
- I-017 : l'audit a ouvert une issue sur le VALIDATING renderer qui existait déjà (Payoss l'avait ajouté dans le même merge). Règle : toujours grep avant d'ouvrir une issue sur un step manquant.

**Ce qui a pris trop de temps :**
- La Phase 1 scan tech prend ~5min car `next build` est bloquant (3 min)
- Solution : lancer le build en background pendant qu'on analyse le backend

**Améliorations intégrées dans audit.md :**
- [x] Check legacy files en Phase 1 scan
- [x] Check shadow bug lib/api.ts
- [x] Checks Notomai-spécifiques par dimension
- [x] Phase 6 retrospective obligatoire
- [x] Format rapport avec DELTA + Slack Summary

---

## Prochains audits

**Cible :** 8.5/10

**Conditions pour y arriver :**
- C-011b résolu (Paul) : +0.5 sur Sécurité (7.0 → 7.5)
- M-018 résolu (Augustin) : +0.3 sur Fiabilité (7.5 → 7.8)
- M-009 résolu (Tom) : +0.5 sur Fluidité (6.5 → 7.0)
- M-017 résolu (Tom) : +0.2 sur Fluidité

**Score projeté après sprint :** 8.0/10
