# Taches Augustin - Formulaires, Dashboard & Commercial

> Document genere le 29/01/2026 - A charger dans Claude Code pour continuer le travail

---

## Contexte projet

Tu travailles sur **Notomai**, un systeme de generation d'actes notariaux (promesses de vente, actes de vente). L'architecture est en 3 couches :

```
FRONTEND (toi)              BACKEND (Paul)              MOTEUR (Tom)
web/dashboard-notaire.html  api/main.py                 execution/core/assembler_acte.py
web/fill.html               modal/modal_app.py          execution/core/exporter_docx.py
web/questionnaires/*.html   execution/chat_handler.py   templates/*.md
web/crypto.js                                           schemas/*.json
web/supabase-client.js
```

**Ton role :** Tu geres les formulaires web qui collectent les donnees clients, le dashboard notaire, et la partie commerciale. Tu ne touches PAS au backend Python ni aux templates Jinja2.

**Le probleme central :** Tes formulaires collectent des donnees chiffrees dans Supabase, mais **ces donnees ne declenchent jamais la generation d'un acte**. Il y a un trou entre "le client remplit le formulaire" et "le notaire recoit son DOCX".

---

## Architecture actuelle de tes fichiers

```
web/
├── dashboard-notaire.html       # Dashboard principal notaire (779 lignes)
├── fill.html                    # Formulaire acquereur generique (395 lignes)
├── crypto.js                    # Chiffrement E2E AES-256-GCM (143 lignes)
├── supabase-client.js           # Client Supabase REST (193 lignes)
├── fill-script.js               # Logique fill.html (278 lignes)
├── questionnaires/
│   ├── vente-appartement.html   # Vendeur appartement, 7 etapes (1270 lignes)
│   ├── vente-maison.html        # Vendeur maison, 8 etapes (1477 lignes)
│   ├── achat-bien.html          # Acquereur complet, 6 etapes (994 lignes)
│   └── questionnaire-common.js  # Logique partagee
```

### Ce qui fonctionne

| Composant | Statut | Detail |
|-----------|--------|--------|
| Dashboard login | OK | API key via Supabase `agent_api_keys` |
| Creation de lien securise | OK | Token 64-hex + cle AES-256 dans le fragment URL |
| Chiffrement E2E | OK | `crypto.js` : AES-256-GCM, cle jamais envoyee au serveur |
| Formulaire vendeur appart | OK | 7 etapes, 350+ champs, progressif |
| Formulaire vendeur maison | OK | 8 etapes, sections terrain/batiment specifiques |
| Formulaire acquereur complet | OK | 6 etapes, financement, projets |
| Formulaire acquereur simple | OK | `fill.html` — identite + coordonnees (minimal) |
| Stockage Supabase | OK | `form_submissions` avec donnees chiffrees |
| Decryptage dans le dashboard | OK | Le notaire colle la cle, voit les donnees |

### Ce qui NE fonctionne PAS

| Probleme | Impact | Fichier |
|----------|--------|---------|
| Pas de bouton "Generer l'acte" | Le notaire voit les donnees mais ne peut rien en faire | `dashboard-notaire.html` |
| Formulaires non relies a l'API de generation | Les donnees restent dans Supabase sans etre utilisees | tous les formulaires |
| Pas de mapping formulaire → schema pipeline | Les noms de champs du formulaire ≠ noms attendus par le moteur | manquant |
| Pas de gestion de dossier multi-formulaires | Un dossier = 1 vendeur + 1 acquereur, mais rien ne les relie | `dashboard-notaire.html` |
| Pas de validation pre-generation | Aucun check de completude avant de lancer la generation | manquant |

---

## Supabase — Tables que tu utilises

### `agent_api_keys` (authentification notaire)

```
id, etude_id, name, key_prefix, key_hash, permissions (JSONB),
rate_limit_rpm, expires_at, revoked_at, total_requests
```

Tu queries cette table dans `dashboard-notaire.html` ligne 464 :
```javascript
GET /rest/v1/agent_api_keys?key_prefix=eq.${apiKey.substring(0,12)}&select=*,etudes(*)
```

### `form_submissions` (donnees formulaires)

```
id (UUID), token (VARCHAR 64), etude_id, notaire_id, dossier_id,
client_id, type_partie (vendeur/acquereur/...),
label, status (pending/submitted/processed),
data_encrypted (TEXT base64), encryption_iv (TEXT base64),
client_nom, client_prenom,
created_at, expires_at (7 jours), submitted_at, processed_at
```

Tu crees des submissions dans `dashboard-notaire.html` ligne 609 :
```javascript
SupabaseClient.createSubmission({
  etudeId, notaireId, dossierId, clientId, typePartie, label, token
})
```

Tu lis les submissions dans `dashboard-notaire.html` ligne 520 :
```javascript
SupabaseClient.listSubmissions(currentUser.etudeId)
```

### `etudes` (info cabinet notaire)

```
id, nom, siret, adresse, email_contact, telephone, owner_user_id
```

### `clients` (profils clients enrichis)

```
id, etude_id, nom_encrypted, prenom_encrypted, email_encrypted,
telephone_encrypted, adresse_encrypted, nom_hash (SHA-256 pour recherche),
type_personne, civilite, date_naissance, lieu_naissance,
nationalite, profession, situation_matrimoniale
```

### `dossiers` (dossiers/actes)

```
id, etude_id, numero (auto), type_acte, statut (brouillon/en_cours/termine/archive),
parties (JSONB: [{client_id, role, quotite}]),
biens (JSONB: [{adresse, cadastre, surface, lots}]),
donnees_metier (JSONB: {prix_total, prets, conditions, fichier_genere}),
created_at, updated_at, deleted_at
```

---

## Flux de donnees actuel (et ou ca casse)

```
1. NOTAIRE cree un lien
   dashboard-notaire.html → openNewFormModal()
   → createSubmission() → token + cle AES
   → URL: https://...?token=abc#key=xyz
                                                        ✅ OK
2. CLIENT remplit le formulaire
   fill.html / questionnaires/*.html
   → Chiffre avec AES-256-GCM dans le navigateur
   → PATCH form_submissions (data_encrypted + iv)
                                                        ✅ OK
3. NOTAIRE voit la soumission
   dashboard-notaire.html → renderSubmissions()
   → viewSubmission() → decryptSubmission()
   → Affiche JSON decrypte
                                                        ✅ OK
4. NOTAIRE veut generer l'acte
   → ??? PAS DE BOUTON ???
   → ??? PAS DE CONNEXION A L'API ???
                                                        ❌ CASSE ICI
```

---

## Tes taches — par priorite

### Vue d'ensemble

```
Semaine 1:  "Le notaire peut generer depuis le dashboard"
  T1  Bouton "Generer" dans le dashboard
  T2  Mapping formulaire → schema pipeline
  T3  Appel API /promesses/generer depuis le dashboard

Semaine 2:  "L'experience est fluide"
  T4  Gestion dossier multi-formulaires (vendeur + acquereur)
  T5  Validation pre-generation (completude, coherence)
  T6  Telechargement DOCX dans le dashboard

Semaine 3:  "Demo commerciale"
  T7  Parcours de demo end-to-end
  T8  Page d'accueil / landing commerciale
  T9  Onboarding premier notaire
```

---

## T1 : Bouton "Generer l'acte" dans le dashboard

### Le probleme

`dashboard-notaire.html` affiche les soumissions avec un bouton "Voir" (ligne 546) et un bouton "Importer vers fiche client" (ligne 429). Mais aucun bouton ne declenche la generation d'un acte.

### Ou ajouter le bouton

Dans la fonction `renderSubmissions()` (ligne 529), chaque soumission affiche des actions. Ajouter un bouton apres le bouton "Voir" existant.

### Ce que le bouton doit faire

1. Decrypter les donnees de la soumission (la cle doit deja etre en memoire apres un premier "Voir")
2. Transformer les donnees du format formulaire → format attendu par l'API (voir T2)
3. Appeler `POST /promesses/generer` (ou `POST /agent/execute`) avec les donnees
4. Afficher un indicateur de chargement
5. Quand la reponse arrive, afficher un lien de telechargement

### Schema de l'appel API

L'API backend (geree par Paul) expose `POST /promesses/generer` dans `api/main.py` ligne 1134.

**Requete attendue :**
```javascript
const response = await fetch(`${API_BASE_URL}/promesses/generer`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': localStorage.getItem('notaire_api_key')
  },
  body: JSON.stringify({
    donnees: donneesTransformees,  // Donnees au format schema pipeline
    type_promesse: "auto",         // Detection automatique du type
    options: {
      format_sortie: "docx",
      zones_grises: true           // Variables en gris dans le DOCX
    }
  })
});
```

**Reponse attendue :**
```json
{
  "statut": "succes",
  "message": "Promesse generee avec succes",
  "fichier": "promesse_vente_20260129_143022.docx",
  "fichier_url": "/files/promesse_vente_20260129_143022.docx",
  "type_detecte": "standard",
  "confiance": 0.92,
  "avertissements": ["Diagnostics non fournis", "Surface Carrez manquante"]
}
```

### URL de base de l'API

```
Production : https://notaire-ai--fastapi-app.modal.run
Dev local  : http://localhost:8000  (si NOTOMAI_DEV_MODE=1)
```

Paul est en train de mettre en place l'endpoint `GET /files/{filename}` pour le telechargement. En attendant, le bouton peut afficher le nom du fichier et le statut de generation.

### Critere de validation

Le notaire clique sur "Generer", voit un loader, puis recoit le nom du fichier genere avec un lien de telechargement.

---

## T2 : Mapping formulaire → schema pipeline

### Le probleme

Les noms de champs dans tes formulaires ne correspondent pas aux noms attendus par le moteur de generation. Le moteur attend un JSON au format `schemas/variables_promesse_vente.json` ou `schemas/variables_vente.json`.

### Exemples de divergence

| Champ formulaire (HTML name) | Chemin attendu par le moteur | Fichier source |
|------------------------------|------------------------------|----------------|
| `vendeur1_nom` | `vendeurs[0].personne_physique.nom` | `vente-appartement.html` |
| `vendeur1_prenoms` | `vendeurs[0].personne_physique.prenoms` | |
| `vendeur1_date_naissance` | `vendeurs[0].personne_physique.date_naissance` | |
| `vendeur1_situation` | `vendeurs[0].situation_matrimoniale.regime` | |
| `tel_portable` | `vendeurs[0].contact.telephone` | |
| `iban` | `vendeurs[0].coordonnees_bancaires.iban` | |
| `copro_syndic` | `copropriete.syndic.nom` | |
| `copro_charges_annuelles` | `copropriete.charges_annuelles` | |
| `pret_montant` | `financement.prets[0].montant` | `achat-bien.html` |
| `apport_personnel` | `financement.apport_personnel` | |
| `quote_part_acq1` | `acquereurs[0].quotite_acquise.fraction` | |

### Ce que tu dois creer

Un fichier JavaScript `web/mapping-formulaire.js` qui transforme la sortie du formulaire en JSON compatible avec le pipeline :

```javascript
/**
 * Transforme les donnees brutes d'un formulaire en format pipeline.
 * @param {Object} formData - Donnees decryptees du formulaire
 * @param {string} typePartie - 'vendeur_appartement', 'vendeur_maison', 'acquereur'
 * @returns {Object} Donnees au format schemas/variables_promesse_vente.json
 */
function mapFormToPipeline(formData, typePartie) {
  // Mapping vendeur
  if (typePartie.startsWith('vendeur')) {
    return {
      vendeurs: [{
        personne_physique: {
          civilite: formData.vendeur1_civilite,
          nom: formData.vendeur1_nom,
          prenoms: formData.vendeur1_prenoms,
          date_naissance: formData.vendeur1_date_naissance,
          lieu_naissance: formData.vendeur1_lieu_naissance,
          nationalite: formData.vendeur1_nationalite || 'francaise',
          profession: formData.vendeur1_profession
        },
        adresse: {
          adresse: formData.vendeur1_adresse,
          code_postal: formData.vendeur1_code_postal,
          ville: formData.vendeur1_ville
        },
        situation_matrimoniale: {
          regime: formData.vendeur1_situation,
          date_mariage: formData.vendeur1_date_mariage,
          lieu_mariage: formData.vendeur1_lieu_mariage,
          regime_matrimonial: formData.vendeur1_regime_matrimonial
        },
        contact: {
          telephone: formData.tel_portable || formData.tel_domicile,
          email: formData.email
        },
        coordonnees_bancaires: {
          iban: formData.iban,
          bic: formData.bic,
          nom_banque: formData.banque
        }
      }],
      // Ajouter vendeur2 si present
      // ...sections specifiques appart/maison...
    };
  }

  // Mapping acquereur
  if (typePartie === 'acquereur') {
    return {
      acquereurs: [{
        personne_physique: {
          civilite: formData.acquereur_civilite,
          nom: formData.acquereur_nom,
          prenoms: formData.acquereur_prenoms,
          // ...
        },
        // ...
      }],
      financement: {
        apport_personnel: formData.apport_personnel,
        prets: formData.prets || [],
        // ...
      }
    };
  }
}
```

### Schemas de reference

Pour connaitre la structure exacte attendue par le moteur, consulte :

| Schema | Chemin | Usage |
|--------|--------|-------|
| Variables vente | `schemas/variables_vente.json` | Structure complete acte de vente |
| Variables promesse | `schemas/variables_promesse_vente.json` | Structure complete promesse |
| Questions vente | `schemas/questions_notaire.json` | 100+ questions avec `variable_cible` |
| Questions promesse | `schemas/questions_promesse_vente.json` | 100+ questions, 21 sections |

**Astuce :** Le fichier `schemas/questions_notaire.json` contient un champ `variable_cible` pour chaque question. C'est le chemin exact dans le JSON attendu. Utilise-le comme reference pour ton mapping.

### Critere de validation

`mapFormToPipeline(donneesDecryptees, 'vendeur_appartement')` retourne un JSON que le moteur accepte sans erreur de variable manquante.

---

## T3 : Appel API depuis le dashboard

### Integration complete

Combine T1 (bouton) + T2 (mapping) pour faire l'appel complet :

```javascript
async function generateDocument(submissionId) {
  const statusEl = document.getElementById(`status-${submissionId}`);
  statusEl.textContent = 'Generation en cours...';
  statusEl.className = 'badge badge-warning';

  try {
    // 1. Recuperer et decrypter les donnees
    const submission = submissions.find(s => s.id === submissionId);
    const decryptedData = await decryptSubmission(submissionId);

    // 2. Mapper vers le format pipeline
    const pipelineData = mapFormToPipeline(
      JSON.parse(decryptedData),
      submission.type_partie
    );

    // 3. Appeler l'API de generation
    const apiUrl = 'https://notaire-ai--fastapi-app.modal.run';
    const response = await fetch(`${apiUrl}/promesses/generer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': localStorage.getItem('notaire_api_key')
      },
      body: JSON.stringify({
        donnees: pipelineData,
        type_promesse: 'auto',
        options: { format_sortie: 'docx', zones_grises: true }
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erreur de generation');
    }

    const result = await response.json();

    // 4. Afficher le resultat
    statusEl.textContent = 'Genere !';
    statusEl.className = 'badge badge-success';

    // 5. Afficher le lien de telechargement
    const downloadBtn = document.createElement('a');
    downloadBtn.href = `${apiUrl}${result.fichier_url}`;
    downloadBtn.textContent = 'Telecharger DOCX';
    downloadBtn.className = 'btn btn-sm btn-primary';
    downloadBtn.download = result.fichier;
    statusEl.parentElement.appendChild(downloadBtn);

    // 6. Afficher les avertissements
    if (result.avertissements && result.avertissements.length > 0) {
      const warnings = document.createElement('div');
      warnings.className = 'alert alert-warning mt-2';
      warnings.innerHTML = '<strong>Attention :</strong><ul>' +
        result.avertissements.map(w => `<li>${w}</li>`).join('') +
        '</ul>';
      statusEl.parentElement.appendChild(warnings);
    }

  } catch (error) {
    statusEl.textContent = `Erreur: ${error.message}`;
    statusEl.className = 'badge badge-danger';
  }
}
```

### Gestion de la cle de decryptage

Actuellement, le notaire doit coller la cle manuellement a chaque fois qu'il veut voir les donnees. Pour la generation, il faut que la cle soit disponible.

**Solutions possibles (par ordre de simplicite) :**

1. **Stocker la cle en sessionStorage** apres le premier decryptage — La cle disparait quand le notaire ferme l'onglet. Compromis securite/UX acceptable.
2. **Demander la cle a chaque generation** — Plus securise mais plus lourd.
3. **Stocker la cle chiffree cote serveur** avec un mot de passe maitre — Plus complexe, pour plus tard.

La solution 1 est recommandee pour le MVP. Modifier `decryptSubmission()` pour stocker :
```javascript
// Dans decryptSubmission(), apres decryptage reussi :
sessionStorage.setItem(`key_${submissionId}`, keyBase64);
```

Et dans `generateDocument()`, recuperer :
```javascript
const keyBase64 = sessionStorage.getItem(`key_${submissionId}`);
if (!keyBase64) {
  // Demander la cle au notaire
  keyBase64 = prompt('Collez la cle de decryptage :');
}
```

### Critere de validation

Le notaire clique "Generer" sur une soumission deja decryptee → l'API est appelee → le DOCX est telecharge (ou un message d'erreur clair est affiche).

---

## T4 : Gestion dossier multi-formulaires

### Le probleme

Un acte de vente implique au minimum un vendeur ET un acquereur. Aujourd'hui, chaque formulaire est une soumission independante. Rien ne relie le formulaire vendeur et le formulaire acquereur du meme dossier.

### Le champ `dossierId` existe deja

Dans `dashboard-notaire.html` ligne 368, le modal de creation de formulaire a un champ `dossierId` (optionnel). Mais :
- Il n'y a pas d'UI pour creer un dossier
- Il n'y a pas de vue "dossier" qui montre toutes les soumissions liees
- La generation ne combine pas vendeur + acquereur

### Ce que tu dois faire

1. **Ajouter un bouton "Nouveau dossier"** dans le dashboard qui cree un dossier via l'API :
   ```javascript
   // POST /dossiers (existe deja dans api/main.py ligne 644)
   const response = await fetch(`${apiUrl}/dossiers`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-API-Key': apiKey
     },
     body: JSON.stringify({
       type_acte: 'promesse_vente',  // ou 'vente'
       parties: [],
       biens: [],
       donnees_metier: {}
     })
   });
   const dossier = await response.json();
   // dossier.id et dossier.numero sont generes automatiquement
   ```

2. **Populer le dropdown `dossierId`** avec les dossiers existants :
   ```javascript
   // GET /dossiers (existe deja, api/main.py ligne 546)
   const response = await fetch(`${apiUrl}/dossiers`, {
     headers: { 'X-API-Key': apiKey }
   });
   const dossiers = await response.json();
   // Remplir le <select id="dossierId"> avec dossiers
   ```

3. **Ajouter une vue "Dossier"** qui montre :
   - Numero du dossier + type d'acte
   - Liste des soumissions liees (vendeur, acquereur)
   - Statut de completude (vendeur OK, acquereur manquant)
   - Bouton "Generer" (actif seulement quand toutes les parties sont presentes)

4. **A la generation**, combiner les donnees vendeur + acquereur :
   ```javascript
   function combinerDonneesDossier(submissionsDecryptees) {
     const vendeurData = submissionsDecryptees.find(s => s.type_partie.startsWith('vendeur'));
     const acquereurData = submissionsDecryptees.find(s => s.type_partie === 'acquereur');

     const vendeurMapped = mapFormToPipeline(vendeurData.data, vendeurData.type_partie);
     const acquereurMapped = mapFormToPipeline(acquereurData.data, 'acquereur');

     // Fusionner
     return {
       ...vendeurMapped,
       ...acquereurMapped,
       // Les vendeurs et acquereurs sont dans des cles separees, pas de conflit
     };
   }
   ```

### Critere de validation

Le notaire cree un dossier, envoie un formulaire vendeur et un formulaire acquereur lies au meme dossier, puis genere l'acte en un clic avec les donnees des deux parties.

---

## T5 : Validation pre-generation

### Le probleme

Avant de lancer la generation, il faut verifier que les donnees sont completes et coherentes. Le moteur va planter si des champs obligatoires manquent.

### Ce qu'il faut verifier

Le backend expose deja `POST /promesses/valider` (api/main.py ligne 1216) qui fait des verifications. Mais cote frontend, il est utile d'avoir une pre-validation rapide.

### Champs obligatoires minimum

Pour une promesse de vente :

| Categorie | Champs requis |
|-----------|---------------|
| Vendeur | nom, prenoms, date_naissance, adresse |
| Acquereur | nom, prenoms, date_naissance, adresse |
| Bien | adresse complete, au moins 1 lot (si copro) |
| Prix | montant > 0 |
| Financement | au moins un mode (pret ou fonds propres) |

### Logique de validation frontend

```javascript
function validerAvantGeneration(donneesPipeline) {
  const erreurs = [];
  const avertissements = [];

  // Vendeur(s)
  if (!donneesPipeline.vendeurs || donneesPipeline.vendeurs.length === 0) {
    erreurs.push('Aucun vendeur renseigne');
  } else {
    donneesPipeline.vendeurs.forEach((v, i) => {
      if (!v.personne_physique?.nom) erreurs.push(`Vendeur ${i+1} : nom manquant`);
      if (!v.personne_physique?.prenoms) erreurs.push(`Vendeur ${i+1} : prenoms manquants`);
      if (!v.personne_physique?.date_naissance) avertissements.push(`Vendeur ${i+1} : date de naissance manquante`);
    });
  }

  // Acquereur(s)
  if (!donneesPipeline.acquereurs || donneesPipeline.acquereurs.length === 0) {
    erreurs.push('Aucun acquereur renseigne');
  }

  // Bien
  if (!donneesPipeline.bien?.adresse?.adresse) {
    erreurs.push('Adresse du bien manquante');
  }

  // Prix
  if (!donneesPipeline.prix?.montant || donneesPipeline.prix.montant <= 0) {
    erreurs.push('Prix de vente manquant ou invalide');
  }

  return {
    valide: erreurs.length === 0,
    erreurs,
    avertissements,
    completude: calculerCompletude(donneesPipeline)
  };
}

function calculerCompletude(donnees) {
  const champsAttendus = [
    'vendeurs[0].personne_physique.nom',
    'vendeurs[0].personne_physique.prenoms',
    'vendeurs[0].personne_physique.date_naissance',
    'vendeurs[0].adresse.adresse',
    'acquereurs[0].personne_physique.nom',
    'acquereurs[0].personne_physique.prenoms',
    'bien.adresse.adresse',
    'bien.adresse.code_postal',
    'bien.adresse.ville',
    'prix.montant',
    'financement.type',
  ];

  let remplis = 0;
  champsAttendus.forEach(chemin => {
    const valeur = getNestedValue(donnees, chemin);
    if (valeur !== undefined && valeur !== null && valeur !== '') remplis++;
  });

  return Math.round((remplis / champsAttendus.length) * 100);
}
```

### Affichage dans le dashboard

Avant de lancer la generation, afficher un modal de confirmation :

```
┌──────────────────────────────────────────────┐
│  Validation des donnees                      │
│                                              │
│  Completude : 78%  ██████████░░░             │
│                                              │
│  ✅ Vendeur : Martin Jean-Pierre             │
│  ✅ Acquereur : Dupont Marie                 │
│  ✅ Bien : 12 rue de la Paix, 75002 Paris    │
│  ✅ Prix : 450 000 EUR                        │
│  ⚠️ Surface Carrez non renseignee            │
│  ⚠️ Diagnostics non fournis                  │
│                                              │
│  [Generer quand meme]   [Completer d'abord]  │
└──────────────────────────────────────────────┘
```

### Critere de validation

Le notaire voit un recapitulatif clair de ce qui est rempli et ce qui manque AVANT la generation. Il peut generer avec des avertissements mais pas avec des erreurs bloquantes.

---

## T6 : Telechargement DOCX dans le dashboard

### Prerequis

Paul est en train d'ajouter `GET /files/{filename}` dans `api/main.py`. Quand c'est pret, le telechargement est simple.

### Ce que tu dois faire

1. **Apres la generation reussie**, afficher un bouton de telechargement :
   ```javascript
   function afficherTelechargement(result) {
     const apiUrl = 'https://notaire-ai--fastapi-app.modal.run';
     const container = document.getElementById('download-container');
     container.innerHTML = `
       <div class="alert alert-success">
         <h5>Document genere avec succes</h5>
         <p>Type : ${result.type_detecte} | Confiance : ${Math.round(result.confiance * 100)}%</p>
         <a href="${apiUrl}${result.fichier_url}"
            class="btn btn-primary"
            download="${result.fichier}">
           Telecharger ${result.fichier}
         </a>
       </div>
     `;
   }
   ```

2. **Gerer le header d'authentification pour le download** :
   Le endpoint `/files/` requiert `X-API-Key`. Un `<a href>` ne peut pas envoyer de header. Solutions :
   ```javascript
   // Option A : Fetch + blob (recommande)
   async function downloadFile(fichierUrl, filename) {
     const apiUrl = 'https://notaire-ai--fastapi-app.modal.run';
     const response = await fetch(`${apiUrl}${fichierUrl}`, {
       headers: { 'X-API-Key': localStorage.getItem('notaire_api_key') }
     });
     const blob = await response.blob();
     const url = window.URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.href = url;
     a.download = filename;
     a.click();
     window.URL.revokeObjectURL(url);
   }
   ```

### Critere de validation

Le notaire clique "Telecharger" et le fichier DOCX se telecharge dans son dossier de telechargements.

---

## T7 : Parcours de demo end-to-end

### Scenario de demo

Preparer un parcours complet pour montrer a un notaire prospect :

```
1. Le notaire se connecte au dashboard avec sa cle API
2. Il cree un nouveau dossier "Vente appartement Dupont → Martin"
3. Il genere un lien securise pour le vendeur (M. Dupont)
4. Il genere un lien securise pour l'acquereur (Mme Martin)
5. [Simulation] Les clients remplissent les formulaires
6. Le notaire voit les soumissions dans le dashboard
7. Il decrypte et verifie les donnees
8. Il clique "Generer la promesse"
9. Le systeme valide, genere, et propose le telechargement
10. Le notaire telecharge un DOCX conforme a sa trame
```

### Donnees de demo

Creer un jeu de donnees pre-rempli pour la demo :

```javascript
const DEMO_VENDEUR = {
  vendeur1_civilite: 'Monsieur',
  vendeur1_nom: 'DUPONT',
  vendeur1_prenoms: 'Jean Pierre Marie',
  vendeur1_date_naissance: '15/03/1965',
  vendeur1_lieu_naissance: 'Paris 12eme (75)',
  vendeur1_nationalite: 'Francaise',
  vendeur1_profession: 'Cadre superieur',
  vendeur1_situation: 'marie',
  vendeur1_date_mariage: '20/06/1990',
  vendeur1_lieu_mariage: 'Paris 8eme (75)',
  vendeur1_regime_matrimonial: 'separation_biens',
  vendeur1_adresse: '45 avenue des Champs-Elysees',
  vendeur1_code_postal: '75008',
  vendeur1_ville: 'Paris',
  tel_portable: '06 12 34 56 78',
  email: 'jean.dupont@email.com',
  iban: 'FR76 3000 6000 0112 3456 7890 189',
  bic: 'AGRIFRPP',
  banque: 'Credit Agricole'
};

const DEMO_ACQUEREUR = {
  acquereur_civilite: 'Madame',
  acquereur_nom: 'MARTIN',
  acquereur_prenoms: 'Sophie Anne',
  acquereur_date_naissance: '22/08/1982',
  acquereur_lieu_naissance: 'Lyon 3eme (69)',
  acquereur_nationalite: 'Francaise',
  acquereur_profession: 'Architecte',
  acquereur_situation: 'celibataire',
  apport_personnel: 90000,
  pret_montant: 360000,
  pret_banque: 'BNP Paribas',
  pret_duree: 240,
  pret_taux_max: 3.5
};

const DEMO_BIEN = {
  adresse: '12 rue de la Paix',
  code_postal: '75002',
  ville: 'Paris',
  lot_numero: '45',
  lot_designation: 'Appartement au 3eme etage, porte droite',
  lot_tantiemes: 125,
  lot_tantiemes_base: 10000,
  surface_carrez: 67.50,
  prix_montant: 450000
};
```

### Critere de validation

La demo tourne de bout en bout sans erreur, du login au telechargement du DOCX.

---

## T8 : Landing page commerciale

### Objectif

Une page simple qui explique le produit et invite les notaires a tester.

### Contenu suggere

```
Notomai - Generez vos actes en 1 minute

[Hero]
"Vos promesses et actes de vente, generes en quelques clics.
100% conformes a vos trames. Securise et chiffre."

[3 blocs]
1. Collectez   — Envoyez un lien securise a vos clients
2. Verifiez    — Les donnees arrivent chiffrees dans votre dashboard
3. Generez     — Un DOCX conforme a votre trame en 5 secondes

[CTA]
"Tester gratuitement" → Formulaire contact ou acces demo

[Footer]
Chiffrement AES-256 | RGPD conforme | Heberge en France
```

### Placement

`web/index.html` ou un sous-domaine dedie.

---

## T9 : Onboarding premier notaire

### Checklist onboarding

1. Creer une entree dans `etudes` (Supabase)
2. Creer une `agent_api_key` pour le notaire
3. Lui envoyer son URL dashboard + cle API
4. Lui faire tester le parcours demo
5. Recueillir son feedback → `feedbacks` table

### Donnees a creer dans Supabase

```sql
-- 1. Etude
INSERT INTO etudes (nom, siret, email_contact, telephone)
VALUES ('Cabinet Dupont & Associes', '12345678900012', 'contact@dupont-notaires.fr', '01 42 00 00 00');

-- 2. API Key (le hash sera genere par le backend)
-- Utiliser POST /admin/api-keys si disponible, sinon insertion directe
```

---

## Reference technique rapide

### Endpoints API que tu dois appeler

| Endpoint | Methode | Quand l'utiliser | Auth |
|----------|---------|------------------|------|
| `/health` | GET | Verifier que le backend tourne | Aucune |
| `/dossiers` | GET | Lister les dossiers du notaire | X-API-Key |
| `/dossiers` | POST | Creer un nouveau dossier | X-API-Key |
| `/dossiers/{id}` | PATCH | Mettre a jour un dossier | X-API-Key |
| `/promesses/generer` | POST | Generer une promesse de vente | X-API-Key |
| `/promesses/valider` | POST | Valider les donnees avant generation | X-API-Key |
| `/promesses/types` | GET | Lister les 4 types de promesse | X-API-Key |
| `/agent/execute` | POST | Envoyer une demande en langage naturel | X-API-Key |
| `/files/{filename}` | GET | Telecharger un DOCX genere | X-API-Key |

### Authentification

Toutes les requetes (sauf `/health`) necesitent le header :
```
X-API-Key: nai_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

La cle est stockee dans `localStorage.getItem('notaire_api_key')` apres le login dashboard.

### Tables Supabase que tu utilises

| Table | Acces | Ce que tu fais |
|-------|-------|----------------|
| `agent_api_keys` | Lecture | Login dashboard |
| `etudes` | Lecture | Info cabinet |
| `form_submissions` | Lecture/Ecriture | CRUD formulaires |
| `dossiers` | Lecture (via API) | Lister/creer dossiers |
| `clients` | Lecture (via API) | Profils clients enrichis |

### Chiffrement E2E — Comment ca marche

```
1. Dashboard cree un token (64-hex) + une cle AES-256 (base64)
2. La cle est mise dans le FRAGMENT de l'URL : https://...?token=abc#key=xyz
3. Le fragment (#key=...) n'est JAMAIS envoye au serveur (standard HTTP)
4. Le client ouvre le formulaire, le navigateur extrait la cle du fragment
5. A la soumission, le navigateur chiffre les donnees avec AES-256-GCM
6. Supabase recoit : token + blob chiffre + IV (jamais les donnees en clair)
7. Le notaire dechiffre dans son navigateur en collant la cle
```

Fichier de reference : `web/crypto.js` (143 lignes)

### Structure des formulaires existants

| Formulaire | Champs | Etapes | Cible |
|------------|--------|--------|-------|
| `fill.html` | ~12 | 1 | Acquereur simple (identite + coordonnees) |
| `achat-bien.html` | ~100 | 6 | Acquereur complet (identite + financement + projets) |
| `vente-appartement.html` | ~350 | 7 | Vendeur appart (identite + copro + travaux + fiscal) |
| `vente-maison.html` | ~400 | 8 | Vendeur maison (identite + terrain + batiment + fiscal) |

### Coordination avec Paul et Tom

| Quand tu as besoin de... | Demande a... | Endpoint/fichier |
|--------------------------|-------------|------------------|
| Generer un DOCX | Paul (backend) | `POST /promesses/generer` |
| Telecharger un DOCX | Paul (backend) | `GET /files/{filename}` |
| Connaitre le format JSON attendu | Tom (schemas) | `schemas/variables_promesse_vente.json` |
| Ajouter un nouveau type de formulaire | Tom (template) | `schemas/questions_*.json` |
| Corriger un bug API | Paul (backend) | `api/main.py` |
| Modifier le format du DOCX genere | Tom (moteur) | `execution/core/exporter_docx.py` |

---

## Checklist avant de commencer

- [ ] Verifier que tu as acces au repo git (branche `tom/dev` ou ta propre branche)
- [ ] Verifier que `web/dashboard-notaire.html` s'ouvre dans ton navigateur
- [ ] Verifier que tu as une cle API de test (`nai_...`)
- [ ] Verifier que le backend Modal repond : `curl https://notaire-ai--fastapi-app.modal.run/health`
- [ ] Lire `schemas/variables_promesse_vente.json` pour comprendre la structure cible
- [ ] Avoir le fichier `web/supabase-client.js` fonctionnel (URL + anon key)
