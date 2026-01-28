# Modal - Déploiement Serverless NotaireAI

Ce dossier contient tous les fichiers de déploiement Modal.com.

## Fichiers

| Fichier | Description |
|---------|-------------|
| `modal_app.py` | **Application principale** - FastAPI, CRON jobs, scaling multi-tenant |
| `modal_app_legacy.py` | Version simplifiée - génération, chat, sync |
| `__init__.py` | Module Python |

## Déploiement

```bash
# Déploiement production
modal deploy modal/modal_app.py

# Test local (hot reload)
modal serve modal/modal_app.py
```

## Endpoints

Une fois déployé, l'API est accessible à:

```
https://notaire-ai--fastapi-app.modal.run/
```

### Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Statut du service |
| `/agent/execute` | POST | Exécuter une demande en langage naturel |
| `/agent/feedback` | POST | Soumettre feedback pour apprentissage |
| `/dossiers` | GET/POST | Lister/Créer dossiers |
| `/dossiers/{id}` | GET/PATCH/DELETE | CRUD dossier |
| `/clauses/sections` | GET | Lister les 65 sections (44 fixes + 21 variables) |
| `/clauses/profils` | GET | Lister les profils pré-configurés |
| `/clauses/analyser` | POST | Analyser données et sélectionner sections |
| `/clauses/feedback` | POST | Soumettre feedback clause |
| `/clauses/suggestions` | GET | Suggestions contextuelles |
| `/stats` | GET | Statistiques d'utilisation |
| `/me` | GET | Info étude authentifiée |

## Architecture

```
modal/
├── modal_app.py           # App principale
│   ├── fastapi_app()      # Point d'entrée ASGI
│   ├── daily_learning_job() # CRON quotidien 2h
│   ├── weekly_catalog_sync() # CRON hebdo dimanche 3h
│   ├── generate_deed()    # Génération acte
│   └── parse_request()    # Parsing NL
│
└── modal_app_legacy.py    # Version legacy
    ├── generate_act()     # Génération simple
    ├── chat_with_notaire() # Chat Claude
    └── sync_knowledge_base() # Sync Supabase
```

## Configuration

### Secrets requis

Créer dans Modal Dashboard (`modal.com/secrets`):

1. **supabase-credentials**:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_KEY` (optionnel)

2. **notaire-secrets** (pour legacy):
   - `ANTHROPIC_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

### Volumes

| Volume | Usage |
|--------|-------|
| `notaire-ai-outputs` | Fichiers générés (persistant) |
| `notaire-templates` | Templates (legacy) |

## Jobs CRON

| Job | Schedule | Description |
|-----|----------|-------------|
| `daily_learning_job` | 2h00 tous les jours | Analyse patterns faibles, améliore le parsing |
| `weekly_catalog_sync` | 3h00 le dimanche | Propage nouvelles clauses validées |

## Multi-tenant

L'API supporte le multi-tenant via Supabase RLS:
- Chaque étude a ses propres dossiers isolés
- Authentification par API Key (`X-API-Key` header)
- Permissions granulaires (read/write/delete)
