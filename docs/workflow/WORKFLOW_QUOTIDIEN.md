# Workflow Quotidien - NotaireAI

## 🎯 Pour chaque développeur

---

## 📅 MATIN (Début de journée)

### 1. Ouvrir VS Code et le terminal

```bash
cd "chemin/vers/notaire-ai"
```

### 2. Récupérer les derniers changements de master

```bash
# Télécharger les changements
git fetch origin

# Vérifier votre branche actuelle
git branch  # Devrait afficher * tom/dev (ou augustin/dev, payoss/dev)

# Fusionner master DANS votre branche
git merge origin/master

# Si conflits → les résoudre (voir section Conflits)
# Si pas de conflits → continuer
```

### 3. Pousser votre branche mise à jour

```bash
git push origin tom/dev
```

### 4. Lancer auto-push (optionnel mais recommandé)

```bash
# Tom
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "tom/dev"

# Augustin
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"

# Payoss
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "payoss/dev"
```

---

## 💻 PENDANT LE TRAVAIL (Journée)

### Workflow automatique (avec auto-push activé)

```
Vous : Travaillez normalement
       ↓
Auto-Save : Sauvegarde fichiers (1 sec)
       ↓
Auto-Push : Commit + Push automatique (toutes les 30 min)
       ↓
GitHub : Votre branche est sauvegardée ✅
```

**Rien à faire, c'est automatique !**

### Workflow manuel (si vous préférez contrôler)

```bash
# Après chaque feature ou toutes les heures
git add .
git commit -m "feat: description de ce que j'ai fait"
git push origin tom/dev
```

---

## 🔄 FEATURE TERMINÉE (Prête pour master)

### 1. Dernière sauvegarde

```bash
# S'assurer que tout est sauvegardé
git add .
git commit -m "feat: ma feature complète"
git push origin tom/dev
```

### 2. Mettre à jour avec master (important !)

```bash
# Récupérer master
git fetch origin

# Fusionner master dans votre branche
git merge origin/master

# Résoudre conflits si nécessaire
# Puis push
git push origin tom/dev
```

### 3. Créer une Pull Request

```bash
# Via GitHub CLI (recommandé)
gh pr create \
  --title "Ajout clause hypothèque" \
  --body "Description de ce que j'ai ajouté. Tests passent."

# Ou via GitHub.com
# → Pull requests → New → tom/dev → master
```

### 4. Attendre la review

```
Un autre dev (Augustin ou Payoss) va :
1. Lire votre code
2. Tester si besoin
3. Approuver ou demander des changements
```

### 5. Merger sur master

```bash
# Une fois approuvée, merger
gh pr merge {numero}

# Choisir : Squash and merge
# Répondre "N" à "Delete branch"
```

---

## 🌙 FIN DE JOURNÉE

### 1. Dernière sauvegarde

```bash
git add .
git commit -m "chore: fin de journée - sauvegarde"
git push origin tom/dev
```

### 2. Créer une PR si feature prête (optionnel)

```bash
# Si votre feature est terminée
gh pr create --title "..." --body "..."
```

### 3. Arrêter auto-push (si lancé)

```
Ctrl+C dans la fenêtre PowerShell
```

---

## 📊 WORKFLOWS PAR DEV

### Tom

```bash
# Matin
git fetch origin && git merge origin/master && git push origin tom/dev
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "tom/dev"

# Pendant le jour
# → Auto-push fait le travail

# Feature prête
gh pr create --title "Ma feature" --body "Description"

# Après review
gh pr merge {numero}
```

### Augustin

```bash
# Matin
git fetch origin && git merge origin/master && git push origin augustin/dev
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"

# Pendant le jour
# → Auto-push fait le travail

# Feature prête
gh pr create --title "Ma feature" --body "Description"

# Après review
gh pr merge {numero}
```

### Payoss

```bash
# Matin
git fetch origin && git merge origin/master && git push origin payoss/dev
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "payoss/dev"

# Pendant le jour
# → Auto-push fait le travail

# Feature prête
gh pr create --title "Ma feature" --body "Description"

# Après review
gh pr merge {numero}
```

---

## 🔧 RÉSOLUTION DE CONFLITS

### Si `git merge origin/master` affiche un conflit

```bash
# 1. Git affiche
CONFLICT (content): Merge conflict in fichier.txt

# 2. Ouvrir le fichier en conflit
# Chercher les marqueurs :

<<<<<<< HEAD (votre code)
votre code ici
=======
code de master ici
>>>>>>> origin/master

# 3. Choisir le bon code (ou combiner)
# Supprimer les marqueurs <<<<, ====, >>>>

# 4. Sauvegarder et marquer comme résolu
git add fichier.txt

# 5. Finaliser le merge
git commit -m "resolve: merge conflict with master"

# 6. Pousser
git push origin tom/dev
```

---

## 📋 CHECKLIST QUOTIDIENNE

### ✅ Début de journée
- [ ] `git fetch origin`
- [ ] `git merge origin/master`
- [ ] `git push origin tom/dev`
- [ ] Lancer auto-push

### ✅ Pendant le travail
- [ ] Auto-push tourne en arrière-plan
- [ ] OU commits manuels réguliers

### ✅ Feature prête
- [ ] `git merge origin/master` (mettre à jour)
- [ ] `gh pr create` (créer PR)
- [ ] Attendre review

### ✅ Après review approuvée
- [ ] `gh pr merge` (Squash and merge)
- [ ] `git fetch origin && git merge origin/master` (récupérer master)

### ✅ Fin de journée
- [ ] Dernier commit + push
- [ ] Arrêter auto-push (Ctrl+C)

---

## 🎯 RÈGLES D'OR

```
1. JAMAIS push directement sur master
2. TOUJOURS push sur votre branche (tom/dev)
3. Créer une PR pour demander merge sur master
4. Attendre l'approbation d'un autre dev
5. Utiliser "Squash and merge" uniquement
6. Mettre à jour votre branche après merge
```

---

## 🚀 COMMANDES RAPIDES

### Routine du matin (une ligne)
```bash
git fetch origin && git merge origin/master && git push origin tom/dev
```

### Sauvegarder votre travail (une ligne)
```bash
git add . && git commit -m "feat: description" && git push origin tom/dev
```

### Créer une PR
```bash
gh pr create --title "Ma feature" --body "Description"
```

### Merger une PR
```bash
gh pr merge {numero}
```

---

## 📊 VISUALISATION

```
VOUS (tom/dev)              GITHUB              MASTER
─────────────               ──────              ──────

Matin :
  fetch + merge  ←────────  master
       ↓
  Travail + commits
       ↓
  push  ─────────────────→  tom/dev

Feature prête :
  PR create  ────────────→  Pull Request
       ↓                         ↓
  Attendre review         Review par autre dev
       ↓                         ↓
  Approuvé                   Approved
       ↓                         ↓
  gh pr merge  ──────────→  Squash merge  ───→  master ✅

Après merge :
  fetch + merge  ←────────  master (avec votre code)
       ↓
  Continuer développement
```

---

## 💡 TIPS

1. **Auto-push** : Lancez-le le matin, oubliez-le jusqu'au soir
2. **PRs petites** : Une feature = une PR (plus facile à review)
3. **Reviews régulières** : Reviewez au moins 1 PR/jour des autres
4. **Communication** : Slack si vous modifiez un fichier sensible
5. **Conflits** : Évitez-les en mergant master régulièrement

---

## ✨ RÉSUMÉ EN 3 ÉTAPES

```
1. Matin → git fetch + git merge origin/master
2. Journée → Auto-push fait le travail
3. Feature prête → gh pr create → Review → Merge
```

**C'est tout ! Simple et efficace. 🚀**
