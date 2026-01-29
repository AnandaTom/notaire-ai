# Diagnostic Workflow Promesse de Vente

> Audit complet du 29/01/2026 - Version 1.5.0

## Verdict

Le moteur de generation fonctionne (template 94.3%, pipeline teste, DOCX conforme). Ce qui manque c'est la **plomberie entre les composants** : le frontend ne parle pas a l'API de generation, l'API ne sert pas les fichiers, et le collecteur a un bug de chemin.

```
Frontend Notaire       Collecte Q&R          Generation DOCX
+-----------------+    +-----------------+    +-----------------+
| Dashboard       | -X-| Questions       | -X-| Assemblage      |
| Questionnaires  |    | Agent NL        |    | Export DOCX     |
| Chiffrement E2E |    | Schemas 100+    |    | Workflow rapide  |
|                 |    |                 |    |                 |
| EXISTE          |    | BUG chemin      |    | FONCTIONNE      |
| PAS CONNECTE    |    | PAS CONNECTE    |    | TESTE E2E       |
+-----------------+    +-----------------+    +-----------------+
```

---

## Bloc 1 : Frontend Notaire

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Dashboard notaire | Fonctionne | `web/dashboard-notaire.html` |
| Questionnaire acquereur | Fonctionne | `web/fill.html` |
| Questionnaire vente appart | Fonctionne | `web/questionnaires/vente-appartement.html` |
| Questionnaire vente maison | Fonctionne | `web/questionnaires/vente-maison.html` |
| Questionnaire achat bien | Fonctionne | `web/questionnaires/achat-bien.html` |
| Chiffrement E2E client | Fonctionne | Supabase + AES-GCM |
| **Bouton "Generer promesse"** | **MANQUE** | A ajouter dans dashboard |
| **Telechargement DOCX** | **MANQUE** | Pas d'endpoint `/files/` |

Le dashboard collecte des donnees client chiffrees via Supabase mais n'a aucun bouton pour declencher la generation d'un acte.

---

## Bloc 2 : Collecte Questions-Reponses

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Schema questions promesse | 100+ questions, 21 sections | `schemas/questions_promesse_vente.json` |
| Schema variables promesse | Complet, multi-template | `schemas/variables_promesse_vente.json` |
| Catalogue unifie 4 types | Mapping complet | `schemas/promesse_catalogue_unifie.json` |
| **Script collecte interactive** | **BUG ligne 57** | `execution/utils/collecter_informations.py` |
| Agent NL (langage naturel) | Parse et genere | `execution/agent_autonome.py` |
| **Agent interactif Q&R** | **N'EXISTE PAS** | L'agent ne pose pas les questions une par une |

### Bug critique

`collecter_informations.py` ligne 57 pointe vers `questions_promesse.json` (n'existe pas) au lieu de `questions_promesse_vente.json`. Le script crashe immediatement pour les promesses.

### Agent autonome

L'agent fonctionne en mode "bulk" : il parse une phrase complete (`"Martin -> Dupont, appart 67m2, 450k"`), pas en mode interactif question par question. Il ne lit pas `questions_promesse_vente.json`.

---

## Bloc 3 : Generation DOCX

| Composant | Statut | Fichier |
|-----------|--------|---------|
| Assemblage Jinja2 | Fonctionne | `execution/core/assembler_acte.py` |
| Export DOCX formate | Fonctionne | `execution/core/exporter_docx.py` |
| Workflow rapide | **Teste et fonctionnel** | `execution/workflow_rapide.py` |
| Gestionnaire promesses 4 types | Existe | `execution/gestionnaires/gestionnaire_promesses.py` |
| API endpoint `/promesses/generer` | Code | `api/main.py` ligne 1134 |
| **Endpoint telechargement fichier** | **MANQUE** | Pas de `GET /files/{name}` |

### Test e2e reussi

```bash
python execution/workflow_rapide.py --type promesse_vente \
    --donnees exemples/donnees_promesse_exemple.json \
    --output .tmp/test_e2e_promesse.docx
# -> DOCX genere en ~5 secondes
```

Note : les chemins dans `workflow_rapide.py` (lignes 116, 146, 171) ont ete corriges pour la structure v1.5.0 (`execution/core/` au lieu de `execution/`).

---

## Les 5 coupures dans la chaine

| # | Coupure | Impact | Qui |
|---|---------|--------|-----|
| 1 | Dashboard sans bouton "Generer" | Le notaire ne peut pas lancer la generation depuis le web | Augustin |
| 2 | API sans endpoint `/files/` | Impossible de telecharger le DOCX genere | Paul |
| 3 | `collecter_informations.py` bug chemin | La collecte interactive CLI ne marche pas pour promesse | Tom (1 ligne) |
| 4 | Agent sans mode interactif Q&R | L'agent parse du texte brut au lieu de poser les questions une par une | Paul |
| 5 | Questionnaires web non relies a la generation | Les formulaires HTML envoient vers Supabase mais ne declenchent pas la generation | Augustin + Paul |

---

## Plan d'action par priorite

### P0 - Pour que ca fonctionne de bout en bout

1. **Endpoint `GET /files/{filename}`** dans `api/main.py`
   - `FileResponse` pour servir les DOCX generes
   - ~5 lignes de code

2. **Bouton "Generer Promesse"** dans `dashboard-notaire.html`
   - Appelle `POST /promesses/generer` avec les donnees decryptees
   - Puis download le DOCX via `/files/`

3. **Fix `collecter_informations.py` ligne 57**
   - `"questions_promesse.json"` -> `"questions_promesse_vente.json"`

### P1 - Pour une bonne experience notaire

4. **Mode interactif dans l'agent**
   - Pose les questions de `questions_promesse_vente.json` une par une
   - Au lieu de parser du texte brut

5. **Relier les questionnaires web a `/promesses/generer`**
   - `fill.html`, `vente-appartement.html` -> API generation
   - Au lieu de juste sauvegarder dans Supabase

6. **Validation metier avancee**
   - Conjoint doit signer si communaute
   - Diagnostics non expires
   - Coherence des dates

### P2 - Ameliorations

7. Template vente de 80.2% -> 85%+ (agent immobilier, plus-value)
8. Workflow automatique Promesse -> Vente (conservation donnees)
9. Template donation-partage

---

# TACHES PAUL - Specifications Detaillees

> Ce bloc contient tout ce que Paul doit faire, avec les fichiers exacts, numeros de ligne, et code de reference.

---

## Vue d'ensemble des responsabilites de Paul

```
Paul gere :  Chat ── Frontend ── Modal ── Backend

Semaine 1:  "Le tuyau fonctionne"
  P0-A  Deploy Modal staging + verifier /health
  P0-B  Endpoint GET /files/{filename} dans api/main.py
  P0-C  Cabler frontend → backend (API key + chat)

Semaine 2:  "Un notaire peut chatter et recuperer un acte"
  P1-A  Streaming SSE sur /agent/execute-stream
  P1-B  Persistance conversationnelle (Supabase)
  P1-C  Download DOCX depuis le chat

Semaine 3:  "Demo-ready"
  P2-A  Deploy frontend Vercel + CORS prod
  P2-B  Mode interactif Q&R dans l'agent
  P2-C  Polish UX (loading states, erreurs, notifications)
```

---

## P0-A : Deployer Modal en staging

### Contexte

Le fichier `modal/modal_app.py` est pret. Il importe `api/main.py` et expose le FastAPI via `@modal.asgi_app()`.

### Configuration actuelle (modal/modal_app.py)

| Parametre | Valeur | Ligne |
|-----------|--------|-------|
| Image | Debian slim + Python 3.11 | 32-40 |
| Deps | fastapi, uvicorn, python-docx, jinja2, pydantic, supabase, python-multipart | 34-39 |
| Secrets | `modal.Secret.from_name("supabase-credentials")` | 46 |
| Volume | `notaire-ai-outputs` monte sur `/outputs` | 52 |
| RAM | 1 GB | 58 |
| CPU | 1.0 | 58 |
| Timeout | 300s (5 min) | 58 |
| Concurrency | 10 inputs par instance | 58 |
| Idle timeout | 60s | 58 |
| Output dir env | `NOTAIRE_OUTPUT_DIR=/outputs` | 77 |

### Ce que tu dois faire

1. **Configurer les secrets Modal** :
   ```bash
   modal secret create supabase-credentials \
     SUPABASE_URL="https://xxx.supabase.co" \
     SUPABASE_KEY="eyJ..." \
     SUPABASE_SERVICE_KEY="eyJ..." \
     ENCRYPTION_MASTER_KEY="..." \
     ANTHROPIC_API_KEY="sk-ant-..."
   ```
   Les valeurs sont dans le fichier `.env` a la racine du projet.

2. **Deployer en staging** :
   ```bash
   modal serve modal/modal_app.py    # Test local d'abord
   modal deploy modal/modal_app.py   # Puis production
   ```

3. **Verifier que ca repond** :
   ```bash
   curl https://notaire-ai--fastapi-app.modal.run/health
   # Attendu : {"status": "ok", "version": "1.5.1", ...}
   ```

4. **Verifier les CORS** — Les origines autorisees sont dans `api/main.py` lignes 372-393 :
   ```python
   ALLOWED_ORIGINS = [
       "https://anandatom.github.io",
       "https://notaire-ai--fastapi-app.modal.run",
   ]
   # + localhost:3000 et 8000 si NOTOMAI_DEV_MODE=1
   ```
   Tu devras ajouter le domaine Vercel final ici quand on deploy le front.

### Critere de validation

`curl /health` retourne 200 avec un JSON valide depuis l'URL Modal.

---

## P0-B : Endpoint GET /files/{filename}

### Le probleme

L'API genere des DOCX dans le volume `/outputs` (Modal) ou `outputs/` (local). Mais aucun endpoint ne permet de les telecharger. La ligne 443 de `api/main.py` retourne un chemin relatif `/files/{name}` qui n'existe pas.

### Fichier a modifier

`api/main.py` — ajouter apres la ligne 799 (apres le endpoint `/health`)

### Code a ajouter

```python
from fastapi.responses import FileResponse
import os

@app.get("/files/{filename}")
async def download_file(filename: str, auth: dict = Depends(verify_api_key)):
    """Telecharge un fichier genere (DOCX/PDF)."""
    output_dir = os.getenv("NOTAIRE_OUTPUT_DIR", "outputs")
    file_path = os.path.join(output_dir, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"Fichier non trouve: {filename}")

    # Securite : empecher path traversal
    real_path = os.path.realpath(file_path)
    real_output = os.path.realpath(output_dir)
    if not real_path.startswith(real_output):
        raise HTTPException(status_code=403, detail="Acces refuse")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
```

### Import a ajouter

`FileResponse` de `fastapi.responses` — verifier si c'est deja importe (probablement pas).

### Critere de validation

```bash
# Generer un fichier de test
python execution/workflow_rapide.py --type promesse_vente \
    --donnees exemples/donnees_promesse_exemple.json \
    --output outputs/test_paul.docx

# Puis telecharger via l'API
curl -H "X-API-Key: nai_xxx" \
    https://notaire-ai--fastapi-app.modal.run/files/test_paul.docx \
    -o test_paul.docx
```

---

## P0-C : Cabler le frontend au backend

### Etat actuel du frontend

| Fichier | Lignes | Ce qu'il fait | Ce qui manque |
|---------|--------|---------------|---------------|
| `frontend/app/page.tsx` | 100 | Chat principal, appelle `POST /api/chat` | Pas de X-API-Key, pas de conversation_id, URL hardcodee |
| `frontend/components/ChatArea.tsx` | 271 | Affiche messages + input + quick actions | Pas de download link, pas de loading skeleton |
| `frontend/app/layout.tsx` | 21 | Layout racine Next.js | Metadata seulement |

### Problemes a corriger dans `frontend/app/page.tsx`

**1. L'appel API (lignes 44-54) n'envoie pas le header d'auth :**

```typescript
// ACTUEL (ligne 44-54) :
fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [...messages, userMessage],
    format: selectedFormat,
  })
})

// A REMPLACER PAR :
fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
  },
  body: JSON.stringify({
    message: input,           // Le backend attend "message", pas "messages"
    user_id: userId,
    etude_id: etudeId,
    conversation_id: conversationId,
    history: messages,
    context: {}
  })
})
```

**2. Pas de variable d'environnement pour l'URL backend :**

Creer `frontend/.env.local` :
```env
NEXT_PUBLIC_API_URL=https://notaire-ai--fastapi-app.modal.run
NEXT_PUBLIC_API_KEY=nai_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**3. Le greeting est hardcode (lignes 17-28) :**

Le message initial mentionne "Maitre Diaz" en dur. A rendre dynamique ou generique.

**4. Pas de conversation_id :**

Ajouter un state pour tracker la conversation :
```typescript
const [conversationId] = useState(() => crypto.randomUUID());
```

### Problemes dans `frontend/components/ChatArea.tsx`

**1. Quick Actions (lignes 57-61) :**
Les boutons "Acte de vente", "Promesse de vente", "Modifier un acte" appellent `onSendMessage(label)` — ca marche, mais le backend recoit juste le texte brut. C'est OK pour l'agent NL qui parse le texte.

**2. Format selector (lignes 206-241) :**
Boutons PDF/DOCX — l'info `selectedFormat` est envoyee au backend mais le backend ne l'utilise pas encore.

**3. Pas de lien de telechargement :**
Quand le backend retourne un fichier genere, le chat doit afficher un bouton "Telecharger". Le backend retourne `fichier_url` dans la reponse de `/agent/execute` (ligne 443 de api/main.py) mais c'est un chemin relatif non fonctionnel.

### Ce que tu dois faire

1. **Ajouter les env vars** dans `frontend/.env.local`
2. **Modifier `page.tsx`** : URL backend, header X-API-Key, conversation_id
3. **Modifier `ChatArea.tsx`** : afficher un bouton download quand `message.metadata?.fichier_url` est present
4. **Tester** : lancer `npm run dev` dans `frontend/`, envoyer "Promesse de vente", verifier que le backend repond

### Schema de la requete attendue par le backend

Le endpoint `POST /chat` (dans `execution/chat_handler.py` lignes 503-580) attend :

```json
{
  "message": "Je veux creer une promesse de vente",
  "user_id": "uuid-optionnel",
  "etude_id": "uuid-optionnel",
  "conversation_id": "uuid-optionnel",
  "history": [
    {"role": "assistant", "content": "Bonjour..."},
    {"role": "user", "content": "..."}
  ],
  "context": {}
}
```

Et retourne :

```json
{
  "content": "Texte de la reponse",
  "suggestions": ["Option 1", "Option 2", "Option 3"],
  "action": {"type": "navigate", "url": "/dossiers"},
  "intention": "CREER",
  "confiance": 0.85,
  "contexte_mis_a_jour": {"type_acte_en_cours": "promesse_vente"}
}
```

### Critere de validation

Le frontend affiche les reponses du backend et les suggestions cliquables.

---

## P1-A : Streaming SSE

### Le probleme

Le chat est bloquant : le frontend attend la reponse complete (5-10s pour une generation). Mauvaise UX.

### Solution

Ajouter un endpoint SSE (Server-Sent Events) dans `api/main.py`.

### Code a ajouter dans `api/main.py`

```python
from sse_starlette.sse import EventSourceResponse
import asyncio, json

@app.post("/agent/execute-stream")
async def execute_streaming(request: Request, auth: dict = Depends(verify_api_key)):
    """Execute une demande avec streaming SSE."""
    body = await request.json()

    async def event_generator():
        # Etape 1: Accusé de reception
        yield {"event": "status", "data": json.dumps({"etape": "reception", "message": "Demande recue..."})}

        # Etape 2: Analyse
        yield {"event": "status", "data": json.dumps({"etape": "analyse", "message": "Analyse de la demande..."})}

        # Appeler le pipeline existant
        try:
            from execution.agent_autonome import AgentAutonome
            agent = AgentAutonome()
            resultat = agent.executer(body.get("demande", ""))

            # Etape 3: Generation
            yield {"event": "status", "data": json.dumps({"etape": "generation", "message": "Generation en cours..."})}

            # Etape 4: Resultat
            yield {"event": "result", "data": json.dumps(resultat)}

        except Exception as e:
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator())
```

### Dependance a ajouter

Dans `requirements.txt` et dans l'image Modal (`modal_app.py` ligne 34) :
```
sse-starlette>=1.6.0
```

### Cote frontend

```typescript
const eventSource = new EventSource(`${API_URL}/agent/execute-stream`);
// Note: EventSource est GET-only. Pour POST, utiliser fetch + ReadableStream :

const response = await fetch(`${API_URL}/agent/execute-stream`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  },
  body: JSON.stringify({ demande: input }),
});

const reader = response.body?.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  // Parser les events SSE et mettre a jour le state
}
```

### Critere de validation

Le chat affiche "Analyse de la demande..." puis "Generation en cours..." progressivement, au lieu d'un spinner pendant 10s.

---

## P1-B : Persistance conversationnelle

### Le probleme

Le `ChatHandler` (`execution/chat_handler.py`) est **stateless**. Chaque message est traite independamment. Le notaire ne peut pas avoir un echange multi-tours pour remplir un dossier incrementalement.

### Etat actuel du ChatHandler

| Classe | Fichier | Ligne | Role |
|--------|---------|-------|------|
| `IntentionChat` | `execution/chat_handler.py` | 32-43 | 10 types d'intention (CREER, MODIFIER, RECHERCHER...) |
| `MessageChat` | | 46-52 | Message avec role, content, timestamp |
| `ContexteConversation` | | 55-62 | Contexte : dossier_actif, type_acte, etape_workflow, donnees_collectees |
| `ReponseChat` | | 65-73 | Reponse avec content, suggestions, action, contexte_mis_a_jour |
| `ChatHandler` | | 80-452 | Handler principal |

La structure `ContexteConversation` existe mais n'est **jamais persistee**. Elle est passee en parametre et perdue entre les requetes.

### Solution : table Supabase + contexte en BDD

**Migration SQL a ajouter** dans `supabase/migrations/` :

```sql
-- conversations et messages pour le chat
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etude_id UUID NOT NULL REFERENCES etudes(id),
    user_id TEXT,
    titre TEXT,
    type_acte TEXT,
    statut TEXT DEFAULT 'active' CHECK (statut IN ('active', 'terminee', 'abandonnee')),
    contexte JSONB DEFAULT '{}',
    donnees_collectees JSONB DEFAULT '{}',
    dossier_id UUID REFERENCES dossiers(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    intention TEXT,
    confiance FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "conversations_etude_isolation" ON conversations
    FOR ALL USING (etude_id = current_setting('app.etude_id')::UUID);

CREATE POLICY "messages_via_conversation" ON conversation_messages
    FOR ALL USING (
        conversation_id IN (
            SELECT id FROM conversations
            WHERE etude_id = current_setting('app.etude_id')::UUID
        )
    );

-- Index
CREATE INDEX idx_conversations_etude ON conversations(etude_id);
CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX idx_conversations_statut ON conversations(statut) WHERE statut = 'active';
```

### Endpoints a ajouter dans `api/main.py`

```python
@app.post("/conversations")
async def create_conversation(request: Request, auth: dict = Depends(require_write_permission)):
    """Cree une nouvelle conversation."""
    body = await request.json()
    # Insert dans Supabase conversations
    # Retourne conversation_id

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, auth: dict = Depends(verify_api_key)):
    """Recupere une conversation avec ses messages."""
    # Select conversations + conversation_messages
    # Retourne conversation + messages[]

@app.get("/conversations")
async def list_conversations(auth: dict = Depends(verify_api_key)):
    """Liste les conversations de l'etude."""
    # Select conversations WHERE etude_id = auth.etude_id

@app.delete("/conversations/{conversation_id}")
async def close_conversation(conversation_id: str, auth: dict = Depends(require_write_permission)):
    """Ferme une conversation (statut = terminee)."""
```

### Modifier le endpoint POST /chat

Dans `execution/chat_handler.py`, le router (lignes 503-580) doit :
1. Si `conversation_id` fourni → charger l'historique depuis Supabase
2. Passer l'historique comme `context` au `ChatHandler.traiter_message()`
3. Sauvegarder le message user + la reponse dans `conversation_messages`
4. Mettre a jour `conversations.contexte` et `conversations.donnees_collectees`

### Critere de validation

Le notaire peut fermer le navigateur, revenir, et reprendre sa conversation la ou il en etait.

---

## P1-C : Download DOCX depuis le chat

### Le probleme

Quand `/agent/execute` genere un acte, il retourne `fichier_url: "/files/{name}"` (ligne 443 de `api/main.py`). Mais :
- L'endpoint `/files/` n'existait pas (corrige en P0-B)
- Le frontend n'affiche pas de bouton download

### Ce que tu dois faire dans ChatArea.tsx

Quand un message du backend contient un `fichier_url` dans ses metadata, afficher un bouton de telechargement :

```tsx
// Dans le rendu des messages assistant
{message.metadata?.fichier_url && (
  <a
    href={`${API_URL}${message.metadata.fichier_url}`}
    download
    className="inline-flex items-center gap-2 mt-2 px-4 py-2 bg-gold-600 text-white rounded hover:bg-gold-700"
  >
    <DownloadIcon size={16} />
    Telecharger le document
  </a>
)}
```

### Schema de reponse de /agent/execute

Quand la generation reussit, la reponse (ligne 430-480 de `api/main.py`) contient :

```json
{
  "statut": "succes",
  "message": "Promesse generee avec succes",
  "dossier": {
    "numero": "PROM-20260129-001",
    "type_acte": "promesse_vente",
    "donnees": { ... }
  },
  "fichier": "promesse_vente_20260129_143022.docx",
  "fichier_url": "/files/promesse_vente_20260129_143022.docx"
}
```

### Critere de validation

Le notaire dit "Genere une promesse pour Martin → Dupont, 450k, appart 67m2" → le chat affiche la reponse + un bouton "Telecharger le document" qui lance le download du DOCX.

---

## P2-A : Deploy frontend sur Vercel

### Prerequis

- Le frontend est dans `frontend/` (Next.js 14.2, React 18, Tailwind, TypeScript)
- `npm run build` doit passer sans erreur

### Etapes

1. **Push le dossier frontend** sur un repo GitHub (ou sous-dossier du repo actuel)
2. **Connecter Vercel** au repo
3. **Configurer les env vars** dans le dashboard Vercel :
   ```
   NEXT_PUBLIC_API_URL=https://notaire-ai--fastapi-app.modal.run
   NEXT_PUBLIC_API_KEY=nai_xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. **Ajouter le domaine Vercel** dans les CORS de `api/main.py` ligne 372 :
   ```python
   ALLOWED_ORIGINS = [
       "https://anandatom.github.io",
       "https://notaire-ai--fastapi-app.modal.run",
       "https://notomai.vercel.app",  # <- AJOUTER
   ]
   ```
5. **Redeployer Modal** pour prendre en compte le nouveau CORS :
   ```bash
   modal deploy modal/modal_app.py
   ```

### Critere de validation

Le frontend est accessible sur `https://notomai.vercel.app` (ou equivalent) et communique avec le backend Modal.

---

## P2-B : Mode interactif Q&R dans l'agent

### Le probleme

L'agent (`execution/agent_autonome.py`) parse une phrase complete et essaie d'en extraire toutes les infos. Il ne sait pas poser des questions une par une au notaire.

Le schema `schemas/questions_promesse_vente.json` contient 100+ questions en 21 sections. L'agent ne les lit pas.

### Etat actuel du ChatHandler

La methode `_reponse_creer` (lignes 310-357 de `chat_handler.py`) detecte l'intention de creer un acte, mais :
- Elle demande juste le type d'acte
- Elle ne lance pas un workflow de collecte question par question
- Elle ne persiste pas les reponses partielles

### Solution proposee

Ajouter un **workflow de collecte** dans le `ChatHandler` qui :

1. Charge les questions depuis `schemas/questions_promesse_vente.json`
2. Pose les questions dans l'ordre des sections (21 sections, priorite obligatoire → optionnelle)
3. Stocke chaque reponse dans `donnees_collectees` du contexte conversation
4. A chaque tour, verifie ce qui manque et pose la question suivante
5. Quand toutes les questions obligatoires ont une reponse, propose de generer

### Schema des questions (questions_promesse_vente.json)

Chaque question suit cette structure :
```json
{
  "id": "vendeur_nom",
  "section": "vendeur",
  "question": "Quel est le nom du vendeur ?",
  "type": "text",
  "obligatoire": true,
  "variable_cible": "vendeurs[0].nom",
  "condition": null
}
```

### Flux d'interaction cible

```
Notaire: "Je veux creer une promesse de vente"
Agent:   "D'accord. Quel est le nom complet du vendeur ?"
         [suggestions: "Personne physique", "Societe"]
Notaire: "Martin Jean-Pierre"
Agent:   "Quel est le nom de l'acquereur ?"
Notaire: "Dupont Marie"
Agent:   "Quelle est l'adresse du bien ?"
...
Agent:   "J'ai toutes les informations. Voulez-vous generer la promesse ?"
         [suggestions: "Generer", "Modifier des informations", "Annuler"]
Notaire: "Generer"
Agent:   "Promesse generee. [Telecharger le document]"
```

### Critere de validation

Le notaire peut creer une promesse en repondant aux questions une par une dans le chat, sans avoir a fournir un JSON.

---

## P2-C : Polish UX

### Loading states

- Ajouter un skeleton loader dans ChatArea.tsx quand `isLoading=true`
- Afficher les etapes de generation (si streaming SSE active)
- Desactiver le bouton "Envoyer" pendant le chargement (deja fait)

### Gestion d'erreurs

Le backend retourne des erreurs generiques (500). Ameliorer :

Dans `api/main.py`, standardiser les erreurs :
```python
class APIError(BaseModel):
    code: str          # ex: "VALIDATION_ERROR", "FILE_NOT_FOUND"
    message: str       # Message lisible
    field: str = None  # Champ concerne (optionnel)
    suggestion: str = None  # Suggestion de correction
```

### Notifications

Quand un acte est genere en arriere-plan, notifier le frontend. Options :
- **Simple** : polling toutes les 5s sur `GET /dossiers/{id}` pour verifier le statut
- **Avance** : WebSocket ou SSE push (plus complexe mais meilleure UX)

---

## Reference technique rapide

### Authentification API

| Element | Valeur | Fichier |
|---------|--------|---------|
| Header | `X-API-Key` | `api/main.py` ligne 208 |
| Format cle | `nai_` + 28+ caracteres | ligne 248 |
| Cache | 5 min en memoire | lignes 211-213 |
| Table Supabase | `agent_api_keys` | ligne 260 |
| Permissions | `read`, `write`, `delete` par cle | ligne 270 |
| Dev mode | `NOTOMAI_DEV_MODE=1` → skip auth | lignes 317-324 |

### Endpoints existants (complet)

| Endpoint | Methode | Auth | Ligne dans api/main.py |
|----------|---------|------|------------------------|
| `/health` | GET | Aucune | 776 |
| `/me` | GET | verify_api_key | 850 |
| `/stats` | GET | verify_api_key | 802 |
| `/agent/execute` | POST | require_write | 407 |
| `/agent/feedback` | POST | verify_api_key | 495 |
| `/chat` | POST | (sub-router) | 396 |
| `/chat/feedback` | POST | (sub-router) | 563 |
| `/dossiers` | GET | verify_api_key | 546 |
| `/dossiers/{id}` | GET | verify_api_key | 600 |
| `/dossiers` | POST | require_write | 644 |
| `/dossiers/{id}` | PATCH | require_write | 697 |
| `/dossiers/{id}` | DELETE | require_delete | 743 |
| `/clauses/sections` | GET | verify_api_key | 865 |
| `/clauses/profils` | GET | verify_api_key | 923 |
| `/clauses/analyser` | POST | verify_api_key | 950 |
| `/clauses/feedback` | POST | require_write | 983 |
| `/clauses/suggestions` | GET | verify_api_key | 1046 |
| `/promesses/generer` | POST | require_write | 1134 |
| `/promesses/detecter-type` | POST | verify_api_key | 1183 |
| `/promesses/valider` | POST | verify_api_key | 1216 |
| `/promesses/profils` | GET | verify_api_key | 1248 |
| `/promesses/types` | GET | verify_api_key | 1276 |
| `/titres` | GET | verify_api_key | 1310 |
| `/titres/{id}` | GET | verify_api_key | 1341 |
| `/titres/recherche/adresse` | GET | verify_api_key | 1371 |
| `/titres/recherche/proprietaire` | GET | verify_api_key | 1398 |
| `/titres/{id}/vers-promesse` | POST | require_write | 1425 |

### CORS (api/main.py lignes 372-393)

```python
ALLOWED_ORIGINS = [
    "https://anandatom.github.io",
    "https://notaire-ai--fastapi-app.modal.run",
]
# + localhost si NOTOMAI_DEV_MODE=1
```

### Modal (modal/modal_app.py)

| Element | Detail |
|---------|--------|
| URL prod | `https://notaire-ai--fastapi-app.modal.run/` |
| Secret name | `supabase-credentials` |
| Volume | `notaire-ai-outputs` → `/outputs` |
| CRON daily | `daily_learning_job` a 2h (lignes 84-170) |
| CRON weekly | `weekly_catalog_sync` dimanche 3h (lignes 173-247) |
| Deploy | `modal deploy modal/modal_app.py` |
| Test local | `modal serve modal/modal_app.py` |

### Frontend (frontend/)

| Element | Detail |
|---------|--------|
| Framework | Next.js 14.2 + React 18 + TypeScript 5 |
| Styling | Tailwind CSS 3.4 |
| AI SDK | @anthropic-ai/sdk 0.32.0 |
| Chat component | `frontend/components/ChatArea.tsx` |
| Main page | `frontend/app/page.tsx` |
| API call | Ligne 44 de page.tsx → `POST /api/chat` |
| Build | `npm run build` |
| Dev | `npm run dev` |

### Tables Supabase utilisees par l'API

| Table | Usage | CRUD dans |
|-------|-------|-----------|
| `agent_api_keys` | Auth API keys | verify_api_key() |
| `etudes` | Info etude notaire | /me |
| `dossiers` | Dossiers clients | /dossiers/* |
| `audit_logs` | Traces d'execution | log_execution() |
| `form_submissions` | Soumissions formulaire | dashboard |
| `titres_propriete` | Titres extraits | /titres/* |
| `promesses_generees` | Promesses generees | /promesses/* |
| `feedbacks_promesse` | Retours notaires | /agent/feedback |

---

## Metriques actuelles

| Metrique | Valeur |
|----------|--------|
| Conformite promesse | **94.3%** (titres 97.2%, tableaux 86%, sections critiques 100%) |
| Conformite vente | 80.2% |
| Templates en production | 4/4 |
| Trames analysees (promesse) | 7 (Principale + A-F) |
| Sections promesse | 165 |
| Questions promesse | 100+ (21 sections) |
| Temps generation | ~5 secondes |
| Endpoints API | 30+ |
