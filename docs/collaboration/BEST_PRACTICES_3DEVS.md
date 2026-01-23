# Meilleures Pratiques GitHub pour 3 Développeurs

## 🎯 Principes fondamentaux

```
1. Une branche = Une personne = Zéro conflit
2. Une PR = Une feature = Une review
3. Master = Production = Toujours stable
```

---

## 1️⃣ Organisation des branches

### Structure recommandée

```
master (production, protégé)
  ↓ PRs
tom/dev          (votre branche principale)
├─ tom/feat-x    (feature en cours)
├─ tom/fix-y     (bug en cours)

augustin/dev     (branche principale Augustin)
├─ augustin/feat-a
├─ augustin/fix-b

payoss/dev       (branche principale Payoss)
├─ payoss/feat-c
├─ payoss/fix-d
```

### Nommage des branches

```
{dev}/dev               - Branche principale de chacun
{dev}/feat-{nom}        - Nouvelle feature
{dev}/fix-{bug}         - Correction de bug
{dev}/docs-{sujet}      - Documentation
{dev}/refactor-{nom}    - Refactorisation
```

Exemples :
```
tom/feat-clause-hypotheque
augustin/fix-export-pdf
payoss/docs-workflow
```

---

## 2️⃣ Commits propres

### Format de commit recommandé

```
type: description courte (50 caractères max)

Description plus longue si nécessaire (optionnel)
- Point 1
- Point 2
```

### Types de commits

```
feat:     Nouvelle fonctionnalité
fix:      Correction de bug
docs:     Documentation
refactor: Refactorisation (pas de changement fonctionnel)
test:     Tests
chore:    Maintenance, dépendances
perf:     Optimisation de performance
style:    Formatage, pas de logique
```

### Exemples de bons commits

```
✅ feat: ajout clause hypothèque conditionnelle
✅ fix: correction export DOCX avec tableaux
✅ docs: mise à jour guide collaboration
✅ refactor: simplifier logique validation

❌ fix
❌ update
❌ wip (work in progress)
❌ asdf
```

---

## 3️⃣ Pull Requests (PRs)

### Quand créer une PR

- ✅ Feature terminée et testée
- ✅ Bug fixé et vérifié
- ✅ Documentation complétée
- ❌ Work in progress (utiliser les drafts)

### Taille idéale d'une PR

```
Petite PR   : 1-5 fichiers    (✅ Facile à review)
Moyenne PR  : 5-20 fichiers   (⚠️ Correcte)
Grande PR   : 20+ fichiers    (❌ Trop complexe)
```

**Règle d'or** : Une PR = une feature. Si c'est trop gros, split en plusieurs PRs.

### Template de PR

```markdown
## Description
Brève description de ce que j'ai fait.

## Type de changement
- [ ] Nouvelle feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation

## Checklist
- [ ] J'ai testé localement
- [ ] Les tests passent
- [ ] Pas de conflits
- [ ] Code formaté

## Screenshots (si applicable)
Ajouter des screenshots pour les changements UI.
```

### Créer une PR

```bash
# Via CLI (recommandé)
git push origin tom/feat-clause
gh pr create \
  --title "Ajout clause hypothèque" \
  --body "Ajoute une clause conditionnelle pour les hypothèques. Tous les tests passent."

# Ou via GitHub.com
# → Pull requests → New → tom/feat-clause → master
```

---

## 4️⃣ Reviews (approbation du code)

### Qui review qui ?

**Rotation recommandée :**

```
Tom         review  Augustin's PR
Augustin    review  Payoss's PR
Payoss      review  Tom's PR
```

**Jamais** : Auto-review (vous reviewez votre propre PR).

### Checklist de review

En lisant une PR, vérifier :

- [ ] Le code fait ce qu'il promet (titre + description)
- [ ] Pas d'erreurs évidentes
- [ ] Pas de code dupliqué
- [ ] Noms de variables clairs
- [ ] Tests ajoutés si nécessaire
- [ ] Documentation mise à jour
- [ ] Pas de secrets (API keys, passwords)
- [ ] Performance acceptable

### Approuver une PR

```bash
# Via GitHub.com ou CLI
gh pr review {numero} --approve

# Ou demander changements
gh pr review {numero} --request-changes
```

### Demander des changements

Soyez constructif :

```
❌ "C'est pas bon"
✅ "Je pense qu'on pourrait utiliser la fonction X ici pour éviter la duplication"

❌ "Pourquoi tu as fait ça ?"
✅ "Pourquoi avoir choisi cette approche plutôt que Y ?"
```

---

## 5️⃣ Merge sur master

### Avant de merger

```bash
# 1. S'assurer que tout est à jour
git fetch origin

# 2. Vérifier qu'il n'y a pas de conflits
git merge origin/master

# 3. Si conflits, les résoudre
# ... puis commit et push

# 4. Attendre que les tests passent (GitHub Actions)
```

### Merger

```bash
# Squash and merge OBLIGATOIRE
gh pr merge {numero}

# Choisir : Squash and merge
```

### Après le merge

```bash
# 1. Récupérer master
git fetch origin
git merge origin/master

# 2. Push votre branche
git push origin tom/dev

# 3. Continuer le développement ou créer nouvelle branche
git checkout -b tom/feat-nouvelle
```

---

## 6️⃣ Gestion des conflits

### Éviter les conflits

```
✅ Petites branches courtes (1-2 jours max)
✅ Merger régulièrement dans master
✅ Ne pas modifier les mêmes fichiers simultanément
✅ Communication : "Je travaille sur fichier X"

❌ Branches longues (1+ semaine)
❌ Laisser master diverger
❌ Modifier seul le même fichier à plusieurs
```

### Résoudre un conflit

```bash
# Pendant un merge
CONFLICT (content): Merge conflict in fichier.txt

# 1. Ouvrir le fichier et chercher les marqueurs
# <<<<<<<< tom/dev
#   votre code
# ========
#   code de master
# >>>>>>>> master

# 2. Garder le code qui vous intéresse
# 3. Supprimer les marqueurs

# 4. git add fichier.txt
# 5. git commit -m "resolve: merge conflict with master"
# 6. git push
```

---

## 7️⃣ Bonnes pratiques quotidiennes

### Matin : Récupérer les changements

```bash
git fetch origin
git merge origin/master
```

### Pendant la journée : Commits réguliers

```bash
# Toutes les heures ou après chaque feature
git add .
git commit -m "feat: description"
git push origin tom/dev
```

### Fin de journée : PR si feature terminée

```bash
# Si prêt à merger
gh pr create --title "..." --body "..."

# Sinon, just push (auto-push le fait aussi)
git push origin tom/dev
```

---

## 8️⃣ Communication sur GitHub

### Utiliser les Issues

```bash
# Signaler un bug
gh issue create --title "Bug: export DOCX échoue"

# Proposer une feature
gh issue create --title "Feature: support PDF"
```

### Commenter les PRs

```
Soyez bienveillant et constructif :

❌ "C'est dégueulasse"
✅ "Je suggère de refactoriser cette fonction pour la clarté"

❌ "Pourquoi tu as pas testé ?"
✅ "Pourrais-tu ajouter un test pour ce cas ?"
```

### Utiliser les mentions

```
@tom Can you review this PR?
Closes #5 (auto-close issue quand PR mergée)
Relates to #3 (lier sans fermer)
```

---

## 9️⃣ Outils pour 3 devs

### GitHub Actions (tests auto)

```yaml
# .github/workflows/test.yml
- Run on chaque push et PR
- Arrête le merge si tests échouent
```

### Branch protection rules

```
Settings → Branches → master
- [x] Require pull request reviews (1 approval)
- [x] Require status checks to pass
- [x] Require branches to be up to date
- [x] Dismiss stale reviews
- [x] Include administrators
```

### Code owners (qui review quoi)

```
# .github/CODEOWNERS
* @tom @augustin @payoss
templates/ @tom
execution/ @payoss
frontend/ @augustin
```

---

## 🔟 Checklist quotidienne

### Début de journée
- [ ] `git fetch origin`
- [ ] `git merge origin/master`
- [ ] Lancer auto-push script

### Pendant le travail
- [ ] Commits clairs et fréquents
- [ ] Push régulièrement
- [ ] Communiquer sur Slack si conflit attendu

### Fin de journée
- [ ] Terminer les commits
- [ ] Push final
- [ ] Créer PR si feature complète
- [ ] Review au moins 1 PR de quelqu'un d'autre

### Avant de merger
- [ ] PR approuvée par 1 autre dev
- [ ] Tests verts
- [ ] Pas de conflits
- [ ] Description claire

---

## 🎯 Résumé des règles d'or

```
1. Une branche par personne = zéro conflits
2. Une feature = une PR = une review
3. Master toujours stable
4. Commits petits et clairs
5. Reviews bienveillantes et constructives
6. Merges réguliers pour éviter les divergences
7. Communication sur GitHub
8. Auto-push pour zéro perte de données
9. Tests avant de merger
10. Apprentissage continu (relire le code des autres)
```

---

## 📊 État idéal de votre repo

```
master (1 commit par jour en moyenne)
  ↑ (PRs mergées)
tom/dev ──→ feature A ──PR──→ master
augustin/dev → feature B ──PR──→ master
payoss/dev → feature C ──PR──→ master
```

Chacun bosse de son côté, tout merge proprement sur master. ✨

---

## 💡 Tips avancés

### Rebase avant merge (optionnel)

```bash
# Avant de créer une PR, mettre à jour votre branche
git rebase origin/master

# Si conflits, les résoudre
git rebase --continue

# Force push (attention !)
git push origin tom/dev --force-with-lease
```

### Squash commits avant PR (optionnel)

```bash
# Si 10 petits commits de debug
git rebase -i origin/master

# Squash les commits non-essentiels
pick commit1
squash commit2
squash commit3
...
```

### Cherry-pick (si urgent)

```bash
# Prendre un commit d'une branche à l'autre
git cherry-pick <commit-hash>
```

---

## 🚀 Vous êtes prêts !

Suivez ces pratiques et votre repo restera **propre, stable et collaboratif**. 🎉

**Questions ? Slack ou GitHub issues.** 💪
