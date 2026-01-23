# Guide de Collaboration - NotaireAI

## Équipe : 3 développeurs

---

## ⚠️ Règle d'Or : NE JAMAIS PERDRE DE DONNÉES

### Problème connu avec Live Share

Les modifications faites par un **invité** sont stockées en **mémoire** chez l'hôte.
Si l'hôte ne sauvegarde pas (`Ctrl+S`) avant de push, les changements sont perdus.

---

## ✅ Bonnes Pratiques

### 1. Auto-Save obligatoire (TOUS les développeurs)

Dans VS Code → `File` → `Preferences` → `Settings` :

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000
}
```

Ou rechercher "auto save" et mettre **"afterDelay"** avec **1000ms**.

### 2. Avant chaque push (HÔTE uniquement)

```bash
# 1. Sauvegarder TOUS les fichiers
Ctrl+K S  (ou File → Save All)

# 2. Vérifier les changements
git status

# 3. Ajouter et committer
git add .
git commit -m "description"

# 4. Push
git push
```

### 3. Communication obligatoire

Avant de push, l'hôte demande :
> "Je vais push, tout le monde a fini ses modifications ?"

### 4. Commits fréquents

| Fréquence | Action |
|-----------|--------|
| Toutes les heures | Push automatique (script) |
| Après chaque feature | Commit manuel avec description |
| Avant pause/fin de journée | Push obligatoire |

### 5. Qui peut être hôte ?

| Rôle | Peut push ? | Recommandation |
|------|-------------|----------------|
| **Hôte** | ✅ Oui | Celui qui a le repo cloné en local |
| **Invité** | ❌ Non | Doit demander à l'hôte de push |

**Conseil** : Tournez le rôle d'hôte, ou travaillez chacun sur votre clone.

---

## 🔄 Workflow recommandé (3 devs)

### Option A : Live Share (travail synchrone)

```
1. UN hôte démarre Live Share
2. Les autres rejoignent comme invités
3. L'hôte active Auto-Save
4. L'hôte fait "Save All" + commit + push régulièrement
5. Communication constante sur les modifications
```

### Option B : Branches séparées (travail asynchrone) ⭐ RECOMMANDÉ

```
Chaque dev a son propre clone :

Dev 1 (Tom) :     git checkout -b tom/feature-x
Dev 2 (Associé) : git checkout -b alex/feature-y
Dev 3 :           git checkout -b chris/feature-z

Workflow :
1. Chacun travaille sur sa branche
2. Push sur sa branche : git push -u origin tom/feature-x
3. Créer une Pull Request pour merger dans master
4. Review par un autre dev
5. Merge
```

### Option C : Hybride (le meilleur des deux)

```
- Live Share pour les sessions de pair programming
- Branches pour le travail individuel
- Pull Requests pour merger
```

---

## 🛡️ Script de sauvegarde automatique

Le script `auto_push.ps1` fait un push toutes les heures.

### Lancer le script :

```powershell
# Dans PowerShell (laisser tourner en arrière-plan)
.\auto_push.ps1
```

### Arrêter le script :

```
Ctrl+C
```

---

## 🚨 En cas de perte de données

### Si les fichiers sont encore ouverts dans VS Code (hôte)

1. `Ctrl+Z` (annuler) dans chaque fichier
2. `Ctrl+S` pour sauvegarder
3. Vérifier avec `git status`

### Si VS Code a été fermé

Les modifications non sauvegardées sont **perdues**.
→ C'est pourquoi Auto-Save est obligatoire.

### Récupérer depuis GitHub

```bash
# Voir l'historique
git log --oneline

# Revenir à un commit précédent (ATTENTION: perd les changements locaux)
git checkout <commit-hash>
```

---

## 📋 Checklist quotidienne

### Début de journée
- [ ] `git pull` pour récupérer les dernières modifications
- [ ] Vérifier que Auto-Save est activé
- [ ] Lancer `auto_push.ps1` si vous êtes l'hôte

### Pendant le travail
- [ ] Communication avant chaque push
- [ ] "Save All" (`Ctrl+K S`) avant de push
- [ ] Commits avec messages clairs

### Fin de journée
- [ ] `git status` pour vérifier les changements
- [ ] `git add . && git commit -m "..." && git push`
- [ ] Prévenir l'équipe que vous avez push

---

## Configuration VS Code recommandée

Ajouter dans `.vscode/settings.json` (partagé avec l'équipe) :

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "git.enableSmartCommit": true,
  "git.autofetch": true,
  "git.confirmSync": false
}
```
