# Guide de Déploiement Modal - Notomai

Ce guide vous accompagne pas à pas pour déployer l'agent Notomai sur Modal.com, une plateforme serverless qui permet d'exécuter votre agent 24/7 avec scaling automatique.

## Table des matières

1. [Pourquoi Modal ?](#pourquoi-modal-)
2. [Prérequis](#prérequis)
3. [Étape 1 : Créer un compte Modal](#étape-1--créer-un-compte-modal)
4. [Étape 2 : Installer Modal CLI](#étape-2--installer-modal-cli)
5. [Étape 3 : Configurer les secrets](#étape-3--configurer-les-secrets)
6. [Étape 4 : Tester en local](#étape-4--tester-en-local)
7. [Étape 5 : Déployer en production](#étape-5--déployer-en-production)
8. [Étape 6 : Configurer le domaine](#étape-6--configurer-le-domaine)
9. [Architecture Multi-tenant](#architecture-multi-tenant)
10. [Self-Annealing (Amélioration continue)](#self-annealing-amélioration-continue)
11. [Monitoring et Logs](#monitoring-et-logs)
12. [Coûts et Facturation](#coûts-et-facturation)
13. [Dépannage](#dépannage)

---

## Pourquoi Modal ?

Modal.com offre plusieurs avantages pour Notomai :

| Avantage | Description |
|----------|-------------|
| **Serverless** | Pas de serveur à gérer, scaling automatique de 0 à N instances |
| **Pay-per-use** | Facturé uniquement quand l'agent est utilisé |
| **Cold start rapide** | ~1-2 secondes pour démarrer une instance |
| **Jobs planifiés** | Cron jobs intégrés pour l'apprentissage continu |
| **Secrets intégrés** | Gestion sécurisée des clés API |
| **Volumes persistants** | Stockage des fichiers générés |

---

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.11+** installé
- **pip** à jour : `python -m pip install --upgrade pip`
- **Git** installé
- Un compte **Supabase** (pour la base de données) - [supabase.com](https://supabase.com)
- Une **carte bancaire** (Modal offre $30 de crédits gratuits, mais requiert une CB)

---

## Étape 1 : Créer un compte Modal

### 1.1 Inscription

1. Allez sur [modal.com](https://modal.com)
2. Cliquez sur **"Get Started"** ou **"Sign Up"**
3. Inscrivez-vous avec :
   - **GitHub** (recommandé - plus simple)
   - **Google**
   - **Email/mot de passe**

### 1.2 Vérification

1. Confirmez votre email si demandé
2. Modal vous attribuera automatiquement **$30 de crédits gratuits**

### 1.3 Interface Modal

Une fois connecté, vous verrez le dashboard Modal avec :
- **Apps** : Vos applications déployées
- **Secrets** : Variables d'environnement sécurisées
- **Volumes** : Stockage persistant
- **Logs** : Journaux d'exécution

---

## Étape 2 : Installer Modal CLI

### 2.1 Installation

Ouvrez un terminal et exécutez :

```bash
pip install modal
```

### 2.2 Authentification

Connectez Modal CLI à votre compte :

```bash
modal token new
```

Cette commande :
1. Ouvrira votre navigateur
2. Vous demandera de vous connecter à Modal
3. Créera un token local dans `~/.modal.toml`

### 2.3 Vérification

Testez que tout fonctionne :

```bash
modal --version
```

Vous devriez voir quelque chose comme `modal 0.55.xxx`

---

## Étape 3 : Configurer les secrets

Les secrets permettent de stocker vos clés API de manière sécurisée.

### 3.1 Créer le secret Supabase

1. Allez sur [modal.com/secrets](https://modal.com/secrets)
2. Cliquez sur **"Create new secret"**
3. Choisissez **"Custom"**
4. Nom du secret : `supabase-credentials`
5. Ajoutez ces variables :

| Clé | Valeur | Où la trouver |
|-----|--------|---------------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase → Settings → API → Project URL |
| `SUPABASE_KEY` | `eyJ...` (anon key) | Supabase → Settings → API → anon public |
| `SUPABASE_SERVICE_KEY` | `eyJ...` (service role) | Supabase → Settings → API → service_role |

### 3.2 Via CLI (alternative)

Vous pouvez aussi créer le secret via terminal :

```bash
modal secret create supabase-credentials \
  SUPABASE_URL="https://votre-projet.supabase.co" \
  SUPABASE_KEY="eyJvotre_anon_key..." \
  SUPABASE_SERVICE_KEY="eyJvotre_service_key..."
```

### 3.3 Vérifier les secrets

```bash
modal secret list
```

Vous devriez voir `supabase-credentials` dans la liste.

---

## Étape 4 : Tester en local

Avant de déployer, testez l'application localement.

### 4.1 Mode développement

Depuis la racine du projet :

```bash
modal serve api/modal_app.py
```

Cette commande :
1. Démarre un serveur local
2. Affiche l'URL temporaire (ex: `https://xxx--notaire-ai--fastapi-app-dev.modal.run`)
3. Recharge automatiquement à chaque modification

### 4.2 Tester les endpoints

Dans un autre terminal, testez l'API :

```bash
# Health check
curl https://xxx--notaire-ai--fastapi-app-dev.modal.run/health

# Liste des dossiers (nécessite auth)
curl https://xxx--notaire-ai--fastapi-app-dev.modal.run/dossiers \
  -H "Authorization: Bearer VOTRE_JWT_SUPABASE"
```

### 4.3 Arrêter le serveur

Appuyez sur `Ctrl+C` pour arrêter le serveur de développement.

---

## Étape 5 : Déployer en production

### 5.1 Déploiement

```bash
modal deploy api/modal_app.py
```

Cette commande :
1. Construit l'image Docker avec les dépendances
2. Déploie l'application sur l'infrastructure Modal
3. Active les cron jobs (apprentissage quotidien, sync hebdomadaire)
4. Affiche les URLs de production

### 5.2 URLs de production

Après déploiement, vos endpoints seront :

| Endpoint | URL |
|----------|-----|
| API principale | `https://notaire-ai--fastapi-app.modal.run/` |
| Health check | `https://notaire-ai--fastapi-app.modal.run/health` |
| Exécuter agent | `https://notaire-ai--fastapi-app.modal.run/agent/execute` |
| Dossiers | `https://notaire-ai--fastapi-app.modal.run/dossiers` |

### 5.3 Vérifier le déploiement

1. Allez sur [modal.com/apps](https://modal.com/apps)
2. Vous devriez voir `notaire-ai` dans la liste
3. Cliquez dessus pour voir les logs et métriques

---

## Étape 6 : Configurer le domaine

Par défaut, Modal utilise des URLs `*.modal.run`. Vous pouvez configurer un domaine personnalisé.

### 6.1 Via Dashboard Modal

1. Allez dans votre app `notaire-ai`
2. Section **"Custom domains"**
3. Ajoutez votre domaine (ex: `api.notomai.fr`)
4. Configurez le DNS chez votre registrar

### 6.2 Configuration DNS

Ajoutez un enregistrement CNAME :

```
api.notomai.fr  →  notaire-ai--fastapi-app.modal.run
```

---

## Architecture Multi-tenant

Notomai est conçu pour servir plusieurs études notariales de manière isolée.

### Comment ça marche ?

```
┌─────────────────────────────────────────────────────────────┐
│                    Modal (Serverless)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   API FastAPI                         │    │
│  │  /agent/execute  /dossiers  /health                  │    │
│  └────────────────────────┬────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Supabase (Multi-tenant)                  │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │  Étude A    │ │  Étude B    │ │  Étude C    │    │    │
│  │  │  (RLS)      │ │  (RLS)      │ │  (RLS)      │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Row Level Security (RLS)

Chaque étude ne voit que ses propres données grâce aux politiques RLS de Supabase :

```sql
-- Exemple de politique RLS
CREATE POLICY "Users can only see their own etude's data"
ON dossiers
FOR ALL
USING (etude_id = auth.jwt() ->> 'etude_id');
```

---

## Self-Annealing (Amélioration continue)

Le principe de **self-annealing** de CLAUDE.md est implémenté via des jobs automatiques.

### Jobs planifiés

| Job | Fréquence | Description |
|-----|-----------|-------------|
| `daily_learning_job` | Tous les jours à 2h | Analyse les patterns à améliorer |
| `weekly_catalog_sync` | Tous les dimanches à 3h | Synchronise les catalogues de clauses |

### Ce que fait le job quotidien

1. **Analyse les exécutions à faible confiance** (< 70%)
2. **Identifie les champs fréquemment corrigés**
3. **Génère un rapport** stocké dans `audit_logs`
4. **Enrichit les patterns** pour améliorer le parsing

### Voir les rapports

```sql
-- Dans Supabase SQL Editor
SELECT * FROM audit_logs
WHERE action = 'daily_learning_report'
ORDER BY created_at DESC
LIMIT 10;
```

### Enrichir manuellement

Quand vous identifiez une nouvelle clause ou un pattern :

1. Ajoutez-le dans `schemas/clauses_catalogue.json`
2. Redéployez : `modal deploy api/modal_app.py`

---

## Monitoring et Logs

### Dashboard Modal

1. Allez sur [modal.com/apps](https://modal.com/apps)
2. Sélectionnez `notaire-ai`
3. Onglets disponibles :
   - **Deployments** : Historique des déploiements
   - **Logs** : Journaux en temps réel
   - **Metrics** : CPU, mémoire, latence
   - **Cron** : État des jobs planifiés

### Logs en temps réel

```bash
modal app logs notaire-ai
```

### Logs des cron jobs

```bash
modal app logs notaire-ai --function daily_learning_job
```

---

## Coûts et Facturation

### Tarification Modal (janvier 2026)

| Ressource | Prix |
|-----------|------|
| CPU (par seconde) | $0.000016 / CPU-second |
| Mémoire (par seconde) | $0.000002 / GB-second |
| GPU (optionnel) | Variable selon le modèle |
| Stockage volumes | $0.30 / GB / mois |

### Estimation pour Notomai

Avec une utilisation typique (10-50 actes/jour) :

| Composant | Estimation mensuelle |
|-----------|---------------------|
| API (requêtes) | ~$5-15 |
| Cron jobs | ~$1-2 |
| Stockage | ~$1-3 |
| **Total** | **~$7-20/mois** |

### Crédits gratuits

- **$30 offerts** à l'inscription
- Suffisant pour ~2-3 mois d'utilisation modérée

### Configurer les alertes

1. Dashboard Modal → Settings → Billing
2. Configurez une alerte à $20/mois

---

## Dépannage

### Erreur : "Secret not found"

```bash
# Vérifiez que le secret existe
modal secret list

# Recréez-le si nécessaire
modal secret create supabase-credentials ...
```

### Erreur : "Container timeout"

Le timeout par défaut est 5 minutes. Si vous avez des actes complexes :

```python
# Dans modal_app.py, augmentez le timeout
@app.function(timeout=600)  # 10 minutes
```

### Erreur : "Volume not mounted"

```bash
# Créez le volume manuellement
modal volume create notaire-ai-outputs
```

### Logs vides

```bash
# Forcez un redéploiement
modal deploy api/modal_app.py --force
```

### Tester un endpoint spécifique

```bash
# Test local de la fonction parse_request
modal run api/modal_app.py::parse_request --texte "Créer promesse Martin→Dupont, 450000€"
```

---

## Prochaines étapes

1. **Configurer le front-end** pour appeler l'API Modal
2. **Ajouter d'autres agents** (voir section Architecture)
3. **Configurer les webhooks** Supabase pour notifications

---

## Architecture pour plusieurs agents

Pour développer d'autres agents, créez de nouveaux fichiers dans `api/` :

```
api/
├── modal_app.py           # Agent création d'actes (actuel)
├── modal_extraction.py    # Agent extraction de titres
├── modal_validation.py    # Agent validation juridique
└── modal_archivage.py     # Agent archivage et recherche
```

Chaque agent peut avoir ses propres :
- Endpoints REST
- Jobs planifiés
- Volumes de stockage
- Ressources (CPU/mémoire)

---

## Support

- **Documentation Modal** : [modal.com/docs](https://modal.com/docs)
- **Discord Modal** : [modal.com/slack](https://modal.com/slack)
- **Issues Notomai** : GitHub du projet

---

*Guide créé le 26 janvier 2026 - Version 1.0*
