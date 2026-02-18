# AUDIT COMPLET NOTOMAI - 18 Fevrier 2026

> Analyse exhaustive du projet par Claude Opus 4.6 : architecture, frontend, backend, securite RGPD, Supabase, templates, infrastructure, bonnes pratiques.

---

## 1. ETAT DES LIEUX

### Score global : 7/10

Le projet est impressionnant en ambition et en profondeur (7 templates, 71 sections Jinja2, 17 tables Supabase, pipeline CLI complet, 257 tests). Mais il y a un decalage important entre le backend Python (mature, fonctionnel) et le frontend Next.js (prometteur mais casse sur des points critiques).

### Inventaire complet

| Categorie | Quantite |
|-----------|----------|
| Scripts Python | 87 |
| Templates Jinja2 | 9 principaux + 60 sections |
| Schemas JSON | 17 |
| Directives (SOPs) | 27 |
| Tests | 257 (8 fichiers) |
| Composants React | 30+ |
| Clauses modulaires | 60+ |
| Pages frontend | 7 |
| Migrations Supabase | 7 custom + 26 auto |
| GitHub Actions | 3 workflows |
| Documentation | 57+ fichiers |
| Skills Claude | 8 |
| Agents Claude | 5 |

### Ce qui marche bien

| Composant | Maturite | Notes |
|-----------|----------|-------|
| Pipeline Python (assemblage -> DOCX) | 9/10 | Solide, enrichissement auto, 11 filtres Jinja2, cache env |
| Templates Jinja2 | 8/10 | 7 templates PROD, 71 sections, 6356 conditionals |
| Detection 3 niveaux | 8/10 | Categorie + type + sous-type, marqueurs ponderes viager |
| Schemas JSON | 8/10 | v4.1.0, support viager, lotissement, servitudes |
| CLI `notaire.py` | 8/10 | Point d'entree unifie, 10 commandes |
| Supabase schema | 7/10 | 17 tables, RLS active, multi-tenant, chiffrement PII |
| Modal deployment | 7/10 | CRON jobs, self-anneal, persistent volume |
| Backend API (FastAPI) | 6/10 | Chat SSE fonctionne, mais endpoints workflow manquent |
| Frontend Next.js | 4/10 | Design soigne, 23 composants, MAIS api.ts manquant |
| Securite RGPD | 5/10 | Bases posees mais lacunes critiques |

---

## 2. PROBLEMES CRITIQUES (Bloquants)

### CRITIQUE #1 : `frontend/lib/api.ts` N'EXISTE PAS

2 composants l'importent :
- `frontend/stores/workflowStore.ts:12` : `import * as api from '@/lib/api'`
- `frontend/components/workflow/FeedbackPanel.tsx:5` : `import * as api from '@/lib/api'`

**Impact** : Le workflow complet (TYPE_SELECT -> COLLECTING -> REVIEW -> GENERATING -> DONE) est 100% non-fonctionnel. Le store appelle `api.startWorkflow()`, `api.submitAnswers()`, `api.validateField()`, `api.streamGeneration()` -- toutes des fonctions qui n'existent pas.

**Paradoxe** : La page chat (`app/app/page.tsx`) fait des fetch directement vers Modal et fonctionne. Seul le workflow guide est casse.

### CRITIQUE #2 : Mismatch Endpoints Backend <-> Frontend

Le frontend attend ces endpoints :

| Endpoint attendu | Existe dans api/main.py ? | Existe dans chat_handler.py ? |
|-----------------|-------|-------|
| POST /chat/stream | via router | OUI (SSE EventSourceResponse) |
| GET /chat/conversations | via router | OUI |
| GET /chat/conversations/{id} | via router | OUI |
| POST /chat/feedback | via router | OUI |
| POST /workflow/start | NON | NON |
| POST /workflow/{id}/submit | NON | NON |
| GET /workflow/{id}/generate-stream | NON | NON |

**Verdict** : Le chat fonctionne. Le workflow guide n'a aucun backend.

### CRITIQUE #3 : Hardcoded UUIDs dans `chat_handler.py`

`execution/chat_handler.py` lignes 755-756 :
```python
REAL_USER_ID = "3138517c-eb64-4b05-af16-7070bf969dd5"  # Jean Dupont
REAL_ETUDE_ID = "a2cb1402-4784-47de-9261-99e9d22bbf08"
```

Tous les utilisateurs sont identifies comme le meme user de test. Le multi-tenant ne fonctionne pas cote chat.

### CRITIQUE #4 : Supabase anon key en dur

`frontend/lib/supabase.ts` ligne 6 -- La cle Supabase anon est hardcodee comme fallback dans le code. Si `.env.local` n'est pas configure, la cle est exposee dans le bundle client.

---

## 3. PROBLEMES IMPORTANTS (Non-bloquants mais a corriger)

### Securite Supabase (13 erreurs, 1 table sans RLS)

Resultats de l'advisor Supabase :
- **13 vues SECURITY_DEFINER** (niveau ERROR) : `v_cost_alerts`, `v_kpis_etude`, `v_dossiers_dashboard`, etc. -- Elles s'executent avec les droits du createur au lieu de l'appelant, contournant le RLS
- **1 table sans RLS** : `api_costs_tracking` -- donnees de couts accessibles publiquement
- **8 fonctions avec `search_path` mutable** (niveau WARN) -- risque d'injection SQL
- **Protection contre mots de passe compromis desactivee** dans Supabase Auth

### Templates non-modulaires (promesse)

Les templates promesse n'utilisent PAS d'includes dynamiques (`{% include %}`). Les sections sont soit inline soit pre-assemblees par le Python. Seul le template vente utilise `{% include %}`. Modifier une section promesse necessite de modifier le template principal.

### Modal : couteux et sans datacenter en France

- Modal applique un multiplicateur 3.75x sur les prix EU (1.25x EU * 3x non-preemptible)
- Aucun datacenter en France -- seulement "EU" generique
- `min_containers=1` coute ~$30-50/mois juste en standby
- Pour un SaaS notarial francais, c'est une faiblesse RGPD (donnees hors France)

### Signed URLs avec cle dev par defaut

`execution/security/signed_urls.py` : si `URL_SIGNING_KEY` n'est pas defini, utilise une cle hardcodee `"dev_only_key_change_in_production_immediately"`. Devrait faire crasher en prod.

### DOCX metadata non strippee

`execution/core/exporter_docx.py` ne supprime pas les metadonnees du DOCX (auteur, chemins, timestamps). Risque RGPD.

### weekly_catalog_sync ecrit sur filesystem read-only

`deployment_modal/modal_app.py` ligne 251 : `catalog_path.write_text(...)` echouera sur Modal car le filesystem est read-only (hors `/outputs`).

### `execution/self_anneal.py` n'existe pas

Importe dans modal_app.py ligne 187 mais le fichier n'existe pas. Gere gracieusement par try/except, mais la feature de self-annealing ne fonctionne pas.

---

## 4. ANALYSE SECURITE RGPD

### Ce qui est bien fait

- Chiffrement PII cote application (`encryption_service.py`, `anonymiser_docx.py`)
- Tables `rgpd_requests` et `audit_logs` deja en place
- RLS active sur 16/17 tables
- `.env` jamais commite (verifie dans l'historique Git)
- `secure_client_manager.py` pour gerer les donnees clients
- HMAC-SHA256 pour les URLs signees avec comparaison timing-safe
- Chat anonymizer pour ne pas envoyer de PII aux LLMs

### Ce qui manque

| Exigence RGPD | Statut | Priorite |
|---------------|--------|----------|
| DPA signe avec Supabase | Absent | CRITIQUE |
| Hebergement en France / SecNumCloud | Non (Supabase = Frankfurt) | IMPORTANT |
| AIPD (Analyse d'impact) | Non realisee | IMPORTANT |
| Politique de retention des donnees | Non implementee | IMPORTANT |
| Workflow droit a l'effacement | Table existe mais pas de workflow | IMPORTANT |
| Registre des traitements | Absent | OBLIGATOIRE |
| Politique de confidentialite | Absente du frontend | OBLIGATOIRE |
| Designation DPO | Non fait | RECOMMANDE |
| Procedure notification de breach | Absente | OBLIGATOIRE |
| Liste des sous-traitants | Absente | OBLIGATOIRE |

### Recommandation infrastructure RGPD

La profession notariale utilise SecNumCloud (OVHcloud) pour le Minutier Central. Pour un MVP, Supabase EU + DPA signe suffit. Mais pour etre adopte par le CSN ou les grandes etudes, il faudra migrer vers un hebergeur SecNumCloud qualifie.

---

## 5. MODAL : GARDER OU CHANGER ?

### Verdict : Garder pour l'instant, planifier la migration

| Critere | Modal | Google Cloud Run (Paris) | AWS Lambda (Frankfurt) |
|---------|-------|--------------------------|------------------------|
| Datacenter France | Non | OUI (europe-west9) | Non |
| Prix (10k gen/mois) | ~$50-150 | ~$15-30 | ~$15-30 |
| DX Python | Excellente | Bonne | Correcte |
| Cold start | Aucun (min_containers=1) | <100ms (2nd gen) | 200-400ms |
| GPU pour OCR/ML | Excellent | Non natif | Non natif |
| RGPD/SecNumCloud | EU generique | DPA + Paris | DPA + Frankfurt |

**Strategie recommandee** : Architecture split
1. Court terme : Garder Modal (ca marche, DX excellente)
2. Moyen terme : Migrer l'API principale vers GCP Cloud Run (Paris) pour la conformite
3. Garder Modal uniquement pour les taches GPU/ML (OCR, extraction titres)

**Estimation cout startup** (~1000 docs/mois) :
- Fly.io/Railway pour API : $20-50/mo
- Modal pour agents IA (on-demand) : $30 free tier
- Supabase Pro : $25/mo
- Total : ~$75-105/mo

---

## 6. RAG : FAUT-IL L'IMPLEMENTER ?

### Verdict : Pas maintenant, mais preparer le terrain

L'approche template Jinja2 est la bonne pour la generation d'actes. Les meilleurs legal tech (Gavel, HotDocs) font pareil. RAG n'est pas fiable a 100% et les actes notariaux exigent une fidelite absolue.

### Ou RAG apporterait de la valeur (Phase 2-3)

1. **Suggestion intelligente de clauses** -- embedder les 45+ clauses via Supabase pgvector
2. **Smart Q&R** -- Suggerer des reponses basees sur les dossiers precedents
3. **Recherche jurisprudentielle** -- Retrouver des precedents pertinents
4. **Reference legale** -- Citer les bons articles du Code Civil

### Implementation recommandee : Supabase pgvector

Pas besoin de LlamaIndex/LangChain -- Supabase supporte nativement pgvector :

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE clause_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    clause_id TEXT,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE FUNCTION search_clauses(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 5
)
RETURNS TABLE (clause_id TEXT, content TEXT, similarity FLOAT)
AS $$
    SELECT clause_id, content, 1 - (embedding <=> query_embedding) AS similarity
    FROM clause_embeddings
    WHERE 1 - (embedding <=> query_embedding) > match_threshold
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$ LANGUAGE sql STABLE;
```

Ne PAS utiliser RAG pour : l'assemblage de templates (garder Jinja2), la validation (garder le deterministe).

---

## 7. UX NOTAIRE

### Ce qui est bien

- Design elegant : palette creme/or (#c9a962), Cormorant Garamond -- ca fait notarial et premium
- Landing page rassurante : mentions "Donnees chiffrees", "Hebergement europeen", "Conforme RGPD"
- Workflow guide en 5 etapes (TYPE_SELECT -> DONE) -- tres bon concept
- 7 types de champs (text, number, date, select, boolean, array, contact)
- SSE streaming pour le chat (reponses progressives)

### Ce qui pose probleme

| Probleme UX | Impact | Gravite |
|-------------|--------|---------|
| Le workflow ne marche pas (api.ts manquant) | Notaire bloque des la 1ere utilisation | CRITIQUE |
| Pas d'onboarding / tutoriel | Notaire perdu | IMPORTANT |
| Pas de page "Mes documents" / historique accessible | Notaire ne retrouve pas ses actes | IMPORTANT |
| Chat et Workflow sont 2 pages separees sans lien clair | Confusion sur quel outil utiliser | MOYEN |
| userId stocke dans localStorage au lieu de Supabase Auth | Session perdue si cookies effaces | MOYEN |
| Pas de responsive / mobile | Pas utilisable sur tablette | FAIBLE (v2) |

### Vision UX recommandee

Le workflow guide devrait etre l'experience centrale, pas le chat. Un notaire devrait pouvoir :
1. Se connecter (Auth Supabase)
2. Voir son tableau de bord (dossiers en cours, rappels)
3. Creer un nouvel acte via le workflow guide
4. Repondre aux questions section par section
5. Voir l'apercu de l'acte genere
6. Telecharger le DOCX
7. Donner du feedback

---

## 8. PAYSAGE CONCURRENTIEL

### Marche francais du logiciel notarial

| Entreprise | Produit | Position | CA | IA |
|-----------|---------|----------|----|----|
| Septeo/Genapi | Suite complete | Leader (~50%+) | 310M EUR | 50M investis, IA generative depuis 2024 |
| Fichorga | Authentic, Juris web | #2 (~25-30%) | - | Analyse IA d'actes (2025) |
| Fiducial | Signature | #3 (~20-25%) | - | FIDJI analyse IA |

### Positionnement recommande pour Notomai

Ne PAS attaquer Septeo frontalement. Se positionner comme :
- **API/moteur white-label** integreable avec les outils existants
- **Alternative rapide et moderne** pour notaires frustres par les outils legacy
- **Specialiste generation d'actes** (pas suite complete)

### Avantages differenciants

1. Architecture cloud-native vs legacy on-premise des concurrents
2. Template-first avec 100% fidelite aux trames originales
3. Integration Claude Opus 4.6 vs IA proprietaire
4. Vitesse : 5-8s vs "minutes" chez les concurrents
5. 7 templates, 4 categories de bien, support viager

---

## 9. CE QUE VOUS N'AVEZ PAS MENTIONNE

1. **Tests E2E frontend** : Aucun test frontend (pas de Vitest, Jest, Cypress, Playwright)
2. **Monitoring** : Aucun outil (Sentry, LogRocket, Datadog)
3. **Rate limiting frontend** : Le chat n'a aucun rate limit cote frontend
4. **Versioning des actes** : Pas de versioning DOCX (ancienne version perdue si modifiee)
5. **CLAUDE.md surdimensionne** : 500+ lignes melangeant doc, changelog et instructions
6. **historique.py** : Schema SQL jamais applique en migration (code mort)
7. **docxtpl** : Alternative a explorer -- Jinja2 directement dans le .docx, elimine l'etape Markdown

---

## 10. PLAN D'ACTION

### Profils equipe

- **Payoss (Paul)** : Full-stack, architecte principal, connaissance profonde du projet
- **Tom** : Frontend React/Next.js
- **Augustin** : Backend/infra

### SPRINT 1 -- DEBLOCAGE (1-2 semaines)

| Tache | Qui | Duree | Priorite |
|-------|-----|-------|----------|
| Creer `frontend/lib/api.ts` -- Client API avec toutes les fonctions importees par workflowStore | Tom | 2-3 jours | CRITIQUE |
| Creer les endpoints `/workflow/*` dans l'API | Augustin | 3-4 jours | CRITIQUE |
| Supprimer la Supabase anon key hardcodee de supabase.ts | Tom | 30 min | CRITIQUE |
| Supprimer les UUIDs hardcodes dans chat_handler.py -- extraire du JWT | Augustin | 1 jour | CRITIQUE |
| Revue croisee : verifier que tout s'integre | Payoss | 1 jour | CRITIQUE |

### SPRINT 2 -- SECURITE (1-2 semaines)

| Tache | Qui | Duree | Priorite |
|-------|-----|-------|----------|
| Corriger les 13 vues SECURITY_DEFINER -> SECURITY_INVOKER | Augustin | 1 jour | IMPORTANT |
| Activer RLS sur api_costs_tracking | Augustin | 30 min | IMPORTANT |
| Fixer les 8 fonctions avec search_path mutable | Augustin | 1 jour | IMPORTANT |
| Activer protection mots de passe compromis (Supabase Auth) | Payoss | 30 min | IMPORTANT |
| Signer le DPA Supabase | Payoss | 1 heure | OBLIGATOIRE |
| Ajouter politique de confidentialite sur la landing | Tom | 1 jour | OBLIGATOIRE |
| Creer le registre des traitements (document RGPD) | Payoss | 2 jours | OBLIGATOIRE |
| Supprimer cle dev par defaut dans signed_urls.py | Augustin | 30 min | IMPORTANT |
| Strip metadata DOCX dans exporter_docx.py | Augustin | 1 jour | IMPORTANT |
| Rediger procedure de notification de breach | Payoss | 1 jour | OBLIGATOIRE |

### SPRINT 3 -- UX NOTAIRE (2-3 semaines)

| Tache | Qui | Duree | Priorite |
|-------|-----|-------|----------|
| Page "Mes documents" -- historique des actes | Tom | 3-4 jours | IMPORTANT |
| Onboarding -- premier lancement avec explication | Tom | 2 jours | IMPORTANT |
| Lier chat et workflow -- bouton "Passer au workflow guide" | Tom | 1 jour | MOYEN |
| Erreurs utilisateur claires -- si Modal down, si validation echoue | Tom | 1 jour | MOYEN |
| Dashboard notaire -- KPIs, actes generes, rappels | Tom | 3-4 jours | MOYEN |
| Feedback integre -- formulaire post-generation | Tom | 1 jour | MOYEN |

### SPRINT 4 -- INFRASTRUCTURE (2-3 semaines)

| Tache | Qui | Duree | Priorite |
|-------|-----|-------|----------|
| CI/CD GitHub Actions -- lint + tests + build + deploy | Augustin | 2-3 jours | IMPORTANT |
| Tests frontend -- Setup Vitest + tests composants critiques | Tom | 3-4 jours | IMPORTANT |
| Monitoring -- Sentry (erreurs frontend+backend), uptime check | Augustin | 1-2 jours | IMPORTANT |
| Rate limiting frontend -- gerer les 429, debounce chat | Tom | 1 jour | MOYEN |
| Versioning documents -- stocker versions dans Supabase Storage | Augustin | 2-3 jours | MOYEN |
| Nettoyer CLAUDE.md -- separer en CHANGELOG.md, ARCHITECTURE.md | Payoss | 1 jour | MOYEN |
| Fix weekly_catalog_sync (ecriture filesystem -> Supabase) | Augustin | 1 jour | MOYEN |

### SPRINT 5 -- EVOLUTION (3-4 semaines)

| Tache | Qui | Duree | Priorite |
|-------|-----|-------|----------|
| Evaluer migration GCP Cloud Run (Paris) pour API principale | Augustin | 1 semaine | PLANIFIE |
| POC RAG -- Supabase pgvector pour suggestion de clauses | Payoss | 1 semaine | PLANIFIE |
| POC docxtpl -- Jinja2 directement dans .docx (pilote modificatif_edd) | Payoss | 1 semaine | PLANIFIE |
| Templates {% include %} -- modulariser les promesses | Payoss | 2-3 jours | PLANIFIE |
| Responsive tablette | Tom | 2-3 jours | PLANIFIE |
| ISO 27001 -- lancer le processus de certification | Payoss | En continu | PLANIFIE |

### Attribution confirmee des axes (18/02/2026)

| Axe | Titre | Qui (CONFIRME) |
|-----|-------|----------------|
| **1** | Connexion Frontend <-> Backend | **Paul** |
| 2 | Nettoyage Frontend | Tom (a confirmer) |
| 3 | Nettoyage Backend | (a attribuer) |
| **4** | Securite Base de Donnees | **Augustin** ✅ |
| **5** | Securite Code (Secrets) | **Augustin** ✅ |
| **6** | Infrastructure & DevOps | **Augustin** ✅ |
| 7 | UX & Experience Notaire | Tom (a confirmer) |
| 8 | Tests & Qualite | Tom (a confirmer) |
| **9** | RGPD & Conformite | **Augustin** ✅ |
| 10 | Architecture & Documentation | Paul |

### Resume des roles

| Personne | Focus principal | Axes |
|----------|----------------|------|
| Payoss (Paul) | Architecture, connexion front-back, revue code | Axes 1, 10 |
| Tom | Frontend, UX notaire, tests frontend | Axes 2, 7, 8 (a confirmer) |
| Augustin | Securite, RGPD, infra, DevOps | **Axes 4, 5, 6, 9** (confirmes) |

---

## 11. VERDICT FINAL

### Bonne direction ?

OUI, globalement. L'architecture 3 couches (Directive/Orchestration/Execution) est solide. Le choix Jinja2 pour les templates est le bon. Les schemas sont riches et bien structures. Le support viager avec detection multi-marqueurs est impressionnant.

### Mauvaise direction quelque part ?

1. Le CLAUDE.md est devenu un changelog au lieu de rester des instructions concises. Il faut le separer.
2. Le frontend a ete developpe en parallele du backend sans s'assurer que les deux communiquent. Resultat : 23 composants beaux mais un fichier api.ts manquant qui casse tout.
3. Modal est un bon choix pour le prototypage mais pas ideal pour la production francaise (pas de DC France, couteux avec multiplicateurs EU).

### Le plus urgent

Creer `frontend/lib/api.ts` + les endpoints `/workflow/*` = le workflow guide fonctionne. Sans ca, le produit est une coquille vide cote utilisateur.

---

*Audit realise par Claude Opus 4.6 le 18/02/2026*
*Sources : analyse code, Supabase advisors, recherches web (RAG, RGPD, Modal, legal tech)*
