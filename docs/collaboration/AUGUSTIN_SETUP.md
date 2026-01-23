# Setup Rapide pour Augustin

## 🎯 Vous n'avez pas auto_push.ps1 ? Voici comment l'obtenir

---

## ✅ Solution rapide (2 minutes)

### Étape 1 : Vérifier votre branche

```bash
git branch
# Devrait afficher : * augustin/dev
```

### Étape 2 : Récupérer master (qui contient auto_push.ps1)

```bash
# Récupérer les derniers changements
git fetch origin

# Fusionner master DANS votre branche
git merge origin/master
```

### Étape 3 : Vérifier que le fichier est là

```bash
# Windows
dir auto_push.ps1

# Ou dans l'explorateur de fichiers
# Vous devriez voir auto_push.ps1
```

### Étape 4 : Lancer auto-push

```bash
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"
```

---

## 🔧 Si vous avez des conflits

### Si `git merge origin/master` affiche des conflits

```bash
# 1. Résoudre les conflits dans VS Code
# Ouvrir les fichiers en conflit
# Choisir le bon code
# Sauvegarder

# 2. Marquer comme résolu
git add .

# 3. Finaliser le merge
git commit -m "merge: récupération de master"

# 4. Vérifier que auto_push.ps1 est là
dir auto_push.ps1
```

---

## 🚀 Workflow complet pour Augustin

```bash
# 1. Récupérer master
git fetch origin
git merge origin/master

# 2. Pousser votre branche mise à jour
git push origin augustin/dev

# 3. Lancer auto-push
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"

# 4. Continuer à travailler normalement
# Auto-push fait le reste !
```

---

## 📋 Checklist

- [ ] `git fetch origin`
- [ ] `git merge origin/master`
- [ ] Vérifier que `auto_push.ps1` existe
- [ ] `.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"`
- [ ] Laisser la fenêtre PowerShell ouverte

---

## ✨ C'est tout !

Après ça, vous avez :
- ✅ auto_push.ps1
- ✅ Tous les autres fichiers de l'équipe
- ✅ Auto-push actif sur augustin/dev

**Vous êtes prêt ! 🚀**

---

## 💡 Pour Payoss aussi

Payoss doit faire exactement la même chose :

```bash
git fetch origin
git merge origin/master
git push origin payoss/dev
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "payoss/dev"
```
