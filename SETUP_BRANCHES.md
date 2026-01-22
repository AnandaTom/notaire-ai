# Setup des branches - Augustin & Payoss

## 🎯 Objectif

Créer votre branche personnelle pour développer indépendamment.

---

## 📋 Étape 1 : Cloner le repo (première fois seulement)

Si vous n'avez pas encore le repo en local :

### Via PowerShell

```powershell
# Allez où vous voulez le dossier (ex: Documents)
cd Documents

# Clonez le repo
git clone https://github.com/AnandaTom/notaire-ai.git

# Entrez dans le dossier
cd notaire-ai
```

### Via GitHub Desktop (plus facile)

1. Ouvrez **GitHub Desktop**
2. **File** → **Clone repository**
3. Entrez `AnandaTom/notaire-ai`
4. Cliquez **Clone**

---

## 🌿 Étape 2 : Créer votre branche

### Pour Augustin (augustinfrance-aico)

```bash
# Récupérer les dernières modifs
git pull

# Créer votre branche de développement
git checkout -b augustin/dev

# Pousser la branche sur GitHub
git push -u origin augustin/dev
```

### Pour Payoss (Payoss)

```bash
# Récupérer les dernières modifs
git pull

# Créer votre branche de développement
git checkout -b payoss/dev

# Pousser la branche sur GitHub
git push -u origin payoss/dev
```

---

## ✅ Vérifier que ça a marché

```bash
# Voir la branche sur laquelle vous êtes
git branch

# Devrait afficher :
#   master
# * augustin/dev  (ou payoss/dev)
```

---

## 🚀 Étape 3 : Lancer l'auto-push

Une fois votre branche créée, lancez le script auto-push.

### Augustin

**Option A (double-cliquez) :**
```
Aller dans le dossier → START_AUTO_PUSH.bat
```

**Option B (PowerShell) :**
```powershell
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"
```

### Payoss

**Option A (double-cliquez) :**
Modifier `START_AUTO_PUSH.bat` d'abord :

Remplacer :
```batch
-BRANCH "tom/dev"
```

Par :
```batch
-BRANCH "payoss/dev"
```

Ensuite double-cliquez.

**Option B (PowerShell) :**
```powershell
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "payoss/dev"
```

---

## 📝 Résumé en 5 étapes

| Étape | Commande | Description |
|-------|----------|-------------|
| 1 | `git clone ...` | Cloner le repo (une fois) |
| 2 | `git pull` | Récupérer master |
| 3 | `git checkout -b augustin/dev` | Créer votre branche |
| 4 | `git push -u origin augustin/dev` | Pousser la branche |
| 5 | `.\auto_push.ps1 -BRANCH "augustin/dev"` | Lancer auto-push |

---

## ⚡ Raccourci (si déjà clonés)

Si vous avez déjà le repo mais pas créé votre branche :

```bash
# Aller dans le dossier
cd notaire-ai

# Récupérer les dernier changements
git pull

# Créer VOTRE branche
git checkout -b augustin/dev  # ou payoss/dev

# Pousser
git push -u origin augustin/dev

# Lancer auto-push
.\auto_push.ps1 -INTERVAL_MINUTES 30 -BRANCH "augustin/dev"
```

---

## 🎯 État final désiré

Quand vous avez fini, vous devriez voir :

```bash
$ git branch
  master
* augustin/dev   ← Vous êtes ici
```

Et sur GitHub, les branches devraient être :

```
master
tom/dev
augustin/dev   ← À créer
payoss/dev     ← À créer
```

---

## 🆘 Troubleshooting

### "fatal: 'origin' does not appear to be a 'git' repository"

Vous n'êtes pas dans le bon dossier. Vérifier :
```bash
cd notaire-ai
```

### "already exists on 'origin'"

Votre branche existe déjà. Simplement :
```bash
git checkout augustin/dev
```

### "Permission denied (publickey)"

Problème de credentials GitHub. Reconnectez-vous :
```bash
gh auth logout
gh auth login
```

---

## 📞 Questions ?

1. Lisez [AUTO_PUSH_GUIDE.md](AUTO_PUSH_GUIDE.md) pour comprendre l'auto-push
2. Lisez [GIT_WORKFLOW.md](GIT_WORKFLOW.md) pour le workflow complet
3. Demandez à Tom si vous avez d'autres questions

---

## 🎉 Prêt !

Dès que vous avez créé votre branche et lancé l'auto-push, vous êtes **100% prêt** à développer en toute sérénité.

**Bienvenue dans le workflow automatisé ! 🚀**
