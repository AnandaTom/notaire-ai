# Brief Paul - Agent Modal Intelligent

**De:** Tom | **Date:** 31/01/2026 | **Objet:** Rendre l'agent Modal aussi intelligent que Claude Code local

---

## Audit de l'agent actuel

J'ai fait un audit complet du code Modal. Voici ce qui ressort :

**`chat_handler.py` (732 lignes)** — C'est un chatbot a reponses figees. Zero appel LLM. Toute la logique est du keyword matching (`if "promesse" in msg -> retourne template texte`). Il ne raisonne pas, il pattern-match.

**`frontend/app/api/chat/route.ts`** — Fait un appel Anthropic, mais avec seulement 37 lignes de system prompt et zero tool use. Claude repond "dans le vide" sans acces aux fonctions du backend.

**Resultat : 95% de l'intelligence est deconnectee.** Tout existe cote Python (detection 3 categories de biens, Q&R 97 questions, validation, assemblage Jinja2, export DOCX, 6 templates, 9 endpoints API) mais rien n'est branche sur l'agent.

| Capacite | Claude Code (local) | Agent Modal (prod) |
|----------|--------------------|--------------------|
| Appel LLM | Oui | Non (chat_handler) / minimal (route.ts) |
| System prompt | 800+ lignes (CLAUDE.md) | 37 lignes |
| Tool use | 40+ outils | 0 |
| Schemas/templates charges | 10 schemas, 6 templates | 0 |
| Detection categorie bien | 3 categories, 2 niveaux | Non |
| Validation donnees | 12+ regles | Non |
| Enrichissement cadastre | API Gouv (BAN + IGN) | Non |
| Auto-correction | Oui | Non |

---

## Solution : Anthropic API + Tool Use

Remplacer `chat_handler.py` par un vrai appel Anthropic Messages API avec 9 tools qui wrappent les fonctions Python **deja codees**.

### Architecture

```
Frontend --> POST /chat --> Modal (FastAPI) --> Anthropic Messages API
                                                  |           |
                                             system prompt   9 tools
                                             = CLAUDE.md     = fonctions Python
                                             + directives    existantes
```

### System prompt

Charger `CLAUDE.md` + `directives/workflow_notaire.md` + `directives/creer_promesse_vente.md` au boot. ~15K tokens, ~$0.05/conversation.

### Les 9 tools (wrappent des fonctions existantes)

| Tool | Wrappe | Fichier source |
|------|--------|----------------|
| `detecter_categorie` | `GestionnairePromesses.detecter_categorie_bien()` | gestionnaire_promesses.py |
| `get_questions` | `CollecteurInteractif.get_questions_for_section()` | agent_autonome.py |
| `submit_answers` | `CollecteurInteractif.submit_answers()` | agent_autonome.py |
| `get_progress` | `CollecteurInteractif.get_progress()` | agent_autonome.py |
| `valider_donnees` | Validation complete | valider_acte.py |
| `generer_document` | `GestionnairePromesses.generer()` | gestionnaire_promesses.py |
| `chercher_clause` | Catalogue 45+ clauses | clauses_catalogue.json |
| `chercher_cadastre` | `CadastreService.enrichir_cadastre()` | cadastre_service.py |
| `soumettre_feedback` | Insert Supabase | feedbacks_promesse |

### Tool `chercher_cadastre` (nouveau — v1.8.0)

Le 9e tool wrappe `CadastreService` (`execution/services/cadastre_service.py`). Il permet a l'agent de :

1. **Geocoder une adresse** → code INSEE + coordonnees GPS (API Adresse BAN)
2. **Chercher une parcelle** → section + numero → surface, geometrie (API Carto IGN)
3. **Enrichir automatiquement** les donnees cadastrales d'un dossier

**Chaine de resolution cadastre :**
```
Titre de propriete (OCR) → Supabase (cache) → API Gouv → Q&R notaire (fallback)
```

**Endpoints API cadastre (deja codes) :**

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/cadastre/geocoder` | POST | Adresse → code_insee + coordonnees |
| `/cadastre/parcelle` | GET | code_insee + section + numero → parcelle |
| `/cadastre/sections` | GET | code_insee → liste des sections |
| `/cadastre/enrichir` | POST | Donnees dossier → donnees enrichies |
| `/cadastre/surface` | GET | Conversion surface texte ↔ m² |

Le tool `chercher_cadastre` appelle `/cadastre/enrichir` en interne. L'enrichissement est aussi appele automatiquement dans `GestionnairePromesses.generer()` avant l'assemblage.

### Endpoint /chat

Refaire le endpoint `/chat` avec la boucle agent standard Anthropic : envoyer le message + tools, si Claude repond `tool_use` on execute le tool et on renvoie le resultat, sinon on retourne la reponse texte. Voir la [doc Anthropic tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) — c'est le pattern exact.

---

## Review paragraphe par paragraphe

L'assembleur produit du Markdown structure par headings (`## TITRE`, `### SOUS-TITRE`). Le frontend doit :

1. **Splitter** le Markdown genere en blocs (par heading)
2. **Afficher** chaque bloc avec boutons Approuver / Corriger / Commenter
3. **POST** les feedbacks vers `/feedback/paragraphe` -> stocke dans Supabase `feedbacks_promesse`

La notaire peut ainsi valider section par section et faire ses retours directement dans l'interface.

---

## Self-anneal + Push GitHub

```
Notaire corrige un paragraphe
  --> Feedback stocke dans Supabase (feedbacks_promesse)
  --> CRON quotidien (Modal) detecte les patterns (3+ memes corrections)
  --> GitHub API : branche + commit du fix + PR automatique
  --> Tom/Paul review + merge
  --> CI/CD redeploy --> l'agent est corrige
```

Le `daily_learning_job` existe deja dans `modal_app.py`, il suffit de l'etendre. Secrets requis : `GITHUB_TOKEN`, `ANTHROPIC_API_KEY`.

---

## Plan d'execution

| Phase | Quoi | Effort |
|-------|------|--------|
| **P1** | Agent intelligent (system prompt + 8 tools + /chat) | ~10h |
| **P2** | Review paragraphe (split MD + UI annotation + feedback API) | ~8h |
| **P3** | Self-anneal (CRON analyse + GitHub API + PR auto) | ~7h |

**Cout estime : ~$60-130/mois** (Anthropic ~$50-100, Modal ~$10-30, Supabase free)

---

## Questions pour Paul

1. Frontend = Next.js ? (vu `frontend/app/`)
2. `modal deploy modal/modal_app.py` fonctionne ?
3. Secrets Modal (SUPABASE_URL, SUPABASE_KEY) deja configures ?
4. Nom exact du repo GitHub ? Qui a les droits de merge ?
5. On commence par quel acte pour le MVP notaire ?
