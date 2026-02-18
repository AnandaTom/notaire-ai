# Prompts Equipe Notomai - Post-Audit 18 Fevrier 2026

3 prompts a copier-coller dans Claude Code, un par personne.
Meme briefing projet + meme liste de 10 axes dans chaque prompt.
Chacun choisit son axe pour ne pas se marcher dessus.
Paul a deja choisi l'axe 1 (connexion front/back).

---

## PROMPT PAUL (Payoss)

```
Passe en mode plan.

# CONTEXTE DU PROJET — NOTOMAI

## C'est quoi ce projet ?

Notomai est un logiciel pour les notaires. Un notaire, c'est la personne qui signe les actes quand tu achetes une maison, un appartement, un terrain. Pour chaque vente, le notaire doit rediger un document officiel (un "acte") qui fait entre 20 et 80 pages. Aujourd'hui, il le fait a la main dans Word en copiant-collant des morceaux de texte. Ca prend des heures.

Notomai automatise ca : le notaire repond a des questions (qui vend ? qui achete ? quel bien ? quel prix ?) et le logiciel genere automatiquement le document Word final, 100% conforme au modele officiel.

## Comment ca marche techniquement ?

Le projet a 3 grandes parties :

### 1. Le FRONTEND (ce que le notaire voit dans son navigateur)
- Technologie : Next.js 14 + React + Tailwind CSS + Zustand (gestion d'etat)
- Dossier : `frontend/`
- 2 pages principales :
  - **Page Chat** (`frontend/app/app/page.tsx`) : le notaire ecrit en langage naturel et l'IA repond en temps reel. CA MARCHE.
  - **Page Workflow** (`frontend/app/app/workflow/page.tsx`) : le notaire repond a des questions etape par etape dans un formulaire guide. CA NE MARCHE PAS (le fichier de liaison `frontend/lib/api.ts` n'existe pas).
- Composants dans `frontend/components/` (23+ fichiers), store dans `frontend/stores/workflowStore.ts`

### 2. Le BACKEND (le serveur qui fait le travail)
- Technologie : Python + FastAPI, deploye sur Modal (un service cloud)
- `api/main.py` = point d'entree API. `execution/` = 87 scripts Python (assemblage, export DOCX, detection, validation, etc.)
- `templates/` = 7 templates Jinja2 de documents (vente, promesse copro, promesse hors copro, terrain, viager, reglement copro, modificatif)
- `deployment_modal/modal_app.py` = configuration du deploiement Modal
- Le chat fonctionne via `execution/chat_handler.py` (streaming SSE, 1072+ lignes)

### 3. La BASE DE DONNEES (Supabase)
- Technologie : Supabase = PostgreSQL heberge (Francfort, EU)
- 17 tables : etudes notariales, clients, dossiers, conversations, actes generes, audit logs
- Multi-tenant : chaque etude ne voit que ses donnees (RLS = Row Level Security)
- Migrations dans `supabase/migrations/`

## Etat actuel

| Composant | Etat | Note |
|-----------|------|------|
| Pipeline Python (assemblage + DOCX) | MARCHE | 257 tests, solide |
| Chat navigateur (SSE) | MARCHE | Streaming temps reel |
| 7 templates de documents | MARCHE | Conformite 80-92% |
| Detection type de bien | MARCHE | 3 niveaux (categorie/type/sous-type) |
| Base Supabase (17 tables) | MARCHE | RLS actif sur 16/17 tables |
| Workflow guide (formulaire) | CASSE | `frontend/lib/api.ts` n'existe pas + endpoints backend manquants |
| Multi-tenant chat | CASSE | UUIDs hardcodes dans chat_handler.py (meme user pour tout le monde) |
| Securite Supabase | PROBLEMES | 13 vues mal configurees, 1 table sans RLS |
| RGPD | INCOMPLET | Pas de DPA, pas de registre, pas de politique confidentialite |

## L'equipe

- **Paul (Payoss)** — c'est moi. Architecte, full-stack. 35 commits
- **Tom (AnandaTom)** — frontend React. 158 commits
- **Augustin (augustinfrance-aico)** — backend Python, infra, Supabase. 46 commits

## L'objectif

Le systeme de generation d'actes doit etre operationnel le plus vite possible :
1. Le notaire ouvre le site
2. Il choisit un type d'acte
3. Il repond aux questions
4. Il recoit son fichier Word

---

# LES 10 AXES DE TRAVAIL DU PROJET

Lis d'abord docs/AUDIT_COMPLET_18_FEVRIER_2026.md pour le detail complet de l'audit.

Puis analyse le code et propose-moi un plan detaille pour l'axe que j'ai choisi (AXE 1). Mais je veux d'abord que tu listes TOUT ce qu'il y a a faire dans CHAQUE axe, pour que je voie la vue d'ensemble. Tom et Augustin recevront la meme liste et choisiront leurs axes.

## AXE 1 — Connexion Frontend <-> Backend ← J'AI CHOISI CELUI-CI
Le probleme central : le frontend et le backend ne se parlent pas pour le workflow.
- Le fichier `frontend/lib/api.ts` n'existe pas. Il est importe par workflowStore.ts (ligne 12) et FeedbackPanel.tsx (ligne 5). Il devrait contenir les fonctions : startWorkflow(), submitAnswers(), validateField(), streamGeneration(), sendFeedback()
- Le fichier `frontend/lib/api/promesse.ts` n'existe pas non plus. Il est importe par useViagerDetection.ts (ligne 7) et ViagerBadge.tsx. Il devrait contenir : detecterType(), getQuestions(), validerPromesse()
- Les endpoints backend pour le workflow n'existent pas : POST /workflow/start, POST /workflow/{id}/submit, GET /workflow/{id}/generate-stream, POST /workflow/{id}/validate-field, POST /feedback
- La page chat (page.tsx) fonctionne car elle fait des fetch() directs — c'est le modele a suivre
- Des URLs Modal sont hardcodees dans WorkflowPage.tsx (ligne 8), page.tsx (ligne 11) — a centraliser

## AXE 2 — Nettoyage & Optimisation Frontend
Le code frontend a 23+ composants ecrits par 2 personnes (Tom + Augustin) avec 2 IA differentes (Sonnet + Opus), sans coordination.
- Fichiers morts : des composants qui ne sont importes nulle part ?
- Imports inutilises : on importe des choses qu'on n'utilise jamais ?
- Code duplique : meme logique copiee-collee dans plusieurs composants ?
- Composants trop gros a decouper (WorkflowPage.tsx 227 lignes, ChatWithViager.tsx 302 lignes)
- Types TypeScript incoherents ou dupliques entre frontend/types/workflow.ts et le reste
- Logique metier dans les composants qui devrait etre dans le store Zustand
- Re-renders inutiles (composants qui se re-affichent sans raison, manque de useMemo/useCallback)
- useEffect mal configures (boucles infinies, dependances manquantes)
- console.log oublies en production

## AXE 3 — Nettoyage & Optimisation Backend
87 scripts Python dans execution/, dont beaucoup semblent faire doublon.
- Doublons potentiels entre les scripts a la racine et les sous-dossiers :
  * exporter_acte.py vs core/exporter_docx.py
  * generer_acte_complet.py vs gestionnaires/orchestrateur.py
  * extraire_variables.py vs extraction/extracteur_v2.py
  * preparer_donnees_test.py vs generation/generer_donnees_test.py
- chat_handler.py fait 1072+ lignes — code mort, fonctions jamais appelees ?
- execution/database/historique.py : contient un schema SQL jamais applique en migration
- Imports inutilises, fonctions mortes, __init__.py incoherents
- Scripts anciens a la racine de execution/ qui sont peut-etre des v1 remplacees par les sous-dossiers

## AXE 4 — Securite Base de Donnees (Supabase)
L'audit a trouve 13 erreurs de securite dans Supabase.
- 13 vues utilisent SECURITY_DEFINER au lieu de SECURITY_INVOKER (elles contournent le RLS, c'est-a-dire que les donnees d'une etude peuvent etre vues par une autre) : v_cost_alerts, v_kpis_etude, v_dossiers_dashboard, v_recent_activity, v_activite_recente, v_statistiques_etude, v_stats_promesses_etude, v_rappels_proches, v_clients_etude, v_documents_dossier, v_conversions_promesse_vente, v_performance_agents
- La table api_costs_tracking n'a pas de RLS (ses donnees sont accessibles a tout le monde)
- 8 fonctions SQL ont un search_path mutable (risque d'injection SQL)
- Protection contre mots de passe compromis desactivee dans Supabase Auth

## AXE 5 — Securite Code (Secrets & Donnees)
Des cles, mots de passe et identifiants sont ecrits en dur dans le code.
- chat_handler.py lignes 755-756 : REAL_USER_ID et REAL_ETUDE_ID hardcodes — tous les utilisateurs du chat sont le meme user de test
- frontend/lib/supabase.ts ligne 6 : cle Supabase anon hardcodee en fallback dans le code
- execution/security/signed_urls.py : cle de dev "dev_only_key_change_in_production_immediately" utilisee si la variable d'environnement n'est pas definie
- execution/core/exporter_docx.py : les metadonnees du fichier Word genere (auteur, chemins, dates) ne sont pas supprimees — risque RGPD
- Verifier qu'aucune autre cle API ne traine dans les 87 scripts Python ou les composants React

## AXE 6 — Infrastructure & DevOps
Le deploiement et les outils de dev ont des problemes.
- deployment_modal/modal_app.py ligne 251 : weekly_catalog_sync ecrit sur le disque dur de Modal, mais Modal est en lecture seule — ca echoue silencieusement
- execution/self_anneal.py : importe dans modal_app.py, fonctionnement incertain
- min_containers=1 coute ~$30-50/mois en standby — justifie a ce stade ?
- Les 3 GitHub Actions : fonctionnent-elles ? Font-elles tourner les 257 tests ?
- Pas de monitoring (Sentry pour les erreurs, alertes si le serveur tombe)
- Pas de health check automatise
- Strategie de deploiement : faut-il evaluer GCP Cloud Run Paris pour la conformite RGPD ?

## AXE 7 — UX & Experience Notaire
Le site est beau mais il manque des choses pour que le notaire s'y retrouve.
- Pas d'onboarding (tutoriel a la premiere connexion)
- Pas de page "Mes documents" pour retrouver les actes deja generes
- Le chat et le workflow sont 2 pages separees sans lien entre elles (le notaire ne sait pas laquelle utiliser)
- Les messages d'erreur sont-ils comprehensibles pour un notaire (pas de jargon technique) ?
- Etats de chargement (loading/skeleton) quand le site attend une reponse du serveur ?
- Coherence entre les 7 types de champs (TextField, NumberField, DateField, SelectField, BooleanField, ArrayField, ContactField) : meme style, meme gestion d'erreur ?
- Dashboard notaire avec statistiques (actes generes, en cours, rappels)

## AXE 8 — Tests & Qualite
Le backend a 257 tests. Le frontend en a zero.
- Aucun test frontend (pas de Vitest, Jest, ni Playwright)
- Quels composants frontend tester en priorite ?
- Les 257 tests backend sont-ils a jour ? Couvrent-ils les endpoints de api/main.py ?
- Les tests tournent-ils automatiquement en CI (GitHub Actions) a chaque push ?
- Y a-t-il des parties du code sans aucun test ?
- Cas limites non geres : formulaire vide, donnees null, double-clic, erreur reseau, timeout

## AXE 9 — RGPD & Conformite Juridique
Les notaires manipulent des donnees tres sensibles (identites, patrimoine, prix). La loi RGPD impose des obligations.
- Pas de DPA (Data Processing Agreement) signe avec Supabase
- Pas de registre des traitements (document obligatoire listant ce qu'on fait avec les donnees)
- Pas de politique de confidentialite affichee sur le site
- Pas de procedure de notification en cas de fuite de donnees (obligatoire sous 72h)
- Pas de liste des sous-traitants (Modal, Supabase, Anthropic)
- Les donnees sont a Francfort (Supabase) et EU generique (Modal), pas en France — point sensible pour les notaires
- Le chiffrement PII existe (encryption_service.py) mais est-il applique partout ?
- Les tables rgpd_requests et audit_logs existent mais le workflow d'effacement n'est pas implemente

## AXE 10 — Architecture & Documentation
Le projet a grossi vite et la documentation n'a pas suivi.
- CLAUDE.md fait 500+ lignes et melange changelog, documentation, et instructions — a scinder
- Le dossier docs/ a 57+ fichiers — doublons ? fichiers obsoletes ?
- web/demo-workflow.html (1038 lignes) — fichier demo standalone, encore utile ?
- Faut-il evaluer docxtpl (Jinja2 directement dans .docx) vs le pipeline actuel (Markdown -> DOCX) ?
- Les templates promesse n'utilisent pas {% include %} (seul le template vente le fait) — les modulariser ?
- Le userId est stocke dans localStorage au lieu de Supabase Auth — quand migrer ?
- schemas/ a 17 fichiers JSON — sont-ils tous a jour et coherents entre eux ?

---

# CE QUE JE TE DEMANDE

1. Lis l'audit complet (docs/AUDIT_COMPLET_18_FEVRIER_2026.md)
2. Analyse le code pour chaque axe
3. Pour CHAQUE axe (les 10), liste tout ce qu'il y a a faire avec le detail des fichiers concernes
4. Pour MON axe (AXE 1), va en profondeur : lis les fichiers, note les signatures exactes, identifie chaque fonction manquante
5. Propose le plan complet. Je choisis l'ordre.
```

---

## PROMPT TOM

```
Passe en mode plan.

# CONTEXTE DU PROJET — NOTOMAI

## C'est quoi ce projet ?

Notomai est un logiciel pour les notaires. Un notaire, c'est la personne qui signe les actes quand tu achetes une maison, un appartement, un terrain. Pour chaque vente, le notaire doit rediger un document officiel (un "acte") qui fait entre 20 et 80 pages. Aujourd'hui, il le fait a la main dans Word en copiant-collant des morceaux de texte. Ca prend des heures.

Notomai automatise ca : le notaire repond a des questions (qui vend ? qui achete ? quel bien ? quel prix ?) et le logiciel genere automatiquement le document Word final, 100% conforme au modele officiel.

## Comment ca marche techniquement ?

Le projet a 3 grandes parties :

### 1. Le FRONTEND (ce que le notaire voit dans son navigateur)
- Technologie : Next.js 14 + React + Tailwind CSS + Zustand (gestion d'etat)
- Dossier : `frontend/`
- 2 pages principales :
  - **Page Chat** (`frontend/app/app/page.tsx`) : le notaire ecrit en langage naturel et l'IA repond en temps reel. CA MARCHE.
  - **Page Workflow** (`frontend/app/app/workflow/page.tsx`) : le notaire repond a des questions etape par etape dans un formulaire guide. CA NE MARCHE PAS (le fichier de liaison `frontend/lib/api.ts` n'existe pas).
- Composants dans `frontend/components/` (23+ fichiers), store dans `frontend/stores/workflowStore.ts`
- Tes composants (ChatWithViager.tsx, ViagerBadge.tsx, useViagerDetection.ts) importent depuis `@/lib/api/promesse` qui n'existe pas encore — Paul va le creer

### 2. Le BACKEND (le serveur qui fait le travail)
- Technologie : Python + FastAPI, deploye sur Modal (un service cloud)
- `api/main.py` = point d'entree API. `execution/` = 87 scripts Python (assemblage, export DOCX, detection, validation, etc.)
- `templates/` = 7 templates Jinja2 de documents (vente, promesse copro, promesse hors copro, terrain, viager, reglement copro, modificatif)
- Le chat fonctionne via `execution/chat_handler.py` (streaming SSE, 1072+ lignes)

### 3. La BASE DE DONNEES (Supabase)
- Technologie : Supabase = PostgreSQL heberge (Francfort, EU)
- 17 tables : etudes notariales, clients, dossiers, conversations, actes generes
- Multi-tenant : chaque etude ne voit que ses donnees (RLS = Row Level Security)

## Etat actuel

| Composant | Etat | Note |
|-----------|------|------|
| Pipeline Python (assemblage + DOCX) | MARCHE | 257 tests, solide |
| Chat navigateur (SSE) | MARCHE | Streaming temps reel |
| 7 templates de documents | MARCHE | Conformite 80-92% |
| Detection type de bien | MARCHE | 3 niveaux (categorie/type/sous-type) |
| Base Supabase (17 tables) | MARCHE | RLS actif sur 16/17 tables |
| Workflow guide (formulaire) | CASSE | `frontend/lib/api.ts` n'existe pas + endpoints backend manquants |
| Multi-tenant chat | CASSE | UUIDs hardcodes dans chat_handler.py |
| Securite Supabase | PROBLEMES | 13 vues mal configurees, 1 table sans RLS |
| RGPD | INCOMPLET | Pas de DPA, pas de registre, pas de politique confidentialite |

## L'equipe

- **Paul (Payoss)** — architecte, full-stack. 35 commits. Il a deja choisi l'AXE 1 (connexion front/back : creer api.ts + verifier les endpoints)
- **Tom (AnandaTom)** — c'est toi. Frontend React. 158 commits. Tu as ecrit la majorite des composants
- **Augustin (augustinfrance-aico)** — backend Python, infra, Supabase. 46 commits

## L'objectif

Le systeme de generation d'actes doit etre operationnel le plus vite possible :
1. Le notaire ouvre le site
2. Il choisit un type d'acte
3. Il repond aux questions
4. Il recoit son fichier Word

---

# LES 10 AXES DE TRAVAIL DU PROJET

Voici tout ce qu'il y a a faire sur le projet, organise en 10 axes independants. Paul a deja pris l'axe 1. Lis-les tous et choisis celui ou ceux que tu veux prendre. Chaque axe est decrit pour que tu comprennes le probleme meme si tu as tout oublie.

Lis d'abord docs/AUDIT_COMPLET_18_FEVRIER_2026.md pour le detail complet de l'audit.

## AXE 1 — Connexion Frontend <-> Backend ← PRIS PAR PAUL
Le probleme central : le frontend et le backend ne se parlent pas pour le workflow.
- Le fichier `frontend/lib/api.ts` n'existe pas. Il est importe par workflowStore.ts (ligne 12) et FeedbackPanel.tsx (ligne 5). Il devrait contenir les fonctions : startWorkflow(), submitAnswers(), validateField(), streamGeneration(), sendFeedback()
- Le fichier `frontend/lib/api/promesse.ts` n'existe pas non plus. Il est importe par useViagerDetection.ts (ligne 7) et ViagerBadge.tsx. Il devrait contenir : detecterType(), getQuestions(), validerPromesse()
- Les endpoints backend pour le workflow n'existent pas : POST /workflow/start, POST /workflow/{id}/submit, GET /workflow/{id}/generate-stream
- Des URLs Modal sont hardcodees dans plusieurs fichiers au lieu d'utiliser des variables d'environnement

## AXE 2 — Nettoyage & Optimisation Frontend
Le code frontend a 23+ composants ecrits par 2 personnes (Tom + Augustin) avec 2 IA differentes (Sonnet + Opus), sans coordination.
- Fichiers morts : des composants qui ne sont importes nulle part ?
- Imports inutilises : on importe des choses qu'on n'utilise jamais ?
- Code duplique : meme logique copiee-collee dans plusieurs composants ?
- Composants trop gros a decouper (WorkflowPage.tsx 227 lignes, ChatWithViager.tsx 302 lignes)
- Types TypeScript incoherents ou dupliques entre frontend/types/workflow.ts et le reste
- Logique metier dans les composants qui devrait etre dans le store Zustand
- Re-renders inutiles (composants qui se re-affichent sans raison, manque de useMemo/useCallback)
- useEffect mal configures (boucles infinies, dependances manquantes)
- console.log oublies en production

## AXE 3 — Nettoyage & Optimisation Backend
87 scripts Python dans execution/, dont beaucoup semblent faire doublon.
- Doublons potentiels entre les scripts a la racine et les sous-dossiers :
  * exporter_acte.py vs core/exporter_docx.py
  * generer_acte_complet.py vs gestionnaires/orchestrateur.py
  * extraire_variables.py vs extraction/extracteur_v2.py
  * preparer_donnees_test.py vs generation/generer_donnees_test.py
- chat_handler.py fait 1072+ lignes — code mort, fonctions jamais appelees ?
- execution/database/historique.py : schema SQL jamais applique en migration
- Imports inutilises, fonctions mortes, __init__.py incoherents

## AXE 4 — Securite Base de Donnees (Supabase)
L'audit a trouve 13 erreurs de securite dans Supabase.
- 13 vues utilisent SECURITY_DEFINER au lieu de SECURITY_INVOKER (elles contournent le RLS — les donnees d'une etude peuvent etre vues par une autre). Vues concernees : v_cost_alerts, v_kpis_etude, v_dossiers_dashboard, v_recent_activity, v_activite_recente, v_statistiques_etude, v_stats_promesses_etude, v_rappels_proches, v_clients_etude, v_documents_dossier, v_conversions_promesse_vente, v_performance_agents
- La table api_costs_tracking n'a pas de RLS (donnees accessibles a tout le monde)
- 8 fonctions SQL ont un search_path mutable (risque d'injection SQL)
- Protection contre mots de passe compromis desactivee dans Supabase Auth

## AXE 5 — Securite Code (Secrets & Donnees)
Des cles, mots de passe et identifiants sont ecrits en dur dans le code.
- chat_handler.py lignes 755-756 : REAL_USER_ID et REAL_ETUDE_ID hardcodes — tous les utilisateurs du chat sont le meme user de test
- frontend/lib/supabase.ts ligne 6 : cle Supabase anon hardcodee en fallback
- execution/security/signed_urls.py : cle de dev "dev_only_key_change_in_production_immediately" si la variable d'environnement manque
- execution/core/exporter_docx.py : les metadonnees du DOCX (auteur, chemins, dates) ne sont pas supprimees — risque RGPD
- Verifier s'il y a d'autres secrets dans les 87 scripts Python ou les composants React

## AXE 6 — Infrastructure & DevOps
Le deploiement et les outils de dev ont des problemes.
- deployment_modal/modal_app.py ligne 251 : weekly_catalog_sync ecrit sur le disque dur de Modal, mais Modal est en lecture seule — ca echoue silencieusement
- execution/self_anneal.py : importe dans modal_app.py, fonctionnement incertain
- min_containers=1 coute ~$30-50/mois en standby — justifie a ce stade ?
- Les 3 GitHub Actions : fonctionnent-elles ? Font-elles tourner les 257 tests ?
- Pas de monitoring (Sentry, alertes si le serveur tombe)
- Evaluer GCP Cloud Run Paris pour la conformite RGPD (donnees en France)

## AXE 7 — UX & Experience Notaire
Le site est beau mais il manque des choses pour que le notaire s'y retrouve.
- Pas d'onboarding (tutoriel a la premiere connexion)
- Pas de page "Mes documents" pour retrouver les actes generes
- Le chat et le workflow sont 2 pages separees sans lien (le notaire ne sait pas laquelle utiliser)
- Messages d'erreur incomprehensibles pour un notaire ?
- Etats de chargement (loading/skeleton) quand le site attend le serveur ?
- Coherence entre les 7 types de champs (meme style, meme gestion d'erreur ?)
- Dashboard notaire avec statistiques

## AXE 8 — Tests & Qualite
Le backend a 257 tests. Le frontend en a zero.
- Aucun test frontend (pas de Vitest, Jest, Playwright)
- Quels composants tester en priorite ?
- Les 257 tests backend sont-ils a jour ? Couvrent-ils les endpoints ?
- Tests en CI automatique a chaque push ?
- Cas limites non geres : formulaire vide, donnees null, double-clic, erreur reseau

## AXE 9 — RGPD & Conformite Juridique
Les notaires manipulent des donnees sensibles. La RGPD impose des obligations legales.
- Pas de DPA signe avec Supabase (contrat sur le traitement des donnees)
- Pas de registre des traitements (document obligatoire)
- Pas de politique de confidentialite sur le site
- Pas de procedure de notification de fuite (obligatoire sous 72h)
- Donnees a Francfort et EU generique, pas en France
- Workflow d'effacement des donnees non implemente

## AXE 10 — Architecture & Documentation
Le projet a grossi vite et la documentation n'a pas suivi.
- CLAUDE.md fait 500+ lignes (melange changelog + doc + instructions) — a scinder
- docs/ a 57+ fichiers — doublons ? fichiers obsoletes ?
- web/demo-workflow.html (1038 lignes) — encore utile ?
- Evaluer docxtpl (Jinja2 directement dans .docx) vs pipeline Markdown -> DOCX ?
- Templates promesse sans {% include %} (seul vente l'utilise) — les modulariser ?
- userId dans localStorage au lieu de Supabase Auth
- 17 schemas JSON — coherents et a jour ?

---

# CE QUE JE TE DEMANDE

1. Lis l'audit complet (docs/AUDIT_COMPLET_18_FEVRIER_2026.md)
2. Analyse le code pour chaque axe
3. Pour CHAQUE axe (les 10), liste tout ce qu'il y a a faire avec le detail des fichiers concernes et une explication simple de chaque probleme
4. L'AXE 1 est pris par Paul. Propose-moi les axes les plus pertinents pour un dev frontend, mais ne choisis pas a ma place — je decide
5. Propose le plan complet. Je choisis.
```

---

## PROMPT AUGUSTIN

```
Passe en mode plan.

# CONTEXTE DU PROJET — NOTOMAI

## C'est quoi ce projet ?

Notomai est un logiciel pour les notaires. Un notaire, c'est la personne qui signe les actes quand tu achetes une maison, un appartement, un terrain. Pour chaque vente, le notaire doit rediger un document officiel (un "acte") qui fait entre 20 et 80 pages. Aujourd'hui, il le fait a la main dans Word en copiant-collant des morceaux de texte. Ca prend des heures.

Notomai automatise ca : le notaire repond a des questions (qui vend ? qui achete ? quel bien ? quel prix ?) et le logiciel genere automatiquement le document Word final, 100% conforme au modele officiel.

## Comment ca marche techniquement ?

Le projet a 3 grandes parties :

### 1. Le FRONTEND (ce que le notaire voit dans son navigateur)
- Technologie : Next.js 14 + React + Tailwind CSS + Zustand (gestion d'etat)
- Dossier : `frontend/`
- 2 pages principales :
  - **Page Chat** (`frontend/app/app/page.tsx`) : le notaire ecrit en langage naturel et l'IA repond en temps reel. CA MARCHE.
  - **Page Workflow** (`frontend/app/app/workflow/page.tsx`) : le notaire repond a des questions etape par etape dans un formulaire guide. CA NE MARCHE PAS (le fichier de liaison `frontend/lib/api.ts` n'existe pas).
- Composants dans `frontend/components/` (23+ fichiers), store dans `frontend/stores/workflowStore.ts`

### 2. Le BACKEND (le serveur qui fait le travail)
- Technologie : Python + FastAPI, deploye sur Modal (un service cloud)
- `api/main.py` = point d'entree API. `execution/` = 87 scripts Python organises en sous-dossiers :
  - `execution/core/` : fonctions de base (assembler un acte, exporter en DOCX, valider)
  - `execution/gestionnaires/` : logique metier (orchestrateur, gestionnaire de promesses/titres/clauses)
  - `execution/extraction/` : extraction de donnees depuis PDF/DOCX (OCR, patterns regex, ML)
  - `execution/generation/` : generation de donnees de test
  - `execution/database/` : acces a Supabase
  - `execution/security/` : chiffrement, anonymisation, gestion des cles
  - `execution/services/` : service cadastre (APIs gouvernementales)
  - `execution/api/` : endpoints internes (validation, feedback, cadastre)
  - `execution/analyse/` : analyse de documents
  - `execution/utils/` : utilitaires divers
  - + des scripts a la racine de execution/ (anciennes versions ?)
- `templates/` = 7 templates Jinja2 de documents
- Le chat fonctionne via `execution/chat_handler.py` (streaming SSE, 1072+ lignes)
- Deploiement : `deployment_modal/modal_app.py`

### 3. La BASE DE DONNEES (Supabase)
- Technologie : Supabase = PostgreSQL heberge (Francfort, EU)
- 17 tables : etudes notariales, clients, dossiers, conversations, actes generes, audit logs
- Multi-tenant : chaque etude ne voit que ses donnees (RLS = Row Level Security)
- Migrations dans `supabase/migrations/`

## Etat actuel

| Composant | Etat | Note |
|-----------|------|------|
| Pipeline Python (assemblage + DOCX) | MARCHE | 257 tests, solide |
| Chat navigateur (SSE) | MARCHE | Streaming temps reel |
| 7 templates de documents | MARCHE | Conformite 80-92% |
| Detection type de bien | MARCHE | 3 niveaux (categorie/type/sous-type) |
| Base Supabase (17 tables) | MARCHE | RLS actif sur 16/17 tables |
| Workflow guide (formulaire) | CASSE | `frontend/lib/api.ts` n'existe pas + endpoints backend manquants |
| Multi-tenant chat | CASSE | UUIDs hardcodes dans chat_handler.py (meme user pour tout le monde) |
| Securite Supabase | PROBLEMES | 13 vues mal configurees, 1 table sans RLS |
| RGPD | INCOMPLET | Pas de DPA, pas de registre, pas de politique confidentialite |

## L'equipe

- **Paul (Payoss)** — architecte, full-stack. 35 commits. Il a deja choisi l'AXE 1 (connexion front/back : creer api.ts + verifier les endpoints)
- **Tom (AnandaTom)** — frontend React. 158 commits
- **Augustin (augustinfrance-aico)** — c'est toi. Backend Python, infra, Supabase. 46 commits

## L'objectif

Le systeme de generation d'actes doit etre operationnel le plus vite possible :
1. Le notaire ouvre le site
2. Il choisit un type d'acte
3. Il repond aux questions
4. Il recoit son fichier Word

---

# LES 10 AXES DE TRAVAIL DU PROJET

Voici tout ce qu'il y a a faire sur le projet, organise en 10 axes independants. Paul a deja pris l'axe 1. Lis-les tous et choisis celui ou ceux que tu veux prendre. Chaque axe est decrit pour que tu comprennes le probleme meme si tu as tout oublie.

Lis d'abord docs/AUDIT_COMPLET_18_FEVRIER_2026.md pour le detail complet de l'audit.

## AXE 1 — Connexion Frontend <-> Backend ← PRIS PAR PAUL
Le probleme central : le frontend et le backend ne se parlent pas pour le workflow.
- Le fichier `frontend/lib/api.ts` n'existe pas. Il est importe par workflowStore.ts (ligne 12) et FeedbackPanel.tsx (ligne 5). Il devrait contenir les fonctions : startWorkflow(), submitAnswers(), validateField(), streamGeneration(), sendFeedback()
- Le fichier `frontend/lib/api/promesse.ts` n'existe pas non plus. Il est importe par useViagerDetection.ts (ligne 7) et ViagerBadge.tsx. Il devrait contenir : detecterType(), getQuestions(), validerPromesse()
- Les endpoints backend pour le workflow n'existent pas : POST /workflow/start, POST /workflow/{id}/submit, GET /workflow/{id}/generate-stream
- IMPORTANT POUR TOI : Paul va creer le fichier frontend qui appelle ces endpoints. Si les endpoints backend n'existent pas encore, il te demandera de les creer. La logique existe deja dans execution/ (gestionnaire_promesses.py, orchestrateur.py, assembler_acte.py, exporter_docx.py) — il faudra juste creer les routes FastAPI

## AXE 2 — Nettoyage & Optimisation Frontend
Le code frontend a 23+ composants ecrits par 2 personnes (Tom + Augustin) avec 2 IA differentes (Sonnet + Opus), sans coordination.
- Fichiers morts, imports inutilises, code duplique entre composants
- Composants trop gros, types incoherents, re-renders inutiles
- console.log oublies en production

## AXE 3 — Nettoyage & Optimisation Backend
87 scripts Python dans execution/, dont beaucoup semblent faire doublon.
- Doublons potentiels entre les scripts a la racine et les sous-dossiers :
  * exporter_acte.py vs core/exporter_docx.py
  * generer_acte_complet.py vs gestionnaires/orchestrateur.py
  * extraire_variables.py vs extraction/extracteur_v2.py
  * preparer_donnees_test.py vs generation/generer_donnees_test.py
- chat_handler.py fait 1072+ lignes — code mort, fonctions jamais appelees ?
- execution/database/historique.py : schema SQL jamais applique en migration
- Imports inutilises, fonctions mortes, __init__.py incoherents
- Scripts anciens a la racine de execution/ qui sont peut-etre des v1 remplacees par les sous-dossiers

## AXE 4 — Securite Base de Donnees (Supabase)
L'audit a trouve 13 erreurs de securite dans Supabase.
- 13 vues utilisent SECURITY_DEFINER au lieu de SECURITY_INVOKER (elles contournent le RLS — les donnees d'une etude peuvent etre vues par une autre). En clair : si un notaire de Paris se connecte, il pourrait voir les donnees d'un notaire de Lyon. Vues concernees : v_cost_alerts, v_kpis_etude, v_dossiers_dashboard, v_recent_activity, v_activite_recente, v_statistiques_etude, v_stats_promesses_etude, v_rappels_proches, v_clients_etude, v_documents_dossier, v_conversions_promesse_vente, v_performance_agents
- La table api_costs_tracking n'a pas de RLS (donnees accessibles a tout le monde)
- 8 fonctions SQL ont un search_path mutable (risque d'injection SQL — quelqu'un pourrait manipuler les requetes pour acceder a des donnees interdites)
- Protection contre mots de passe compromis desactivee dans Supabase Auth (si un utilisateur met un mot de passe qui a fuite sur internet, Supabase ne le bloque pas)

## AXE 5 — Securite Code (Secrets & Donnees)
Des cles, mots de passe et identifiants sont ecrits en dur dans le code.
- chat_handler.py lignes 755-756 : REAL_USER_ID et REAL_ETUDE_ID hardcodes — en clair, peu importe qui se connecte au chat, le serveur pense que c'est toujours le meme utilisateur de test. Le multi-tenant (separer les donnees par etude) ne fonctionne pas
- frontend/lib/supabase.ts ligne 6 : cle Supabase anon hardcodee en fallback. Si quelqu'un regarde le code source du site, il peut voir cette cle
- execution/security/signed_urls.py : cle de dev "dev_only_key_change_in_production_immediately" utilisee si la variable d'environnement manque. En production, ca veut dire que les URLs signees utilisent une cle connue de tous
- execution/core/exporter_docx.py : quand il genere un Word, il laisse des infos dedans (nom de l'ordinateur, chemin du fichier, date). Le notaire qui ouvre le document pourrait voir ces infos techniques — pas professionnel et risque RGPD
- Verifier s'il y a d'autres secrets dans les 87 scripts Python ou les composants React

## AXE 6 — Infrastructure & DevOps
Le deploiement et les outils de dev ont des problemes.
- deployment_modal/modal_app.py ligne 251 : weekly_catalog_sync essaie d'ecrire un fichier sur le disque dur, mais sur Modal le disque est en lecture seule (comme si tu essayais d'ecrire sur un DVD). Le script plante en silence, personne ne le sait
- execution/self_anneal.py : importe dans modal_app.py, fonctionnement incertain
- min_containers=1 signifie qu'on paie un serveur 24h/24 (~$30-50/mois) meme quand personne ne l'utilise. Est-ce necessaire maintenant ou peut-on mettre min_containers=0 et accepter un demarrage de 2-3 secondes ?
- Les 3 GitHub Actions (scripts qui tournent automatiquement quand on pousse du code) — fonctionnent-elles ? Font-elles tourner les 257 tests ?
- Pas de monitoring : si le serveur plante a 3h du matin, personne n'est prevenu
- Question strategique : Modal n'a pas de serveur en France. Pour les notaires (donnees sensibles), faut-il migrer vers Google Cloud Run qui a un datacenter a Paris ?

## AXE 7 — UX & Experience Notaire
Le site est beau mais il manque des choses pour que le notaire s'y retrouve.
- Pas d'onboarding : quand le notaire arrive pour la premiere fois, il n'y a pas de tutoriel
- Pas de page "Mes documents" : le notaire ne peut pas retrouver les actes qu'il a generes avant
- Le chat et le workflow sont 2 pages separees : le notaire ne comprend pas laquelle utiliser
- Les messages d'erreur sont-ils comprehensibles pour un notaire ou affichent-ils du jargon technique ?
- Quand le site attend une reponse du serveur, y a-t-il une animation de chargement ou un ecran fige ?
- Les 7 types de champs du formulaire (texte, nombre, date, liste deroulante, oui/non, tableau, contact) ont-ils le meme style et le meme comportement ?
- Dashboard notaire avec statistiques (combien d'actes generes, en cours, rappels)

## AXE 8 — Tests & Qualite
Le backend a 257 tests. Le frontend en a zero.
- Aucun test frontend : si quelqu'un casse un composant React, personne ne le sait avant qu'un utilisateur le signale
- Quels composants tester en priorite ? (les plus critiques = ceux du workflow)
- Les 257 tests backend sont-ils a jour ? Couvrent-ils les routes de l'API ?
- Les tests tournent-ils automatiquement a chaque push (CI/CD) ?
- Cas limites non geres : que se passe-t-il si le notaire soumet un formulaire vide ? Si la connexion internet coupe en pleine generation ? Si il double-clique sur "Generer" ?

## AXE 9 — RGPD & Conformite Juridique
Les notaires manipulent des donnees tres sensibles (identites completes, patrimoine, prix de vente). La loi RGPD impose des obligations strictes. Si on ne les respecte pas, l'amende peut aller jusqu'a 4% du chiffre d'affaires ou 20 millions d'euros.
- Pas de DPA signe avec Supabase : un DPA (Data Processing Agreement) est un contrat qui dit "Supabase, voici comment tu dois traiter nos donnees". C'est obligatoire
- Pas de registre des traitements : document obligatoire qui liste toutes les donnees qu'on collecte, pourquoi, combien de temps on les garde
- Pas de politique de confidentialite sur le site : page obligatoire qui explique aux notaires ce qu'on fait de leurs donnees
- Pas de procedure en cas de fuite : si quelqu'un pirate la base, on a 72h pour prevenir la CNIL. On n'a aucune procedure pour ca
- Donnees a Francfort (Supabase) et EU generique (Modal), pas en France — les notaires y sont sensibles
- Le chiffrement existe dans le code (encryption_service.py) mais est-il applique partout ?

## AXE 10 — Architecture & Documentation
Le projet a grossi vite et la documentation n'a pas suivi.
- CLAUDE.md fait 500+ lignes (melange changelog + doc + instructions) — a scinder en fichiers separes
- docs/ a 57+ fichiers — doublons ? fichiers obsoletes ?
- web/demo-workflow.html (1038 lignes) — fichier demo standalone, encore utile ?
- Evaluer docxtpl (Jinja2 directement dans .docx) vs pipeline Markdown -> DOCX
- Templates promesse sans {% include %} (seul vente l'utilise) — les modulariser ?
- userId dans localStorage au lieu de Supabase Auth
- 17 schemas JSON — coherents et a jour ?

---

# CE QUE JE TE DEMANDE

1. Lis l'audit complet (docs/AUDIT_COMPLET_18_FEVRIER_2026.md)
2. Analyse le code pour chaque axe
3. Pour CHAQUE axe (les 10), liste tout ce qu'il y a a faire avec le detail des fichiers concernes et une explication simple de chaque probleme
4. L'AXE 1 est pris par Paul. Propose-moi les axes les plus pertinents pour un dev backend/infra, mais ne choisis pas a ma place — je decide
5. Propose le plan complet. Je choisis.
```

---

*Genere le 18/02/2026 a partir de l'audit complet Notomai*
