# Auto-Sync - Automatisation Complète

## 🎯 Qu'est-ce que Auto-Sync ?

**Auto-Sync = Auto-Push + Sync avec Master automatique**

```
┌─────────────────────────────────────────────────────────┐
│              WORKFLOW 100% AUTOMATISÉ                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Toutes les 30 min : Commit + Push vos changements    │
│   Toutes les 60 min : Récupérer master + Merge auto    │
│                                                         │
│   Vous : Travaillez normalement                        │
│   Script : S'occupe de TOUT                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Lancer Auto-Sync (ultra simple)

### Option 1 : Double-cliquer (recommandé)

```
START_AUTO_SYNC.bat
```

Double-cliquez → Le script tourne → Oubliez tout !

### Option 2 : PowerShell avec paramètres

```powershell
# Tom
.\auto_sync.ps1 -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "tom/dev"

# Augustin
.\auto_sync.ps1 -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "augustin/dev"

# Payoss
.\auto_sync.ps1 -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "payoss/dev"
```

---

## ⚙️ Paramètres personnalisables

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `SYNC_INTERVAL_MINUTES` | 60 | Sync avec master toutes les X min |
| `PUSH_INTERVAL_MINUTES` | 30 | Push changements toutes les X min |
| `BRANCH` | tom/dev | Votre branche |

### Exemples

```powershell
# Sync très fréquent (toutes les 30 min)
.\auto_sync.ps1 -SYNC_INTERVAL_MINUTES 30 -PUSH_INTERVAL_MINUTES 15 -BRANCH "tom/dev"

# Sync léger (toutes les 2 heures)
.\auto_sync.ps1 -SYNC_INTERVAL_MINUTES 120 -PUSH_INTERVAL_MINUTES 60 -BRANCH "tom/dev"
```

---

## 📊 Ce que fait Auto-Sync

### Toutes les 30 minutes (PUSH)

```bash
# 1. Vérifier s'il y a des changements
git status

# 2. Si oui : commit + push
git add .
git commit -m "auto: Sauvegarde automatique - [timestamp]"
git push origin tom/dev
```

### Toutes les 60 minutes (SYNC)

```bash
# 1. Récupérer master
git fetch origin master

# 2. Merger master dans votre branche
git merge origin/master

# 3. Si pas de conflit : push
git push origin tom/dev

# 4. Si conflit : alerte + abort
# (vous devez résoudre manuellement)
```

---

## 🔄 Workflow complet automatisé

```
VOUS                           AUTO-SYNC
────                           ─────────

Vous travaillez                ⏱️ Check toutes les 5 min
  ↓
Ctrl+S (auto-save)             ⏱️ Après 30 min → Commit + Push
  ↓
Continuer à travailler         ⏱️ Après 60 min → Fetch + Merge master
  ↓
Ctrl+S                         ⏱️ Après 30 min → Commit + Push
  ↓
...                            ⏱️ Loop infini

RÉSULTAT:
  ✅ Vos changements sont sauvegardés toutes les 30 min
  ✅ Vous êtes à jour avec master toutes les 60 min
  ✅ Zéro perte de données
  ✅ Zéro conflit (détecté rapidement)
```

---

## ⚠️ Gestion des conflits

### Si un conflit arrive

Le script affiche :

```
[2026-01-22 16:30:45] ⚠️  Merge conflict detected!
[2026-01-22 16:30:45] ⚠️  Please resolve conflicts manually and run:
           git add . && git commit && git push origin tom/dev
```

### Actions à prendre

```bash
# 1. Voir les fichiers en conflit
git status

# 2. Ouvrir les fichiers et résoudre
# (Chercher <<<<<<<, =======, >>>>>>>)

# 3. Marquer comme résolu
git add .

# 4. Finaliser
git commit -m "resolve: merge conflict with master"

# 5. Push
git push origin tom/dev

# 6. Le script continue automatiquement
```

---

## 🎯 Comparaison des scripts

| Fonctionnalité | auto_push.ps1 | auto_sync.ps1 |
|----------------|---------------|---------------|
| Commit + Push auto | ✅ | ✅ |
| Sync avec master | ❌ | ✅ |
| Détection conflits | ❌ | ✅ |
| Intervalle configurable | ✅ | ✅ (2 intervals) |

**Recommandation** : Utilisez `auto_sync.ps1` pour une automatisation complète !

---

## 📋 Workflow quotidien avec Auto-Sync

### Matin

```bash
# Lancer Auto-Sync
.\START_AUTO_SYNC.bat

# C'est tout !
```

### Journée

```
Travaillez normalement → Auto-Sync s'occupe de tout
```

### Soir

```
Ctrl+C (arrêter le script)
```

---

## 🔧 Configuration par développeur

### START_AUTO_SYNC_TOM.bat

```batch
powershell -ExecutionPolicy Bypass -File ".\auto_sync.ps1" -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "tom/dev"
```

### START_AUTO_SYNC_AUGUSTIN.bat

```batch
powershell -ExecutionPolicy Bypass -File ".\auto_sync.ps1" -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "augustin/dev"
```

### START_AUTO_SYNC_PAYOSS.bat

```batch
powershell -ExecutionPolicy Bypass -File ".\auto_sync.ps1" -SYNC_INTERVAL_MINUTES 60 -PUSH_INTERVAL_MINUTES 30 -BRANCH "payoss/dev"
```

---

## 📊 Output du script

```
🚀 NotaireAI Auto-Sync Started
Branch: tom/dev
Sync with master: every 60 minutes
Push changes: every 30 minutes
═══════════════════════════════════════════════════════
[2026-01-22 16:00:00] 🔄 Syncing with master...
[2026-01-22 16:00:05] ✅ Successfully synced with master
[2026-01-22 16:00:10] ✅ Pushed sync to tom/dev
[2026-01-22 16:00:10] ⏳ Next sync in ~60 min | Next push in ~30 min
───────────────────────────────────────────────────────
[2026-01-22 16:30:00] 📤 Changes detected, committing and pushing...
[2026-01-22 16:30:05] ✅ Push completed to tom/dev!
[2026-01-22 16:30:05] ⏳ Next sync in ~30 min | Next push in ~30 min
───────────────────────────────────────────────────────
```

---

## ✅ Avantages

| Avantage | Description |
|----------|-------------|
| 🔄 **Sync auto** | Toujours à jour avec master |
| 📤 **Push auto** | Zéro perte de données |
| ⚠️ **Détection conflits** | Alertes immédiates |
| ⏱️ **Gain de temps** | Plus de commandes git manuelles |
| 🛡️ **Sécurité** | Double backup (local + GitHub) |

---

## 🎯 Workflow final recommandé

```
AVANT (manuel)                   APRÈS (auto-sync)
──────────────                   ─────────────────

Matin :                          Matin :
  git fetch                        START_AUTO_SYNC.bat
  git merge origin/master
  git push

Journée :                        Journée :
  git add .                        Travaillez
  git commit
  git push
  (toutes les heures)

Sync avec master :               Sync avec master :
  git fetch                        Automatique (60 min)
  git merge origin/master
  (quand vous y pensez)

Fin de journée :                 Fin de journée :
  git push                         Ctrl+C
```

**Résultat** : Vous ne tapez PLUS JAMAIS de commandes git ! 🎉

---

## 🚀 Pour démarrer maintenant

```powershell
# 1. Double-cliquez
START_AUTO_SYNC.bat

# 2. Laissez tourner
# 3. Oubliez Git !
```

**Bienvenue dans le workflow 100% automatisé ! ✨**
