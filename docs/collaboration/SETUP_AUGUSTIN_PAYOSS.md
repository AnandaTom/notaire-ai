# Setup Augustin & Payoss - Instructions Complètes

## ⚠️ Problème rencontré

Si vous voyez cette erreur en lançant `START_DAY_XXX.bat`:
```
L'argument « .\morning_sync.ps1 » du paramètre -File n'existe pas.
```

C'est normal! Vous devez d'abord récupérer les scripts depuis `master`.

---

## ✅ Solution: Setup complet en 7 étapes

### Étape 1: Cloner le repo (si pas déjà fait)

```bash
git clone https://github.com/AnandaTom/notaire-ai.git
cd notaire-ai
```

### Étape 2: Configurer Git

```bash
git config user.email "votre-email@automai.fr"
git config user.name "Votre Nom"
```

**Augustin**:
```bash
git config user.email "augustin@automai.fr"
git config user.name "Augustin France"
```

**Payoss**:
```bash
git config user.email "payoss@automai.fr"
git config user.name "Payoss"
```

### Étape 3: Créer votre branche DEPUIS master

**Augustin**:
```bash
git checkout master
git pull origin master
git checkout -b augustin/dev
```

**Payoss**:
```bash
git checkout master
git pull origin master
git checkout -b payoss/dev
```

### Étape 4: Vérifier que vous avez les scripts

```bash
# Vérifier que les fichiers existent
ls *.bat
ls *.ps1
```

Vous devriez voir:
```
START_DAY_TOM.bat
START_DAY_AUGUSTIN.bat
START_DAY_PAYOSS.bat
END_DAY.bat
auto_sync_v2.ps1
morning_sync.ps1
```

✅ Si vous voyez ces fichiers, c'est bon!
❌ Si vous ne les voyez pas, retournez à l'étape 3.

### Étape 5: Pusher votre branche

**Augustin**:
```bash
git push -u origin augustin/dev
```

**Payoss**:
```bash
git push -u origin payoss/dev
```

### Étape 6: Configurer les clés Supabase 🔐

```bash
# Copier le template
cp .env.template .env

# Ouvrir dans VS Code
code .env
```

Remplir ces 3 lignes avec les clés reçues par message sécurisé:
```env
SUPABASE_URL=https://wcklvjckzktijtgakdrk.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_... (voir message Signal/WhatsApp)
SUPABASE_SECRET_KEY=sb_secret_... (voir message Signal/WhatsApp)
```

Sauvegarder (Ctrl+S) et fermer.

### Étape 7: Tester START_DAY

**Augustin**: Double-clic sur `START_DAY_AUGUSTIN.bat`
**Payoss**: Double-clic sur `START_DAY_PAYOSS.bat`

Vous devriez voir:
```
========================================
  NotaireAI - Demarrage Journee (AUGUSTIN)
========================================

[1/3] Merge des PRs...
Aucune Pull Request ouverte pour le moment.

[2/3] Lancement auto-sync...
[Fenêtre PowerShell s'ouvre en arrière-plan]

[3/3] Termine !
========================================
  PRET ! Vous pouvez travailler.
========================================
```

✅ Si vous voyez ce message, c'est parfait!

---

## 🎯 Workflow quotidien après le setup

### Matin (9h00)
```
Double-clic sur START_DAY_AUGUSTIN.bat (ou PAYOSS.bat)
```

### Journée (9h01-18h00)
```
Travaillez normalement, faites Ctrl+S
```
→ Auto-sync s'occupe du reste (invisible)

### Soir (18h00)
```
Double-clic sur END_DAY.bat
```

---

## ❓ Questions fréquentes

**Q: Pourquoi je n'avais pas les fichiers .bat et .ps1?**
R: Car ils ont été ajoutés récemment sur `master`. En créant votre branche depuis `master` (étape 3), vous récupérez tout.

**Q: Que se passe-t-il si j'ai déjà créé ma branche sans les scripts?**
R: Pas grave! Faites:
```bash
git checkout votre-branche
git merge origin/master
```
Cela fusionnera master dans votre branche et vous aurez les scripts.

**Q: Je vois "Already up to date" quand je merge master, mais je n'ai toujours pas les scripts**
R: Vérifiez que vous êtes sur la bonne branche:
```bash
git branch  # Montre votre branche actuelle
git checkout master  # Aller sur master
git pull origin master  # Récupérer les derniers changements
ls *.bat  # Vérifier que les fichiers existent
git checkout votre-branche  # Retourner sur votre branche
git merge master  # Fusionner
```

**Q: Auto-sync ne fait rien, comment savoir s'il tourne?**
R: Ouvrez le Gestionnaire des tâches (Ctrl+Shift+Esc) → Onglet "Détails" → Cherchez "powershell.exe". Vous devriez voir un processus PowerShell qui tourne.

---

## 🚨 Points d'attention

### Si vous avez l'erreur "morning_sync.ps1 n'existe pas"
→ Retournez à l'étape 3 et mergez master

### Si vous avez l'erreur "Access denied" ou "Unauthorized"
→ Vérifiez que vous avez bien configuré `.env` (étape 6)

### Si START_DAY ne fait rien
→ Vérifiez que vous êtes bien sur votre branche (pas sur master):
```bash
git branch  # Devrait montrer * augustin/dev ou * payoss/dev
```

---

## 📞 Support

**Problème non résolu?**
1. Lisez WORKFLOW_SIMPLE.md
2. Demandez à Claude Code dans VS Code
3. Contactez Tom

Bon courage! 🚀
