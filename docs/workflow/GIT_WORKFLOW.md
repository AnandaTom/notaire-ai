# Git Workflow - Équipe NotaireAI (3 devs)

## Principe : Chacun sa branche, merge via Pull Request

```
master ───────────────────────────────────────────────────
          ↑           ↑           ↑
          │ PR        │ PR        │ PR
          │           │           │
tom/xxx ──┘           │           │
alex/xxx ─────────────┘           │
chris/xxx ────────────────────────┘
```

---

## 🚀 Setup initial (une seule fois par dev)

### Dev 1 - Tom
```bash
git clone https://github.com/AnandaTom/notaire-ai.git
cd notaire-ai
git checkout -b tom/dev
git push -u origin tom/dev
```

### Dev 2 - Alex
```bash
git clone https://github.com/AnandaTom/notaire-ai.git
cd notaire-ai
git checkout -b alex/dev
git push -u origin alex/dev
```

### Dev 3 - Chris
```bash
git clone https://github.com/AnandaTom/notaire-ai.git
cd notaire-ai
git checkout -b chris/dev
git push -u origin chris/dev
```

---

## 📅 Workflow quotidien

### 1. Début de journée : récupérer les dernières modifs de master

```bash
# Sur votre branche
git checkout tom/dev  # (ou alex/dev, chris/dev)

# Récupérer master
git fetch origin
git merge origin/master

# Résoudre les conflits si nécessaire, puis :
git push
```

### 2. Pendant le travail : commits réguliers

```bash
# Après chaque modification importante
git add .
git commit -m "feat: description claire du changement"
git push
```

### 3. Feature terminée : créer une Pull Request

```bash
# Via GitHub CLI
gh pr create --title "Ma feature" --body "Description de ce que j'ai fait"

# OU via GitHub.com
# → Pull requests → New pull request → tom/dev → master
```

### 4. Review et merge

1. Un autre dev review la PR
2. Approuve ou demande des changements
3. Une fois approuvé → **Squash and merge**
4. La branche est supprimée automatiquement après merge

### 5. Après le merge : mettre à jour sa branche

```bash
git checkout tom/dev
git fetch origin
git merge origin/master
git push
```

---

## 🔀 Nommage des branches

| Type | Format | Exemple |
|------|--------|---------|
| Feature | `{dev}/feat-{description}` | `tom/feat-nouvelle-clause` |
| Fix | `{dev}/fix-{description}` | `alex/fix-export-pdf` |
| Dev principale | `{dev}/dev` | `chris/dev` |

---

## 📝 Nommage des commits

```
type: description courte

Types:
- feat: nouvelle fonctionnalité
- fix: correction de bug
- docs: documentation
- refactor: refactoring
- test: ajout de tests
- chore: maintenance
```

Exemples :
```
feat: ajout clause hypothèque conditionnelle
fix: correction export DOCX avec tableaux
docs: mise à jour guide collaboration
```

---

## ⚠️ Règles importantes

### À FAIRE ✅
- Toujours travailler sur SA branche
- Pull request pour merger dans master
- Review par au moins 1 autre dev
- Commits clairs et fréquents
- `git fetch && git merge origin/master` chaque matin

### À NE PAS FAIRE ❌
- Push directement sur master
- Merge sans review
- Commits géants avec 50 fichiers
- Travailler sur la branche d'un autre

---

## 🛠️ Commandes utiles

```bash
# Voir toutes les branches
git branch -a

# Changer de branche
git checkout tom/dev

# Créer une nouvelle branche pour une feature
git checkout -b tom/feat-ma-feature

# Voir l'état
git status

# Voir les différences
git diff

# Voir l'historique
git log --oneline -10

# Annuler les modifications non committées
git checkout -- .

# Créer une PR
gh pr create

# Voir les PRs en cours
gh pr list

# Merger une PR (après review)
gh pr merge <numero>
```

---

## 🔄 Résolution de conflits

Si `git merge origin/master` crée des conflits :

```bash
# 1. Ouvrir les fichiers en conflit
#    Chercher les marqueurs <<<<<<<, =======, >>>>>>>

# 2. Résoudre manuellement (garder le bon code)

# 3. Marquer comme résolu
git add .

# 4. Finaliser le merge
git commit -m "merge: résolution conflits avec master"

# 5. Push
git push
```

---

## 📊 Visualiser le workflow

```bash
# Graphe des branches
git log --oneline --graph --all -20
```

---

## 🤖 Automatisation (optionnel)

### GitHub Actions : tests automatiques sur chaque PR

Le fichier `.github/workflows/test.yml` (à créer) peut :
- Lancer les tests Python
- Vérifier le formatage
- Bloquer le merge si les tests échouent
