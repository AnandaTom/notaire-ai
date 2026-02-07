# Avancement Securite - Notomai

**Derniere mise a jour** : 5 fevrier 2026
**Auteur** : Audit automatise (Claude Opus 4.5)

---

## En resume

Un audit de securite complet a ete realise sur le code de Notomai. Il a revele **5 problemes critiques** et **5 points de renforcement**. Nous les corrigeons un par un.

**Phase 1 (critiques) : 5/5 termines**
**Phase 2 (renforcement) : 5/5 termines**

Phase 3 commencee (1/5). Les 4 points restants seront traites plus tard. On passe au developpement du chat.

---

## Ce qui a ete fait (Phase 1 - Corrections critiques)

### 1. Anonymisation des donnees envoyees a l'IA Claude

| | |
|---|---|
| **Le probleme** | Quand un notaire discute avec le chatbot, tout le texte (noms, adresses, dates de naissance, patrimoine) etait envoye tel quel aux serveurs d'Anthropic aux Etats-Unis. C'est une fuite de donnees personnelles. |
| **Ce qu'on a fait** | On a cree un filtre (`chat-anonymizer.ts`) qui remplace automatiquement les noms, adresses, prix et dates par des codes anonymes AVANT d'envoyer le message a l'IA. Quand l'IA repond, les codes sont re-transformes en vrais noms pour l'affichage. L'IA ne voit jamais les vraies donnees. |
| **Fichiers modifies** | `frontend/lib/chat-anonymizer.ts` (cree), `frontend/app/api/chat/route.ts` (reecrit) |
| **Statut** | FAIT |

### 2. Remplacement du systeme de connexion

| | |
|---|---|
| **Le probleme** | Le mot de passe du notaire etait "hashe" (transforme en code) avec une methode faible (SHA-256 sans sel), puis envoye dans l'URL de la page. Cela signifie que le mot de passe code etait visible dans les logs du serveur et dans l'historique du navigateur. Un pirate pouvait facilement retrouver le vrai mot de passe. |
| **Ce qu'on a fait** | On a remplace tout ca par le systeme d'authentification integre de Supabase (notre base de donnees). Ce systeme utilise bcrypt (beaucoup plus resistant), des jetons de session temporaires (JWT), et un rafraichissement automatique. Le mot de passe n'apparait jamais dans une URL. On a aussi supprime l'ancienne colonne `password_hash` de la base de donnees. |
| **Fichiers modifies** | `web/supabase-client.js` (reecrit section auth), `web/dashboard-notaire.html` (login/logout adapte), migration SQL appliquee |
| **Statut** | FAIT |

### 3. Restriction des origines autorisees (CORS)

| | |
|---|---|
| **Le probleme** | L'API de feedback acceptait des requetes depuis **n'importe quel site web** (`*`). Un site malveillant pouvait donc envoyer des requetes a notre API en se faisant passer pour un utilisateur. |
| **Ce qu'on a fait** | On a restreint les origines autorisees aux seuls domaines Notomai (`anandatom.github.io` et `notaire-ai--fastapi-app.modal.run`). En mode developpement, `localhost` est aussi autorise. |
| **Fichier modifie** | `execution/api/api_feedback.py` |
| **Statut** | FAIT |

### 4. Protection contre l'injection de commandes dans le chatbot

| | |
|---|---|
| **Le probleme** | Le parametre "format" (pdf ou docx) envoye par l'utilisateur etait injecte directement dans les instructions de l'IA, sans verification. Un utilisateur malveillant pouvait envoyer un faux "format" contenant des instructions pour manipuler l'IA. |
| **Ce qu'on a fait** | On a ajoute une liste blanche : seuls `pdf` et `docx` sont acceptes. Tout autre valeur est rejetee. On a aussi limite la longueur des messages et verifie que la structure des donnees est correcte. |
| **Fichier modifie** | `frontend/app/api/chat/route.ts` |
| **Statut** | FAIT |

### 5. Mise a jour de la documentation legale

| | |
|---|---|
| **Le probleme** | Les documents legaux (registre des traitements, politique de confidentialite) affirmaient que les donnees personnelles n'etaient pas envoyees a l'IA. C'etait faux. En cas de controle CNIL, cela aurait ete considere comme une fausse declaration. |
| **Ce qu'on a fait** | On a mis a jour les deux documents pour refleter honnetement la situation : oui, les conversations transitent par Anthropic (USA), avec les garanties contractuelles en place, et un module d'anonymisation est en cours d'integration. |
| **Fichiers modifies** | `docs/legal/REGISTRE_TRAITEMENTS.md`, `docs/legal/POLITIQUE_CONFIDENTIALITE.md` |
| **Statut** | FAIT |

---

## Ce qui a ete fait (Phase 2 - Renforcement)

### 6. Chiffrement des donnees rendu obligatoire

| | |
|---|---|
| **Le probleme** | Le code de chiffrement des donnees sensibles (noms, adresses) existait, mais il etait optionnel. Si la librairie de chiffrement n'etait pas installee, les donnees etaient stockees en clair dans des champs appeles "..._encrypted". C'est trompeur et dangereux. |
| **Ce qu'on a fait** | Le systeme refuse maintenant de demarrer si le chiffrement n'est pas disponible. Plus aucun fallback en texte clair. Si la librairie `cryptography` n'est pas installee ou que la cle manque, une erreur claire s'affiche. |
| **Fichier modifie** | `execution/security/secure_client_manager.py` |
| **Statut** | FAIT |

### 7. Limite de requetes (rate limiting) ajoutee

| | |
|---|---|
| **Le probleme** | Rien n'empechait quelqu'un d'envoyer des milliers de requetes par seconde a l'API. Ca pouvait saturer le systeme ou servir a deviner des mots de passe par essais successifs. |
| **Ce qu'on a fait** | On a ajoute un compteur en memoire qui limite le nombre de requetes par cle API et par minute. Quand la limite est depassee, l'API repond avec une erreur 429 "Too Many Requests". La limite est configurable par cle (defaut: 60 requetes/minute). |
| **Fichier modifie** | `api/main.py` (classe `RateLimiter` + integration dans `verify_api_key`) |
| **Statut** | FAIT |

### 8. Logs d'audit fiabilises

| | |
|---|---|
| **Le probleme** | Les logs de securite (qui a fait quoi, quand) etaient silencieusement perdus si la base de donnees etait temporairement indisponible. On ne savait jamais qu'on avait perdu des logs. |
| **Ce qu'on a fait** | Quand Supabase est indisponible, les logs sont maintenant ecrits dans un fichier local (`.tmp/audit_logs/audit_YYYYMMDD.jsonl`). Un message d'avertissement est affiche. En dernier recours, les logs sont ecrits sur la sortie d'erreur pour ne jamais les perdre silencieusement. |
| **Fichier modifie** | `execution/database/agent_database.py` |
| **Statut** | FAIT |

### 9. Regles d'acces en base de donnees corrigees (RLS)

| | |
|---|---|
| **Le probleme** | Certaines regles d'acces Supabase etaient trop permissives. Par exemple : n'importe qui pouvait inserer ou lire TOUS les documents clients. La table des notaires etait entierement lisible par n'importe qui. Des policies doublons se contredisaient. |
| **Ce qu'on a fait** | On a corrige 3 tables : (1) `documents_client` : l'insertion et la lecture anonyme ne sont autorisees que pour les documents lies a un questionnaire valide et non expire. (2) `form_submissions` : les 3 policies doublons trop larges ont ete supprimees, les 2 policies strictes restent. (3) `notaire_users` : l'acces anonyme est restreint aux notaires actifs, et les mises a jour ne sont possibles que pour le notaire connecte. |
| **Migration SQL** | `fix_overly_permissive_rls_policies` appliquee |
| **Statut** | FAIT |

### 10. Mode developpement bloque en production

| | |
|---|---|
| **Le probleme** | Un "mode dev" (`NOTOMAI_DEV_MODE=1`) desactive l'authentification pour faciliter les tests. Si ce mode etait active par erreur en production, n'importe qui pouvait acceder a tout sans mot de passe. |
| **Ce qu'on a fait** | Le mode dev est maintenant bloque sur les serveurs Modal (production). Il ne peut s'activer que en local (quand la variable `MODAL_ENVIRONMENT` n'est pas definie). Un message d'avertissement est affiche quand le mode dev est actif. |
| **Fichier modifie** | `api/main.py` |
| **Statut** | FAIT |

---

## Ce qui a ete fait (Phase 3 - Conformite RGPD avancee) - EN COURS

### 14. Suppression securisee des fichiers temporaires

| | |
|---|---|
| **Le probleme** | Quand le systeme supprimait un fichier temporaire (acte genere, donnees client en JSON, cache), il utilisait `unlink()` qui se contente de marquer l'espace comme libre. Les donnees restaient physiquement sur le disque et pouvaient etre recuperees avec un logiciel specialise. |
| **Ce qu'on a fait** | On a cree un module `secure_delete.py` qui ecrase le contenu de chaque fichier avec des donnees aleatoires puis des zeros AVANT de le supprimer. Impossible de recuperer le texte original. Ce module est maintenant utilise partout ou des fichiers temporaires sont supprimes : orchestrateur, extraction de titres, export PDF, cache cadastre. |
| **Fichiers modifies** | `execution/security/secure_delete.py` (cree), `execution/gestionnaires/orchestrateur.py`, `execution/extraire_titre_api.py`, `execution/core/exporter_pdf.py`, `execution/services/cadastre_service.py` |
| **Statut** | FAIT |

### A faire (Phase 3 - restant)

| # | Quoi | Pourquoi |
|---|------|----------|
| 11 | Ecran de consentement | Le client doit accepter la collecte de ses donnees (obligation RGPD) |
| 12 | Double authentification (2FA) | Un code en plus du mot de passe pour securiser l'acces |
| 13 | Chiffrer les documents generes (DOCX/PDF) | Les actes generes sont en clair sur le disque |
| 15 | Documenter les garanties contractuelles Anthropic | S'assurer que les clauses avec Anthropic couvrent le transfert UE→USA |

## Ce qui restera apres (Phase 4 - Durcissement long terme)

| # | Quoi | Pourquoi |
|---|------|----------|
| 16 | Migrer la cle de chiffrement vers un coffre-fort | Actuellement dans un fichier `.env`, devrait etre dans un secret manager |
| 17 | Test d'intrusion externe | Faire tester la securite par un professionnel independant |
| 18 | Tests automatises des regles d'acces | Verifier automatiquement que le RLS fonctionne a chaque mise a jour |
| 19 | Headers de securite web (CSP/HSTS) | Proteger le frontend contre certaines attaques web |
| 20 | Stocker les conversations chiffrees | Les discussions avec le chatbot sont en clair en base |

---

## Tableau de bord global

| Phase | Description | Avancement |
|-------|-------------|------------|
| **Phase 1** | Corrections critiques (bloquantes) | **5/5 termines** |
| **Phase 2** | Renforcement securite | **5/5 termines** |
| **Phase 3** | Conformite RGPD avancee | **1/5 termine** - en pause |
| **Phase 4** | Durcissement long terme | 0/5 - a venir |

---

*Ce fichier est mis a jour au fur et a mesure de l'avancement des corrections.*
