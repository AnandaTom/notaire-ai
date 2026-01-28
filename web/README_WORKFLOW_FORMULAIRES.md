# Workflow Formulaires Clients - NotaireAI

Ce document explique le système de collecte sécurisée des données clients via formulaires web.

---

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           WORKFLOW COMPLET                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

    NOTAIRE                         CLIENT                          SUPABASE
       │                               │                               │
       │  1. Crée formulaire           │                               │
       │──────────────────────────────────────────────────────────────▶│
       │   (etude_id, notaire_id,      │                               │
       │    type_partie, token)        │                               │
       │                               │                               │
       │  2. Envoie lien au client     │                               │
       │─────────────────────────────▶ │                               │
       │   URL + clé chiffrement       │                               │
       │                               │                               │
       │                               │  3. Remplit formulaire        │
       │                               │──────────────────────────────▶│
       │                               │   (données chiffrées)         │
       │                               │                               │
       │  4. Voit "Soumis"             │                               │
       │◀──────────────────────────────────────────────────────────────│
       │                               │                               │
       │  5. Déchiffre + importe       │                               │
       │──────────────────────────────────────────────────────────────▶│
       │   vers fiche client           │                               │
       │                               │                               │
       ▼                               ▼                               ▼
```

---

## Comment ça marche ?

### Étape 1 : Le notaire crée un formulaire

Le notaire se connecte au **Dashboard** (`dashboard-notaire.html`) avec sa clé API.

Il clique sur **"+ Nouveau formulaire"** et renseigne :
- Nom et prénom du client
- Type de partie (acquéreur, vendeur, etc.)
- Dossier associé (optionnel)
- Libellé/référence

**Ce qui se passe en coulisses :**
1. Un **token unique** (64 caractères) est généré
2. Une **clé de chiffrement AES-256** est créée
3. Un enregistrement est créé dans `form_submissions` avec :
   - `etude_id` → l'étude du notaire
   - `notaire_id` → le notaire qui crée le formulaire
   - `token` → identifiant unique du formulaire
   - `status: pending` → en attente de réponse

**Le lien généré :**
```
https://example.com/fill.html?token=abc123...#key=clé_base64...
```

| Partie | Rôle | Sécurité |
|--------|------|----------|
| `?token=abc123` | Identifie le formulaire dans Supabase | Transmis au serveur |
| `#key=...` | Clé de chiffrement | **JAMAIS transmis au serveur** (fragment URL) |

---

### Étape 2 : Le client remplit le formulaire

Le client reçoit le lien par email/SMS et l'ouvre dans son navigateur.

**Vérifications automatiques :**
- Token valide ?
- Formulaire pas déjà soumis ?
- Lien pas expiré (7 jours) ?

**Le formulaire collecte :**
- Identité complète (nom, prénoms, date/lieu naissance)
- Adresse actuelle
- Situation matrimoniale (+ conjoint si applicable)
- Pièce d'identité (numéro CNI, dates)
- Coordonnées bancaires (IBAN, BIC)
- Contact (téléphone, email)
- Consentement RGPD

---

### Étape 3 : Chiffrement et envoi

Quand le client clique "Envoyer" :

1. **Les données sont structurées** en JSON :
```json
{
  "acquereur": {
    "personne_physique": { "nom": "DUPONT", "prenoms": ["Jean", "Pierre"], ... },
    "adresse": { "adresse": "12 rue...", "code_postal": "75001", ... },
    "situation_matrimoniale": { "regime": "marie", "conjoint": {...} },
    "pieces_identite": { "cni": {...} },
    "coordonnees_bancaires": { "iban": "FR76...", ... },
    "contact": { "telephone": "06...", "email": "..." }
  },
  "metadata": { "submitted_at": "...", "rgpd_consent": true }
}
```

2. **Chiffrement côté client** (dans le navigateur) :
   - Algorithme : **AES-256-GCM**
   - Clé : celle du fragment URL (jamais envoyée au serveur)
   - IV : généré aléatoirement (96 bits)

3. **Envoi à Supabase** :
   - `data_encrypted` : données chiffrées (base64)
   - `encryption_iv` : IV pour déchiffrement
   - `status: submitted`

**Résultat :** Les données sont stockées mais **illisibles** sans la clé.

---

### Étape 4 : Le notaire consulte et importe

Le notaire voit dans son dashboard que le formulaire est "Soumis".

**Pour voir les données :**
1. Cliquer sur "Voir"
2. Coller la clé de déchiffrement (depuis le lien original)
3. Les données sont déchiffrées **localement** dans le navigateur

**Pour importer vers la fiche client :**
1. Cliquer "Importer vers fiche client"
2. La fonction `enrich_client_from_submission()` est appelée
3. Les données enrichissent/créent la fiche dans la table `clients`

---

## Architecture technique

### Tables Supabase

```
┌─────────────────────────────────────────────────────────────────┐
│                        form_submissions                          │
├─────────────────────────────────────────────────────────────────┤
│ id                  │ UUID (PK)                                 │
│ token               │ VARCHAR(64) - identifiant unique          │
│ etude_id            │ UUID (FK → etudes) - l'étude notariale    │
│ notaire_id          │ UUID (FK → auth.users) - notaire créateur │
│ dossier_id          │ UUID (FK → dossiers) - dossier lié        │
│ client_id           │ UUID (FK → clients) - fiche à enrichir    │
│ type_partie         │ TEXT - vendeur/acquereur/etc.             │
│ data_encrypted      │ TEXT - données chiffrées (base64)         │
│ encryption_iv       │ TEXT - IV pour déchiffrement              │
│ status              │ TEXT - pending/submitted/processed        │
│ client_nom          │ TEXT - nom (non chiffré, pour affichage)  │
│ client_prenom       │ TEXT - prénom (non chiffré)               │
│ expires_at          │ TIMESTAMP - expiration (7 jours)          │
│ submitted_at        │ TIMESTAMP - date soumission               │
│ processed_at        │ TIMESTAMP - date import                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           clients                                │
├─────────────────────────────────────────────────────────────────┤
│ id                  │ UUID (PK)                                 │
│ etude_id            │ UUID (FK → etudes)                        │
│ created_by          │ UUID (FK → auth.users) - notaire          │
│ nom_encrypted       │ TEXT - nom chiffré                        │
│ prenom_encrypted    │ TEXT - prénom chiffré                     │
│ email_encrypted     │ TEXT - email chiffré                      │
│ telephone_encrypted │ TEXT - téléphone chiffré                  │
│ adresse_encrypted   │ TEXT - adresse chiffrée                   │
│ civilite            │ TEXT                                      │
│ date_naissance      │ DATE                                      │
│ lieu_naissance      │ TEXT                                      │
│ nationalite         │ TEXT                                      │
│ profession          │ TEXT                                      │
│ situation_matrimoniale │ TEXT                                   │
│ ai_enrichments      │ JSONB - données enrichies (CNI, IBAN...)  │
│ source              │ TEXT - origine (conversation, genapi...)  │
└─────────────────────────────────────────────────────────────────┘
```

### Fichiers du système

```
web/
├── dashboard-notaire.html    # Interface notaire (création liens, suivi)
├── fill.html                 # Formulaire acquéreur
├── formulaire_vendeur.html   # Formulaire vendeur
├── crypto.js                 # Module chiffrement AES-256-GCM
├── supabase-client.js        # Client API Supabase
├── fill-script.js            # Logique formulaire client
├── styles.css                # Styles communs
└── questionnaires/
    ├── vente-appartement.html  # Questionnaire vente appart
    ├── vente-maison.html       # Questionnaire vente maison
    └── achat-bien.html         # Questionnaire achat
```

---

## Sécurité

### Chiffrement bout-en-bout (E2E)

```
                    NAVIGATEUR CLIENT                    SERVEUR SUPABASE
                          │                                    │
   Données en clair ──────┤                                    │
          │               │                                    │
          ▼               │                                    │
   ┌──────────────┐       │                                    │
   │ Chiffrement  │       │                                    │
   │ AES-256-GCM  │       │                                    │
   │ (clé locale) │       │                                    │
   └──────────────┘       │                                    │
          │               │                                    │
          ▼               │                                    │
   Données chiffrées ─────┼───────────────────────────────────▶│ Stockage
                          │                                    │ (illisible)
                          │                                    │
```

**Pourquoi c'est sécurisé :**

| Menace | Protection |
|--------|------------|
| Interception réseau | Données déjà chiffrées avant envoi |
| Fuite base de données | Données illisibles sans clé |
| Accès admin Supabase | Données illisibles sans clé |
| Vol du lien | Clé dans fragment URL (pas loggé par serveurs) |

### La clé ne quitte jamais le client

Le **fragment URL** (`#key=...`) n'est **jamais** envoyé au serveur :
- Les serveurs web ignorent tout ce qui suit `#`
- La clé reste uniquement côté client
- Seul celui qui possède le lien complet peut déchiffrer

---

## Multi-tenant : Plusieurs études / notaires

### Structure hiérarchique

```
Étude A (etude_id = aaa)
├── Notaire 1 (notaire_id = n1)
│   ├── Formulaire client Dupont
│   └── Formulaire client Martin
└── Notaire 2 (notaire_id = n2)
    └── Formulaire client Bernard

Étude B (etude_id = bbb)
└── Notaire 3 (notaire_id = n3)
    └── Formulaire client Thomas
```

### Isolation des données

Chaque formulaire est automatiquement associé à :
1. **L'étude** (`etude_id`) → pour le RLS (Row Level Security)
2. **Le notaire** (`notaire_id`) → pour filtrer par collaborateur
3. **Le dossier** (`dossier_id`) → pour lier à une affaire

**Le notaire ne voit que ses propres formulaires** grâce aux politiques RLS Supabase.

---

## Guide d'utilisation

### Pour le notaire

1. **Se connecter** au dashboard avec sa clé API (`nai_xxxx...`)
2. **Créer un formulaire** en cliquant "+ Nouveau formulaire"
3. **Envoyer le lien** au client par email ou SMS
4. **Conserver la clé** (dans le lien après `#key=`) pour déchiffrer plus tard
5. **Attendre** que le client remplisse
6. **Consulter** les données et les importer vers la fiche client

### Pour le client

1. **Ouvrir le lien** reçu du notaire
2. **Remplir** tous les champs obligatoires
3. **Vérifier** les informations
4. **Envoyer** → confirmation de succès

---

## API disponibles

### Créer un formulaire (côté notaire)

```javascript
await SupabaseClient.createSubmission({
    etudeId: 'uuid-etude',
    notaireId: 'uuid-notaire',
    dossierId: 'uuid-dossier',  // optionnel
    clientId: 'uuid-client',     // optionnel
    typePartie: 'acquereur',
    label: 'Achat appartement rue Victor Hugo',
    token: 'abc123...'
});
```

### Lister les formulaires

```javascript
// Par étude
const submissions = await SupabaseClient.listSubmissions(etudeId);

// Par notaire
const mySubmissions = await SupabaseClient.listSubmissionsByNotaire(notaireId);
```

### Enrichir une fiche client

```javascript
// Après déchiffrement des données
const result = await SupabaseClient.enrichClientFromSubmission(
    submissionId,
    decryptedData
);
// result = { success: true, action: 'created', client_id: 'uuid' }
```

---

## Troubleshooting

### "Lien invalide ou expiré"

**Causes possibles :**
- Le token n'existe pas dans `form_submissions`
- Le formulaire a déjà été soumis (`status = 'submitted'`)
- Le lien a expiré (plus de 7 jours)

**Solution :** Le notaire doit créer un nouveau formulaire.

### "Clé de sécurité manquante"

**Cause :** Le lien a été tronqué, le fragment `#key=...` est absent.

**Solution :** Utiliser le lien complet, avec la partie après `#`.

### "Impossible de déchiffrer"

**Cause :** Mauvaise clé de déchiffrement.

**Solution :** Vérifier que la clé correspond exactement au lien envoyé au client.

---

## Évolutions futures

- [ ] Notification email automatique au notaire quand formulaire soumis
- [ ] Relance automatique si formulaire non rempli après X jours
- [ ] Pré-remplissage si fiche client existante
- [ ] Signature électronique intégrée
- [ ] Export PDF des données collectées
