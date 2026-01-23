# Configuration Collaborateurs - Supabase MCP

Guide pour Augustin, Payos et les autres collaborateurs pour se connecter à Supabase via Claude Code.

## Prérequis

- VS Code avec l'extension Claude Code installée
- Node.js (pour npx)
- Accès au repo GitHub du projet

## Étape 1 : Cloner le repo (si pas déjà fait)

```bash
git clone https://github.com/votre-org/notaire-ai.git
cd notaire-ai
```

## Étape 2 : Créer votre Personal Access Token Supabase

1. Allez sur [supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
2. Connectez-vous avec le compte partagé ou demandez un accès à Tom
3. Cliquez sur **"Generate new token"**
4. Nom : `Claude Code - [Votre Prénom]`
5. **Copiez et sauvegardez le token** (il ne sera plus affiché)

## Étape 3 : Configurer le MCP Supabase

Copiez le template et ajoutez votre token :

```bash
# Windows PowerShell
copy .mcp.json.template .mcp.json

# Linux/Mac
cp .mcp.json.template .mcp.json
```

Éditez `.mcp.json` et remplacez `<YOUR_PERSONAL_ACCESS_TOKEN>` par votre token :

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--project-ref=wcklvjckzktijtgakdrk"
      ],
      "env": {
        "SUPABASE_ACCESS_TOKEN": "sbp_votre_token_ici"
      }
    }
  }
}
```

## Étape 4 : Configurer les variables d'environnement Python

Copiez le template et remplissez :

```bash
# Windows PowerShell
copy .env.template .env

# Linux/Mac
cp .env.template .env
```

Éditez `.env` avec les valeurs (demandez à Tom si besoin) :

```env
SUPABASE_URL=https://wcklvjckzktijtgakdrk.supabase.co
SUPABASE_KEY=votre_publishable_key
SUPABASE_SERVICE_KEY=votre_secret_key
ENCRYPTION_MASTER_KEY=clé_partagée_par_tom
```

## Étape 5 : Installer les dépendances Python

```bash
pip install supabase python-dotenv cryptography
```

## Étape 6 : Redémarrer VS Code

1. Fermez complètement VS Code
2. Rouvrez-le dans le dossier du projet
3. Ou : `Ctrl+Shift+P` → `Reload Window`

## Étape 7 : Tester la connexion

### Test MCP (dans Claude Code)

Demandez à Claude : "Liste les tables Supabase"

Il devrait répondre avec les tables : etudes, clients, dossiers, audit_logs, rgpd_requests

### Test Python

```bash
python execution/supabase_client.py
```

Sortie attendue :
```
Test de connexion Supabase...
URL: https://wcklvjckzktijtgakdrk.supabase.co
KEY: ****xxxx

OK: Connexion Supabase réussie

✓ Supabase est prêt à être utilisé!
Manager connecté: True
```

## Sécurité

⚠️ **IMPORTANT** :
- Ne commitez JAMAIS `.mcp.json` ou `.env` (ils sont dans `.gitignore`)
- Ne partagez pas votre Personal Access Token
- Chaque collaborateur a son propre token

## Informations Projet

| Paramètre | Valeur |
|-----------|--------|
| Project Ref | `wcklvjckzktijtgakdrk` |
| Region | Paris (eu-west-3) |
| Dashboard | [Supabase Dashboard](https://supabase.com/dashboard/project/wcklvjckzktijtgakdrk) |

## Aide

Si problème de connexion :
1. Vérifiez que votre token est valide sur le dashboard Supabase
2. Vérifiez que `.mcp.json` est bien formaté (JSON valide)
3. Redémarrez VS Code complètement
4. Contactez Tom

## Tables disponibles

| Table | Description |
|-------|-------------|
| `etudes` | Études notariales (multi-tenant) |
| `etude_users` | Utilisateurs par étude |
| `clients` | Clients avec PII chiffré |
| `dossiers` | Dossiers/actes notariaux |
| `audit_logs` | Logs d'audit RGPD |
| `rgpd_requests` | Demandes de droits RGPD |

## Commandes utiles dans Claude Code

```
# Lister les tables
"Liste les tables Supabase"

# Voir les clients
"Montre-moi les clients de l'étude X"

# Exécuter une requête
"Exécute cette requête SQL: SELECT * FROM etudes LIMIT 5"

# Créer une migration
"Crée une migration pour ajouter un champ email_secondaire à la table clients"
```
