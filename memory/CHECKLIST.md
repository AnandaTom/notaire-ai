# Checklist de Verification — Claude

> Ce fichier existe parce que j'ai fait une erreur critique le 18/02/2026 :
> j'ai affirme que des endpoints n'existaient pas alors qu'ils etaient dans
> un fichier de 2887 lignes que je n'avais lu qu'en partie.
>
> REGLE : ne jamais affirmer qu'un truc n'existe pas sans preuve negative.

---

## Avant d'affirmer qu'un endpoint/fonction/fichier N'EXISTE PAS

1. [ ] **Grep le pattern** dans tout le projet
   ```bash
   grep -rn "pattern" --include="*.py" .
   grep -rn "pattern" --include="*.ts" .
   ```

2. [ ] **Verifier la taille du fichier** — si > 500 lignes, ne PAS lire sequentiellement
   ```bash
   wc -l fichier
   ```

3. [ ] **Grep dans le fichier specifique** pour le pattern exact
   ```bash
   grep -n "@app\.\|router\.\|def \|export " fichier
   ```

4. [ ] **Consulter `memory/CODE_MAP.md`** avant toute affirmation

5. [ ] **Si le fichier fait > 1000 lignes** : lire par sections avec offset/limit, pas tout d'un coup

---

## Avant de modifier un fichier

1. [ ] **Lire le fichier ENTIER** d'abord (ou au moins grep les zones pertinentes)
2. [ ] **Verifier les imports** — qui importe ce fichier ? Quels impacts ?
   ```bash
   grep -rn "import.*nom_fichier" --include="*.ts" --include="*.py" .
   ```
3. [ ] **Verifier le .gitignore** — le fichier sera-t-il commite ?
4. [ ] **Verifier les types** — si TypeScript, les types correspondent-ils ?

---

## Apres avoir modifie du code (OBLIGATOIRE)

1. [ ] **`/review`** — Lancer le reviewer sub-agent (correctness + effectiveness)
2. [ ] **Corriger** les issues CRITICAL et MODERATE identifiees
3. [ ] **Re-review** si des corrections ont ete faites
4. [ ] **`/document`** — Lancer le documenter sub-agent (scripts + directives + memory/)
5. [ ] **Verifier** que memory/JOURNAL.md a ete mis a jour

## Avant de commiter

1. [ ] **`/review` et `/document` ont ete executes** (voir section ci-dessus)
2. [ ] **`next build`** passe (si frontend modifie)
3. [ ] **`git diff --stat`** — verifier qu'on ne commite que ce qu'on veut
4. [ ] **Pas de secrets** dans le diff (API keys, passwords, tokens)
5. [ ] **Message de commit** clair et descriptif pour que les autres Claude comprennent

---

## Avant un audit / affirmation sur l'etat du code

1. [ ] **Lister TOUS les endpoints** : `grep -n "@app\.\|@router\." api/main.py`
2. [ ] **Compter les lignes** : `wc -l` sur chaque fichier cle
3. [ ] **Verifier les routers inclus** : `grep -n "include_router" api/main.py`
4. [ ] **Cross-reference** : ce que le frontend appelle vs ce que le backend expose
5. [ ] **Ne PAS copier-coller** des affirmations d'une session precedente sans verifier

---

## Fichiers > 1000 lignes (attention particuliere)

| Fichier | LOC | Piege |
|---------|-----|-------|
| `api/main.py` | 2887 | Les endpoints workflow sont a L1891+, pas au debut |
| `execution/agent_autonome.py` | 3142 | Contient aussi CollecteurInteractif et ParseurDemandeNL |
| `execution/gestionnaires/gestionnaire_promesses.py` | 1695 | Contient detecter_type() + generer() + valider() |
| `execution/chat_handler.py` | 1237 | Les UUIDs hardcodes sont a L755-756 |
| `execution/anthropic_agent.py` | 820 | Wrapper Claude avec streaming |

---

## Patterns de mismatch connus (frontend ↔ backend)

| Frontend envoie | Backend attend | Ou est le mapping |
|----------------|----------------|-------------------|
| `type_acte: 'promesse_vente'` | `categorie_bien: 'copropriete'` | `api/index.ts:startWorkflow()` |
| attend `{id, titre}` | retourne `{key, title}` | `api/index.ts:startWorkflow()` |
| envoie `sectionId` | ignore (track interne) | `api/index.ts:submitAnswers()` |
| `X-API-Key` header | accepte aussi `?api_key=` query | `api/main.py:303` (pour SSE) |
