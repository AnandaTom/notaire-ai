# Manual Push & Merge Guide

## 🎯 Deux workflows différents

| Situation | Action |
|-----------|--------|
| **Vous avez une feature terminée** | Créer une PR → Merger sur master |
| **Vous voulez juste sauvegarder** | Push manuel (auto-push le fait aussi) |

---

## 📤 Push manuel (sauvegarder votre travail)

### Pas de PR, juste sauvegarder

```bash
# Vous êtes sur votre branche
git branch  # devrait montrer * tom/dev

# Vérifier ce que vous avez changé
git status

# Ajouter tous les changements
git add .

# Committer avec un message clair
git commit -m "feat: ajout clause hypothèque"

# Pousser sur votre branche
git push origin tom/dev
```

### Nommage des commits (recommandé)

```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: documentation
refactor: refactorisation
test: ajout de tests
chore: maintenance
```

Exemples :
```
feat: ajout clause hypothèque conditionnelle
fix: correction export DOCX avec tableaux
docs: mise à jour guide collaboration
```

---

## 🔀 Pull Request & Merge sur master

### Workflow complet

```
1. Feature terminée sur tom/dev
   ↓
2. Créer une PR (tom/dev → master)
   ↓
3. Augustin ou Payoss review
   ↓
4. Approuvé → Squash and merge
   ↓
5. tom/dev est fusionné dans master ✅
   ↓
6. Mettre à jour votre branche locale
```

---

## 📋 Créer une Pull Request

### Option A : Via GitHub CLI (recommandé)

```bash
# Vous êtes sur tom/dev
# Assurez-vous d'avoir pushé vos changements

git push origin tom/dev

# Créer la PR
gh pr create \
  --title "Ajout clause hypothèque" \
  --body "Description courte de ce que j'ai ajouté"
```

### Option B : Via GitHub.com (plus graphique)

1. Allez sur https://github.com/AnandaTom/notaire-ai
2. **Pull requests** (onglet en haut)
3. **New pull request**
4. Base: `master`, Compare: `tom/dev`
5. **Create pull request**
6. Remplissez titre et description

### Option C : À partir du message GitHub CLI lors du push

Quand vous pushez, GitHub affiche un lien :

```
remote:
remote: Create a pull request for 'tom/dev' on GitHub by visiting:
remote: https://github.com/AnandaTom/notaire-ai/pull/new/tom/dev
```

Cliquez simplement sur ce lien !

---

## 👀 Review (pour les autres devs)

### Tom, Augustin ou Payoss reçoit une notification

1. Allez sur la PR
2. Lisez les changements (**Files changed**)
3. Cliquez **Review changes**
4. Approuvez ou demandez changements :
   ```
   - ✅ Approve (le code est bon)
   - 💬 Comment (poser une question)
   - ❌ Request changes (à corriger)
   ```

---

## ✅ Approuver et Merger

### Une fois approuvée

1. Allez sur la PR
2. Cliquez **Squash and merge** ← IMPORTANT
3. Cliquez **Confirm squash and merge**
4. La branche est fusionnée dans master 🎉

**Squash and merge** = tous vos commits deviennent 1 seul commit. Plus propre !

### Via GitHub CLI

```bash
# Lister les PRs ouvertes
gh pr list

# Merger une PR (ex: PR #1)
gh pr merge 1

# Choisir "Squash and merge"
```

---

## 🔄 Mettre à jour votre branche après merge

Après que votre PR a été mergée :

```bash
# Allez sur master
git checkout master

# Récupérez les derniers changements
git pull origin master

# Retournez sur votre branche
git checkout tom/dev

# Fusionnez master dans votre branche
git merge origin/master

# Poussez
git push origin tom/dev
```

**Ou en une ligne :**

```bash
git fetch origin && git checkout tom/dev && git merge origin/master && git push
```

---

## 🎯 Cas pratiques

### Cas 1 : Vous avez terminé une feature

```bash
# 1. Assurez-vous d'être sur votre branche
git branch  # * tom/dev

# 2. Vérifier vos changements
git diff

# 3. Commit
git add .
git commit -m "feat: ma super feature"

# 4. Push
git push origin tom/dev

# 5. Créer une PR
gh pr create --title "Ma feature" --body "Description"

# 6. Attendre la review

# 7. Une fois approuvée, merger
gh pr merge 1  # ou cliquer sur GitHub

# 8. Mettre à jour votre branche
git fetch origin
git merge origin/master
git push
```

### Cas 2 : Vous avez un conflit

```bash
# Pendant un merge
CONFLICT (content): Merge conflict in fichier.txt

# 1. Ouvrir le fichier et résoudre (chercher <<<<<<)
# 2. git add fichier.txt
# 3. git commit -m "resolve: merge conflict"
# 4. git push
```

### Cas 3 : Vous voulez annuler un push

```bash
# Annuler le dernier commit (en local seulement)
git reset HEAD~1

# Ou revenir à un commit spécifique
git reset <commit-hash>
```

---

## 📊 Commandes utiles

```bash
# Voir votre branche
git branch

# Voir l'historique
git log --oneline -5

# Voir les PRs
gh pr list

# Créer une PR
gh pr create

# Merger une PR
gh pr merge 1

# Voir les diffs
git diff

# Voir le statut
git status
```

---

## 🚨 Règles importantes

### À FAIRE ✅
- [ ] Commit avec messages clairs
- [ ] Push sur votre branche (tom/dev, augustin/dev, etc.)
- [ ] Créer une PR pour merger dans master
- [ ] Laisser un autre dev review
- [ ] Utiliser "Squash and merge"

### À NE PAS FAIRE ❌
- [ ] Push directement sur master
- [ ] Merger sans review
- [ ] Commits géants avec 50 fichiers
- [ ] Messages de commit vagues ("fix" ou "update")

---

## 🎓 Résumé du workflow

```
Vous                          GitHub
──────                        ──────

Travail
  ↓
git commit
  ↓
git push origin tom/dev  ──→  Branche tom/dev
  ↓
gh pr create             ──→  Pull Request
  ↓
[Attendre review]
  ↓
[Approuvé]
  ↓
Squash and merge         ──→  master
  ↓
git fetch && git merge   ←──  Récupérer master
  ↓
git push                 ──→  Mettre à jour tom/dev
```

---

## 💡 Tips

1. **Push souvent** : Toutes les heures ou après une feature
2. **PRs petites** : Une feature = une PR (plus facile à review)
3. **Messages clairs** : Quelqu'un devra lire votre commit dans 6 mois
4. **Review entre vous** : Tom review Augustin, Augustin review Payoss, Payoss review Tom

---

## ✨ Bienvenue au workflow professionnel ! 🚀
