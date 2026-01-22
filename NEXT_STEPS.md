# Next Steps - Workflow Équipe NotaireAI

## ✅ Fait
- [x] Branche `tom/dev` créée et pushée

## 📋 À faire maintenant

### Étape 1 : Augustin et Payoss créent leurs branches

**Augustin** (augustinfrance-aico) :
```bash
git pull
git checkout -b augustin/dev
git push -u origin augustin/dev
```

**Payoss** (Payoss) :
```bash
git pull
git checkout -b payoss/dev
git push -u origin payoss/dev
```

### Étape 2 : Vérifier la configuration du repo (Admin)

```bash
# Vérifier que les branches existent
gh api repos/AnandaTom/notaire-ai/branches
```

### Étape 3 : Configurer les branch protection rules (optionnel mais recommandé)

Sur GitHub.com :
1. **Settings** → **Branches**
2. **Add rule** pour `master`
3. Cocher :
   - [x] Require pull request reviews before merging
   - [x] Require review from CODEOWNERS
   - [x] Require status checks to pass before merging
   - [x] Require branches to be up to date before merging
   - [x] Dismiss stale pull request approvals
   - [x] Include administrators

### Étape 4 : Créer un CODEOWNERS file

```bash
# Créer .github/CODEOWNERS
```

Contenu :
```
# Chaque dev review les PR de son domaine
* @AnandaTom @augustinfrance-aico @Payoss

# Templates
templates/ @AnandaTom
directives/ @AnandaTom

# Frontend
frontend/ @augustinfrance-aico

# Scripts Python
execution/ @Payoss
```

### Étape 5 : Daily workflow pour chaque dev

```bash
# Matin : récupérer master
git fetch origin
git merge origin/master

# Pendant le jour : commit et push sur sa branche
git add .
git commit -m "feat: description"
git push

# Fin de journée : créer une PR si feature terminée
gh pr create --title "Ma feature" --body "Description"
```

### Étape 6 : Review et merge

Quand une PR est créée :
1. Au moins 1 autre dev review
2. Approuve ou demande changements
3. Une fois approuvé → **Squash and merge**
4. Branche supprimée automatiquement

---

## 📊 État des branches

| Dev | Branche | Statut |
|-----|---------|--------|
| Tom | `tom/dev` | ✅ Créée |
| Augustin | `augustin/dev` | ❌ À créer |
| Payoss | `payoss/dev` | ❌ À créer |
| Production | `master` | ✅ Protégée |

---

## 🚀 Premier workflow

### Tom (vous)
```bash
# Vous êtes déjà sur tom/dev, c'est bon

# Faire des changements
echo "# Ma feature" >> test.txt

# Commit
git add .
git commit -m "feat: test workflow"

# Push
git push

# Créer une PR
gh pr create --title "Test workflow" --body "Mon premier PR"
```

### Augustin et Payoss
```bash
# Ils clonent/pullent
git pull

# Créent leurs branches
git checkout -b augustin/dev
git push -u origin augustin/dev

# Puis pareil que Tom
```

---

## ✅ Checklist avant de démarrer

- [ ] Augustin a créé `augustin/dev`
- [ ] Payoss a créé `payoss/dev`
- [ ] Branch protection rules configurées sur `master`
- [ ] `.github/CODEOWNERS` créé
- [ ] Chaque dev a auto-save activé (.vscode/settings.json)
- [ ] Chaque dev comprend le workflow GIT_WORKFLOW.md

---

## Commandes de survie

```bash
# Où suis-je ?
git branch

# Aller sur master
git checkout master

# Récupérer les dernières modifs
git fetch origin
git merge origin/master

# Voir mes branches
git branch -a

# Voir les PRs en cours
gh pr list

# Créer une PR
gh pr create

# Merger une PR (après review)
gh pr merge 1
```

---

## 🎯 Objectifs

- ✅ Zéro perte de données (chacun sa branche)
- ✅ Code quality (review obligatoire)
- ✅ Historique propre (squash merge)
- ✅ Master stable (tests auto + review)

Bonne chance ! 🚀
