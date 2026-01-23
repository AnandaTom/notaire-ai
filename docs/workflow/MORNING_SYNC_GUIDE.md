# Morning Sync Guide - Démarrer la journée avec la dernière version

## 🎯 Objectif

Chaque matin, synchroniser tout le monde avec la dernière version de l'agent :
1. Merger les PRs de la veille
2. Récupérer le code combiné sur votre branche

---

## 🌅 Workflow du matin

```
┌─────────────────────────────────────────────────────────┐
│               MORNING SYNC WORKFLOW                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Hier soir :                                          │
│   ├─ Tom a créé une PR (tom/dev → master)             │
│   ├─ Augustin a créé une PR (augustin/dev → master)    │
│   └─ Payoss a créé une PR (payoss/dev → master)        │
│                                                         │
│   Ce matin (9h) :                                      │
│   ├─ Review + Merge les 3 PRs                          │
│   │  (Tom review Augustin, Augustin review Payoss...)  │
│   └─ Master contient maintenant tout le travail ✅     │
│                                                         │
│   Chacun récupère :                                     │
│   ├─ git fetch origin                                  │
│   ├─ git merge origin/master                           │
│   └─ Travail avec la version complète ✅               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ Utilisation rapide

### Option 1 : Script automatisé (recommandé)

```bash
# Double-cliquer
START_MORNING_SYNC.bat
```

Le script va :
1. Lister les PRs ouvertes
2. Vous demander si vous voulez les merger
3. Sync votre branche automatiquement

### Option 2 : Manuel (si vous préférez GitHub.com)

```bash
# 1. Aller sur GitHub.com
https://github.com/AnandaTom/notaire-ai/pulls

# 2. Cliquer sur chaque PR
# 3. Review → Approve → Squash and merge

# 4. Revenir dans le terminal
git fetch origin
git merge origin/master
git push origin tom/dev
```

---

## 🔧 Modes du script

### Mode INTERACTIF (recommandé)

```powershell
.\morning_sync.ps1
```

**Workflow** :
```
📋 Pull Requests ouvertes:
   Trouvé 3 PR(s) ouverte(s)

─────────────────────────────────────
PR #5 : Ajout clause hypothèque
Auteur: augustin (augustin/dev)

Actions disponibles:
  [v] Voir les changements (git diff)
  [m] Merger cette PR
  [s] Skip (ignorer)
  [q] Quit (arrêter)

Votre choix: m

✅ PR #5 mergée
```

Vous choisissez pour **chaque PR** si vous voulez la merger.

### Mode AUTO (DANGER - déconseillé)

```powershell
.\morning_sync.ps1 -AUTO_APPROVE
```

**Merge automatiquement toutes les PRs sans review.**

⚠️ **Utiliser seulement si** :
- Vous faites confiance à 100% à votre équipe
- Petites PRs simples
- Tests automatiques passent

---

## 📋 Checklist du matin

### Vous (Tom)

```
□ Lancer START_MORNING_SYNC.bat
□ Reviewer les PRs d'Augustin et Payoss
□ Merger celles qui sont OK
□ Sync votre branche (automatique)
□ Lancer auto_sync_v2.ps1
□ Commencer à travailler
```

### Augustin

```
□ Lancer morning_sync.ps1
□ Reviewer les PRs de Tom et Payoss
□ Merger
□ Sync automatique
□ Lancer auto_sync_v2.ps1 -BRANCH "augustin/dev"
```

### Payoss

```
□ Lancer morning_sync.ps1
□ Reviewer les PRs de Tom et Augustin
□ Merger
□ Sync automatique
□ Lancer auto_sync_v2.ps1 -BRANCH "payoss/dev"
```

---

## 🔄 Rotation des reviews

Pour que chacun review le code des autres :

| Dev | Review qui ? |
|-----|--------------|
| Tom | PRs d'Augustin |
| Augustin | PRs de Payoss |
| Payoss | PRs de Tom |

**Rotation** : Chacun review au moins 1 PR par jour.

---

## ⚠️ Pourquoi NE PAS auto-merger sans review ?

| Risque | Exemple |
|--------|---------|
| **Bugs** | Code qui casse une feature existante |
| **Mauvaise qualité** | Code non optimisé, difficile à maintenir |
| **Régression** | Nouvelles features cassent les anciennes |
| **Sécurité** | Failles de sécurité introduites |
| **Conflits cachés** | Merge réussi mais logique cassée |

**Review = Quality gate** ✅

---

## ✅ Automatisations possibles (safe)

### 1. Tests automatiques (GitHub Actions)

```yaml
# .github/workflows/test.yml (déjà configuré)
on: [pull_request]

jobs:
  test:
    - run: pytest
    - run: validate schemas
```

**Résultat** : Si les tests échouent, la PR ne peut pas être mergée.

### 2. Auto-approve si tests passent (optionnel)

```yaml
# .github/workflows/auto-approve.yml
on: [pull_request]

jobs:
  auto-approve:
    if: github.event.pull_request.user.login == 'augustin'
    steps:
      - run: gh pr review $PR --approve
```

**Mais** : Vous devez quand même cliquer "Merge" manuellement.

### 3. Dependabot (dépendances)

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Résultat** : PRs automatiques pour mettre à jour les dépendances.

---

## 🎯 Workflow complet recommandé

```
Soir (fin de journée) :
  ├─ Tom : gh pr create (tom/dev → master)
  ├─ Augustin : gh pr create (augustin/dev → master)
  └─ Payoss : gh pr create (payoss/dev → master)

Matin (9h) :
  ├─ Réunion rapide 5 min (optionnel)
  │  └─ Discuter des PRs importantes
  │
  ├─ Chacun lance morning_sync.ps1
  │  ├─ Review 1-2 PRs des autres
  │  └─ Merge si OK
  │
  └─ Master contient le travail de tous ✅

Journée :
  ├─ Lancer auto_sync_v2.ps1 (sync auto)
  └─ Travailler normalement
```

---

## 📊 Exemple concret

### Hier soir (Mardi 18h)

```
Tom : PR #5 "Ajout clause hypothèque"
Augustin : PR #6 "Fix export PDF"
Payoss : PR #7 "Update templates"
```

### Ce matin (Mercredi 9h)

```powershell
# Tom lance
.\morning_sync.ps1

# Output:
📋 Pull Requests ouvertes:
   Trouvé 2 PR(s) ouverte(s)  (sa propre PR n'est pas listée)

PR #6 : Fix export PDF (Augustin)
  → Tom review et merge ✅

PR #7 : Update templates (Payoss)
  → Tom review et merge ✅

🔄 Synchronisation avec master...
✅ Branche synchronisée avec master

# Tom a maintenant:
# - Son code (clause hypothèque)
# - Code d'Augustin (fix PDF)
# - Code de Payoss (templates)
```

Augustin et Payoss font pareil de leur côté.

**Résultat** : Tout le monde a la version complète ! 🎉

---

## 🚀 Commandes rapides

```bash
# Morning sync interactif
.\morning_sync.ps1

# Morning sync avec preview (test)
.\morning_sync.ps1 -DRY_RUN

# Morning sync auto (DANGER)
.\morning_sync.ps1 -AUTO_APPROVE
```

---

## ✨ Best practices

1. **Review le matin à froid** : Plus objectif qu'en fin de journée
2. **Petites PRs** : Plus facile à reviewer rapidement
3. **Tests passent** : Vérifier les tests avant de merger
4. **Communication** : Slack si une PR est urgente
5. **Rotation** : Tout le monde review tout le monde

---

## 🎉 Résultat

```
✅ Chaque matin, tout le monde démarre avec:
   - Le code combiné de toute l'équipe
   - Master stable et testé
   - Prêt à développer de nouvelles features
```

**Bienvenue dans le workflow professionnel ! 🚀**
