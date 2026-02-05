# Comment fonctionne le chatbot NotaireAI

> Ce document explique le fonctionnement du chatbot en termes simples.
> Pas besoin de connaitre la programmation pour comprendre.

**Derniere mise a jour** : 5 fevrier 2026 (v2.2 — SSE streaming, keepalive, suppression anonymisation)

---

## En une phrase

Le notaire discute avec un assistant intelligent (Claude, par Anthropic) qui lui pose les bonnes questions, enregistre les reponses, et genere le document final (promesse de vente ou acte de vente) au format Word.

---

## Le parcours d'une conversation

```
 NOTAIRE                    NOTRE SERVEUR                   CLAUDE (IA)
    |                            |                              |
    |  "Je veux creer une        |                              |
    |   promesse pour un         |                              |
    |   appartement"             |                              |
    |--------------------------->|                              |
    |                            |                              |
    |                            |  1. Envoie le message        |
    |                            |     a Claude via SSE         |
    |                            |----------------------------->|
    |                            |                              |
    |                            |  2. Claude detecte que       |
    |                            |     c'est un appartement     |
    |                            |     (= copropriete)          |
    |                            |                              |
    |                            |  3. Claude demande les       |
    |                            |     questions de la section  |
    |                            |     "vendeur"                |
    |                            |<-----------------------------|
    |                            |                              |
    |                            |  4. Le serveur execute       |
    |                            |     la demande et renvoie    |
    |                            |     les questions            |
    |                            |----------------------------->|
    |                            |                              |
    |                            |  5. Claude formule les       |
    |                            |     questions en langage     |
    |                            |     naturel                  |
    |                            |<-----------------------------|
    |                            |                              |
    |  "Pouvez-vous me donner   |                              |
    |   le nom du vendeur et    |  6. Reponse streamee en      |
    |   son adresse ?"          |     temps reel (token par    |
    |<--- SSE stream ------------|     token)                   |
    |                            |                              |
    |  "M. Dupont, 12 rue..."   |                              |
    |--------------------------->|  ... le cycle continue ...   |
```

---

## Les 5 composants principaux

### 1. Le frontend (ce que voit le notaire)

C'est la page web ou le notaire tape ses messages. Elle est faite avec Next.js 14 (un framework web React). Le notaire voit :

- Une zone de conversation (comme un chat) avec rendu Markdown
- Des boutons de suggestion ("Creer une promesse", "Acte de vente", etc.)
- Une **barre de progression** indiquant l'avancement de la collecte (pourcentage)
- Des **boutons feedback** (pouce haut/bas) sur chaque reponse de l'assistant
- Un **historique des conversations** dans la barre laterale gauche
- Un bouton "Nouvelle conversation" pour demarrer un nouvel acte
- Un lien pour telecharger le document quand il est pret

Le frontend ne fait qu'afficher et transmettre. Toute l'intelligence est sur le serveur.

**Persistence** : le `userId` et la `conversationId` active sont stockes dans le localStorage du navigateur. Quand le notaire recharge la page, la conversation reprend automatiquement.

**Fichiers frontend** :

| Fichier | Role |
|---------|------|
| `frontend/app/page.tsx` | Page principale : etat, appels API, persistence localStorage |
| `frontend/components/ChatArea.tsx` | Zone de chat : bulles, feedback, suggestions, input |
| `frontend/components/Sidebar.tsx` | Barre laterale : historique conversations, navigation |
| `frontend/components/Header.tsx` | En-tete : titre, barre de progression |
| `frontend/app/globals.css` | Animations (fade-in, typing dots) |

### 2. Le serveur Modal (le cerveau)

Modal est un service cloud qui heberge notre serveur. Quand le notaire envoie un message :

1. Le serveur recoit le message
2. Il **charge l'historique** depuis Supabase (colonne `messages` JSONB dans `conversations`)
3. Il envoie le message a Claude (l'IA d'Anthropic) via **SSE streaming**
4. Claude reflechit et peut demander a executer des actions (voir section suivante)
5. La reponse est **streamee en temps reel** (mot par mot) vers le navigateur
6. Il **sauvegarde** les messages dans Supabase (JSONB)

**Pourquoi Modal ?** C'est un serveur "a la demande" : on ne paye que quand il est utilise. Pas de serveur qui tourne en permanence.

**Workspace Modal** : `notomai`
**URL de l'API** : `https://notomai--notaire-ai-fastapi-app.modal.run`

### 3. Claude et ses 8 outils

Claude (modele `claude-sonnet-4`) est l'intelligence artificielle qui comprend les demandes du notaire. Mais Claude ne fait pas tout seul : il dispose de **8 outils** qu'il peut appeler pour effectuer des actions concretes :

| Outil | Ce qu'il fait | Exemple |
|-------|---------------|---------|
| **Detecter le type de bien** | Identifie si c'est un appartement, une maison ou un terrain | "Un appartement" → copropriete |
| **Recuperer les questions** | Va chercher les questions a poser pour chaque section | Section "vendeur" → 8 questions |
| **Enregistrer les reponses** | Sauvegarde ce que le notaire a repondu | Nom: Dupont, Adresse: 12 rue... |
| **Voir la progression** | Calcule le pourcentage de completion | 45% termine, 12 champs manquants |
| **Valider les donnees** | Verifie la coherence (prix > 0, dates logiques, etc.) | Erreur: quotites ne font pas 100% |
| **Generer le document** | Cree le fichier Word (DOCX) final | promesse_20260205.docx |
| **Chercher des clauses** | Trouve des clauses juridiques dans le catalogue | "condition suspensive pret" |
| **Enregistrer un feedback** | Sauvegarde une remarque du notaire pour ameliorer le systeme | "Ajouter une clause sur..." |

**Comment ca marche concretement :**

Claude ne genere pas le document lui-meme. Il **pilote** les outils existants. Quand il decide qu'il a besoin de savoir quelles questions poser, il appelle l'outil "Recuperer les questions". Quand le notaire a repondu a assez de questions, Claude appelle "Valider les donnees" puis "Generer le document".

C'est comme un chef de projet qui delegue les taches a des specialistes.

### 4. Supabase (la memoire)

Supabase est notre base de donnees. Elle stocke :

- **Les conversations** : tout l'historique des echanges (colonne `messages` JSONB)
- **L'etat de l'agent** : ou en est la collecte, quelles donnees ont deja ete recueillies (colonne `agent_state` JSONB)
- **Le contexte** : type d'acte en cours, progression, categorie de bien (colonne `context` JSONB)
- **Les clients** : donnees chiffrees (personne ne peut les lire sans la cle)
- **Les feedbacks** : retours des notaires (pouce haut/bas) pour ameliorer le systeme

Quand le notaire revient le lendemain, la conversation reprend exactement la ou il s'etait arrete, grace a l'etat sauvegarde dans Supabase.

### 5. Les endpoints API

| Endpoint | Methode | Role |
|----------|---------|------|
| `/health` | GET | Verification que le serveur fonctionne |
| `/chat/` | POST | Envoyer un message et recevoir une reponse (non-streaming) |
| `/chat/stream` | POST | **Envoyer un message et recevoir la reponse en SSE streaming** |
| `/chat/conversations` | GET | Lister les 20 dernieres conversations |
| `/chat/conversations/{id}` | GET | Charger une conversation complete |
| `/chat/feedback` | POST | Enregistrer un feedback (pouce haut/bas) |

---

## Securite : comment sont protegees les donnees

| Protection | Explication |
|------------|-------------|
| **Chiffrement des clients** | Les donnees clients sont chiffrees en base de donnees (AES-256). Meme si quelqu'un accede a la base, il ne peut pas lire les noms. |
| **UUIDs hardcodes** | Le frontend n'a pas d'authentification. Le backend utilise des UUIDs fixes pour satisfaire les contraintes de la base (FK vers `auth.users` et `etudes`). |
| **CORS restreint** | Seuls les domaines autorises peuvent appeler l'API (`notomai--...modal.run`, `localhost:3000`, `localhost:3001`, `anandatom.github.io`). |
| **Limite de requetes** | Maximum 60 requetes par minute pour eviter les abus. |
| **Acces restreint** | Chaque etude ne voit que ses propres donnees (isolation par RLS Supabase). |
| **Suppression securisee** | Les fichiers temporaires sont ecrases avant suppression (impossible a recuperer). |
| **Anti-boucle** | L'agent est limite a 8 actions par message pour eviter un emballement. |
| **Fallback** | Si Claude est indisponible, l'ancien systeme par mots-cles prend le relais automatiquement. |

> **Note sur l'anonymisation (v2.2)** : L'anonymisation chat (remplacement des noms par `[VENDEUR_1]`, etc.) a ete **desactivee** le 5 fevrier 2026. Elle causait un bug ou Claude melangeait les tokens anonymes et les vraies donnees dans ses reponses (ex: `Monsieur [VENDEUR_1] MARTIN Pierre Jean`). La cause : les resultats des outils (tool_results) contenaient les vraies donnees en clair, tandis que le system prompt demandait a Claude d'utiliser les placeholders. Claude recevait donc les deux formats et les melangeait. Le module `ChatAnonymizer` reste disponible dans `execution/security/chat_anonymizer.py` pour une future reimplementation qui anonymiserait aussi les tool_results.

---

## Cout par conversation

| Element | Cout |
|---------|------|
| 1 echange (question + reponse) | ~0.01-0.02 EUR |
| 1 conversation complete (~20 echanges) | ~0.20-0.40 EUR |
| Budget mensuel (250-500 conversations) | ~50-100 EUR |
| Serveur Modal | Paiement a l'usage (~0.001 EUR/requete) |

---

## Fichiers techniques (pour les developpeurs)

### Backend

| Fichier | Role |
|---------|------|
| `execution/anthropic_agent.py` | L'agent principal : boucle de conversation avec Claude |
| `execution/anthropic_tools.py` | Les 8 outils que Claude peut appeler |
| `execution/chat_handler.py` | Point d'entree du chat (endpoints /chat/*) + persistance JSONB + fallback |
| `execution/security/chat_anonymizer.py` | Anonymisation/de-anonymisation des donnees |
| `execution/agent_autonome.py` | CollecteurInteractif (questions/reponses schema-driven) |
| `execution/gestionnaires/gestionnaire_promesses.py` | Generation des documents (detection, assemblage, export) |
| `execution/core/valider_acte.py` | Validation des donnees (14+ regles de coherence) |
| `schemas/clauses_catalogue.json` | Catalogue de 45+ clauses juridiques |
| `api/main.py` | App FastAPI principale (CORS, routeur, lifespan) |
| `modal/modal_app.py` | Configuration du serveur Modal (workspace `notomai`) |

### Frontend

| Fichier | Role |
|---------|------|
| `frontend/app/page.tsx` | Page principale : etat global, appels API, persistence localStorage |
| `frontend/components/ChatArea.tsx` | Zone de chat : bulles de messages, feedback, suggestions, saisie |
| `frontend/components/Sidebar.tsx` | Barre laterale : historique conversations, bouton nouvelle conversation |
| `frontend/components/Header.tsx` | En-tete : titre de session, barre de progression collecte |
| `frontend/app/globals.css` | Styles globaux : animations, scrollbar, polices |
| `frontend/package.json` | Dependencies : next, react, react-markdown, lucide-react, tailwindcss |

---

## Schema technique complet

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
│  ┌──────────────────────────────────────┐   │
│  │  Header (barre de progression)       │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  localStorage: userId, activeConversation   │
└────────┬────────────────────────────────────┘
         │
         │  POST /chat/        (message, conversation_id)
         │  GET  /chat/conversations
         │  GET  /chat/conversations/{id}
         │  POST /chat/feedback (rating)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  SERVEUR MODAL  (notomai workspace)                      │
│  https://notomai--notaire-ai-fastapi-app.modal.run       │
│                                                           │
│  api/main.py → chat_handler.py                           │
│                                                           │
│  1. Charge historique + context depuis Supabase           │
│  2. Delegue a AnthropicAgent                              │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ANTHROPIC AGENT  (anthropic_agent.py)             │  │
│  │                                                     │  │
│  │  a. Prepare les messages (historique + courant)    │  │
│  │  b. Envoie a Claude + 8 tools via SSE streaming    │  │
│  │  c. Boucle: si Claude veut un outil →              │  │
│  │     - execute dans thread pool (asyncio.to_thread) │  │
│  │     - renvoie le resultat                          │  │
│  │     - SSE pings (15s) maintiennent la connexion    │  │
│  │  d. Quand Claude repond → stream tokens au frontend│  │
│  │  e. Retourne progress_pct + categorie_bien         │  │
│  └──────────────────────────────────┬───────────┘      │  │
│                                     │                   │  │
│         ┌───────────────────────────┼──────────┐       │  │
│         │  8 TOOLS (anthropic_tools.py)        │       │  │
│         │                                       │       │  │
│         │  detect_property_type ──► gestionnaire│       │  │
│         │  get_questions ─────────► collecteur  │       │  │
│         │  submit_answers ────────► collecteur  │       │  │
│         │  get_collection_progress► collecteur  │       │  │
│         │  validate_deed_data ───► validateur   │       │  │
│         │  generate_document ────► gestionnaire │       │  │
│         │  search_clauses ───────► catalogue    │       │  │
│         │  submit_feedback ──────► api_feedback │       │  │
│         └───────────────────────────────────────┘       │  │
│                                                           │
│  3. Sauvegarde messages dans conversations.messages JSONB │
│  4. Si AnthropicAgent echoue → fallback ChatHandler      │
│     (ancien systeme par mots-cles, sans IA)              │
│                                                           │
└──────────┬──────────────────────────┬────────────────────┘
           │                          │
           │                          │  Lecture/ecriture
           │                          ▼
           │                 ┌─────────────────────┐
           │                 │  SUPABASE            │
           │                 │  (base de donnees)   │
           │                 │                      │
           │                 │  conversations       │
           │                 │    .messages (JSONB)  │
           │                 │    .context (JSONB)   │
           │                 │    .agent_state       │
           │                 │    .message_count     │
           │                 │  feedbacks (ratings)  │
           │                 │  clients (chiffre)    │
           │                 │  audit_logs           │
           │                 └─────────────────────┘
           │
           │  Appels API (SSE streaming)
           ▼
  ┌─────────────────────┐
  │  CLAUDE (Anthropic)  │
  │  claude-sonnet-4     │
  │                      │
  │  Recoit les messages │
  │  en clair            │
  └─────────────────────┘
```

---

## Historique des versions

| Version | Date | Changements |
|---------|------|-------------|
| v2.2 | 5 fev 2026 | **SSE streaming temps reel**, keepalive pings (15s), suppression anonymisation (bug tokens), `asyncio.to_thread` pour outils longs |
| v2.1 | 5 fev 2026 | Frontend integre (progress bar, feedback, historique conversations), workspace `notomai`, persistance JSONB, 3 nouveaux endpoints |
| v2.0 | 5 fev 2026 | Agent Anthropic avec 8 outils, anonymisation, boucle agentic, fallback keyword |
| v1.0 | 4 fev 2026 | Chat par mots-cles, pas d'IA |

---

## Travail realise le 5 fevrier 2026 (session v2.2)

### Problemes resolus

1. **SSE streaming non fonctionnel en navigateur**
   - Le parsing SSE dans `page.tsx` avait 3 bugs : normalisation `\r\n`, scope des variables, gestion fin de stream
   - Corrige : parser SSE robuste qui gere tous les cas edge

2. **Connexion SSE coupee pendant operations longues** (`TypeError: network error`)
   - Cause : `executor.execute()` bloquait l'event loop Python 10-30s pendant la generation de documents
   - Aucun byte envoye pendant ce temps → navigateur ferme la connexion apres ~30s d'inactivite
   - Fix 1 : `asyncio.to_thread()` autour de `executor.execute()` libere l'event loop
   - Fix 2 : `ping=15` sur `EventSourceResponse` envoie des pings SSE automatiques toutes les 15s

3. **Erreur CORS sur port 3001**
   - Next.js auto-incremente le port si 3000 est occupe
   - Fix : Ajoute `localhost:3001` et `127.0.0.1:3001` dans `ALLOWED_ORIGINS`

4. **Tokens d'anonymisation visibles dans le chat** (`[VENDEUR_1]`, `[DATE_3]`, etc.)
   - Cause racine : le system prompt disait a Claude d'utiliser les tokens, mais les tool_results envoyaient les vraies donnees en clair. Claude melangeait les deux formats.
   - Fix : **Suppression complete de l'anonymisation** dans le pipeline chat
     - Retire la section "Donnees anonymisees" du system prompt
     - Simplifie `_prepare_messages()` pour ne plus anonymiser
     - Retire tous les appels `deanonymiser()`
     - Le module `ChatAnonymizer` reste disponible pour reimplementation future

### Fichiers modifies

| Fichier | Modifications |
|---------|--------------|
| `execution/anthropic_agent.py` | `asyncio.to_thread()` pour outils, suppression anonymisation |
| `execution/chat_handler.py` | `ping=15` + headers sur `EventSourceResponse` |
| `api/main.py` | Ajout `localhost:3001` dans CORS |
| `frontend/app/page.tsx` | Parser SSE corrige (3 bugs) |

---

## Travail restant a faire

### Priorite haute

1. **Authentification utilisateur**
   - Actuellement : UUIDs hardcodes, pas de login
   - A faire : Integration Supabase Auth (email/password ou OAuth)
   - Impact : Chaque notaire/etude aura son propre espace isole

2. **Tests E2E du chat**
   - Ecrire des tests Playwright/Cypress pour le flow complet
   - Tester : envoi message, reception SSE, generation document, telechargement

3. **Gestion des erreurs cote frontend**
   - Afficher un message si le backend est down
   - Retry automatique en cas d'erreur reseau temporaire

### Priorite moyenne

4. **Reimplementation de l'anonymisation (optionnel)**
   - Si necessaire pour RGPD : anonymiser AUSSI les tool_results
   - Alternative : utiliser l'option Anthropic pour ne pas stocker les prompts

5. **Historique de conversation persistant**
   - Actuellement : les messages sont en JSONB dans Supabase
   - A faire : pagination pour tres longues conversations

6. **Upload de documents**
   - Permettre au notaire d'uploader un titre de propriete (PDF/DOCX)
   - Extraction automatique des informations

---

## Idees d'amelioration future

### Experience utilisateur

- **Mode brouillon** : Sauvegarder automatiquement le brouillon toutes les 30s
- **Raccourcis clavier** : Ctrl+Enter pour envoyer, Echap pour annuler
- **Historique de commandes** : Fleche haut pour rappeler le dernier message
- **Suggestions contextuelles** : Proposer des reponses basees sur les donnees deja collectees
- **Preview du document** : Afficher un apercu du DOCX avant telechargement

### Performance

- **Prompt caching Anthropic** : Deja implemente sur system prompt et tools
- **Cache Redis** : Cacher les questions/clauses frequemment utilisees
- **Pre-generation** : Commencer la generation du document des que les donnees sont completes a 80%
- **Compression SSE** : Utiliser gzip pour reduire la bande passante

### Intelligence

- **Apprentissage des corrections** : Si un notaire corrige une clause, proposer la correction aux autres
- **Detection d'intentions ambigues** : Demander confirmation si confiance < 70%
- **Multi-langue** : Supporter d'autres langues pour les notaires frontaliers
- **Voice-to-text** : Dicter les reponses au lieu de taper

### Securite

- **Audit trail complet** : Logger toutes les actions avec timestamp et user_id
- **2FA** : Authentification a deux facteurs pour les notaires
- **IP whitelisting** : Restreindre l'acces aux IPs de l'etude
- **Expiration de session** : Deconnecter apres 30min d'inactivite

---

*Document mis a jour le 5 fevrier 2026 — Architecture agent intelligent v2.2*
