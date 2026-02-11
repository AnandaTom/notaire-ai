# Audit General Notomai - 10 Fevrier 2026

> Document de reference pour Augustin (front-end) / Tom (templates) / Payos (Modal + infra)
> Objectif: identifier les gaps pour qu'un agent front-end puisse discuter avec des notaires et generer des actes ultra fiables.

---

## 1. ETAT ACTUEL DU SYSTEME

### 1.1 Architecture Globale

```
FRONT-END (Next.js)          BACKEND (Modal/FastAPI)          DATABASE (Supabase)
  ┌──────────────┐            ┌─────────────────┐             ┌──────────────┐
  │ ChatArea.tsx  │──POST────▶│ /agent/execute   │────────────▶│ 16 tables    │
  │ Sidebar.tsx   │           │ /dossiers        │             │ RLS actif    │
  │ ParagraphRev. │◀──JSON────│ /validation/*    │◀────────────│ Multi-tenant │
  └──────────────┘            │ /cadastre/*      │             └──────────────┘
                              │ /api/feedback    │                    │
                              │ /api/questions   │             ┌──────────────┐
                              └────────┬─────────┘             │ Edge Func.   │
                                       │                       │ - send-quest.│
                              ┌────────▼─────────┐             │ - send-link  │
                              │ PIPELINE PYTHON   │             └──────────────┘
                              │ - ParseurNL       │
                              │ - Gestionnaires   │
                              │ - Jinja2 Assembly │
                              │ - DOCX Export     │
                              └──────────────────┘
```

### 1.2 Templates (Tom)

| Template | Conformite | Statut | Bookmarks |
|----------|-----------|--------|-----------|
| Vente lots copropriete | 80.2% | PROD | 361 |
| Promesse copropriete | 88.9% | PROD | 298 |
| Promesse hors copropriete | NEW | PROD | - |
| Promesse terrain a batir | NEW | PROD | - |
| **Promesse viager** | NEW | PROD | - |
| Reglement copropriete EDD | 85.5% | PROD | 116 |
| Modificatif EDD | 91.7% | PROD | 60 |

**7 templates en production, 3 categories de biens + viager, 6 sous-types conditionnels.**

### 1.3 Pipeline de Generation

```
Donnees JSON ──▶ Validation ──▶ Detection type ──▶ Jinja2 Assembly ──▶ DOCX Export
    ~0ms            ~50ms          ~20ms              ~1.5s              ~3.5s
                                                                    TOTAL: ~5.7s
```

**Points forts:**
- Detection 3 niveaux: categorie + type + sous-type (confiance 70-95%)
- Validation en temps reel champ par champ (`/validation/champ`)
- Support multi-parties ("Martin & Pierre → Dupont & Thomas")
- Enrichissement cadastre automatique via APIs gouv.fr
- Feedback continu avec apprentissage (2 AM daily job)

### 1.4 Base de Donnees Supabase (16 tables)

| Table | Rows | Role |
|-------|------|------|
| `etudes` | 1 | Etude notariale (tenant) |
| `notaire_users` | 1 | Profils notaires |
| `etude_users` | 1 | Roles (notaire/clerc/admin/agent_ia) |
| `clients` | 6 | Chiffrement E2E (nom_encrypted, etc.) |
| `dossiers` | 9 | Dossiers avec donnees_questionnaire JSONB |
| `conversations` | 9 | Historique chatbot + agent_state |
| `feedbacks` | 1 | Retours notaires (self-annealing) |
| `form_submissions` | 0 | Formulaires clients (tokens 7j, chiffrement) |
| `documents_client` | 0 | Upload documents (CNI, contrat mariage...) |
| `templates` | 7 | Catalogue templates avec conformite_score |
| `actes_generes` | 5 | Historique actes + temps_generation_ms |
| `evenements_dossier` | 8 | Timeline dossier |
| `rappels` | 5 | Alertes + echeances |
| `audit_logs` | 54 | Securite + tracabilite |
| `rgpd_requests` | 0 | Droit d'acces/suppression |
| `agent_api_keys` | 2 | Cles API par etude |

**Edge Functions (2):**
- `send-questionnaire-notification` (v3) - Notifie le notaire quand un client soumet
- `send-questionnaire-link` (v1) - Envoie le lien questionnaire au client

### 1.5 API Endpoints Existants

#### Modal (Production)
| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/agent/execute` | POST | Requete NL → agent → generation |
| `/dossiers` | GET/POST | CRUD dossiers |
| `/dossiers/{id}` | GET | Detail dossier |
| `/clauses/sections` | GET | Catalogue clauses |
| `/health` | GET | Health check |

#### Validation
| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/validation/donnees` | POST | Validation complete |
| `/validation/champ` | POST | Validation temps reel champ |
| `/validation/schema/{type}` | GET | Schema JSON par type d'acte |

#### Feedback
| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/feedback` | POST | Soumettre feedback |
| `/api/feedbacks` | GET | Lister avec filtres |
| `/api/feedback/{id}/traiter` | POST | Approuver/rejeter |
| `/api/suggestions` | GET | Suggestions IA |
| `/api/stats` | GET | Stats apprentissage |

#### Cadastre
| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/cadastre/geocoder` | POST | Adresse → code INSEE |
| `/cadastre/parcelle` | GET | Parcelle → donnees cadastrales |
| `/cadastre/sections` | GET | Sections d'une commune |
| `/cadastre/enrichir` | POST | Enrichissement auto |

#### Questions / Workflow
| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/questions/promesse` | GET | Questions filtrees par categorie |
| `/questions/promesse/answer` | POST | Soumettre reponses |
| `/questions/promesse/progress/{id}` | GET | Progression collecte |
| `/questions/promesse/prefill` | POST | Pre-remplissage depuis titre |
| `/workflow/promesse/start` | POST | Demarrer workflow complet |
| `/workflow/promesse/{id}/submit` | POST | Soumettre reponses + suite |
| `/workflow/promesse/{id}/generate` | POST | Declencher generation DOCX |
| `/workflow/promesse/{id}/generate-stream` | GET | Generation SSE (progression) |
| `/workflow/promesse/{id}/status` | GET | Etat du workflow |

### 1.6 Front-End Actuel (Next.js)

```
frontend/
├── app/
│   ├── page.tsx                  # Page d'accueil
│   ├── layout.tsx                # Layout racine (Tailwind)
│   └── api/chat/route.ts        # Bridge vers backend
├── components/
│   ├── ChatArea.tsx              # Interface chat principale
│   ├── Header.tsx                # Navigation
│   ├── Sidebar.tsx               # Liste dossiers
│   └── ParagraphReview.tsx       # Editeur de paragraphes
├── lib/                          # Utilitaires
└── package.json                  # Next.js 13+, React 18, Tailwind 3
```

**Etat:** Structure de base existante, mais **pas de workflow Q&R complet**, pas de gestion de session multi-etapes, pas de formulaires dynamiques.

---

## 2. PROBLEMES IDENTIFIES

### 2.1 Securite (CRITIQUE)

| Probleme | Severite | Impact |
|----------|----------|--------|
| 8 vues `SECURITY DEFINER` (bypass RLS) | ERREUR | Les vues dashboard exposent les donnees sans filtrage tenant |
| 6 fonctions `search_path mutable` | WARN | Potentiel detournement de fonctions |
| `leaked_password_protection` desactive | WARN | Mots de passe compromis non detectes |
| 2 Edge Functions avec `verify_jwt: false` | ERREUR | Endpoints invocables sans authentification |
| 18 FK non indexees | PERF | Requetes lentes sur les jointures |
| ~20 RLS policies avec `auth.uid()` sans `(select ...)` | PERF | Re-evaluation par ligne au lieu d'une fois |

**Vues a corriger en priorite:**
- `conversation_stats`, `v_evolution_mensuelle`, `v_kpis_par_type_acte`
- `v_kpis_etude`, `v_submissions_documents_status`, `v_rappels_dashboard`
- `v_dossiers_dashboard`, `feedbacks_pending`

### 2.2 Gaps Front-End pour un Agent Fiable

| Gap | Description | Priorite |
|-----|-------------|----------|
| **Pas de workflow Q&R visuel** | Le `CollecteurInteractif` existe en CLI, mais pas de composant React qui affiche les questions section par section avec conditions | P0 |
| **Pas de session multi-etapes** | Le front-end n'a pas de machine a etats pour guider: Type → Parties → Bien → Prix → Conditions → Generation | P0 |
| **Pas de validation temps reel UX** | L'API `/validation/champ` existe mais n'est pas branchee cote front | P1 |
| **Pas de pre-remplissage visuel** | Le prefill depuis titre existe en backend (64% auto) mais pas d'UI pour afficher "champs deja remplis" | P1 |
| **Pas de streaming generation** | L'endpoint SSE `/generate-stream` existe mais pas de composant pour afficher la progression | P1 |
| **Pas de review paragraphe** | `ParagraphReview.tsx` existe mais pas connecte au pipeline | P2 |
| **Pas de gestion feedback inline** | Le notaire ne peut pas cliquer sur un paragraphe pour dire "modifier ceci" | P2 |
| **Pas de gestion documents** | Upload de documents clients (CNI, etc.) + validation | P2 |

### 2.3 Gaps Backend pour la Fiabilite

| Gap | Description | Priorite |
|-----|-------------|----------|
| **Pas d'endpoint chat conversationnel** | L'agent parse du NL one-shot, pas de vrai chat multi-tour avec memoire | P0 |
| **Pas de sauvegarde partielle** | Si le notaire ferme le navigateur au milieu de la collecte, tout est perdu | P1 |
| **Pas de calcul emoluments** | La table `dossiers` a les colonnes mais pas de logique de calcul | P2 |
| **Conversion Promesse→Vente pas exposee** | Le script existe mais pas d'endpoint API | P2 |
| **Detection type pas assez explicite** | La confiance est renvoyee mais pas d'explication UI-friendly | P2 |

---

## 3. PISTES D'AMELIORATION POUR LE FRONT-END

### 3.1 PRIORITE 0 : Workflow Conversationnel Multi-Etapes

**Objectif:** Un notaire ouvre l'app, dit "je veux faire une promesse", et l'agent le guide etape par etape.

**Architecture recommandee:**

```
┌─────────────────────────────────────────────────────────┐
│                    WORKFLOW ENGINE                        │
│                                                          │
│  State Machine (zustand/xstate):                         │
│                                                          │
│  IDLE → TYPE_DETECTION → PARTIES → BIEN → PRIX          │
│    → CONDITIONS → REVIEW → GENERATION → DONE             │
│                                                          │
│  Chaque etape:                                           │
│  1. Charge les questions depuis /questions/promesse      │
│  2. Filtre par section + conditions (backend)            │
│  3. Affiche formulaire dynamique                         │
│  4. Valide en temps reel (/validation/champ)             │
│  5. Sauvegarde partielle (donnees_questionnaire JSONB)   │
│  6. Passe a l'etape suivante                             │
│                                                          │
│  Sidebar: progression (8/21 sections completes)          │
│  Header: "Promesse de vente - Copropriete - 73% complet" │
└─────────────────────────────────────────────────────────┘
```

**Endpoints a utiliser:**
1. `POST /workflow/promesse/start` → cree le workflow + dossier
2. `GET /questions/promesse?section=X&categorie=Y` → questions filtrees
3. `POST /questions/promesse/answer` → soumet les reponses
4. `POST /validation/champ` → validation temps reel
5. `GET /workflow/promesse/{id}/status` → progression
6. `POST /workflow/promesse/{id}/generate` → lance la generation
7. `GET /workflow/promesse/{id}/generate-stream` → SSE progression

**Donnees de session dans Supabase:**
```sql
-- Deja existant dans dossiers.donnees_questionnaire (JSONB)
-- + conversations.agent_state (JSONB) pour l'etat du workflow
```

### 3.2 PRIORITE 0 : Chat Intelligent avec Memoire

**Objectif:** Le notaire peut aussi juste "discuter" avec l'agent au lieu de remplir des formulaires.

**Architecture:**

```
┌─────────────────────────────────────────────────┐
│                 CHAT MODE                        │
│                                                  │
│  Notaire: "Fais une promesse pour Martin qui     │
│           vend son appart rue de la Paix a       │
│           Dupont pour 450k"                      │
│                                                  │
│  Agent:  "J'ai detecte une promesse de vente     │
│          (copropriete) avec:                     │
│          ✓ Vendeur: Martin                       │
│          ✓ Acquereur: Dupont                     │
│          ✓ Bien: appartement, rue de la Paix     │
│          ✓ Prix: 450 000 EUR                     │
│                                                  │
│          Il me manque:                           │
│          ? Prenom et date de naissance vendeur    │
│          ? Details du lot (numero, tantiemes)     │
│          ? Situation matrimoniale des parties     │
│                                                  │
│          Voulez-vous completer maintenant ou      │
│          passer au formulaire guide?"            │
│                                                  │
│  [Completer ici]  [Formulaire guide]  [Brouillon]│
└─────────────────────────────────────────────────┘
```

**Composants React necessaires:**
- `ChatMode.tsx` - Interface chat avec NL parsing
- `FormMode.tsx` - Formulaire guide section par section
- `HybridMode.tsx` - Switch fluide entre les deux
- `ConfidenceIndicator.tsx` - Affiche le score + champs manquants
- `EntityCard.tsx` - Carte vendeur/acquereur/bien editable

**Backend a adapter:**
- Transformer `/agent/execute` en endpoint multi-tour (conversation_id)
- Stocker le contexte dans `conversations.agent_state`
- Renvoyer les `champs_manquants` avec mapping UI

### 3.3 PRIORITE 1 : Formulaires Dynamiques

**Le schema `questions_promesse_vente.json` contient deja 97 questions en 21 sections** avec:
- Type de question (texte, choix, date, nombre)
- Conditions d'affichage (`condition: "pret_applicable == true"`)
- Chemins variables (`variable_path: "promettant[].nom"`)
- Placeholder et aide contextuelle

**Composant recommande:**

```tsx
// DynamicQuestion.tsx
interface Question {
  id: string;
  texte: string;
  type: "texte" | "choix" | "date" | "nombre" | "oui_non";
  options?: string[];
  condition?: string;
  variable_path: string;
  obligatoire: boolean;
  aide?: string;
  placeholder?: string;
}

// Logique:
// 1. Fetch questions par section depuis API
// 2. Evaluer conditions (reference aux reponses precedentes)
// 3. Afficher le bon composant selon le type
// 4. Valider en temps reel via /validation/champ
// 5. Sauvegarder dans donnees_questionnaire
```

### 3.4 PRIORITE 1 : Generation avec Progression

```tsx
// GenerationProgress.tsx
// Utilise EventSource (SSE) depuis /workflow/promesse/{id}/generate-stream
//
// Etapes affichees:
// [✓] Detection du type: Promesse copropriete (95% confiance)
// [✓] Validation des donnees: 47/52 champs remplis
// [✓] Enrichissement cadastre: Parcelle AH-0068 trouvee
// [►] Assemblage Jinja2: partie_developpee_promesse.md...
// [ ] Export DOCX
// [ ] Verification conformite
//
// Temps estime: ~6 secondes
```

### 3.5 PRIORITE 2 : Review et Feedback Inline

```
┌─────────────────────────────────────────────────┐
│  ACTE DE VENTE - Review Mode                     │
│                                                  │
│  [Section: DESIGNATION DU BIEN]                  │
│  ┌─────────────────────────────────────────────┐ │
│  │ Un appartement situe au deuxieme etage      │ │
│  │ d'un immeuble sis 12 rue de la Paix,        │ │
│  │ 75002 PARIS, cadastre section AH n°68       │ │
│  │                                    [✎] [👎] │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  [Section: PRIX ET PAIEMENT]                     │
│  ┌─────────────────────────────────────────────┐ │
│  │ Le present bien est vendu moyennant le      │ │
│  │ prix de QUATRE CENT CINQUANTE MILLE EUROS   │ │
│  │ (450 000,00 EUR)                  [✎] [👎]  │ │
│  └─────────────────────────────────────────────┘ │
│                                                  │
│  [Telecharger DOCX]  [Modifier]  [Valider]       │
└─────────────────────────────────────────────────┘
```

**Le composant `ParagraphReview.tsx` existe deja** - il faut le connecter a:
- `/api/feedback` pour les corrections
- `/agent/execute` avec intention=MODIFIER pour regenerer

---

## 4. CONTRAT D'INTERFACE FRONT ↔ BACK

### 4.1 Demarrer un nouveau dossier

```typescript
// POST /workflow/promesse/start
// Body:
{
  "etude_id": "uuid",
  "type_acte": "promesse_vente", // ou "vente"
  "source": "chat" | "formulaire" | "titre_upload",
  "donnees_initiales"?: { // optionnel, si chat NL
    "texte": "Martin vend son appart a Dupont pour 450k"
  }
}

// Response:
{
  "workflow_id": "uuid",
  "dossier_id": "uuid",
  "detection": {
    "categorie_bien": "copropriete",
    "type_promesse": "standard",
    "sous_type": null,
    "confiance": 0.85,
    "raison": "Syndic et lots detectes"
  },
  "premiere_section": "identification",
  "questions": [...],           // Questions de la 1ere section
  "donnees_pre_remplies": {...}, // Si titre ou NL parsing
  "progression": {
    "sections_total": 21,
    "sections_completes": 0,
    "champs_remplis": 0,
    "champs_total": 97
  }
}
```

### 4.2 Soumettre des reponses

```typescript
// POST /workflow/promesse/{workflow_id}/submit
// Body:
{
  "section": "identification",
  "reponses": {
    "acte.date": "2026-02-10",
    "acte.type_promesse": "unilatérale",
    "acte.duree_validite": 90
  }
}

// Response:
{
  "validation": {
    "valide": true,
    "erreurs": [],
    "avertissements": ["Duree de validite de 90 jours inhabituelle (standard: 60j)"]
  },
  "prochaine_section": "vendeur",
  "questions": [...],
  "progression": {
    "sections_completes": 1,
    "pourcentage": 12
  }
}
```

### 4.3 Validation temps reel

```typescript
// POST /validation/champ
// Body:
{
  "type_acte": "promesse_vente",
  "chemin": "promettants.0.situation_matrimoniale",
  "valeur": "marié",
  "contexte": { /* donnees deja saisies */ }
}

// Response:
{
  "valide": true,
  "messages": [
    {
      "niveau": "info",
      "code": "CONJOINT_REQUIS",
      "message": "Le conjoint devra intervenir a l'acte",
      "suggestion": "Renseigner l'identite du conjoint",
      "champ_ui": "Vendeur 1 - Situation matrimoniale"
    }
  ]
}
```

### 4.4 Lancer la generation

```typescript
// POST /workflow/promesse/{workflow_id}/generate
// Response: { "generation_id": "uuid" }

// GET /workflow/promesse/{workflow_id}/generate-stream (SSE)
// Events:
data: {"etape": "detection", "statut": "complete", "detail": "Copropriete, 95%"}
data: {"etape": "validation", "statut": "complete", "detail": "47/52 champs"}
data: {"etape": "cadastre", "statut": "en_cours", "detail": "Enrichissement..."}
data: {"etape": "cadastre", "statut": "complete", "detail": "Parcelle AH-0068"}
data: {"etape": "assemblage", "statut": "en_cours", "detail": "Jinja2 rendering"}
data: {"etape": "assemblage", "statut": "complete", "detail": "12 sections"}
data: {"etape": "export", "statut": "en_cours", "detail": "DOCX generation"}
data: {"etape": "export", "statut": "complete", "fichier": "/outputs/promesse_2026.docx"}
data: {"etape": "verification", "statut": "complete", "conformite": 88.9}
data: {"etape": "done", "fichier_docx": "url", "fichier_md": "url", "duree_ms": 5700}
```

---

## 5. PLAN D'ACTION RECOMMANDE

### Phase 1 : Fondations (1-2 semaines)

**Augustin (Front):**
- [ ] State machine workflow (zustand ou xstate): IDLE → TYPE → PARTIES → BIEN → PRIX → CONDITIONS → REVIEW → GENERATE → DONE
- [ ] Composant `DynamicQuestion.tsx` qui rend les questions du schema
- [ ] Composant `WorkflowProgress.tsx` (sidebar avec sections)
- [ ] Integration `/workflow/promesse/start` + `/submit`

**Tom (Templates):**
- [ ] Verifier que les 97 questions couvrent tous les bookmarks des templates
- [ ] Ajouter des `placeholder` et `aide` manquants dans `questions_promesse_vente.json`
- [ ] Tester chaque template avec des donnees minimales via le pipeline

**Payos (Backend/Modal):**
- [ ] Exposer `/workflow/promesse/*` endpoints dans Modal
- [ ] Implementer la sauvegarde partielle (`donnees_questionnaire` JSONB)
- [ ] Fixer les 8 vues SECURITY DEFINER
- [ ] Activer `verify_jwt` sur les Edge Functions

### Phase 2 : Chat + Validation (2-3 semaines)

**Augustin:**
- [ ] `ChatMode.tsx` avec parsing NL + affichage entites detectees
- [ ] `HybridMode.tsx` switch chat ↔ formulaire
- [ ] Branchement `/validation/champ` sur chaque input
- [ ] `GenerationProgress.tsx` avec SSE

**Tom:**
- [ ] Mapping questions → bookmarks pour calculer la completude reelle
- [ ] Tests E2E: donnes minimales → DOCX valide pour chaque template
- [ ] Enrichir `clauses_catalogue.json` avec les conditions d'activation

**Payos:**
- [ ] Transformer `/agent/execute` en multi-tour (conversation_id + memoire)
- [ ] Implementer le SSE pour `/generate-stream`
- [ ] Fixer les RLS `auth.uid()` → `(select auth.uid())`
- [ ] Indexer les 18 FK manquantes

### Phase 3 : Review + Feedback (2-3 semaines)

**Augustin:**
- [ ] `DocumentReview.tsx` - Affichage section par section
- [ ] Feedback inline (clic sur paragraphe → correction)
- [ ] Upload documents clients (CNI, etc.)
- [ ] Dashboard notaire (dossiers, rappels, stats)

**Tom:**
- [ ] Conversion Promesse → Vente exposee dans le workflow
- [ ] Templates pour les 13 trames anonymisees (plan d'integration existant)

**Payos:**
- [ ] Endpoint conversion promesse → vente
- [ ] Calcul automatique emoluments (bareme notarial)
- [ ] CI/CD: tests automatiques sur PR

---

## 6. SCHEMAS SUPABASE - REFERENCE POUR LE FRONT

### Tables principales que le front utilise directement:

```typescript
// dossiers - Le dossier du notaire
interface Dossier {
  id: string;
  etude_id: string;
  numero: string;
  type_acte: "vente" | "promesse_vente" | "donation" | ...;
  statut: "brouillon" | "en_cours" | "termine" | "archive";
  parties: Party[];          // JSONB
  biens: Bien[];             // JSONB
  donnees_metier: object;    // JSONB - donnees completes
  donnees_questionnaire: object; // JSONB - reponses du formulaire
  prix_vente?: number;
  prix_total?: number;       // Generated: prix_vente + mobilier
  emoluments_ttc?: number;
  date_signature_prevue?: string;
  priorite: "basse" | "normale" | "haute" | "urgente";
  complexite: "simple" | "standard" | "complexe" | "tres_complexe";
  temps_total_minutes: number;
}

// conversations - L'historique chat
interface Conversation {
  id: string;
  etude_id: string;
  user_id: string;
  messages: Message[];       // JSONB
  context: object;           // JSONB
  agent_state: object;       // JSONB - etat du workflow
  message_count: number;
  feedback_count: number;
}

// form_submissions - Formulaires envoyes aux clients
interface FormSubmission {
  id: string;
  token: string;             // URL publique (64 chars hex)
  type_partie: "vendeur" | "acquereur" | ...;
  type_questionnaire: "vente_appartement" | "vente_maison" | ...;
  status: "pending" | "submitted" | "processed" | "expired";
  data_encrypted: string;    // AES-256-GCM
  expires_at: string;        // +7 jours
  client_nom?: string;
  client_email?: string;
}

// actes_generes - Les documents generes
interface ActeGenere {
  id: string;
  dossier_id: string;
  template_id: string;
  type_acte: string;
  fichier_docx?: string;
  fichier_pdf?: string;
  variables_remplies: number;
  variables_totales: number;
  taux_completion: number;   // Generated: (remplies/totales)*100
  status: "brouillon" | "genere" | "valide" | "signe" | "archive";
  temps_generation_ms?: number;
}
```

### Auth pattern (toutes les requetes):

```typescript
// Header obligatoire:
Authorization: Bearer <supabase_jwt>
// ou
X-API-Key: nai_xxxxxxxx   // Pour les agents IA

// Le RLS filtre automatiquement par etude_id
// Pas besoin de passer etude_id dans chaque requete
```

---

## 7. VARIABLES D'ENVIRONNEMENT

```env
# Front-end (.env.local)
NEXT_PUBLIC_API_URL=https://notaire-ai--fastapi-app.modal.run
NEXT_PUBLIC_SUPABASE_URL=https://wcklvjckzktijtgakdrk.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_APP_NAME=NotaireAI

# Backend (Modal secrets)
SUPABASE_URL=...
SUPABASE_KEY=... (service key)
ANTHROPIC_API_KEY=...
GITHUB_TOKEN=...
```

---

## 8. ALERTES A CORRIGER EN PRIORITE

### Securite (a faire AVANT mise en production client)

1. **Vues SECURITY DEFINER** → Remplacer par des vues INVOKER ou ajouter des filtres `WHERE etude_id = ...`
   - `conversation_stats`, `v_evolution_mensuelle`, `v_kpis_par_type_acte`
   - `v_kpis_etude`, `v_submissions_documents_status`, `v_rappels_dashboard`
   - `v_dossiers_dashboard`, `feedbacks_pending`

2. **Edge Functions sans JWT** → Activer `verify_jwt: true` sur:
   - `send-questionnaire-notification`
   - `send-questionnaire-link`

3. **Leaked password protection** → Activer dans Supabase Auth settings

4. **RLS initplan** → Remplacer `auth.uid()` par `(select auth.uid())` dans ~20 policies

### Performance

5. **18 FK non indexees** → Creer les index (une migration)
6. **40+ index inutilises** → Nettoyer apres mise en production (pas urgent)
7. **Multiple permissive policies** sur `feedbacks` → Fusionner en une seule

---

## 9. RESUME POUR AUGUSTIN

**Ce qui existe et fonctionne:**
- 6 templates PROD avec detection automatique 3 niveaux
- Pipeline complet: donnees → validation → assemblage → DOCX en ~6s
- API complete avec validation temps reel, cadastre, feedback
- Supabase avec 16 tables, RLS, multi-tenant
- Front Next.js avec structure de base (ChatArea, Sidebar, ParagraphReview)

**Ce qu'il te reste a construire:**
1. **Workflow multi-etapes** (state machine) - la colonne vertebrale du front
2. **Formulaires dynamiques** renderises depuis les schemas JSON (97 questions)
3. **Mode chat** qui parse le NL et affiche les entites detectees
4. **Switch fluide** entre chat et formulaire
5. **Validation temps reel** branchee sur `/validation/champ`
6. **Progression generation** via SSE
7. **Review document** section par section avec feedback inline

**Les endpoints existent deja** - il faut les consommer cote React. Le plus gros travail est la UX du workflow multi-etapes.

**Tech stack recommande:**
- zustand ou xstate pour le state machine workflow
- React Hook Form pour les formulaires dynamiques
- TanStack Query pour le cache API
- EventSource natif pour le SSE
- Supabase JS Client pour auth + realtime

---

*Document genere le 10/02/2026 par audit automatise Claude Code*
