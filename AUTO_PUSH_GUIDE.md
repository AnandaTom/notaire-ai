# Auto-Push Guide - NotaireAI

## 🎯 Objectif

Chaque X minutes, le script commit et push automatiquement vos changements sur votre branche (`tom/dev`).

**Plus de `git push` manuel** - tout est automatisé.

---

## ✅ Comment ça marche

```
┌─────────────────────────────────────────────────────┐
│           VOTRE WORKFLOW AUTOMATISÉ                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│   Vous : Travaillez normalement (Ctrl+S auto)      │
│                                                     │
│   Script (toutes les 30 min) :                      │
│   ├─ Détecte les changements (git status)          │
│   ├─ git add .                                      │
│   ├─ git commit -m "auto: ..."                      │
│   └─ git push origin tom/dev                        │
│                                                     │
│   Résultat : Tout est sauvegardé sur GitHub ✅     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Lancer le script (2 options)

### Option A : Double-cliquer (le plus simple)

1. Allez dans votre dossier NotaireAI
2. Double-cliquez sur **`START_AUTO_PUSH.bat`**
3. Une fenêtre PowerShell s'ouvre
4. Le script tourne en arrière-plan

### Option B : Via PowerShell

```powershell
# Aller dans le dossier
cd "c:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"

# Lancer avec interval de 30 minutes (par défaut)
.\auto_push.ps1

# Ou personnaliser l'interval (ex: 15 minutes)
.\auto_push.ps1 -INTERVAL_MINUTES 15

# Ou personnaliser la branche
.\auto_push.ps1 -INTERVAL_MINUTES 20 -BRANCH "tom/feat-nouvelle-clause"
```

---

## ⚙️ Personnalisation

### Changer l'interval

Dans `START_AUTO_PUSH.bat`, remplacer :

```batch
powershell -ExecutionPolicy Bypass -File ".\auto_push.ps1" -INTERVAL_MINUTES 30 -BRANCH "tom/dev"
```

Par exemple, pour **10 minutes** :

```batch
powershell -ExecutionPolicy Bypass -File ".\auto_push.ps1" -INTERVAL_MINUTES 10 -BRANCH "tom/dev"
```

### Intervals recommandés

| Interval | Cas d'usage |
|----------|------------|
| **10 min** | Travail critique (ne rien perdre) |
| **30 min** | Normal (balance sauvegarde/commits clean) |
| **60 min** | Développement léger |

---

## 📊 Output du script

Quand le script tourne, vous verrez :

```
🚀 NotaireAI Auto-Push Started
Branch: tom/dev
Interval: 30 minutes
───────────────────────────────────────
[2025-01-22 14:30:45] ✅ Changes detected, committing and pushing...
[2025-01-22 14:30:50] ✅ Push completed to tom/dev!
[2025-01-22 14:30:50] ⏳ Next push in 30 minutes...
───────────────────────────────────────
[2025-01-22 15:00:45] ⏸️  No changes to push.
[2025-01-22 15:00:45] ⏳ Next push in 30 minutes...
```

---

## ⏹️ Arrêter le script

```
Ctrl+C dans la fenêtre PowerShell
```

---

## 🔐 Avantages

| Avantage | Description |
|----------|-------------|
| ✅ **Zéro perte de données** | Tout est pushé régulièrement |
| ✅ **Automatisé** | Vous travaillez, le script s'occupe du push |
| ✅ **Historique traçable** | Chaque changement = un commit |
| ✅ **Collaboratif** | Vos changements sont visibles pour Augustin/Payoss |
| ✅ **Simple** | Just Ctrl+S + le script fait le reste |

---

## 🎯 Workflow final (avec auto-push)

```
AVANT (manuel)                  APRÈS (auto)
─────────────────────────       ──────────────────────
Vous travaillez                 Vous travaillez
      ↓                               ↓
Vous faites Ctrl+S         Auto-Save (1 sec)
      ↓                               ↓
Vous faites "git push"         Script: git commit + push
      ↓                         (toutes les 30 min)
❌ Oubli possible                ↓
❌ Perte de données       ✅ Tout sauvegardé
```

---

## 📝 Notes importantes

1. **Auto-Save doit être activé** : Vérifiez `.vscode/settings.json`
   ```json
   "files.autoSave": "afterDelay",
   "files.autoSaveDelay": 1000
   ```

2. **Le script tourne 24/7** : Laissez la fenêtre ouverte

3. **Les autres devs font pareil** : Augustin et Payoss lancent aussi leur script avec leur branche

4. **Conflits git** : Le script peut échouer si des conflits arrivent. Dans ce cas, vous devez les résoudre manuellement

---

## 🐛 Troubleshooting

### "PowerShell execution policy" error

Utiliser le `.bat` au lieu de lancer le script directement. Le `.bat` contourne ça.

### Push fails avec erreur

```
fatal: cannot access 'https://...'
```

Vérifier :
- [ ] Connexion internet
- [ ] Credentials GitHub (token expiré ?)
- [ ] Branche existe sur GitHub

### Commits s'accumulent

Le script crée un commit **à chaque push**. C'est normal. Au moment du merge en PR, vous pouvez faire "Squash and merge" pour nettoyer.

---

## 🚀 Commande à lancer maintenant

```batch
START_AUTO_PUSH.bat
```

Ou en PowerShell :

```powershell
.\auto_push.ps1
```

C'est tout ! Vous êtes maintenant en **auto-push mode** ✨
