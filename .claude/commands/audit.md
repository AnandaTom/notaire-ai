---
description: Audit complet du code — architecture, securite, fiabilite, optimisation, fluidite. Commence TOUJOURS par lire memory/.
argument-hint: [scope optionnel: "full", "frontend", "backend", "security", "axe N"]
---

# Audit Code Complet - Notomai

Tu es un auditeur de code rigoureux. Tu ne devines JAMAIS — tu verifies.

## Regles absolues

1. **LIRE `memory/` EN PREMIER** — avant toute analyse :
   - `memory/AUDIT_HISTORY.md` → scores historiques + ce que les audits precedents ont rate
   - `memory/CODE_MAP.md` → taille et contenu de chaque fichier
   - `memory/ISSUES.md` → ce qui est deja connu/corrige (eviter les doublons)
   - `memory/JOURNAL.md` → ce qui a ete fait recemment

2. **Ne JAMAIS affirmer qu'un fichier/endpoint/fonction n'existe pas sans `grep`.**
   Si un fichier fait > 500 lignes, tu DOIS grep les patterns, pas lire sequentiellement.

3. **Chaque affirmation doit avoir une preuve** : numero de ligne, resultat de grep, ou citation exacte.

4. **Chaque probleme doit etre actionnable** : fichier:ligne + qui le corrige + effort estime.

5. **Ne pas redeclarer une issue deja dans ISSUES.md** — la mentionner par son ID seulement.

## Scope

Argument recu : `$ARGUMENTS`

- Si vide ou "full" → audit complet (5 dimensions)
- Si "frontend" → dim 2 + 5 seulement
- Si "backend" → dim 1 + 2 + 4 seulement
- Si "security" → dim 3 seulement (+ scan grep credentials)
- Si "axe N" → focus sur l'axe N du PLAN_10_AXES.md

---

## Workflow

### Phase 0 : Charger le contexte (OBLIGATOIRE, tout en parallele)

```
Lire simultanement :
- memory/AUDIT_HISTORY.md   → score precedent, tendances, ce qui a ete rate
- memory/CODE_MAP.md        → structure fichiers
- memory/ISSUES.md          → issues ouvertes (ne pas les redeclarer)
- memory/JOURNAL.md         → commits recents (qui a touche quoi)
```

Puis :
```bash
# Commits recents tous devs
git log --oneline --all --since="3 days ago" | head -30

# Fichiers modifies recemment
git diff --name-only HEAD~5..HEAD
```

**Avant d'analyser : noter le score precedent depuis AUDIT_HISTORY.md pour calculer le delta.**

---

### Phase 1 : Scan technique rapide (tout en parallele)

```bash
# 1. LOC fichiers cles — detecter les fichiers qui ont grossi
wc -l api/main.py api/agents.py execution/chat_handler.py execution/agent_autonome.py frontend/stores/workflowStore.ts frontend/components/workflow/WorkflowPage.tsx

# 2. Build frontend — bloquant si echec
cd frontend && npx next build 2>&1 | tail -20

# 3. Tests backend
python -m pytest tests/ -q --tb=no 2>&1 | tail -5

# 4. Secrets dans le code (hors .env et node_modules)
grep -rn "eyJ\|supabase.*anon\|api_key\s*=\s*['\"]sk\|ghp_\|nai_" \
  --include="*.ts" --include="*.tsx" --include="*.py" --include="*.js" \
  --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=__pycache__ | head -20

# 5. Legacy files suspects (hors frontend/app/ et frontend/components/)
ls frontend/assets/ frontend/public/assets/ frontend/pages/ web/ 2>/dev/null | head -20

# 6. lib/api.ts shadow bug
ls frontend/lib/api.ts 2>/dev/null && echo "SHADOW BUG PRESENT" || echo "OK"

# 7. Dead code Python
python -c "
import os, ast, sys
used = set()
defined = set()
for root, dirs, files in os.walk('execution'):
    dirs[:] = [d for d in dirs if d != '__pycache__']
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                src = open(path).read()
                if 'import' in src:
                    used.add(path)
                defined.add(path)
            except: pass
never_imported = [f for f in defined if f not in used and 'test' not in f and '__init__' not in f]
print(f'{len(never_imported)} fichiers potentiellement non importes')
" 2>/dev/null
```

---

### Phase 2 : Analyse par dimension

Pour chaque dimension : **Score /10 | Points positifs (preuve) | Problemes (fichier:ligne) | Owner | Effort**

---

#### DIMENSION 1 : ARCHITECTURE (7.5 ref)

Checks prioritaires (par ordre d'importance) :
- [ ] Separation 3 couches respectee (directives / orchestration / execution)
- [ ] Fichiers > 1500 lignes → candidats refactoring (grep dans CODE_MAP)
- [ ] Imports circulaires Python (`grep -r "from execution" execution/ | grep -v __pycache__`)
- [ ] Coherence endpoints API (tous suivent le meme pattern auth + error handling ?)
- [ ] Dead code Python — fichiers dans `execution/` jamais importes dans api/

**Notomai-specific :**
- [ ] `lib/api.ts` n'existe PAS (shadow bug si present)
- [ ] Templates Jinja2 sans logique metier (pas de `{% if %}` complexes avec business rules)
- [ ] `execution/` sous-dossiers bien utilises (core/, gestionnaires/, services/, etc.)

---

#### DIMENSION 2 : OPTIMISATION (6.5 ref)

Checks prioritaires :
- [ ] Bundle frontend : taille First Load JS par page (next build output — cible < 150KB)
- [ ] Re-renders Zustand : selectors atomiques ou store entier consomme ?
- [ ] N+1 queries : boucles avec `supabase.from().select()` individuel ?
- [ ] Cache cadastre actif (CadastreService TTL 24h)
- [ ] SSE streaming : pas de buffering (response.body.getReader() direct)
- [ ] Cold starts Modal : `min_containers` configure ?

---

#### DIMENSION 3 : SECURITE (7.0 ref)

Checks prioritaires :
- [ ] **Legacy files** : `web/`, `frontend/public/assets/`, `frontend/assets/`, `frontend/pages/` — clés hardcodees ?
- [ ] **Supabase anon key** : grep `eyJ` dans tous les .ts/.js/.html (hors .env)
- [ ] RLS active sur toutes les tables (advisor MCP si disponible)
- [ ] Headers securite Next.js (`next.config.js` → `headers()`)
- [ ] Rate limiting API (X-RateLimit headers dans api/main.py ?)
- [ ] CORS config (origines autorisees bien restreintes ?)

**Issues deja connues (ne pas redeclarer) :** C-011b, I-004, M-007, M-011

---

#### DIMENSION 4 : FIABILITE (7.5 ref)

Checks prioritaires :
- [ ] Tests qui passent : `pytest -q --tb=no` → count failures
- [ ] Silent catches : `catch { }` ou `catch (e) {}` sans log ni user feedback
- [ ] Timeouts sur toutes les requetes externes (Anthropic=120s, Supabase=30s)
- [ ] Retry logic sur operations critiques (generation DOCX, appel Claude)
- [ ] Validation frontend : erreurs visibles a l'utilisateur (pas juste console.error)
- [ ] Workflow recovery : `beforeunload` + `saveDraft()` branche ?

**Issues deja connues :** M-018 (7 tests ENCRYPTION_MASTER_KEY)

---

#### DIMENSION 5 : FLUIDITE UX (8.0 ref)

Checks prioritaires :
- [ ] **Accessibilite** : `aria-label`, `role`, `tabIndex` sur elements interactifs (grep dans frontend/components/)
- [ ] Loading states : toutes les actions async ont un spinner ou skeleton ?
- [ ] Responsive : classes `sm:` / `md:` / `lg:` presentes sur les composants principaux ?
- [ ] Navigation back : peut-on revenir en arriere sans perdre les donnees ?
- [ ] VALIDATING step : renderer present dans WorkflowPage ?
- [ ] Messages d'erreur : clairs pour un notaire non-technique ?

**Issues deja connues :** M-009 (aria=0%), M-017 (responsive minimal)

---

### Phase 3 : Cross-reference ISSUES.md

```
Pour chaque probleme trouve :
  → Deja dans ISSUES.md ? → Citer l'ID, ne pas redeclarer
  → Nouveau ? → Creer l'issue (C/I/M selon gravite)
  → Dans ISSUES.md mais corrige ? → Marquer ferme avec commit + date
```

---

### Phase 4 : Rapport final

Format obligatoire — **concis, actionnable, copiable** :

```markdown
# Audit Notomai — [DATE]

## Score Global : X.X/10 ([DELTA] vs audit precedent)

| Dimension | Score | Prev | Delta | Resume 1 ligne |
|-----------|-------|------|-------|----------------|
| Architecture | X/10 | X/10 | ↑↓→ | ... |
| Optimisation | X/10 | X/10 | ↑↓→ | ... |
| Securite | X/10 | X/10 | ↑↓→ | ... |
| Fiabilite | X/10 | X/10 | ↑↓→ | ... |
| Fluidite | X/10 | X/10 | ↑↓→ | ... |

## Actions immédiates (CRITIQUE)
| Issue | Fichier:Ligne | Impact | Owner | Effort |
|-------|--------------|--------|-------|--------|
| C-xxx | ... | ... | Paul/Tom/Aug | 30min |

## Cette semaine (IMPORTANT)
| Issue | Fichier:Ligne | Impact | Owner | Effort |
|-------|--------------|--------|-------|--------|

## Backlog (MOYEN)
- M-xxx : description — owner — effort estimé

## Ce qui est bien fait
- [avec preuve fichier:ligne]

## Issues fermées ce cycle
- [ID] : description — commit

---

## Slack Summary (copier-coller)
```
📊 Audit [DATE] — X.X/10 ([DELTA])
🔴 CRITIQUE: [issue + owner]
🟡 IMPORTANT: [issue + owner]
✅ FERME: [issue]
Score: Archi X | Sécu X | Fiab X | Optim X | UX X
→ Prochain audit cible: X.X/10 si [condition]
```
```

---

### Phase 5 : Mettre a jour memory/

```
1. memory/ISSUES.md     → ajouter nouveaux problemes, fermer les resolus
2. memory/CODE_MAP.md   → si LOC changes ou nouveaux fichiers
3. memory/JOURNAL.md    → entree de session (score, delta, principales actions)
4. memory/AUDIT_HISTORY.md → OBLIGATOIRE : ajouter ligne de l'audit (voir format ci-dessous)
```

---

### Phase 6 : Retrospective (OBLIGATOIRE — amelioration continue)

**Apres chaque audit, repondre a ces 3 questions et les noter dans `memory/AUDIT_HISTORY.md` :**

1. **Ce que j'ai trouve que les audits precedents avaient rate** → mettre a jour les checks Phase 1/2
2. **Ce que cet audit a rate et qu'on a decouvert ensuite** → ajouter a `missed_issues`
3. **Ce qui a pris trop de temps** → peut-on le grepper/automatiser ?

**Format AUDIT_HISTORY.md :**
```
| DATE | SCORE | DELTA | TOP_ISSUE | FERMES | MISSED_ISSUES |
```

**Si tu trouves un pattern recurrent** (ex: legacy files resurrectes a chaque merge, shadow bug lib/api.ts) :
→ Ajouter le check en Phase 1 SCAN TECHNIQUE avec le grep exact
→ Mettre a jour ce fichier audit.md directement

L'audit s'ameliore a chaque iteration. Chaque audit doit etre plus rapide et plus precis que le precedent.

---

### Phase 7 : Boucle auto-renforçante (OBLIGATOIRE apres implementation)

**Cette phase s'execute apres que le dev a implemente les fixes identifies par l'audit.**

```
/audit → identifies issues → dev fixes code → /review → fix CRITICAL/MODERATE → /document → commit → prochain /audit
```

**A la fin du rapport (Phase 4), TOUJOURS rappeler cette boucle :**

```markdown
## Boucle obligatoire apres implementation

Une fois tes taches implementees :
1. `/review` — spawne `superpowers:code-reviewer`, revue 2 passes (correctness + effectiveness)
2. Corriger tous les CRITICAL et MODERATE trouves
3. `/document` — spawne `general-purpose` documenter, sync docstrings + directives + memory/
4. Committer → puis relancer `/audit` pour mesurer la progression

Sans /review et /document : le prochain audit trouvera les memes problemes.
```

**Pourquoi cette boucle est critique :**
- `/review` charge avec zero contexte → yeux frais → catches les bugs que l'auteur manque
- `/document` garde les docs en sync → le prochain audit lit des docs a jour → moins de faux positifs
- Le prochain `/audit` lit AUDIT_HISTORY.md → compare avec ce cycle → mesure la progression reelle

**Si le dev a deja utilise /review + /document dans sa session :** verifier dans JOURNAL.md et mentionner que la boucle a ete completee.

**Ce que cette boucle evite :**
- Issues qui persistent d'audit en audit (pas de feedback loop)
- Documentation desynchro (audit lit des docs obsoletes → faux scores)
- Regressions silencieuses (code non-revue merge dans main)
