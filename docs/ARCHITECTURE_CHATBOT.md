# Architecture du Chatbot NotaireAI

> Documentation technique complète du chatbot intelligent pour la génération d'actes notariaux.
> Ce document explique le fonctionnement en termes simples et techniques.

**Version** : 2.3.0
**Dernière mise à jour** : 11 février 2026
**Auteur** : Claude Opus 4.5

---

## En une phrase

Le notaire discute avec un assistant intelligent (Claude, par Anthropic) qui lui pose les bonnes questions, enregistre les réponses dans une base de données, et génère le document final (promesse de vente ou acte de vente) au format Word.

---

## Statut actuel : FONCTIONNEL

| Composant | Statut | Notes |
|-----------|--------|-------|
| Chat `/chat/` | ✅ OK | Persistance complète |
| Streaming `/chat/stream` | ✅ OK | SSE avec conversation_id |
| Génération documents | ✅ OK | URLs signées HMAC |
| Persistance BDD | ✅ OK | Conversations créées automatiquement |
| Health check | ✅ OK | Test Supabase au démarrage |

---

## Le parcours d'une conversation

```
 NOTAIRE                    NOTRE SERVEUR                   CLAUDE (IA)
    |                            |                              |
    |  "Je veux créer une        |                              |
    |   promesse pour un         |                              |
    |   appartement"             |                              |
    |--------------------------->|                              |
    |                            |                              |
    |                            |  1. Génère un UUID si        |
    |                            |     conversation_id absent   |
    |                            |                              |
    |                            |  2. Crée la conversation     |
    |                            |     dans Supabase            |
    |                            |                              |
    |                            |  3. Envoie le message        |
    |                            |     à Claude via SSE         |
    |                            |----------------------------->|
    |                            |                              |
    |                            |  4. Claude détecte que       |
    |                            |     c'est un appartement     |
    |                            |     (= copropriété)          |
    |                            |                              |
    |                            |  5. Claude collecte les      |
    |                            |     données et les stocke    |
    |                            |     dans agent_state         |
    |                            |<-----------------------------|
    |                            |                              |
    |  "Pouvez-vous me donner   |                              |
    |   le nom du vendeur ?"    |  6. Réponse streamée +       |
    |<--- SSE stream ------------|     conversation_id          |
    |                            |                              |
    |  [Message suivant avec     |                              |
    |   conversation_id]         |  7. Charge historique        |
    |--------------------------->|     depuis Supabase          |
    |                            |     et continue...           |
```

---

## Les 5 composants principaux

### 1. Le frontend (ce que voit le notaire)

Page web Next.js 14 avec :
- Zone de conversation (chat) avec rendu Markdown
- Boutons de suggestion contextuels
- Barre de progression (pourcentage collecte)
- Boutons feedback (pouce haut/bas) sur chaque réponse
- Historique des conversations (sidebar)
- Lien de téléchargement sécurisé (URL signée)

**Persistence** : `userId` et `conversationId` stockés en localStorage.

| Fichier | Rôle |
|---------|------|
| `frontend/app/page.tsx` | Page principale, appels API, persistence |
| `frontend/components/ChatArea.tsx` | Zone de chat, feedback, suggestions |
| `frontend/components/Sidebar.tsx` | Historique conversations |
| `frontend/components/Header.tsx` | Titre, barre de progression |

### 2. Le serveur Modal (le cerveau)

Modal est un service cloud serverless. Quand le notaire envoie un message :

1. Réception du message
2. **Génération automatique d'un `conversation_id`** si non fourni
3. **Création de la conversation** dans Supabase (si nouvelle)
4. Chargement de l'historique depuis `conversations.messages` (JSONB)
5. Envoi à Claude via SSE streaming
6. Exécution des outils demandés par Claude
7. **Sauvegarde** des messages + `agent_state` dans Supabase
8. Retour du `conversation_id` au frontend

**Workspace Modal** : `notomai`
**URL API** : `https://notomai--notaire-ai-fastapi-app.modal.run`

### 3. Claude et ses 8 outils

Claude (modèle `claude-sonnet-4`) dispose de 8 outils pour effectuer des actions :

| Outil | Fonction | Exemple |
|-------|----------|---------|
| `detect_property_type` | Identifie le type de bien | "appartement" → copropriété |
| `get_questions` | Récupère les questions par section | Section "vendeur" → 8 questions |
| `submit_answers` | Enregistre les réponses | Nom: Dupont, Adresse: 12 rue... |
| `get_collection_progress` | Calcule la progression | 45% terminé, 12 champs manquants |
| `validate_deed_data` | Vérifie la cohérence | Erreur: quotités ≠ 100% |
| `generate_document` | Crée le DOCX final | promesse_20260211.docx |
| `search_clauses` | Recherche dans le catalogue | "condition suspensive prêt" |
| `submit_feedback` | Enregistre un retour notaire | "Ajouter clause sur..." |

**Fonctionnement** : Claude pilote les outils comme un chef de projet. Il ne génère pas le document lui-même.

### 4. Supabase (la mémoire)

Base de données PostgreSQL stockant :

| Table | Colonnes clés | Usage |
|-------|---------------|-------|
| `conversations` | id, messages (JSONB), agent_state (JSONB), context, message_count | Historique complet |
| `feedbacks` | conversation_id, rating, correction | Retours notaires |
| `etudes` | id, nom, siret | Isolation multi-tenant |
| `notaire_users` | id, etude_id, auth_user_id | Utilisateurs |

**Schéma conversations** :
```sql
id              UUID PRIMARY KEY
etude_id        UUID REFERENCES etudes(id)
user_id         UUID REFERENCES auth.users(id)
messages        JSONB DEFAULT '[]'
agent_state     JSONB DEFAULT '{}'
context         JSONB DEFAULT '{}'
message_count   INTEGER DEFAULT 0
last_message_at TIMESTAMPTZ
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### 5. Les endpoints API

| Endpoint | Méthode | Rôle |
|----------|---------|------|
| `/health` | GET | Santé du service (teste Supabase) |
| `/chat/` | POST | Message → réponse + conversation_id |
| `/chat/stream` | POST | Message → SSE streaming + conversation_id |
| `/chat/conversations` | GET | Liste des 20 dernières conversations |
| `/chat/conversations/{id}` | GET | Charge une conversation complète |
| `/chat/feedback` | POST | Enregistre un feedback |
| `/download/{filename}` | GET | Téléchargement sécurisé (URL signée) |

---

## Sécurité

| Protection | Explication |
|------------|-------------|
| **Chiffrement clients** | Données chiffrées AES-256 en base |
| **URLs signées** | Téléchargements avec HMAC-SHA256, expiration 1h |
| **CORS restreint** | Seuls domaines autorisés |
| **Rate limiting** | 60 req/min par clé API |
| **RLS Supabase** | Isolation par étude |
| **Health check** | Test Supabase au démarrage |
| **Fallback** | ChatHandler par mots-clés si Claude indisponible |

---

## Flux de persistance (v2.3)

```python
# 1. Génération automatique d'UUID si absent
conversation_id = request.conversation_id or str(uuid.uuid4())

# 2. Création conversation si nouvelle
if not exists:
    supabase.table("conversations").insert({
        "id": conversation_id,
        "etude_id": REAL_ETUDE_ID,
        "user_id": REAL_USER_ID,
        "messages": [],
        "message_count": 0,
    }).execute()

# 3. Après réponse Claude, sauvegarde messages + état
supabase.table("conversations").update({
    "messages": existing + [user_msg, assistant_msg],
    "message_count": len(messages),
    "last_message_at": datetime.now().isoformat(),
    "agent_state": agent.state,
}).eq("id", conversation_id).execute()

# 4. Retour conversation_id au frontend
return {"conversation_id": conversation_id, "content": "..."}
```

---

## Schéma technique complet

```
┌─────────────────────────────────────────────┐
│  NAVIGATEUR WEB (Next.js 14)                │
│                                              │
│  ┌──────────────┐ ┌─────────────────────┐   │
│  │  Sidebar     │ │  ChatArea           │   │
│  │              │ │                      │   │
│  │ - Historique │ │  - Messages          │   │
│  │ - Nouvelle   │ │  - Feedback 👍👎    │   │
│  │   conv.      │ │  - Suggestions       │   │
│  │              │ │  - Download link     │   │
│  └──────────────┘ └─────────────────────┘   │
│                                              │
│  localStorage: userId, conversationId        │
└────────┬────────────────────────────────────┘
         │
         │  POST /chat/ {message, conversation_id?}
         │  → Réponse: {content, conversation_id}
         ▼
┌─────────────────────────────────────────────────────────┐
│  SERVEUR MODAL  (notomai workspace)                      │
│  https://notomai--notaire-ai-fastapi-app.modal.run       │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  STARTUP: Health check Supabase                     │ │
│  │  "✅ Supabase connecté" ou "⚠️ Supabase non dispo" │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  api/main.py → chat_handler.py                           │
│                                                           │
│  1. Génère UUID si conversation_id absent                │
│  2. Crée conversation si nouvelle                        │
│  3. Charge historique + context depuis Supabase          │
│  4. Délègue à AnthropicAgent                             │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ANTHROPIC AGENT  (anthropic_agent.py)             │  │
│  │                                                     │  │
│  │  - Prépare messages (historique + courant)         │  │
│  │  - Envoie à Claude + 8 tools via SSE               │  │
│  │  - Boucle: si outil demandé → execute + renvoie    │  │
│  │  - Sauvegarde agent_state dans Supabase            │  │
│  │  - Stream tokens au frontend                        │  │
│  └──────────────────────────────────────────┘          │  │
│                                                           │
│  5. Sauvegarde messages dans conversations.messages      │
│  6. Retourne conversation_id + content                   │
└──────────┬──────────────────────────┬────────────────────┘
           │                          │
           ▼                          ▼
  ┌─────────────────┐        ┌─────────────────────┐
  │  CLAUDE API      │        │  SUPABASE            │
  │  claude-sonnet-4 │        │                      │
  │                  │        │  conversations       │
  │  Reçoit messages │        │    .id               │
  │  Appelle tools   │        │    .messages []      │
  │  Génère réponse  │        │    .agent_state {}   │
  └─────────────────┘        │    .message_count    │
                              │  feedbacks           │
                              └─────────────────────┘
```

---

## Coût par conversation

| Élément | Coût |
|---------|------|
| 1 échange (question + réponse) | ~0.01-0.02 EUR |
| 1 conversation complète (~20 échanges) | ~0.20-0.40 EUR |
| Budget mensuel (250-500 conversations) | ~50-100 EUR |
| Serveur Modal | Paiement à l'usage (~0.001 EUR/requête) |

---

## Fichiers techniques

### Backend

| Fichier | Rôle |
|---------|------|
| `execution/anthropic_agent.py` | Agent principal : boucle conversation Claude |
| `execution/anthropic_tools.py` | 8 outils appelables par Claude |
| `execution/chat_handler.py` | Endpoints /chat/*, persistance JSONB, UUID auto |
| `execution/gestionnaires/gestionnaire_promesses.py` | Génération documents |
| `execution/security/signed_urls.py` | URLs signées HMAC-SHA256 |
| `api/main.py` | App FastAPI, CORS, health check startup |
| `modal/modal_app.py` | Configuration serveur Modal |

### Frontend

| Fichier | Rôle |
|---------|------|
| `frontend/app/page.tsx` | Page principale, appels API, localStorage |
| `frontend/components/ChatArea.tsx` | Chat, feedback, suggestions |
| `frontend/components/Sidebar.tsx` | Historique conversations |
| `frontend/components/Header.tsx` | Progression collecte |

---

## Historique des versions

| Version | Date | Changements |
|---------|------|-------------|
| **v2.3** | 11 fév 2026 | **UUID auto-généré**, health check Supabase, fix persistance complète |
| v2.2 | 5 fév 2026 | SSE streaming, keepalive pings, suppression anonymisation |
| v2.1 | 5 fév 2026 | Frontend intégré, workspace `notomai`, persistance JSONB |
| v2.0 | 5 fév 2026 | Agent Anthropic avec 8 outils, boucle agentic |
| v1.0 | 4 fév 2026 | Chat par mots-clés, pas d'IA |

---

## Corrections majeures v2.3 (11 février 2026)

### Bug critique : Conversations jamais créées

**Problème** : Quand `conversation_id` n'était pas fourni dans la requête, aucune conversation n'était créée en BDD. Le code avait :
```python
conversation_id = request.conversation_id  # None si absent
if supabase and conversation_id:  # Jamais exécuté si None!
    # Création conversation...
```

**Solution** :
```python
conversation_id = request.conversation_id or str(uuid.uuid4())  # Auto-généré
if supabase:  # Toujours exécuté
    # Création conversation...
```

**Fichiers modifiés** :
- `execution/chat_handler.py` : endpoints `/chat/` et `/chat/stream`

### Améliorations

| Amélioration | Description |
|--------------|-------------|
| Logging erreurs | Remplacement de 6 `except: pass` par logging avec `exc_info=True` |
| Health check | Test connexion Supabase au démarrage de l'API |
| conversation_id dans stream | Ajouté dans le `done` event SSE |

---

## Travail restant

### Priorité haute

1. **Authentification utilisateur** - Intégration Supabase Auth (JWT)
2. **Extraction user_id/etude_id du JWT** - Remplacer UUIDs hardcodés
3. **Tests E2E** - Playwright/Cypress pour flow complet

### Priorité moyenne

4. **Redis rate limiting** - Persister limites entre redémarrages
5. **Circuit breaker Anthropic** - Retry avec backoff exponentiel
6. **Upload documents** - Permettre upload titre de propriété

---

*Document mis à jour le 11 février 2026 — Architecture chatbot v2.3*
