---
description: Audit complet du code — architecture, securite, fiabilite, optimisation, fluidite. Commence TOUJOURS par lire memory/.
argument-hint: [scope optionnel: "full", "frontend", "backend", "security", "axe 1", etc.]
---

# Audit Code Complet - Notomai

Tu es un auditeur de code rigoureux. Tu ne devines JAMAIS — tu verifies.

## Regles absolues

1. **LIRE `memory/` EN PREMIER** — avant toute analyse :
   - `memory/CODE_MAP.md` → pour connaitre la taille et le contenu de chaque fichier
   - `memory/CHECKLIST.md` → pour ne rien rater (grep obligatoire sur fichiers > 500 lignes)
   - `memory/ISSUES.md` → pour savoir ce qui est deja connu/corrige
   - `memory/JOURNAL.md` → pour savoir ce qui a ete fait recemment

2. **Ne JAMAIS affirmer qu'un fichier/endpoint/fonction n'existe pas sans `grep`.**
   Si un fichier fait > 500 lignes, tu DOIS grep les patterns, pas lire sequentiellement.

3. **Chaque affirmation doit avoir une preuve** : numero de ligne, resultat de grep, ou citation exacte.

## Scope

Argument recu : `$ARGUMENTS`

- Si vide ou "full" → audit complet (5 dimensions)
- Si "frontend" → focus frontend uniquement
- Si "backend" → focus backend uniquement
- Si "security" → focus securite uniquement
- Si "axe N" → focus sur l'axe N du PLAN_10_AXES.md

## Workflow

### Phase 0 : Charger le contexte (OBLIGATOIRE)

Lire en parallele :
- `memory/CODE_MAP.md`
- `memory/ISSUES.md`
- `memory/JOURNAL.md`
- `memory/CHECKLIST.md`

### Phase 1 : Scan technique

Executer en parallele :

```bash
# 1. Taille des fichiers cles
wc -l api/main.py api/agents.py execution/chat_handler.py execution/agent_autonome.py frontend/stores/workflowStore.ts

# 2. Tous les endpoints backend
grep -n "@app\.\|@router\." api/main.py api/agents.py

# 3. Imports frontend cassés
cd frontend && grep -rn "from.*@/lib\|import.*@/lib" --include="*.ts" --include="*.tsx" | head -30

# 4. Secrets/credentials dans le code
grep -rn "password\|secret\|api_key.*=.*['\"]" --include="*.ts" --include="*.tsx" --include="*.py" | grep -v node_modules | grep -v ".env" | grep -v "__pycache__" | head -20

# 5. Build status
cd frontend && npx next build 2>&1 | tail -15

# 6. Supabase advisors
# (via MCP si disponible)
```

### Phase 2 : Analyse par dimension

Analyser chacune des 5 dimensions ci-dessous. Pour chaque dimension :
- Score /10
- Points positifs (avec preuve)
- Problemes trouves (avec fichier:ligne)
- Recommandations concretes

---

#### DIMENSION 1 : ARCHITECTURE

Verifier :
- [ ] Separation 3 couches (Directives / Orchestration / Execution) respectee
- [ ] Pas de logique metier dans les templates Jinja2
- [ ] Pas de logique UI dans les stores
- [ ] Imports circulaires ? (`grep -rn "from.*import" | sort | uniq -d`)
- [ ] Fichiers > 1000 lignes → candidats au refactoring ?
- [ ] Code mort ? (fonctions/fichiers jamais importes)
- [ ] Coherence des patterns (est-ce que tous les endpoints suivent le meme style ?)

Questions a repondre :
1. Le code est-il bien organise ? Un nouveau dev peut-il s'y retrouver ?
2. Y a-t-il des abstractions inutiles ou manquantes ?
3. Les dependances sont-elles justifiees ?

---

#### DIMENSION 2 : OPTIMISATION

Verifier :
- [ ] Requetes N+1 (boucles avec fetch/query individuels)
- [ ] Donnees chargees inutilement (over-fetching)
- [ ] Cache utilise la ou ca compte (cadastre, questions, templates)
- [ ] Bundle frontend : taille de chaque page (`next build` output)
- [ ] Cold starts Modal (min_containers, timeout)
- [ ] Imports dynamiques / code splitting frontend
- [ ] Pas de re-renders React inutiles (stores Zustand bien decoupe ?)

Questions a repondre :
1. Ou sont les bottlenecks de performance ?
2. Qu'est-ce qui pourrait etre mis en cache et ne l'est pas ?
3. Le bundle frontend est-il raisonnable ?

---

#### DIMENSION 3 : SECURITE

Verifier :
- [ ] Secrets dans le code (`grep` passwords, api keys, tokens)
- [ ] Supabase RLS sur TOUTES les tables (utiliser `get_advisors` MCP si disponible)
- [ ] Vues SECURITY_DEFINER vs INVOKER
- [ ] Input sanitization (injection SQL, XSS, path traversal)
- [ ] Auth : JWT valide ? API key validee ? Rate limiting ?
- [ ] CORS configure correctement ?
- [ ] Headers securite (CSP, HSTS, X-Frame-Options)
- [ ] Fichiers sensibles dans .gitignore ?
- [ ] Dependencies avec CVE connus (`npm audit`, `pip audit`)

Questions a repondre :
1. Un attaquant peut-il acceder a des donnees d'une autre etude ?
2. Un utilisateur non-authentifie peut-il appeler des endpoints sensibles ?
3. Y a-t-il des secrets exposes dans le bundle client ?

---

#### DIMENSION 4 : FIABILITE

Verifier :
- [ ] Gestion d'erreurs : try/catch partout ou ca peut echouer ?
- [ ] Fallbacks : que se passe-t-il si Supabase est down ? Modal ? Claude API ?
- [ ] Timeouts configures sur toutes les requetes externes
- [ ] Retry logic sur les operations critiques
- [ ] Tests : combien ? Quel coverage ? Tests E2E ?
- [ ] Validation des donnees a chaque frontiere (user input, API response, DB query)
- [ ] Logs : suffisants pour debugger en prod ?
- [ ] Monitoring : alertes si erreur ?

Questions a repondre :
1. Si une API externe est down pendant 5 min, que se passe-t-il ?
2. Un notaire peut-il perdre des donnees en cours de saisie ?
3. Les erreurs sont-elles claires et actionnables pour le notaire ?

---

#### DIMENSION 5 : FLUIDITE (UX technique)

Verifier :
- [ ] SSE streaming fonctionne (pas de lag, pas de buffering)
- [ ] Loading states sur toutes les actions async
- [ ] Optimistic updates ou y a-t-il un "flash" apres chaque action ?
- [ ] Navigation : peut-on revenir en arriere sans perdre ses donnees ?
- [ ] Formulaires : validation temps reel ou seulement a la soumission ?
- [ ] Responsive : fonctionne sur tablette ?
- [ ] Accessibilite : aria-labels, focus management, contraste

Questions a repondre :
1. Un notaire peut-il completer un acte sans aucun moment de friction ?
2. Les temps de reponse sont-ils acceptables (< 2s pour chaque action) ?
3. L'experience est-elle coherente entre chat et workflow ?

---

### Phase 3 : Cross-reference avec les issues connues

Comparer les problemes trouves avec `memory/ISSUES.md` :
- Probleme deja connu → mentionner le ticket (ex: I-001)
- Probleme NOUVEAU → l'ajouter a ISSUES.md
- Probleme CORRIGE mais encore dans ISSUES.md → le fermer

### Phase 4 : Rapport final

Format obligatoire :

```markdown
# Audit Notomai — [DATE]

## Score Global : X/10

| Dimension | Score | Tendance | Resume |
|-----------|-------|----------|--------|
| Architecture | X/10 | ↑↓→ | ... |
| Optimisation | X/10 | ↑↓→ | ... |
| Securite | X/10 | ↑↓→ | ... |
| Fiabilite | X/10 | ↑↓→ | ... |
| Fluidite | X/10 | ↑↓→ | ... |

## Problemes critiques (action immediate)
1. [FICHIER:LIGNE] Description — impact — qui devrait corriger

## Problemes importants (cette semaine)
1. [FICHIER:LIGNE] Description — impact

## Ameliorations suggerees (backlog)
1. Description — benefice estime

## Ce qui est bien fait
1. ...

## Diff depuis dernier audit
- Issues fermees depuis : ...
- Nouveaux problemes : ...
- Tendance generale : amelioration / regression / stable
```

### Phase 5 : Mettre a jour memory/

- Ajouter les nouveaux problemes dans `memory/ISSUES.md`
- Fermer les problemes resolus
- Mettre a jour `memory/CODE_MAP.md` si des fichiers ont change
- Ajouter une entree dans `memory/JOURNAL.md`
