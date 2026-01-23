# Workflow Par Développeur - NotaireAI

## 🎯 Chaque dev a son fichier START_DAY

```
Tom       → START_DAY_TOM.bat
Augustin  → START_DAY_AUGUSTIN.bat
Payoss    → START_DAY_PAYOSS.bat
```

Tous utilisent le **même END_DAY.bat** ✅

---

## 📋 Récapitulatif des fichiers

### START_DAY (matin)

| Fichier | Pour qui | Branche |
|---------|----------|---------|
| `START_DAY_TOM.bat` | Tom | tom/dev |
| `START_DAY_AUGUSTIN.bat` | Augustin | augustin/dev |
| `START_DAY_PAYOSS.bat` | Payoss | payoss/dev |

**Différence** : La branche spécifiée dans auto_sync_v2.ps1

### END_DAY (soir)

| Fichier | Pour qui |
|---------|----------|
| `END_DAY.bat` | **Tous** (auto-détecte la branche) |

---

## 🔍 Différence entre les fichiers START_DAY

### START_DAY_TOM.bat (ligne 13)
```batch
start /min powershell -ExecutionPolicy Bypass -File ".\auto_sync_v2.ps1" -BRANCH "tom/dev"
```

### START_DAY_AUGUSTIN.bat (ligne 13)
```batch
start /min powershell -ExecutionPolicy Bypass -File ".\auto_sync_v2.ps1" -BRANCH "augustin/dev"
```

### START_DAY_PAYOSS.bat (ligne 13)
```batch
start /min powershell -ExecutionPolicy Bypass -File ".\auto_sync_v2.ps1" -BRANCH "payoss/dev"
```

**UNIQUEMENT la branche change** ! Le reste est identique.

---

## 📊 Ce que fait chaque .bat en détail

### START_DAY_XXX.bat (Matin)

```
┌─────────────────────────────────────────────────┐
│            START_DAY (MATIN)                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Merge PRs (morning_sync.ps1 -AUTO_APPROVE)  │
│    ├─ Récupère toutes les PRs ouvertes         │
│    ├─ Les approve automatiquement              │
│    └─ Les merge sur master (Squash)            │
│                                                 │
│ 2. Sync avec master                            │
│    ├─ git fetch origin                         │
│    ├─ git merge origin/master                  │
│    └─ git push origin votre_branche            │
│                                                 │
│ 3. Lance auto-sync en arrière-plan             │
│    ├─ Tourne toute la journée                  │
│    ├─ Commit + Push (30 min)                   │
│    └─ Sync master (60 min)                     │
│                                                 │
│ Résultat: Vous avez le code de tout le monde ✅│
│                                                 │
└─────────────────────────────────────────────────┘
```

### END_DAY.bat (Soir)

```
┌─────────────────────────────────────────────────┐
│              END_DAY (SOIR)                     │
├─────────────────────────────────────────────────┤
│                                                 │
│ 1. Dernier commit                              │
│    ├─ git add .                                │
│    └─ git commit -m "Fin de journée..."        │
│                                                 │
│ 2. Push sur votre branche                      │
│    ├─ Détecte automatiquement votre branche    │
│    └─ git push origin votre_branche            │
│                                                 │
│ 3. Crée une Pull Request                       │
│    ├─ gh pr create                             │
│    ├─ Titre: "Travail du [date]"               │
│    └─ Body: "Auto-PR - Travail de la journée"  │
│                                                 │
│ Résultat: Votre travail est sur GitHub + PR ✅ │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Workflow quotidien pour chacun

### Tom

```
Matin:  Double-clic START_DAY_TOM.bat
Journée: Travail (auto-sync actif)
Soir:   Double-clic END_DAY.bat
```

### Augustin

```
Matin:  Double-clic START_DAY_AUGUSTIN.bat
Journée: Travail (auto-sync actif)
Soir:   Double-clic END_DAY.bat
```

### Payoss

```
Matin:  Double-clic START_DAY_PAYOSS.bat
Journée: Travail (auto-sync actif)
Soir:   Double-clic END_DAY.bat
```

---

## 📁 Organisation des fichiers

```
Projet/
├─ START_DAY_TOM.bat         ← Tom utilise celui-ci
├─ START_DAY_AUGUSTIN.bat    ← Augustin utilise celui-ci
├─ START_DAY_PAYOSS.bat      ← Payoss utilise celui-ci
├─ END_DAY.bat               ← Tous utilisent celui-ci
│
├─ auto_sync_v2.ps1          ← Script appelé par START_DAY
└─ morning_sync.ps1          ← Script appelé par START_DAY
```

---

## 💡 Pourquoi 3 fichiers START_DAY ?

### Problème

Si tout le monde utilise le même fichier sans spécifier la branche :
```batch
auto_sync_v2.ps1  # Sans -BRANCH
```

Auto_sync_v2.ps1 va **auto-détecter** la branche actuelle.

**Risque** : Si Augustin est accidentellement sur `master`, auto-sync refuse (protection).

### Solution

Spécifier explicitement la branche :
```batch
auto_sync_v2.ps1 -BRANCH "augustin/dev"  # ✅ Sûr
```

---

## ✅ Résumé

| Question | Réponse |
|----------|---------|
| **Même fichier pour tous ?** | NON pour START_DAY, OUI pour END_DAY |
| **Différence ?** | La branche spécifiée |
| **Pourquoi ?** | Sécurité + clarté |
| **END_DAY commun ?** | OUI, auto-détecte la branche |

---

## 🎯 Action pour chacun

### Tom
```
Créer raccourci Bureau:
- START_DAY_TOM.bat → "Démarrer Journée"
- END_DAY.bat → "Fin Journée"
```

### Augustin
```
Créer raccourci Bureau:
- START_DAY_AUGUSTIN.bat → "Démarrer Journée"
- END_DAY.bat → "Fin Journée"
```

### Payoss
```
Créer raccourci Bureau:
- START_DAY_PAYOSS.bat → "Démarrer Journée"
- END_DAY.bat → "Fin Journée"
```

---

## 🎉 Résultat final

Chaque dev a **2 raccourcis sur le bureau** :
- ☀️ Démarrer Journée (matin)
- 🌙 Fin Journée (soir)

**2 clics par jour, c'est tout ! 🚀**
