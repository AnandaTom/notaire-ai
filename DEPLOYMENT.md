# Guide de Déploiement - NotaireAI

## Architecture

```
Local (VS Code) → GitHub → Modal (API) → Notaires (Frontend)
                              ↓
                          Supabase (DB partagée)
```

## Étapes de déploiement

### 1. Créer un compte Modal

1. Aller sur [modal.com](https://modal.com)
2. Créer un compte (gratuit pour commencer)
3. Installer Modal CLI : `pip install modal`
4. Authentifier : `modal token new`

### 2. Configurer les secrets Modal

```bash
# Ajouter les secrets nécessaires
modal secret create notaire-secrets \
  ANTHROPIC_API_KEY=sk-ant-... \
  SUPABASE_URL=https://xxx.supabase.co \
  SUPABASE_KEY=eyJ...
```

### 3. Créer le repository GitHub

```bash
# Dans le dossier du projet
git init
git add .
git commit -m "Initial commit - NotaireAI"
git remote add origin https://github.com/VOTRE_USERNAME/notaire-ai.git
git push -u origin main
```

### 4. Configurer GitHub Secrets

Dans GitHub → Settings → Secrets and variables → Actions :

- `MODAL_TOKEN_ID` : Votre token ID Modal
- `MODAL_TOKEN_SECRET` : Votre token secret Modal

### 5. Déployer le frontend

Option A - Vercel (recommandé) :
```bash
cd frontend
npx vercel
```

Option B - Netlify :
```bash
cd frontend
npm run build
# Déployer le dossier .next
```

### 6. Configurer Supabase (optionnel mais recommandé)

1. Créer un projet sur [supabase.com](https://supabase.com)
2. Créer les tables :

```sql
-- Table des améliorations proposées par les notaires
CREATE TABLE improvements (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  type TEXT NOT NULL, -- 'new_clause', 'correction', 'suggestion'
  content JSONB NOT NULL,
  submitted_by TEXT,
  status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des actes générés (anonymisé)
CREATE TABLE acts_generated (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  act_type TEXT NOT NULL,
  clauses_used TEXT[],
  format TEXT, -- 'pdf', 'docx'
  tokens_used INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table des clauses personnalisées
CREATE TABLE custom_clauses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  category TEXT NOT NULL, -- 'conditionnelle', 'optionnelle'
  name TEXT NOT NULL,
  content TEXT NOT NULL,
  conditions JSONB,
  approved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Workflow collaboratif

### Pour vous (administrateur)

1. Modifiez le code localement (VS Code + Claude)
2. Testez : `modal serve modal_app.py`
3. Committez et push : `git add . && git commit -m "..." && git push`
4. Le déploiement est automatique via GitHub Actions

### Pour les notaires

1. Utilisent le frontend (Vercel/Netlify)
2. Proposent des améliorations via l'interface
3. Les propositions sont stockées dans Supabase
4. Vous validez et intégrez les meilleures suggestions

## Coûts estimés

| Service | Gratuit jusqu'à | Ensuite |
|---------|-----------------|---------|
| Modal | ~$30/mois crédit | ~$0.001/requête |
| Vercel | 100GB bandwidth | $20/mois |
| Supabase | 500MB DB | $25/mois |
| Claude API | - | ~$0.02/acte |

**Total estimé** : ~$50-100/mois pour un usage modéré (100 actes/mois)

## Commandes utiles

```bash
# Déployer manuellement sur Modal
modal deploy modal_app.py

# Tester localement
modal serve modal_app.py

# Voir les logs
modal logs notaire-ai

# Mettre à jour les templates
modal volume put notaire-templates templates/ /templates/
```
