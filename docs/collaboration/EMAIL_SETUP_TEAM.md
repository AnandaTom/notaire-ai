# Email Setup - À envoyer à Augustin et Payoss

---

## 📧 Email à copier-coller

**Destinataires**: Augustin, Payoss
**Sujet**: NotaireAI - Setup en 5 minutes ⏱️

---

Salut l'équipe! 👋

Le repo **NotaireAI** est prêt avec un workflow ultra-simple qui vous fera gagner 30 min/jour.

**Le principe**: 2 clics par jour au lieu de 50 commandes Git.

## 🚀 Setup (5 minutes chrono)

### 1. Cloner le repo
```bash
git clone https://github.com/AnandaTom/notaire-ai.git
cd notaire-ai
```

### 2. Configurer Git
```bash
git config user.email "votre-email@automai.fr"
git config user.name "Votre Nom"
```

### 3. Créer votre branche

**Augustin**:
```bash
git checkout -b augustin/dev
git push -u origin augustin/dev
```

**Payoss**:
```bash
git checkout -b payoss/dev
git push -u origin payoss/dev
```

### 4. Configurer les clés Supabase 🔐

```bash
# Copier le template
cp .env.template .env

# Ouvrir le fichier .env dans VS Code
code .env
```

Remplir ces 3 variables (je vous envoie les clés par **message sécurisé**):
- `SUPABASE_URL`: https://wcklvjckzktijtgakdrk.supabase.co
- `SUPABASE_PUBLISHABLE_KEY`: (voir message Signal/WhatsApp)
- `SUPABASE_SECRET_KEY`: (voir message Signal/WhatsApp)

⚠️ **IMPORTANT**: Ne jamais commiter le fichier `.env` sur GitHub (il est protégé par `.gitignore`).

## 🎯 Workflow quotidien (ULTRA-SIMPLE)

### Matin (9h00)
```
Double-clic sur START_DAY_AUGUSTIN.bat (ou PAYOSS.bat)
```
Ce script fait automatiquement:
- ✅ Merge toutes les PRs de la veille
- ✅ Sync votre branche avec master
- ✅ Lance auto-sync en arrière-plan

**Durée**: 30 secondes.

### Journée (9h01-18h00)
```
Travaillez normalement, faites juste Ctrl+S pour sauvegarder
```
Auto-sync fait automatiquement (en arrière-plan):
- ✅ Commit toutes les 30 minutes
- ✅ Push sur votre branche
- ✅ Sync avec master toutes les heures

**Vous n'avez RIEN à faire.**

### Soir (18h00)
```
Double-clic sur END_DAY.bat
```
Ce script fait automatiquement:
- ✅ Commit final de vos changements
- ✅ Push sur votre branche
- ✅ Crée une Pull Request

**Durée**: 10 secondes.

## 📊 Comparaison avant/après

| Action | Avant (manuel) | Après (ultra-simple) |
|--------|----------------|----------------------|
| **Matin** | 10 commandes git | 1 double-clic ✨ |
| **Journée** | git push x10 | 0 commande ✨ |
| **Soir** | 5 commandes git + PR | 1 double-clic ✨ |
| **Total/jour** | ~50 commandes | **2 clics** |

**Gain de temps**: ~30 min/jour = 2h30/semaine = **10h/mois**! 🚀

## 📚 Documentation disponible

Tout est documenté dans le repo:
- **NEXT_STEPS.md** → Ce qu'il faut faire (vous êtes ici)
- **WORKFLOW_SIMPLE.md** → Explication détaillée du workflow
- **WORKFLOW_PAR_DEV.md** → Différences entre les 3 devs
- **BEST_PRACTICES_3DEVS.md** → 10 règles d'or pour collaborer
- **COLLABORATION.md** → Éviter la perte de données

## 🎉 Premier jour idéal (Demain)

**9h00**: Les 3 (Tom, Augustin, Payoss) double-cliquent sur leur START_DAY
→ Tout le monde a la dernière version

**9h01-18h00**: Chacun travaille sur sa partie
→ Auto-sync synchronise en arrière-plan (invisible)

**18h00**: Les 3 double-cliquent sur END_DAY
→ 3 PRs créées automatiquement

**Lendemain 9h00**: START_DAY merge automatiquement les 3 PRs
→ Le cycle recommence avec le code combiné des 3

**Résultat**: Collaboration fluide, zéro perte de données, historique propre.

## ❓ Questions fréquentes

**Q: Que fait auto-sync exactement?**
R: Il commit + push toutes les 30 min, et sync avec master toutes les heures. Vous n'avez rien à faire, il tourne en arrière-plan.

**Q: Que se passe-t-il si j'oublie de lancer START_DAY le matin?**
R: Pas grave, lancez-le quand vous y pensez. Vous aurez juste un décalage avec master.

**Q: Que se passe-t-il si j'oublie END_DAY le soir?**
R: Pas grave, auto-sync a déjà commité + pushé vos changements. Vous devrez juste créer la PR manuellement le lendemain.

**Q: Puis-je continuer à travailler après END_DAY?**
R: Oui! La PR sera mise à jour automatiquement avec vos nouveaux commits.

**Q: Que faire si j'ai un conflit Git?**
R: Auto-sync détecte les conflits et vous alerte avec un son. Consultez COLLABORATION.md pour la résolution.

## 🚨 Points d'attention

### Sécurité
- ✅ `.env` est dans `.gitignore` (ne sera jamais commité)
- ✅ `.env.template` contient seulement des placeholders
- ⚠️ Ne jamais partager les clés par GitHub/Slack/email non sécurisé

### Git Flow
- ✅ Chaque dev travaille sur sa branche (augustin/dev, payoss/dev)
- ✅ PRs auto-créées chaque soir
- ✅ Merges semi-auto chaque matin
- ⚠️ Ne jamais travailler directement sur `master`

### Auto-sync
- ✅ Tourne en arrière-plan toute la journée
- ✅ Notifications sonores en cas de conflit
- ⚠️ Si vous éteignez VS Code, relancez START_DAY

## 📞 Support

**Problème?**
1. Consultez la doc (WORKFLOW_SIMPLE.md, etc.)
2. Demandez à Claude Code dans VS Code
3. Contactez Tom

**Bienvenue dans le workflow le plus simple du monde!** 🎉

Tom

---

## 🔐 Message sécurisé séparé (Signal/WhatsApp)

**À envoyer sur Signal/WhatsApp avec message auto-détruit activé:**

```
Clés Supabase NotaireAI:

SUPABASE_URL=https://wcklvjckzktijtgakdrk.supabase.co
SUPABASE_PUBLISHABLE_KEY=[VOTRE_CLE_PUBLISHABLE_ICI]
SUPABASE_SECRET_KEY=[VOTRE_CLE_SECRET_ICI]

Copiez-les dans votre fichier .env (voir email pour instructions).

⚠️ Supprimez ce message après avoir copié les clés.
```

---

## ✅ Checklist avant d'envoyer

- [ ] Remplacer `[VOTRE_CLE_PUBLISHABLE_ICI]` par votre vraie clé publishable
- [ ] Remplacer `[VOTRE_CLE_SECRET_ICI]` par votre vraie clé secret
- [ ] Envoyer l'email ci-dessus à Augustin et Payoss
- [ ] Envoyer les clés sur Signal/WhatsApp (message auto-détruit)
- [ ] Vérifier demain matin que tout le monde a fait le setup
