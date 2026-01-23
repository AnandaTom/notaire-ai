# Guide de Configuration Supabase - NotaireAI

## Checklist Rapide

- [ ] Étape 1 : Créer le projet Supabase (Paris)
- [ ] Étape 2 : Récupérer les clés API
- [ ] Étape 3 : Générer la clé de chiffrement
- [ ] Étape 4 : Créer le fichier .env
- [ ] Étape 5 : Activer les extensions PostgreSQL
- [ ] Étape 6 : Appliquer les migrations SQL
- [ ] Étape 7 : Installer les dépendances Python
- [ ] Étape 8 : Tester l'installation

---

## Étape 1 : Créer le Projet Supabase (Paris)

1. Allez sur https://supabase.com/dashboard
2. Cliquez sur **"New Project"**
3. Configurez :
   - **Name** : `notaire-ai-prod`
   - **Database Password** : Générez un mot de passe fort (gardez-le !)
   - **Region** : `EU West (Paris)` ✓
   - **Pricing Plan** : Free tier pour commencer
4. Cliquez **"Create new project"** et attendez ~2 minutes

---

## Étape 2 : Récupérer les Clés API

Dans votre projet Supabase :

1. Allez dans **Settings** → **API**
2. Copiez :
   - **Project URL** : `https://xxx.supabase.co`
   - **anon public key** : pour `SUPABASE_KEY`
   - **service_role key** : pour `SUPABASE_SERVICE_KEY`

> ⚠️ **IMPORTANT** : La `service_role key` est secrète ! Ne jamais l'exposer côté client.

---

## Étape 3 : Générer la Clé de Chiffrement

Exécutez dans votre terminal :

```bash
cd "C:\Users\tomra\OneDrive\Dokumente\Agence IA Automatisation\Agentic Workflows\Agent AI Création & Modification d'actes notariaux"
python execution/encryption_service.py generate-key
```

> ⚠️ **CRITIQUE** : Sauvegardez cette clé dans un endroit sécurisé (gestionnaire de mots de passe).
> La perte de cette clé = perte des données chiffrées !

---

## Étape 4 : Créer le fichier .env

1. Copiez `.env.template` vers `.env`
2. Remplissez les valeurs :

```env
# Supabase (depuis l'étape 2)
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-anon-key
SUPABASE_SERVICE_KEY=votre-service-role-key

# Chiffrement (depuis l'étape 3)
ENCRYPTION_MASTER_KEY=la-cle-generee

# Agent
AGENT_USER_ID=agent-notaire-ia
AGENT_NAME=NotaireAI Agent
```

---

## Étape 5 : Activer les Extensions PostgreSQL

Dans Supabase → **SQL Editor**, exécutez :

```sql
-- Extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

---

## Étape 6 : Appliquer les Migrations SQL

Dans **SQL Editor**, exécutez les fichiers dans cet ordre :

| Ordre | Fichier | Description |
|-------|---------|-------------|
| 1 | `migrations/001_core_tables.sql` | Tables principales |
| 2 | `migrations/002_rls_policies.sql` | Politiques RLS |
| 3 | `migrations/003_audit_trail.sql` | Logs d'audit |
| 4 | `migrations/004_gdpr_requests.sql` | Gestion RGPD |

> 💡 **Astuce** : Copiez-collez le contenu de chaque fichier dans l'éditeur SQL et exécutez.

---

## Étape 7 : Installer les Dépendances Python

```bash
pip install -r requirements.txt
```

Ou avec un environnement virtuel :

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## Étape 8 : Tester l'Installation

### Test du chiffrement
```bash
python execution/encryption_service.py generate-key
```

### Tests unitaires
```bash
python -m pytest tests/test_security.py -v
```

### Test de connexion Supabase
```python
from execution.secure_client_manager import SecureClientManager

manager = SecureClientManager(etude_id="test")
print("Connexion OK!" if manager.supabase else "Mode offline")
```

---

## Vérification Finale

- [ ] Clé de chiffrement générée et stockée sécurisée
- [ ] Fichier `.env` créé avec toutes les variables
- [ ] Extensions PostgreSQL activées
- [ ] 4 migrations SQL appliquées sans erreur
- [ ] RLS activé sur toutes les tables
- [ ] Tests de sécurité passent
- [ ] Connexion Supabase fonctionne

---

## Dépannage

### Erreur "supabase not found"
```bash
pip install supabase
```

### Erreur "cryptography not found"
```bash
pip install cryptography
```

### Mode offline activé
Vérifiez que les variables `SUPABASE_URL` et `SUPABASE_KEY` sont correctes dans `.env`.

### RLS bloque les requêtes
Assurez-vous d'avoir créé une étude et un utilisateur associé avant de tester.

---

## Ressources

- [Documentation Supabase](https://supabase.com/docs)
- [DPA Supabase (RGPD)](https://supabase.com/legal/dpa)
- [Cryptography Python](https://cryptography.io/en/latest/)

---

*Dernière mise à jour : Janvier 2026*
