# Architecture du Chatbot NotaireAI

> Document technique expliquant comment le chatbot fonctionne, de A à Z.

---

## Vue d'ensemble simplifiée

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    NOTAIRE                                                                  │
│    (navigateur web)                                                         │
│         │                                                                   │
│         │ 1. "Je veux créer une vente"                                      │
│         ▼                                                                   │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                     FRONTEND                                     │     │
│    │                     (dashboard/)                                 │     │
│    │                                                                  │     │
│    │   Page d'accueil = Chatbot                                      │     │
│    │   - Zone de conversation                                         │     │
│    │   - Boutons d'action rapide                                      │     │
│    │   - Onglets : Dossiers, Clients, Actes, Paramètres              │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│         │                                                                   │
│         │ 2. Envoie le message                                              │
│         ▼                                                                   │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                     MODAL                                        │     │
│    │                     (serverless)                                 │     │
│    │                                                                  │     │
│    │   Endpoint: /chat                                                │     │
│    │   - Reçoit le message                                            │     │
│    │   - Charge le contexte (dossiers récents, etc.)                 │     │
│    │   - Appelle Ollama (IA locale sur Modal)                        │     │
│    │   - Passe le relais à agent_autonome.py                         │     │
│    │   - Enregistre le feedback pour apprentissage                   │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│         │                                                                   │
│         │ 3. Lit/écrit les données                                          │
│         ▼                                                                   │
│    ┌─────────────────────────────────────────────────────────────────┐     │
│    │                     SUPABASE                                     │     │
│    │                     (base de données)                            │     │
│    │                                                                  │     │
│    │   Tables :                                                       │     │
│    │   - etudes (infos de l'étude notariale)                         │     │
│    │   - clients (données chiffrées AES-256)                         │     │
│    │   - dossiers (actes en cours)                                   │     │
│    │   - conversations (historique chat)        ◄── NOUVEAU          │     │
│    │   - feedbacks (apprentissage continu)      ◄── NOUVEAU          │     │
│    │   - audit_logs (traçabilité RGPD)                               │     │
│    └─────────────────────────────────────────────────────────────────┘     │
│         │                                                                   │
│         │ 4. Retourne la réponse                                            │
│         ▼                                                                   │
│    NOTAIRE voit la réponse + peut corriger/valider                         │
│         │                                                                   │
│         │ 5. Si correction → APPRENTISSAGE                                  │
│         ▼                                                                   │
│    L'agent devient plus intelligent                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Détail de chaque composant

### 1. FRONTEND (ce que voit le notaire)

**Emplacement :** `dashboard/`

**Pages :**
```
dashboard/
├── index.html          # Page actuelle (tableau de bord dev)
├── app/
│   ├── index.html      # NOUVELLE page d'accueil = Chatbot
│   ├── chat.js         # Logique du chat
│   ├── dossiers.html   # Liste des dossiers
│   ├── clients.html    # Liste des clients
│   └── styles.css      # Styles communs
```

**Le chatbot affiche :**
- Message de bienvenue personnalisé
- Zone de saisie pour taper
- Historique de la conversation
- Boutons d'action rapide ("Créer vente", "Mes dossiers", etc.)
- Boutons de feedback (pouce haut/bas) sur chaque réponse

---

### 2. MODAL (le cerveau dans le cloud)

**Emplacement :** `execution/modal_chat.py`

**Ce que fait Modal :**

```
┌─────────────────────────────────────────────────────────────────┐
│                         MODAL                                    │
│                                                                  │
│   1. RÉCEPTION                                                   │
│      └─► Reçoit : { message, user_id, etude_id, history }       │
│                                                                  │
│   2. CONTEXTE                                                    │
│      └─► Charge depuis Supabase :                               │
│          - 5 derniers dossiers du notaire                       │
│          - 10 derniers clients                                   │
│          - Préférences de l'utilisateur                         │
│                                                                  │
│   3. COMPRÉHENSION (Ollama)                                     │
│      └─► Ollama analyse le message :                            │
│          - Intention : CREER, MODIFIER, RECHERCHER, QUESTION    │
│          - Entités : vendeur, acquéreur, bien, prix             │
│          - Ton : formel (adapté au notaire)                     │
│                                                                  │
│   4. ACTION (agent_autonome.py)                                  │
│      └─► Exécute l'action détectée :                            │
│          - Créer un acte → lance le workflow                    │
│          - Chercher un client → requête Supabase                │
│          - Répondre une question → génère réponse               │
│                                                                  │
│   5. RÉPONSE                                                     │
│      └─► Retourne :                                              │
│          - response : "Voici ce que j'ai trouvé..."             │
│          - actions : [{ type: "navigate", url: "/dossiers" }]   │
│          - suggestions : ["Créer vente", "Voir client"]         │
│                                                                  │
│   6. APPRENTISSAGE                                               │
│      └─► Enregistre dans feedbacks :                            │
│          - Ce qui a été demandé                                  │
│          - Ce qui a été répondu                                  │
│          - Attente du feedback notaire                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Pourquoi Modal ?**
- Tu l'utilises déjà (pas de nouvelle techno)
- Paiement à l'usage (économique)
- GPU disponible pour Ollama
- Serverless (pas de serveur à gérer)

---

### 3. OLLAMA (l'IA qui comprend le français)

**Ce que c'est :** Un logiciel qui fait tourner des modèles d'IA localement.

**Modèle recommandé :** `llama3:8b` ou `mistral:7b`

**Ce qu'il fait dans notre système :**

```
ENTRÉE : "J'aimerais faire une vente pour le client Dupont,
          c'est un appartement à Lyon"

        │
        ▼

OLLAMA ANALYSE :
- Intention : CREER (veut créer quelque chose)
- Type d'acte : vente
- Client mentionné : "Dupont"
- Bien : appartement
- Localisation : Lyon

        │
        ▼

SORTIE : {
    "intention": "CREER",
    "type_acte": "vente",
    "entites": {
        "client_nom": "Dupont",
        "bien_type": "appartement",
        "bien_ville": "Lyon"
    },
    "confiance": 0.92,
    "reponse_naturelle": "Je vais créer un acte de vente pour
                          M. Dupont concernant un appartement à Lyon.
                          Pouvez-vous me confirmer l'adresse exacte ?"
}
```

**Sécurité :** Ollama tourne SUR Modal, dans ton environnement. Les données ne vont pas chez OpenAI ou Anthropic.

---

### 4. SUPABASE (la base de données)

**Tables existantes :**
- `etudes` - Les études notariales
- `clients` - Les clients (données chiffrées)
- `dossiers` - Les actes en cours
- `audit_logs` - Traçabilité RGPD

**Nouvelles tables :**

```sql
-- Historique des conversations
conversations (
    id              UUID        -- Identifiant unique
    etude_id        UUID        -- Quelle étude
    user_id         UUID        -- Quel utilisateur
    started_at      TIMESTAMP   -- Début de conversation
    last_message_at TIMESTAMP   -- Dernier message
    messages        JSONB       -- Liste des messages
    context         JSONB       -- Contexte (dossier actif, etc.)
)

-- Apprentissage continu
feedbacks (
    id                  UUID        -- Identifiant unique
    conversation_id     UUID        -- Quelle conversation
    etude_id            UUID        -- Quelle étude
    message_index       INT         -- Quel message dans la conversation

    -- Ce que l'agent a fait
    agent_intention     TEXT        -- "CREER", "RECHERCHER", etc.
    agent_response      TEXT        -- Ce qu'il a répondu
    agent_action        JSONB       -- Action exécutée

    -- Feedback du notaire
    rating              INT         -- 1 à 5, ou -1/+1
    correction          TEXT        -- "Il fallait dire X pas Y"
    correct_intention   TEXT        -- La bonne intention

    -- Apprentissage
    feedback_type       TEXT        -- "vocabulaire", "clause", "erreur"
    applied             BOOLEAN     -- Déjà intégré ?
    applied_at          TIMESTAMP   -- Quand
    applied_to          TEXT        -- "clauses_catalogue.json", etc.

    created_at          TIMESTAMP
)
```

---

### 5. BOUCLE D'APPRENTISSAGE (Self-Annealing)

**Le principe :** Chaque interaction améliore l'agent.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                        CYCLE D'AMÉLIORATION CONTINUE                        │
│                                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐               │
│   │ NOTAIRE │───►│  AGENT  │───►│ NOTAIRE │───►│ SYSTÈME │               │
│   │ demande │    │ répond  │    │ corrige │    │ apprend │               │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘               │
│        │                             │               │                     │
│        │                             │               ▼                     │
│        │                             │    ┌───────────────────────┐       │
│        │                             │    │ ENRICHISSEMENT        │       │
│        │                             │    │                       │       │
│        │                             │    │ • clauses_catalogue   │       │
│        │                             │    │ • questions_notaire   │       │
│        │                             │    │ • lecons_apprises     │       │
│        │                             │    │ • patterns Ollama     │       │
│        │                             │    └───────────────────────┘       │
│        │                             │               │                     │
│        │                             │               ▼                     │
│        │                             │    ┌───────────────────────┐       │
│        │                             └───►│ AGENT AMÉLIORÉ        │       │
│        │                                  │                       │       │
│        │                                  │ Comprend mieux        │       │
│        │                                  │ Répond mieux          │       │
│        │                                  │ Fait moins d'erreurs  │       │
│        │                                  └───────────────────────┘       │
│        │                                             │                     │
│        └─────────────────────────────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Types d'apprentissage :**

| Feedback du notaire | Ce qui est amélioré | Fichier impacté |
|---------------------|---------------------|-----------------|
| "On dit acquéreur, pas acheteur" | Vocabulaire | patterns Ollama |
| Ajoute une clause personnalisée | Catalogue de clauses | `clauses_catalogue.json` |
| "Cette question n'est pas claire" | Questions | `questions_notaire.json` |
| Corrige une erreur dans l'acte | Leçons apprises | `lecons_apprises.md` |
| "Bonne réponse !" (pouce haut) | Renforcement | Score de confiance |

---

## Flux de données détaillé

```
1. NOTAIRE TAPE UN MESSAGE
   "Créer une vente pour Dupont, appartement Lyon"

2. FRONTEND ENVOIE À MODAL
   POST /chat
   {
       "message": "Créer une vente pour Dupont...",
       "user_id": "uuid-du-notaire",
       "etude_id": "uuid-de-l-etude",
       "conversation_id": "uuid-conversation-en-cours"
   }

3. MODAL CHARGE LE CONTEXTE (depuis Supabase)
   - Derniers dossiers de l'étude
   - Clients récents
   - Historique de la conversation

4. MODAL APPELLE OLLAMA
   Prompt: "Tu es un assistant notarial.
            Le notaire dit: 'Créer une vente pour Dupont...'
            Contexte: [dossiers récents], [clients récents]
            Que dois-je faire ?"

5. OLLAMA RÉPOND
   {
       "intention": "CREER",
       "type_acte": "vente",
       "entites": { "client": "Dupont", "bien": "appartement Lyon" },
       "reponse": "Je prépare une vente pour M. Dupont..."
   }

6. MODAL EXÉCUTE L'ACTION
   - Cherche "Dupont" dans clients (via nom_hash, données chiffrées)
   - Trouve 2 résultats : Jean Dupont, Marie Dupont

7. MODAL RETOURNE AU FRONTEND
   {
       "response": "J'ai trouvé 2 clients Dupont :
                    • Jean Dupont (dossier 2024-045)
                    • Marie Dupont (nouveau client)
                    Lequel souhaitez-vous ?",
       "actions": [],
       "suggestions": ["Jean Dupont", "Marie Dupont", "Autre client"]
   }

8. FRONTEND AFFICHE LA RÉPONSE
   + Boutons de feedback (pouce haut / pouce bas)

9. NOTAIRE CLIQUE SUR "JEAN DUPONT"
   → Nouvelle itération du cycle

10. SI NOTAIRE CLIQUE SUR POUCE BAS
    → Formulaire de correction
    → Enregistré dans `feedbacks`
    → Sera analysé pour améliorer l'agent
```

---

## Sécurité

| Aspect | Protection | Comment |
|--------|------------|---------|
| Données clients | Chiffrées AES-256 | `encryption_service.py` |
| Accès base | RLS par étude | Policies Supabase |
| Transmission | HTTPS/TLS | Automatique |
| Authentification | JWT Supabase | `auth.users` |
| Traçabilité | Audit logs | Table `audit_logs` |
| Données vers Ollama | Restent sur Modal | Pas d'API externe |

**Important :** Les vraies données (noms, adresses) ne quittent JAMAIS Supabase/Modal.
Ollama reçoit uniquement des identifiants ou des données anonymisées si nécessaire.

---

## Coûts estimés

| Composant | Coût mensuel | Notes |
|-----------|--------------|-------|
| Supabase | 0€ | Tier gratuit suffisant au début |
| Modal | ~10-30€ | Selon usage (~0.001€/requête) |
| Domaine | ~10€/an | Optionnel |
| **TOTAL** | **~10-30€/mois** | Au démarrage |

---

## Prochaines étapes

1. ✅ Architecture documentée (ce fichier)
2. ⏳ Créer tables Supabase (`conversations`, `feedbacks`)
3. ⏳ Créer endpoint Modal (`/chat`)
4. ⏳ Créer interface frontend (chatbot)
5. ⏳ Connecter le tout
6. ⏳ Tester avec un vrai notaire

---

*Document créé le 27 janvier 2026*
*Version 1.0*
