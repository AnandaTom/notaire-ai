# Déploiement Agent NotaireAI - Multi-Tenant

Guide pour déployer un agent NotaireAI pour un nouveau notaire (client).

## Architecture Multi-Tenant

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SUPABASE (Unique)                             │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Table: etudes                                                      │  │
│  │  ├── Maître Dupont (etude-001) ──┐                                │  │
│  │  ├── Maître Martin (etude-002) ──┼── Données isolées par RLS     │  │
│  │  └── Maître Bernard (etude-003) ─┘                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Agent Dupont    │  │ Agent Martin    │  │ Agent Bernard   │         │
│  │ API_KEY=nai_abc │  │ API_KEY=nai_def │  │ API_KEY=nai_ghi │         │
│  │ → etude-001     │  │ → etude-002     │  │ → etude-003     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Principe clé** : Chaque agent a sa propre clé API (`NOTAIRE_API_KEY`) qui détermine automatiquement à quelle étude il appartient. Impossible d'accéder aux données d'une autre étude.

## Processus d'Onboarding (5 min)

### Étape 1 : Créer l'étude et générer les credentials

```bash
# Mode interactif
python execution/onboarding_notaire.py

# Ou en ligne de commande
python execution/onboarding_notaire.py \
    --nom "Maître Dupont - Paris 8e" \
    --siret "12345678901234" \
    --email "contact@dupont-notaire.fr" \
    --output .tmp/config_dupont.json
```

**Sortie :**
```
============================================================
  ONBOARDING TERMINÉ - CONFIGURATION AGENT
============================================================

📋 Étude: Maître Dupont - Paris 8e
   ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
   SIRET: 12345678901234

🔑 Variables d'environnement pour l'agent:
------------------------------------------------------------
NOTAIRE_API_KEY=nai_abc123def456ghi789jkl012mno345pqr678
NOTAIRE_ETUDE_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
SUPABASE_URL=https://wcklvjckzktijtgakdrk.supabase.co
------------------------------------------------------------

⚠️  IMPORTANT:
   - La clé API ne sera PLUS JAMAIS affichée
   - Copiez-la maintenant dans le .env de l'agent
   - En cas de perte, générez une nouvelle clé
```

### Étape 2 : Configurer l'agent Modal

Dans le fichier de déploiement Modal de l'agent :

```python
# modal_agent.py
import modal

app = modal.App("notaire-dupont")

# Secrets depuis Modal Dashboard
secrets = modal.Secret.from_name("notaire-dupont-secrets")

@app.function(secrets=[secrets])
def agent_handler(request):
    from execution.agent_database import AgentDB

    # Connexion automatique avec la clé API
    db = AgentDB()  # Utilise NOTAIRE_API_KEY automatiquement

    # Toutes les opérations sont filtrées par étude
    clients = db.get_all_clients()  # Uniquement les clients de Maître Dupont
    dossiers = db.get_all_dossiers()  # Uniquement ses dossiers
```

**Créer les secrets Modal :**
```bash
modal secret create notaire-dupont-secrets \
    NOTAIRE_API_KEY="nai_abc123def456ghi789jkl012mno345pqr678" \
    SUPABASE_URL="https://wcklvjckzktijtgakdrk.supabase.co" \
    SUPABASE_SERVICE_KEY="eyJ..."
```

### Étape 3 : Tester l'isolation

```python
# Test que l'agent ne voit que ses données
from execution.agent_database import AgentDB

# Agent Dupont
db_dupont = AgentDB(api_key="nai_abc...")
print(db_dupont.etude_id)  # → a1b2c3d4-...
print(db_dupont.get_all_clients())  # → Uniquement clients Dupont

# Agent Martin (autre clé)
db_martin = AgentDB(api_key="nai_def...")
print(db_martin.etude_id)  # → x9y8z7w6-...
print(db_martin.get_all_clients())  # → Uniquement clients Martin
```

## Gestion des Clés API

### Générer une nouvelle clé (si perdue)

```python
from execution.onboarding_notaire import create_api_key
from supabase import create_client

client = create_client(url, service_key)
etude_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

new_key = create_api_key(client, etude_id, name="Agent Backup")
print(new_key["api_key"])  # Sauvegarder immédiatement !
```

### Révoquer une clé compromise

```sql
-- Dans Supabase SQL Editor
UPDATE agent_api_keys
SET revoked_at = now(),
    revoked_reason = 'Compromission suspectée'
WHERE key_prefix = 'abc12345';
```

### Lister les clés d'une étude

```sql
SELECT name, key_prefix, created_at, last_used_at, revoked_at
FROM agent_api_keys
WHERE etude_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

## Automatisation Complète

Pour déployer un agent automatiquement à la signature d'un contrat :

```python
# webhook_nouveau_client.py
import json
from execution.onboarding_notaire import onboard_notaire

def handle_new_client(webhook_data):
    """Appelé quand un nouveau notaire signe un contrat."""

    # 1. Créer l'étude et les credentials
    config = onboard_notaire(
        nom=webhook_data["nom_etude"],
        siret=webhook_data["siret"],
        email=webhook_data["email"]
    )

    # 2. Créer les secrets Modal via API
    create_modal_secrets(
        name=f"notaire-{config['etude']['id'][:8]}",
        secrets=config['agent_config']
    )

    # 3. Déployer l'agent Modal
    deploy_modal_agent(
        app_name=f"notaire-{config['etude']['id'][:8]}",
        secrets_name=f"notaire-{config['etude']['id'][:8]}"
    )

    # 4. Envoyer les infos de connexion au notaire
    send_welcome_email(
        email=webhook_data["email"],
        agent_url=f"https://notaire-{config['etude']['id'][:8]}.modal.run"
    )

    return config
```

## Checklist Déploiement

- [ ] Créer l'étude avec `onboarding_notaire.py`
- [ ] Sauvegarder la clé API (ne sera plus affichée)
- [ ] Configurer les secrets Modal
- [ ] Déployer l'agent
- [ ] Tester l'isolation des données
- [ ] Envoyer les accès au notaire
- [ ] Former le notaire sur l'utilisation

## Sécurité

| Aspect | Protection |
|--------|------------|
| Isolation données | RLS Postgres + etude_id automatique |
| Authentification | Clé API hashée (SHA256) |
| Rate limiting | 60 req/min par défaut |
| Audit | Logs complets dans audit_logs |
| Révocation | Possible immédiatement |
| Expiration | Optionnelle (configurable) |

## Troubleshooting

### "etude_id requis"
La clé API n'a pas pu être validée. Vérifiez :
- La variable `NOTAIRE_API_KEY` est correcte
- La clé n'a pas été révoquée
- La clé n'a pas expiré

### "Clé API invalide ou expirée"
Générez une nouvelle clé via `create_api_key()`.

### Données mélangées entre études
Impossible si vous utilisez `AgentDB` correctement. Vérifiez que vous n'override pas manuellement `etude_id`.
