# Troubleshooting - NotaireAI

Guide de résolution des problèmes courants.

---

## 🚨 Erreur: "You have not concluded your merge (MERGE_HEAD exists)"

### Symptômes
```
fatal: You have not concluded your merge (MERGE_HEAD exists).
Please, commit your changes before you merge.
```

### Cause
Un merge précédent a été commencé mais pas finalisé (commit manquant).

### Solution

#### Étape 1: Vérifier l'état
```bash
git status
```

Lisez attentivement ce qui s'affiche. Vous verrez une de ces situations:

---

#### Situation A: "All conflicts fixed but you are still merging"
```
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)
```

**Solution**: Finaliser le merge
```bash
git add .
git commit -m "merge: sync with master"
```

---

#### Situation B: "You have unmerged paths"
```
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   .env.template
        both modified:   execution/assembler_acte.py
```

**Solution**: Résoudre les conflits
```bash
# 1. Ouvrir le fichier en conflit dans VS Code
code .env.template

# 2. Chercher les marqueurs de conflit:
#    <<<<<<< HEAD
#    votre version
#    =======
#    version de master
#    >>>>>>> origin/master

# 3. Choisir quelle version garder (ou combiner)
#    Supprimer les marqueurs <<<<<<<, =======, >>>>>>>

# 4. Sauvegarder (Ctrl+S)

# 5. Marquer comme résolu
git add .env.template

# 6. Répéter pour chaque fichier en conflit

# 7. Finaliser le merge
git commit -m "merge: resolve conflicts with master"
```

---

#### Situation C: "Changes not staged for commit"
```
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
        modified:   execution/exporter_docx.py
```

**Solution**: Stager et commiter
```bash
git add .
git commit -m "merge: sync with master"
```

---

#### Situation D: "Rien à merger" mais MERGE_HEAD existe quand même

**Solution**: Annuler et recommencer
```bash
# Annuler le merge en cours
git merge --abort

# Recommencer proprement
git fetch origin master
git merge origin/master
```

---

## 🚨 Erreur: "morning_sync.ps1 n'existe pas"

### Symptômes
```
L'argument « .\morning_sync.ps1 » du paramètre -File n'existe pas.
```

### Cause
Votre branche a été créée avant que les scripts soient ajoutés sur master.

### Solution
```bash
# Récupérer les dernières modifs de master
git fetch origin master

# Fusionner master dans votre branche
git merge origin/master

# Vérifier que vous avez les fichiers
ls *.bat
ls *.ps1
```

Vous devriez voir:
- `START_DAY_XXX.bat` ✅
- `END_DAY.bat` ✅
- `auto_sync_v2.ps1` ✅
- `morning_sync.ps1` ✅

---

## 🚨 Erreur: "Access denied" ou "Unauthorized"

### Symptômes
```
fatal: Authentication failed
```
ou
```
remote: Permission denied
```

### Cause
Git n'a pas les bonnes credentials pour GitHub.

### Solution

#### Option 1: Utiliser GitHub CLI (recommandé)
```bash
# Se connecter à GitHub
gh auth login

# Suivre les instructions interactives
```

#### Option 2: Vérifier les credentials
```bash
# Voir la config actuelle
git config --list | grep user

# Configurer si nécessaire
git config user.email "votre-email@automai.fr"
git config user.name "Votre Nom"
```

---

## 🚨 Erreur: "Please commit your changes before merging"

### Symptômes
```
error: Your local changes to the following files would be overwritten by merge:
    execution/exporter_docx.py
Please commit your changes or stash them before you merge.
```

### Cause
Vous avez des modifications non commitées qui entreraient en conflit avec le merge.

### Solution

#### Option A: Commiter vos changements d'abord
```bash
git add .
git commit -m "feat: work in progress"
git merge origin/master
```

#### Option B: Stasher temporairement (si vous ne voulez pas commiter maintenant)
```bash
# Mettre de côté vos changements
git stash

# Faire le merge
git merge origin/master

# Récupérer vos changements
git stash pop
```

---

## 🚨 Auto-sync ne fait rien

### Symptômes
Pas de commits automatiques, pas de push.

### Diagnostic
```powershell
# Vérifier que le processus tourne
Get-Process | Where-Object {$_.ProcessName -eq "powershell"}
```

Vous devriez voir au moins un processus PowerShell.

### Solutions

#### Solution 1: Relancer START_DAY
```
Double-clic sur START_DAY_XXX.bat
```

#### Solution 2: Vérifier les logs
```bash
# Voir les derniers logs
cat .auto_sync.log
```

#### Solution 3: Lancer manuellement pour tester
```powershell
powershell -ExecutionPolicy Bypass -File .\auto_sync_v2.ps1 -VERBOSE
```

---

## 🚨 Conflits Git fréquents

### Conflit dans .env.template

**Résolution**: Toujours garder la version avec les placeholders (pas les vraies clés)

```bash
# Ouvrir le fichier
code .env.template

# Garder cette version:
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_your-key-here
SUPABASE_SECRET_KEY=sb_secret_your-key-here

# Supprimer les marqueurs <<<<<<<, =======, >>>>>>>
# Sauvegarder (Ctrl+S)

git add .env.template
git commit -m "merge: resolve .env.template conflict"
```

### Conflit dans execution/*.py

**Résolution**: Discuter avec l'équipe pour décider quelle version garder

```bash
# Voir les différences
git diff execution/assembler_acte.py

# Si votre version est meilleure:
git checkout --ours execution/assembler_acte.py

# Si la version master est meilleure:
git checkout --theirs execution/assembler_acte.py

# Ou combiner manuellement dans VS Code

git add execution/assembler_acte.py
git commit -m "merge: resolve conflict in assembler_acte.py"
```

---

## 🚨 Pull Request échoue

### Symptômes
```
X Pull request AnandaTom/notaire-ai#5 is not mergeable
```

### Cause
Conflit entre votre branche et master.

### Solution
```bash
# Mettre à jour votre branche avec master
git fetch origin master
git merge origin/master

# Résoudre les conflits si nécessaire
# Puis pusher
git push origin votre-branche

# La PR sera automatiquement mise à jour
```

---

## 🚨 "Already up to date" mais je n'ai pas les fichiers

### Symptômes
```bash
git merge origin/master
# Already up to date.

ls *.bat
# Aucun fichier trouvé
```

### Cause
Vous n'êtes probablement pas sur la bonne branche.

### Solution
```bash
# Vérifier votre branche actuelle
git branch
# Devrait montrer: * augustin/dev ou * payoss/dev

# Si vous êtes sur master:
git checkout augustin/dev  # ou payoss/dev

# Si la branche n'existe pas:
git checkout -b augustin/dev
git push -u origin augustin/dev
```

---

## 🚨 "Permission denied (publickey)"

### Symptômes
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

### Cause
SSH key manquante ou invalide.

### Solution

#### Option 1: Utiliser HTTPS au lieu de SSH (plus simple)
```bash
# Changer l'URL du remote
git remote set-url origin https://github.com/AnandaTom/notaire-ai.git

# Vérifier
git remote -v
```

#### Option 2: Configurer une clé SSH
```bash
# Générer une clé SSH
ssh-keygen -t ed25519 -C "votre-email@automai.fr"

# Ajouter à GitHub
# 1. Copier la clé publique
cat ~/.ssh/id_ed25519.pub

# 2. Aller sur GitHub.com → Settings → SSH Keys → Add new
# 3. Coller la clé
```

---

## 🚨 Scripts PowerShell bloqués par la politique d'exécution

### Symptômes
```
... cannot be loaded because running scripts is disabled on this system.
```

### Solution
```powershell
# Autoriser l'exécution des scripts (en tant qu'admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ou lancer avec bypass:
powershell -ExecutionPolicy Bypass -File .\START_DAY_XXX.bat
```

---

## 📞 Support

**Problème non résolu?**
1. Lisez [WORKFLOW_SIMPLE.md](WORKFLOW_SIMPLE.md)
2. Lisez [BEST_PRACTICES_3DEVS.md](BEST_PRACTICES_3DEVS.md)
3. Demandez à Claude Code dans VS Code
4. Contactez Tom

---

## 🔧 Commandes de diagnostic

### Vérifier l'état général
```bash
git status
git branch
git remote -v
git log --oneline -5
```

### Vérifier les processus auto-sync
```powershell
Get-Process | Where-Object {$_.ProcessName -eq "powershell"}
```

### Vérifier les logs auto-sync
```bash
tail -n 50 .auto_sync.log
```

### Vérifier la configuration Git
```bash
git config --list
```

### Nettoyer l'état Git (ATTENTION: perte de modifications non commitées)
```bash
# Annuler tous les changements non commitésI (DANGEREUX)
git reset --hard HEAD

# Nettoyer les fichiers non trackés
git clean -fd
```

---

## ✅ Checklist de vérification rapide

Avant de demander de l'aide, vérifiez:

- [ ] Je suis sur la bonne branche (`git branch`)
- [ ] J'ai récupéré les dernières modifs (`git fetch origin`)
- [ ] J'ai les fichiers .bat et .ps1 (`ls *.bat`)
- [ ] Mon `.env` est configuré (`cat .env | grep SUPABASE`)
- [ ] Auto-sync tourne (Gestionnaire des tâches → powershell.exe)
- [ ] Pas de conflits en cours (`git status` ne mentionne pas "unmerged")

Si tout est ✅ mais ça ne marche toujours pas → Contactez Tom avec le résultat de `git status`.
